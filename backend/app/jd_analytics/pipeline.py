"""JD Analytics pipeline (plain Python).
 
read file -> extract_a (Gemini) and extract_b (Mistral) in parallel -> validate -> merge -> cache.
"""
import hashlib
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Literal, Optional
 
from pydantic import BaseModel, Field, field_validator
 
from app.shared.docreader import read_document
from app.shared.llm import call_structured, get_gemini, get_mistral
from app.shared.schemas import CategoryCode, Confidence, ExtractionResult, Skill
 
MAX_JD_CHARS = 30_000  # keeps a huge upload from burning the free-tier token quota
 
 
class ExtractionError(RuntimeError):
    """Both models failed, so there is nothing to return."""
 
 
# ---------------------------------------------------------------------------
# What we ask each LLM to return. Kept local (not in schemas.py) because the
# contract has no "raw model answer" shape; we convert to schemas.Skill after merging.
# ---------------------------------------------------------------------------
class LLMSkill(BaseModel):
    skill_name: str = Field(min_length=1)
    category_code: CategoryCode
    importance: Literal["must_have", "nice_to_have"]
    evidence: str = ""
    confidence: Confidence = "medium"
 
    @field_validator("skill_name", "evidence", mode="before")
    @classmethod
    def _strip_text(cls, v):
        return v.strip() if isinstance(v, str) else ("" if v is None else v)
 
    @field_validator("category_code", mode="before")
    @classmethod
    def _upper_code(cls, v):  # models sometimes answer "sql" or " SQL "
        return v.strip().upper() if isinstance(v, str) else v
 
    @field_validator("importance", "confidence", mode="before")
    @classmethod
    def _tidy_label(cls, v):  # "Must-Have" -> "must_have"
        return v.strip().lower().replace("-", "_").replace(" ", "_") if isinstance(v, str) else v
 
 
class LLMExtraction(BaseModel):
    company: str = ""
    role: str = ""
    skills: list[LLMSkill] = Field(min_length=1)  # an empty list counts as a bad answer and is retried
 
    @field_validator("company", "role", mode="before")
    @classmethod
    def _none_to_empty(cls, v):
        return "" if v is None else v
 
 
# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------
CATEGORY_GUIDE = """\
COD   - programming languages and hands-on coding ability (Python, Java, C++, JavaScript)
DSA   - data structures, algorithms, complexity, problem solving
OOD   - object-oriented design, design patterns, clean code
APTI  - aptitude: logical, quantitative and analytical reasoning
COMM  - communication, teamwork, leadership, collaboration, stakeholder management
AI    - machine learning, deep learning, NLP, LLMs, data science, statistics
CLOUD - cloud platforms, containers, Kubernetes, DevOps, CI/CD, infrastructure
SQL   - databases and SQL (relational or NoSQL), data modelling, warehousing, analytics queries
SWE   - software engineering practice: frameworks (React, FastAPI, Spring), APIs, testing, version control, code review, agile, debugging
SYSD  - system design: distributed systems, scalability, architecture, reliability
NETW  - networking: TCP/IP, HTTP, DNS, protocols, network security
OS    - operating systems: Linux, processes, memory, concurrency, file systems
OTHER - anything that fits none of the above (for example domain knowledge)"""
 
PROMPT_HEAD = f"""You are analysing a job description (JD) to list the skills a candidate needs.
 
Extract every distinct skill, technology, tool or competency the JD asks for. JDs are written in plain prose, so also infer skills from the responsibilities and qualifications (for example "build services used by millions of people" implies system design). A typical JD gives 10 to 30 skills. Do not invent skills the JD does not support.
 
For each skill return:
- skill_name: short and specific, such as "Python", "Kubernetes" or "System design". Keep named technologies exactly as named (for example "PostgreSQL", "React", "TensorFlow") and give each its own entry. One skill per entry, no duplicates, no sentences.
  Use the short, standard, generic name that most people would use: "Communication" (not "Stakeholder communication" or "Technical communication"), "Statistics" (not "Statistical judgment"), "Machine learning" (not "Predictive modeling"), "Data visualization" (not "BI/visualization tools"), "Data modeling" (not "Schema design"). Name the skill itself, not the activity or a quality ("Overfitting", not "Overfitting recognition"). Never list a project, a degree, a number of years or a job title as a skill. If several phrases in the JD mean the same skill, return it once.
- category_code: exactly one of these codes:
{CATEGORY_GUIDE}
- importance: "must_have" if the JD says required, requires, minimum, must, essential or mandatory. "nice_to_have" if it says preferred, bonus, a plus, nice to have, ideally or familiarity with. If the JD does not say, use "must_have" for minimum or basic qualifications and core responsibilities, otherwise "nice_to_have".
- evidence: a short quote (at most 20 words) copied from the JD that shows why the skill is needed.
- confidence: "high" if the skill is named explicitly, "medium" if it is clearly implied by a responsibility, "low" if it is a guess.
 
Also return company and role (the hiring company and the job title) if the JD states them, otherwise empty strings."""
 
 
def build_prompt(jd_text: str) -> str:
    return f'{PROMPT_HEAD}\n\nJob description:\n"""\n{jd_text[:MAX_JD_CHARS]}\n"""'
 
 
# ---------------------------------------------------------------------------
# The two extractors (module-level functions so tests can replace them)
# ---------------------------------------------------------------------------
def extract_a(jd_text: str) -> LLMExtraction:
    """Model A: Gemini (our main model)."""
    return call_structured(get_gemini(), build_prompt(jd_text), LLMExtraction)
 
 
def extract_b(jd_text: str) -> LLMExtraction:
    """Model B: Mistral (throttled and backed off inside call_structured)."""
    return call_structured(get_mistral(), build_prompt(jd_text), LLMExtraction)
 
 
def _describe_error(e: Exception) -> str:
    if isinstance(e, KeyError):  # get_gemini()/get_mistral() read their settings from the environment
        return f"missing environment variable {e.args[0]}"
    return f"{type(e).__name__}: {str(e)[:300]}"
 
 
def run_models(jd_text: str) -> tuple[Optional[LLMExtraction], Optional[LLMExtraction], dict[str, str]]:
    """Run both models at the same time. A model that fails (after its own retries) returns None."""
    failures: dict[str, str] = {}
    results: dict[str, LLMExtraction] = {}
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {"gemini": pool.submit(extract_a, jd_text), "mistral": pool.submit(extract_b, jd_text)}
        for name, future in futures.items():
            try:
                results[name] = future.result()
            except Exception as e:  # any failure just means "use the other model"
                failures[name] = _describe_error(e)
    return results.get("gemini"), results.get("mistral"), failures
 
 
# ---------------------------------------------------------------------------
# Merge
# ---------------------------------------------------------------------------
_CONF_ORDER = ["low", "medium", "high"]
 
 
def lower_confidence(confidence: str) -> str:
    """high -> medium -> low (low stays low)."""
    return _CONF_ORDER[max(0, _CONF_ORDER.index(confidence) - 1)]
 
 
def _key(name: str) -> str:
    """Matching key: lowercase, ignore / - & , ( ) and simple plurals, so
    "Data Visualization Tools" and "data-visualization tool" match.
    Characters that are part of names (C++, C#, .NET, Node.js) are kept."""
    text = name.lower()
    for ch in "/-&,()":
        text = text.replace(ch, " ")
    words = []
    for w in text.split():
        if w == "and":
            continue
        if len(w) > 4 and w.endswith("s") and not w.endswith("ss"):
            w = w[:-1]  # databases -> database (applied to both models, so it stays consistent)
        words.append(w)
    return " ".join(words)
 
 
def _index(extraction: LLMExtraction) -> dict[str, LLMSkill]:
    skills: dict[str, LLMSkill] = {}
    for s in extraction.skills:
        skills.setdefault(_key(s.skill_name), s)  # if a model repeats a skill, keep the first
    return skills
 
 
def _to_skill(s: LLMSkill, confidence: str, models_agree: Optional[bool], evidence: Optional[str] = None) -> Skill:
    return Skill(
        skill_name=s.skill_name,
        category_code=s.category_code,
        evidence=s.evidence if evidence is None else evidence,
        confidence=confidence,
        importance=s.importance,
        models_agree=models_agree,
    )
 
 
def merge(gemini: Optional[LLMExtraction], mistral: Optional[LLMExtraction], source_file: str) -> ExtractionResult:
    """Combine the two model answers into one ExtractionResult(source_type='jd').
 
    - found by both:  models_agree=True (Gemini's category, importance and confidence are kept)
    - found by one:   models_agree=False and confidence lowered one level
    - category clash: keep Gemini's category, lower confidence, record it in extras.disagreements
    - only one model worked: use it alone, models_agree=None, confidence unchanged
    """
    if gemini is None and mistral is None:
        raise ExtractionError("Neither model returned a result.")
 
    disagreements: list[dict] = []
    skills: list[Skill] = []
 
    if gemini is not None and mistral is not None:
        a, b = _index(gemini), _index(mistral)
        for key, sa in a.items():
            sb = b.get(key)
            if sb is None:
                skills.append(_to_skill(sa, lower_confidence(sa.confidence), False))
                continue
            confidence = sa.confidence
            if sa.category_code != sb.category_code:
                confidence = lower_confidence(confidence)
                disagreements.append({
                    "skill": sa.skill_name,
                    "gemini_category": sa.category_code,
                    "mistral_category": sb.category_code,
                })
            skills.append(_to_skill(sa, confidence, True, evidence=sa.evidence or sb.evidence))
        for key, sb in b.items():
            if key not in a:
                skills.append(_to_skill(sb, lower_confidence(sb.confidence), False))
        company = gemini.company or mistral.company
        role = gemini.role or mistral.role
    else:
        only = gemini if gemini is not None else mistral
        assert only is not None
        skills = [_to_skill(s, s.confidence, None) for s in _index(only).values()]
        company, role = only.company, only.role
 
    return ExtractionResult(
        source_type="jd",
        source_file=source_file,
        company=company,
        role=role,
        skills=skills,
        extras={"disagreements": disagreements},
    )
 
 
def analyze_text(jd_text: str, source_file: str) -> ExtractionResult:
    """Run both models on JD text and merge. Raises ExtractionError if both fail."""
    gemini, mistral, failures = run_models(jd_text)
    if gemini is None and mistral is None:
        reasons = "; ".join(f"{name}: {why}" for name, why in failures.items())
        raise ExtractionError(f"Both models failed, so the JD could not be analysed. {reasons}")
    result = merge(gemini, mistral, source_file)
    result.extras["models_used"] = [n for n, r in (("gemini", gemini), ("mistral", mistral)) if r is not None]
    result.extras["models_failed"] = failures  # empty when both worked
    return result
 
 
# ---------------------------------------------------------------------------
# Files and cache
# ---------------------------------------------------------------------------
def data_dir() -> Path:
    """backend/data, or GAPMAP_DATA_DIR if set (used by tests)."""
    override = os.environ.get("GAPMAP_DATA_DIR")
    return Path(override) if override else Path(__file__).resolve().parents[2] / "data"
 
 
def jd_dir() -> Path:
    return data_dir() / "jds"
 
 
def cache_dir() -> Path:
    return data_dir() / "cache"
 
 
def list_jd_files() -> list[Path]:
    """Sample JD files (.pdf and .docx) in backend/data/jds, sorted by name."""
    if not jd_dir().is_dir():
        return []
    return sorted(p for p in jd_dir().iterdir() if p.is_file() and p.suffix.lower() in (".pdf", ".docx"))
 
 
def file_hash(path: Path) -> str:
    """SHA-256 of the file's bytes; this is the cache key."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()
 
 
def cache_path(path: Path) -> Path:
    return cache_dir() / f"{file_hash(path)}.json"
 
 
def _load_cache(cp: Path) -> Optional[ExtractionResult]:
    try:
        return ExtractionResult.model_validate_json(cp.read_text(encoding="utf-8"))
    except (OSError, ValueError):  # missing, unreadable or no longer matches the schema: just recompute
        return None
 
 
def _save_cache(cp: Path, result: ExtractionResult) -> None:
    cp.parent.mkdir(parents=True, exist_ok=True)
    # write to a temp file first so a crash never leaves a half-written cache entry
    tmp = cp.with_name(f"{cp.name}.{os.getpid()}.{threading.get_ident()}.tmp")
    tmp.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    os.replace(tmp, cp)
 
 
def get_cached(path: str | Path) -> Optional[ExtractionResult]:
    """Return the cached result for this file's content, or None."""
    return _load_cache(cache_path(Path(path)))
 
 
def analyze_file(path: str | Path, source_name: Optional[str] = None, refresh: bool = False) -> ExtractionResult:
    """Analyze a JD file, using the cache unless refresh=True.
 
    source_name is the name to report (an upload's original file name instead of its temp path).
    """
    p = Path(path)
    name = source_name or p.name
    cp = cache_path(p)  # raises FileNotFoundError if the file is missing
 
    if not refresh:
        cached = _load_cache(cp)
        if cached is not None:
            cached.source_file = name  # same content may have been cached under another file name
            return cached
 
    result = analyze_text(read_document(p), name)
    # Do not cache a one-model result: when the other API is back, a rerun should do better.
    if not result.extras.get("models_failed"):
        _save_cache(cp, result)
    return result
 
 
def analyze_jd(jd_file: str | Path, refresh: bool = False) -> ExtractionResult:
    """Analyze a sample JD by file name (or path). Uses the cache; refresh=True forces a new run."""
    p = Path(jd_file)
    if not p.is_file():
        p = jd_dir() / p.name
    return analyze_file(p, refresh=refresh)
