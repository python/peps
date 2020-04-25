"""Docutils CommonMark parser"""
from sphinx.application import Sphinx

__version__ = '1.0.0'


def setup(app: Sphinx):
    """Initialize Sphinx extension."""
    from .pep_parser import PEPParser
    from .generate_pep_index import create_pep_zero

    app.add_source_parser(PEPParser)

    return {'version': __version__, 'parallel_read_safe': True}