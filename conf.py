"""Configuration for building PEPs using Sphinx."""

from pathlib import Path
import sys

sys.path.append(str(Path("pep_sphinx_extensions").absolute()))

# -- Project information -----------------------------------------------------

project = "PEPs"
master_doc = "contents"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings.
extensions = ["pep_sphinx_extensions", "sphinx.ext.githubpages"]

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
    ".venv",
    "venv",
    "requirements.txt",
    # Sphinx:
    "build",
    "output.txt",  # Link-check output
    # PEPs:
    "pep-0012",
    "README.rst",
    "CONTRIBUTING.rst",
]

# -- Options for HTML output -------------------------------------------------

# HTML output settings
html_math_renderer = "maths_to_html"  # Maths rendering
html_show_copyright = False  # Turn off miscellany
html_show_sphinx = False
html_title = "peps.python.org"  # Set <title/>

# Theme settings
html_theme_path = ["pep_sphinx_extensions"]
html_theme = "pep_theme"  # The actual theme directory (child of html_theme_path)
html_use_index = False  # Disable index (we use PEP 0)
html_sourcelink_suffix = ""  # Fix links to GitHub (don't append .txt)
html_style = ""  # must be defined here or in theme.conf, but is unused
html_permalinks = False  # handled in the PEPContents transform

templates_path = ['pep_sphinx_extensions/pep_theme/templates']  # Theme template relative paths from `confdir`
