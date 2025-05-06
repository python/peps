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
    "notfound.extension",
    "pep_sphinx_extensions",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.githubpages",
]

# The file extensions of source files. Sphinx uses these suffixes as sources.
source_suffix = {
    ".rst": "pep",
}

# List of patterns (relative to source dir) to include when looking for source files.
include_patterns = [
    # Required for Sphinx
    "contents.rst",
    # PEP files
    "pep-????.rst",
    # PEP ancillary files
    "pep-????/*.rst",
    # PEPs API
    "api/*.rst",
    # Documentation
    "docs/*.rst",
]
# And to ignore when looking for source files.
exclude_patterns = [
    # PEP Template
    "pep-0012/pep-NNNN.rst",
]

# Warn on missing references
nitpicky = True

nitpick_ignore = [
    # Standard C types
    ("c:type", "int8_t"),
    ("c:type", "uint8_t"),
    ("c:type", "int64_t"),
]
for role, name in list(nitpick_ignore):
    if role in ("c:type", "c:struct"):
        nitpick_ignore.append(("c:identifier", name))
del role, name

# Intersphinx configuration (keep this in alphabetical order)
intersphinx_mapping = {
    "devguide": ("https://devguide.python.org/", None),
    "mypy": ("https://mypy.readthedocs.io/en/latest/", None),
    "packaging": ("https://packaging.python.org/en/latest/", None),
    "py3.11": ("https://docs.python.org/3.11/", None),
    "py3.12": ("https://docs.python.org/3.12/", None),
    "py3.13": ("https://docs.python.org/3.13/", None),
    "py3.14": ("https://docs.python.org/3.14/", None),
    "python": ("https://docs.python.org/3/", None),
    "trio": ("https://trio.readthedocs.io/en/latest/", None),
    "typing": ("https://typing.python.org/en/latest/", None),
}
intersphinx_disabled_reftypes = []

# sphinx.ext.extlinks
# This config is a dictionary of external sites,
# mapping unique short aliases to a base URL and a prefix.
# https://www.sphinx-doc.org/en/master/usage/extensions/extlinks.html
extlinks = {
    "pypi": ("https://pypi.org/project/%s/", "%s"),
}

# sphinx-notfound-page
# https://sphinx-notfound-page.readthedocs.io/en/latest/faq.html#does-this-extension-work-with-github-pages
notfound_urls_prefix = None

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

# Theme template relative paths from `confdir`
templates_path = [os.fspath(_PSE_PATH / "pep_theme" / "templates")]
