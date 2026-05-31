from pathlib import Path
from unittest.mock import patch

import pytest

from pep_sphinx_extensions.generate_bibtex import (
    _escape_bibtex,
    _format_authors,
    _generate_bibtex_entry,
    _parse_created,
    create_bibtex_files,
)

MOCK_TARGET = "pep_sphinx_extensions.generate_bibtex.get_from_doctree"

PEP_8_HEADERS = {
    "PEP": "8",
    "Title": "Style Guide for Python Code",
    "Author": "Guido van Rossum, Barry Warsaw, Alyssa Coghlan",
    "Created": "05-Jul-2001",
}


def _mock_doctree(headers: dict[str, str]):
    """Return a mock get_from_doctree that returns values from headers dict."""
    return lambda full_path, text: headers.get(text, "")


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Hello World", "Hello World"),
        ("Tom & Jerry", r"Tom \& Jerry"),
        ("100%", r"100\%"),
        ("$x$", r"\$x\$"),
        ("C#", r"C\#"),
        ("snake_case", r"snake\_case"),
        ("{}", r"\{\}"),
        ("~tilde", r"\~tilde"),
        ("no specials", "no specials"),
    ],
)
def test_escape_bibtex(text: str, expected: str) -> None:
    assert _escape_bibtex(text) == expected


@pytest.mark.parametrize(
    ("created", "expected"),
    [
        ("01-Jan-1990", ("1990", "jan")),
        ("15-Sep-2021", ("2021", "sep")),
        ("28-Feb-2000", ("2000", "feb")),
    ],
)
def test_parse_created(created: str, expected: tuple[str, str]) -> None:
    assert _parse_created(created) == expected


@pytest.mark.parametrize(
    ("author_header", "expected"),
    [
        ("Cardinal Ximénez", "Cardinal Ximénez"),
        (
            "Cardinal Ximénez <Cardinal.Ximenez@spanish.inquisition>,"
            " Cardinal Biggles <Cardinal.Biggles@spanish.inquisition>",
            "Cardinal Ximénez and Cardinal Biggles",
        ),
        (
            "Cardinal Ximénez,\n Cardinal Biggles",
            "Cardinal Ximénez and Cardinal Biggles",
        ),
        (
            "Cardinal Ximénez, Cardinal Biggles, Cardinal Fang",
            "Cardinal Ximénez and Cardinal Biggles and Cardinal Fang",
        ),
    ],
)
def test_format_authors(author_header: str, expected: str) -> None:
    assert _format_authors(author_header) == expected


def test_generate_bibtex_entry() -> None:
    # Arrange / Act
    with patch(MOCK_TARGET, _mock_doctree(PEP_8_HEADERS)):
        result = _generate_bibtex_entry(Path("pep-0008.doctree"))

    # Assert
    assert "@techreport{pep8," in result
    assert 'author = "Guido van Rossum and Barry Warsaw and Alyssa Coghlan"' in result
    assert 'title = "PEP 8 --- Style Guide for Python Code"' in result
    assert 'year = "2001"' in result
    assert "month = jul," in result
    assert 'number = "8"' in result
    assert 'url = "https://peps.python.org/pep-0008/"' in result


def test_generate_bibtex_entry_title_escaped() -> None:
    # Arrange
    headers = {**PEP_8_HEADERS, "PEP": "999", "Title": "Use of $ & % in PEPs"}

    # Act
    with patch(MOCK_TARGET, _mock_doctree(headers)):
        result = _generate_bibtex_entry(Path("pep-0999.doctree"))

    # Assert
    assert r"Use of \$ \& \% in PEPs" in result


def test_generate_bibtex_entry_author_escaped() -> None:
    # Arrange
    headers = {**PEP_8_HEADERS, "Author": "Tom & Jerry <tj@example.com>"}

    # Act
    with patch(MOCK_TARGET, _mock_doctree(headers)):
        result = _generate_bibtex_entry(Path("pep-0008.doctree"))

    # Assert
    assert r"Tom \& Jerry" in result


def test_create_bibtex_files(tmp_path: Path) -> None:
    # Arrange
    doctree_dir = tmp_path / "doctrees"
    doctree_dir.mkdir()
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    (doctree_dir / "pep-0008.doctree").touch()

    # Act
    with patch(MOCK_TARGET, _mock_doctree(PEP_8_HEADERS)):
        create_bibtex_files(str(doctree_dir), str(output_dir))

    # Assert
    bib = (output_dir / "pep-0008.bib").read_text()
    assert "@techreport{pep8," in bib
    assert 'author = "Guido van Rossum and Barry Warsaw and Alyssa Coghlan"' in bib


def test_create_bibtex_files_no_doctrees(tmp_path: Path) -> None:
    # Arrange
    doctree_dir = tmp_path / "doctrees"
    doctree_dir.mkdir()
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    # Act
    create_bibtex_files(str(doctree_dir), str(output_dir))

    # Assert
    assert list(output_dir.glob("*.bib")) == []
