# Authors: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
This package contains Docutils Writer modules.
"""

__docformat__ = 'reStructuredText'


import sys
import docutils
from docutils import languages, Component
from docutils.transforms import universal


class Writer(Component):

    """
    Abstract base class for docutils Writers.

    Each writer module or package must export a subclass also called 'Writer'.
    Each writer must support all standard node types listed in
    `docutils.nodes.node_class_names`.

    Call `write()` to process a document.
    """

    component_type = 'writer'

    document = None
    """The document to write."""

    language = None
    """Language module for the document."""

    destination = None
    """`docutils.io` IO object; where to write the document."""

    def __init__(self):
        """Initialize the Writer instance."""

    def write(self, document, destination):
        self.document = document
        self.language = languages.get_language(
            document.settings.language_code)
        self.destination = destination
        self.translate()
        output = self.destination.write(self.output)
        return output

    def translate(self):
        """
        Override to do final document tree translation.

        This is usually done with a `docutils.nodes.NodeVisitor` subclass, in
        combination with a call to `docutils.nodes.Node.walk()` or
        `docutils.nodes.Node.walkabout()`.  The ``NodeVisitor`` subclass must
        support all standard elements (listed in
        `docutils.nodes.node_class_names`) and possibly non-standard elements
        used by the current Reader as well.
        """
        raise NotImplementedError('subclass must override this method')


_writer_aliases = {
      'html': 'html4css1',
      'pprint': 'pseudoxml',
      'pformat': 'pseudoxml',
      'pdf': 'rlpdf',
      'xml': 'docutils_xml',}

def get_writer_class(writer_name):
    """Return the Writer class from the `writer_name` module."""
    writer_name = writer_name.lower()
    if _writer_aliases.has_key(writer_name):
        writer_name = _writer_aliases[writer_name]
    module = __import__(writer_name, globals(), locals())
    return module.Writer
