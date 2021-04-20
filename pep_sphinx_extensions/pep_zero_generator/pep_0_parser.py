"""Code for handling object representation of a PEP."""

from __future__ import annotations

from email.parser import HeaderParser
from pathlib import Path
import re
import textwrap
from typing import NamedTuple
import unicodedata


class PEPError(Exception):
    def __init__(self, error: str, pep_file: Path, pep_number: int | None = None):
        super().__init__(error)
        self.filename = pep_file
        self.number = pep_number

    def __str__(self):
        error_msg = super(PEPError, self).__str__()
        error_msg = f"({self.filename}): {error_msg}"
        pep_str = f"PEP {self.number}"
        return f"{pep_str} {error_msg}" if self.number is not None else error_msg


class Name(NamedTuple):
    name: str = None  # mononym
    forename: str = None
    surname: str = None
    suffix: str = None


class Author:
    """Represent PEP authors.

    Attributes:
        last_first: The author's name in Surname, Forename, Suffix order.
        nick: Author's nickname for PEP tables. Defaults to surname.
        email: The author's email address.
        _first_last: The author's full name, unchanged

    """
    __slots__ = "last_first", "nick", "email", "_first_last"

    def __init__(self, author_email_tuple: tuple[str, str], authors_exceptions: dict[str, dict[str, str]]):
        """Parse the name and email address of an author."""
        name, email = author_email_tuple
        self._first_last: str = name.strip()
        self.email: str = email.lower()

        self.last_first: str = ""
        self.nick: str = ""

        if self._first_last in authors_exceptions:
            name_dict = authors_exceptions[self._first_last]
            self.last_first = name_dict["Surname First"]
            self.nick = name_dict["Name Reference"]
        else:
            name_parts = self._parse_name(self._first_last)
            if name_parts.name is not None:
                self.last_first = self.nick = name_parts.name
            else:
                if name_parts.surname[1] == ".":
                    # Add an escape to avoid docutils turning `v.` into `22.`.
                    name_parts.surname = f"\\{name_parts.surname}"
                self.last_first = f"{name_parts.surname}, {name_parts.forename}"
                self.nick = name_parts.surname

            if name_parts.suffix is not None:
                self.last_first += f", {name_parts.suffix}"

    def __hash__(self):
        return hash(self.last_first)

    def __eq__(self, other):
        if not isinstance(other, Author):
            return NotImplemented
        return self.last_first == other.last_first

    def __len__(self):
        return len(unicodedata.normalize("NFC", self.last_first))

    @staticmethod
    def _parse_name(full_name: str) -> Name:
        """Decompose a full name into parts.

        If a mononym (e.g, 'Aahz') then return the full name. If there are
        suffixes in the name (e.g. ', Jr.' or 'III'), then find and extract
        them. If there is a middle initial followed by a full stop, then
        combine the following words into a surname (e.g. N. Vander Weele). If
        there is a leading, lowercase portion to the last name (e.g. 'van' or
        'von') then include it in the surname.

        """
        possible_suffixes = {"Jr", "Jr.", "II", "III"}

        pre_suffix, _, raw_suffix = full_name.partition(",")
        name_parts = pre_suffix.strip().split(" ")
        num_parts = len(name_parts)
        suffix = raw_suffix.strip() or None

        if num_parts == 0:
            raise ValueError("Name is empty!")
        elif num_parts == 1:
            return Name(name=name_parts[0], suffix=suffix)
        elif num_parts == 2:
            return Name(forename=name_parts[0].strip(), surname=name_parts[1], suffix=suffix)

        # handles rogue uncaught suffixes
        if name_parts[-1] in possible_suffixes:
            suffix = f"{name_parts.pop(-1)} {suffix}".strip()

        # handles von, van, v. etc.
        if name_parts[-2].islower():
            forename = " ".join(name_parts[:-2]).strip()
            surname = " ".join(name_parts[-2:])
            return Name(forename=forename, surname=surname, suffix=suffix)

        # handles double surnames after a middle initial (e.g. N. Vander Weele)
        elif any(s.endswith(".") for s in name_parts):
            split_position = [i for i, x in enumerate(name_parts) if x.endswith(".")][-1] + 1
            forename = " ".join(name_parts[:split_position]).strip()
            surname = " ".join(name_parts[split_position:])
            return Name(forename=forename, surname=surname, suffix=suffix)

        # default to using the last item as the surname
        else:
            forename = " ".join(name_parts[:-1]).strip()
            return Name(forename=forename, surname=name_parts[-1], suffix=suffix)


def author_sort_by(author: Author) -> str:
    """Skip lower-cased words in surname when sorting."""
    surname, *_ = author.last_first.split(",")
    surname_parts = surname.split()
    for i, part in enumerate(surname_parts):
        if part[0].isupper():
            base = " ".join(surname_parts[i:]).lower()
            return unicodedata.normalize("NFKD", base)
    # If no capitals, use the whole string
    return unicodedata.normalize("NFKD", surname.lower())


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

    # Valid values for the Type header.
    type_values = {"Standards Track", "Informational", "Process"}
    # Valid values for the Status header.
    # Active PEPs can only be for Informational or Process PEPs.
    status_values = {
        "Accepted", "Provisional", "Rejected", "Withdrawn",
        "Deferred", "Final", "Active", "Draft", "Superseded",
    }

    def raise_pep_error(self, msg: str, pep_num: bool = False) -> None:
        pep_number = self.number if pep_num else None
        raise PEPError(msg, self.filename, pep_number=pep_number)

    def __init__(self, filename: Path, author_lookup: dict, title_length: int):
        """Init object from an open PEP file object.

        pep_file is full text of the PEP file, filename is path of the PEP file, author_lookup is author exceptions file

        """
        self.filename: Path = filename
        self.title_length: int = title_length

        # Parse the headers.
        pep_text = filename.read_text("UTF8")
        metadata = HeaderParser().parsestr(pep_text)
        required_header_misses = self.required_headers - set(metadata.keys())
        if required_header_misses:
            msg = f"PEP is missing required headers ({', '.join(required_header_misses)})"
            self.raise_pep_error(msg)

        try:
            self.number: int = int(metadata["PEP"])
        except ValueError:
            self.raise_pep_error("PEP number isn't an integer")

        # Check PEP number matches filename
        if self.number != int(filename.stem[4:]):
            self.raise_pep_error(f"PEP number does not match file name ({filename})", pep_num=True)

        # Title
        self.title: str = metadata["Title"]

        # Type
        self.pep_type: str = metadata["Type"]
        if self.pep_type not in self.type_values:
            self.raise_pep_error(f"{self.pep_type} is not a valid Type value", pep_num=True)

        # Status
        status = metadata["Status"]
        if status not in self.status_values:
            if status == "April Fool!":  # See PEP 401 :)
                status = "Rejected"
            else:
                self.raise_pep_error(f"{status} is not a valid Status value", pep_num=True)

        # Special case for Active PEPs.
        if status == "Active" and self.pep_type not in {"Process", "Informational"}:
            msg = "Only Process and Informational PEPs may have an Active status"
            self.raise_pep_error(msg, pep_num=True)

        # Special case for Provisional PEPs.
        if status == "Provisional" and self.pep_type != "Standards Track":
            msg = "Only Standards Track PEPs may have a Provisional status"
            self.raise_pep_error(msg, pep_num=True)
        self.status: str = status

        # Parse PEP authors
        self.authors: list[Author] = self.parse_authors(metadata["Author"], author_lookup)

    def parse_authors(self, author_header: str, author_lookup: dict) -> list[Author]:
        """Parse Author header line"""
        authors_and_emails = self._parse_author(author_header)
        if not authors_and_emails:
            raise self.raise_pep_error("no authors found", pep_num=True)
        return [Author(author_tuple, author_lookup) for author_tuple in authors_and_emails]

    angled = re.compile(r"(?P<author>.+?) <(?P<email>.+?)>(,\s*)?")
    paren = re.compile(r"(?P<email>.+?) \((?P<author>.+?)\)(,\s*)?")
    simple = re.compile(r"(?P<author>[^,]+)(,\s*)?")

    @staticmethod
    def _parse_author(data: str) -> list[tuple[str, str]]:
        """Return a list of author names and emails."""
        # XXX Consider using email.utils.parseaddr (doesn't work with names
        # lacking an email address.

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
            else:
                # If authors were found then stop searching as only expect one
                # style of author citation.
                if author_list:
                    break
        return author_list

    @property
    def title_abbr(self) -> str:
        """Shorten the title to be no longer than the max title length."""
        if len(self.title) <= self.title_length:
            return self.title
        wrapped_title, *_excess = textwrap.wrap(self.title, self.title_length - 4)
        return f"{wrapped_title} ..."

    @property
    def pep(self) -> dict[str, str | int]:
        """Return the line entry for the PEP."""
        return {
            # how the type is to be represented in the index
            "type": self.pep_type[0].upper(),
            "number": self.number,
            "title": self.title_abbr,
            # how the status should be represented in the index
            "status": self.status[0].upper() if self.status not in {"Draft", "Active"} else " ",
            # the author list as a comma-separated with only last names
            "authors": ", ".join(x.nick for x in self.authors),
        }
