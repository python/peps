import check_peps  # NoQA: inserted into sys.modules in conftest.py
import pytest


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
    assert check_peps.HEADER_PATTERN.match(test_input)[1] == expected


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
    assert check_peps.HEADER_PATTERN.match(test_input) is None


def test_validate_required_headers():
    found_headers = dict.fromkeys(
        ("PEP", "Title", "Author", "Status", "Type", "Created")
    )
    warnings = [
        warning for (_, warning) in check_peps._validate_required_headers(found_headers)
    ]
    assert warnings == [], warnings


def test_validate_required_headers_missing():
    found_headers = dict.fromkeys(("PEP", "Title", "Author", "Type"))
    warnings = [
        warning for (_, warning) in check_peps._validate_required_headers(found_headers)
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
        warning for (_, warning) in check_peps._validate_required_headers(found_headers)
    ]
    assert warnings == [
        "Headers must be in PEP 12 order. Correct order: PEP, Title, Author, Sponsor, Status, Type, Created, Replaces"
    ], warnings


@pytest.mark.parametrize(
    "line",
    [
        "!",
        "The Zen of Python",
        "A title that is exactly 79 characters long, but shorter than 80 characters long",
    ],
)
def test_validate_title(line: str):
    warnings = [warning for (_, warning) in check_peps._validate_title(1, line)]
    assert warnings == [], warnings


def test_validate_title_blank():
    warnings = [warning for (_, warning) in check_peps._validate_title(1, "-" * 80)]
    assert warnings == ["PEP title must be less than 80 characters"], warnings


def test_validate_title_too_long():
    warnings = [warning for (_, warning) in check_peps._validate_title(1, "")]
    assert warnings == ["PEP must have a title"], warnings


@pytest.mark.parametrize(
    "line",
    [
        "Accepted",
        "Active",
        "April Fool!",
        "Deferred",
        "Draft",
        "Final",
        "Provisional",
        "Rejected",
        "Superseded",
        "Withdrawn",
    ],
)
def test_validate_status_valid(line: str):
    warnings = [warning for (_, warning) in check_peps._validate_status(1, line)]
    assert warnings == [], warnings


@pytest.mark.parametrize(
    "line",
    [
        "Standards Track",
        "Informational",
        "Process",
        "accepted",
        "active",
        "april fool!",
        "deferred",
        "draft",
        "final",
        "provisional",
        "rejected",
        "superseded",
        "withdrawn",
    ],
)
def test_validate_status_invalid(line: str):
    warnings = [warning for (_, warning) in check_peps._validate_status(1, line)]
    assert warnings == ["Status must be a valid PEP status"], warnings


@pytest.mark.parametrize(
    "line",
    [
        "Standards Track",
        "Informational",
        "Process",
    ],
)
def test_validate_type_valid(line: str):
    warnings = [warning for (_, warning) in check_peps._validate_type(1, line)]
    assert warnings == [], warnings


@pytest.mark.parametrize(
    "line",
    [
        "standards track",
        "informational",
        "process",
        "Accepted",
        "Active",
        "April Fool!",
        "Deferred",
        "Draft",
        "Final",
        "Provisional",
        "Rejected",
        "Superseded",
        "Withdrawn",
    ],
)
def test_validate_type_invalid(line: str):
    warnings = [warning for (_, warning) in check_peps._validate_type(1, line)]
    assert warnings == ["Type must be a valid PEP type"], warnings


@pytest.mark.parametrize(
    ("line", "expected_warnings"),
    [
        # valid entries
        ("Governance", set()),
        ("Packaging", set()),
        ("Typing", set()),
        ("Release", set()),
        ("Governance, Packaging", set()),
        ("Packaging, Typing", set()),
        # duplicates
        ("Governance, Governance", {"duplicates"}),
        ("Release, Release", {"duplicates"}),
        ("Packaging, Packaging", {"duplicates"}),
        ("Spam, Spam", {"duplicates", "valid"}),
        ("lobster, lobster", {"duplicates", "capitalisation", "valid"}),
        ("governance, governance", {"duplicates", "capitalisation"}),
        # capitalisation
        ("governance", {"capitalisation"}),
        ("packaging", {"capitalisation"}),
        ("typing", {"capitalisation"}),
        ("release", {"capitalisation"}),
        ("Governance, release", {"capitalisation"}),
        # validity
        ("Spam", {"valid"}),
        ("lobster", {"capitalisation", "valid"}),
        # sorted
        ("Packaging, Governance", {"sorted"}),
        ("Typing, Release", {"sorted"}),
        ("Release, Governance", {"sorted"}),
        ("spam, packaging", {"capitalisation", "valid", "sorted"}),
    ],
    # call str() on each parameterised value in the test ID.
    ids=str,
)
def test_validate_topic(line: str, expected_warnings: set):
    warnings = [warning for (_, warning) in check_peps._validate_topic(1, line)]

    found_warnings = set()

    if "duplicates" in expected_warnings:
        found_warnings.add("duplicates")
        expected = "Topic must not contain duplicates"
        matching = [w for w in warnings if w == expected]
        assert matching == [expected], warnings

    if "capitalisation" in expected_warnings:
        found_warnings.add("capitalisation")
        expected = "Topic must be properly capitalised (Title Case)"
        matching = [w for w in warnings if w == expected]
        assert matching == [expected], warnings

    if "valid" in expected_warnings:
        found_warnings.add("valid")
        expected = "Topic must be for a valid sub-index"
        matching = [w for w in warnings if w == expected]
        assert matching == [expected], warnings

    if "sorted" in expected_warnings:
        found_warnings.add("sorted")
        expected = "Topic must be sorted lexicographically"
        matching = [w for w in warnings if w == expected]
        assert matching == [expected], warnings

    if expected_warnings == set():
        assert warnings == [], warnings

    assert found_warnings == expected_warnings


@pytest.mark.parametrize(
    "line",
    [
        "0, 1, 8, 12, 20,",
        "101, 801,",
        "3099, 9999",
    ],
)
def test_validate_pep_references(line: str):
    warnings = [
        warning for (_, warning) in check_peps._validate_pep_references(1, line)
    ]
    assert warnings == [], warnings


@pytest.mark.parametrize(
    "line",
    [
        "0,1,8, 12, 20,",
        "101,801,",
        "3099, 9998,9999",
    ],
)
def test_validate_pep_references_separators(line: str):
    warnings = [
        warning for (_, warning) in check_peps._validate_pep_references(1, line)
    ]
    assert warnings == [
        "PEP references must be separated by comma-spaces (', ')"
    ], warnings


@pytest.mark.parametrize(
    ("line", "expected_warnings"),
    [
        # valid entries
        ("1.0, 2.4, 2.7, 2.8, 3.0, 3.1, 3.4, 3.7, 3.11, 3.14", set()),
        ("2.x", set()),
        ("3.x", set()),
        ("3.0.1", set()),
        # segments
        ("", {"segments"}),
        ("1", {"segments"}),
        ("1.2.3.4", {"segments"}),
        # major
        ("0.0", {"major"}),
        ("4.0", {"major"}),
        ("9.0", {"major"}),
        # minor number
        ("3.a", {"minor numeric"}),
        ("3.spam", {"minor numeric"}),
        ("3.0+", {"minor numeric"}),
        ("3.0-9", {"minor numeric"}),
        ("9.Z", {"major", "minor numeric"}),
        # minor leading zero
        ("3.01", {"minor zero"}),
        ("0.00", {"major", "minor zero"}),
        # micro empty
        ("3.x.1", {"micro empty"}),
        ("9.x.1", {"major", "micro empty"}),
        # micro leading zero
        ("3.3.0", {"micro zero"}),
        ("3.3.00", {"micro zero"}),
        ("3.3.01", {"micro zero"}),
        ("3.0.0", {"micro zero"}),
        ("3.00.0", {"minor zero", "micro zero"}),
        ("0.00.0", {"major", "minor zero", "micro zero"}),
        # micro number
        ("3.0.a", {"micro numeric"}),
        ("0.3.a", {"major", "micro numeric"}),
    ],
    # call str() on each parameterised value in the test ID.
    ids=str,
)
def test_validate_python_version(line: str, expected_warnings: set):
    warnings = [
        warning for (_, warning) in check_peps._validate_python_version(1, line)
    ]

    found_warnings = set()

    if "segments" in expected_warnings:
        found_warnings.add("segments")
        expected = f"Python-Version must have two or three segments: {line}"
        matching = [w for w in warnings if w == expected]
        assert matching == [expected], warnings

    if "major" in expected_warnings:
        found_warnings.add("major")
        expected = f"Python-Version major part must be 1, 2, or 3: {line}"
        matching = [w for w in warnings if w == expected]
        assert matching == [expected], warnings

    if "minor numeric" in expected_warnings:
        found_warnings.add("minor numeric")
        expected = f"Python-Version minor part must be numeric: {line}"
        matching = [w for w in warnings if w == expected]
        assert matching == [expected], warnings

    if "minor zero" in expected_warnings:
        found_warnings.add("minor zero")
        expected = f"Python-Version minor part must not have leading zeros: {line}"
        matching = [w for w in warnings if w == expected]
        assert matching == [expected], warnings

    if "micro empty" in expected_warnings:
        found_warnings.add("micro empty")
        expected = (
            f"Python-Version micro part must be empty if minor part is 'x': {line}"
        )
        matching = [w for w in warnings if w == expected]
        assert matching == [expected], warnings

    if "micro zero" in expected_warnings:
        found_warnings.add("micro zero")
        expected = f"Python-Version micro part must not have leading zeros: {line}"
        matching = [w for w in warnings if w == expected]
        assert matching == [expected], warnings

    if "micro numeric" in expected_warnings:
        found_warnings.add("micro numeric")
        expected = f"Python-Version micro part must be numeric: {line}"
        matching = [w for w in warnings if w == expected]
        assert matching == [expected], warnings

    if expected_warnings == set():
        assert warnings == [], warnings

    assert found_warnings == expected_warnings
