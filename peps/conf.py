# Configuration file for the Sphinx documentation builder.

# -- Path setup --------------------------------------------------------------

import docutils
from docutils.readers import standalone
from docutils.transforms import frontmatter, references, misc

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'peps'
copyright = '2020, AUTHNAME'
author = 'AUTHNAME'

# The full version, including alpha/beta/rc tags
release = '1.0.0'

html_title = "Python Enhancement Proposals (PEPs)"
html_short_title = "PEPs Home" #
html_show_copyright = False
html_show_sphinx = False

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["pepreader"]

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
    'CONTRIBUTING.rst'
]

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'classic'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']


def new_get_transforms(self):
    # Replicate result of standalone.Reader.get_transforms()
    transforms = docutils.readers.Reader.get_transforms(self) + [
        references.Substitutions,
        references.PropagateTargets,
        frontmatter.DocTitle,
        frontmatter.SectionSubTitle,
        frontmatter.DocInfo,
        references.AnonymousHyperlinks,
        references.IndirectHyperlinks,
        references.Footnotes,
        references.ExternalTargets,
        references.InternalTargets,
        references.DanglingReferences,
        misc.Transitions,
    ]

    # Explicitly remove these transforms, as we implement PEP-specific pre-processing
    # transforms.remove(frontmatter.DocTitle)
    # transforms.remove(frontmatter.SectionSubTitle)
    transforms.remove(frontmatter.DocInfo)

    return transforms


standalone.Reader.get_transforms = new_get_transforms
