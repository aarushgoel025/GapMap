import os
import sys

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
from dotenv import load_dotenv
try:
    from mistralai.client import Mistral
except ImportError:
    from mistralai import Mistral

load_dotenv()

MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
DEFAULT_MODEL = os.getenv("MISTRAL_MODEL", "open-mistral-nemo")

client = Mistral(api_key=MISTRAL_API_KEY)


def get_completion(prompt: str, model: str = DEFAULT_MODEL, system_prompt: str = None) -> str:
    """Send a prompt to Mistral and return the response text."""
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.complete(
        model=model,
        messages=messages
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    test_prompt = "Explain AI agents in simple terms."
    print(f"Testing with model: {DEFAULT_MODEL}...\n")
    result = get_completion(test_prompt)
    print("Response:\n" + result)
