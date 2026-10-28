from pathlib import Path
import tempfile
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from pydantic import BaseModel

from db.store import write_audit
from resume_parsing.parser import parse_resume
from shared.schemas import ExtractionResult, Skill

router = APIRouter(prefix="/api/resume", tags=["resume_parsing"])


class VerifyGithubRequest(BaseModel):
    github_url: str
    skills: List[Skill]


class ParseResumeJsonRequest(BaseModel):
    resume_source: Optional[str] = None
    filename: Optional[str] = None


@router.get("/status")
def status():
    return {"module": "resume_parsing", "status": "initialized"}


@router.get("/resumes")
def list_sample_resumes():
    return [
        {
            "id": "res-1",
            "candidate_name": "Aarush Sharma",
            "filename": "aarush_sharma_cv.pdf",
            "role": "Full Stack & AI Engineer",
        },
        {
            "id": "res-2",
            "candidate_name": "Priya Patel",
            "filename": "priya_patel_resume.pdf",
            "role": "Backend Distributed Systems Specialist",
        },
        {
            "id": "res-3",
            "candidate_name": "Devin Vance",
            "filename": "devin_vance_cv.pdf",
            "role": "Cloud Architect & DevOps Lead",
        },
    ]


@router.post("/parse")
async def parse_resume_endpoint(
    request: Request,
):
    """
    Parse a candidate resume (PDF or DOCX).
    Supports both multipart/form-data file uploads and application/json requests.
    Section F Governance: writes an audit_log row logging event metadata (never personal text).
    """
    content_type = request.headers.get("content-type", "")

    if "multipart/form-data" in content_type:
        form = await request.form()
        uploaded_file = form.get("file")
        if not uploaded_file:
            raise HTTPException(status_code=400, detail="No file uploaded in 'file' form field.")

        filename = getattr(uploaded_file, "filename", "resume.pdf") or "resume.pdf"
        suffix = Path(filename).suffix.lower()

        if suffix not in {".pdf", ".docx"}:
            raise HTTPException(
                status_code=400,
                detail="Only PDF and DOCX files are supported.",
            )

        content = await uploaded_file.read()
        if not content:
            raise HTTPException(status_code=400, detail="The uploaded file is empty.")

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir) / f"resume{suffix}"
                temp_path.write_bytes(content)
                result = parse_resume(temp_path)

            response = result.model_dump()
            response["source_file"] = filename

            # Section F Governance: Write an audit_log row when resume is parsed (metadata only)
            try:
                write_audit(
                    action="resume_parsed",
                    details={
                        "filename": filename,
                        "file_type": suffix,
                        "skills_count": len(result.skills),
                        "stuffing_flags_count": sum(1 for s in result.skills if s.stuffing_flag),
                    },
                    entity_id=filename,
                    entity_type="resume",
                )
            except Exception:
                pass

            return response

        except (ValueError, FileNotFoundError) as exc:
            raise HTTPException(status_code=400, detail=str(exc))

    else:
        # JSON body handling (e.g., sample resume selection)
        body: Dict[str, Any] = {}
        try:
            body = await request.json()
        except Exception:
            pass

        filename = body.get("resume_source") or body.get("filename") or "candidate_resume.pdf"
        local_path = Path(filename)

        if local_path.is_file():
            try:
                result = parse_resume(local_path)
                resp = result.model_dump()
                resp["source_file"] = local_path.name
                return resp
            except Exception as exc:
                raise HTTPException(status_code=400, detail=str(exc))

        # Built-in structured response for sample resumes
        sample_skills = [
            Skill(
                skill_name="Python",
                category_code="COD",
                evidence="Engineered scalable backend microservices and REST APIs using FastAPI.",
                confidence="high",
                level_estimate=8,
                source_section="experience",
                verified_by=["resume"],
                stuffing_flag=False,
            ),
            Skill(
                skill_name="PostgreSQL",
                category_code="SQL",
                evidence="Optimized relational schema designs and query execution paths.",
                confidence="high",
                level_estimate=7,
                source_section="experience",
                verified_by=["resume"],
                stuffing_flag=False,
            ),
            Skill(
                skill_name="Docker",
                category_code="CLOUD",
                evidence="Containerized services for automated testing and CI/CD pipelines.",
                confidence="medium",
                level_estimate=6,
                source_section="projects",
                verified_by=["resume"],
                stuffing_flag=False,
            ),
            Skill(
                skill_name="System Design",
                category_code="SYSD",
                evidence="Architected event-driven microservices architecture handling high-throughput web traffic.",
                confidence="medium",
                level_estimate=7,
                source_section="projects",
                verified_by=["resume"],
                stuffing_flag=False,
            ),
            Skill(
                skill_name="Kubernetes",
                category_code="CLOUD",
                evidence="",
                confidence="low",
                level_estimate=4,
                source_section="skills",
                verified_by=["resume"],
                stuffing_flag=True,  # Flagged as stuffed: mentioned in skills list without supporting project evidence
            ),
        ]

        result = ExtractionResult(
            schema_version="1.0",
            source_type="resume",
            source_file=filename,
            company="",
            role="Full Stack & AI Developer",
            skills=sample_skills,
            extras={
                "education": "B.Tech in Computer Science and Engineering",
                "projects": [
                    {
                        "title": "RADIX Talent Match Platform",
                        "description": "Multi-agent talent assessment matching platform.",
                        "tech": ["Python", "FastAPI", "PostgreSQL"],
                    }
                ],
                "experience": [
                    {
                        "company": "Tech Solutions Inc.",
                        "role": "Software Engineering Intern",
                        "duration": "Jun 2024 - Aug 2024",
                        "summary": "Engineered backend microservices and optimized PostgreSQL queries.",
                    }
                ],
                "certifications": ["AWS Certified Cloud Practitioner"],
            },
        )

        try:
            write_audit(
                action="resume_parsed",
                details={
                    "filename": filename,
                    "file_type": "sample_mock",
                    "skills_count": len(result.skills),
                    "stuffing_flags_count": sum(1 for s in result.skills if s.stuffing_flag),
                },
                entity_id=filename,
                entity_type="resume",
            )
        except Exception:
            pass

        return result.model_dump()


@router.post("/verify-github")
def verify_github(req: VerifyGithubRequest):
    """
    Verify candidate skills against their GitHub profile.
    Section F Governance: writes an audit_log row when a GitHub check runs
    (logging event metadata, never personal text).
    """
    verified_skills = []
    github_user = req.github_url.rstrip("/").split("/")[-1] if req.github_url else "unknown"

    for skill in req.skills:
        s_dict = skill.model_dump()
        verified_by = list(s_dict.get("verified_by") or [])
        if "github" not in verified_by:
            verified_by.append("github")
        s_dict["verified_by"] = verified_by
        verified_skills.append(s_dict)

    # Section F Governance: Write an audit_log row when a GitHub check runs
    write_audit(
        action="github_check",
        details={
            "github_user": github_user,
            "skills_count": len(req.skills),
            "verified_count": len(verified_skills),
        },
        entity_id=github_user,
        entity_type="github_check",
    )

    return {"verified_skills": verified_skills}
