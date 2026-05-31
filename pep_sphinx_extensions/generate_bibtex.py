# This file is placed in the public domain or under the
# CC0-1.0-Universal license, whichever is more permissive.

from __future__ import annotations

import re
import textwrap
from pathlib import Path

from pep_sphinx_extensions.doctree import get_from_doctree

# LaTeX special characters that need escaping in BibTeX values
_BIBTEX_SPECIAL = re.compile(r"([&%$#_{}~^])")
_EMAIL_ADDRESS = re.compile(r"\s*<[^>]+>")


def _escape_bibtex(text: str) -> str:
    """Escape special BibTeX characters in a string."""
    return _BIBTEX_SPECIAL.sub(r"\\\1", text)


def _parse_created(created: str) -> tuple[str, str]:
    """Parse a PEP 'Created' date string (e.g. '01-Jan-2020') into (year, month).

    Returns the year as a string and the BibTeX month abbreviation.
    """
    _, month_abbr, year = created.split("-")
    return year, month_abbr.lower()


def _format_authors(author_header: str) -> str:
    """Format the Author header value for BibTeX.

    Strips email addresses and joins names with " and ".
    """
    # Remove email addresses in angle brackets
    author_header = _EMAIL_ADDRESS.sub("", author_header)
    # Split on commas and clean up
    authors = [name.strip() for name in author_header.split(",") if name.strip()]
    return " and ".join(authors)


def _generate_bibtex_entry(full_path: Path) -> str:
    """Generate a BibTeX entry for a single PEP from its doctree."""
    number = int(get_from_doctree(full_path, "PEP"))
    created = get_from_doctree(full_path, "Created")
    author = get_from_doctree(full_path, "Author")
    title = get_from_doctree(full_path, "Title")

    year, month = _parse_created(created)
    authors_bibtex = _escape_bibtex(_format_authors(author))
    title_escaped = _escape_bibtex(title)

    return textwrap.dedent(f"""\
        @techreport{{pep{number},
            author = "{authors_bibtex}",
            title = "PEP {number} --- {title_escaped}",
            institution = "Python Software Foundation",
            year = "{year}",
            month = {month},
            type = "PEP",
            number = "{number}",
            url = "https://peps.python.org/pep-{number:0>4}/",
        }}""")


def create_bibtex_files(doctree_dir: str, output_dir: str) -> None:
    """Generate a .bib file for each PEP in the output directory."""
    out = Path(output_dir)
    for doctree_file in Path(doctree_dir).glob("pep-????.doctree"):
        pep_name = doctree_file.stem  # for example "pep-0008"
        entry = _generate_bibtex_entry(doctree_file)
        (out / f"{pep_name}.bib").write_text(entry + "\n", encoding="utf-8")
