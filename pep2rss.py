# usage: pep2rss.py $REPOS $REV
# (standard post-commit args)

import datetime
import re
from pathlib import Path

from feedgen import entry
from feedgen import feed


def firstline_startingwith(full_path, text):
    for line in full_path.open(encoding="utf-8"):
        if line.startswith(text):
            return line[len(text):].strip()
    return None


def pep_creation_dt(full_path):
    created_str = firstline_startingwith(full_path, "Created:")
    # bleh, I was hoping to avoid re but some PEPs editorialize on the Created line
    m = re.search(r"(\d+-\w+-\d{4})", created_str)
    if not m:
        # some older ones have an empty line, that's okay, if it's old we ipso facto don't care about it.
        # "return None" would make the most sense but datetime objects refuse to compare with that. :-|
        return datetime.datetime.fromtimestamp(0, tz=datetime.timezone.utc)
    created_str = m.group(1)
    try:
        dt = datetime.datetime.strptime(created_str, "%d-%b-%Y")
    except ValueError:
        dt = datetime.datetime.strptime(created_str, "%d-%B-%Y")
    return dt.replace(tzinfo=datetime.timezone.utc)


def main():
    # get list of peps with creation time (from "Created:" string in pep source)
    peps_with_dt = [(pep_creation_dt(path), path) for path in Path().glob("pep-????.*")]
    peps_with_dt.sort(reverse=True)  # sort peps by date, newest first

    # generate rss items for 10 most recent peps
    items = []
    for dt, full_path in peps_with_dt[:10]:
        try:
            n = int(full_path.stem.split("-")[-1])
        except ValueError:
            continue
        title = firstline_startingwith(full_path, "Title:")
        author = firstline_startingwith(full_path, "Author:")
        url = f"http://www.python.org/dev/peps/pep-{n:0>4}"
        item = entry.FeedEntry()
        item.title(f"PEP {n}: {title}")
        item.link(href=url)
        item.description(f"Author: {author}")
        item.guid(url, permalink=True)
        item.pubDate(dt)
        items.append(item)

    # the rss envelope
    desc = """
    Newest Python Enhancement Proposals (PEPs) - Information on new
    language features, and some meta-information like release
    procedure and schedules
    """.strip()
    fg = feed.FeedGenerator()
    fg.language('en')
    fg.title('Newest Python PEPs')
    fg.link(href='http://www.python.org/dev/peps')
    fg.description(desc)
    fg.lastBuildDate(datetime.datetime.now(tz=datetime.timezone.utc))
    for item in reversed(items):
        fg.add_entry(item)

    Path("peps.rss").write_bytes(fg.rss_str())


if __name__ == "__main__":
    main()
