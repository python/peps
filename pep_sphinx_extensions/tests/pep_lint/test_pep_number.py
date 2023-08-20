import pytest

import pep_lint  # NoQA: inserted into sys.modules in conftest.py


@pytest.mark.parametrize(
    "line",
    [
        "PEP: 0",
        "PEP:      12",
    ],
)
def test_validate_pep_number(line: str):
    warnings = [warning for (_, warning) in pep_lint._validate_pep_number(line)]
    assert warnings == [], warnings


@pytest.mark.parametrize(
    "line",
    [
        "0",
        "PEP:12",
        "PEP 0",
        "PEP 12",
        "PEP:0",
    ],
)
def test_validate_pep_number_invalid_header(line: str):
    warnings = [warning for (_, warning) in pep_lint._validate_pep_number(line)]
    assert warnings == ["PEP must begin with the 'PEP:' header"], warnings


@pytest.mark.parametrize(
    ("pep_number", "expected_warnings"),
    [
        # valid entries
        ("0", set()),
        ("1", set()),
        ("12", set()),
        ("20", set()),
        ("101", set()),
        ("801", set()),
        ("3099", set()),
        ("9999", set()),
        # empty
        ("", {"not blank"}),
        # leading zeros
        ("01", {"leading zeros"}),
        ("001", {"leading zeros"}),
        ("0001", {"leading zeros"}),
        ("00001", {"leading zeros"}),
        # non-numeric
        ("a", {"non-numeric"}),
        ("123abc", {"non-numeric"}),
        ("0123A", {"leading zeros", "non-numeric"}),
        ("０", {"non-numeric"}),
        ("10１", {"non-numeric"}),
        ("999９", {"non-numeric"}),
        ("𝟎", {"non-numeric"}),
        ("𝟘", {"non-numeric"}),
        ("𝟏𝟚", {"non-numeric"}),
        ("𝟸𝟬", {"non-numeric"}),
        ("-1", {"non-numeric"}),
        ("+1", {"non-numeric"}),
        # out of bounds
        ("10000", {"range"}),
        ("54321", {"range"}),
        ("99999", {"range"}),
        ("32768", {"range"}),
    ],
    # call str() on each parameterised value in the test ID.
    ids=str,
)
def test_pep_num_checker(pep_number: str, expected_warnings: set):
    warnings = [
        warning for (_, warning) in pep_lint._pep_num(1, pep_number, "<Prefix>")
    ]

    found_warnings = set()
    pep_number = pep_number.strip()

    if "not blank" in expected_warnings:
        found_warnings.add("not blank")
        expected = f"<Prefix> must not be blank: {pep_number!r}"
        matching = [w for w in warnings if w == expected]
        assert matching == [expected], warnings

    if "leading zeros" in expected_warnings:
        found_warnings.add("leading zeros")
        expected = f"<Prefix> must not contain leading zeros: {pep_number!r}"
        matching = [w for w in warnings if w == expected]
        assert matching == [expected], warnings

    if "non-numeric" in expected_warnings:
        found_warnings.add("non-numeric")
        expected = f"<Prefix> must be numeric: {pep_number!r}"
        matching = [w for w in warnings if w == expected]
        assert matching == [expected], warnings

    if "range" in expected_warnings:
        found_warnings.add("range")
        expected = f"<Prefix> must be between 0 and 9999: {pep_number!r}"
        matching = [w for w in warnings if w == expected]
        assert matching == [expected], warnings

    if expected_warnings == set():
        assert warnings == [], warnings

    assert found_warnings == expected_warnings
