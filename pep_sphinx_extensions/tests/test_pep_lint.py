import importlib.util
import sys
from pathlib import Path

import pytest

# Import "pep-lint.py" as "pep_lint"
PEP_LINT_PATH = Path(__file__).resolve().parent.parent.parent.joinpath("pep-lint.py")
spec = importlib.util.spec_from_file_location("pep_lint", PEP_LINT_PATH)
sys.modules["pep_lint"] = pep_lint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pep_lint)


def test_header_pattern_capitalisation():
    pattern = pep_lint.HEADER_PATTERN

    assert pattern.match("Header:")[1] == "Header"
    assert pattern.match("header:")[1] == "header"
    assert pattern.match("hEADER:")[1] == "hEADER"
    assert pattern.match("hEaDeR:")[1] == "hEaDeR"


def test_header_pattern_trailing_spaces():
    pattern = pep_lint.HEADER_PATTERN

    assert pattern.match("Header:")[1] == "Header"
    assert pattern.match("Header: ")[1] == "Header"
    assert pattern.match("Header:  ")[1] == "Header"


def test_header_pattern_trailing_content():
    pattern = pep_lint.HEADER_PATTERN

    assert pattern.match("Header: Text")[1] == "Header"
    assert pattern.match("Header: 123")[1] == "Header"
    assert pattern.match("Header: !")[1] == "Header"
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

    assert pattern.match("Hyphenated-Header:")[1] == "Hyphenated-Header"
    assert pattern.match("Underscored_Header:") is None
    assert pattern.match("Spaced Header:") is None


@pytest.mark.parametrize(
    ("email", "expected_warnings"),
    [
        ("Cardinal Ximénez", {}),
    ]
)
def test_email_checker(email, expected_warnings):

    warnings = list(pep_lint._email(1, email, "<Prefix>"))

    if "valid name" in expected_warnings:
        expected_warnings.remove("valid name")
        matching = [warning for warning in warnings
                    if f"<Prefix> entries must begin with a valid 'Name': {email!r}" == warning]
        assert len(matching) == 1

