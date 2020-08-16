# Configuration file for the Sphinx documentation builder.

# -- Path setup --------------------------------------------------------------

import sys
from pathlib import Path
sys.path.extend(str(Path('./pep_extensions').absolute()))

# -- Project information -----------------------------------------------------

project = 'PEPs'
master_doc = 'contents'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings.
extensions = ["pep_extensions", "sphinx.ext.githubpages"]

# The file extensions of source files. Sphinx uses these suffixes as sources.
source_suffix = {
    '.rst': 'pep',
    '.txt': 'pep',
}

# List of patterns (relative to source dir) to ignore when looking for source files.
exclude_patterns = [
    # Windows:
    'Thumbs.db',
    '.DS_Store',
    # Python:
    'venv',
    'requirements.txt',
    # Sphinx:
    'build',
    "output.txt",  # Linkcheck output
    # Project:
    'README.rst',
    'CONTRIBUTING.rst',
]

# -- Options for HTML output -------------------------------------------------

# HTML output settings
html_math_renderer = "math2html"
html_show_copyright = False
html_show_sphinx = False
html_title = "peps.python.org"
