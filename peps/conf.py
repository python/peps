# This file is placed in the public domain or under the
# CC0-1.0-Universal license, whichever is more permissive.

"""Configuration for building PEPs using Sphinx."""

import os
from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(os.fspath(_ROOT))

# -- Project information -----------------------------------------------------

project = "PEPs"
master_doc = "contents"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings.
extensions = [
    "pep_sphinx_extensions",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.githubpages",
]

# The file extensions of source files. Sphinx uses these suffixes as sources.
source_suffix = {
    ".rst": "pep",
}

# List of patterns (relative to source dir) to ignore when looking for source files.
include_patterns = [
    # Required for Sphinx
    "contents.rst",
    # PEP files
    "pep-????.rst",
    # PEP ancillary files
    "pep-????/*.rst",
    # Documentation
    "docs/*.rst",
]
exclude_patterns = [
    # PEP Template
    "pep-0012/pep-NNNN.rst",
]

# Warn on missing references
nitpicky = True

# Intersphinx configuration
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'packaging': ('https://packaging.python.org/en/latest/', None),
    'typing': ('https://typing.readthedocs.io/en/latest/', None),
    'devguide': ('https://devguide.python.org/', None),
    'py3.11': ('https://docs.python.org/3.11/', None),
    'py3.12': ('https://docs.python.org/3.12/', None),
}
intersphinx_disabled_reftypes = []

# sphinx.ext.extlinks
# This config is a dictionary of external sites,
# mapping unique short aliases to a base URL and a prefix.
# https://www.sphinx-doc.org/en/master/usage/extensions/extlinks.html
extlinks = {
    "pypi": ("https://pypi.org/project/%s/", "%s"),
}

# -- Options for HTML output -------------------------------------------------

_PSE_PATH = _ROOT / "pep_sphinx_extensions"

# HTML output settings
html_math_renderer = "maths_to_html"  # Maths rendering

# Theme settings
html_theme_path = [os.fspath(_PSE_PATH)]
html_theme = "pep_theme"  # The actual theme directory (child of html_theme_path)
html_use_index = False  # Disable index (we use PEP 0)
html_style = ""  # must be defined here or in theme.conf, but is unused
html_permalinks = False  # handled in the PEPContents transform
html_baseurl = "https://peps.python.org"  # to create the CNAME file
gettext_auto_build = False  # speed-ups

templates_path = [os.fspath(_PSE_PATH / "pep_theme" / "templates")]  # Theme template relative paths from `confdir`
