import pep_lint  # NoQA: inserted into sys.modules in conftest.py
import pytest


@pytest.mark.parametrize(
    "line",
    [
        "Alice",
        "Alice,",
        "Alice, Bob, Charlie",
        "Alice,\nBob,\nCharlie",
        "Alice,\n   Bob,\n   Charlie",
        "Alice,\n        Bob,\n        Charlie",
        "Cardinal Ximénez",
        "Alice <alice@domain.example>",
        "Cardinal Ximénez <Cardinal.Ximenez@spanish.inquisition>",
    ],
    ids=repr,  # the default calls str and renders newlines.
)
def test_validate_author(line: str):
    warnings = [warning for (_, warning) in pep_lint._validate_author(1, line)]
    assert warnings == [], warnings


@pytest.mark.parametrize(
    "line",
    [
        "Alice,\n         Bob,\n        Charlie",
        "Alice,\n        Bob,\n         Charlie",
        "Alice,\n         Bob,\n         Charlie",
        "Alice,\n              Bob",
    ],
    ids=repr,  # the default calls str and renders newlines.
)
def test_validate_author_over__indented(line: str):
    warnings = [warning for (_, warning) in pep_lint._validate_author(1, line)]
    assert {*warnings} == {"Author line must not be over-indented"}, warnings


@pytest.mark.parametrize(
    "line",
    [
        "Cardinal Ximénez\nCardinal Biggles\nCardinal Fang",
        "Cardinal Ximénez,\nCardinal Biggles\nCardinal Fang",
        "Cardinal Ximénez\nCardinal Biggles,\nCardinal Fang",
    ],
    ids=repr,  # the default calls str and renders newlines.
)
def test_validate_author_continuation(line: str):
    warnings = [warning for (_, warning) in pep_lint._validate_author(1, line)]
    assert {*warnings} == {"Author continuation lines must end with a comma"}, warnings


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
