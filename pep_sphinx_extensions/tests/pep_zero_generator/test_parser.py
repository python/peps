from pathlib import Path

import pytest

from pep_sphinx_extensions.pep_zero_generator import parser
from pep_sphinx_extensions.pep_zero_generator.author import Author
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
        "shorthand": ":abbr:`P (Process)`",
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
        ("", "", ""),
        ("I", " ", ":abbr:`I (Informational)`"),
        ("I", "A", ":abbr:`I A (Informational, Active)`"),
        ("I", "D", ":abbr:`I D (Informational, Deferred)`"),
        ("P", "F", ":abbr:`P F (Process, Final)`"),
        ("P", "S", ":abbr:`P S (Process, Superseded)`"),
        ("P", "W", ":abbr:`P W (Process, Withdrawn)`"),
        ("S", "A", ":abbr:`S A (Standards Track, Accepted)`"),
        ("S", "R", ":abbr:`S R (Standards Track, Rejected)`"),
        ("S", "P", ":abbr:`S P (Standards Track, Provisional)`"),
    ],
)
def test_abbreviate_type_status(test_type, test_status, expected):
    assert parser._abbreviate_type_status(test_type, test_status) == expected
