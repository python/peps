"""Code for handling object representation of a PEP."""

from __future__ import annotations

from email.parser import HeaderParser
from pathlib import Path
import re
import textwrap
from typing import TYPE_CHECKING

from pep_sphinx_extensions.pep_zero_generator.author import parse_author_email
from pep_sphinx_extensions.pep_zero_generator.constants import ACTIVE_ALLOWED
from pep_sphinx_extensions.pep_zero_generator.constants import HIDE_STATUS
from pep_sphinx_extensions.pep_zero_generator.constants import SPECIAL_STATUSES
from pep_sphinx_extensions.pep_zero_generator.constants import STATUS_ACTIVE
from pep_sphinx_extensions.pep_zero_generator.constants import STATUS_PROVISIONAL
from pep_sphinx_extensions.pep_zero_generator.constants import STATUS_VALUES
from pep_sphinx_extensions.pep_zero_generator.constants import TYPE_STANDARDS
from pep_sphinx_extensions.pep_zero_generator.constants import TYPE_VALUES
from pep_sphinx_extensions.pep_zero_generator.errors import PEPError

if TYPE_CHECKING:
    from pep_sphinx_extensions.pep_zero_generator.author import Author


class PEP:
    """Representation of PEPs.

    Attributes:
        number : PEP number.
        title : PEP title.
        pep_type : The type of PEP.  Can only be one of the values from TYPE_VALUES.
        status : The PEP's status.  Value must be found in STATUS_VALUES.
        authors : A list of the authors.

    """

    # The required RFC 822 headers for all PEPs.
    required_headers = {"PEP", "Title", "Author", "Status", "Type", "Created"}

    def __init__(self, filename: Path, authors_overrides: dict):
        """Init object from an open PEP file object.

        pep_file is full text of the PEP file, filename is path of the PEP file, author_lookup is author exceptions file

        """
        self.filename: Path = filename

        # Parse the headers.
        pep_text = filename.read_text(encoding="utf-8")
        metadata = HeaderParser().parsestr(pep_text)
        required_header_misses = PEP.required_headers - set(metadata.keys())
        if required_header_misses:
            _raise_pep_error(self, f"PEP is missing required headers {required_header_misses}")

        try:
            self.number = int(metadata["PEP"])
        except ValueError:
            _raise_pep_error(self, "PEP number isn't an integer")

        # Check PEP number matches filename
        if self.number != int(filename.stem[4:]):
            _raise_pep_error(self, f"PEP number does not match file name ({filename})", pep_num=True)

        # Title
        self.title: str = metadata["Title"]

        # Type
        self.pep_type: str = metadata["Type"]
        if self.pep_type not in TYPE_VALUES:
            _raise_pep_error(self, f"{self.pep_type} is not a valid Type value", pep_num=True)

        # Status
        status = metadata["Status"]
        if status in SPECIAL_STATUSES:
            status = SPECIAL_STATUSES[status]
        if status not in STATUS_VALUES:
            _raise_pep_error(self, f"{status} is not a valid Status value", pep_num=True)

        # Special case for Active PEPs.
        if status == STATUS_ACTIVE and self.pep_type not in ACTIVE_ALLOWED:
            msg = "Only Process and Informational PEPs may have an Active status"
            _raise_pep_error(self, msg, pep_num=True)

        # Special case for Provisional PEPs.
        if status == STATUS_PROVISIONAL and self.pep_type != TYPE_STANDARDS:
            msg = "Only Standards Track PEPs may have a Provisional status"
            _raise_pep_error(self, msg, pep_num=True)
        self.status: str = status

        # Parse PEP authors
        self.authors: list[Author] = _parse_authors(self, metadata["Author"], authors_overrides)

    def __repr__(self) -> str:
        return f"<PEP {self.number:0>4} - {self.title}>"

    def __lt__(self, other: PEP) -> bool:
        return self.number < other.number

    def details(self, *, title_length) -> dict[str, str | int]:
        """Return the line entry for the PEP."""
        return {
            # how the type is to be represented in the index
            "type": self.pep_type[0].upper(),
            "number": self.number,
            "title": _title_abbr(self.title, title_length),
            # how the status should be represented in the index
            "status": " " if self.status in HIDE_STATUS else self.status[0].upper(),
            # the author list as a comma-separated with only last names
            "authors": ", ".join(x.nick for x in self.authors),
        }


def _raise_pep_error(pep: PEP, msg: str, pep_num: bool = False) -> None:
    if pep_num:
        raise PEPError(msg, pep.filename, pep_number=pep.number)
    raise PEPError(msg, pep.filename)


def _parse_authors(pep: PEP, author_header: str, authors_overrides: dict) -> list[Author]:
    """Parse Author header line"""
    authors_and_emails = _parse_author(author_header)
    if not authors_and_emails:
        raise _raise_pep_error(pep, "no authors found", pep_num=True)
    return [parse_author_email(author_tuple, authors_overrides) for author_tuple in authors_and_emails]


author_angled = re.compile(r"(?P<author>.+?) <(?P<email>.+?)>(,\s*)?")
author_paren = re.compile(r"(?P<email>.+?) \((?P<author>.+?)\)(,\s*)?")
author_simple = re.compile(r"(?P<author>[^,]+)(,\s*)?")


def _parse_author(data: str) -> list[tuple[str, str]]:
    """Return a list of author names and emails."""

    author_list = []
    for regex in (author_angled, author_paren, author_simple):
        for match in regex.finditer(data):
            # Watch out for suffixes like 'Jr.' when they are comma-separated
            # from the name and thus cause issues when *all* names are only
            # separated by commas.
            match_dict = match.groupdict()
            author = match_dict["author"]
            if not author.partition(" ")[1] and author.endswith("."):
                prev_author = author_list.pop()
                author = ", ".join([prev_author, author])
            if "email" not in match_dict:
                email = ""
            else:
                email = match_dict["email"]
            author_list.append((author, email))

        # If authors were found then stop searching as only expect one
        # style of author citation.
        if author_list:
            break
    return author_list


def _title_abbr(title, title_length) -> str:
    """Shorten the title to be no longer than the max title length."""
    if len(title) <= title_length:
        return title
    wrapped_title, *_excess = textwrap.wrap(title, title_length - 4)
    return f"{wrapped_title} ..."
