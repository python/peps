"""Sphinx extensions for performant PEP processing"""
import sphinx.builders.html
from sphinx.application import Sphinx
from sphinx.environment import default_settings
from docutils.writers.html5_polyglot import HTMLTranslator

from pep_extensions.config import __version__
from pep_extensions.pep_processor.html import pep_html_translator
from pep_extensions.pep_processor.parsing import pep_parser
from pep_extensions.pep_processor.parsing import pep_role

# Monkeypatch sphinx.environment.default_settings as Sphinx doesn't allow custom settings or Readers
default_settings.update({
    'pep_references': True,
    'rfc_references': True,
    "pep_base_url": "",
    "pep_file_url_template": "pep-%04d.html"
})


def setup(app: Sphinx) -> dict:
    """Initialize Sphinx extension."""

    app.add_source_parser(pep_parser.PEPParser)  # Add PEP transforms
    app.add_role('pep', pep_role.PEPRole(), override=True)  # Transform PEP references to links
    app.set_translator("html", pep_html_translator.PEPTranslator)  # Docutils Node Visitor overrides

    # Mathematics rendering
    def depart_maths(): pass  # Type checker wants a callable
    inline_maths = (HTMLTranslator.visit_math, depart_maths)
    block_maths = (HTMLTranslator.visit_math_block, depart_maths)
    app.add_html_math_renderer('math2html', inline_maths, block_maths)  # Render maths to HTML

    return {'version': __version__, 'parallel_read_safe': True, 'parallel_write_safe': True}
