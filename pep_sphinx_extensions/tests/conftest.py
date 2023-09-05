import importlib.util
import sys
from pathlib import Path

PEP_ROOT = Path(__file__, "..", "..", "..").resolve()

# Import "check-peps.py" as "check_peps"
CHECK_PEPS_PATH = Path(__file__).resolve().parents[2] / "check-peps.py"
spec = importlib.util.spec_from_file_location("check_peps", CHECK_PEPS_PATH)
sys.modules["check_peps"] = check_peps = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_peps)
