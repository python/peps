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
    docnames.append(filename)
    # Add to files for writer
    env.found_docs.add(filename)

    return file_path


def generate_subindices(
    subindices: dict[str, str],
    peps: list[PEP],
    docnames: list[str],
    env: BuildEnvironment,
) -> None:
    # Create sub index page
    generate_topic_contents(docnames, env)

    for subindex, additional_description in subindices.items():
        header_text = f"{subindex.title()} PEPs"
        header_line = "#" * len(header_text)
        header = header_text + "\n" + header_line + "\n"

        topic = subindex.lower()
        filtered_peps = [pep for pep in peps if topic in pep.topic]
        subindex_intro = f"""\
This is the index of all Python Enhancement Proposals (PEPs) labelled
under the '{subindex.title()}' topic. This is a sub-index of :pep:`0`,
the PEP index.

{additional_description}
"""
        subindex_text = writer.PEPZeroWriter().write_pep0(
            filtered_peps, header, subindex_intro, is_pep0=False,
        )
        update_sphinx(f"topic/{subindex}", subindex_text, docnames, env)


def generate_topic_contents(docnames: list[str], env: BuildEnvironment):
    update_sphinx("topic/index", """\
Topic Index
***********

PEPs are indexed by topic on the pages below:

.. toctree::
   :maxdepth: 1
   :titlesonly:
   :glob:

   *
""", docnames, env)
