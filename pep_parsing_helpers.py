import re
import datetime
import time


def first_line_starting_with(full_path, text):
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
    created_str = first_line_starting_with(full_path, 'Created:')
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


def parse_authors(authors_str):
    orig_authors = authors_str.split(',')
    authors = []
    for author in orig_authors:
        authors.append(author.strip())

    return authors


