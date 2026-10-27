import json
import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Base directory setup for JSON storage fallback
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "backend" / "data"
PROFILES_DIR = DATA_DIR / "profiles"
RUNS_DIR = DATA_DIR / "runs"
JDS_DIR = DATA_DIR / "jds"

for directory in (PROFILES_DIR, RUNS_DIR, JDS_DIR):
    directory.mkdir(parents=True, exist_ok=True)

# Supabase Client Initialization
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

_supabase_client = None
if SUPABASE_URL and SUPABASE_SERVICE_KEY:
    try:
        from supabase import create_client
        clean_url = SUPABASE_URL.strip().rstrip("/")
        if clean_url.endswith("/rest/v1"):
            clean_url = clean_url[:-8].rstrip("/")
        _supabase_client = create_client(clean_url, SUPABASE_SERVICE_KEY.strip())
        logger.info("Supabase client initialized successfully.")
    except Exception as exc:
        logger.warning("Failed to initialize Supabase client: %s. Using JSON fallback.", exc)
        _supabase_client = None


def _to_dict(obj: Any) -> Dict[str, Any]:
    """Convert a Pydantic model or dict-like object to a plain Python dict."""
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "dict"):
        return obj.dict()
    if isinstance(obj, dict):
        return dict(obj)
    raise TypeError(f"Cannot serialize object of type {type(obj)}")


# ---------------------------------------------------------------------------
# Profile Store Functions
# ---------------------------------------------------------------------------

def save_profile(profile_data: Union[Dict[str, Any], Any]) -> Dict[str, Any]:
    """
    Save a profile to Supabase or JSON fallback.
    Assigns a profile_id if not present.
    """
    data = _to_dict(profile_data)
    if not data.get("profile_id"):
        data["profile_id"] = str(uuid.uuid4())

    profile_id = data["profile_id"]

    # Try Supabase if configured
    if _supabase_client:
        try:
            resp = _supabase_client.table("profiles").upsert(data).execute()
            if resp.data:
                return resp.data[0]
        except Exception as exc:
            logger.warning("Supabase save_profile error: %s. Falling back to JSON.", exc)

    # JSON fallback
    file_path = PROFILES_DIR / f"{profile_id}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)

    return data


def load_profile(profile_id: str) -> Optional[Dict[str, Any]]:
    """Load a profile by profile_id from Supabase or JSON fallback."""
    if _supabase_client:
        try:
            resp = _supabase_client.table("profiles").select("*").eq("profile_id", profile_id).execute()
            if resp.data and len(resp.data) > 0:
                return resp.data[0]
        except Exception as exc:
            logger.warning("Supabase load_profile error: %s. Falling back to JSON.", exc)

    # JSON fallback
    file_path = PROFILES_DIR / f"{profile_id}.json"
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    # Check if matching by partial filename or ID in stem
    for p in sorted(PROFILES_DIR.glob("*.json")):
        if profile_id.lower() in p.stem.lower():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                continue
    return None


def list_profiles() -> List[Dict[str, Any]]:
    """List all profiles from Supabase or JSON fallback."""
    if _supabase_client:
        try:
            resp = _supabase_client.table("profiles").select("*").execute()
            if resp.data is not None:
                return resp.data
        except Exception as exc:
            logger.warning("Supabase list_profiles error: %s. Falling back to JSON.", exc)

    # JSON fallback
    profiles = []
    for file_path in sorted(PROFILES_DIR.glob("*.json")):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                profiles.append(json.load(f))
        except Exception as exc:
            logger.warning("Failed reading profile file %s: %s", file_path, exc)
    return profiles


# ---------------------------------------------------------------------------
# Job Description (JD) Store Functions
# ---------------------------------------------------------------------------

def save_jd(
    jd_data: Any = None,
    jd_id: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Save JD data to Supabase or JSON fallback.
    Supports:
      - save_jd(jd_data, jd_id="...")
      - save_jd("jd_id", jd_data)
      - save_jd(jd_data)
    """
    if isinstance(jd_data, str) and (jd_id is not None or kwargs):
        # Called as save_jd("id", data)
        actual_id = jd_data
        actual_data = _to_dict(jd_id if jd_id is not None else kwargs.get("data", {}))
    elif isinstance(jd_data, (dict, object)):
        actual_data = _to_dict(jd_data)
        actual_id = jd_id or actual_data.get("jd_id") or actual_data.get("id") or str(uuid.uuid4())
    else:
        raise ValueError("Invalid arguments to save_jd")

    actual_data["jd_id"] = str(actual_id)

    if _supabase_client:
        try:
            resp = _supabase_client.table("jds").upsert(actual_data).execute()
            if resp.data:
                return resp.data[0]
        except Exception as exc:
            logger.warning("Supabase save_jd error: %s. Falling back to JSON.", exc)

    file_path = JDS_DIR / f"{actual_data['jd_id']}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(actual_data, f, indent=2, default=str)

    return actual_data


def load_jd(jd_id: str) -> Optional[Dict[str, Any]]:
    """Load JD data by jd_id from Supabase or JSON fallback."""
    if _supabase_client:
        try:
            resp = _supabase_client.table("jds").select("*").eq("jd_id", jd_id).execute()
            if resp.data and len(resp.data) > 0:
                return resp.data[0]
        except Exception as exc:
            logger.warning("Supabase load_jd error: %s. Falling back to JSON.", exc)

    file_path = JDS_DIR / f"{jd_id}.json"
    if file_path.exists():
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # Search by partial / stem match
    clean_id = jd_id.lower().replace(".pdf", "").replace(".docx", "").replace(".json", "")
    for p in sorted(JDS_DIR.glob("*.json")):
        if clean_id in p.stem.lower() or clean_id in p.name.lower() or jd_id.lower() in p.name.lower():
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                continue

    return None


def list_jds() -> List[Dict[str, Any]]:
    """List all JD extraction documents from Supabase or JSON fallback."""
    if _supabase_client:
        try:
            resp = _supabase_client.table("jds").select("*").execute()
            if resp.data is not None:
                return resp.data
        except Exception as exc:
            logger.warning("Supabase list_jds error: %s. Falling back to JSON.", exc)

    jds = []
    for file_path in sorted(JDS_DIR.glob("*.json")):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                jds.append(json.load(f))
        except Exception as exc:
            logger.warning("Failed reading JD file %s: %s", file_path, exc)
    return jds


# ---------------------------------------------------------------------------
# Run Store Functions
# ---------------------------------------------------------------------------

def save_run(
    run_data: Any = None,
    run_id: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Save pipeline run results to Supabase or JSON fallback under backend/data/runs.
    Supports:
      - save_run(run_data, run_id="...")
      - save_run("run_id", run_data)
      - save_run(run_data)
    """
    if isinstance(run_data, str) and (run_id is not None or kwargs):
        actual_id = run_data
        actual_data = _to_dict(run_id if run_id is not None else kwargs.get("data", {}))
    elif isinstance(run_data, (dict, object)):
        actual_data = _to_dict(run_data)
        actual_id = run_id or actual_data.get("run_id") or actual_data.get("id") or str(uuid.uuid4())
    else:
        raise ValueError("Invalid arguments to save_run")

    actual_data["run_id"] = str(actual_id)

    if _supabase_client:
        try:
            resp = _supabase_client.table("runs").upsert(actual_data).execute()
            if resp.data:
                return resp.data[0]
        except Exception as exc:
            logger.warning("Supabase save_run error: %s. Falling back to JSON.", exc)

    file_path = RUNS_DIR / f"{actual_data['run_id']}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(actual_data, f, indent=2, default=str)

    return actual_data


# ---------------------------------------------------------------------------
# Audit Log Functions
# ---------------------------------------------------------------------------

def write_audit(
    action: Union[str, Dict[str, Any]] = "",
    details: Optional[Dict[str, Any]] = None,
    entity_id: Optional[str] = None,
    entity_type: str = "profile",
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Write an audit log entry to Supabase or JSON fallback under backend/data/runs.
    Accepts action as string or full dict, with optional details and entity_id.
    """
    if isinstance(action, dict):
        entry = dict(action)
    else:
        entry = {
            "action": str(action),
            "details": details or {},
            "entity_id": str(entity_id) if entity_id else None,
            "entity_type": entity_type,
        }
    entry.update(kwargs)

    if not entry.get("audit_id"):
        entry["audit_id"] = str(uuid.uuid4())
    if not entry.get("timestamp"):
        entry["timestamp"] = datetime.now(timezone.utc).isoformat()

    if _supabase_client:
        try:
            resp = _supabase_client.table("audit_logs").insert(entry).execute()
            if resp.data:
                return resp.data[0]
        except Exception as exc:
            logger.warning("Supabase write_audit error: %s. Falling back to JSON.", exc)

    # Write individually to backend/data/runs/audit_{id}.json
    single_file = RUNS_DIR / f"audit_{entry['audit_id']}.json"
    with open(single_file, "w", encoding="utf-8") as f:
        json.dump(entry, f, indent=2, default=str)

    # Append to cumulative audit log backend/data/runs/audit_log.json
    log_file = RUNS_DIR / "audit_log.json"
    log_entries: List[Dict[str, Any]] = []
    if log_file.exists():
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                content = json.load(f)
                if isinstance(content, list):
                    log_entries = content
        except Exception:
            log_entries = []

    log_entries.append(entry)
    with open(log_file, "w", encoding="utf-8") as f:
        json.dump(log_entries, f, indent=2, default=str)

    return entry
