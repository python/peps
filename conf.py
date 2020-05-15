# Configuration file for the Sphinx documentation builder.

# -- Path setup --------------------------------------------------------------


import sys
from pathlib import Path
sys.path.extend(str(Path('./pep_extensions').absolute()))


# -- Project information -----------------------------------------------------

project = 'PEPs'
copyright = '2020, PEP Authors'
author = 'PEP Authors'

# The full version, including alpha/beta/rc tags
# release = '1.0.0'

html_title = "Python Enhancement Proposals (PEPs)"
html_short_title = "PEPs Home"
html_show_copyright = False
html_show_sphinx = False

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["pep_extensions"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The file extensions of source files. Sphinx considers the files with
# these suffixes as sources.
source_suffix = {
    '.rst': 'pep',
    '.txt': 'pep',
}

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    '_build',
    'Thumbs.db',
    '.DS_Store',
    'venv',
    'build',
    'README.rst',
    'CONTRIBUTING.rst',
    'requirements.txt',
]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

html_theme = 'classic'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

master_doc = 'contents'
