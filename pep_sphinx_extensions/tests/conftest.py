import importlib.util
import sys
from pathlib import Path

# Import "check-pep.py" as "check_pep"
CHECK_PEP_PATH = Path(__file__).resolve().parents[2] / "check-pep.py"
spec = importlib.util.spec_from_file_location("check_pep", CHECK_PEP_PATH)
sys.modules["check_pep"] = check_pep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_pep)
