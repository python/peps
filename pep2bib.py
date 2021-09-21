#!/usr/bin/env python3

# usage: python3 pep2bib.py .

import datetime
import glob
import os
import re
import sys
import time
from pybtex.database import Entry, BibliographyData

BIB_PATH = os.path.join(sys.argv[1], 'peps.bib')


def firstline_startingwith(full_path, text):
    result = None
    for line in open(full_path, encoding="utf-8"):
        if result is not None:
            if not line[0].strip():  # Line begins with whitespace
                result += line
            else:
                return result
        if line.startswith(text):
            result = line[len(text):].strip()
    return None


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


def pep_number(full_path):
    n_str = full_path.split('-')[-1].split('.')[0]
    try:
        n = int(n_str)
    except ValueError:
        raise Exception("Can't parse pep number %s" % n_str)

    return n


name_first_regex = re.compile('(.*)<.*>')
mail_first_regex = re.compile('.*\((.*)\)')
name_only_regex = re.compile('(.*)')

months = {
    1: 'jan',
    2: 'feb',
    3: 'mar',
    4: 'apr',
    5: 'may',
    6: 'jun',
    7: 'jul',
    8: 'aug',
    9: 'sep',
    10: 'oct',
    11: 'nov',
    12: 'dec',
}


def clean_authors(authors_str):
    authors = authors_str.split(',')
    cleaned = []
    for author in authors:
        match = name_first_regex.match(author)
        if match is None:
            match = mail_first_regex.match(author)
        if match is None:
            match = name_only_regex.match(author)
        cleaned.append(match.group(1).strip())
    return " and ".join(cleaned)


def main():
    # get list of peps with creation time
    # (from "Created:" string in pep .rst or .txt)
    peps = glob.glob('pep-*.txt')
    peps.extend(glob.glob('pep-*.rst'))

    peps_with_dt = [(pep_number(full_path), pep_creation_dt(full_path), full_path) for full_path in peps]
    # sort peps by date, newest first
    peps_with_dt.sort()

    # generate rss items for 10 most recent peps
    items = {}
    for n, dt, full_path in peps_with_dt:
        title = firstline_startingwith(full_path, 'Title:')
        authors = firstline_startingwith(full_path, 'Author:')
        authors = clean_authors(authors)
        url = 'https://www.python.org/dev/peps/pep-%0.4d/' % n
        item = Entry('techreport', [
            ('author', authors),
            ('title', 'PEP %d: %s' % (n, title)),
            ('institution', "Python Software Foundation"),
            ('year', str(dt.year)),
            ('month', months[dt.month]),
            ('type', 'PEP'),
            ('number', str(n)),
            ('url', url)
        ])
        items['pep%d' % n] = item

    bib = BibliographyData(items)
    bib_str = bib.to_string('bibtex')

    # pybtex always quotes strings, but we want month strings unquoted, so bib styles can replace it
    bib_str = re.sub('month = "(.*)"', r'month = \1', bib_str)

    with open(BIB_PATH, 'w', encoding="utf-8") as fp:
        fp.write(bib_str)


if __name__ == '__main__':
    main()
