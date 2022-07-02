"""Automatically create PEP 0 (the PEP index),

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
from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from pep_sphinx_extensions.pep_zero_generator.constants import SUBINDICES_BY_TOPIC
from pep_sphinx_extensions.pep_zero_generator import parser
from pep_sphinx_extensions.pep_zero_generator import subindices
from pep_sphinx_extensions.pep_zero_generator import writer

if TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment


def _parse_peps() -> list[parser.PEP]:
    # Read from root directory
    path = Path(".")
    peps: list[parser.PEP] = []

    for file_path in path.iterdir():
        if not file_path.is_file():
            continue  # Skip directories etc.
        if file_path.match("pep-0000*"):
            continue  # Skip pre-existing PEP 0 files
        if file_path.match("pep-????.???") and file_path.suffix in {".txt", ".rst"}:
            pep = parser.PEP(path.joinpath(file_path).absolute())
            peps.append(pep)

    return sorted(peps)


def create_pep_json(peps: list[parser.PEP]) -> str:
    return json.dumps({pep.number: pep.full_details for pep in peps}, indent=1)


def create_pep_zero(app: Sphinx, env: BuildEnvironment, docnames: list[str]) -> None:
    peps = _parse_peps()

    pep0_text = writer.PEPZeroWriter().write_pep0(peps)
    pep0_path = subindices.update_sphinx("pep-0000", pep0_text, docnames, env)
    peps.append(parser.PEP(pep0_path))

    subindices.generate_subindices(SUBINDICES_BY_TOPIC, peps, docnames, env)

    # Create peps.json
    json_path = Path(app.outdir, "api", "peps.json").resolve()
    json_path.parent.mkdir(exist_ok=True)
    json_path.write_text(create_pep_json(peps), encoding="utf-8")
