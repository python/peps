"""Sphinx extensions for performant PEP processing"""
from sphinx.application import Sphinx

__version__ = '1.0.0'
pep_url = "pep-{:0>4}.html"


def setup(app: Sphinx):
    """Initialize Sphinx extension."""
    from .pep_parser import PEPParser
    from .generate_pep_index import create_pep_zero
    from .pep_role import PEPRole

    app.connect("env-before-read-docs", create_pep_zero)
    app.add_source_parser(PEPParser)
    app.add_role('pep', PEPRole(), override=True)

    return {'version': __version__, 'parallel_read_safe': True, 'parallel_write_safe': True}
