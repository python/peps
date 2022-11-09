"""Code to handle the output of PEP 0."""

from __future__ import annotations

import datetime
from typing import TYPE_CHECKING
import unicodedata

from pep_sphinx_extensions.pep_processor.transforms.pep_headers import (
    ABBREVIATED_STATUSES,
    ABBREVIATED_TYPES,
)
from pep_sphinx_extensions.pep_zero_generator.constants import DEAD_STATUSES
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

HEADER = f"""\
PEP: 0
Title: Index of Python Enhancement Proposals (PEPs)
Last-Modified: {datetime.date.today()}
Author: python-dev <python-dev@python.org>
Status: Active
Type: Informational
Content-Type: text/x-rst
Created: 13-Jul-2000
"""

INTRO = """\
This PEP contains the index of all Python Enhancement Proposals,
known as PEPs.  PEP numbers are :pep:`assigned <1#pep-editors>`
by the PEP editors, and once assigned are never changed.  The
`version control history <https://github.com/python/peps>`_ of
the PEP texts represent their historical record.  The PEPs are
:doc:`indexed by topic <topic/index>` for specialist subjects.
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

    def emit_author_table_separator(self, max_name_len: int) -> None:
        author_table_separator = "=" * max_name_len + "  " + "=" * len("email address")
        self.output.append(author_table_separator)

    def emit_pep_row(
        self, *, shorthand: str, number: int, title: str, authors: str
    ) -> None:
        self.emit_text(f"   * - {shorthand}")
        self.emit_text(f"     - :pep:`{number} <{number}>`")
        self.emit_text(f"     - :pep:`{title.replace('`', '')} <{number}>`")
        self.emit_text(f"     - {authors}")

    def emit_column_headers(self) -> None:
        """Output the column headers for the PEP indices."""
        self.emit_text(".. list-table::")
        self.emit_text("   :header-rows: 1")
        self.emit_text("   :widths: auto")
        self.emit_text("   :class: pep-zero-table")
        self.emit_newline()
        self.emit_text("   * - ")
        self.emit_text("     - PEP")
        self.emit_text("     - Title")
        self.emit_text("     - Authors")

    def emit_title(self, text: str, *, symbol: str = "=") -> None:
        self.output.append(text)
        self.output.append(symbol * len(text))
        self.emit_newline()

    def emit_subtitle(self, text: str) -> None:
        self.emit_title(text, symbol="-")

    def emit_pep_category(self, category: str, peps: list[PEP]) -> None:
        self.emit_subtitle(category)
        self.emit_column_headers()
        for pep in peps:
            self.emit_pep_row(**pep.details)
        # list-table must have at least one body row
        if len(peps) == 0:
            self.emit_text("   * -")
            self.emit_text("     -")
            self.emit_text("     -")
            self.emit_text("     -")
        self.emit_newline()

    def write_pep0(self, peps: list[PEP], header: str = HEADER, intro: str = INTRO, is_pep0: bool = True):
        if len(peps) == 0:
            return ""

        # PEP metadata
        self.emit_text(header)
        self.emit_newline()

        # Introduction
        self.emit_title("Introduction")
        self.emit_text(intro)
        self.emit_newline()

        # PEPs by category
        self.emit_title("Index by Category")
        meta, info, provisional, accepted, open_, finished, historical, deferred, dead = _classify_peps(peps)
        pep_categories = [
            ("Meta-PEPs (PEPs about PEPs or Processes)", meta),
            ("Other Informational PEPs", info),
            ("Provisional PEPs (provisionally accepted; interface may still change)", provisional),
            ("Accepted PEPs (accepted; may not be implemented yet)", accepted),
            ("Open PEPs (under consideration)", open_),
            ("Finished PEPs (done, with a stable interface)", finished),
            ("Historical Meta-PEPs and Informational PEPs", historical),
            ("Deferred PEPs (postponed pending further research or updates)", deferred),
            ("Abandoned, Withdrawn, and Rejected PEPs", dead),
        ]
        for (category, peps_in_category) in pep_categories:
            # For sub-indices, only emit categories with entries.
            # For PEP 0, emit every category, but only with a table when it has entries.
            if len(peps_in_category) > 0:
                self.emit_pep_category(category, peps_in_category)
            elif is_pep0:
                # emit the category with no table
                self.emit_subtitle(category)
                self.emit_text("None.")
                self.emit_newline()

        self.emit_newline()

        # PEPs by number
        self.emit_title("Numerical Index")
        self.emit_column_headers()
        for pep in peps:
            self.emit_pep_row(**pep.details)

        self.emit_newline()

        # Reserved PEP numbers
        if is_pep0:
            self.emit_title("Reserved PEP Numbers")
            self.emit_column_headers()
            for number, claimants in sorted(self.RESERVED.items()):
                self.emit_pep_row(
                    shorthand="", number=number, title="RESERVED", authors=claimants
                )

            self.emit_newline()

        # PEP types key
        self.emit_title("PEP Types Key")
        for type_ in sorted(TYPE_VALUES):
            self.emit_text(
                f"* **{type_[0]}** --- *{type_}*: {ABBREVIATED_TYPES[type_]}"
            )
            self.emit_newline()

        self.emit_text(":pep:`More info in PEP 1 <1#pep-types>`.")
        self.emit_newline()

        # PEP status key
        self.emit_title("PEP Status Key")
        for status in sorted(STATUS_VALUES):
            # Draft PEPs have no status displayed, Active shares a key with Accepted
            status_code = "<No letter>" if status == STATUS_DRAFT else status[0]
            self.emit_text(
                f"* **{status_code}** --- *{status}*: {ABBREVIATED_STATUSES[status]}"
            )
            self.emit_newline()

        self.emit_text(":pep:`More info in PEP 1 <1#pep-review-resolution>`.")
        self.emit_newline()

        if is_pep0:
            # PEP owners
            authors_dict = _verify_email_addresses(peps)
            max_name_len = max(len(author_name) for author_name in authors_dict)
            self.emit_title("Authors/Owners")
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

        pep0_string = "\n".join([str(s) for s in self.output])
        return pep0_string


def _classify_peps(peps: list[PEP]) -> tuple[list[PEP], ...]:
    """Sort PEPs into meta, informational, accepted, open, finished,
    and essentially dead."""
    meta = []
    info = []
    provisional = []
    accepted = []
    open_ = []
    finished = []
    historical = []
    deferred = []
    dead = []
    for pep in peps:
        # Order of 'if' statement important.  Key Status values take precedence
        # over Type value, and vice-versa.
        if pep.status == STATUS_DRAFT:
            open_.append(pep)
        elif pep.status == STATUS_DEFERRED:
            deferred.append(pep)
        elif pep.pep_type == TYPE_PROCESS:
            if pep.status in {STATUS_ACCEPTED, STATUS_ACTIVE}:
                meta.append(pep)
            elif pep.status in {STATUS_WITHDRAWN, STATUS_REJECTED}:
                dead.append(pep)
            else:
                historical.append(pep)
        elif pep.status in DEAD_STATUSES:
            dead.append(pep)
        elif pep.pep_type == TYPE_INFO:
            # Hack until the conflict between the use of "Final"
            # for both API definition PEPs and other (actually
            # obsolete) PEPs is addressed
            if pep.status == STATUS_ACTIVE or "Release Schedule" not in pep.title:
                info.append(pep)
            else:
                historical.append(pep)
        elif pep.status == STATUS_PROVISIONAL:
            provisional.append(pep)
        elif pep.status in {STATUS_ACCEPTED, STATUS_ACTIVE}:
            accepted.append(pep)
        elif pep.status == STATUS_FINAL:
            finished.append(pep)
        else:
            raise PEPError(f"Unsorted ({pep.pep_type}/{pep.status})", pep.filename, pep.number)
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
