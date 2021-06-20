"""Sphinx extensions for performant PEP processing"""

from __future__ import annotations

from typing import TYPE_CHECKING

from docutils.writers.html5_polyglot import HTMLTranslator
from sphinx.environment import BuildEnvironment
from sphinx.environment import default_settings

from pep_sphinx_extensions import config
from pep_sphinx_extensions.pep_processor.html import pep_html_translator
from pep_sphinx_extensions.pep_processor.parsing import pep_parser
from pep_sphinx_extensions.pep_processor.parsing import pep_role
from pep_sphinx_extensions.pep_zero_generator.pep_index_generator import create_pep_zero

if TYPE_CHECKING:
    from sphinx.application import Sphinx

# Monkeypatch sphinx.environment.default_settings as Sphinx doesn't allow custom settings or Readers
# These settings should go in docutils.conf, but are overridden here for now so as not to affect
# pep2html.py
default_settings |= {
    "pep_references": True,
    "rfc_references": True,
    "pep_base_url": "",
    "pep_file_url_template": "pep-%04d.html",
    "_disable_config": True,  # disable using docutils.conf whilst running both PEP generators
}

# Monkeypatch sphinx.environment.BuildEnvironment.collect_relations, as it takes a long time
# and we don't use the parent/next/prev functionality
BuildEnvironment.collect_relations = lambda self: {}


def _depart_maths():
    pass  # No-op callable for the type checker


def _update_config_for_builder(app: Sphinx):
    if app.builder.name == "dirhtml":
        # Docutils Node Visitor overrides (dirhtml builder)
        app.set_translator("dirhtml", pep_html_translator.PEPTranslator)

        # PEP url overrides
        config.pep_url = f"../{config.pep_stem}"
        app.env.settings["pep_file_url_template"] = "../pep-%04d"
    elif app.builder.name == "epub":
        # Docutils Node Visitor overrides (epub builder)
        app.set_translator("epub", pep_html_translator.PEPTranslator)


def setup(app: Sphinx) -> dict[str, bool]:
    """Initialize Sphinx extension."""

    # Register plugin logic
    app.add_source_parser(pep_parser.PEPParser)  # Add PEP transforms
    app.add_role("pep", pep_role.PEPRole(), override=True)  # Transform PEP references to links
    app.set_translator("html", pep_html_translator.PEPTranslator)  # Docutils Node Visitor overrides (html builder)
    app.connect("env-before-read-docs", create_pep_zero)  # PEP 0 hook
    app.connect("builder-inited", _update_config_for_builder)  # Update configuration values for builder used

    # Mathematics rendering
    inline_maths = HTMLTranslator.visit_math, _depart_maths
    block_maths = HTMLTranslator.visit_math_block, _depart_maths
    app.add_html_math_renderer("maths_to_html", inline_maths, block_maths)  # Render maths to HTML

    # Parallel safety: https://www.sphinx-doc.org/en/master/extdev/index.html#extension-metadata
    return {"parallel_read_safe": True, "parallel_write_safe": True}
