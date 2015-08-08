#!/usr/bin/env python
"""Auto-generate PEP 0 (PEP index).

Generating the PEP index is a multi-step process.  To begin, you must first
parse the PEP files themselves, which in and of itself takes a couple of steps:

    1. Parse metadata.
    2. Validate metadata.

With the PEP information collected, to create the index itself you must:

    1. Output static text.
    2. Format an entry for the PEP.
    3. Output the PEP (both by category and numerical index).

"""
from __future__ import absolute_import, with_statement
from __future__ import print_function

import sys
import os
import codecs

from operator import attrgetter

from pep0.output import write_pep0
from pep0.pep import PEP, PEPError


def main(argv):
    if not argv[1:]:
        path = '.'
    else:
        path = argv[1]

    peps = []
    if os.path.isdir(path):
        for file_path in os.listdir(path):
            if file_path == 'pep-0000.txt':
                continue
            abs_file_path = os.path.join(path, file_path)
            if not os.path.isfile(abs_file_path):
                continue
            if file_path.startswith("pep-") and file_path.endswith(".txt"):
                with codecs.open(abs_file_path, 'r', encoding='UTF-8') as pep_file:
                    try:
                        pep = PEP(pep_file)
                        if pep.number != int(file_path[4:-4]):
                            raise PEPError('PEP number does not match file name',
                                           file_path, pep.number)
                        peps.append(pep)
                    except PEPError as e:
                        errmsg = "Error processing PEP %s (%s), excluding:" % \
                            (e.number, e.filename)
                        print(errmsg, e, file=sys.stderr)
                        sys.exit(1)
        peps.sort(key=attrgetter('number'))
    elif os.path.isfile(path):
        with open(path, 'r') as pep_file:
            peps.append(PEP(pep_file))
    else:
        raise ValueError("argument must be a directory or file path")

    with codecs.open('pep-0000.txt', 'w', encoding='UTF-8') as pep0_file:
        write_pep0(peps, pep0_file)

if __name__ == "__main__":
    main(sys.argv)
