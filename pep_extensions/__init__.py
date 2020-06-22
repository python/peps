"""Sphinx extensions for performant PEP processing"""
import sphinx.builders.html
from sphinx.application import Sphinx
from docutils.writers.html5_polyglot import HTMLTranslator

from pep_extensions.config import __version__
from pep_extensions.pep_processor.html import pep_html_translator
from pep_extensions.pep_processor.parsing import pep_parser
from pep_extensions.pep_processor.parsing import pep_role
from pep_extensions.pep_zero_generator.pep_index_generator import create_pep_zero


# Monkeypatch StandaloneHTMLBuilder to not include JS libraries (underscore.js & jQuery)
def init_less_js(self) -> None:
    js_files = [('js/doctools.js', {}), ('js/language_data.js', {}), ]
    js_files.extend([*self.app.registry.js_files, *self.get_builder_config('js_files', 'html')])
    js_files.append(('translations.js',) if self.config.language and self._get_translations_js() else (None, {}))
    for filename, attrs in js_files:
        self.add_js_file(filename, **attrs)


sphinx.builders.html.StandaloneHTMLBuilder.init_js_files = init_less_js


def setup(app: Sphinx) -> dict:
    """Initialize Sphinx extension."""

    app.add_source_parser(pep_parser.PEPParser)
    app.add_role('pep', pep_role.PEPRole(), override=True)
    app.set_translator("html", pep_html_translator.PEPTranslator)
    app.connect("env-before-read-docs", create_pep_zero)
    app.add_html_math_renderer('math2html', (HTMLTranslator.visit_math, None), (HTMLTranslator.visit_math_block, None))  # NoQA

    return {'version': __version__, 'parallel_read_safe': True, 'parallel_write_safe': True}
