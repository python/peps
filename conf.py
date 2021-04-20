"""Configuration for building PEPs using Sphinx."""

import sys
from pathlib import Path

sys.path.append(str(Path("pep_sphinx_extensions").absolute()))

# -- Project information -----------------------------------------------------

project = "PEPs"
master_doc = "contents"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings.
extensions = ["pep_sphinx_extensions"]

# The file extensions of source files. Sphinx uses these suffixes as sources.
source_suffix = {
    ".rst": "pep",
    ".txt": "pep",
}

# List of patterns (relative to source dir) to ignore when looking for source files.
exclude_patterns = [
    # Windows:
    "Thumbs.db",
    ".DS_Store",
    # Python:
    "venv",
    "requirements.txt",
    # Sphinx:
    "build",
    "output.txt",  # Link-check output
    # PEPs:
    "README.rst",
    "CONTRIBUTING.rst",
]

# -- Options for HTML output -------------------------------------------------

# HTML output settings
html_math_renderer = "maths_to_html"  # Maths rendering
html_show_copyright = False  # Turn off miscellany
html_show_sphinx = False
html_title = "peps.python.org"  # Set <title/>
