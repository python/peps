# This file is placed in the public domain or under the
# CC0-1.0-Universal license, whichever is more permissive.

import datetime
import email.utils
from pathlib import Path

from docutils import frontend
from docutils import nodes
from docutils import utils
from docutils.parsers import rst
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
    if full_path.stem == "pep-0102":
        # remove additional content on the Created line
        created_str = created_str.split(" ", 1)[0]
    return datetime.datetime.strptime(created_str, "%d-%b-%Y")


def parse_rst(text: str) -> nodes.document:
    settings = frontend.OptionParser((rst.Parser,)).get_default_values()
    document = utils.new_document('<rst-doc>', settings=settings)
    rst.Parser().parse(text, document)
    return document


def pep_abstract(full_path: Path) -> str:
    """Return the first paragraph of the PEP abstract"""
    text = full_path.read_text(encoding="utf-8")
    # TODO replace .traverse with .findall when Sphinx updates to docutils>=0.18.1
    for node in parse_rst(text).traverse(nodes.section):
        if node.next_node(nodes.title).astext() == "Abstract":
            return node.next_node(nodes.paragraph).astext().strip().replace("\n", " ")
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
        if "@" in author or " at " in author:
            parsed_authors = email.utils.getaddresses([author])
            # ideal would be to pass as a list of dicts with names and emails to
            # item.author, but FeedGen's RSS <author/> output doesn't pass W3C
            # validation (as of 12/06/2021)
            joined_authors = ", ".join(f"{name} ({email_address})" for name, email_address in parsed_authors)
        else:
            joined_authors = author
        url = f"https://www.python.org/dev/peps/pep-{pep_num:0>4}"

        item = entry.FeedEntry()
        item.title(f"PEP {pep_num}: {title}")
        item.link(href=url)
        item.description(pep_abstract(full_path))
        item.guid(url, permalink=True)
        item.published(dt.replace(tzinfo=datetime.timezone.utc))  # ensure datetime has a timezone
        item.author(email=joined_authors)
        items.append(item)

    # The rss envelope
    desc = """
    Newest Python Enhancement Proposals (PEPs) - Information on new
    language features, and some meta-information like release
    procedure and schedules.
    """

    # Setup feed generator
    fg = feed.FeedGenerator()
    fg.language("en")
    fg.generator("")
    fg.docs("https://cyber.harvard.edu/rss/rss.html")

    # Add metadata
    fg.title("Newest Python PEPs")
    fg.link(href="https://www.python.org/dev/peps")
    fg.link(href="https://www.python.org/dev/peps/peps.rss", rel="self")
    fg.description(" ".join(desc.split()))
    fg.lastBuildDate(datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc))

    # Add PEP information (ordered by newest first)
    for item in items:
        fg.add_entry(item)

    pep_dir.joinpath("peps.rss").write_bytes(fg.rss_str(pretty=True))


if __name__ == "__main__":
    main()
