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
    base = Path(__file__).resolve().parent.parent / "data" / "cache"
    base.mkdir(parents=True, exist_ok=True)
    return base / f"github_{username.lower()}.json"


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
        except Exception as e:
            # Network or timeout failure: fallback to user handle
            user_data = user_data or {"login": username, "public_repos": 0}
            repos = repos or []

    # Cache response data
    try:
        cache_file.write_text(
            json.dumps({"user": user_data, "repos": repos}, indent=2),
            encoding="utf-8",
        )
    except Exception:
        pass

    # Extract languages and keywords across repositories
    detected_keywords: set[str] = set()
    repo_summaries: List[Dict[str, Any]] = []
    top_languages: Dict[str, int] = {}

    for repo in repos:
        name = repo.get("name", "")
        lang = repo.get("language")
        topics = repo.get("topics") or []
        desc = (repo.get("description") or "").lower()

        if lang:
            detected_keywords.add(lang.lower())
            top_languages[lang] = top_languages.get(lang, 0) + 1

        for topic in topics:
            detected_keywords.add(topic.lower())

        # Check description words
        for token in re.findall(r"\b[a-zA-Z0-9+#.-]+\b", desc):
            detected_keywords.add(token.lower())

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
    existing_skill_names = {s.get("skill_name", "").lower() for s in working_skills}

    for s in working_skills:
        s_name = s.get("skill_name", "").lower()
        s_cat = s.get("category_code", "")

        # Check for direct or keyword match in detected keywords
        is_matched = False
        matching_repo = None

        for kw in detected_keywords:
            if kw in s_name or s_name in kw:
                is_matched = True
                break

        # Check if any repo specifically used this language
        for repo in repo_summaries:
            r_lang = (repo.get("language") or "").lower()
            if r_lang and (r_lang in s_name or s_name in r_lang):
                is_matched = True
                matching_repo = repo
                break

        if is_matched:
            verified_by = list(s.get("verified_by") or [])
            if "github" not in verified_by:
                verified_by.append("github")
            s["verified_by"] = verified_by

            # Clear stuffing flag since real code repositories prove practical use!
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

            repo_name = matching_repo["name"] if matching_repo else (repo_summaries[0]["name"] if repo_summaries else "public repo")
            repo_lang = matching_repo["language"] if matching_repo else "code"
            s["evidence"] = f"Verified in public GitHub repository '{repo_name}' ({repo_lang})."
            verified_count += 1

    # Also discover new verified skills from the candidate's GitHub repositories!
    for kw, mapping in GITHUB_SKILL_MAP.items():
        if kw in detected_keywords:
            canonical_name = mapping["name"]
            cat_code = mapping["code"]
            if canonical_name.lower() not in existing_skill_names:
                working_skills.append({
                    "skill_name": canonical_name,
                    "category_code": cat_code,
                    "evidence": f"Demonstrated in public GitHub repository ({kw}).",
                    "confidence": "high",
                    "level_estimate": 7,
                    "source_section": "github",
                    "verified_by": ["github"],
                    "stuffing_flag": False,
                })
                existing_skill_names.add(canonical_name.lower())
                verified_count += 1

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
