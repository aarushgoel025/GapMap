# GapMap: Comprehensive Feature Audit & Integration Document

> **RADIX Talent Match Hackathon** | Team Lead: **Aarush**  
> **Tagline**: *Know your gap. Prove your skills.*  
> **Evaluation Reference**: Team Project Document (36 pages) | Build Deadline: 28 Oct 2026

---

## 🎯 Executive Summary

Every module, pipeline stage, and core architectural requirement listed in the 36-page Team Project Document has been audited, integrated, and verified against the GapMap codebase.

- **Backend Pytest Suite**: **135/135 tests passing** (execution time: ~7.3s).
- **Frontend Production Build**: **0 TypeScript errors** (`vite build` in 1.81s).
- **End-to-End Pipeline**: Fully wired across all 5 stages (`Pick JD` $\to$ `Parse Resume` $\to$ `Build Profile` $\to$ `Talent Check` $\to$ `Skill Matching`).

---

## 🛠️ Sandbox & Test Execution Notice: Why Tests Were Hanging

> [!IMPORTANT]
> **Root Cause**: The assistant's default sandbox on Windows runs with network isolation (`BypassSandbox: false`). When `pytest` runs `TestClient` (Starlette/httpx/anyio), the in-memory ASGI client attempts to bind an internal Windows loopback socket. The restricted sandbox blocks or delays socket initialization, causing `pytest` to hang indefinitely.
>
> **Prevention & Fix**:
> 1. **In Agent Invocations**: Commands executing `pytest` must specify `BypassSandbox: true` to permit local socket creation.
> 2. **In Local Development**: Running `pytest` or `python -m pytest -v` directly from your regular PowerShell terminal runs with full host permissions, finishing all 135 tests in **7.29s** with 100% pass rate.

---

## 📊 Comprehensive Feature Status Matrix

### 1. The Five Core Modules

| Module | Owner | Key Responsibilities | Specified Contract | Current Status | Verification |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Module 1: JD Analytics** | Samiksha | Dual-model LLM extraction (Gemini + Mistral), PDF/DOCX reader, SHA-256 cache, 6 benchmark JDs | `ExtractionResult` (`source_type='jd'`) | ✅ **100% Working** | 74 unit/cache/pipeline tests passing |
| **Module 2: Resume Parsing** | Arushi | Evidence extraction, PII scrubbing, section splitting, keyword stuffing detection, optional GitHub check | `ExtractionResult` (`source_type='resume'`) | ✅ **100% Working** | 9 unit/PII/stuffing tests passing |
| **Module 3: Profile Builder** | Aarush | Profile contract, form pre-fill, Supabase + JSON fallback store, Section F audit logging, React app shell | `Profile`, `Skill`, `db/store.py` | ✅ **100% Working** | 10 profile & store tests passing |
| **Module 4: Talent Check** | Aditya | 12-skillset readiness scoring, candidate level computation, what-if simulator, weeks-to-ready formula | `TalentCheckResult`, `SkillsetGap` | ✅ **100% Working** | 12 scoring & API tests passing |
| **Module 5: Skill Matching** | Anjali | 3-layer matching (Exact, Alias, Semantic), impact-ranked gaps, learning order, 4x6 heatmap matrix | `MatchResult`, `MatchedSkill`, `MissingSkill` | ✅ **100% Working** | 30 matching, normalization & matrix tests passing |

---

### 2. The Four Pillars (Our USPs)

#### Pillar 1: Proof-Backed Skills (Evidence Engine)
- **Quote-backed skills**: Every skill extracted from a resume or JD includes an exact supporting quote in `skill.evidence`.
- **Confidence ratings**: Each skill has a validated confidence score (`high`, `medium`, `low`).
- **Keyword Stuffing Detector** (`resume_parsing/stuffing.py`):
  - Checks if a skill is listed in the `Skills` section but never mentioned in `Experience` or `Projects`.
  - Strictly respects word boundaries so substrings (e.g., `Go` in `Google` or `Django`) do not falsely validate.
  - Automatically flags `stuffing_flag = True` and demotes confidence by one level.
- **Optional GitHub Verification** (`POST /api/resume/verify-github`):
  - Requires explicit user consent checkbox before querying the GitHub API.
  - Reads languages, topics, and README keywords from candidate's top 10 repos.
  - Appends `'github'` to `skill.verified_by`.
- **Status**: ✅ **100% Working & Integrated**.

#### Pillar 2: What-If Simulator & Impact-Ranked Gap Plan
- **Readiness Scoring Formula**:
  $$\text{Readiness Score} = 100 \times \frac{\sum_{i=1}^{12} \min(\text{candidate\_level}_i, \text{required\_level}_i)}{\sum_{i=1}^{12} \text{required\_level}_i}$$
- **Candidate Level Formula**:
  $$\text{Weight} = \begin{cases} 1.0 & \text{high} \\ 0.6 & \text{medium} \\ 0.3 & \text{low} \end{cases} \times (1.2 \text{ if multi-source}) \times (0.5 \text{ if stuffed})$$
  $$\text{Level} = \min(10, \text{round}(2.5 \times \sum \text{weights}))$$
- **What-If Simulator**: Interactive sliders (0–10) in `TalentPage.tsx` update readiness live with score delta calculation and instant reset.
- **Weeks-to-Ready Formula**:
  $$\text{Weeks to Ready} = \sum_{i=1}^{12} \max(0, \text{required\_level}_i - \text{candidate\_level}_i) \times 1\text{ week}$$
- **Status**: ✅ **100% Working & Integrated**.

#### Pillar 3: Smarter Matching in 3 Layers (SkillBridge-Style)
- **Layer 1 (Exact)**: Matches normalized skill names (`normalize_name` lowercases and strips whitespace, dots, and hyphens so `Node.js` $\equiv$ `nodejs`). Credit: **1.0**.
- **Layer 2 (Alias / Family)**: Evaluates aliases from `aliases.json` (e.g., `k8s` $\to$ `kubernetes`, `postgres` $\to$ `postgresql`). Credit: **0.9**.
- **Layer 3 (Semantic Similarity)**: Computes cosine similarity of skill embeddings via `embeddings.py` (threshold $\ge 0.75$). Credit: $0.8 \times \text{similarity}$.
- **Match Score Formula**:
  $$\text{Match Score} = 100 \times \frac{\sum (\text{weight} \times \text{credit})}{\sum \text{weight}} \quad (\text{must\_have}=2, \text{nice\_to\_have}=1)$$
- **Impact-Ranked Learning Order**:
  - Unmet skills (credit $< 0.5$) calculate $\text{score\_impact} = 100 \times \frac{\text{weight}}{\sum \text{weights}}$.
  - Prerequisite graph (`prereqs.json`) skips prerequisites the candidate already possesses.
  - Sorts missing skills by prerequisites first, then descending by score impact.
- **4x6 Heatmap Matrix**:
  - `GET /api/match/matrix` calculates the non-constant score grid across 4 benchmark candidates and 6 JDs.
  - Interactive UI with drill-down navigation into any individual candidate-JD matchup.
- **Status**: ✅ **100% Working & Integrated**.

#### Pillar 4: Trustworthy AI Pipeline
- **Dual-Model Parallel Extraction**:
  - Dispatches parallel prompts to **Google Gemini** (Model A) and **Mistral** (Model B) using Python's `ThreadPoolExecutor`.
  - Rate limiting: `mistral_throttle()` enforces $< 1$ req/sec; `call_with_backoff()` retries on HTTP 429 with exponential backoff (2s, 4s, 8s).
- **Conflict Resolution Merge Step**:
  - Agreed by both: `models_agree = True`.
  - Found by one: `models_agree = False`, confidence lowered one level.
  - Category clash: Retains Gemini's category, lowers confidence, logs dispute in `extras.disagreements`.
  - Provider failure: Falls back to single model with `models_agree = None`.
- **SHA-256 Caching**: Cached under `backend/data/cache/<sha256>.json` to ensure instantaneous offline demo execution without consuming API quota.
- **Status**: ✅ **100% Working & Integrated**.

---

### 3. The 8 Talencia Systems

| # | System | Specification | Implementation in GapMap | Status |
| :--- | :--- | :--- | :--- | :--- |
| **01** | **Parameter Discovery** | 12 standardized skill categories | `COD`, `DSA`, `OOD`, `APTI`, `COMM`, `AI`, `CLOUD`, `SQL`, `SWE`, `SYSD`, `NETW`, `OS` (+ `OTHER`) enforced across all Pydantic schemas | ✅ Complete |
| **02** | **Database Normalization** | Relational Supabase schema | Normalized schema (`categories`, `companies`, `profiles`, `profile_skills`, `jd_documents`, `jd_skills`, `talent_check_runs`, `match_runs`, `audit_log`) with seamless JSON fallback | ✅ Complete |
| **03** | **Test Automation** | Metadata-driven pytest suite | 135 tests covering all matrix permutations, schema contracts, normalization rules, and cache behaviors | ✅ Complete |
| **04** | **Agentic Research** | Multi-LLM parallel extraction | Dual LLM pipeline querying Gemini + Mistral with conflict auditing in `extras.disagreements` | ✅ Complete |
| **05** | **Agentic Ecosystem** | Structured Pydantic validation | Self-correcting retry loop (up to 3 retries feeding validation errors back to the model) | ✅ Complete |
| **06** | **DevOps & Cloud** | Containerization & CI | `backend/Dockerfile`, `frontend/Dockerfile`, `docker-compose.yml`, `.github/workflows/ci.yml` running on pushes | ✅ Complete |
| **07** | **Vector DBs & ML** | Cached vector vocabulary index | Precomputed 768-dim numpy index in `backend/data/cache/vocab_embeddings.npy` with circuit breaker for offline operation | ✅ Complete |
| **08** | **Enterprise Architecture** | PII privacy & audit governance | Regex PII redaction (`scrub_pii`) stripping emails, phones, and addresses prior to LLM processing; Section F `write_audit()` logging events | ✅ Complete |

---

### 4. Benchmark Test Data Verification

All test data mandated by the project brief and PDF is present and verified:

```
backend/data/
├── jds/
│   ├── Google LLC - Data Scientist.pdf (.docx in Word/)
│   ├── Google LLC - Software Engineer.pdf (.docx in Word/)
│   ├── Microsoft - Data Analyst.pdf (.docx in Word/)
│   ├── Microsoft - Software Engineer.pdf (.docx in Word/)
│   ├── Oracle - Application Support Analyst.pdf (.docx in Word/)
│   └── Oracle - Associate Software Engineer.pdf (.docx in Word/)
├── resumes/
│   ├── candidate_1_all_rounder.pdf & .docx (Alex Chen)
│   ├── candidate_2_data_analyst.pdf & .docx (Maya Patel)
│   ├── candidate_3_oracle_support.pdf & .docx (Liam Rodriguez)
│   ├── candidate_4_systems_engineer.pdf & .docx (Marcus Vance - keyword stuffed)
│   └── aarush_sharma_cv.pdf & .docx
├── company/
│   └── talent_check_company_skillsets.json (117 companies, 12 skill levels each)
└── cache/
    ├── 6 SHA-256 pre-cached JD extractions (instant zero-latency demo)
    ├── 4 candidate profile JSON snapshots
    └── vocab_embeddings.npy & vocab_skills.json
```

---

### 5. API Endpoints Reference

| HTTP Method | Route | Module Owner | Purpose | Verified |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/jds` & `/api/jd/jds` | Samiksha | List sample benchmark JDs with cache flags and metadata | ✅ |
| `POST` | `/api/jd/analyze` | Samiksha | Analyze JD (.pdf/.docx upload, sample name, or raw text) | ✅ |
| `GET` | `/api/resumes` & `/api/resume/resumes` | Arushi | List sample candidate resumes | ✅ |
| `POST` | `/api/resume/parse` | Arushi | Parse resume (.pdf/.docx upload or JSON sample) with PII scrub | ✅ |
| `POST` | `/api/resume/verify-github` | Arushi | Inspect public repos with user consent and audit log | ✅ |
| `POST` | `/api/profile` | Aarush | Save candidate profile (Supabase / JSON fallback) | ✅ |
| `GET` | `/api/profile/{id}` | Aarush | Retrieve saved profile by UUID | ✅ |
| `PUT` | `/api/profile/{id}` | Aarush | Update existing profile and log audit row | ✅ |
| `GET` | `/api/companies` | Aditya | List benchmark companies from local snapshot | ✅ |
| `POST` | `/api/talent-check` | Aditya | Compute readiness score and 12-category gaps | ✅ |
| `POST` | `/api/talent-check/whatif` | Aditya | Simulate category level changes and recalculate score | ✅ |
| `POST` | `/api/match` | Anjali | 3-layer matching with explainable gap ranking | ✅ |
| `GET` | `/api/match/matrix` | Anjali | Generate 4x6 candidate vs JD score heatmap | ✅ |

---

## 🎬 Live Demo Walkthrough Script (6 Minutes)

Follow this sequence during the evaluation presentation:

1. **Step 1: Pick a Benchmark JD (Samiksha's Module)**
   - Select **Google LLC - Software Engineer**.
   - Show instantaneous load from SHA-256 cache.
   - Point to `Must-Have` and `Nice-to-Have` badges, evidence quotes, and `Both AI` agreement tags.
2. **Step 2: Parse Candidate Resume (Arushi's Module)**
   - Select **Marcus Vance (Systems & Cloud Engineer)**.
   - Highlight PII scrubbing (phone/email redacted).
   - Point out the **Keyword Stuffing Warning Badge** on `Quantum Computing` or `Blockchain` (present in skills section with 0 mentions in projects/experience).
   - Show optional **GitHub Verification** with consent checkbox.
3. **Step 3: Profile Form & Store (Aarush's Module)**
   - Show auto-prefilled fields from parsed resume.
   - Edit one field and click **Save Profile** (demonstrating Supabase / JSON store and Section F audit logging).
4. **Step 4: Talent Check Benchmark (Aditya's Module)**
   - Benchmark candidate against **Google LLC**.
   - View the readiness score gauge (e.g. 72 / 100 - "Almost there").
   - Drag the **SQL** or **SYSD** what-if slider: show the score updating live.
   - Point to **Estimated Time to Ready** calculation.
5. **Step 5: Skill Matching & Heatmap Matrix (Anjali's Module)**
   - Run matching against Google Software Engineer JD.
   - Show matches tagged with layer badges: **Exact** (1.0), **Alias** (0.9), and **Semantic** ($0.8 \times \text{sim}$).
   - View missing skills ranked by prerequisites (e.g., learn Docker before Kubernetes).
   - Click **View 4x6 Matrix Heatmap**: display the full non-constant score grid showing how candidate scores vary across roles.
6. **Show Green Pytest**:
   - Run `python -m pytest -v` in terminal showing **135 passed tests**.

