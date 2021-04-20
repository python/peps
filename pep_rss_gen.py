import datetime
import email.utils
from pathlib import Path
import re

from dateutil import parser
import docutils.frontend
import docutils.nodes
import docutils.parsers.rst
import docutils.utils
from feedgen import entry
from feedgen import feed


# Monkeypatch feedgen.util.formatRFC2822
def _format_rfc_2822(dt: datetime.datetime) -> str:
    return email.utils.format_datetime(dt, usegmt=True)


entry.formatRFC2822 = feed.formatRFC2822 = _format_rfc_2822
line_cache: dict[Path, dict[str, str]] = {}


def first_line_starting_with(full_path: Path, text: str) -> str:
    # Try and retrieve from cache
    if full_path in line_cache:
        return line_cache[full_path].get(text, "")

    # Else read source
    line_cache[full_path] = path_cache = {}
    for line in full_path.open(encoding="utf-8"):
        if line.startswith("Created:"):
            path_cache["Created:"] = line.removeprefix("Created:").strip()
        elif line.startswith("Title:"):
            path_cache["Title:"] = line.removeprefix("Title:").strip()
        elif line.startswith("Author:"):
            path_cache["Author:"] = line.removeprefix("Author:").strip()

        # Once all have been found, exit loop
        if path_cache.keys == {"Created:", "Title:", "Author:"}:
            break
    return path_cache.get(text, "")


def pep_creation(full_path: Path) -> datetime.datetime:
    created_str = first_line_starting_with(full_path, "Created:")
    # bleh, I was hoping to avoid re but some PEPs editorialize on the Created line
    # (note as of Aug 2020 only PEP 102 has additional content on the Created line)
    m = re.search(r"(\d+[- ][\w\d]+[- ]\d{2,4})", created_str)
    if not m:
        # some older ones have an empty line, that's okay, if it's old we ipso facto don't care about it.
        # "return None" would make the most sense but datetime objects refuse to compare with that. :-|
        return datetime.datetime(1900, 1, 1)
    created_str = m.group(1)
    try:
        return parser.parse(created_str, dayfirst=True)
    except (ValueError, OverflowError):
        return datetime.datetime(1900, 1, 1)


def parse_rst(text: str) -> docutils.nodes.document:
    rst_parser = docutils.parsers.rst.Parser()
    components = (docutils.parsers.rst.Parser,)
    settings = docutils.frontend.OptionParser(components=components).get_default_values()
    document = docutils.utils.new_document('<rst-doc>', settings=settings)
    rst_parser.parse(text, document)
    return document


def pep_abstract(full_path: Path) -> str:
    """Return the first paragraph of the PEP abstract"""
    text = full_path.read_text(encoding="utf-8")
    for node in parse_rst(text):
        if "<title>Abstract</title>" in str(node):
            for child in node:
                if child.tagname == "paragraph":
                    return child.astext().strip().replace("\n", " ")
    return ""


def main():
    # get the directory with the PEP sources
    pep_dir = Path(__file__).parent

    # get list of peps with creation time (from "Created:" string in pep source)
    peps_with_dt = sorted((pep_creation(path), path) for path in pep_dir.glob("pep-????.*"))

    # generate rss items for 10 most recent peps
    items = []
    for dt, full_path in peps_with_dt[-10:]:
        try:
            pep_num = int(full_path.stem.split("-")[-1])
        except ValueError:
            continue

        title = first_line_starting_with(full_path, "Title:")
        author = first_line_starting_with(full_path, "Author:")
        parsed_authors = email.utils.getaddresses([author]) if "@" in author else [(author, "")]
        url = f"https://www.python.org/dev/peps/pep-{pep_num:0>4}"

        item = entry.FeedEntry()
        item.title(f"PEP {pep_num}: {title}")
        item.link(href=url)
        item.description(pep_abstract(full_path))
        item.guid(url, permalink=True)
        item.published(dt.replace(tzinfo=datetime.timezone.utc))  # ensure datetime has a timezone
        item.author([dict(name=parsed_author[0], email=parsed_author[1]) for parsed_author in parsed_authors])
        items.append(item)

    # The rss envelope
    desc = """
    Newest Python Enhancement Proposals (PEPs) - Information on new
    language features, and some meta-information like release
    procedure and schedules.
    """.replace("\n    ", " ").strip()

    # Setup feed generator
    fg = feed.FeedGenerator()
    fg.language("en")
    fg.generator("")
    fg.docs("https://cyber.harvard.edu/rss/rss.html")

    # Add metadata
    fg.title("Newest Python PEPs")
    fg.link(href="https://www.python.org/dev/peps")
    fg.description(desc)
    fg.lastBuildDate(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc))

    # Add PEP information (ordered by newest first)
    for item in items:
        fg.add_entry(item)

    pep_dir.joinpath("peps.rss").write_bytes(fg.rss_str(pretty=True))


if __name__ == "__main__":
    main()
