from pathlib import Path

import pytest

from pep_sphinx_extensions.pep_zero_generator import parser
from pep_sphinx_extensions.pep_zero_generator.author import Author
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
from pep_sphinx_extensions.pep_zero_generator.errors import PEPError
from pep_sphinx_extensions.tests.utils import AUTHORS_OVERRIDES


def test_pep_repr():
    pep8 = parser.PEP(Path("pep-0008.txt"))

    assert repr(pep8) == "<PEP 0008 - Style Guide for Python Code>"


def test_pep_less_than():
    pep8 = parser.PEP(Path("pep-0008.txt"))
    pep3333 = parser.PEP(Path("pep-3333.txt"))

    assert pep8 < pep3333


def test_pep_equal():
    pep_a = parser.PEP(Path("pep-0008.txt"))
    pep_b = parser.PEP(Path("pep-0008.txt"))

    assert pep_a == pep_b


def test_pep_details(monkeypatch):
    pep8 = parser.PEP(Path("pep-0008.txt"))

    assert pep8.details == {
        "authors": "GvR, Warsaw, Coghlan",
        "number": 8,
        "shorthand": ":abbr:`PA (Process, Active)`",
        "title": "Style Guide for Python Code",
    }


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (
            "First Last <user@example.com>",
            [Author(last_first="Last, First", nick="Last", email="user@example.com")],
        ),
        (
            "First Last",
            [Author(last_first="Last, First", nick="Last", email="")],
        ),
        (
            "user@example.com (First Last)",
            [Author(last_first="Last, First", nick="Last", email="user@example.com")],
        ),
        pytest.param(
            "First Last <user at example.com>",
            [Author(last_first="Last, First", nick="Last", email="user@example.com")],
            marks=pytest.mark.xfail,
        ),
    ],
)
def test_parse_authors(test_input, expected):
    # Arrange
    dummy_object = parser.PEP(Path("pep-0160.txt"))

    # Act
    out = parser._parse_authors(dummy_object, test_input, AUTHORS_OVERRIDES)

    # Assert
    assert out == expected


def test_parse_authors_invalid():

    pep = parser.PEP(Path("pep-0008.txt"))

    with pytest.raises(PEPError, match="no authors found"):
        parser._parse_authors(pep, "", AUTHORS_OVERRIDES)


@pytest.mark.parametrize(
    "test_type, test_status, expected",
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
    pep = parser.PEP(Path("pep-0008.txt"))
    pep.pep_type = test_type
    pep.status = test_status

    assert pep.shorthand == expected
