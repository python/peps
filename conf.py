# Configuration file for the Sphinx documentation builder.

# -- Path setup --------------------------------------------------------------

import sys
from pathlib import Path
sys.path.extend(str(Path('./pep_extensions').absolute()))

# -- Project information -----------------------------------------------------

project = 'PEPs'
copyright = '2020, PEP Authors'
author = 'PEP Authors'

master_doc = 'contents'

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings.
extensions = ["pep_extensions", "sphinx.ext.githubpages"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['pep_extensions/theme/templates']

# The file extensions of source files. Sphinx considers the files with
# these suffixes as sources.
source_suffix = {
    '.rst': 'pep',
    '.txt': 'pep',
}

# List of patterns, relative to source directory, to ignore when
# looking for source files.
exclude_patterns = [
    '_build',
    'Thumbs.db',
    '.DS_Store',
    'venv',
    'build',
    "_build",
    "_build-old",
    "package",
    'README.rst',
    'CONTRIBUTING.rst',
    'requirements.txt',
    "output.txt",
]

# -- Options for HTML output -------------------------------------------------

# HTML output settings
html_math_renderer = "math2html"
html_show_copyright = False
html_show_sphinx = False
html_title = "PEPs.Python.org"

# Theme settings
html_theme = "theme"
html_theme_path = ["pep_extensions"]
html_favicon = Path(html_theme_path[0], html_theme, "static/py.png").as_posix()
template_bridge = "pep_extensions.pep_processor.html.pep_jinja2.PEPTemplateLoader"
