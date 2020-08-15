"""Sphinx extensions for performant PEP processing"""
import sphinx.builders.html
from sphinx.application import Sphinx
from sphinx.environment import default_settings
from docutils.writers.html5_polyglot import HTMLTranslator

from pep_extensions.config import __version__

# Monkeypatch sphinx.environment.default_settings as Sphinx doesn't allow custom settings or Readers
default_settings.update({
    'pep_references': True,
    'rfc_references': True,
    "pep_base_url": "",
    "pep_file_url_template": "pep-%04d.html"
})


# Monkeypatch StandaloneHTMLBuilder to not include JS libraries (underscore.js & jQuery)
def init_less_js(self) -> None:
    js_files = [('js/doctools.js', {}), ('js/language_data.js', {})]
    js_files.extend([*self.app.registry.js_files, *self.get_builder_config('js_files', 'html')])
    if self.config.language and self._get_translations_js():
        js_files.append(('translations.js',))
    for filename, attrs in js_files:
        self.add_js_file(filename, **attrs)


sphinx.builders.html.StandaloneHTMLBuilder.init_js_files = init_less_js


def setup(app: Sphinx) -> dict:
    """Initialize Sphinx extension."""

    # Mathematics rendering
    def depart_maths(): pass  # Type checker wants a callable
    inline_maths = (HTMLTranslator.visit_math, depart_maths)
    block_maths = (HTMLTranslator.visit_math_block, depart_maths)
    app.add_html_math_renderer('math2html', inline_maths, block_maths)  # Render maths to HTML

    return {'version': __version__, 'parallel_read_safe': True, 'parallel_write_safe': True}
