import sys
from pathlib import Path

# Ensure backend directory is in sys.path
_backend_dir = Path(__file__).resolve().parent / "backend"
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from app.jd_analytics.router import router

__all__ = ["router"]
