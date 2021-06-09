"""Code for handling object representation of a PEP."""

from __future__ import annotations

from email.parser import HeaderParser
from pathlib import Path
import re
import textwrap

from pep_sphinx_extensions.pep_zero_generator.author import Author
from pep_sphinx_extensions.pep_zero_generator.constants import STATUS_PROVISIONAL
from pep_sphinx_extensions.pep_zero_generator.constants import STATUS_ACTIVE
from pep_sphinx_extensions.pep_zero_generator.constants import TYPE_STANDARDS
from pep_sphinx_extensions.pep_zero_generator.constants import type_values
from pep_sphinx_extensions.pep_zero_generator.constants import status_values
from pep_sphinx_extensions.pep_zero_generator.constants import special_statuses
from pep_sphinx_extensions.pep_zero_generator.constants import active_allowed
from pep_sphinx_extensions.pep_zero_generator.constants import hide_status
from pep_sphinx_extensions.pep_zero_generator.errors import PEPError


class PEP:
    """Representation of PEPs.

    Attributes:
        number : PEP number.
        title : PEP title.
        pep_type : The type of PEP.  Can only be one of the values from PEP.type_values.
        status : The PEP's status.  Value must be found in PEP.status_values.
        authors : A list of the authors.

    """

    # The required RFC 822 headers for all PEPs.
    required_headers = {"PEP", "Title", "Author", "Status", "Type", "Created"}

    def raise_pep_error(self, msg: str, pep_num: bool = False) -> None:
        pep_number = self.number if pep_num else None
        raise PEPError(msg, self.filename, pep_number=pep_number)

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
            self.raise_pep_error(f"PEP is missing required headers {required_header_misses}")

        try:
            self.number = int(metadata["PEP"])
        except ValueError:
            self.raise_pep_error("PEP number isn't an integer")

        # Check PEP number matches filename
        if self.number != int(filename.stem[4:]):
            self.raise_pep_error(f"PEP number does not match file name ({filename})", pep_num=True)

        # Title
        self.title: str = metadata["Title"]

        # Type
        self.pep_type: str = metadata["Type"]
        if self.pep_type not in type_values:
            self.raise_pep_error(f"{self.pep_type} is not a valid Type value", pep_num=True)

        # Status
        status = metadata["Status"]
        if status in special_statuses:
            status = special_statuses[status]
        if status not in status_values:
            self.raise_pep_error(f"{status} is not a valid Status value", pep_num=True)

        # Special case for Active PEPs.
        if status == STATUS_ACTIVE and self.pep_type not in active_allowed:
            msg = "Only Process and Informational PEPs may have an Active status"
            self.raise_pep_error(msg, pep_num=True)

        # Special case for Provisional PEPs.
        if status == STATUS_PROVISIONAL and self.pep_type != TYPE_STANDARDS:
            msg = "Only Standards Track PEPs may have a Provisional status"
            self.raise_pep_error(msg, pep_num=True)
        self.status: str = status

        # Parse PEP authors
        self.authors: list[Author] = self.parse_authors(metadata["Author"], authors_overrides)

    def parse_authors(self, author_header: str, authors_overrides: dict) -> list[Author]:
        """Parse Author header line"""
        authors_and_emails = self._parse_author(author_header)
        if not authors_and_emails:
            raise self.raise_pep_error("no authors found", pep_num=True)
        return [Author(author_tuple, authors_overrides) for author_tuple in authors_and_emails]

    angled = re.compile(r"(?P<author>.+?) <(?P<email>.+?)>(,\s*)?")
    paren = re.compile(r"(?P<email>.+?) \((?P<author>.+?)\)(,\s*)?")
    simple = re.compile(r"(?P<author>[^,]+)(,\s*)?")

    @staticmethod
    def _parse_author(data: str) -> list[tuple[str, str]]:
        """Return a list of author names and emails."""

        author_list = []
        for regex in (PEP.angled, PEP.paren, PEP.simple):
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

    def title_abbr(self, title_length) -> str:
        """Shorten the title to be no longer than the max title length."""
        if len(self.title) <= title_length:
            return self.title
        wrapped_title, *_excess = textwrap.wrap(self.title, title_length - 4)
        return f"{wrapped_title} ..."

    def pep(self, *, title_length) -> dict[str, str | int]:
        """Return the line entry for the PEP."""
        return {
            # how the type is to be represented in the index
            "type": self.pep_type[0].upper(),
            "number": self.number,
            "title": self.title_abbr(title_length),
            # how the status should be represented in the index
            "status": self.status[0].upper() if self.status not in hide_status else " ",
            # the author list as a comma-separated with only last names
            "authors": ", ".join(x.nick for x in self.authors),
        }
