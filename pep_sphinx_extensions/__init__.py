"""Sphinx extensions for performant PEP processing"""

from __future__ import annotations

from typing import TYPE_CHECKING

from docutils.writers.html5_polyglot import HTMLTranslator
from sphinx import environment

from pep_sphinx_extensions.generate_rss import create_rss_feed
from pep_sphinx_extensions.pep_processor.html import pep_html_builder
from pep_sphinx_extensions.pep_processor.html import pep_html_translator
from pep_sphinx_extensions.pep_processor.parsing import pep_banner_directive
from pep_sphinx_extensions.pep_processor.parsing import pep_parser
from pep_sphinx_extensions.pep_processor.parsing import pep_role
from pep_sphinx_extensions.pep_processor.transforms import pep_references
from pep_sphinx_extensions.pep_zero_generator.pep_index_generator import create_pep_zero

if TYPE_CHECKING:
    from sphinx.application import Sphinx


def _update_config_for_builder(app: Sphinx) -> None:
    app.env.document_ids = {}  # For PEPReferenceRoleTitleText
    app.env.settings["builder"] = app.builder.name
    if app.builder.name == "dirhtml":
        app.env.settings["pep_url"] = "pep-{:0>4}/"

    app.connect("build-finished", _post_build)  # Post-build tasks


def _post_build(app: Sphinx, exception: Exception | None) -> None:
    from pathlib import Path

    from build import create_index_file

    if exception is not None:
        return

    # internal_builder exists if Sphinx is run by build.py
    if "internal_builder" not in app.tags:
        create_index_file(Path(app.outdir), app.builder.name)
    create_rss_feed(app.doctreedir, app.outdir)


def setup(app: Sphinx) -> dict[str, bool]:
    """Initialize Sphinx extension."""

    environment.default_settings["pep_url"] = "pep-{:0>4}.html"
    environment.default_settings["halt_level"] = 2  # Fail on Docutils warning

    # Register plugin logic
    app.add_builder(pep_html_builder.FileBuilder, override=True)
    app.add_builder(pep_html_builder.DirectoryBuilder, override=True)

    app.add_source_parser(pep_parser.PEPParser)  # Add PEP transforms

    app.set_translator("html", pep_html_translator.PEPTranslator)  # Docutils Node Visitor overrides (html builder)
    app.set_translator("dirhtml", pep_html_translator.PEPTranslator)  # Docutils Node Visitor overrides (dirhtml builder)

    app.add_role("pep", pep_role.PEPRole(), override=True)  # Transform PEP references to links

    app.add_post_transform(pep_references.PEPReferenceRoleTitleText)

    # Register custom directives
    app.add_directive(
        "pep-banner", pep_banner_directive.PEPBanner)
    app.add_directive(
        "canonical-doc", pep_banner_directive.CanonicalDocBanner)
    app.add_directive(
        "canonical-pypa-spec", pep_banner_directive.CanonicalPyPASpecBanner)
    app.add_directive(
        "canonical-typing-spec", pep_banner_directive.CanonicalTypingSpecBanner)
    app.add_directive("rejected", pep_banner_directive.RejectedBanner)
    app.add_directive("superseded", pep_banner_directive.SupersededBanner)
    app.add_directive("withdrawn", pep_banner_directive.WithdrawnBanner)

    # Register event callbacks
    app.connect("builder-inited", _update_config_for_builder)  # Update configuration values for builder used
    app.connect("env-before-read-docs", create_pep_zero)  # PEP 0 hook

    # Mathematics rendering
    inline_maths = HTMLTranslator.visit_math, None
    block_maths = HTMLTranslator.visit_math_block, None
    app.add_html_math_renderer("maths_to_html", inline_maths, block_maths)  # Render maths to HTML

    # Parallel safety: https://www.sphinx-doc.org/en/master/extdev/index.html#extension-metadata
    return {"parallel_read_safe": True, "parallel_write_safe": True}
