"""Seed the 4 sample candidate resumes and 6 sample job descriptions."""
from pathlib import Path
import json

from app.shared.schemas import Skill, Profile, ExtractionResult

DATA_DIR = Path(__file__).resolve().parent
PROFILES_DIR = DATA_DIR / "profiles"
JDS_DIR = DATA_DIR / "jds"
CACHE_DIR = DATA_DIR / "cache"

for d in [PROFILES_DIR, JDS_DIR, CACHE_DIR]:
    d.mkdir(parents=True, exist_ok=True)

def seed_all():
    # 1. Four Sample Candidate Profiles
    profiles = [
        Profile(
            profile_id="candidate_1_all_rounder",
            name="Alex Chen (All-Rounder)",
            email="alex.chen@example.com",
            education="B.S. in Computer Science, State University",
            github_url="https://github.com/alexchen-dev",
            preferred_roles=["Software Engineer", "Full Stack Developer"],
            skills=[
                Skill(skill_name="Python", category_code="COD", confidence="high"),
                Skill(skill_name="TypeScript", category_code="COD", confidence="high"),
                Skill(skill_name="React", category_code="SWE", confidence="high"),
                Skill(skill_name="Node.js", category_code="SWE", confidence="high"),
                Skill(skill_name="SQL", category_code="SQL", confidence="medium"),
                Skill(skill_name="Docker", category_code="CLOUD", confidence="medium"),
                Skill(skill_name="Git", category_code="SWE", confidence="high"),
                Skill(skill_name="REST API", category_code="SWE", confidence="high"),
                Skill(skill_name="Data Structures", category_code="DSA", confidence="high"),
                Skill(skill_name="System Design", category_code="SYSD", confidence="medium"),
                Skill(skill_name="Linux", category_code="OS", confidence="medium"),
                Skill(skill_name="Communication", category_code="COMM", confidence="high"),
            ]
        ),
        Profile(
            profile_id="candidate_2_data_analyst",
            name="Priya Patel (Data & AI Analyst)",
            email="priya.patel@example.com",
            education="M.S. in Data Science, Tech Institute",
            github_url="https://github.com/priyapatel-data",
            preferred_roles=["Data Engineer", "Machine Learning Engineer"],
            skills=[
                Skill(skill_name="Python", category_code="COD", confidence="high"),
                Skill(skill_name="SQL", category_code="SQL", confidence="high"),
                Skill(skill_name="PostgreSQL", category_code="SQL", confidence="high"),
                Skill(skill_name="Pandas", category_code="AI", confidence="high"),
                Skill(skill_name="NumPy", category_code="AI", confidence="high"),
                Skill(skill_name="Machine Learning", category_code="AI", confidence="high"),
                Skill(skill_name="Deep Learning", category_code="AI", confidence="medium"),
                Skill(skill_name="Statistics", category_code="APTI", confidence="high"),
                Skill(skill_name="BigQuery", category_code="CLOUD", confidence="medium"),
                Skill(skill_name="NLP", category_code="AI", confidence="medium"),
                Skill(skill_name="Data Structures", category_code="DSA", confidence="medium"),
                Skill(skill_name="Git", category_code="SWE", confidence="medium"),
            ]
        ),
        Profile(
            profile_id="candidate_3_oracle_support",
            name="Rohan Verma (Support & Database Associate)",
            email="rohan.verma@example.com",
            education="B.Tech in Information Technology",
            github_url="https://github.com/rohanverma-it",
            preferred_roles=["Database Administrator", "Support Engineer", "Java Developer"],
            skills=[
                Skill(skill_name="SQL", category_code="SQL", confidence="high"),
                Skill(skill_name="Oracle", category_code="SQL", confidence="high"),
                Skill(skill_name="DBMS", category_code="SQL", confidence="high"),
                Skill(skill_name="Linux", category_code="OS", confidence="high"),
                Skill(skill_name="Java", category_code="COD", confidence="high"),
                Skill(skill_name="Spring Boot", category_code="SWE", confidence="medium"),
                Skill(skill_name="Computer Networks", category_code="NETW", confidence="medium"),
                Skill(skill_name="Operating Systems", category_code="OS", confidence="high"),
                Skill(skill_name="Communication", category_code="COMM", confidence="high"),
                Skill(skill_name="Aptitude", category_code="APTI", confidence="medium"),
            ]
        ),
        Profile(
            profile_id="candidate_4_systems_engineer",
            name="Marcus Vance (Systems & Cloud Engineer)",
            email="marcus.vance@example.com",
            education="B.S. in Computer Systems Engineering",
            github_url="https://github.com/marcusvance-ops",
            preferred_roles=["Cloud Architect", "DevOps Engineer", "Systems Engineer"],
            skills=[
                Skill(skill_name="Linux", category_code="OS", confidence="high"),
                Skill(skill_name="Operating Systems", category_code="OS", confidence="high"),
                Skill(skill_name="Computer Networks", category_code="NETW", confidence="high"),
                Skill(skill_name="Docker", category_code="CLOUD", confidence="high"),
                Skill(skill_name="Kubernetes", category_code="CLOUD", confidence="high"),
                Skill(skill_name="AWS", category_code="CLOUD", confidence="high"),
                Skill(skill_name="Google Cloud", category_code="CLOUD", confidence="medium"),
                Skill(skill_name="Terraform", category_code="CLOUD", confidence="high"),
                Skill(skill_name="Microservices", category_code="SYSD", confidence="high"),
                Skill(skill_name="Go", category_code="COD", confidence="medium"),
                Skill(skill_name="C++", category_code="COD", confidence="medium"),
                Skill(skill_name="System Design", category_code="SYSD", confidence="high"),
                Skill(skill_name="Git", category_code="SWE", confidence="high"),
            ]
        ),
    ]

    for p in profiles:
        file_path = PROFILES_DIR / f"{p.profile_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(p.model_dump_json(indent=2))
        cache_path = CACHE_DIR / f"{p.profile_id}.json"
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(p.model_dump_json(indent=2))

    # 2. Six Sample Job Descriptions (Google, Microsoft, Oracle Financial Services Software - 2 roles each)
    jds = [
        ExtractionResult(
            source_type="jd",
            source_file="google_software_engineer.pdf",
            company="Google",
            role="Software Engineer, Core Systems",
            skills=[
                Skill(skill_name="Python", category_code="COD", importance="must_have", confidence="high"),
                Skill(skill_name="Data Structures", category_code="DSA", importance="must_have", confidence="high"),
                Skill(skill_name="System Design", category_code="SYSD", importance="must_have", confidence="high"),
                Skill(skill_name="Linux", category_code="OS", importance="must_have", confidence="high"),
                Skill(skill_name="Go", category_code="COD", importance="nice_to_have", confidence="medium"),
                Skill(skill_name="C++", category_code="COD", importance="nice_to_have", confidence="medium"),
                Skill(skill_name="Docker", category_code="CLOUD", importance="nice_to_have", confidence="medium"),
                Skill(skill_name="Git", category_code="SWE", importance="nice_to_have", confidence="high"),
            ]
        ),
        ExtractionResult(
            source_type="jd",
            source_file="google_cloud_architect.pdf",
            company="Google",
            role="Cloud Infrastructure Architect",
            skills=[
                Skill(skill_name="Google Cloud", category_code="CLOUD", importance="must_have", confidence="high"),
                Skill(skill_name="Kubernetes", category_code="CLOUD", importance="must_have", confidence="high"),
                Skill(skill_name="Docker", category_code="CLOUD", importance="must_have", confidence="high"),
                Skill(skill_name="Computer Networks", category_code="NETW", importance="must_have", confidence="high"),
                Skill(skill_name="Terraform", category_code="CLOUD", importance="nice_to_have", confidence="high"),
                Skill(skill_name="Linux", category_code="OS", importance="nice_to_have", confidence="high"),
                Skill(skill_name="Python", category_code="COD", importance="nice_to_have", confidence="medium"),
                Skill(skill_name="Microservices", category_code="SYSD", importance="nice_to_have", confidence="high"),
            ]
        ),
        ExtractionResult(
            source_type="jd",
            source_file="microsoft_fullstack.pdf",
            company="Microsoft",
            role="Full Stack Cloud Developer",
            skills=[
                Skill(skill_name="TypeScript", category_code="COD", importance="must_have", confidence="high"),
                Skill(skill_name="React", category_code="SWE", importance="must_have", confidence="high"),
                Skill(skill_name="Node.js", category_code="SWE", importance="must_have", confidence="high"),
                Skill(skill_name="Azure", category_code="CLOUD", importance="must_have", confidence="high"),
                Skill(skill_name="SQL", category_code="SQL", importance="nice_to_have", confidence="medium"),
                Skill(skill_name="REST API", category_code="SWE", importance="nice_to_have", confidence="high"),
                Skill(skill_name="Git", category_code="SWE", importance="nice_to_have", confidence="high"),
                Skill(skill_name="Communication", category_code="COMM", importance="nice_to_have", confidence="high"),
            ]
        ),
        ExtractionResult(
            source_type="jd",
            source_file="microsoft_data_engineer.pdf",
            company="Microsoft",
            role="Senior Data Platform Engineer",
            skills=[
                Skill(skill_name="Python", category_code="COD", importance="must_have", confidence="high"),
                Skill(skill_name="SQL", category_code="SQL", importance="must_have", confidence="high"),
                Skill(skill_name="Azure", category_code="CLOUD", importance="must_have", confidence="high"),
                Skill(skill_name="Machine Learning", category_code="AI", importance="must_have", confidence="high"),
                Skill(skill_name="Pandas", category_code="AI", importance="nice_to_have", confidence="high"),
                Skill(skill_name="NumPy", category_code="AI", importance="nice_to_have", confidence="medium"),
                Skill(skill_name="Data Structures", category_code="DSA", importance="nice_to_have", confidence="high"),
                Skill(skill_name="Statistics", category_code="APTI", importance="nice_to_have", confidence="medium"),
            ]
        ),
        ExtractionResult(
            source_type="jd",
            source_file="oracle_database_engineer.pdf",
            company="Oracle Financial Services Software",
            role="Database Infrastructure Engineer",
            skills=[
                Skill(skill_name="SQL", category_code="SQL", importance="must_have", confidence="high"),
                Skill(skill_name="Oracle", category_code="SQL", importance="must_have", confidence="high"),
                Skill(skill_name="DBMS", category_code="SQL", importance="must_have", confidence="high"),
                Skill(skill_name="Linux", category_code="OS", importance="must_have", confidence="high"),
                Skill(skill_name="Computer Networks", category_code="NETW", importance="nice_to_have", confidence="medium"),
                Skill(skill_name="Java", category_code="COD", importance="nice_to_have", confidence="medium"),
                Skill(skill_name="Operating Systems", category_code="OS", importance="nice_to_have", confidence="high"),
                Skill(skill_name="Communication", category_code="COMM", importance="nice_to_have", confidence="high"),
            ]
        ),
        ExtractionResult(
            source_type="jd",
            source_file="oracle_java_engineer.pdf",
            company="Oracle Financial Services Software",
            role="Enterprise Java Application Developer",
            skills=[
                Skill(skill_name="Java", category_code="COD", importance="must_have", confidence="high"),
                Skill(skill_name="Spring Boot", category_code="SWE", importance="must_have", confidence="high"),
                Skill(skill_name="SQL", category_code="SQL", importance="must_have", confidence="high"),
                Skill(skill_name="Object-Oriented Design", category_code="OOD", importance="must_have", confidence="high"),
                Skill(skill_name="REST API", category_code="SWE", importance="nice_to_have", confidence="high"),
                Skill(skill_name="Oracle", category_code="SQL", importance="nice_to_have", confidence="medium"),
                Skill(skill_name="Git", category_code="SWE", importance="nice_to_have", confidence="high"),
                Skill(skill_name="Microservices", category_code="SYSD", importance="nice_to_have", confidence="medium"),
            ]
        ),
    ]

    for jd in jds:
        slug = jd.source_file.replace(".pdf", "")
        file_path = JDS_DIR / f"{slug}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(jd.model_dump_json(indent=2))
        cache_path = CACHE_DIR / f"{slug}.json"
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(jd.model_dump_json(indent=2))

    print(f"Seeded {len(profiles)} sample profiles and {len(jds)} sample JDs!")

if __name__ == "__main__":
    seed_all()

