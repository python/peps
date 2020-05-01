"""Automatically create PEP 0 (the PEP index)

This file generates and writes the PEP index to disk, ready for later
processing by Sphinx. Firstly, we parse the individual PEP files, getting the
RFC2822 header, and parsing and then validating that metadata.

After collecting and validating all the PEP data, the creation of the index
itself is in three steps:

    1. Output static text.
    2. Format an entry for the PEP.
    3. Output the PEP (both by the category and numerical index).

We then add the newly created PEP 0 file to two Sphinx environment variables
to allow it to be processed as normal.

"""
import re
import csv
from operator import attrgetter
from pathlib import Path

from . import pep0
from . import pep0_writer


def create_pep_zero(_, env, docnames):
    # app is unneeded by this function

    # Read from root directory
    path = Path('.')

    pep_zero_filename = 'pep-0000'
    peps = []
    pep_pat = re.compile(r"pep-\d{4}")  # Path.match() doesn't support regular expressions

    with open("AUTHORS.csv", "r", encoding="UTF8") as f:
        read = csv.DictReader(f, quotechar='"', skipinitialspace=True)
        author_data = {}
        for line in read:
            full_name = line.pop("Full Name").strip().strip("\"")
            details = {k.strip().strip("\""): v.strip().strip("\"") for k, v in line.items()}
            author_data[full_name] = details

    for file_path in path.iterdir():
        if not file_path.is_file():
            continue  # Skip directories etc.
        if file_path.match('pep-0000*'):
            continue  # Skip pre-existing PEP 0 files
        if pep_pat.match(str(file_path)) and file_path.suffix in (".txt", ".rst"):
            file_path_absolute = path.joinpath(file_path).absolute()
            pep_text = file_path_absolute.read_text("UTF8")
            pep = pep0.PEP(pep_text, file_path_absolute, author_data)
            if pep.number != int(file_path.stem[4:]):
                raise pep0.PEPError(f'PEP number does not match file name ({file_path})', file_path, pep.number)
            peps.append(pep)
    peps.sort(key=attrgetter('number'))

    pep_writer = pep0_writer.PEPZeroWriter()
    pep0_text = pep_writer.write_pep0(peps)
    with open(pep_zero_filename + ".rst", 'w', encoding='UTF-8') as pep0_file:
        pep0_file.write(pep0_text)

    # Add to files for builder
    docnames.insert(1, pep_zero_filename)
    # Add to files for writer
    env.found_docs.add(pep_zero_filename)
