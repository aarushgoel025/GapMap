import pytest

from app.shared.docreader import DocumentReadError, read_document
from jd_test_utils import JD_LINES, make_docx, make_pdf


def test_reads_pdf_text(tmp_path):
    path = make_pdf(tmp_path / "jd.pdf", JD_LINES)
    text = read_document(path)
    assert "Minimum qualifications" in text
    assert "Kubernetes" in text


def test_reads_docx_paragraphs_and_tables_in_order(tmp_path):
    path = make_docx(tmp_path / "jd.docx", ["Intro paragraph", "Requirements"],
                     table_rows=[["Skill", "Level"], ["Python", "Required"]])
    lines = read_document(path).splitlines()
    assert lines[:2] == ["Intro paragraph", "Requirements"]
    assert "Skill | Level" in lines
    assert "Python | Required" in lines


def test_accepts_str_path_and_uppercase_extension(tmp_path):
    path = make_pdf(tmp_path / "JD.PDF", ["Hello world"])
    assert "Hello world" in read_document(str(path))


def test_unsupported_extension(tmp_path):
    path = tmp_path / "jd.txt"
    path.write_text("hello")
    with pytest.raises(DocumentReadError, match="Unsupported file type"):
        read_document(path)


def test_missing_file(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_document(tmp_path / "nope.pdf")


def test_document_without_text(tmp_path):
    path = make_docx(tmp_path / "empty.docx", [])
    with pytest.raises(DocumentReadError, match="No text found"):
        read_document(path)


@pytest.mark.parametrize("name", ["broken.pdf", "broken.docx"])
def test_corrupt_files_give_clear_error(tmp_path, name):
    path = tmp_path / name
    path.write_bytes(b"this is not a real document")
    with pytest.raises(DocumentReadError, match="Could not read"):
        read_document(path)
