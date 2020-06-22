# -*- coding: utf-8 -*-
"""Code for handling object representation of a PEP."""
import re
import textwrap
import unicodedata
from email.message import Message
from email.parser import HeaderParser
from pathlib import Path
from typing import List, Tuple


class PEPError(Exception):
    def __init__(self, error, pep_file, pep_number=None):
        super(PEPError, self).__init__(error)
        self.filename = pep_file
        self.number = pep_number

    def __str__(self):
        error_msg = super(PEPError, self).__str__()
        if self.number is not None:
            return f"PEP {self.number}: {error_msg}"
        else:
            return f"({self.filename}): {error_msg}"


class PEPParseError(PEPError):

    pass


class Author:
    """Represent PEP authors.

    Attributes:

        + first_last : str
            The author's full name.

        + last_first : str
            Output the author's name in Last, First, Suffix order.

        + first : str
            The author's first name.  A middle initial may be included.

        + last : str
            The author's last name.

        + suffix : str
            A person's suffix (can be the empty string).

        + sort_by : str
            Modification of the author's last name that should be used for
            sorting.

        + email : str
            The author's email address.
    """

    def __init__(self, author_and_email_tuple, authors_lookup):
        """Parse the name and email address of an author."""
        name, email = author_and_email_tuple
        self.first_last = name.strip()
        self.email = email.lower()

        name_dict = authors_lookup[self.first_last]

        self.last_first = name_dict["Surname First"]
        self.nick = name_dict["Name Reference"]

    def __hash__(self):
        return hash(self.first_last)

    def __eq__(self, other):
        return self.first_last == other.first_last

    @property
    def sort_by(self):
        last = self.last_first.split(",")[0]
        name_parts = last.split()
        for index, part in enumerate(name_parts):
            if part[0].isupper():
                base = " ".join(name_parts[index:]).lower()
                break
        else:
            # If no capitals, use the whole string
            base = last.lower()
        return unicodedata.normalize("NFKD", base)


class PEP:
    """Representation of PEPs.

    Attributes:

        + number : int
            PEP number.

        + title : str
            PEP title.

        + type_ : str
            The type of PEP.  Can only be one of the values from
            PEP.type_values.

        + status : str
            The PEP's status.  Value must be found in PEP.status_values.

        + authors : Sequence(Author)
            A list of the authors.
    """

    # The various RFC 822 headers that are supported.
    # The second item in the nested tuples represents if the header is
    # required or not.
    headers = (
        ("PEP", True), ("Title", True), ("Version", False),
        ("Last-Modified", False), ("Author", True), ("Sponsor", False),
        ("BDFL-Delegate", False), ("Discussions-To", False), ("Status", True),
        ("Type", True), ("Content-Type", False), ("Requires", False),
        ("Created", True), ("Python-Version", False), ("Post-History", False),
        ("Replaces", False), ("Superseded-By", False), ("Resolution", False),
    )
    # Valid values for the Type header.
    type_values = ("Standards Track", "Informational", "Process")
    # Valid values for the Status header.
    # Active PEPs can only be for Informational or Process PEPs.
    status_values = (
        "Accepted", "Provisional", "Rejected", "Withdrawn",
        "Deferred", "Final", "Active", "Draft", "Superseded",
    )

    def __init__(self, pep_file: str, filename: str, author_lookup: dict):
        """Init object from an open PEP file object."""
        # Parse the headers.
        self.filename = filename
        pep_parser = HeaderParser()
        metadata = pep_parser.parsestr(pep_file)
        header_order = iter(self.headers)
        current_header = ""
        try:
            for header_name in metadata.keys():
                current_header, required = next(header_order)
                while header_name != current_header and not required:
                    current_header, required = next(header_order)
                if header_name != current_header:
                    raise PEPError(
                        "did not deal with "
                        f"{header_name} before having to handle {current_header}",
                        filename,
                    )
        except StopIteration:
            raise PEPError("headers missing or out of order", filename)
        required = False
        try:
            while not required:
                current_header, required = next(header_order)
            else:
                raise PEPError(f"PEP is missing its '{current_header}' header", filename)
        except StopIteration:
            pass
        # 'PEP'.
        try:
            self.number = int(metadata["PEP"])
        except ValueError:
            raise PEPParseError("PEP number isn't an integer", filename)
        # 'Title'.
        self.title = metadata["Title"]
        # 'Type'.
        type_ = metadata["Type"]
        if type_ not in self.type_values:
            raise PEPError(f"{type_} is not a valid Type value", filename, self.number)
        self.type_ = type_
        # 'Status'.
        status = metadata["Status"]
        if status not in self.status_values:
            if status == "April Fool!":
                # See PEP 401 :)
                status = "Rejected"
            else:
                raise PEPError(f"{status} is not a valid Status value", filename, self.number)
        # Special case for Active PEPs.
        if status == "Active" and self.type_ not in ("Process", "Informational"):
            raise PEPError(
                "Only Process and Informational PEPs may " "have an Active status",
                filename,
                self.number,
            )
        # Special case for Provisional PEPs.
        if status == "Provisional" and self.type_ != "Standards Track":
            raise PEPError(
                "Only Standards Track PEPs may " "have a Provisional status",
                filename,
                self.number,
            )
        self.status = status
        # 'Author'.
        authors_and_emails = self._parse_author(metadata["Author"])
        if len(authors_and_emails) < 1:
            raise PEPError("no authors found", filename, self.number)
        self.authors = [Author(author_email, author_lookup) for author_email in authors_and_emails]

    @staticmethod
    def _parse_author(data):
        """Return a list of author names and emails."""
        # XXX Consider using email.utils.parseaddr (doesn't work with names
        # lacking an email address.
        angled = "(?P<author>.+?) <(?P<email>.+?)>"
        paren = "(?P<email>.+?) \((?P<author>.+?)\)"
        simple = "(?P<author>[^,]+)"
        author_list = []
        for regex in (angled, paren, simple):
            # Watch out for commas separating multiple names.
            regex += r"(,\s*)?"
            for match in re.finditer(regex, data):
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
    def type_abbr(self):
        """Return how the type is to be represented in the index."""
        return self.type_[0].upper()

    @property
    def status_abbr(self):
        """Return how the status should be represented in the index."""
        if self.status in ("Draft", "Active"):
            return " "
        else:
            return self.status[0].upper()

    @property
    def author_abbr(self):
        """Return the author list as a comma-separated with only last names."""
        return ", ".join(x.nick for x in self.authors)

    @property
    def title_abbr(self):
        """Shorten the title to be no longer than the max title length."""
        if len(self.title) <= pep_0_constants.title_length:
            return self.title
        wrapped_title = textwrap.wrap(self.title, pep_0_constants.title_length - 4)
        return wrapped_title[0] + " ..."

    def __str__(self):
        """Return the line entry for the PEP."""
        pep_info = {
            "type": self.type_abbr,
            "number": str(self.number),
            "title": self.title_abbr,
            "status": self.status_abbr,
            "authors": self.author_abbr,
        }
        return pep_0_constants.column_format(**pep_info)
