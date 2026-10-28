# backend/app/shared/llm.py (owner: Samiksha)
import os, time, threading
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
import json, re
from typing import TypeVar
from pydantic import BaseModel, ValidationError

load_dotenv()

def get_gemini():
    return ChatGoogleGenerativeAI(
        model=os.environ['GEMINI_MODEL'],
        google_api_key=os.environ['GEMINI_API_KEY'],
        temperature=0)

def get_mistral():
    # Mistral is OpenAI-compatible, so ChatOpenAI works with a different base_url
    return ChatOpenAI(
        base_url='https://api.mistral.ai/v1',
        api_key=os.environ['MISTRAL_API_KEY'],
        model=os.environ['MISTRAL_MODEL'],
        temperature=0)

_lock = threading.Lock()
_last_call = {'t': 0.0}

def mistral_throttle(min_gap=1.1):
    # keeps us under 1 request per second
    with _lock:
        wait = _last_call['t'] + min_gap - time.time()
        if wait > 0:
            time.sleep(wait)
        _last_call['t'] = time.time()

def call_with_backoff(fn, tries=4):
    # retry on 429 with waits of 2, 4, 8 seconds (max 30)
    for attempt in range(tries):
        try:
            return fn()
        except Exception as e:
            if '429' in str(e) and attempt < tries - 1:
                time.sleep(min(2 ** (attempt + 1), 30))
                continue
            raise

# quick test:
# print(get_mistral().invoke('Reply with only: ok').content)


# ---------------------------------------------------------------------------
# Added below the section 10 code: structured (validated) output helper
# ---------------------------------------------------------------------------
T = TypeVar("T", bound=BaseModel)


class StructuredOutputError(RuntimeError):
    """The model never returned JSON that passes the Pydantic schema."""


def _to_text(content) -> str:
    # Gemini can return a list of content parts instead of a plain string
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(p if isinstance(p, str) else str(p.get("text", "")) for p in content
                       if isinstance(p, (str, dict)))
    return str(content)


def _extract_json(raw: str) -> str:
    # models sometimes wrap the JSON in ```json fences or add a sentence around it
    text = raw.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        text = text[start:end + 1]
    return text


def _invoke(model, prompt: str) -> str:
    def call():
        # get_mistral() is the only ChatOpenAI we use, and Mistral allows ~1 request/second.
        # Throttling inside call() means every backoff retry is throttled too.
        if isinstance(model, ChatOpenAI):
            mistral_throttle()
        return model.invoke(prompt)

    return _to_text(call_with_backoff(call).content)


def call_structured(model, prompt: str, schema: type[T], retries: int = 3) -> T:
    """Ask `model` (from get_gemini()/get_mistral()) for JSON and return a validated `schema` object.

    If the answer is not valid JSON or fails validation, retry up to `retries` more times,
    sending the validation error and the bad answer back so the model can fix it.
    """
    base_prompt = (
        f"{prompt}\n\n"
        "Return ONLY one JSON object (no markdown, no commentary) that matches this JSON schema:\n"
        f"{json.dumps(schema.model_json_schema())}"
    )
    current = base_prompt
    last_error = ""
    for _ in range(retries + 1):
        raw = _invoke(model, current)
        try:
            return schema.model_validate_json(_extract_json(raw))
        except ValidationError as e:  # also covers text that is not valid JSON at all
            last_error = str(e)[:1500]
            current = (
                f"{base_prompt}\n\n"
                f"Your previous answer was rejected with this error:\n{last_error}\n\n"
                f"Your previous answer was:\n{raw[:3000]}\n\n"
                "Fix every problem and return ONLY the corrected JSON object."
            )
    raise StructuredOutputError(
        f"No valid {schema.__name__} after {retries + 1} attempts. Last error: {last_error}"
    )
