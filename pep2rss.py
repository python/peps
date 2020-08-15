import datetime
import email.utils
import re
from pathlib import Path

import lxml.etree  # Prevents AttributeError when importing `feedgen.util`
import feedgen.util

if feedgen.util and lxml.etree:
    # Monkeypatch format function
    feedgen.util.formatRFC2822 = lambda dt: email.utils.format_datetime(dt, usegmt=True)

from dateutil import parser
from feedgen import entry
from feedgen import feed


def first_line_starting_with(full_path: Path, text: str) -> str:
    for line in full_path.open(encoding="utf-8"):
        if line.startswith(text):
            return line[len(text):].strip()
    return ""


def pep_creation_dt(full_path: Path) -> datetime.datetime:
    created_str = first_line_starting_with(full_path, "Created:")
    # bleh, I was hoping to avoid re but some PEPs editorialize on the Created line
    # (note as of Aug 2020 only PEP 102 has additional content on the Created line)
    m = re.search(r"(\d+[- ][\w\d]+[- ]\d{2,4})", created_str)
    if not m:
        # some older ones have an empty line, that's okay, if it's old we ipso facto don't care about it.
        # "return None" would make the most sense but datetime objects refuse to compare with that. :-|
        return datetime.datetime.fromtimestamp(0, tz=datetime.timezone.utc)
    created_str = m.group(1)
    try:
        dt = parser.parse(created_str, dayfirst=True)
    except (ValueError, OverflowError):
        dt = datetime.datetime.fromtimestamp(0)
    return dt.replace(tzinfo=datetime.timezone.utc)


def main():
    pep_dir = Path(__file__).parent  # this must point to the directory with the PEP sources
    # get list of peps with creation time (from "Created:" string in pep source)
    peps_with_dt = [(pep_creation_dt(path), path) for path in pep_dir.glob("pep-????.*")]
    peps_with_dt.sort()  # sort peps by date, newest first

    # generate rss items for 10 most recent peps
    items = []
    for dt, full_path in peps_with_dt[-10:]:
        try:
            n = int(full_path.stem.split("-")[-1])
        except ValueError:
            continue
        title = first_line_starting_with(full_path, "Title:")
        author = first_line_starting_with(full_path, "Author:")
        parsed_authors = email.utils.getaddresses([author]) if "@" in author else [(author, "")]
        url = f"http://www.python.org/dev/peps/pep-{n:0>4}"
        item = entry.FeedEntry()
        item.title(f"PEP {n}: {title}")
        item.link(href=url)
        item.description(f"Author: {author}")  # TODO add PEP abstract ref GH-1085
        item.guid(url, permalink=True)
        item.pubDate(dt)
        item.author([dict(name=parsed_author[0], email=parsed_author[1]) for parsed_author in parsed_authors])
        items.append(item)

    # the rss envelope
    desc = """
    Newest Python Enhancement Proposals (PEPs) - Information on new
    language features, and some meta-information like release
    procedure and schedules
    """.strip()

    # Setup feed generator
    fg = feed.FeedGenerator()
    fg.language('en')
    fg.generator("")
    fg.docs("http://blogs.law.harvard.edu/tech/rss")

    # Add metadata
    fg.title('Newest Python PEPs')
    fg.link(href='http://www.python.org/dev/peps')
    fg.description(desc)
    fg.lastBuildDate(datetime.datetime.now(tz=datetime.timezone.utc))

    # Add PEP information (ordered by newest first)
    for item in items:
        fg.add_entry(item)

    Path("peps.rss").write_bytes(fg.rss_str(pretty=True))


if __name__ == "__main__":
    main()
