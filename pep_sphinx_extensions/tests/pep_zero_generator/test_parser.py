import pytest

from pep_sphinx_extensions.pep_zero_generator import parser
from pep_sphinx_extensions.pep_zero_generator.constants import (
    STATUS_ACCEPTED,
    STATUS_ACTIVE,
    STATUS_DEFERRED,
    STATUS_DRAFT,
    STATUS_FINAL,
    STATUS_PROVISIONAL,
    STATUS_REJECTED,
    STATUS_SUPERSEDED,
    STATUS_WITHDRAWN,
    TYPE_INFO,
    TYPE_PROCESS,
    TYPE_STANDARDS,
)
from pep_sphinx_extensions.pep_zero_generator.parser import _Author

from ..conftest import PEP_ROOT


def test_pep_repr():
    pep8 = parser.PEP(PEP_ROOT / "pep-0008.rst")

    assert repr(pep8) == "<PEP 0008 - Style Guide for Python Code>"


def test_pep_less_than():
    pep8 = parser.PEP(PEP_ROOT / "pep-0008.rst")
    pep3333 = parser.PEP(PEP_ROOT / "pep-3333.rst")

    assert pep8 < pep3333


def test_pep_equal():
    pep_a = parser.PEP(PEP_ROOT / "pep-0008.rst")
    pep_b = parser.PEP(PEP_ROOT / "pep-0008.rst")

    assert pep_a == pep_b


@pytest.mark.parametrize(
    ("test_input", "expected"),
    [
        (
            "pep-0008.rst",
            {
                "authors": "Guido van Rossum, Barry Warsaw, Alyssa Coghlan",
                "number": 8,
                "shorthand": ":abbr:`PA (Process, Active)`",
                "title": "Style Guide for Python Code",
                "python_version": "",
            },
        ),
        (
            "pep-0719.rst",
            {
                "authors": "Thomas Wouters",
                "number": 719,
                "shorthand": ":abbr:`IA (Informational, Active)`",
                "title": "Python 3.13 Release Schedule",
                "python_version": "3.13",
            },
        ),
    ],
)
def test_pep_details(test_input, expected):
    pep = parser.PEP(PEP_ROOT / test_input)

    assert pep.details == expected


@pytest.mark.parametrize(
    ("test_input", "expected"),
    [
        (
            "First Last <user@example.com>",
            [_Author(full_name="First Last", email="user@example.com")],
        ),
        (
            "First Last",
            [_Author(full_name="First Last", email="")],
        ),
        pytest.param(
            "First Last <user at example.com>",
            [_Author(full_name="First Last", email="user@example.com")],
            marks=pytest.mark.xfail,
        ),
        pytest.param(
            " , First Last,",
            {"First Last": ""},
            marks=pytest.mark.xfail(raises=ValueError),
        ),
    ],
)
def test_parse_authors(test_input, expected):
    # Act
    out = parser._parse_author(test_input)

    # Assert
    assert out == expected


def test_parse_authors_invalid():
    with pytest.raises(ValueError, match="Name is empty!"):
        assert parser._parse_author("")


@pytest.mark.parametrize(
    ("test_type", "test_status", "expected"),
    [
        (TYPE_INFO, STATUS_DRAFT, ":abbr:`I (Informational, Draft)`"),
        (TYPE_INFO, STATUS_ACTIVE, ":abbr:`IA (Informational, Active)`"),
        (TYPE_INFO, STATUS_ACCEPTED, ":abbr:`IA (Informational, Accepted)`"),
        (TYPE_INFO, STATUS_DEFERRED, ":abbr:`ID (Informational, Deferred)`"),
        (TYPE_PROCESS, STATUS_ACCEPTED, ":abbr:`PA (Process, Accepted)`"),
        (TYPE_PROCESS, STATUS_ACTIVE, ":abbr:`PA (Process, Active)`"),
        (TYPE_PROCESS, STATUS_FINAL, ":abbr:`PF (Process, Final)`"),
        (TYPE_PROCESS, STATUS_SUPERSEDED, ":abbr:`PS (Process, Superseded)`"),
        (TYPE_PROCESS, STATUS_WITHDRAWN, ":abbr:`PW (Process, Withdrawn)`"),
        (TYPE_STANDARDS, STATUS_ACCEPTED, ":abbr:`SA (Standards Track, Accepted)`"),
        (TYPE_STANDARDS, STATUS_REJECTED, ":abbr:`SR (Standards Track, Rejected)`"),
        (TYPE_STANDARDS, STATUS_PROVISIONAL, ":abbr:`SP (Standards Track, Provisional)`"),  # fmt: skip
    ],
)
def test_abbreviate_type_status(test_type, test_status, expected):
    # set up dummy PEP object and monkeypatch attributes
    pep = parser.PEP(PEP_ROOT / "pep-0008.rst")
    pep.pep_type = test_type
    pep.status = test_status

    assert pep.shorthand == expected
