import datetime as dt

import pytest

import pep_lint  # NoQA: inserted into sys.modules in conftest.py


@pytest.mark.parametrize(
    "line",
    [
        "!",
        "The Zen of Python",
        "A title that is exactly 79 characters long, but shorter than 80 characters long",
    ],
)
def test_validate_title(line: str):
    warnings = [warning for (_, warning) in pep_lint._validate_title(1, line)]
    assert warnings == [], warnings


def test_validate_title_blank():
    warnings = [warning for (_, warning) in pep_lint._validate_title(1, "-" * 80)]
    assert warnings == ["PEP title must be less than 80 characters"], warnings


def test_validate_title_too_long():
    warnings = [warning for (_, warning) in pep_lint._validate_title(1, "")]
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
    warnings = [warning for (_, warning) in pep_lint._validate_status(1, line)]
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
    warnings = [warning for (_, warning) in pep_lint._validate_status(1, line)]
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
    warnings = [warning for (_, warning) in pep_lint._validate_type(1, line)]
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
    warnings = [warning for (_, warning) in pep_lint._validate_type(1, line)]
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
        ("Release, Release", {"duplicates"}),
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
    warnings = [warning for (_, warning) in pep_lint._validate_topic(1, line)]

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


def test_validate_content_type_valid():
    warnings = [
        warning for (_, warning) in pep_lint._validate_content_type(1, "text/x-rst")
    ]
    assert warnings == [], warnings


@pytest.mark.parametrize(
    "line",
    [
        "text/plain",
        "text/markdown",
        "text/csv",
        "text/rtf",
        "text/javascript",
        "text/html",
        "text/xml",
    ],
)
def test_validate_content_type_invalid(line: str):
    warnings = [warning for (_, warning) in pep_lint._validate_content_type(1, line)]
    assert warnings == ["Content-Type must be 'text/x-rst'"], warnings


@pytest.mark.parametrize(
    "line",
    [
        "0, 1, 8, 12, 20,",
        "101, 801,",
        "3099, 9999",
    ],
)
def test_validate_pep_references(line: str):
    warnings = [warning for (_, warning) in pep_lint._validate_pep_references(1, line)]
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
    warnings = [warning for (_, warning) in pep_lint._validate_pep_references(1, line)]
    assert warnings == [
        "PEP references must be separated by comma-spaces (', ')"
    ], warnings


@pytest.mark.parametrize(
    "line",
    [
        # valid entries
        "01-Jan-2000",
        "29-Feb-2016",
        "31-Dec-2000",
        "01-Apr-2003",
        "01-Apr-2007",
        "01-Apr-2009",
        "01-Jan-1990",
    ],
)
def test_validate_created(line: str):
    warnings = [warning for (_, warning) in pep_lint._validate_created(1, line)]
    assert warnings == [], warnings


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
    warnings = [warning for (_, warning) in pep_lint._validate_python_version(1, line)]

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


@pytest.mark.parametrize(
    "date_str",
    [
        # valid entries
        "01-Jan-2000",
        "29-Feb-2016",
        "31-Dec-2000",
        "01-Apr-2003",
        "01-Apr-2007",
        "01-Apr-2009",
        "01-Jan-1990",
    ],
)
def test_date_checker_valid(date_str: str):
    warnings = [warning for (_, warning) in pep_lint._date(1, date_str, "<Prefix>")]
    assert warnings == [], warnings


@pytest.mark.parametrize(
    "date_str",
    [
        # malformed
        "2000-01-01",
        "01 January 2000",
        "1 Jan 2000",
        "1-Jan-2000",
        "1-January-2000",
        "Jan-1-2000",
        "January 1 2000",
        "January 01 2000",
        "01/01/2000",
        "01/Jan/2000",  # 🇬🇧, 🇦🇺, 🇨🇦, 🇳🇿, 🇮🇪 , ...
        "Jan/01/2000",  # 🇺🇸
        "1st January 2000",
        "The First day of January in the year of Our Lord Two Thousand",
        "Jan, 1, 2000",
        "2000-Jan-1",
        "2000-Jan-01",
        "2000-January-1",
        "2000-January-01",
        "00 Jan 2000",
        "00-Jan-2000",
    ],
)
def test_date_checker_malformed(date_str: str):
    warnings = [warning for (_, warning) in pep_lint._date(1, date_str, "<Prefix>")]
    expected = f"<Prefix> must be a 'DD-mmm-YYYY' date: {date_str!r}"
    assert warnings == [expected], warnings


@pytest.mark.parametrize(
    "date_str",
    [
        # too early
        "31-Dec-1989",
        "01-Apr-1916",
        "01-Jan-0020",
        "01-Jan-0023",
    ],
)
def test_date_checker_too_early(date_str: str):
    warnings = [warning for (_, warning) in pep_lint._date(1, date_str, "<Prefix>")]
    expected = f"<Prefix> must not be before Python was invented: {date_str!r}"
    assert warnings == [expected], warnings


@pytest.mark.parametrize(
    "date_str",
    [
        # the future
        "31-Dec-2999",
        "01-Jan-2100",
        "01-Jan-2100",
        (dt.datetime.now() + dt.timedelta(days=15)).strftime("%d-%b-%Y"),
        (dt.datetime.now() + dt.timedelta(days=100)).strftime("%d-%b-%Y"),
    ],
)
def test_date_checker_too_late(date_str: str):
    warnings = [warning for (_, warning) in pep_lint._date(1, date_str, "<Prefix>")]
    expected = f"<Prefix> must not be in the future: {date_str!r}"
    assert warnings == [expected], warnings
