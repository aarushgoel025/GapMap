from pathlib import Path
import tempfile

from fastapi import APIRouter, File, HTTPException, UploadFile
from resume_parsing.parser import parse_resume

router = APIRouter(prefix="/api/resume", tags=["resume_parsing"])


@router.get("/status")
def status():
    return {"module": "resume_parsing", "status": "initialized"}


@router.post("/parse")
async def parse_uploaded_resume(file: UploadFile = File(...)):
    filename = file.filename or "resume"
    suffix = Path(filename).suffix.lower()

    if suffix not in {".pdf", ".docx"}:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported.",
        )

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir) / f"resume{suffix}"
            temp_path.write_bytes(content)
            result = parse_resume(temp_path)

        response = result.model_dump()
        response["source_file"] = filename
        return response

    except (ValueError, FileNotFoundError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))
