# GapMap (RADIX Talent Match)

> An automated ATS & talent readiness platform that parses resumes, analyzes job descriptions, verifies candidate skills, and pinpoints competency gaps against company hiring bars.

---

## 👥 Team & Modules

- **Aarush (Owner / Scrum Master)**: Profile Contract, Supabase & JSON Fallback Store, App Shell, Core Schemas (`schemas.py`)
- **Samiksha**: Module 1 - JD Analytics (`jd_analytics/`)
- **Arushi**: Module 2 - Resume Parsing (`resume_parsing/`)
- **Aditya**: Module 4 - Talent Check (`talent_check/`)
- **Anjali**: Module 5 - Skill Matching (`skill_matching/`)

---

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- (Optional) Docker and Docker Compose

### 1. Backend Setup

```bash
# Clone the repository
git clone https://github.com/aarushgoel025/GapMap.git
cd GapMap

# Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
copy .env.example .env   # On Linux/macOS: cp .env.example .env

# Run FastAPI backend
uvicorn backend.app.main:app --reload --port 8000
```
- API Root: http://localhost:8000
- Interactive Swagger API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```
- Frontend UI: http://localhost:5173

### Talent Check API

- `GET /api/talent-check/companies` lists available company benchmarks.
- `POST /api/talent-check` accepts a `company` and either a `profile` or `profile_id`.
- `POST /api/talent-check/whatif` accepts the same profile input plus `changes`, a list of `{ "category_code": "COD", "new_level": 8 }` simulations. Simulations do not update the stored profile.

The readiness response includes a 0-100 score, a label, and per-category required and candidate levels. The time-to-ready estimate is zero for candidates already labeled ready; the current model does not estimate learning time.

---

## 🐳 Docker Deployment

To launch the entire full-stack application with one command:

```bash
docker compose up --build
```

---

## 🧪 Running Tests

```bash
pytest -v
```

---

## 🌿 Git Branching Workflow for Teammates

To avoid merge conflicts, each team member works in their dedicated branch:

| Module / Role | Dedicated Branch | Working Directory |
| :--- | :--- | :--- |
| **Samiksha (JD Analytics)** | `feature/jd-analytics` | `jd_analytics/`, `frontend/src/modules/jd/` |
| **Arushi (Resume Parsing)** | `feature/resume-parsing` | `resume_parsing/`, `frontend/src/modules/resume/` |
| **Aarush (Profile & Store)** | `feature/profile-store` | `profile/`, `db/`, `shared/`, `frontend/src/modules/profile/` |
| **Aditya (Talent Check)** | `feature/talent-check` | `talent_check/`, `frontend/src/modules/talent/` |
| **Anjali (Skill Matching)** | `feature/skill-matching` | `skill_matching/`, `frontend/src/modules/matching/` |

### How to work on your branch:
1. `git checkout -b <your-branch-name>`
2. Make your edits inside your module folder
3. `git add .` and `git commit -m "feat(<module>): description of changes"`
4. `git push origin <your-branch-name>`
5. Create a Pull Request into `main` for Aarush to review and merge!
