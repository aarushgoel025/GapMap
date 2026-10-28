import threading
 
import pytest
from pydantic import ValidationError
 
from app.jd_analytics import pipeline
from app.jd_analytics.pipeline import ExtractionError, LLMExtraction, lower_confidence, merge
from app.shared.schemas import ExtractionResult
from jd_test_utils import extraction, llm_skill
 
 
# ---------------------------------------------------------------- model answer validation
def test_llm_skill_tidies_casing_and_labels():
    s = llm_skill(" Python ", category="sql", importance="Must-Have", confidence="HIGH")
    assert (s.skill_name, s.category_code, s.importance, s.confidence) == ("Python", "SQL", "must_have", "high")
 
 
def test_llm_skill_rejects_unknown_category():
    with pytest.raises(ValidationError):
        llm_skill("Python", category="FOO")
 
 
def test_llm_extraction_rejects_empty_skill_list():
    with pytest.raises(ValidationError):
        LLMExtraction(company="x", role="y", skills=[])
 
 
def test_llm_extraction_accepts_null_company():
    assert LLMExtraction(company=None, role=None, skills=[llm_skill("Go")]).company == ""
 
 
@pytest.mark.parametrize("before,after", [("high", "medium"), ("medium", "low"), ("low", "low")])
def test_lower_confidence(before, after):
    assert lower_confidence(before) == after
 
 
# ---------------------------------------------------------------- merge
def test_skill_found_by_both_is_matched_case_insensitively():
    a = extraction([llm_skill("Python", confidence="high")])
    b = extraction([llm_skill("python", confidence="medium")])
    result = merge(a, b, "jd.pdf")
    assert len(result.skills) == 1
    skill = result.skills[0]
    assert skill.skill_name == "Python"  # Gemini's spelling
    assert skill.models_agree is True
    assert skill.confidence == "high"  # Gemini's confidence is kept
    assert result.extras["disagreements"] == []
 
 
def test_skill_found_by_one_model_is_flagged_and_lowered():
    a = extraction([llm_skill("Python"), llm_skill("Go", confidence="high")])
    b = extraction([llm_skill("Python"), llm_skill("Rust", confidence="low")])
    by_name = {s.skill_name: s for s in merge(a, b, "jd.pdf").skills}
    assert set(by_name) == {"Python", "Go", "Rust"}
    assert by_name["Python"].models_agree is True
    assert (by_name["Go"].models_agree, by_name["Go"].confidence) == (False, "medium")  # Gemini only
    assert (by_name["Rust"].models_agree, by_name["Rust"].confidence) == (False, "low")  # Mistral only
 
 
def test_category_conflict_keeps_gemini_and_records_it():
    a = extraction([llm_skill("Docker", category="CLOUD", confidence="high")])
    b = extraction([llm_skill("Docker", category="OS", confidence="high")])
    result = merge(a, b, "jd.pdf")
    skill = result.skills[0]
    assert skill.category_code == "CLOUD"
    assert skill.confidence == "medium"
    assert skill.models_agree is True  # both models found the skill
    assert result.extras["disagreements"] == [
        {"skill": "Docker", "gemini_category": "CLOUD", "mistral_category": "OS"}
    ]
 
 
def test_single_model_result_has_models_agree_none_and_unchanged_confidence():
    only = extraction([llm_skill("Python", confidence="high"), llm_skill("SQL", "SQL", confidence="low")])
    for gemini, mistral in ((only, None), (None, only)):
        result = merge(gemini, mistral, "jd.pdf")
        assert [s.models_agree for s in result.skills] == [None, None]
        assert [s.confidence for s in result.skills] == ["high", "low"]
        assert result.extras["disagreements"] == []
 
 
def test_importance_comes_from_gemini_and_evidence_falls_back_to_mistral():
    a = extraction([llm_skill("Python", importance="must_have", evidence="")])
    b = extraction([llm_skill("Python", importance="nice_to_have", evidence="Python is a plus")])
    skill = merge(a, b, "jd.pdf").skills[0]
    assert skill.importance == "must_have"
    assert skill.evidence == "Python is a plus"
 
 
def test_repeated_skill_inside_one_model_is_deduplicated():
    a = extraction([llm_skill("Python"), llm_skill("python")])
    assert len(merge(a, None, "jd.pdf").skills) == 1
 
 
def test_company_and_role_fall_back_to_the_other_model():
    a = extraction([llm_skill("Go")], company="", role="")
    b = extraction([llm_skill("Go")], company="Google", role="SWE")
    result = merge(a, b, "jd.pdf")
    assert (result.company, result.role) == ("Google", "SWE")
 
 
def test_merge_with_no_results_fails():
    with pytest.raises(ExtractionError):
        merge(None, None, "jd.pdf")
 
 
def test_merged_result_is_a_valid_jd_extraction_result():
    result = merge(extraction([llm_skill("Python")]), extraction([llm_skill("Python")]), "jd.pdf")
    assert isinstance(result, ExtractionResult)
    assert result.source_type == "jd" and result.source_file == "jd.pdf"
    assert ExtractionResult.model_validate_json(result.model_dump_json()) == result
 
 
# ---------------------------------------------------------------- analyze_text (parallel run and failures)
def test_both_models_run_at_the_same_time(monkeypatch):
    barrier = threading.Barrier(2, timeout=5)  # only passes if both extractors are running together
 
    def fake(text):
        barrier.wait()
        return extraction([llm_skill("Python")])
 
    monkeypatch.setattr(pipeline, "extract_a", fake)
    monkeypatch.setattr(pipeline, "extract_b", fake)
    result = pipeline.analyze_text("jd text", "jd.pdf")
    assert result.skills[0].models_agree is True
    assert result.extras["models_used"] == ["gemini", "mistral"]
    assert result.extras["models_failed"] == {}
 
 
@pytest.mark.parametrize("failing,survivor", [("a", "mistral"), ("b", "gemini")])
def test_one_model_failing_uses_the_other_alone(monkeypatch, failing, survivor):
    def boom(text):
        raise RuntimeError("provider is down")
 
    ok = lambda text: extraction([llm_skill("Python", confidence="high")])  # noqa: E731
    monkeypatch.setattr(pipeline, "extract_a", boom if failing == "a" else ok)
    monkeypatch.setattr(pipeline, "extract_b", boom if failing == "b" else ok)
    result = pipeline.analyze_text("jd text", "jd.pdf")
    assert result.skills[0].models_agree is None
    assert result.skills[0].confidence == "high"
    assert result.extras["models_used"] == [survivor]
    assert "provider is down" in next(iter(result.extras["models_failed"].values()))
 
 
def test_both_models_failing_raises_a_clear_error(monkeypatch):
    def no_key(text):
        raise KeyError("GEMINI_API_KEY")
 
    def down(text):
        raise RuntimeError("503 unavailable")
 
    monkeypatch.setattr(pipeline, "extract_a", no_key)
    monkeypatch.setattr(pipeline, "extract_b", down)
    with pytest.raises(ExtractionError) as err:
        pipeline.analyze_text("jd text", "jd.pdf")
    message = str(err.value)
    assert "missing environment variable GEMINI_API_KEY" in message
    assert "503 unavailable" in message
 
 
def test_prompt_contains_the_rules_the_models_need():
    prompt = pipeline.build_prompt("We need Python.")
    for code in ["COD", "DSA", "OOD", "APTI", "COMM", "AI", "CLOUD", "SQL", "SWE", "SYSD", "NETW", "OS", "OTHER"]:
        assert code in prompt
    for word in ["must_have", "nice_to_have", "required", "preferred", "evidence", "confidence", "We need Python."]:
        assert word in prompt
 
 
# ---------------------------------------------------------------- matching key
@pytest.mark.parametrize("a,b", [
    ("Data Visualization Tools", "data-visualization tool"),
    ("BI / Visualization", "BI Visualization"),
    ("Research and Development", "Research & Development"),
    ("SQL Databases", "sql database"),
])
def test_key_ignores_case_punctuation_and_plurals(a, b):
    assert pipeline._key(a) == pipeline._key(b)
 
 
@pytest.mark.parametrize("a,b", [("C++", "C"), ("C#", "C"), (".NET", "NET"), ("Java", "JavaScript"), ("AWS", "AW")])
def test_key_keeps_distinct_names_apart(a, b):
    assert pipeline._key(a) != pipeline._key(b)
 
 
def test_merge_matches_names_that_differ_only_in_punctuation():
    a = extraction([llm_skill("Data visualization tools", "OTHER")])
    b = extraction([llm_skill("data-visualization tool", "OTHER")])
    result = merge(a, b, "jd.pdf")
    assert len(result.skills) == 1 and result.skills[0].models_agree is True
