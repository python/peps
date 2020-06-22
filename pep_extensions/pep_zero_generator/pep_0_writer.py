"""Code to handle the output of PEP 0."""
import datetime
import unicodedata
from functools import partial
from operator import attrgetter
from typing import List


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
    RESERVED = [
        (801, "Warsaw"),
    ]

    def __init__(self):
        self._output: List[str] = []

    def output(self, content):
        # Appends content argument to the _output list
        self._output.append(content)

    def emit_newline(self):
        self.output('')

    def emit_table_separator(self):
        self.output(pep_0_constants.table_separator)

    def emit_author_table_separator(self, max_name_len):
        author_table_separator = "=" * max_name_len + "  " + "=" * len("email address")
        self.output(author_table_separator)

    def emit_column_headers(self):
        """Output the column headers for the PEP indices."""
        column_headers = {
            "status": ".",
            "type": ".",
            "number": "PEP",
            "title": "PEP Title",
            "authors": "PEP Author(s)",
        }
        self.emit_table_separator()
        self.output(pep_0_constants.column_format(**column_headers))
        self.emit_table_separator()

    @staticmethod
    def sort_peps(peps):
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
            if pep.status == "Draft":
                open_.append(pep)
            elif pep.status == "Deferred":
                deferred.append(pep)
            elif pep.type_ == "Process":
                if pep.status == "Active":
                    meta.append(pep)
                elif pep.status in ("Withdrawn", "Rejected"):
                    dead.append(pep)
                else:
                    historical.append(pep)
            elif pep.status in ("Rejected", "Withdrawn", "Incomplete", "Superseded"):
                dead.append(pep)
            elif pep.type_ == "Informational":
                # Hack until the conflict between the use of "Final"
                # for both API definition PEPs and other (actually
                # obsolete) PEPs is addressed
                if pep.status == "Active" or "Release Schedule" not in pep.title:
                    info.append(pep)
                else:
                    historical.append(pep)
            elif pep.status == "Provisional":
                provisional.append(pep)
            elif pep.status in ("Accepted", "Active"):
                accepted.append(pep)
            elif pep.status == "Final":
                finished.append(pep)
            else:
                raise pep_0_parser.PEPError(f"unsorted ({pep.type_}/{pep.status})", pep.filename, pep.number)
        return meta, info, provisional, accepted, open_, finished, historical, deferred, dead

    @staticmethod
    def verify_email_addresses(peps):
        authors_dict = {}
        for pep in peps:
            for author in pep.authors:
                # If this is the first time we have come across an author, add them.
                if author not in authors_dict:
                    authors_dict[author] = [author.email]
                else:
                    found_emails = authors_dict[author]
                    # If no email exists for the author, use the new value.
                    if not found_emails[0]:
                        authors_dict[author] = [author.email]
                    # If the new email is an empty string, move on.
                    elif not author.email:
                        continue
                    # If the email has not been seen, add it to the list.
                    elif author.email not in found_emails:
                        authors_dict[author].append(author.email)

        valid_authors_dict = {}
        too_many_emails = []
        for author, emails in authors_dict.items():
            if len(emails) > 1:
                too_many_emails.append((author.first_last, emails))
            else:
                valid_authors_dict[author] = emails[0]
        if too_many_emails:
            err_output = []
            for author, emails in too_many_emails:
                err_output.append(" " * 4 + f"{author}: {emails}")
            raise ValueError(
                "some authors have more than one email address listed:\n"
                + "\n".join(err_output)
            )

        return valid_authors_dict

    @staticmethod
    def sort_authors(authors_dict):
        authors_list = list(authors_dict.keys())
        authors_list.sort(key=attrgetter("sort_by"))
        return authors_list

    @staticmethod
    def normalized_last_first(name):
        return len(unicodedata.normalize("NFC", name.last_first))

    def emit_title(self, text, anchor, *, symbol="="):
        self.output(".. _{anchor}:\n".format(anchor=anchor))
        self.output(text)
        self.output(symbol * len(text))
        self.emit_newline()

    def emit_subtitle(self, text, anchor):
        self.emit_title(text, anchor, symbol="-")

    def emit_pep_category(self, category, anchor, peps):
        self.emit_subtitle(category, anchor)
        self.emit_column_headers()
        for pep in peps:
            self.output(pep)
        self.emit_table_separator()
        self.emit_newline()

    def write_pep0(self, peps: list):

        # PEP metadata
        today = datetime.date.today().strftime("%Y-%m-%d")
        self.output(pep_0_constants.header.format(last_modified=today))
        self.emit_newline()

        # Introduction
        self.emit_title("Introduction", "intro")
        self.output(pep_0_constants.intro)
        self.emit_newline()

        # PEPs by category
        self.emit_title("Index by Category", "by-category")
        (meta, info, provisional, accepted, open_,
         finished, historical, deferred, dead) = self.sort_peps(peps)
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
        for pep_category in pep_categories:
            category = pep_category[0]
            anchor = pep_category[1]
            peps_in_category = pep_category[2]
            self.emit_pep_category(category, anchor, peps_in_category)

        self.emit_newline()

        # PEPs by number
        self.emit_title("Numerical Index", "by-pep-number")
        self.emit_column_headers()
        prev_pep = 0
        for pep in peps:
            if pep.number - prev_pep > 1:
                self.emit_newline()
            self.output(str(pep))
            prev_pep = pep.number

        self.emit_table_separator()
        self.emit_newline()

        # Reserved PEP numbers
        self.emit_title("Reserved PEP Numbers", "reserved")
        self.emit_column_headers()
        for number, claimants in sorted(self.RESERVED):
            self.output(pep_0_constants.column_format(**{
                "type": ".",
                "status": ".",
                "number": number,
                "title": "RESERVED",
                "authors": claimants,
            }))

        self.emit_table_separator()
        self.emit_newline()

        # PEP types key
        self.emit_title("PEP Types Key", "type-key")
        for type_ in sorted(pep_0_parser.PEP.type_values):
            self.output(f"    {type_[0]} - {type_} PEP")
            self.emit_newline()

        self.emit_newline()

        # PEP status key
        self.emit_title("PEP Status Key", "status-key")
        for status in sorted(pep_0_parser.PEP.status_values):
            # Draft PEPs have no status displayed, Active shares a key with Accepted
            if status in ("Active", "Draft"):
                continue
            if status == "Accepted":
                msg = "    A - Accepted (Standards Track only) or Active proposal"
            else:
                msg = "    {status[0]} - {status} proposal".format(status=status)
            self.output(msg)
            self.emit_newline()

        self.emit_newline()

        # PEP owners
        self.emit_title("Authors/Owners", "authors")
        authors_dict = self.verify_email_addresses(peps)
        max_name = max(authors_dict.keys(), key=self.normalized_last_first)
        max_name_len = len(max_name.last_first)
        self.emit_author_table_separator(max_name_len)
        _author_header_fmt = f"{'Name':{max_name_len}}  Email Address"
        self.output(_author_header_fmt)
        self.emit_author_table_separator(max_name_len)
        sorted_authors = self.sort_authors(authors_dict)
        _author_fmt = "{author.last_first:{max_name_len}}  {author_email}"
        for author in sorted_authors:
            # Use the email from authors_dict instead of the one from 'author' as
            # the author instance may have an empty email.
            _entry = _author_fmt.format(
                author=author,
                author_email=authors_dict[author],
                max_name_len=max_name_len,
            )
            self.output(_entry)
        self.emit_author_table_separator(max_name_len)
        self.emit_newline()
        self.emit_newline()

        # References for introduction footnotes
        self.emit_title("References", "references")
        self.output(pep_0_constants.references)
        self.output(pep_0_constants.footer)

        pep0_string = '\n'.join([str(s) for s in self._output])
        return pep0_string
