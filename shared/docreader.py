"""Read plain text from PDF and DOCX files (shared by JD Analytics and Resume Parsing)."""
from pathlib import Path

import docx  # python-docx
import pdfplumber
from docx.text.paragraph import Paragraph


class DocumentReadError(ValueError):
    """The file is missing a readable text layer, is corrupt, or has an unsupported type."""


def read_document(path: str | Path) -> str:
    """Return the text of a .pdf or .docx file. Raises DocumentReadError with a clear message."""
    p = Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"File not found: {p}")

    ext = p.suffix.lower()
    if ext == ".pdf":
        text = _read_pdf(p)
    elif ext == ".docx":
        text = _read_docx(p)
    else:
        raise DocumentReadError(f"Unsupported file type '{ext}'. Please use a .pdf or .docx file.")

    text = text.strip()
    if not text:
        # a scanned PDF (images only) has no text layer for pdfplumber to read
        raise DocumentReadError(f"No text found in '{p.name}'. If it is a scanned PDF, use a text-based copy.")
    return text


def _read_pdf(p: Path) -> str:
    try:
        with pdfplumber.open(p) as pdf:
            return "\n".join((page.extract_text() or "") for page in pdf.pages)
    except Exception as e:  # pdfminer raises many different error types for bad files
        raise DocumentReadError(f"Could not read PDF '{p.name}': {e}") from e


def _read_docx(p: Path) -> str:
    try:
        document = docx.Document(str(p))
        lines: list[str] = []
        # iter_inner_content keeps paragraphs and tables in their original order
        for block in document.iter_inner_content():
            if isinstance(block, Paragraph):
                lines.append(block.text)
            else:  # a table: one line per row, cells joined with " | "
                for row in block.rows:
                    cells: list[str] = []
                    for cell in row.cells:
                        t = cell.text.strip()
                        # merged cells repeat the same text, so skip consecutive duplicates
                        if t and (not cells or cells[-1] != t):
                            cells.append(t)
                    if cells:
                        lines.append(" | ".join(cells))
        return "\n".join(lines)
    except Exception as e:  # corrupt zip, wrong format, and so on
        raise DocumentReadError(f"Could not read DOCX '{p.name}': {e}") from e
