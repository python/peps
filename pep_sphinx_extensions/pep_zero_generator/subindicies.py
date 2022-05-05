"""Utilities to support sub-indices for PEPs."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from pep_sphinx_extensions.pep_zero_generator import writer

if TYPE_CHECKING:
    from sphinx.environment import BuildEnvironment

    from pep_sphinx_extensions.pep_zero_generator.parser import PEP


def update_sphinx(filename: str, text: str, docnames: list[str], env: BuildEnvironment) -> Path:
    file_path = Path(f"{filename}.rst").resolve()
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(text, encoding="utf-8")

    # Add to files for builder
    docnames.insert(1, filename)
    # Add to files for writer
    env.found_docs.add(filename)

    return file_path


def generate_subindicies(
    subindicies: tuple[str],
    peps: list[PEP],
    docnames: list[str],
    env: BuildEnvironment
) -> None:
    for subindex in subindicies:
        header_text = f"{subindex.title()} PEPs"
        header_line = "#" * len(header_text)
        header = header_text + "\n" + header_line + "\n"

        topic = subindex.lower()
        filtered_peps = [pep for pep in peps if topic in pep.topics]
        subindex_intro = f"""\
This is the index of all Python Enhancement Proposals (PEPs) labelled
under the '{subindex.title()}' topic. This is a sub-index of :pep:`0`,
the PEP index.
"""
        subindex_text = writer.PEPZeroWriter().write_pep0(
            filtered_peps, header, subindex_intro, is_subindex=True,
        )
        update_sphinx(f"topic/{subindex}", subindex_text, docnames, env)
