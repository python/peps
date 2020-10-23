#!/usr/bin/env python3

# usage: pep-hook.py $REPOS $REV
# (standard post-commit args)

import os, glob, time, datetime, stat, re, sys
import PyRSS2Gen as rssgen

RSS_PATH = os.path.join(sys.argv[1], 'peps.rss')

def firstline_startingwith(full_path, text):
    for line in open(full_path, encoding="utf-8"):
        if line.startswith(text):
            return line[len(text):].strip()
    return None

# get list of peps with creation time
# (from "Created:" string in pep .rst or .txt)
peps = glob.glob('pep-*.txt')
peps.extend(glob.glob('pep-*.rst'))
def pep_creation_dt(full_path):
    created_str = firstline_startingwith(full_path, 'Created:')
    # bleh, I was hoping to avoid re but some PEPs editorialize
    # on the Created line
    m = re.search(r'''(\d+-\w+-\d{4})''', created_str)
    if not m:
        # some older ones have an empty line, that's okay, if it's old
        # we ipso facto don't care about it.
        # "return None" would make the most sense but datetime objects
        # refuse to compare with that. :-|
        return datetime.datetime(*time.localtime(0)[:6])
    created_str = m.group(1)
    try:
        t = time.strptime(created_str, '%d-%b-%Y')
    except ValueError:
        t = time.strptime(created_str, '%d-%B-%Y')
    return datetime.datetime(*t[:6])
peps_with_dt = [(pep_creation_dt(full_path), full_path) for full_path in peps]
# sort peps by date, newest first
peps_with_dt.sort(reverse=True)

# generate rss items for 10 most recent peps
items = []
for dt, full_path in peps_with_dt[:10]:
    try:
        n = int(full_path.split('-')[-1].split('.')[0])
    except ValueError:
        pass
    title = firstline_startingwith(full_path, 'Title:')
    author = firstline_startingwith(full_path, 'Author:')
    url = 'https://www.python.org/dev/peps/pep-%0.4d/' % n
    item = rssgen.RSSItem(
        title = 'PEP %d: %s' % (n, title),
        link = url,
        description = 'Author: %s' % author,
        guid = rssgen.Guid(url),
        pubDate = dt)
    items.append(item)

# the rss envelope
desc = """
Newest Python Enhancement Proposals (PEPs) - Information on new
language features, and some meta-information like release
procedure and schedules
""".strip()
rss = rssgen.RSS2(
    title = 'Newest Python PEPs',
    link = 'https://www.python.org/dev/peps/',
    description = desc,
    lastBuildDate = datetime.datetime.now(),
    items = items)

with open(RSS_PATH, 'w', encoding="utf-8") as fp:
    fp.write(rss.to_xml(encoding="utf-8"))
