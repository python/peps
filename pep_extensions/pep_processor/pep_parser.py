from sphinx import parsers

from pep_extensions.pep_processor import pep_headers
from pep_extensions.pep_processor import pep_title
from pep_extensions.pep_processor import pep_contents
from pep_extensions.pep_processor import pep_footer


class PEPParser(parsers.RSTParser):
    supported = ("pep", "python-enhancement-proposal")

    def __init__(self):
        super().__init__(rfc2822=True)

    def get_transforms(self):
        transforms = super().get_transforms()
        transforms.extend([
            pep_headers.PEPHeaders,
            pep_title.PEPTitle,
            pep_contents.PEPContents,
            pep_footer.PEPFooter,
        ])
        return transforms
