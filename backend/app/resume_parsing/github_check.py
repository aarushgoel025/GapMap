import os
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional
import requests
from dotenv import load_dotenv

from db.store import write_audit

load_dotenv()

# Skill to Category mapping for GitHub languages and topics
GITHUB_SKILL_MAP: Dict[str, Dict[str, Any]] = {
    # Coding & Languages (COD)
    "python": {"name": "Python", "code": "COD"},
    "javascript": {"name": "JavaScript", "code": "COD"},
    "typescript": {"name": "TypeScript", "code": "COD"},
    "java": {"name": "Java", "code": "COD"},
    "c++": {"name": "C++", "code": "COD"},
    "cpp": {"name": "C++", "code": "COD"},
    "c": {"name": "C", "code": "COD"},
    "c#": {"name": "C#", "code": "COD"},
    "csharp": {"name": "C#", "code": "COD"},
    "go": {"name": "Go", "code": "COD"},
    "golang": {"name": "Go", "code": "COD"},
    "rust": {"name": "Rust", "code": "COD"},
    "kotlin": {"name": "Kotlin", "code": "COD"},
    "swift": {"name": "Swift", "code": "COD"},

    # Software Engineering (SWE)
    "react": {"name": "React", "code": "SWE"},
    "nextjs": {"name": "Next.js", "code": "SWE"},
    "fastapi": {"name": "FastAPI", "code": "SWE"},
    "flask": {"name": "Flask", "code": "SWE"},
    "django": {"name": "Django", "code": "SWE"},
    "nodejs": {"name": "Node.js", "code": "SWE"},
    "node": {"name": "Node.js", "code": "SWE"},
    "express": {"name": "Express.js", "code": "SWE"},
    "spring": {"name": "Spring Boot", "code": "SWE"},
    "html": {"name": "HTML/CSS Frontend", "code": "SWE"},
    "css": {"name": "HTML/CSS Frontend", "code": "SWE"},
    "git": {"name": "Git & Version Control", "code": "SWE"},
    "github": {"name": "Git & GitHub Workflows", "code": "SWE"},
    "testing": {"name": "Unit & Integration Testing", "code": "SWE"},
    "pytest": {"name": "Automated Testing (Pytest)", "code": "SWE"},

    # Cloud & DevOps (CLOUD)
    "docker": {"name": "Docker & Containerization", "code": "CLOUD"},
    "dockerfile": {"name": "Docker & Containerization", "code": "CLOUD"},
    "kubernetes": {"name": "Kubernetes", "code": "CLOUD"},
    "k8s": {"name": "Kubernetes", "code": "CLOUD"},
    "aws": {"name": "AWS Cloud Services", "code": "CLOUD"},
    "gcp": {"name": "Google Cloud Platform", "code": "CLOUD"},
    "azure": {"name": "Microsoft Azure", "code": "CLOUD"},
    "terraform": {"name": "Terraform & IaC", "code": "CLOUD"},
    "ci/cd": {"name": "CI/CD Pipelines", "code": "CLOUD"},
    "github-actions": {"name": "GitHub Actions CI/CD", "code": "CLOUD"},

    # Databases & SQL (SQL)
    "sql": {"name": "SQL & Relational Databases", "code": "SQL"},
    "postgresql": {"name": "PostgreSQL", "code": "SQL"},
    "postgres": {"name": "PostgreSQL", "code": "SQL"},
    "mysql": {"name": "MySQL", "code": "SQL"},
    "sqlite": {"name": "SQLite", "code": "SQL"},
    "mongodb": {"name": "MongoDB & NoSQL", "code": "SQL"},
    "redis": {"name": "Redis In-Memory Store", "code": "SQL"},

    # AI & Machine Learning (AI)
    "jupyter notebook": {"name": "Jupyter Notebook & Data Science", "code": "AI"},
    "jupyter": {"name": "Jupyter Notebook & Data Science", "code": "AI"},
    "machine-learning": {"name": "Machine Learning", "code": "AI"},
    "deep-learning": {"name": "Deep Learning", "code": "AI"},
    "pytorch": {"name": "PyTorch", "code": "AI"},
    "tensorflow": {"name": "TensorFlow", "code": "AI"},
    "nlp": {"name": "Natural Language Processing", "code": "AI"},
    "llm": {"name": "Large Language Models & GenAI", "code": "AI"},
    "pandas": {"name": "Data Analytics (Pandas/NumPy)", "code": "AI"},

    # Data Structures & Algorithms (DSA)
    "algorithms": {"name": "Data Structures & Algorithms", "code": "DSA"},
    "leetcode": {"name": "Algorithmic Problem Solving", "code": "DSA"},
    "data-structures": {"name": "Data Structures & Algorithms", "code": "DSA"},

    # System Design (SYSD)
    "system-design": {"name": "System Design & Architecture", "code": "SYSD"},
    "microservices": {"name": "Microservices Architecture", "code": "SYSD"},
    "distributed-systems": {"name": "Distributed Systems", "code": "SYSD"},

    # Operating Systems (OS)
    "linux": {"name": "Linux & Unix Environments", "code": "OS"},
    "shell": {"name": "Shell Scripting & Bash", "code": "OS"},
    "bash": {"name": "Shell Scripting & Bash", "code": "OS"},

    # Networking (NETW)
    "networking": {"name": "Computer Networking", "code": "NETW"},
    "api": {"name": "REST & HTTP APIs", "code": "NETW"},
    "socket": {"name": "Network Socket Programming", "code": "NETW"},
}


# Canonical skill synonyms for matching resume skills against repo languages/topics
SKILL_SYNONYMS: Dict[str, set[str]] = {
    "python": {"python", "py", "python3"},
    "javascript": {"javascript", "js", "ecmascript"},
    "typescript": {"typescript", "ts"},
    "java": {"java"},
    "c++": {"c++", "cpp", "cplusplus"},
    "c#": {"c#", "csharp", "c-sharp"},
    "c": {"c"},
    "go": {"go", "golang"},
    "rust": {"rust"},
    "html": {"html", "html5"},
    "css": {"css", "css3"},
    "sql": {"sql", "mysql", "postgresql", "postgres", "sqlite", "tsql", "plsql", "plpgsql"},
    "mysql": {"mysql"},
    "postgresql": {"postgresql", "postgres"},
    "mongodb": {"mongodb", "mongo"},
    "redis": {"redis"},
    "docker": {"docker", "dockerfile", "container", "containers"},
    "kubernetes": {"kubernetes", "k8s"},
    "fastapi": {"fastapi"},
    "react": {"react", "reactjs"},
    "nextjs": {"nextjs", "next.js"},
    "django": {"django"},
    "flask": {"flask"},
    "nodejs": {"node", "nodejs", "node.js"},
    "git": {"git", "github"},
    "aws": {"aws", "amazon-web-services"},
    "linux": {"linux", "ubuntu", "debian", "unix"},
    "machine learning": {"machine-learning", "ml", "deep-learning", "pytorch", "tensorflow"},
    "data structures": {"data-structures", "algorithms", "leetcode", "dsa"},
}

FALSE_FRIEND_SUBSTRINGS: Dict[str, List[str]] = {
    "java": ["javascript"],
    "c": ["c++", "c#", "css", "html", "react"],
    "r": ["rust", "ruby"],
    "go": ["google"],
}


def extract_github_username(github_input: str) -> str:
    """Extract clean GitHub username from URL or handle."""
    if not github_input:
        return ""
    cleaned = github_input.strip().rstrip("/")
    # If full URL like https://github.com/aarushgoel025
    if "github.com/" in cleaned:
        cleaned = cleaned.split("github.com/")[-1].split("/")[0]
    # Strip leading @
    if cleaned.startswith("@"):
        cleaned = cleaned[1:]
    return cleaned.strip()


def get_cache_file(username: str) -> Path:
    for candidate in [
        Path.cwd() / "data" / "cache",
        Path(__file__).resolve().parent.parent / "data" / "cache",
        Path(__file__).resolve().parent.parent.parent / "data" / "cache",
        Path(__file__).resolve().parent.parent.parent.parent / "data" / "cache",
    ]:
        if (candidate / f"github_{username.lower()}.json").is_file():
            return candidate / f"github_{username.lower()}.json"

    base = Path.cwd() / "data" / "cache"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"github_{username.lower()}.json"


def match_skill_against_repos(skill_name: str, repos: List[Dict[str, Any]]) -> tuple[Optional[Dict[str, Any]], Optional[str]]:
    """
    Strictly verify whether a skill claimed on a resume is substantiated by public repositories.
    Uses language equality/aliases, topic tags, repository name tokens, or explicit description matches.
    Prevents false substring matches (e.g. 'java' matching 'javascript', 'or' matching 'oracle', 'in' matching 'linux').
    """
    parts = [p.strip().lower() for p in re.split(r"[/&,]+", skill_name) if p.strip()]
    if not parts:
        parts = [skill_name.strip().lower()]

    for repo in repos:
        r_name = (repo.get("name") or "").strip().lower()
        r_lang = (repo.get("language") or "").strip().lower()
        r_topics = {t.strip().lower() for t in (repo.get("topics") or [])}
        r_desc = (repo.get("description") or "").strip().lower()
        name_tokens = set(re.split(r"[-_.]+", r_name))

        for part in parts:
            # Prevent false-friend language matches (e.g., Java matching JavaScript)
            if part in FALSE_FRIEND_SUBSTRINGS:
                if any(ff == r_lang for ff in FALSE_FRIEND_SUBSTRINGS[part]):
                    continue

            # 1. Primary Language Match
            if r_lang:
                if part == r_lang:
                    return repo, f"Verified primary repository language '{repo.get('language')}' in '{repo.get('name')}'"
                if part in SKILL_SYNONYMS and r_lang in SKILL_SYNONYMS[part]:
                    return repo, f"Verified primary repository language '{repo.get('language')}' in '{repo.get('name')}'"

            # 2. Topic Tags Match
            target_syns = SKILL_SYNONYMS.get(part, {part, part.replace(" ", "-"), part.replace(" ", "")})
            matched_topics = target_syns.intersection(r_topics)
            if matched_topics:
                return repo, f"Verified repository topic tag '{list(matched_topics)[0]}' in '{repo.get('name')}'"

            # 3. Repository Name Token Match
            matched_name = target_syns.intersection(name_tokens)
            if matched_name and len(list(matched_name)[0]) >= 3:
                return repo, f"Verified repository '{repo.get('name')}'"

            # 4. Whole-word match in description for verified technical terms
            for syn in target_syns:
                if len(syn) >= 3 and re.search(r"\b" + re.escape(syn) + r"\b", r_desc, re.IGNORECASE):
                    if part == "java" and not re.search(r"\bjava\b(?!\s*script)", r_desc, re.IGNORECASE):
                        continue
                    return repo, f"Verified in description of '{repo.get('name')}' ({syn})"

    return None, None


def verify_github_profile(
    github_url_or_user: str,
    skills: Optional[List[Dict[str, Any]]] = None,
    refresh: bool = False,
) -> Dict[str, Any]:
    """
    Query the GitHub REST API for a candidate's profile and 10 most recent repos.
    Cross-references repository languages and topics with candidate skills,
    adds 'github' to verified_by, removes stuffing flags, and upgrades confidence.
    """
    username = extract_github_username(github_url_or_user)
    if not username:
        return {
            "error": "Invalid GitHub username or URL provided",
            "verified_skills": skills or [],
            "verified_count": 0,
        }

    cache_file = get_cache_file(username)

    user_data: Dict[str, Any] = {}
    repos: List[Dict[str, Any]] = []

    # Check cache if not forced refresh
    if not refresh and cache_file.is_file():
        try:
            cached_result = json.loads(cache_file.read_text(encoding="utf-8"))
            user_data = cached_result.get("user", {})
            repos = cached_result.get("repos", [])
        except Exception:
            pass

    # If not in cache, query GitHub API
    if not user_data or not repos:
        token = os.getenv("GITHUB_TOKEN")
        headers = {"User-Agent": "GapMap-Talent-Engine"}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        try:
            u_res = requests.get(
                f"https://api.github.com/users/{username}",
                headers=headers,
                timeout=6,
            )
            if u_res.status_code == 200:
                user_data = u_res.json()
            elif u_res.status_code == 404:
                return {
                    "error": f"GitHub user '{username}' not found.",
                    "verified_skills": skills or [],
                    "verified_count": 0,
                }
            else:
                user_data = {"login": username, "public_repos": 0}

            r_res = requests.get(
                f"https://api.github.com/users/{username}/repos?sort=pushed&per_page=10",
                headers=headers,
                timeout=6,
            )
            if r_res.status_code == 200:
                repos = r_res.json()
        except Exception:
            # If network error, attempt to keep any existing cache
            if not repos and cache_file.is_file():
                try:
                    cached_result = json.loads(cache_file.read_text(encoding="utf-8"))
                    user_data = cached_result.get("user", {})
                    repos = cached_result.get("repos", [])
                except Exception:
                    pass
            user_data = user_data or {"login": username, "public_repos": 0}
            repos = repos or []

    # Cache response data only if we received repos
    if repos:
        try:
            cache_file.write_text(
                json.dumps({"user": user_data, "repos": repos}, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

    # Extract languages across repositories
    repo_summaries: List[Dict[str, Any]] = []
    top_languages: Dict[str, int] = {}

    for repo in repos:
        name = repo.get("name", "")
        lang = repo.get("language")
        topics = repo.get("topics") or []

        if lang:
            top_languages[lang] = top_languages.get(lang, 0) + 1

        repo_summaries.append({
            "name": name,
            "language": lang or "Mixed",
            "topics": topics[:4],
            "description": repo.get("description") or "",
            "stars": repo.get("stargazers_count", 0),
            "html_url": repo.get("html_url", f"https://github.com/{username}/{name}"),
        })

    # Cross-reference with candidate skills
    working_skills = [dict(s) for s in (skills or [])]
    verified_count = 0

    for s in working_skills:
        s_name = s.get("skill_name", "")
        matching_repo, match_evidence = match_skill_against_repos(s_name, repos)

        if matching_repo and match_evidence:
            verified_by = list(s.get("verified_by") or [])
            if "github" not in verified_by:
                verified_by.append("github")
            s["verified_by"] = verified_by

            # Clear stuffing flag since real code repositories prove practical use
            s["stuffing_flag"] = False

            # Elevate confidence
            if s.get("confidence") == "low":
                s["confidence"] = "medium"
            elif s.get("confidence") == "medium":
                s["confidence"] = "high"

            # Upgrade level estimate
            curr_est = s.get("level_estimate")
            if curr_est is None or curr_est < 7:
                s["level_estimate"] = 7 if s.get("confidence") == "medium" else 8

            s["evidence"] = match_evidence
            verified_count += 1

    # If candidate had no skills, populate discovered skills directly from GitHub
    if not working_skills:
        existing_skill_names = set()
        for kw, mapping in GITHUB_SKILL_MAP.items():
            for repo in repos:
                r_lang = (repo.get("language") or "").strip().lower()
                r_topics = {t.strip().lower() for t in (repo.get("topics") or [])}
                if kw == r_lang or kw in r_topics:
                    canonical_name = mapping["name"]
                    cat_code = mapping["code"]
                    if canonical_name.lower() not in existing_skill_names:
                        working_skills.append({
                            "skill_name": canonical_name,
                            "category_code": cat_code,
                            "evidence": f"Demonstrated in public GitHub repository '{repo.get('name')}' ({kw}).",
                            "confidence": "high",
                            "level_estimate": 7,
                            "source_section": "github",
                            "verified_by": ["github"],
                            "stuffing_flag": False,
                        })
                        existing_skill_names.add(canonical_name.lower())
                        verified_count += 1
                    break

    # Section F Governance: Write audit row (logging event metadata, never personal text)
    try:
        write_audit(
            action="github_check",
            details={
                "github_user": username,
                "skills_count": len(working_skills),
                "verified_count": verified_count,
                "public_repos": user_data.get("public_repos", len(repo_summaries)),
            },
            entity_id=username,
            entity_type="github_check",
        )
    except Exception:
        pass

    return {
        "username": username,
        "name": user_data.get("name") or username,
        "avatar_url": user_data.get("avatar_url"),
        "bio": user_data.get("bio") or "",
        "public_repos": user_data.get("public_repos", len(repo_summaries)),
        "top_languages": list(top_languages.keys()),
        "repos": repo_summaries[:6],
        "verified_skills": working_skills,
        "verified_count": verified_count,
    }
