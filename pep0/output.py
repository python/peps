"""Code to handle the output of PEP 0."""
from __future__ import absolute_import
from __future__ import print_function
import datetime
import sys
import unicodedata

from itertools import groupby
from operator import attrgetter

from . import constants
from .pep import PEP, PEPError

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
    (801, 'Warsaw'),
    ]


indent = u' '

def emit_column_headers(output):
    """Output the column headers for the PEP indices."""
    column_headers = {'status': '.', 'type': '.', 'number': 'PEP',
                        'title': 'PEP Title', 'authors': 'PEP Author(s)'}
    print(constants.table_separator, file=output)
    print(constants.column_format % column_headers, file=output)
    print(constants.table_separator, file=output)


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
        if pep.status == 'Draft':
            open_.append(pep)
        elif pep.status == 'Deferred':
            deferred.append(pep)
        elif pep.type_ == 'Process':
            if pep.status == "Active":
                meta.append(pep)
            elif pep.status in ("Withdrawn", "Rejected"):
                dead.append(pep)
            else:
                historical.append(pep)
        elif pep.status in ('Rejected', 'Withdrawn',
                            'Incomplete', 'Superseded'):
            dead.append(pep)
        elif pep.type_ == 'Informational':
            # Hack until the conflict between the use of "Final"
            # for both API definition PEPs and other (actually
            # obsolete) PEPs is addressed
            if (pep.status == "Active" or
                "Release Schedule" not in pep.title):
                info.append(pep)
            else:
                historical.append(pep)
        elif pep.status == 'Provisional':
            provisional.append(pep)
        elif pep.status in ('Accepted', 'Active'):
            accepted.append(pep)
        elif pep.status == 'Final':
            finished.append(pep)
        else:
            raise PEPError("unsorted (%s/%s)" %
                           (pep.type_, pep.status),
                           pep.filename, pep.number)
    return (meta, info, provisional, accepted, open_,
            finished, historical, deferred, dead)


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
            err_output.append("    %s: %r" % (author, emails))
        raise ValueError("some authors have more than one email address "
                         "listed:\n" + '\n'.join(err_output))

    return valid_authors_dict


def sort_authors(authors_dict):
    authors_list = sorted(authors_dict.keys(), key=attrgetter("sort_by"))
    unique_authors = [next(a) for k, a in groupby(authors_list, key=attrgetter("last_first"))]
    return unique_authors

def normalized_last_first(name):
    return len(unicodedata.normalize('NFC', name.last_first))

def emit_title(text, anchor, output, *, symbol="="):
    print(".. _{anchor}:\n".format(anchor=anchor), file=output)
    print(text, file=output)
    print(symbol*len(text), file=output)
    print(file=output)

def emit_subtitle(text, anchor, output):
    emit_title(text, anchor, output, symbol="-")

def emit_pep_category(output, category, anchor, peps):
    emit_subtitle(category, anchor, output)
    emit_column_headers(output)
    for pep in peps:
        print(pep, file=output)
    print(constants.table_separator, file=output)
    print(file=output)

def write_pep0(peps, output=sys.stdout):
    # PEP metadata
    today = datetime.date.today().strftime("%Y-%m-%d")
    print(constants.header % today, file=output)
    print(file=output)
    # Introduction
    emit_title("Introduction", "intro", output)
    print(constants.intro, file=output)
    print(file=output)
    # PEPs by category
    (meta, info, provisional, accepted, open_,
           finished, historical, deferred, dead) = sort_peps(peps)
    emit_title("Index by Category", "by-category", output)
    emit_pep_category(
        category="Meta-PEPs (PEPs about PEPs or Processes)",
        anchor="by-category-meta",
        peps=meta,
        output=output,
    )
    emit_pep_category(
        category="Other Informational PEPs",
        anchor="by-category-other-info",
        peps=info,
        output=output,
    )
    emit_pep_category(
        category="Provisional PEPs (provisionally accepted; interface may still change)",
        anchor="by-category-provisional",
        peps=provisional,
        output=output,
    )
    emit_pep_category(
        category="Accepted PEPs (accepted; may not be implemented yet)",
        anchor="by-category-accepted",
        peps=accepted,
        output=output,
    )
    emit_pep_category(
        category="Open PEPs (under consideration)",
        anchor="by-category-open",
        peps=open_,
        output=output,
    )
    emit_pep_category(
        category="Finished PEPs (done, with a stable interface)",
        anchor="by-category-finished",
        peps=finished,
        output=output,
    )
    emit_pep_category(
        category="Historical Meta-PEPs and Informational PEPs",
        anchor="by-category-historical",
        peps=historical,
        output=output,
    )
    emit_pep_category(
        category="Deferred PEPs (postponed pending further research or updates)",
        anchor="by-category-deferred",
        peps=deferred,
        output=output,
    )
    emit_pep_category(
        category="Abandoned, Withdrawn, and Rejected PEPs",
        anchor="by-category-abandoned",
        peps=dead,
        output=output,
    )
    print(file=output)
    # PEPs by number
    emit_title("Numerical Index", "by-pep-number", output)
    emit_column_headers(output)
    prev_pep = 0
    for pep in peps:
        if pep.number - prev_pep > 1:
            print(file=output)
        print(constants.text_type(pep), file=output)
        prev_pep = pep.number
    print(constants.table_separator, file=output)
    print(file=output)
    # Reserved PEP numbers
    emit_title('Reserved PEP Numbers', "reserved", output)
    emit_column_headers(output)
    for number, claimants in sorted(RESERVED):
        print(constants.column_format % {
            'type': '.',
            'status': '.',
            'number': number,
            'title': 'RESERVED',
            'authors': claimants,
            }, file=output)
    print(constants.table_separator, file=output)
    print(file=output)
    # PEP types key
    emit_title("PEP Types Key", "type-key", output)
    for type_ in sorted(PEP.type_values):
        print(u"    %s - %s PEP" % (type_[0], type_), file=output)
        print(file=output)
    print(file=output)
    # PEP status key
    emit_title("PEP Status Key", "status-key", output)
    for status in sorted(PEP.status_values):
        # Draft PEPs have no status displayed, Active shares a key with Accepted
        if status in ("Active", "Draft"):
            continue
        if status == "Accepted":
            msg = "    A - Accepted (Standards Track only) or Active proposal"
        else:
            msg = "    {status[0]} - {status} proposal".format(status=status)
        print(msg, file=output)
        print(file=output)

    print(file=output)
    # PEP owners
    emit_title("Authors/Owners", "authors", output)
    authors_dict = verify_email_addresses(peps)
    max_name = max(authors_dict.keys(), key=normalized_last_first)
    max_name_len = len(max_name.last_first)
    author_table_separator = "="*max_name_len + "  " + "="*len("email address")
    print(author_table_separator, file=output)
    _author_header_fmt = "{name:{max_name_len}}  Email Address"
    print(_author_header_fmt.format(name="Name", max_name_len=max_name_len), file=output)
    print(author_table_separator, file=output)
    sorted_authors = sort_authors(authors_dict)
    _author_fmt = "{author.last_first:{max_name_len}}  {author_email}"
    for author in sorted_authors:
        # Use the email from authors_dict instead of the one from 'author' as
        # the author instance may have an empty email.
        _entry = _author_fmt.format(
            author=author,
            author_email=authors_dict[author],
            max_name_len=max_name_len,
        )
        print(_entry, file=output)
    print(author_table_separator, file=output)
    print(file=output)
    print(file=output)
    # References for introduction footnotes
    emit_title("References", "references", output)
    print(constants.references, file=output)
    print(constants.footer, file=output)
