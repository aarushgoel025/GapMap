import os
import sys
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import httpx

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

load_dotenv()

try:
    from mistralai.client import Mistral
except ImportError:
    try:
        from mistralai import Mistral
    except ImportError:
        Mistral = None

from db.store import write_audit

# Mistral Configuration
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
DEFAULT_MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "open-mistral-nemo")

# Gemini Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DEFAULT_GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")

mistral_client = Mistral(api_key=MISTRAL_API_KEY) if (Mistral and MISTRAL_API_KEY) else None


def get_mistral_completion(prompt: str, model: str = DEFAULT_MISTRAL_MODEL, system_prompt: Optional[str] = None) -> str:
    """
    Send a prompt to Mistral and return the response text.
    Section F Governance: writes an audit log entry (logging event metadata, never personal text).
    """
    if not mistral_client:
        raise RuntimeError("MISTRAL_API_KEY is not configured or Mistral client unavailable.")

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    response = mistral_client.chat.complete(
        model=model,
        messages=messages
    )
    result_text = response.choices[0].message.content

    # Section F Governance: Log event metadata, NEVER personal text
    write_audit(
        action="llm_call",
        details={
            "provider": "mistral",
            "model": model,
            "prompt_length_chars": len(prompt),
            "response_length_chars": len(result_text) if result_text else 0,
            "system_prompt_present": bool(system_prompt),
        },
        entity_type="llm"
    )

    return result_text


def get_gemini_completion(prompt: str, model: str = DEFAULT_GEMINI_MODEL, system_prompt: Optional[str] = None) -> str:
    """
    Send a prompt to Google Gemini via REST API and return the response text.
    Section F Governance: writes an audit log entry (logging event metadata, never personal text).
    """
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    clean_model = model.strip()
    if clean_model.startswith("models/"):
        clean_model = clean_model[7:]

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{clean_model}:generateContent?key={GEMINI_API_KEY}"

    contents = []
    if system_prompt:
        contents.append({"role": "user", "parts": [{"text": f"System context: {system_prompt}"}]})
    contents.append({"role": "user", "parts": [{"text": prompt}]})

    payload = {"contents": contents}

    with httpx.Client(timeout=30.0) as http_client:
        resp = http_client.post(url, json=payload)
        resp.raise_for_status()
        data = resp.json()

    candidates = data.get("candidates", [])
    if not candidates:
        raise RuntimeError(f"Gemini returned no candidates: {data}")

    result_text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")

    # Section F Governance: Log event metadata, NEVER personal text
    write_audit(
        action="llm_call",
        details={
            "provider": "gemini",
            "model": clean_model,
            "prompt_length_chars": len(prompt),
            "response_length_chars": len(result_text),
            "system_prompt_present": bool(system_prompt),
        },
        entity_type="llm"
    )

    return result_text


def get_completion(prompt: str, model: str = DEFAULT_MISTRAL_MODEL, system_prompt: Optional[str] = None) -> str:
    """
    Default LLM completion entrypoint (falls back to Gemini if Mistral key is absent, or vice versa).
    """
    if mistral_client:
        return get_mistral_completion(prompt, model=model, system_prompt=system_prompt)
    if GEMINI_API_KEY:
        return get_gemini_completion(prompt, system_prompt=system_prompt)
    raise RuntimeError("No LLM key configured. Please set MISTRAL_API_KEY or GEMINI_API_KEY in .env.")


def check_models_agreement(prompt: str) -> Dict[str, Any]:
    """
    Evaluate agreement between Gemini and Mistral for Section 7 schemas.py:
    'models_agree: Optional[bool] # Gemini and Mistral result'
    """
    results = {}
    if mistral_client:
        try:
            results["mistral"] = get_mistral_completion(prompt).strip().lower()
        except Exception as e:
            results["mistral_error"] = str(e)

    if GEMINI_API_KEY:
        try:
            results["gemini"] = get_gemini_completion(prompt).strip().lower()
        except Exception as e:
            results["gemini_error"] = str(e)

    if "mistral" in results and "gemini" in results:
        agree = results["mistral"] == results["gemini"] or (
            results["mistral"] in results["gemini"] or results["gemini"] in results["mistral"]
        )
        return {"models_agree": agree, "mistral": results["mistral"], "gemini": results["gemini"]}

    return {"models_agree": None, "details": results}


if __name__ == "__main__":
    test_prompt = "Is Python a programming language? Answer YES or NO."
    print("Testing Dual LLM Setup (Section 10 & Governance)...")
    if mistral_client:
        print("[Mistral] Testing completion...")
        try:
            print("[Mistral Response]:", get_mistral_completion(test_prompt))
        except Exception as err:
            print("[Mistral Error]:", err)

    if GEMINI_API_KEY:
        print("[Gemini] Testing completion...")
        try:
            print("[Gemini Response]:", get_gemini_completion(test_prompt))
        except Exception as err:
            print("[Gemini Error]:", err)
