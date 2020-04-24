"""Docutils CommonMark parser"""
from sphinx.application import Sphinx

__version__ = '1.0.0'


def setup(app: Sphinx):
    """Initialize Sphinx extension."""
    from .pep_parser import PEPParser, PEPTitleCollector

    # app.add_env_collector(PEPTitleCollector)
    app.add_source_parser(PEPParser)

    return {'version': __version__, 'parallel_read_safe': True}