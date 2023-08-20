import pytest

import pep_lint  # NoQA: inserted into sys.modules in conftest.py


@pytest.mark.parametrize(
    ("test_input", "expected"),
    [
        # capitalisation
        ("Header:", "Header"),
        ("header:", "header"),
        ("hEADER:", "hEADER"),
        ("hEaDeR:", "hEaDeR"),
        # trailing spaces
        ("Header: ", "Header"),
        ("Header:  ", "Header"),
        ("Header:   \t", "Header"),
        # trailing content
        ("Header: Text", "Header"),
        ("Header: 123", "Header"),
        ("Header: !", "Header"),
        # separators
        ("Hyphenated-Header:", "Hyphenated-Header"),
    ],
)
def test_header_pattern(test_input, expected):
    assert pep_lint.HEADER_PATTERN.match(test_input)[1] == expected


@pytest.mark.parametrize(
    "test_input",
    [
        # trailing content
        "Header:Text",
        "Header:123",
        "Header:!",
        # colon position
        "Header",
        "Header : ",
        "Header :",
        "SemiColonHeader;",
        # separators
        "Underscored_Header:",
        "Spaced Header:",
        "Plus+Header:",
    ],
)
def test_header_pattern_no_match(test_input):
    assert pep_lint.HEADER_PATTERN.match(test_input) is None


def test_validate_required_headers():
    found_headers = dict.fromkeys(
        ("PEP", "Title", "Author", "Status", "Type", "Created")
    )
    warnings = [
        warning for (_, warning) in pep_lint._validate_required_headers(found_headers)
    ]
    assert warnings == [], warnings


def test_validate_required_headers_missing():
    found_headers = dict.fromkeys(("PEP", "Title", "Author", "Type"))
    warnings = [
        warning for (_, warning) in pep_lint._validate_required_headers(found_headers)
    ]
    assert warnings == [
        "Must have required header: Status",
        "Must have required header: Created",
    ], warnings


def test_validate_required_headers_order():
    found_headers = dict.fromkeys(
        ("PEP", "Title", "Sponsor", "Author", "Type", "Status", "Replaces", "Created")
    )
    warnings = [
        warning for (_, warning) in pep_lint._validate_required_headers(found_headers)
    ]
    assert warnings == [
        "Headers must be in PEP 12 order. Correct order: PEP, Title, Author, Sponsor, Status, Type, Created, Replaces"
    ], warnings
