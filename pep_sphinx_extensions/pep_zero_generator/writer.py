"""Code to handle the output of PEP 0."""

from __future__ import annotations

import datetime
import functools
from typing import TYPE_CHECKING
import unicodedata

from pep_sphinx_extensions.pep_zero_generator.constants import DEAD_STATUSES
from pep_sphinx_extensions.pep_zero_generator.constants import HIDE_STATUS
from pep_sphinx_extensions.pep_zero_generator.constants import STATUS_ACCEPTED
from pep_sphinx_extensions.pep_zero_generator.constants import STATUS_ACTIVE
from pep_sphinx_extensions.pep_zero_generator.constants import STATUS_DEFERRED
from pep_sphinx_extensions.pep_zero_generator.constants import STATUS_DRAFT
from pep_sphinx_extensions.pep_zero_generator.constants import STATUS_FINAL
from pep_sphinx_extensions.pep_zero_generator.constants import STATUS_PROVISIONAL
from pep_sphinx_extensions.pep_zero_generator.constants import STATUS_REJECTED
from pep_sphinx_extensions.pep_zero_generator.constants import STATUS_VALUES
from pep_sphinx_extensions.pep_zero_generator.constants import STATUS_WITHDRAWN
from pep_sphinx_extensions.pep_zero_generator.constants import TYPE_INFO
from pep_sphinx_extensions.pep_zero_generator.constants import TYPE_PROCESS
from pep_sphinx_extensions.pep_zero_generator.constants import TYPE_VALUES
from pep_sphinx_extensions.pep_zero_generator.errors import PEPError

if TYPE_CHECKING:
    from pep_sphinx_extensions.pep_zero_generator.parser import PEP

title_length = 55
author_length = 40
table_separator = "== ====  " + "="*title_length + " " + "="*author_length

# column format is called as a function with a mapping containing field values
column_format = functools.partial(
    "{type}{status}{number: >5}  {title: <{title_length}} {authors}".format,
    title_length=title_length
)

header = f"""\
PEP: 0
Title: Index of Python Enhancement Proposals (PEPs)
Last-Modified: {datetime.date.today()}
Author: python-dev <python-dev@python.org>
Status: Active
Type: Informational
Content-Type: text/x-rst
Created: 13-Jul-2000
"""

intro = """\
This PEP contains the index of all Python Enhancement Proposals,
known as PEPs.  PEP numbers are assigned by the PEP editors, and
once assigned are never changed [1_].  The version control history [2_] of
the PEP texts represent their historical record.
"""

references = """\
.. [1] PEP 1: PEP Purpose and Guidelines
.. [2] View PEP history online: https://github.com/python/peps
"""


class PEPZeroWriter:
    # This is a list of reserved PEP numbers.  Reservations are not to be used for
    # the normal PEP number allocation process - just give out the next available
    # PEP number.  These are for "special" numbers that may be used for semantic,
    # humorous, or other such reasons, e.g. 401, 666, 754.
    #
    # PEP numbers may only be reserved with the approval of a PEP editor.  Fields
    # here are the PEP number being reserved and the claimants for the PEP.
    # Although the output is sorted when PEP 0 is generated, please keep this list
    # sorted as well.
    RESERVED = {
        801: "Warsaw",
    }

    def __init__(self):
        self.output: list[str] = []

    def emit_text(self, content: str) -> None:
        # Appends content argument to the output list
        self.output.append(content)

    def emit_newline(self) -> None:
        self.output.append("")

    def emit_table_separator(self) -> None:
        self.output.append(table_separator)

    def emit_author_table_separator(self, max_name_len: int) -> None:
        author_table_separator = "=" * max_name_len + "  " + "=" * len("email address")
        self.output.append(author_table_separator)

    def emit_pep_row(self, pep_details: dict[str, int | str]) -> None:
        self.emit_text(column_format(**pep_details))

    def emit_column_headers(self) -> None:
        """Output the column headers for the PEP indices."""
        self.emit_table_separator()
        self.emit_pep_row({"status": ".", "type": ".", "number": "PEP", "title": "PEP Title", "authors": "PEP Author(s)"})
        self.emit_table_separator()

    def emit_title(self, text: str, anchor: str, *, symbol: str = "=") -> None:
        self.output.append(f".. _{anchor}:\n")
        self.output.append(text)
        self.output.append(symbol * len(text))
        self.emit_newline()

    def emit_subtitle(self, text: str, anchor: str) -> None:
        self.emit_title(text, anchor, symbol="-")

    def emit_pep_category(self, category: str, anchor: str, peps: list[PEP]) -> None:
        self.emit_subtitle(category, anchor)
        self.emit_column_headers()
        for pep in peps:
            self.output.append(column_format(**pep.details(title_length=title_length)))
        self.emit_table_separator()
        self.emit_newline()

    def write_pep0(self, peps: list[PEP]):

        # PEP metadata
        self.emit_text(header)
        self.emit_newline()

        # Introduction
        self.emit_title("Introduction", "intro")
        self.emit_text(intro)
        self.emit_newline()

        # PEPs by category
        self.emit_title("Index by Category", "by-category")
        meta, info, provisional, accepted, open_, finished, historical, deferred, dead = _classify_peps(peps)
        pep_categories = [
            ("Meta-PEPs (PEPs about PEPs or Processes)", "by-category-meta", meta),
            ("Other Informational PEPs", "by-category-other-info", info),
            ("Provisional PEPs (provisionally accepted; interface may still change)", "by-category-provisional", provisional),
            ("Accepted PEPs (accepted; may not be implemented yet)", "by-category-accepted", accepted),
            ("Open PEPs (under consideration)", "by-category-open", open_),
            ("Finished PEPs (done, with a stable interface)", "by-category-finished", finished),
            ("Historical Meta-PEPs and Informational PEPs", "by-category-historical", historical),
            ("Deferred PEPs (postponed pending further research or updates)", "by-category-deferred", deferred),
            ("Abandoned, Withdrawn, and Rejected PEPs", "by-category-abandoned", dead),
        ]
        for (category, anchor, peps_in_category) in pep_categories:
            self.emit_pep_category(category, anchor, peps_in_category)

        self.emit_newline()

        # PEPs by number
        self.emit_title("Numerical Index", "by-pep-number")
        self.emit_column_headers()
        prev_pep = 0
        for pep in peps:
            if pep.number - prev_pep > 1:
                self.emit_newline()
            self.emit_pep_row(pep.details(title_length=title_length))
            prev_pep = pep.number

        self.emit_table_separator()
        self.emit_newline()

        # Reserved PEP numbers
        self.emit_title("Reserved PEP Numbers", "reserved")
        self.emit_column_headers()
        for number, claimants in sorted(self.RESERVED.items()):
            self.emit_pep_row({"type": ".", "status": ".", "number": number, "title": "RESERVED", "authors": claimants})

        self.emit_table_separator()
        self.emit_newline()

        # PEP types key
        self.emit_title("PEP Types Key", "type-key")
        for type_ in sorted(TYPE_VALUES):
            self.emit_text(f"    {type_[0]} - {type_} PEP")
            self.emit_newline()

        self.emit_newline()

        # PEP status key
        self.emit_title("PEP Status Key", "status-key")
        for status in sorted(STATUS_VALUES):
            # Draft PEPs have no status displayed, Active shares a key with Accepted
            if status in HIDE_STATUS:
                continue
            if status == STATUS_ACCEPTED:
                msg = "    A - Accepted (Standards Track only) or Active proposal"
            else:
                msg = f"    {status[0]} - {status} proposal"
            self.emit_text(msg)
            self.emit_newline()

        self.emit_newline()

        # PEP owners
        authors_dict = _verify_email_addresses(peps)
        max_name_len = max(len(author_name) for author_name in authors_dict)
        self.emit_title("Authors/Owners", "authors")
        self.emit_author_table_separator(max_name_len)
        self.emit_text(f"{'Name':{max_name_len}}  Email Address")
        self.emit_author_table_separator(max_name_len)
        for author_name in _sort_authors(authors_dict):
            # Use the email from authors_dict instead of the one from "author" as
            # the author instance may have an empty email.
            self.emit_text(f"{author_name:{max_name_len}}  {authors_dict[author_name]}")
        self.emit_author_table_separator(max_name_len)
        self.emit_newline()
        self.emit_newline()

        # References for introduction footnotes
        self.emit_title("References", "references")
        self.emit_text(references)

        pep0_string = "\n".join([str(s) for s in self.output])
        return pep0_string


def _classify_peps(peps: list[PEP]) -> tuple[list[PEP], ...]:
    """Sort PEPs into meta, informational, accepted, open, finished,
    and essentially dead."""
    remaining = set(peps)

    # The order of the comprehensions below is important. Key status values
    # take precedence over type value, and vice-versa.
    open_ = sorted(pep for pep in remaining if pep.status == STATUS_DRAFT)
    remaining -= {pep for pep in open_}

    deferred = sorted(pep for pep in remaining if pep.status == STATUS_DEFERRED)
    remaining -= {pep for pep in deferred}

    meta = sorted(pep for pep in remaining if pep.pep_type == TYPE_PROCESS and pep.status == STATUS_ACTIVE)
    remaining -= {pep for pep in meta}

    dead = [pep for pep in remaining if pep.pep_type == TYPE_PROCESS and pep.status in {STATUS_WITHDRAWN, STATUS_REJECTED}]
    remaining -= {pep for pep in dead}

    historical = [pep for pep in remaining if pep.pep_type == TYPE_PROCESS]
    remaining -= {pep for pep in historical}

    dead = sorted(dead + [pep for pep in remaining if pep.status in DEAD_STATUSES])
    remaining -= {pep for pep in dead}

    # Hack until the conflict between the use of `Final`
    # for both API definition PEPs and other (actually
    # obsolete) PEPs is addressed
    info = sorted(
        pep for pep in remaining
        if pep.pep_type == TYPE_INFO and (pep.status == STATUS_ACTIVE or "Release Schedule" not in pep.title)
    )
    remaining -= {pep for pep in info}

    historical = sorted(historical + [pep for pep in remaining if pep.pep_type == TYPE_INFO])
    remaining -= {pep for pep in historical}

    provisional = sorted(pep for pep in remaining if pep.status == STATUS_PROVISIONAL)
    remaining -= {pep for pep in provisional}

    accepted = sorted(pep for pep in remaining if pep.status in {STATUS_ACCEPTED, STATUS_ACTIVE})
    remaining -= {pep for pep in accepted}

    finished = sorted(pep for pep in remaining if pep.status == STATUS_FINAL)
    remaining -= {pep for pep in finished}

    for pep in remaining:
        raise PEPError(f"unsorted ({pep.pep_type}/{pep.status})", pep.filename, pep.number)

    return meta, info, provisional, accepted, open_, finished, historical, deferred, dead


def _verify_email_addresses(peps: list[PEP]) -> dict[str, str]:
    authors_dict: dict[str, set[str]] = {}
    for pep in peps:
        for author in pep.authors:
            # If this is the first time we have come across an author, add them.
            if author.last_first not in authors_dict:
                authors_dict[author.last_first] = set()

            # If the new email is an empty string, move on.
            if not author.email:
                continue
            # If the email has not been seen, add it to the list.
            authors_dict[author.last_first].add(author.email)

    valid_authors_dict: dict[str, str] = {}
    too_many_emails: list[tuple[str, set[str]]] = []
    for last_first, emails in authors_dict.items():
        if len(emails) > 1:
            too_many_emails.append((last_first, emails))
        else:
            valid_authors_dict[last_first] = next(iter(emails), "")
    if too_many_emails:
        err_output = []
        for author, emails in too_many_emails:
            err_output.append(" " * 4 + f"{author}: {emails}")
        raise ValueError(
            "some authors have more than one email address listed:\n"
            + "\n".join(err_output)
        )

    return valid_authors_dict


def _sort_authors(authors_dict: dict[str, str]) -> list[str]:
    return sorted(authors_dict, key=_author_sort_by)


def _author_sort_by(author_name: str) -> str:
    """Skip lower-cased words in surname when sorting."""
    surname, *_ = author_name.split(",")
    surname_parts = surname.split()
    for i, part in enumerate(surname_parts):
        if part[0].isupper():
            base = " ".join(surname_parts[i:]).lower()
            return unicodedata.normalize("NFKD", base)
    # If no capitals, use the whole string
    return unicodedata.normalize("NFKD", surname.lower())
