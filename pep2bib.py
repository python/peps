#!/usr/bin/env python3

# usage: python3 pep2bib.py .

import glob
import os
import re
import sys
from pybtex.database import Entry, BibliographyData

from pep_parsing_helpers import pep_number, pep_creation_dt, first_line_starting_with, parse_authors

BIB_PATH = os.path.join(sys.argv[1], 'peps.bib')


name_first_regex = re.compile(r'(.*)<.*>')
mail_first_regex = re.compile(r'.*\((.*)\)')
name_only_regex = re.compile(r'(.*)')


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


def authors_to_bib(authors):
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
    # sort peps by number
    peps_with_dt.sort()

    items = {}
    for n, dt, full_path in peps_with_dt:
        title = first_line_starting_with(full_path, 'Title:')
        author_string = first_line_starting_with(full_path, 'Author:')
        authors = parse_authors(author_string)
        authors = authors_to_bib(authors)
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
