"""Sphinx extensions for performant PEP processing"""

from __future__ import annotations

from typing import TYPE_CHECKING

from docutils.writers.html5_polyglot import HTMLTranslator
from sphinx import environment
from sphinx import project

from pep_sphinx_extensions.pep_processor.html import pep_html_builder
from pep_sphinx_extensions.pep_processor.html import pep_html_translator
from pep_sphinx_extensions.pep_processor.parsing import pep_canonical_content_directive
from pep_sphinx_extensions.pep_processor.parsing import pep_parser
from pep_sphinx_extensions.pep_processor.parsing import pep_role
from pep_sphinx_extensions.pep_processor.transforms import pep_references
from pep_sphinx_extensions.pep_zero_generator.pep_index_generator import create_pep_zero

if TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.config import Config


def find_files(self: environment.BuildEnvironment, config: Config, _b) -> None:
    """Find all pep source files."""
    import fnmatch
    from pathlib import Path

    root = Path(self.project.srcdir).absolute()
    self.project.docnames = set()
    for pattern in config.include_patterns:
        for path in root.glob(pattern):
            filename = str(path.relative_to(root))
            if any(fnmatch.fnmatch(filename, pattern) for pattern in config.exclude_patterns):
                continue

            doc_name = self.project.path2doc(filename)
            if not doc_name:
                continue

            if doc_name not in self.project.docnames:
                self.project.docnames.add(doc_name)
                continue

            other_files = [str(f.relative_to(root)) for f in root.glob(f"{doc_name}.*")]
            project.logger.warning(
                f'multiple files found for the document "{doc_name}": {other_files!r}\n'
                f'Use {self.doc2path(doc_name)!r} for the build.', once=True)


environment.BuildEnvironment.find_files = find_files


def _depart_maths():
    pass  # No-op callable for the type checker


def _update_config_for_builder(app: Sphinx) -> None:
    app.env.document_ids = {}  # For PEPReferenceRoleTitleText
    if app.builder.name == "dirhtml":
        app.env.settings["pep_url"] = "/pep-{:0>4}"

    # internal_builder exists if Sphinx is run by build.py
    if "internal_builder" not in app.tags:
        app.connect("build-finished", _post_build)  # Post-build tasks


def _post_build(app: Sphinx, exception: Exception | None) -> None:
    from pathlib import Path

    from build import create_index_file

    if exception is not None:
        return
    create_index_file(Path(app.outdir), app.builder.name)


def setup(app: Sphinx) -> dict[str, bool]:
    """Initialize Sphinx extension."""

    environment.default_settings["pep_url"] = "/pep-{:0>4}.html"
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
        'canonical-content', pep_canonical_content_directive.CanonicalContent)
    app.add_directive(
        'canonical-content-pypa', pep_canonical_content_directive.CanonicalContentPyPA)

    # Register event callbacks
    app.connect("builder-inited", _update_config_for_builder)  # Update configuration values for builder used
    app.connect("env-before-read-docs", create_pep_zero)  # PEP 0 hook

    # Mathematics rendering
    inline_maths = HTMLTranslator.visit_math, _depart_maths
    block_maths = HTMLTranslator.visit_math_block, _depart_maths
    app.add_html_math_renderer("maths_to_html", inline_maths, block_maths)  # Render maths to HTML

    # Parallel safety: https://www.sphinx-doc.org/en/master/extdev/index.html#extension-metadata
    return {"parallel_read_safe": True, "parallel_write_safe": True}
