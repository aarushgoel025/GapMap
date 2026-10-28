import json
from types import SimpleNamespace

import pytest
from pydantic import BaseModel

from app.shared import llm


class Pet(BaseModel):
    name: str
    age: int


class FakeModel:
    """Stands in for a LangChain chat model: returns the queued answers in order."""

    def __init__(self, answers):
        self.answers = list(answers)
        self.prompts: list[str] = []

    def invoke(self, prompt):
        self.prompts.append(prompt)
        answer = self.answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return SimpleNamespace(content=answer)


GOOD = json.dumps({"name": "Rex", "age": 3})


def test_valid_answer_first_try():
    model = FakeModel([GOOD])
    pet = llm.call_structured(model, "Describe a pet", Pet)
    assert pet == Pet(name="Rex", age=3)
    assert len(model.prompts) == 1
    assert "Describe a pet" in model.prompts[0]
    assert '"age"' in model.prompts[0]  # the JSON schema is part of the prompt


def test_handles_code_fences_and_extra_text():
    model = FakeModel([f"Sure! Here you go:\n```json\n{GOOD}\n```\nHope that helps."])
    assert llm.call_structured(model, "p", Pet).name == "Rex"


def test_handles_list_of_content_parts():
    model = FakeModel([[{"type": "text", "text": GOOD}]])
    assert llm.call_structured(model, "p", Pet).age == 3


def test_validation_error_is_fed_back_and_retried():
    bad = json.dumps({"name": "Rex", "age": "many"})
    model = FakeModel([bad, GOOD])
    pet = llm.call_structured(model, "p", Pet)
    assert pet.age == 3
    assert len(model.prompts) == 2
    assert "rejected" in model.prompts[1]
    assert "age" in model.prompts[1]  # the validation error names the bad field
    assert bad in model.prompts[1]  # and the previous answer is included


def test_text_that_is_not_json_is_retried():
    model = FakeModel(["I cannot do that", GOOD])
    assert llm.call_structured(model, "p", Pet).name == "Rex"
    assert len(model.prompts) == 2


def test_gives_up_after_three_retries():
    model = FakeModel(["nope"] * 10)
    with pytest.raises(llm.StructuredOutputError, match="4 attempts"):
        llm.call_structured(model, "p", Pet)
    assert len(model.prompts) == 4  # first try + 3 retries


def test_429_is_retried_with_backoff(monkeypatch):
    sleeps: list[float] = []
    monkeypatch.setattr(llm.time, "sleep", lambda s: sleeps.append(s))
    model = FakeModel([Exception("Error 429: too many requests"), GOOD])
    assert llm.call_structured(model, "p", Pet).name == "Rex"
    assert sleeps == [2]


def test_other_api_errors_are_not_swallowed():
    model = FakeModel([Exception("401 unauthorized")])
    with pytest.raises(Exception, match="401"):
        llm.call_structured(model, "p", Pet)


def test_mistral_is_throttled_before_every_call(monkeypatch):
    class FakeChatOpenAI(FakeModel):  # plays the role of get_mistral()'s ChatOpenAI
        pass

    monkeypatch.setattr(llm, "ChatOpenAI", FakeChatOpenAI)
    throttled: list[int] = []
    monkeypatch.setattr(llm, "mistral_throttle", lambda *a, **k: throttled.append(1))

    mistral = FakeChatOpenAI(["bad", GOOD])
    llm.call_structured(mistral, "p", Pet)
    assert len(throttled) == 2  # one per call, including the retry

    throttled.clear()
    llm.call_structured(FakeModel([GOOD]), "p", Pet)  # a Gemini-style model is not throttled
    assert throttled == []
