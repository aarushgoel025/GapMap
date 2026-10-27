import os
import sys
from typing import Optional
from dotenv import load_dotenv

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

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
DEFAULT_MODEL = os.getenv("MISTRAL_MODEL", "open-mistral-nemo")

client = Mistral(api_key=MISTRAL_API_KEY) if (Mistral and MISTRAL_API_KEY) else None


def get_completion(prompt: str, model: str = DEFAULT_MODEL, system_prompt: Optional[str] = None) -> str:
    """
    Send a prompt to Mistral and return the response text.
    Section F Governance: writes an audit log entry (logging event metadata, never personal text).
    """
    if not client:
        raise RuntimeError("MISTRAL_API_KEY is not configured or Mistral client unavailable.")

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.complete(
        model=model,
        messages=messages
    )
    result_text = response.choices[0].message.content

    # Section F Governance: Log the event metadata, NEVER the personal text
    write_audit(
        action="llm_call",
        details={
            "model": model,
            "prompt_length_chars": len(prompt),
            "response_length_chars": len(result_text) if result_text else 0,
            "system_prompt_present": bool(system_prompt),
        },
        entity_type="llm"
    )

    return result_text


if __name__ == "__main__":
    test_prompt = "Explain AI agents in simple terms."
    print(f"Testing with model: {DEFAULT_MODEL}...\n")
    if client:
        result = get_completion(test_prompt)
        print("Response:\n" + result)
    else:
        print("Mistral client not configured. Add MISTRAL_API_KEY to .env to test.")
