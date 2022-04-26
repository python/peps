from pathlib import Path

import pytest

from pep_sphinx_extensions.pep_zero_generator import parser
from pep_sphinx_extensions.pep_zero_generator.author import Author
from pep_sphinx_extensions.pep_zero_generator.errors import PEPError
from pep_sphinx_extensions.tests.utils import AUTHORS_OVERRIDES


def test_pep_repr():
    pep8 = parser.PEP(Path("pep-0008.txt"), AUTHORS_OVERRIDES)

    assert repr(pep8) == "<PEP 0008 - Style Guide for Python Code>"


def test_pep_less_than():
    pep8 = parser.PEP(Path("pep-0008.txt"), AUTHORS_OVERRIDES)
    pep3333 = parser.PEP(Path("pep-3333.txt"), AUTHORS_OVERRIDES)

    assert pep8 < pep3333


def test_pep_equal():
    pep_a = parser.PEP(Path("pep-0008.txt"), AUTHORS_OVERRIDES)
    pep_b = parser.PEP(Path("pep-0008.txt"), AUTHORS_OVERRIDES)

    assert pep_a == pep_b


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (80, "Style Guide for Python Code"),
        (10, "Style ..."),
    ],
)
def test_pep_details(test_input, expected):
    pep8 = parser.PEP(Path("pep-0008.txt"), AUTHORS_OVERRIDES)

    assert pep8.details(title_length=test_input) == {
        "authors": "GvR, Warsaw, Coghlan",
        "number": 8,
        "status": " ",
        "title": expected,
        "type": "P",
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
    pep = parser.PEP(Path("pep-0160.txt"), AUTHORS_OVERRIDES)

    # Act
    out = parser._parse_authors(pep, test_input, AUTHORS_OVERRIDES)

    # Assert
    assert out == expected


def test_parse_authors_invalid():

    pep = parser.PEP(Path("pep-0008.txt"), AUTHORS_OVERRIDES)

    with pytest.raises(PEPError, match="no authors found"):
        parser._parse_authors(pep, "", AUTHORS_OVERRIDES)
