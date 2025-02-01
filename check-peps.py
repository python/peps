#!/usr/bin/env python3

# This file is placed in the public domain or under the
# CC0-1.0-Universal license, whichever is more permissive.

"""check-peps: Check PEPs for common mistakes.

Usage: check-peps [-d | --detailed] <PEP files...>

Only the PEPs specified are checked.
If none are specified, all PEPs are checked.

Use "--detailed" to show the contents of lines where errors were found.
"""

from __future__ import annotations

import datetime as dt
import re
import sys
from pathlib import Path

TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator, KeysView, Sequence
    from typing import TypeAlias

    # (line number, warning message)
    Message: TypeAlias = tuple[int, str]
    MessageIterator: TypeAlias = Iterator[Message]


# get the directory with the PEP sources
ROOT_DIR = Path(__file__).resolve().parent
PEP_ROOT = ROOT_DIR / "peps"

# See PEP 12 for the order
# Note we retain "BDFL-Delegate"
ALL_HEADERS = (
    "PEP",
    "Title",
    "Author",
    "Sponsor",
    "BDFL-Delegate", "PEP-Delegate",
    "Discussions-To",
    "Status",
    "Type",
    "Topic",
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

DEFAULT_FLAGS = re.ASCII | re.IGNORECASE  # Insensitive latin

# any sequence of letters or '-', followed by a single ':' and a space or end of line
HEADER_PATTERN = re.compile(r"^([a-z\-]+):(?: |$)", DEFAULT_FLAGS)
# any sequence of unicode letters or legal special characters
NAME_PATTERN = re.compile(r"(?:[^\W\d_]|[ ',\-.])+(?: |$)")
# any sequence of ASCII letters, digits, or legal special characters
EMAIL_LOCAL_PART_PATTERN = re.compile(r"[\w!#$%&'*+\-/=?^{|}~.]+", DEFAULT_FLAGS)

DISCOURSE_THREAD_PATTERN = re.compile(r"([\w\-]+/)?\d+", DEFAULT_FLAGS)
DISCOURSE_POST_PATTERN = re.compile(r"([\w\-]+/)?\d+(/\d+)?", DEFAULT_FLAGS)

MAILMAN_2_PATTERN = re.compile(r"[\w\-]+/\d{4}-[a-z]+/\d+\.html", DEFAULT_FLAGS)
MAILMAN_3_THREAD_PATTERN = re.compile(r"[\w\-]+@python\.org/thread/[a-z0-9]+/?", DEFAULT_FLAGS)
MAILMAN_3_MESSAGE_PATTERN = re.compile(r"[\w\-]+@python\.org/message/[a-z0-9]+/?(#[a-z0-9]+)?", DEFAULT_FLAGS)

# Controlled by the "--detailed" flag
DETAILED_ERRORS = False


def check(filenames: Sequence[str] = (), /) -> int:
    """The main entry-point."""
    if filenames:
        filenames = map(Path, filenames)
    else:
        filenames = PEP_ROOT.glob("pep-????.rst")
    if (count := sum(map(check_file, filenames))) > 0:
        s = "s" * (count != 1)
        print(f"check-peps failed: {count} error{s}", file=sys.stderr)
        return 1
    return 0


def check_file(filename: Path, /) -> int:
    filename = filename.resolve()
    try:
        content = filename.read_text(encoding="utf-8")
    except FileNotFoundError:
        return _output_error(filename, [""], [(0, "Could not read PEP!")])
    else:
        lines = content.splitlines()
        return _output_error(filename, lines, check_peps(filename, lines))


def check_peps(filename: Path, lines: Sequence[str], /) -> MessageIterator:
    yield from check_headers(lines)
    for line_num, line in enumerate(lines, start=1):
        if filename.stem.removeprefix("pep-") in SKIP_DIRECT_PEP_LINK_CHECK:
            continue
        yield from check_direct_links(line_num, line.lstrip())


def check_headers(lines: Sequence[str], /) -> MessageIterator:
    yield from _validate_pep_number(next(iter(lines), ""))

    found_headers = {}
    found_header_lines: list[tuple[str, int]] = []
    line_num = 0
    for line_num, line in enumerate(lines, start=1):
        if line.strip() == "":
            headers_end_line_num = line_num
            break
        if match := HEADER_PATTERN.match(line):
            header = match[1]
            found_header_lines.append((header, line_num))
            if header in ALL_HEADERS:
                if header not in found_headers:
                    found_headers[header] = None
                else:
                    yield line_num, f"Must not have duplicate header: {header} "
            else:
                yield line_num, f"Must not have invalid header: {header}"
    else:
        headers_end_line_num = line_num

    yield from _validate_required_headers(found_headers.keys())

    shifted_line_nums = [line for _, line in found_header_lines[1:]]
    for i, (header, line_num) in enumerate(found_header_lines):
        start = line_num - 1
        end = headers_end_line_num - 1
        if i < len(found_header_lines) - 1:
            end = shifted_line_nums[i] - 1
        remainder = "\n".join(lines[start:end]).removeprefix(f"{header}:")
        if remainder != "":
            if remainder[0] not in {" ", "\n"}:
                yield line_num, f"Headers must have a space after the colon: {header}"
            remainder = remainder.lstrip()
        yield from _validate_header(header, line_num, remainder)


def _validate_header(header: str, line_num: int, content: str) -> MessageIterator:
    if header == "Title":
        yield from _validate_title(line_num, content)
    elif header == "Author":
        yield from _validate_author(line_num, content)
    elif header == "Sponsor":
        yield from _validate_sponsor(line_num, content)
    elif header in {"BDFL-Delegate", "PEP-Delegate"}:
        yield from _validate_delegate(line_num, content)
    elif header == "Discussions-To":
        yield from _validate_discussions_to(line_num, content)
    elif header == "Status":
        yield from _validate_status(line_num, content)
    elif header == "Type":
        yield from _validate_type(line_num, content)
    elif header == "Topic":
        yield from _validate_topic(line_num, content)
    elif header in {"Requires", "Replaces", "Superseded-By"}:
        yield from _validate_pep_references(line_num, content)
    elif header == "Created":
        yield from _validate_created(line_num, content)
    elif header == "Python-Version":
        yield from _validate_python_version(line_num, content)
    elif header == "Post-History":
        yield from _validate_post_history(line_num, content)
    elif header == "Resolution":
        yield from _validate_resolution(line_num, content)


def check_direct_links(line_num: int, line: str) -> MessageIterator:
    """Check that PEPs and RFCs aren't linked directly"""

    line = line.lower()
    if "dev/peps/pep-" in line or "peps.python.org/pep-" in line:
        yield line_num, "Use the :pep:`NNN` role to refer to PEPs"
    if "rfc-editor.org/rfc/" in line or "ietf.org/doc/html/rfc" in line:
        yield line_num, "Use the :rfc:`NNN` role to refer to RFCs"


def _output_error(filename: Path, lines: Sequence[str], errors: Iterable[Message]) -> int:
    relative_filename = filename.relative_to(ROOT_DIR)
    err_count = 0
    for line_num, msg in errors:
        err_count += 1

        print(f"{relative_filename}:{line_num}:  {msg}")
        if not DETAILED_ERRORS:
            continue

        line = lines[line_num - 1]
        print("     |")
        print(f"{line_num: >4} | '{line}'")
        print("     |")

    return err_count


###########################
#  PEP Header Validators  #
###########################


def _validate_required_headers(found_headers: KeysView[str]) -> MessageIterator:
    """PEPs must have all required headers, in the PEP 12 order"""

    if missing := REQUIRED_HEADERS.difference(found_headers):
        for missing_header in sorted(missing, key=ALL_HEADERS.index):
            yield 1, f"Must have required header: {missing_header}"

    ordered_headers = sorted(found_headers, key=ALL_HEADERS.index)
    if list(found_headers) != ordered_headers:
        order_str = ", ".join(ordered_headers)
        yield 1, "Headers must be in PEP 12 order. Correct order: " + order_str


def _validate_pep_number(line: str) -> MessageIterator:
    """'PEP' header must be a number 1-9999"""

    if not line.startswith("PEP: "):
        yield 1, "PEP must begin with the 'PEP:' header"
        return

    pep_number = line.removeprefix("PEP: ").lstrip()
    yield from _pep_num(1, pep_number, "'PEP:' header")


def _validate_title(line_num: int, line: str) -> MessageIterator:
    """'Title' must be 1-79 characters"""

    if len(line) == 0:
        yield line_num, "PEP must have a title"
    elif len(line) > 79:
        yield line_num, "PEP title must be less than 80 characters"


def _validate_author(line_num: int, body: str) -> MessageIterator:
    """'Author' must be list of 'Name <email@example.com>, …'"""

    lines = body.split("\n")
    for offset, line in enumerate(lines):
        if offset >= 1 and line[:9].isspace():
            # Checks for:
            # Author: Alice
            #             Bob
            #         ^^^^
            # Note that len("Author: ") == 8
            yield line_num + offset, "Author line must not be over-indented"
        if offset < len(lines) - 1:
            if not line.endswith(","):
                yield line_num + offset, "Author continuation lines must end with a comma"
        for part in line.removesuffix(",").split(", "):
            yield from _email(line_num + offset, part, "Author")


def _validate_sponsor(line_num: int, line: str) -> MessageIterator:
    """'Sponsor' must have format 'Name <email@example.com>'"""

    yield from _email(line_num, line, "Sponsor")


def _validate_delegate(line_num: int, line: str) -> MessageIterator:
    """'Delegate' must have format 'Name <email@example.com>'"""

    if line == "":
        return

    # PEP 451
    if ", " in line:
        for part in line.removesuffix(",").split(", "):
            yield from _email(line_num, part, "Delegate")
        return

    yield from _email(line_num, line, "Delegate")


def _validate_discussions_to(line_num: int, line: str) -> MessageIterator:
    """'Discussions-To' must be a thread URL"""

    yield from _thread(line_num, line, "Discussions-To", discussions_to=True)
    if line.startswith("https://"):
        return
    for suffix in "@python.org", "@googlegroups.com":
        if line.endswith(suffix):
            remainder = line.removesuffix(suffix)
            if re.fullmatch(r"[\w\-]+", remainder) is None:
                yield line_num, "Discussions-To must be a valid mailing list"
            return
    yield line_num, "Discussions-To must be a valid thread URL or mailing list"


def _validate_status(line_num: int, line: str) -> MessageIterator:
    """'Status' must be a valid PEP status"""

    if line not in ALL_STATUSES:
        yield line_num, "Status must be a valid PEP status"


def _validate_type(line_num: int, line: str) -> MessageIterator:
    """'Type' must be a valid PEP type"""

    if line not in {"Standards Track", "Informational", "Process"}:
        yield line_num, "Type must be a valid PEP type"


def _validate_topic(line_num: int, line: str) -> MessageIterator:
    """'Topic' must be for a valid sub-index"""

    topics = line.split(", ")
    unique_topics = set(topics)
    if len(topics) > len(unique_topics):
        yield line_num, "Topic must not contain duplicates"

    if unique_topics - {"Governance", "Packaging", "Typing", "Release"}:
        if not all(map(str.istitle, unique_topics)):
            yield line_num, "Topic must be properly capitalised (Title Case)"
        if unique_topics - {"governance", "packaging", "typing", "release"}:
            yield line_num, "Topic must be for a valid sub-index"
    if sorted(topics) != topics:
        yield line_num, "Topic must be sorted lexicographically"


def _validate_pep_references(line_num: int, line: str) -> MessageIterator:
    """`Requires`/`Replaces`/`Superseded-By` must be 'NNN' PEP IDs"""

    line = line.removesuffix(",").rstrip()
    if line.count(", ") != line.count(","):
        yield line_num, "PEP references must be separated by comma-spaces (', ')"
        return

    references = line.split(", ")
    for reference in references:
        yield from _pep_num(line_num, reference, "PEP reference")


def _validate_created(line_num: int, line: str) -> MessageIterator:
    """'Created' must be a 'DD-mmm-YYYY' date"""

    yield from _date(line_num, line, "Created")


def _validate_python_version(line_num: int, line: str) -> MessageIterator:
    """'Python-Version' must be an ``X.Y[.Z]`` version"""

    versions = line.split(", ")
    for version in versions:
        if version.count(".") not in {1, 2}:
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
        elif minor != "0" and minor[0] == "0":
            yield line_num, f"Python-Version minor part must not have leading zeros: {version}"

        if micro == "":
            return
        if minor == "x":
            yield line_num, f"Python-Version micro part must be empty if minor part is 'x': {version}"
        elif micro[0] == "0":
            yield line_num, f"Python-Version micro part must not have leading zeros: {version}"
        elif not _is_digits(micro):
            yield line_num, f"Python-Version micro part must be numeric: {version}"


def _validate_post_history(line_num: int, body: str) -> MessageIterator:
    """'Post-History' must be '`DD-mmm-YYYY <Thread URL>`__, …' or `DD-mmm-YYYY`"""

    if body == "":
        return

    for offset, line in enumerate(body.removesuffix(",").split("\n"), start=line_num):
        for post in line.removesuffix(",").strip().split(", "):
            prefix, postfix = (post.startswith("`"), post.endswith(">`__"))
            if not prefix and not postfix:
                yield from _date(offset, post, "Post-History")
            elif prefix and postfix:
                post_date, post_url = post[1:-4].split(" <")
                yield from _date(offset, post_date, "Post-History")
                yield from _thread(offset, post_url, "Post-History")
            else:
                yield offset, "post line must be a date or both start with “`” and end with “>`__”"


def _validate_resolution(line_num: int, line: str) -> MessageIterator:
    """'Resolution' must be a direct thread/message URL or a link with a date."""

    prefix, postfix = (line.startswith("`"), line.endswith(">`__"))
    if not prefix and not postfix:
        yield from _thread(line_num, line, "Resolution", allow_message=True)
    elif prefix and postfix:
        post_date, post_url = line[1:-4].split(" <")
        yield from _date(line_num, post_date, "Resolution")
        yield from _thread(line_num, post_url, "Resolution", allow_message=True)
    else:
        yield line_num, "Resolution line must be a link or both start with “`” and end with “>`__”"


########################
#  Validation Helpers  #
########################


def _pep_num(line_num: int, pep_number: str, prefix: str) -> MessageIterator:
    if pep_number == "":
        yield line_num, f"{prefix} must not be blank: {pep_number!r}"
        return
    if pep_number.startswith("0") and pep_number != "0":
        yield line_num, f"{prefix} must not contain leading zeros: {pep_number!r}"
    if not _is_digits(pep_number):
        yield line_num, f"{prefix} must be numeric: {pep_number!r}"
    elif not 0 <= int(pep_number) <= 9999:
        yield line_num, f"{prefix} must be between 0 and 9999: {pep_number!r}"


def _is_digits(string: str) -> bool:
    """Match a string of ASCII digits ([0-9]+)."""
    return string.isascii() and string.isdigit()


def _email(line_num: int, author_email: str, prefix: str) -> MessageIterator:
    author_email = author_email.strip()

    if author_email.count("<") > 1:
        msg = f"{prefix} entries must not contain multiple '<': {author_email!r}"
        yield line_num, msg
    if author_email.count(">") > 1:
        msg = f"{prefix} entries must not contain multiple '>': {author_email!r}"
        yield line_num, msg
    if author_email.count("@") > 1:
        msg = f"{prefix} entries must not contain multiple '@': {author_email!r}"
        yield line_num, msg

    author = author_email.split("<", 1)[0].rstrip()
    if NAME_PATTERN.fullmatch(author) is None:
        msg = f"{prefix} entries must begin with a valid 'Name': {author_email!r}"
        yield line_num, msg
        return

    email_text = author_email.removeprefix(author)
    if not email_text:
        # Does not have the optional email part
        return

    if not email_text.startswith(" <") or not email_text.endswith(">"):
        msg = f"{prefix} entries must be formatted as 'Name <email@example.com>': {author_email!r}"
        yield line_num, msg
    email_text = email_text.removeprefix(" <").removesuffix(">")

    if "@" in email_text:
        local, domain = email_text.rsplit("@", 1)
    elif " at " in email_text:
        local, domain = email_text.rsplit(" at ", 1)
    else:
        yield line_num, f"{prefix} entries must contain a valid email address: {author_email!r}"
        return
    if EMAIL_LOCAL_PART_PATTERN.fullmatch(local) is None or _invalid_domain(domain):
        yield line_num, f"{prefix} entries must contain a valid email address: {author_email!r}"


def _invalid_domain(domain_part: str) -> bool:
    *labels, root = domain_part.split(".")
    for label in labels:
        if not label.replace("-", "").isalnum():
            return True
    return not root.isalnum() or not root.isascii()


def _thread(line_num: int, url: str, prefix: str, *, allow_message: bool = False, discussions_to: bool = False) -> MessageIterator:
    if allow_message and discussions_to:
        msg = "allow_message and discussions_to cannot both be True"
        raise ValueError(msg)

    msg = f"{prefix} must be a valid thread URL"

    if not url.startswith("https://"):
        if not discussions_to:
            yield line_num, msg
        return

    if url.startswith("https://discuss.python.org/t/"):
        remainder = url.removeprefix("https://discuss.python.org/t/").removesuffix("/")

        # Discussions-To links must be the thread itself, not a post
        if discussions_to:
            # The equivalent pattern is similar to '([\w\-]+/)?\d+',
            # but the topic name must contain a non-numeric character

            # We use ``str.rpartition`` as the topic name is optional
            topic_name, _, topic_id = remainder.rpartition("/")
            if topic_name == '' and _is_digits(topic_id):
                return
            topic_name = topic_name.replace("-", "0").replace("_", "0")
            # the topic name must not be entirely numeric
            valid_topic_name = not _is_digits(topic_name) and topic_name.isalnum()
            if valid_topic_name and _is_digits(topic_id):
                return
        else:
            # The equivalent pattern is similar to '([\w\-]+/)?\d+(/\d+)?',
            # but the topic name must contain a non-numeric character
            if remainder.count("/") == 2:
                # When there are three parts, the URL must be "topic-name/topic-id/post-id".
                topic_name, topic_id, post_id = remainder.rsplit("/", 2)
                topic_name = topic_name.replace("-", "0").replace("_", "0")
                valid_topic_name = not _is_digits(topic_name) and topic_name.isalnum()
                if valid_topic_name and _is_digits(topic_id) and _is_digits(post_id):
                    # the topic name must not be entirely numeric
                    return
            elif remainder.count("/") == 1:
                # When there are only two parts, there's an ambiguity between
                # "topic-name/topic-id" and "topic-id/post-id".
                # We disambiguate by checking if the LHS is a valid name and
                # the RHS is a valid topic ID (for the former),
                # and then if both the LHS and RHS are valid IDs (for the latter).
                left, right = remainder.rsplit("/")
                left = left.replace("-", "0").replace("_", "0")
                # the topic name must not be entirely numeric
                left_is_name = not _is_digits(left) and left.isalnum()
                if left_is_name and _is_digits(right):
                    return
                elif _is_digits(left) and _is_digits(right):
                    return
            else:
                # When there's only one part, it must be a valid topic ID.
                if _is_digits(remainder):
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


def _date(line_num: int, date_str: str, prefix: str) -> MessageIterator:
    try:
        parsed_date = dt.datetime.strptime(date_str, "%d-%b-%Y")
    except ValueError:
        yield line_num, f"{prefix} must be a 'DD-mmm-YYYY' date: {date_str!r}"
        return
    else:
        if date_str[1] == "-":  # Date must be zero-padded
            yield line_num, f"{prefix} must be a 'DD-mmm-YYYY' date: {date_str!r}"
            return

    if parsed_date.year < 1990:
        yield line_num, f"{prefix} must not be before Python was invented: {date_str!r}"
    if parsed_date > (dt.datetime.now() + dt.timedelta(days=14)):
        yield line_num, f"{prefix} must not be in the future: {date_str!r}"


if __name__ == "__main__":
    if {"-h", "--help", "-?"}.intersection(sys.argv[1:]):
        print(__doc__, file=sys.stderr)
        raise SystemExit(0)

    files = {}
    for arg in sys.argv[1:]:
        if not arg.startswith("-"):
            files[arg] = None
        elif arg in {"-d", "--detailed"}:
            DETAILED_ERRORS = True
        else:
            print(f"Unknown option: {arg!r}", file=sys.stderr)
            raise SystemExit(1)
    raise SystemExit(check(files))
