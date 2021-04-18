"""Configuration for building PEPs using Sphinx."""

# -- Project information -----------------------------------------------------

project = "PEPs"
master_doc = "contents"

# -- General configuration ---------------------------------------------------

# The file extensions of source files. Sphinx uses these suffixes as sources.
source_suffix = {
    ".rst": "restructuredtext",
    ".txt": "restructuredtext",
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
html_show_copyright = False  # Turn off miscellany
html_show_sphinx = False
html_title = "peps.python.org"  # Set <title/>
