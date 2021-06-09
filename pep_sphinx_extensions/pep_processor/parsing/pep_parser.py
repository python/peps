from __future__ import annotations

from typing import TYPE_CHECKING

from sphinx import parsers

from pep_sphinx_extensions.pep_processor.transforms import pep_contents
from pep_sphinx_extensions.pep_processor.transforms import pep_footer
from pep_sphinx_extensions.pep_processor.transforms import pep_headers
from pep_sphinx_extensions.pep_processor.transforms import pep_title

if TYPE_CHECKING:
    from docutils import transforms


class PEPParser(parsers.RSTParser):
    """RST parser with custom PEP transforms."""

    supported = ("pep", "python-enhancement-proposal")  # for source_suffix in conf.py

    def __init__(self):
        """Mark the document as containing RFC 2822 headers."""
        super().__init__(rfc2822=True)

    def get_transforms(self) -> list[type[transforms.Transform]]:
        """Use our custom PEP transform rules."""
        return [
            pep_headers.PEPHeaders,
            pep_title.PEPTitle,
            pep_contents.PEPContents,
            pep_footer.PEPFooter,
        ]
