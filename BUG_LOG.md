# GapMap Integration & Bug Log

> Maintained by Aarush (Scrum Master & Integration Lead)
> Purpose: Record daily integration issues, contract mismatches, and resolutions across modules.

---

## 📋 Integration Status Matrix

| Module | Owner | Contract Schema | Status | Last Checked |
| :--- | :--- | :--- | :--- | :--- |
| **Module 1: JD Analytics** | Samiksha | `ExtractionResult` (`source_type='jd'`) | Contract Verified | 2026-10-27 |
| **Module 2: Resume Parsing** | Arushi | `ExtractionResult` (`source_type='resume'`) | Contract Verified | 2026-10-27 |
| **Module 3: Profile Contract & Store** | Aarush | `Profile`, `Skill`, `db/store.py` | Complete & Passing | 2026-10-27 |
| **Module 4: Talent Check** | Aditya | `TalentCheckResult`, `SkillsetGap` | Merged & Verified (30/30 tests passing) | 2026-10-27 |
| **Module 5: Skill Matching** | Anjali | `MatchResult`, `MatchedSkill`, `MissingSkill` | Merged & Verified (52/52 tests passing) | 2026-10-27 |

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
- **Status**: ✅ Resolved & Verified (52/52 tests passing).

---

## 🔄 Daily Stand-up Notes
- **Yesterday**: Created repository structure, schemas v1.0, database store with JSON fallback, profile endpoints, and app shell.
- **Today**: Pushed repository to GitHub, merged Aditya's Talent Check module, integrated Anjali's Skill Matching & 4x6 Heatmap Matrix module, resolved store/router contracts, and achieved 52/52 passing backend tests and clean frontend build.
- **Next**: Coordinate with Samiksha (JD Analytics) and Arushi (Resume Parsing) to merge remaining modules.

