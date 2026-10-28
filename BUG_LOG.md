# GapMap Integration & Bug Log

> Maintained by Aarush (Scrum Master & Integration Lead)
> Purpose: Record daily integration issues, contract mismatches, and resolutions across modules.

---

## 📋 Integration Status Matrix

| Module | Owner | Contract Schema | Status | Last Checked |
| :--- | :--- | :--- | :--- | :--- |
| **Module 1: JD Analytics** | Samiksha | `ExtractionResult` (`source_type='jd'`) | Merged & Verified (135/135 tests passing) | 2026-10-28 |
| **Module 2: Resume Parsing** | Arushi | `ExtractionResult` (`source_type='resume'`) | Merged & Verified (61/61 tests passing) | 2026-10-28 |
| **Module 3: Profile Contract & Store** | Aarush | `Profile`, `Skill`, `db/store.py` | Complete & Passing | 2026-10-27 |
| **Module 4: Talent Check** | Aditya | `TalentCheckResult`, `SkillsetGap` | Merged & Verified (30/30 tests passing) | 2026-10-27 |
| **Module 5: Skill Matching** | Anjali | `MatchResult`, `MatchedSkill`, `MissingSkill` | Merged & Verified (61/61 tests passing) | 2026-10-28 |

---

## 🐛 Bug & Issue Tracker

### Issue #001: Missing GitHub Verification Endpoint in Backend
- **Severity**: Medium
- **Component**: `resume_parsing/router.py` / `frontend/src/api.ts`
- **Description**: Frontend Profile form has GitHub verification button with consent, but backend was missing the `/api/resume/verify-github` route, causing fallback to mock.
- **Resolution**: Implemented `POST /api/resume/verify-github` and added governance audit logging (`github_check` action) without personal text.
- **Status**: ✅ Resolved & Tested.

### Issue #002: Supabase Connectivity Dependency for Talent Check
- **Severity**: Low
- **Component**: `talent_check`
- **Description**: Relying on live Supabase for the 117-company benchmark dataset could cause latency or network failures during live demo.
- **Resolution**: Stored full 117-company benchmark dataset in `backend/data/talent_check_company_skillsets.json` for 100% offline, instant local evaluation.
- **Status**: ✅ Resolved.

### Issue #003: Contract Verification Between Pipeline Stages
- **Severity**: High
- **Component**: `tests/test_contracts.py`
- **Description**: Need automated contract testing ensuring that real output from one module flows cleanly into the next without schema breakage.
- **Resolution**: Created `tests/test_contracts.py` testing Resume → Profile, Profile → Talent Check, and Profile + JD → Skill Matching.
- **Status**: ✅ Resolved (18/18 tests passing).

### Issue #004: Skill Matching & Heatmap Matrix Integration (Module 5)
- **Severity**: Medium
- **Component**: `skill_matching` / `db/store.py` / `frontend/src/modules/matching`
- **Description**: Module 5 (Skill Matching) needed 3-layer matching (Exact, Alias, Semantic), precomputed embeddings vector vocabulary, explainable gaps with prerequisite dependencies, a 4x6 non-constant matrix heatmap, and dynamic store resolution.
- **Resolution**:
  - Integrated 3-layer matching engine (`Exact` 1.0, `Alias` 0.9 via `aliases.json`, `Semantic` 0.8 × sim via `embeddings.py`).
  - Added `list_jds()` and robust fallback filename/stem search to `db/store.py`.
  - Seeded 4 sample candidate profiles and 6 sample JDs with precomputed numpy vocab index in `backend/data/cache/`.
  - Integrated full UI with `ScoreRing`, `MatchedSkillsTable`, `MissingSkillsList` (ranked by prerequisites and score impact), candidate/JD selectors, and interactive 4x6 Matrix Heatmap page.
  - Resolved circular import in `backend/app/__init__.py` and bridged import namespaces (`app.db`, `app.shared`, `app.skill_matching`).
  - All 52 backend tests passing, frontend builds cleanly in 2.3s.
- **Status**: ✅ Resolved.

### Issue #005: Resume Parsing, Privacy Redaction & Stuffing Detection (Module 2)
- **Severity**: Medium
- **Component**: `resume_parsing` (`parser.py`, `privacy.py`, `sections.py`, `stuffing.py`, `ai_extractor.py`, `router.py`) / `frontend/src/modules/resume/ResumePage.tsx`
- **Description**: Module 2 (Arushi's work on branch `feature/resume-parsing`) needed to be pulled and integrated. Required merging file upload parsing (`POST /api/resume/parse` supporting `.pdf` and `.docx`), regex PII scrubbing (`scrub_pii`), resume section splitting, strict word-boundary stuffing detection (checking Project and Experience sections for evidence, demoting unevidenced skills), and Section F governance audit logging.
- **Resolution**:
  - Pulled Arushi's work from branch `origin/feature/resume-parsing`.
  - Added dependencies `pdfplumber>=0.11.0`, `python-docx>=1.1.0`, `python-multipart>=0.0.9`, `langchain-openai>=1.0.0`, `langchain-google-genai>=4.0.0` to root and backend `requirements.txt`.
  - Unified `resume_parsing/router.py` to support multipart file upload parsing (`.pdf`, `.docx`), JSON payload parsing, sample resumes listing, and GitHub profile verification with Section F audit logging (`write_audit`).
  - Added circuit breaker in `skill_matching/embeddings.py` to prevent network timeouts when offline.
  - Implemented real drag-and-drop file upload UI, stuffing warning badges, and tabs in `frontend/src/modules/resume/ResumePage.tsx`.
  - Created comprehensive test suite in `tests/test_resume_parsing.py` testing PII redaction, section parsing, stuffing boundaries, offline AI extraction, and endpoints.
  - All 61 tests passing; frontend built cleanly with 0 errors.
- **Status**: ✅ Resolved & Verified (61/61 tests passing).

### Issue #006: JD Analytics Integration & Dual-Model AI Extraction (Module 1)
- **Severity**: High
- **Component**: `backend/app/jd_analytics` (`pipeline.py`, `router.py`) / `shared` (`docreader.py`, `llm.py`, `schemas.py`) / `frontend/src/modules/jd/JdPage.tsx`
- **Description**: Module 1 (Samiksha's work on branch `feature/jd-analytics`, commit `2d211c55b83afd7bf649cac6831e47a891c1ca30`) needed to be pulled and fully integrated into the GapMap project.
- **Resolution**:
  - Resolved 3-way merge conflicts across `backend/app/shared/docreader.py`, `backend/app/shared/llm.py`, and `backend/app/shared/schemas.py`.
  - Linked root `jd_analytics/router.py` directly to `backend/app/jd_analytics/router.py` ensuring all endpoints (`GET /api/jds`, `GET /api/jd/jds`, `GET /api/jd/status`, `POST /api/jd/analyze`) are properly registered with `main.py`.
  - Preserved dual-model parallel extraction (`Gemini` + `Mistral`) with automatic category conflict resolution, confidence downgrading, and disagreement auditing.
  - Integrated 6 pre-cached benchmark JD files (Google LLC, Microsoft Corporation, Oracle Financial Services in `.pdf` and `.docx` format) with SHA-256 caching in `backend/data/cache/` for instant offline testing and live demos.
  - Unified `analyze_jd` endpoint to support multipart file uploads (`.pdf`, `.docx`), sample filenames, and raw pasted text.
  - Implemented comprehensive frontend UI in `JdPage.tsx` with sample selector, drag-and-drop upload, raw text input, dual-model agreement badges, and category breakdown.
  - All 135 tests passing across the backend suite; frontend TypeScript builds in 2.89s with 0 errors.
- **Status**: ✅ Resolved & Verified (135/135 tests passing).

---

## 🔄 Daily Stand-up Notes
- **Yesterday**: Created repository structure, schemas v1.0, database store with JSON fallback, profile endpoints, and app shell.
- **Today**: Merged Aditya's Talent Check (Module 4), integrated Anjali's Skill Matching & 4x6 Matrix Heatmap (Module 5), pulled and integrated Arushi's Resume Parsing (Module 2), and pulled and fully integrated Samiksha's JD Analytics (Module 1). Achieved 135/135 passing tests and 0-error frontend build.
- **Next**: Finalize end-to-end integration walkthrough and prepare presentation demo.
