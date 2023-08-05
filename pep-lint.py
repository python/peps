#!/usr/bin/env python3

# This file is placed in the public domain or under the
# CC0-1.0-Universal license, whichever is more permissive.

import datetime
import re
import sys
from pathlib import Path

# get the directory with the PEP sources
PEP_ROOT = Path(__file__).resolve().parent

# See PEP 12 for the order
# Note we retain "BDFL-Delegate"
ALL_HEADERS = (
    "PEP",
    "Title",
    "Version",
    "Last-Modified",
    "Author",
    "Sponsor",
    "BDFL-Delegate", "PEP-Delegate",
    "Discussions-To",
    "Status",
    "Type",
    "Topic",
    "Content-Type",
    "Requires",
    "Created",
    "Python-Version",
    "Post-History",
    "Replaces",
    "Superseded-By",
    "Resolution",
)
REQUIRED_HEADERS = frozenset({"PEP", "Title", "Author", "Status", "Type", "Created"})

# See PEP 1 for the full list
ALL_STATUSES = frozenset({
    "Accepted",
    "Active",
    "April Fool!",
    "Deferred",
    "Draft",
    "Final",
    "Provisional",
    "Rejected",
    "Superseded",
    "Withdrawn",
})

# PEPs that are allowed to link directly to PEPs
SKIP_DIRECT_PEP_LINK_CHECK = frozenset({"0009", "0287", "0676", "0684", "8001"})

HEADER_PATTERN = re.compile(r"^([a-z\-]+):(?: |$)", re.IGNORECASE)
EMAIL_PATTERN = re.compile(
    r"""
    ([^\W\d_]|[. ])+               # Name; any sequence of unicode letters, full stops, or spaces
    ( <                            # Start of optional email part: ' <'
    [a-z0-9!#$%&'*+\-/=?^_{|}~.]+  # Local part; ASCII letters, digits, and legal special characters
    (@| at )                       # Local and domain parts separator
    (\w+\.)+[a-z0-9-]+             # Domain, with at least two segments
    >)?                            # End of optional email part: '>'
    """,
    re.IGNORECASE | re.VERBOSE
)
DISCOURSE_THREAD_PATTERN = re.compile(r'([\w\-]+/)?\d+')
DISCOURSE_POST_PATTERN = re.compile(r'([\w\-]+/)?\d+(/\d+)?')
MAILMAN_2_PATTERN = re.compile(r'[\w\-]+/\d{4}-[A-Za-z]+/[A-Za-z0-9]+\.html')
MAILMAN_3_THREAD_PATTERN = re.compile(r'[\w\-]+@python\.org/thread/[A-Za-z0-9]+/?(#[A-Za-z0-9]+)?')
MAILMAN_3_MESSAGE_PATTERN = re.compile(r'[\w\-]+@python\.org/message/[A-Za-z0-9]+/?(#[A-Za-z0-9]+)?')


def check():
    """The main entry-point."""
    failed = 0
    for iterator in (PEP_ROOT.glob("pep-????.txt"), PEP_ROOT.glob("pep-????.rst")):
        for file in iterator:
            content = file.read_text(encoding='utf-8')
            lines = content.splitlines()
            failed += _output_error(file, lines, check_pep(file, lines))
    if failed > 0:
        print(f"pep-lint failed: {failed} errors", file=sys.stderr)
        return 1
    return 0


def check_pep(filename, lines):
    yield from check_headers(lines)
    for line_num, line in enumerate(lines, start=1):
        if filename.stem.removeprefix("pep-") in SKIP_DIRECT_PEP_LINK_CHECK:
            continue
        yield from check_direct_links(line_num, line.lstrip())


def check_headers(lines):
    yield from _validate_pep_number(next(iter(lines), ""))

    found_headers = {}
    line_num = 0
    for line_num, line in enumerate(lines, start=1):
        if line.strip() == "":
            headers_end_line_num = line_num
            break
        if match := HEADER_PATTERN.match(line):
            header = match[1]
            if header in ALL_HEADERS:
                if header not in found_headers:
                    found_headers[match[1]] = line_num
                else:
                    yield line_num, f"Must not have duplicate header: {header} "
            else:
                yield line_num, f"Must not have invalid header: {header}"
    else:
        headers_end_line_num = line_num

    yield from _validate_required_headers(found_headers)

    shifted_line_nums = list(found_headers.values())[1:]
    for i, (header, line_num) in enumerate(found_headers.items()):
        start = line_num - 1
        end = headers_end_line_num - 1
        if i < len(found_headers) - 1:
            end = shifted_line_nums[i] - 1
        remainder = "\n".join(lines[start:end]).removeprefix(f"{header}:")
        if remainder != "":
            if remainder[0] not in {" ", "\n"}:
                yield line_num, f"Headers must have a space after the colon: {header}"
            remainder = remainder.lstrip()

        if header == "Title":
            yield from _validate_title(line_num, remainder)
        elif header == "Author":
            yield from _validate_author(line_num, remainder)
        elif header == "Sponsor":
            yield from _validate_sponsor(line_num, remainder)
        elif header in {"BDFL-Delegate", "PEP-Delegate"}:
            yield from _validate_delegate(line_num, remainder)
        elif header == "Discussions-To":
            yield from _validate_discussions_to(line_num, remainder)
        elif header == "Status":
            yield from _validate_status(line_num, remainder)
        elif header == "Type":
            yield from _validate_type(line_num, remainder)
        elif header == "Topic":
            yield from _validate_topic(line_num, remainder)
        elif header == "Content-Type":
            yield from _validate_content_type(line_num, remainder)
        elif header in {"Requires", "Replaces", "Superseded-By"}:
            yield from _validate_pep_references(line_num, remainder)
        elif header == "Created":
            yield from _validate_created(line_num, remainder)
        elif header == "Python-Version":
            yield from _validate_python_version(line_num, remainder)
        elif header == "Post-History":
            yield from _validate_post_history(line_num, remainder)
        elif header == "Resolution":
            yield from _validate_resolution(line_num, remainder)


def check_direct_links(line_num, line):
    """Check that PEPs and RFCs aren't linked directly"""

    line = line.lstrip().lower()
    if "dev/peps/pep-" in line or "peps.python.org/pep-" in line:
        yield line_num, "Use the :pep:`NNN` role to refer to PEPs"
    if "rfc-editor.org/rfc/" in line or "ietf.org/doc/html/rfc" in line:
        yield line_num, "Use the :rfc:`NNN` role to refer to RFCs"


def _output_error(filename, lines, errors):
    err_count = 0
    for line_num, msg in errors:
        print(f"{filename}:{line_num}: |", file=sys.stderr)
        print(f"{filename}:{line_num}: {msg}", file=sys.stderr)
        print(f"{filename}:{line_num}: from:   {lines[line_num - 1]!r}", file=sys.stderr)
        print(f"{filename}:{line_num}: |", file=sys.stderr)
        err_count += 1
    return err_count


###########################
#  PEP Header Validators  #
###########################


def _validate_required_headers(found_headers):
    """PEPs must have all required headers, in the PEP 12 order"""

    if missing := REQUIRED_HEADERS.difference(found_headers):
        for missing_header in sorted(missing, key=ALL_HEADERS.index):
            yield 0, f"Must have required header: {missing_header}"

    ordered_headers = sorted(found_headers, key=ALL_HEADERS.index)
    if list(found_headers) != ordered_headers:
        order_str = ", ".join(ordered_headers)
        yield 0, "Headers must be in PEP 12 order. Correct order: " + order_str


def _validate_pep_number(line):
    """'PEP' header must be a number 1-9999"""

    if not line.startswith("PEP: "):
        yield 1, "PEP must begin with the 'PEP:' header"
        return

    pep_number = line.removeprefix("PEP: ").strip()
    yield from _pep_num(1, pep_number, "'PEP:' header")


def _validate_title(line_num, line):
    """'Title' must be 1-79 characters"""

    if len(line.strip()) == 0:
        yield line_num, "PEP must have a title"
    elif len(line.strip()) > 79:
        yield line_num, "PEP title must be less than 80 characters"


def _validate_author(line_num, body):
    """'Author' must be list of 'Name <email@example.com>, …'"""

    lines = body.split("\n")
    for offset, line in enumerate(lines):
        if offset > 1 and line[:9].isspace():
            yield line_num + offset, f"Author line must not be over-indented"
        if offset < len(lines) - 1:
            if not line.endswith(","):
                yield line_num + offset, "Author continuation lines must end with a comma"
        yield from _email(line_num + offset, line, "Author")


def _validate_sponsor(line_num, line):
    """'Sponsor' must have format 'Name <email@example.com>'"""

    yield from _email(line_num, line, "Sponsor")


def _validate_delegate(line_num, line):
    """'Delegate' must have format 'Name <email@example.com>'"""

    if line.strip() != "":
        yield from _email(line_num, line, "Delegate")


def _validate_discussions_to(line_num, line):
    """'Discussions-To' must be a thread URL"""

    yield from _thread(line_num, line, "Discussions-To", discussions_to=True)
    for suffix in "@python.org", "@googlegroups.com":
        if line.endswith(suffix):
            remainder = line.removesuffix(suffix)
            if re.fullmatch(r'[\w\-]+', remainder) is None:
                yield line_num, "Discussions-To must be a valid mailing list"


def _validate_status(line_num, line):
    """'Status' must be a valid PEP status"""

    if line not in ALL_STATUSES:
        yield line_num, "Status must be a valid PEP status"


def _validate_type(line_num, line):
    """'Type' must be a valid PEP type"""

    if line not in {"Standards Track", "Informational", "Process"}:
        yield line_num, "Type must be a valid PEP type"


def _validate_topic(line_num, line):
    """'Topic' must be for a valid sub-index"""

    topics = line.split(", ")
    unique_topics = set(topics)
    if len(topics) > len(unique_topics):
        yield line_num, "Topic must not contain duplicates"

    if unique_topics - {"Governance", "Packaging", "Typing", "Release"}:
        yield line_num, "Topic must be for a valid sub-index"


def _validate_content_type(line_num, line):
    """'Content-Type' must be 'text/x-rst'"""

    if line != "text/x-rst":
        yield line_num, "Content-Type must be 'text/x-rst'"


def _validate_pep_references(line_num, line):
    """`Requires`/`Replaces`/`Superseded-By` must be 'NNN' PEP IDs"""

    references = line.split(", ")
    for reference in references:
        yield from _pep_num(line_num, reference, "PEP reference")


def _validate_created(line_num, line):
    """'Created' must be a 'DD-mmm-YYYY' date"""

    yield from _date(line_num, line, "Created")


def _validate_python_version(line_num, line):
    """'Python-Version' must be an ``X.Y[.Z]`` version"""

    versions = line.split(", ")
    for version in versions:
        if version.count(".") > 2:
            yield line_num, f"Python-Version must have two or three segments: {version}"
            continue

        try:
            major, minor, micro = version.split(".", 2)
        except ValueError:
            major, minor = version.split(".", 1)
            micro = ""

        if major not in "123":
            yield line_num, f"Python-Version major part must be 1, 2, or 3: {version}"
        if not _is_digits(minor) and minor != "x":
            yield line_num, f"Python-Version minor part must be numeric: {version}"

        if micro == "":
            return
        if minor == "x":
            yield line_num, f"Python-Version micro part must be empty if minor part is 'x': {version}"
        elif micro[0] == "0":
            yield line_num, f"Python-Version micro part must not have leading zeros: {version}"
        elif not _is_digits(micro):
            yield line_num, f"Python-Version micro part must be numeric: {version}"


def _validate_post_history(line_num, body):
    """'Post-History' must be '`DD-mmm-YYYY <Thread URL>`__, …'"""

    body = body
    if not body:
        return

    for post in body.replace("\n", " ").removesuffix(",").split(", "):
        post = post.strip()

        if not post.startswith("`") and not post.endswith(">`__"):
            yield from _date(line_num, post, "Post-History")
        else:
            post_date, post_url = post[1:-4].split(" <")
            yield from _date(line_num, post_date, "Post-History")
            yield from _thread(line_num, post_url, "Post-History")


def _validate_resolution(line_num, line):
    """'Resolution' must be a direct thread/message URL"""

    yield from _thread(line_num, line, "Resolution", allow_message=True)


########################
#  Validation Helpers  #
########################

def _pep_num(line_num, pep_number, prefix):
    if pep_number.startswith("0") and pep_number != "0":
        yield line_num, f"{prefix} must not contain leading zeros: {pep_number}"
    if not _is_digits(pep_number):
        yield line_num, f"{prefix} must be numeric: {pep_number}"
    elif not 0 <= int(pep_number) <= 9999:
        yield line_num, f"{prefix} must be between 0 and 9999: {pep_number}"


def _is_digits(string):
    return all(c in "0123456789" for c in string)


def _email(line_num, author_email, prefix):
    if EMAIL_PATTERN.match(author_email.strip()) is None:
        yield line_num, f"{prefix} must be a list of 'Name <email@example.com>' entries: {author_email}"


def _thread(line_num, url, prefix, allow_message=False, discussions_to=False):
    msg = f"{prefix} must be a valid thread URL"

    if not url.startswith("https://"):
        if not discussions_to:
            yield line_num, msg
        return

    if url.startswith("https://discuss.python.org/t/"):
        # Discussions-To links must be the thread itself, not a post
        pattern = DISCOURSE_THREAD_PATTERN if discussions_to else DISCOURSE_POST_PATTERN

        remainder = url.removeprefix("https://discuss.python.org/t/").removesuffix("/")
        if pattern.fullmatch(remainder) is not None:
            return

    if url.startswith("https://mail.python.org/pipermail/"):
        remainder = url.removeprefix("https://mail.python.org/pipermail/")
        if MAILMAN_2_PATTERN.fullmatch(remainder) is not None:
            return

    if url.startswith("https://mail.python.org/archives/list/"):
        remainder = url.removeprefix("https://mail.python.org/archives/list/")
        if allow_message and MAILMAN_3_MESSAGE_PATTERN.fullmatch(remainder) is not None:
            return
        if MAILMAN_3_THREAD_PATTERN.fullmatch(remainder) is not None:
            return

    yield line_num, msg


def _date(line_num, date_str, prefix):
    try:
        dt = datetime.datetime.strptime(date_str, "%d-%b-%Y")
    except ValueError:
        yield line_num, f"{prefix} must be a 'DD-mmm-YYYY' date: {date_str}"
        return

    if dt.year < 1990:
        yield line_num, f"{prefix} must not be before Python was invented: {date_str}"
    if dt > (datetime.datetime.now() + datetime.timedelta(days=14)):
        yield line_num, f"{prefix} must not be in the future: {date_str}"


if __name__ == '__main__':
    raise SystemExit(check())