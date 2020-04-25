from sphinx import parsers
from . import pep_headers
from . import pep_title
from . import pep_contents





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
        ])
        return transforms
