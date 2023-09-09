import importlib.util
import sys
from pathlib import Path

_ROOT_PATH = Path(__file__, "..", "..", "..").resolve()
PEP_ROOT = _ROOT_PATH / "peps"

# Import "check-peps.py" as "check_peps"
CHECK_PEPS_PATH = _ROOT_PATH / "check-peps.py"
spec = importlib.util.spec_from_file_location("check_peps", CHECK_PEPS_PATH)
sys.modules["check_peps"] = check_peps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_peps)
