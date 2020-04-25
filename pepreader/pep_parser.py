from sphinx import parsers
from .pep_headers import PEPHeaders
from .pep_title import PEPTitle
from .pep_contents import PEPContents





class PEPParser(parsers.RSTParser):
    supported = ("pep", "python-enhancement-proposal")

    def __init__(self):
        super().__init__(rfc2822=True)

    def get_transforms(self):
        transforms = super().get_transforms()
        transforms.extend([
            PEPHeaders,
            PEPTitle,
            PEPContents,
        ])
        return transforms
