import importlib.util
import sys
from pathlib import Path

# Import "pep-lint.py" as "pep_lint"
PEP_LINT_PATH = Path(__file__).resolve().parent.parent.parent.joinpath("pep-lint.py")
spec = importlib.util.spec_from_file_location("pep_lint", PEP_LINT_PATH)
sys.modules["pep_lint"] = pep_lint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pep_lint)


def test_header_pattern_capitalisation():
    pattern = pep_lint.HEADER_PATTERN

    assert pattern.match("Header:") is not None
    assert pattern.match("header:") is not None
    assert pattern.match("hEADER:") is not None
    assert pattern.match("hEaDeR:") is not None


def test_header_pattern_trailing_spaces():
    pattern = pep_lint.HEADER_PATTERN

    assert pattern.match("Header:") is not None
    assert pattern.match("Header: ") is not None
    assert pattern.match("Header:  ") is not None


def test_header_pattern_trailing_content():
    pattern = pep_lint.HEADER_PATTERN

    assert pattern.match("Header: Text") is not None
    assert pattern.match("Header: 123") is not None
    assert pattern.match("Header: !") is not None
    assert pattern.match("Header:Text") is None
    assert pattern.match("Header:123") is None
    assert pattern.match("Header:!") is None


def test_header_pattern_colon_position():
    pattern = pep_lint.HEADER_PATTERN

    assert pattern.match("Header") is None
    assert pattern.match("Header : ") is None
    assert pattern.match("Header :") is None


def test_header_pattern_separators():
    pattern = pep_lint.HEADER_PATTERN

    assert pattern.match("Hyphenated-Header:") is not None
    assert pattern.match("Underscored_Header:") is None
    assert pattern.match("Spaced Header:") is None
