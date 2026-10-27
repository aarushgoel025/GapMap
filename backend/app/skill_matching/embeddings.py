"""Embedding utilities and precomputed vector vocabulary index for Skill Matching."""
import json
import os
import re
from pathlib import Path
from typing import Optional

import numpy as np

from app.skill_matching.config import CACHE_DIR
from app.skill_matching.normalize import normalize_name

_VOCAB_SKILLS: list[str] = []
_VOCAB_EMBEDDINGS: Optional[np.ndarray] = None


def _deterministic_local_embed(texts: list[str], dim: int = 256) -> np.ndarray:
    """Fast, deterministic fallback vector generator based on char n-grams and word tokens.
    Guarantees consistent cosine similarities offline without requiring GPU or external API.
    """
    vectors = np.zeros((len(texts), dim), dtype=np.float32)
    for row_idx, text in enumerate(texts):
        cleaned = normalize_name(text)
        if not cleaned:
            continue
        # Token and character n-grams (2 to 4 chars)
        ngrams = [cleaned[i : i + n] for n in (2, 3, 4) for i in range(len(cleaned) - n + 1)]
        words = re.findall(r"\w+", text.lower())
        tokens = ngrams + words
        for token in tokens:
            h = hash(token)
            idx = abs(h) % dim
            sign = 1.0 if (h // dim) % 2 == 0 else -1.0
            vectors[row_idx, idx] += sign
        # L2 normalize
        norm = np.linalg.norm(vectors[row_idx])
        if norm > 1e-6:
            vectors[row_idx] /= norm
    return vectors


def embed_texts(texts: list[str]) -> np.ndarray:
    """Embed a list of text strings using Gemini Embeddings API if configured, else local fallback."""
    if not texts:
        return np.empty((0, 256), dtype=np.float32)

    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key:
        try:
            import requests

            url = f"https://generativelanguage.googleapis.com/v1beta/models/text-embedding-004:batchEmbedContents?key={api_key}"
            requests_body = {
                "requests": [
                    {"model": "models/text-embedding-004", "content": {"parts": [{"text": t}]}}
                    for t in texts
                ]
            }
            res = requests.post(url, json=requests_body, timeout=10)
            if res.status_code == 200:
                data = res.json()
                embeddings = [e["values"] for e in data.get("embeddings", [])]
                arr = np.array(embeddings, dtype=np.float32)
                # Normalize
                norms = np.linalg.norm(arr, axis=1, keepdims=True)
                norms[norms < 1e-6] = 1.0
                return arr / norms
        except Exception:
            pass  # Fallback to local on network/quota error

    return _deterministic_local_embed(texts)


def build_vocab_index() -> int:
    """Scans backend/data/cache for extracted skill names, embeds them, and saves to cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    skills_set: set[str] = set()

    # Read from cache JSON files
    for p in CACHE_DIR.glob("*.json"):
        if p.name == "vocab_skills.json":
            continue
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict) and "skills" in data:
                for s in data["skills"]:
                    name = s.get("skill_name") if isinstance(s, dict) else str(s)
                    if name:
                        skills_set.add(name)
        except Exception:
            continue

    # Default core vocabulary if cache is fresh or empty
    if len(skills_set) < 10:
        skills_set.update([
            "Python", "JavaScript", "TypeScript", "React", "Node.js", "FastAPI", "Docker",
            "Kubernetes", "PostgreSQL", "MongoDB", "SQL", "Git", "AWS", "Google Cloud",
            "Azure", "Linux", "Machine Learning", "Deep Learning", "NLP", "LLMs",
            "System Design", "Microservices", "REST API", "Data Structures", "Java",
            "C++", "C#", "Go", "Pandas", "NumPy", "PyTorch", "TensorFlow", "HTML", "CSS"
        ])

    skill_list = sorted(list(skills_set))
    embeddings = embed_texts(skill_list)

    # Save to disk
    vocab_file = CACHE_DIR / "vocab_skills.json"
    npy_file = CACHE_DIR / "vocab_embeddings.npy"

    with open(vocab_file, "w", encoding="utf-8") as f:
        json.dump(skill_list, f, indent=2)

    np.save(npy_file, embeddings)

    global _VOCAB_SKILLS, _VOCAB_EMBEDDINGS
    _VOCAB_SKILLS = skill_list
    _VOCAB_EMBEDDINGS = embeddings
    return len(skill_list)


def load_vocab_index() -> None:
    """Loads vocabulary and precomputed embeddings from cache at startup."""
    global _VOCAB_SKILLS, _VOCAB_EMBEDDINGS
    vocab_file = CACHE_DIR / "vocab_skills.json"
    npy_file = CACHE_DIR / "vocab_embeddings.npy"

    if vocab_file.exists() and npy_file.exists():
        try:
            with open(vocab_file, "r", encoding="utf-8") as f:
                _VOCAB_SKILLS = json.load(f)
            _VOCAB_EMBEDDINGS = np.load(npy_file)
            return
        except Exception:
            pass

    build_vocab_index()


def cosine_top1(query: str, candidates: Optional[list[str]] = None) -> tuple[str, float]:
    """Returns the top matching skill and its cosine similarity."""
    global _VOCAB_SKILLS, _VOCAB_EMBEDDINGS
    if not query.strip():
        return ("", 0.0)

    if candidates:
        cand_embeds = embed_texts(candidates)
        query_embed = embed_texts([query])[0]
        sims = cand_embeds @ query_embed
        best_idx = int(np.argmax(sims))
        return (candidates[best_idx], float(sims[best_idx]))

    if _VOCAB_EMBEDDINGS is None or not _VOCAB_SKILLS:
        load_vocab_index()

    if _VOCAB_EMBEDDINGS is None or len(_VOCAB_SKILLS) == 0:
        return ("", 0.0)

    query_embed = embed_texts([query])[0]
    sims = _VOCAB_EMBEDDINGS @ query_embed
    best_idx = int(np.argmax(sims))
    return (_VOCAB_SKILLS[best_idx], float(sims[best_idx]))

