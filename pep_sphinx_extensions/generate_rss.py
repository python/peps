# This file is placed in the public domain or under the
# CC0-1.0-Universal license, whichever is more permissive.

from __future__ import annotations

import datetime as dt
from email.utils import format_datetime, getaddresses
from html import escape
from pathlib import Path

from pep_sphinx_extensions.doctree import get_from_doctree

RSS_DESCRIPTION = (
    "Newest Python Enhancement Proposals (PEPs): "
    "Information on new language features "
    "and some meta-information like release procedure and schedules."
)


def _format_rfc_2822(datetime: dt.datetime) -> str:
    datetime = datetime.replace(tzinfo=dt.timezone.utc)
    return format_datetime(datetime, usegmt=True)


def pep_creation(full_path: Path) -> dt.datetime:
    created_str = get_from_doctree(full_path, "Created")
    try:
        return dt.datetime.strptime(created_str, "%d-%b-%Y")
    except ValueError:
        return dt.datetime.min


def _generate_items(doctree_dir: Path):
    # get list of peps with creation time (from "Created:" string in pep source)
    peps_with_dt = sorted((pep_creation(path), path) for path in doctree_dir.glob("pep-????.doctree"))

    # generate rss items for 10 most recent peps (in reverse order)
    for datetime, full_path in reversed(peps_with_dt[-10:]):
        try:
            pep_num = int(get_from_doctree(full_path, "PEP"))
        except ValueError:
            continue

        title = get_from_doctree(full_path, "Title")
        url = f"https://peps.python.org/pep-{pep_num:0>4}/"
        abstract = get_from_doctree(full_path, "Abstract")
        author = get_from_doctree(full_path, "Author")
        if "@" in author or " at " in author:
            parsed_authors = getaddresses([author])
            joined_authors = ", ".join(f"{name} ({email_address})" for name, email_address in parsed_authors)
        else:
            joined_authors = author

        item = f"""\
    <item>
      <title>PEP {pep_num}: {escape(title, quote=False)}</title>
      <link>{escape(url, quote=False)}</link>
      <description>{escape(abstract, quote=False)}</description>
      <author>{escape(joined_authors, quote=False)}</author>
      <guid isPermaLink="true">{url}</guid>
      <pubDate>{_format_rfc_2822(datetime)}</pubDate>
    </item>"""
        yield item


def create_rss_feed(doctree_dir: Path, output_dir: Path):
    # The rss envelope
    last_build_date = _format_rfc_2822(dt.datetime.now(dt.timezone.utc))
    items = "\n".join(_generate_items(Path(doctree_dir)))
    output = f"""\
<?xml version='1.0' encoding='UTF-8'?>
<rss xmlns:atom="http://www.w3.org/2005/Atom" xmlns:content="http://purl.org/rss/1.0/modules/content/" version="2.0">
  <channel>
    <title>Newest Python PEPs</title>
    <link>https://peps.python.org/</link>
    <description>{RSS_DESCRIPTION}</description>
    <atom:link href="https://peps.python.org/peps.rss" rel="self"/>
    <docs>https://cyber.harvard.edu/rss/rss.html</docs>
    <language>en</language>
    <lastBuildDate>{last_build_date}</lastBuildDate>
{items}
  </channel>
</rss>
"""

    # output directory for target HTML files
    Path(output_dir, "peps.rss").write_text(output, encoding="utf-8")
