
from unittest.mock import patch

from shared.schemas import ExtractionResult, Skill
from resume_parsing.ai_extractor import extract_resume_with_ai


def test_gemini_path_uses_structured_output_without_live_api():
    fake_result = ExtractionResult(
        source_type="resume",
        source_file="sample_resume.docx",
        skills=[
            Skill(
                skill_name="Python",
                category_code="COD",
                evidence="Built a Python application",
                confidence="high",
                level_estimate=7,
                source_section="Projects",
                stuffing_flag=False,
            )
        ],
        extras={
            "education": "B.Tech Computer Science",
            "projects": [],
            "experience": [],
            "certifications": [],
        },
    )

    with (
        patch("resume_parsing.ai_extractor.get_gemini") as mock_gemini,
        patch("resume_parsing.ai_extractor.call_structured", return_value=fake_result)
        as mock_call,
    ):
        mock_gemini.return_value = object()

        result = extract_resume_with_ai(
            resume_text="Built a Python application",
            source_file="sample_resume.docx",
            provider="gemini",
        )

    assert result.source_type == "resume"
    assert result.source_file == "sample_resume.docx"
    assert result.skills[0].skill_name == "Python"
    mock_gemini.assert_called_once()
    mock_call.assert_called_once()
    assert mock_call.call_args.kwargs["schema"] is ExtractionResult



def test_mistral_path_uses_structured_output_without_live_api():
    fake_result = ExtractionResult(
        source_type="resume",
        source_file="sample_resume.docx",
        skills=[],
        extras={},
    )

    with (
        patch("resume_parsing.ai_extractor.get_mistral") as mock_mistral,
        patch(
            "resume_parsing.ai_extractor.call_structured",
            return_value=fake_result,
        ) as mock_call,
    ):
        mock_mistral.return_value = object()

        result = extract_resume_with_ai(
            resume_text="Python developer",
            source_file="sample_resume.docx",
            provider="mistral",
        )

    assert result.source_type == "resume"
    mock_mistral.assert_called_once()
    mock_call.assert_called_once()

if __name__ == "__main__":
    test_gemini_path_uses_structured_output_without_live_api()
    test_mistral_path_uses_structured_output_without_live_api()
    print("Offline AI extractor tests: PASS")

