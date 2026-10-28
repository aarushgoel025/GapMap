import sys
from pathlib import Path

# Ensure root directory is accessible so shared.schemas can be imported
_root_dir = Path(__file__).resolve().parents[3]
if str(_root_dir) not in sys.path:
    sys.path.insert(0, str(_root_dir))

from shared.schemas import *  # noqa: F401, F403
