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
import os
from pathlib import Path
from typing import TYPE_CHECKING

from pep_sphinx_extensions.pep_zero_generator import parser
from pep_sphinx_extensions.pep_zero_generator import subindices
from pep_sphinx_extensions.pep_zero_generator import writer
from pep_sphinx_extensions.pep_zero_generator.constants import SUBINDICES_BY_TOPIC

if TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment


def _parse_peps(path: Path) -> list[parser.PEP]:
    # Read from root directory
    peps: list[parser.PEP] = []

    for file_path in path.iterdir():
        if not file_path.is_file():
            continue  # Skip directories etc.
        if file_path.match("pep-0000*"):
            continue  # Skip pre-existing PEP 0 files
        if file_path.match("pep-????.rst"):
            pep = parser.PEP(path.joinpath(file_path).absolute())
            peps.append(pep)

    return sorted(peps)


def create_pep_json(peps: list[parser.PEP]) -> str:
    return json.dumps({pep.number: pep.full_details for pep in peps}, indent=1)


def write_peps_json(peps: list[parser.PEP], path: Path) -> None:
    # Create peps.json
    json_peps = create_pep_json(peps)
    Path(path, "peps.json").write_text(json_peps, encoding="utf-8")
    os.makedirs(os.path.join(path, "api"), exist_ok=True)
    Path(path, "api", "peps.json").write_text(json_peps, encoding="utf-8")


def create_pep_zero(app: Sphinx, env: BuildEnvironment, docnames: list[str]) -> None:
    peps = _parse_peps(Path(app.srcdir))

    numerical_index_text = writer.PEPZeroWriter().write_numerical_index(peps)
    subindices.update_sphinx("numerical", numerical_index_text, docnames, env)

    pep0_text = writer.PEPZeroWriter().write_pep0(peps, builder=env.settings["builder"])
    pep0_path = subindices.update_sphinx("pep-0000", pep0_text, docnames, env)
    peps.append(parser.PEP(pep0_path))

    subindices.generate_subindices(SUBINDICES_BY_TOPIC, peps, docnames, env)

    write_peps_json(peps, Path(app.outdir))
