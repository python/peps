import datetime as dt
import importlib.util
import sys
from pathlib import Path

import pytest

# Import "pep-lint.py" as "pep_lint"
PEP_LINT_PATH = Path(__file__).resolve().parent.parent.parent.joinpath("pep-lint.py")
spec = importlib.util.spec_from_file_location("pep_lint", PEP_LINT_PATH)
sys.modules["pep_lint"] = pep_lint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pep_lint)


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


@pytest.mark.parametrize(
    "line",
    [
        "Alice",
        "Cardinal Ximénez",
        "Alice <alice@domain.example>",
        "Cardinal Ximénez <Cardinal.Ximenez@spanish.inquisition>",
    ],
)
def test_validate_sponsor(line: str):
    warnings = [warning for (_, warning) in pep_lint._validate_sponsor(1, line)]
    assert warnings == [], warnings


@pytest.mark.parametrize(
    "line",
    [
        "",
        "Alice, Bob, Charlie",
        "Alice, Bob, Charlie,",
        "Alice <alice@domain.example>",
        "Cardinal Ximénez <Cardinal.Ximenez@spanish.inquisition>",
    ],
)
def test_validate_delegate(line: str):
    warnings = [warning for (_, warning) in pep_lint._validate_delegate(1, line)]
    assert warnings == [], warnings


@pytest.mark.parametrize(
    "line",
    [
        "list-name@python.org",
        "distutils-sig@python.org",
        "csv@python.org",
        "python-3000@python.org",
        "ipaddr-py-dev@googlegroups.com",
        "python-tulip@googlegroups.com",
        "https://discuss.python.org/t/thread-name/123456",
        "https://discuss.python.org/t/thread-name/123456/",
        "https://discuss.python.org/t/thread_name/123456",
        "https://discuss.python.org/t/thread_name/123456/",
        "https://discuss.python.org/t/123456/",
        "https://discuss.python.org/t/123456",
    ],
)
def test_validate_discussions_to_valid(line: str):
    warnings = [warning for (_, warning) in pep_lint._validate_discussions_to(1, line)]
    assert warnings == [], warnings


@pytest.mark.parametrize(
    "line",
    [
        "$pecial+chars@python.org",
        "a-discussions-to-list!@googlegroups.com",
    ],
)
def test_validate_discussions_to_list_name(line: str):
    warnings = [warning for (_, warning) in pep_lint._validate_discussions_to(1, line)]
    assert warnings == ["Discussions-To must be a valid mailing list"], warnings


@pytest.mark.parametrize(
    "line",
    [
        "list-name@python.org.uk",
        "distutils-sig@mail-server.example",
    ],
)
def test_validate_discussions_to_invalid_list_domain(line: str):
    warnings = [warning for (_, warning) in pep_lint._validate_discussions_to(1, line)]
    assert warnings == ["Discussions-To must be a valid thread URL or mailing list"], warnings


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
    "body",
    [
        "",
        (
            "01-Jan-2001, 02-Feb-2002,\n              "
            "03-Mar-2003, 04-Apr-2004,\n              "
            "05-May-2005,"
        ),
        (
            "`01-Jan-2000 <https://mail.python.org/pipermail/list-name/0000-Month/0123456.html>`__,\n              "
            "`11-Mar-2005 <https://mail.python.org/archives/list/list-name@python.org/thread/abcdef0123456789/>`__,\n              "
            "`21-May-2010 <https://discuss.python.org/t/thread-name/123456/654321>`__,\n              "
            "`31-Jul-2015 <https://discuss.python.org/t/123456>`__,"
        ),
        "01-Jan-2001, `02-Feb-2002 <https://discuss.python.org/t/123456>`__,\n03-Mar-2003",
    ],
)
def test_validate_post_history_valid(body: str):
    warnings = [warning for (_, warning) in pep_lint._validate_post_history(1, body)]
    assert warnings == [], warnings


@pytest.mark.parametrize(
    "line",
    [
        "https://mail.python.org/archives/list/list-name@python.org/thread/abcXYZ123",
        "https://mail.python.org/archives/list/list-name@python.org/thread/abcXYZ123/",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123/",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123#Anchor",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123/#Anchor",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123#Anchor123",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123/#Anchor123",
    ],
)
def test_validate_resolution_valid(line: str):
    warnings = [warning for (_, warning) in pep_lint._validate_resolution(1, line)]
    assert warnings == [], warnings


@pytest.mark.parametrize(
    "line",
    [
        "https://mail.python.org/archives/list/list-name@python.org/thread",
        "https://mail.python.org/archives/list/list-name@python.org/message",
        "https://mail.python.org/archives/list/list-name@python.org/thread/",
        "https://mail.python.org/archives/list/list-name@python.org/message/",
        "https://mail.python.org/archives/list/list-name@python.org/thread/abcXYZ123#anchor",
        "https://mail.python.org/archives/list/list-name@python.org/thread/abcXYZ123/#anchor",
        "https://mail.python.org/archives/list/list-name@python.org/message/#abcXYZ123",
        "https://mail.python.org/archives/list/list-name@python.org/message/#abcXYZ123/",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123/anchor/",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123/anchor/",
        "https://mail.python.org/archives/list/list-name@python.org/spam/abcXYZ123",
        "https://mail.python.org/archives/list/list-name@python.org/spam/abcXYZ123/",
    ],
)
def test_validate_resolution_invalid(line: str):
    warnings = [warning for (_, warning) in pep_lint._validate_resolution(1, line)]
    assert warnings == ["Resolution must be a valid thread URL"], warnings


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


@pytest.mark.parametrize(
    ("email", "expected_warnings"),
    [
        # ... entries must not contain multiple '...'
        ("Cardinal Ximénez <<", {"multiple <"}),
        ("Cardinal Ximénez <<<", {"multiple <"}),
        ("Cardinal Ximénez >>", {"multiple >"}),
        ("Cardinal Ximénez >>>", {"multiple >"}),
        ("Cardinal Ximénez <<<>>>", {"multiple <", "multiple >"}),
        ("Cardinal Ximénez @@", {"multiple @"}),
        ("Cardinal Ximénez <<@@@>", {"multiple <", "multiple @"}),
        ("Cardinal Ximénez <@@@>>", {"multiple >", "multiple @"}),
        ("Cardinal Ximénez <<@@>>", {"multiple <", "multiple >", "multiple @"}),
        # valid names
        ("Cardinal Ximénez", set()),
        ("  Cardinal Ximénez", set()),
        ("\t\tCardinal Ximénez", set()),
        ("Cardinal Ximénez  ", set()),
        ("Cardinal Ximénez\t\t", set()),
        ("Cardinal O'Ximénez", set()),
        ("Cardinal Ximénez, Inquisitor", set()),
        ("Cardinal Ximénez-Biggles", set()),
        ("Cardinal Ximénez-Biggles, Inquisitor", set()),
        ("Cardinal T. S. I. Ximénez", set()),
        # ... entries must have a valid 'Name'
        ("Cardinal_Ximénez", {"valid name"}),
        ("Cardinal Ximénez 3", {"valid name"}),
        ("~ Cardinal Ximénez ~", {"valid name"}),
        ("Cardinal Ximénez!", {"valid name"}),
        ("@Cardinal Ximénez", {"valid name"}),
        ("Cardinal_Ximénez <>", {"valid name"}),
        ("Cardinal Ximénez 3 <>", {"valid name"}),
        ("~ Cardinal Ximénez ~ <>", {"valid name"}),
        ("Cardinal Ximénez! <>", {"valid name"}),
        ("@Cardinal Ximénez <>", {"valid name"}),
        # ... entries must be formatted as 'Name <email@example.com>'
        ("Cardinal Ximénez<>", {"name <email>"}),
        ("Cardinal Ximénez<", {"name <email>"}),
        ("Cardinal Ximénez <", {"name <email>"}),
        ("Cardinal Ximénez  <", {"name <email>"}),
        ("Cardinal Ximénez  <>", {"name <email>"}),
        # ... entries must contain a valid email address (missing)
        ("Cardinal Ximénez <>", {"valid email"}),
        ("Cardinal Ximénez <> ", {"valid email"}),
        ("Cardinal Ximénez <@> ", {"valid email"}),
        ("Cardinal Ximénez <at> ", {"valid email"}),
        ("Cardinal Ximénez < at > ", {"valid email"}),
        # ... entries must contain a valid email address (local)
        ("Cardinal Ximénez <Cardinal.Ximénez@spanish.inquisition>", {"valid email"}),
        ("Cardinal Ximénez <Cardinal.Ximénez at spanish.inquisition>", {"valid email"}),
        ("Cardinal Ximénez <Cardinal.Ximenez AT spanish.inquisition>", {"valid email"}),
        ("Cardinal Ximénez <Cardinal.Ximenez @spanish.inquisition> ", {"valid email"}),
        ("Cardinal Ximénez <Cardinal Ximenez@spanish.inquisition> ", {"valid email"}),
        ("Cardinal Ximénez < Cardinal Ximenez @spanish.inquisition> ", {"valid email"}),
        ("Cardinal Ximénez <(Cardinal.Ximenez)@spanish.inquisition>", {"valid email"}),
        ("Cardinal Ximénez <Cardinal,Ximenez@spanish.inquisition>", {"valid email"}),
        ("Cardinal Ximénez <Cardinal:Ximenez@spanish.inquisition>", {"valid email"}),
        ("Cardinal Ximénez <Cardinal;Ximenez@spanish.inquisition>", {"valid email"}),
        (
            "Cardinal Ximénez <Cardinal><Ximenez@spanish.inquisition>",
            {"multiple <", "multiple >", "valid email"},
        ),
        (
            "Cardinal Ximénez <Cardinal@Ximenez@spanish.inquisition>",
            {"multiple @", "valid email"},
        ),
        (r"Cardinal Ximénez <Cardinal\Ximenez@spanish.inquisition>", {"valid email"}),
        ("Cardinal Ximénez <[Cardinal.Ximenez]@spanish.inquisition>", {"valid email"}),
        ('Cardinal Ximénez <"Cardinal"Ximenez"@spanish.inquisition>', {"valid email"}),
        ("Cardinal Ximénez <Cardinal;Ximenez@spanish.inquisition>", {"valid email"}),
        ("Cardinal Ximénez <Cardinal£Ximénez@spanish.inquisition>", {"valid email"}),
        ("Cardinal Ximénez <Cardinal§Ximenez@spanish.inquisition>", {"valid email"}),
        # ... entries must contain a valid email address (domain)
        (
            "Cardinal Ximénez <Cardinal.Ximenez@spanish+american.inquisition>",
            {"valid email"},
        ),
        ("Cardinal Ximénez <Cardinal.Ximenez@spani$h.inquisition>", {"valid email"}),
        ("Cardinal Ximénez <Cardinal.Ximenez@spanish.inquisitioñ>", {"valid email"}),
        (
            "Cardinal Ximénez <Cardinal.Ximenez@th£.spanish.inquisition>",
            {"valid email"},
        ),
        # valid name-emails
        ("Cardinal Ximénez <Cardinal.Ximenez@spanish.inquisition>", set()),
        ("Cardinal Ximénez <Cardinal.Ximenez at spanish.inquisition>", set()),
        ("Cardinal Ximénez <Cardinal_Ximenez@spanish.inquisition>", set()),
        ("Cardinal Ximénez <Cardinal-Ximenez@spanish.inquisition>", set()),
        ("Cardinal Ximénez <Cardinal!Ximenez@spanish.inquisition>", set()),
        ("Cardinal Ximénez <Cardinal#Ximenez@spanish.inquisition>", set()),
        ("Cardinal Ximénez <Cardinal$Ximenez@spanish.inquisition>", set()),
        ("Cardinal Ximénez <Cardinal%Ximenez@spanish.inquisition>", set()),
        ("Cardinal Ximénez <Cardinal&Ximenez@spanish.inquisition>", set()),
        ("Cardinal Ximénez <Cardinal'Ximenez@spanish.inquisition>", set()),
        ("Cardinal Ximénez <Cardinal*Ximenez@spanish.inquisition>", set()),
        ("Cardinal Ximénez <Cardinal+Ximenez@spanish.inquisition>", set()),
        ("Cardinal Ximénez <Cardinal/Ximenez@spanish.inquisition>", set()),
        ("Cardinal Ximénez <Cardinal=Ximenez@spanish.inquisition>", set()),
        ("Cardinal Ximénez <Cardinal?Ximenez@spanish.inquisition>", set()),
        ("Cardinal Ximénez <Cardinal^Ximenez@spanish.inquisition>", set()),
        ("Cardinal Ximénez <{Cardinal.Ximenez}@spanish.inquisition>", set()),
        ("Cardinal Ximénez <Cardinal|Ximenez@spanish.inquisition>", set()),
        ("Cardinal Ximénez <Cardinal~Ximenez@spanish.inquisition>", set()),
        ("Cardinal Ximénez <Cardinal.Ximenez@español.inquisition>", set()),
        ("Cardinal Ximénez <Cardinal.Ximenez at español.inquisition>", set()),
        ("Cardinal Ximénez <Cardinal.Ximenez@spanish-american.inquisition>", set()),
    ],
    # call str() on each parameterised value in the test ID.
    ids=str,
)
def test_email_checker(email: str, expected_warnings: set):
    warnings = [warning for (_, warning) in pep_lint._email(1, email, "<Prefix>")]

    found_warnings = set()
    email = email.strip()

    if "multiple <" in expected_warnings:
        found_warnings.add("multiple <")
        expected = f"<Prefix> entries must not contain multiple '<': {email!r}"
        matching = [w for w in warnings if w == expected]
        assert matching == [expected], warnings

    if "multiple >" in expected_warnings:
        found_warnings.add("multiple >")
        expected = f"<Prefix> entries must not contain multiple '>': {email!r}"
        matching = [w for w in warnings if w == expected]
        assert matching == [expected], warnings

    if "multiple @" in expected_warnings:
        found_warnings.add("multiple @")
        expected = f"<Prefix> entries must not contain multiple '@': {email!r}"
        matching = [w for w in warnings if w == expected]
        assert matching == [expected], warnings

    if "valid name" in expected_warnings:
        found_warnings.add("valid name")
        expected = f"<Prefix> entries must begin with a valid 'Name': {email!r}"
        matching = [w for w in warnings if w == expected]
        assert matching == [expected], warnings

    if "name <email>" in expected_warnings:
        found_warnings.add("name <email>")
        expected = f"<Prefix> entries must be formatted as 'Name <email@example.com>': {email!r}"
        matching = [w for w in warnings if w == expected]
        assert matching == [expected], warnings

    if "valid email" in expected_warnings:
        found_warnings.add("valid email")
        expected = f"<Prefix> entries must contain a valid email address: {email!r}"
        matching = [w for w in warnings if w == expected]
        assert matching == [expected], warnings

    if expected_warnings == set():
        assert warnings == [], warnings

    assert found_warnings == expected_warnings


@pytest.mark.parametrize(
    "thread_url",
    [
        "https://discuss.python.org/t/thread-name/123456",
        "https://discuss.python.org/t/thread-name/123456/",
        "https://discuss.python.org/t/thread_name/123456",
        "https://discuss.python.org/t/thread_name/123456/",
        "https://discuss.python.org/t/thread-name/123456/654321/",
        "https://discuss.python.org/t/thread-name/123456/654321",
        "https://discuss.python.org/t/123456",
        "https://discuss.python.org/t/123456/",
        "https://discuss.python.org/t/123456/654321/",
        "https://discuss.python.org/t/123456/654321",
        "https://discuss.python.org/t/1",
        "https://discuss.python.org/t/1/",
        "https://mail.python.org/pipermail/list-name/0000-Month/0123456.html",
        "https://mail.python.org/archives/list/list-name@python.org/thread/abcXYZ123",
        "https://mail.python.org/archives/list/list-name@python.org/thread/abcXYZ123/",
    ],
)
def test_thread_checker_valid(thread_url: str):
    warnings = [warning for (_, warning) in pep_lint._thread(1, thread_url, "<Prefix>")]
    assert warnings == [], warnings


@pytest.mark.parametrize(
    "thread_url",
    [
        "http://link.example",
        "list-name@python.org",
        "distutils-sig@python.org",
        "csv@python.org",
        "python-3000@python.org",
        "ipaddr-py-dev@googlegroups.com",
        "python-tulip@googlegroups.com",
        "https://link.example",
        "https://discuss.python.org",
        "https://discuss.python.org/",
        "https://discuss.python.org/c/category",
        "https://discuss.python.org/t/thread_name/123456//",
        "https://discuss.python.org/t/thread+name/123456",
        "https://discuss.python.org/t/thread+name/123456#",
        "https://discuss.python.org/t/thread+name/123456/#",
        "https://discuss.python.org/t/thread+name/123456/#anchor",
        "https://discuss.python.org/t/thread+name/",
        "https://discuss.python.org/t/thread+name",
        "https://discuss.python.org/t/thread-name/123abc",
        "https://discuss.python.org/t/thread-name/123abc/",
        "https://discuss.python.org/t/thread-name/123456/123abc",
        "https://discuss.python.org/t/thread-name/123456/123abc/",
        "https://discuss.python.org/t/123/456/789",
        "https://discuss.python.org/t/123/456/789/",
        "https://discuss.python.org/t/#/",
        "https://discuss.python.org/t/#",
        "https://mail.python.org/pipermail/list+name/0000-Month/0123456.html",
        "https://mail.python.org/pipermail/list-name/YYYY-Month/0123456.html",
        "https://mail.python.org/pipermail/list-name/0123456/0123456.html",
        "https://mail.python.org/pipermail/list-name/0000-Month/0123456",
        "https://mail.python.org/pipermail/list-name/0000-Month/0123456/",
        "https://mail.python.org/pipermail/list-name/0000-Month/",
        "https://mail.python.org/pipermail/list-name/0000-Month",
        "https://mail.python.org/archives/list/list-name@python.org/thread/abcXYZ123#anchor",
        "https://mail.python.org/archives/list/list-name@python.org/thread/abcXYZ123/#anchor",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123/",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123#anchor",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123/#anchor",
        "https://mail.python.org/archives/list/list-name@python.org/spam/abcXYZ123",
        "https://mail.python.org/archives/list/list-name@python.org/spam/abcXYZ123/",
    ],
)
def test_thread_checker_invalid(thread_url: str):
    warnings = [warning for (_, warning) in pep_lint._thread(1, thread_url, "<Prefix>")]
    assert warnings == ["<Prefix> must be a valid thread URL"], warnings


@pytest.mark.parametrize(
    "thread_url",
    [
        "https://mail.python.org/archives/list/list-name@python.org/thread/abcXYZ123",
        "https://mail.python.org/archives/list/list-name@python.org/thread/abcXYZ123/",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123/",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123#Anchor",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123/#Anchor",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123#Anchor123",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123/#Anchor123",
    ],
)
def test_thread_checker_valid_allow_message(thread_url: str):
    warnings = [
        warning
        for (_, warning) in pep_lint._thread(
            1, thread_url, "<Prefix>", allow_message=True
        )
    ]
    assert warnings == [], warnings


@pytest.mark.parametrize(
    "thread_url",
    [
        "https://mail.python.org/archives/list/list-name@python.org/thread",
        "https://mail.python.org/archives/list/list-name@python.org/message",
        "https://mail.python.org/archives/list/list-name@python.org/thread/",
        "https://mail.python.org/archives/list/list-name@python.org/message/",
        "https://mail.python.org/archives/list/list-name@python.org/thread/abcXYZ123#anchor",
        "https://mail.python.org/archives/list/list-name@python.org/thread/abcXYZ123/#anchor",
        "https://mail.python.org/archives/list/list-name@python.org/message/#abcXYZ123",
        "https://mail.python.org/archives/list/list-name@python.org/message/#abcXYZ123/",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123/anchor/",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123/anchor/",
        "https://mail.python.org/archives/list/list-name@python.org/spam/abcXYZ123",
        "https://mail.python.org/archives/list/list-name@python.org/spam/abcXYZ123/",
    ],
)
def test_thread_checker_invalid_allow_message(thread_url: str):
    warnings = [
        warning
        for (_, warning) in pep_lint._thread(
            1, thread_url, "<Prefix>", allow_message=True
        )
    ]
    assert warnings == ["<Prefix> must be a valid thread URL"], warnings


@pytest.mark.parametrize(
    "thread_url",
    [
        "list-name@python.org",
        "distutils-sig@python.org",
        "csv@python.org",
        "python-3000@python.org",
        "ipaddr-py-dev@googlegroups.com",
        "python-tulip@googlegroups.com",
        "https://discuss.python.org/t/thread-name/123456",
        "https://discuss.python.org/t/thread-name/123456/",
        "https://discuss.python.org/t/thread_name/123456",
        "https://discuss.python.org/t/thread_name/123456/",
        "https://discuss.python.org/t/123456/",
        "https://discuss.python.org/t/123456",
    ],
)
def test_thread_checker_valid_discussions_to(thread_url: str):
    warnings = [
        warning
        for (_, warning) in pep_lint._thread(
            1, thread_url, "<Prefix>", discussions_to=True
        )
    ]
    assert warnings == [], warnings


@pytest.mark.parametrize(
    "thread_url",
    [
        "https://discuss.python.org/t/thread-name/123456/000",
        "https://discuss.python.org/t/thread-name/123456/000/",
        "https://discuss.python.org/t/thread_name/123456/000",
        "https://discuss.python.org/t/thread_name/123456/000/",
        "https://discuss.python.org/t/123456/000/",
        "https://discuss.python.org/t/12345656/000",
        "https://discuss.python.org/t/thread-name",
        "https://discuss.python.org/t/thread_name",
        "https://discuss.python.org/t/thread+name",
    ],
)
def test_thread_checker_invalid_discussions_to(thread_url: str):
    warnings = [
        warning
        for (_, warning) in pep_lint._thread(
            1, thread_url, "<Prefix>", discussions_to=True
        )
    ]
    assert warnings == ["<Prefix> must be a valid thread URL"], warnings


def test_thread_checker_allow_message_discussions_to():
    with pytest.raises(ValueError, match="cannot both be True"):
        list(
            pep_lint._thread(1, "", "<Prefix>", allow_message=True, discussions_to=True)
        )


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
