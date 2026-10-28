"""FastAPI router for JD Analytics: GET /api/jds, GET /api/jd/jds, and POST /api/jd/analyze."""
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from pydantic import BaseModel

from app.jd_analytics import pipeline
from app.shared.docreader import DocumentReadError
from app.shared.schemas import ExtractionResult

router = APIRouter(prefix="/api", tags=["jd_analytics"])

ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB is far more than any JD


# schemas.py has no model for "list of sample files", so this small response model lives in our module.
class JDFile(BaseModel):
    filename: str
    cached: bool  # True if an analysis is already cached (the demo will be instant)


class JDListing(BaseModel):
    files: list[JDFile]


@router.get("/status")
@router.get("/jd/status")
def status():
    """Status endpoint for health check and teammate router verification."""
    return {"module": "jd_analytics", "status": "initialized"}


@router.get("/jds", response_model=JDListing)
def list_jds() -> JDListing:
    """List the sample JD files in backend/data/jds."""
    files: list[JDFile] = []
    for p in pipeline.list_jd_files():
        files.append(JDFile(filename=p.name, cached=pipeline.get_cached(p) is not None))
    return JDListing(files=files)


@router.get("/jd/jds")
def list_sample_jds() -> List[Dict[str, Any]]:
    """List sample JDs formatted for frontend display."""
    items: List[Dict[str, Any]] = []
    for idx, p in enumerate(pipeline.list_jd_files()):
        cached = pipeline.get_cached(p)
        company = ""
        role = ""
        snippet = ""
        if cached:
            company = cached.company
            role = cached.role
            top_skills = [s.skill_name for s in cached.skills[:4]]
            snippet = f"Requirements: {', '.join(top_skills)} and more."
        if not company and " - " in p.stem:
            parts = p.stem.split(" - ", 1)
            company = parts[0]
            role = parts[1]
        items.append({
            "id": f"jd-{idx + 1}",
            "title": role or p.stem,
            "company": company or "Benchmark Company",
            "filename": p.name,
            "snippet": snippet or f"Target benchmark JD for {p.stem}",
            "cached": cached is not None,
        })
    return items


# Plain `def` on purpose: FastAPI runs it in a worker thread, so the slow LLM calls do not block the server.
@router.post("/jd/analyze", response_model=ExtractionResult)
def analyze_jd(
    file: Optional[UploadFile] = File(None, description="A JD as .pdf or .docx"),
    sample: Optional[str] = Form(None, description="File name of a sample JD from GET /api/jds"),
    text: Optional[str] = Form(None, description="Raw JD text pasted by user"),
    refresh: bool = Query(False, description="Ignore the cache and run the models again"),
) -> ExtractionResult:
    """Analyze an uploaded JD, a sample JD by file name, or custom text."""
    sample = (sample or "").strip()  # Swagger often adds spaces around a pasted name
    has_upload = file is not None and bool(file.filename)
    has_sample = bool(sample)
    has_text = bool(text and text.strip())

    input_count = sum([has_upload, has_sample, has_text])
    if input_count != 1:
        raise HTTPException(400, "Send either an uploaded file or a sample file name, not both and not neither.")

    try:
        if has_sample:
            return _analyze_sample(sample, refresh)
        if has_text:
            assert text is not None
            return pipeline.analyze_text(text.strip(), source_file="custom_jd.txt")
        assert file is not None
        return _analyze_upload(file, refresh)
    except HTTPException:
        raise
    except DocumentReadError as e:
        raise HTTPException(422, str(e))
    except pipeline.ExtractionError as e:
        raise HTTPException(502, str(e))


def _analyze_sample(sample: str, refresh: bool) -> ExtractionResult:
    name = Path(sample).name
    if name != sample:  # blocks paths such as ../../secret.pdf
        raise HTTPException(400, "Use only the file name of a sample JD, without any folders.")
    path = pipeline.jd_dir() / name
    if path.suffix.lower() not in ALLOWED_EXTENSIONS or not path.is_file():
        raise HTTPException(404, f"Sample JD '{name}' was not found. Call GET /api/jds to see the available files.")
    return pipeline.analyze_file(path, refresh=refresh)


def _analyze_upload(file: UploadFile, refresh: bool) -> ExtractionResult:
    name = Path(file.filename or "").name
    suffix = Path(name).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(400, f"Unsupported file type '{suffix}'. Please upload a .pdf or .docx file.")
    data = file.file.read(MAX_UPLOAD_BYTES + 1)
    if not data:
        raise HTTPException(400, "The uploaded file is empty.")
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "The uploaded file is too large (limit 10 MB).")

    # Save to a temp file so the document readers can open it; the folder is deleted afterwards.
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp) / f"upload{suffix}"
        tmp_path.write_bytes(data)
        return pipeline.analyze_file(tmp_path, source_name=name, refresh=refresh)
