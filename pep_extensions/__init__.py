"""Sphinx extensions for performant PEP processing"""
from sphinx.application import Sphinx
from docutils.writers.html5_polyglot import HTMLTranslator

from pep_extensions.config import __version__
from pep_extensions.pep_processor import pep_html_translator
from pep_extensions.pep_processor import pep_parser
from pep_extensions.pep_processor import pep_role
from pep_extensions.pepzero.generate_pep_index import create_pep_zero


def setup(app: Sphinx):
    """Initialize Sphinx extension."""

    app.add_source_parser(pep_parser.PEPParser)
    app.add_role('pep', pep_role.PEPRole(), override=True)
    app.set_translator("html", pep_html_translator.PEPTranslator)
    app.connect("env-before-read-docs", create_pep_zero)
    app.add_html_math_renderer('math2html', (HTMLTranslator.visit_math, None), (HTMLTranslator.visit_math_block, None))  # NoQA

    return {'version': __version__, 'parallel_read_safe': True, 'parallel_write_safe': True}
