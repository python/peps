"""Sphinx extensions for performant PEP processing"""
from sphinx.application import Sphinx

from pep_extensions.config import __version__
from pep_extensions.pep_zero_generator.pep_index_generator import create_pep_zero


def setup(app: Sphinx) -> dict:
    """Initialize Sphinx extension."""

    app.connect("env-before-read-docs", create_pep_zero)  # PEP 0 hook

    return {'version': __version__, 'parallel_read_safe': True, 'parallel_write_safe': True}
