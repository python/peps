"""Code to handle the output of PEP 0."""
from __future__ import absolute_import
from __future__ import print_function
import datetime
import sys
import unicodedata

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

def write_column_headers(output):
    """Output the column headers for the PEP indices."""
    column_headers = {'status': u'', 'type': u'', 'number': u'num',
                        'title': u'title', 'authors': u'owner'}
    print(constants.column_format % column_headers, file=output)
    underline_headers = {}
    for key, value in column_headers.items():
        underline_headers[key] = constants.text_type(len(value) * '-')
    print(constants.column_format % underline_headers, file=output)


def sort_peps(peps):
    """Sort PEPs into meta, informational, accepted, open, finished,
    and essentially dead."""
    meta = []
    info = []
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
        elif pep.status in ('Accepted', 'Active'):
            accepted.append(pep)
        elif pep.status == 'Final':
            finished.append(pep)
        else:
            raise PEPError("unsorted (%s/%s)" %
                           (pep.type_, pep.status),
                           pep.filename, pep.number)
    return meta, info, accepted, open_, finished, historical, deferred, dead


def verify_email_addresses(peps):
    authors_dict = {}
    for pep in peps:
        for author in pep.authors:
            # If this is the first time we have come across an author, add him.
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
    authors_list = list(authors_dict.keys())
    authors_list.sort(key=attrgetter('sort_by'))
    return authors_list

def normalized_last_first(name):
    return len(unicodedata.normalize('NFC', name.last_first))


def write_pep0(peps, output=sys.stdout):
    today = datetime.date.today().strftime("%Y-%m-%d")
    print(constants.header % today, file=output)
    print(file=output)
    print(u"Introduction", file=output)
    print(constants.intro, file=output)
    print(file=output)
    print(u"Index by Category", file=output)
    print(file=output)
    write_column_headers(output)
    (meta, info, accepted, open_, finished,
           historical, deferred, dead) = sort_peps(peps)
    print(file=output)
    print(u" Meta-PEPs (PEPs about PEPs or Processes)", file=output)
    print(file=output)
    for pep in meta:
        print(constants.text_type(pep), file=output)
    print(file=output)
    print(u" Other Informational PEPs", file=output)
    print(file=output)
    for pep in info:
        print(constants.text_type(pep), file=output)
    print(file=output)
    print(u" Accepted PEPs (accepted; may not be implemented yet)", file=output)
    print(file=output)
    for pep in accepted:
        print(constants.text_type(pep), file=output)
    print(file=output)
    print(u" Open PEPs (under consideration)", file=output)
    print(file=output)
    for pep in open_:
        print(constants.text_type(pep), file=output)
    print(file=output)
    print(u" Finished PEPs (done, implemented in code repository)", file=output)
    print(file=output)
    for pep in finished:
        print(constants.text_type(pep), file=output)
    print(file=output)
    print(u" Historical Meta-PEPs and Informational PEPs", file=output)
    print(file=output)
    for pep in historical:
        print(constants.text_type(pep), file=output)
    print(file=output)
    print(u" Deferred PEPs", file=output)
    print(file=output)
    for pep in deferred:
        print(constants.text_type(pep), file=output)
    print(file=output)
    print(u" Abandoned, Withdrawn, and Rejected PEPs", file=output)
    print(file=output)
    for pep in dead:
        print(constants.text_type(pep), file=output)
    print(file=output)
    print(file=output)
    print(u"Numerical Index", file=output)
    print(file=output)
    write_column_headers(output)
    prev_pep = 0
    for pep in peps:
        if pep.number - prev_pep > 1:
            print(file=output)
        print(constants.text_type(pep), file=output)
        prev_pep = pep.number
    print(file=output)
    print(file=output)
    print(u'Reserved PEP Numbers', file=output)
    print(file=output)
    write_column_headers(output)
    for number, claimants in sorted(RESERVED):
        print(constants.column_format % {
            'type': '',
            'status': '',
            'number': number,
            'title': 'RESERVED',
            'authors': claimants,
            }, file=output)
    print(file=output)
    print(file=output)
    print(u"Key", file=output)
    print(file=output)
    for type_ in PEP.type_values:
        print(u"    %s - %s PEP" % (type_[0], type_), file=output)
    print(file=output)
    for status in PEP.status_values:
        print(u"    %s - %s proposal" % (status[0], status), file=output)

    print(file=output)
    print(file=output)
    print(u"Owners", file=output)
    print(file=output)
    authors_dict = verify_email_addresses(peps)
    max_name = max(authors_dict.keys(), key=normalized_last_first)
    max_name_len = len(max_name.last_first)
    print(u"    %s  %s" % ('name'.ljust(max_name_len), 'email address'), file=output)
    print(u"    %s  %s" % ((len('name')*'-').ljust(max_name_len),
                                    len('email address')*'-'), file=output)
    sorted_authors = sort_authors(authors_dict)
    for author in sorted_authors:
        # Use the email from authors_dict instead of the one from 'author' as
        # the author instance may have an empty email.
        print((u"    %s  %s" %
                (author.last_first.ljust(max_name_len), authors_dict[author])), file=output)
    print(file=output)
    print(file=output)
    print(u"References", file=output)
    print(file=output)
    print(constants.references, file=output)
    print(constants.footer, file=output)
