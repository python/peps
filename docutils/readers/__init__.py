# Authors: David Goodger; Ueli Schlaepfer
# Contact: goodger@users.sourceforge.net
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
This package contains Docutils Reader modules.
"""

__docformat__ = 'reStructuredText'


import sys
from docutils import utils, parsers, Component
from docutils.transforms import universal


class Reader(Component):

    """
    Abstract base class for docutils Readers.

    Each reader module or package must export a subclass also called 'Reader'.

    The three steps of a Reader's responsibility are defined: `scan()`,
    `parse()`, and `transform()`. Call `read()` to process a document.
    """

    component_type = 'reader'

    def __init__(self, parser=None, parser_name='restructuredtext'):
        """
        Initialize the Reader instance.

        Several instance attributes are defined with dummy initial values.
        Subclasses may use these attributes as they wish.
        """

        self.parser = parser
        """A `parsers.Parser` instance shared by all doctrees.  May be left
        unspecified if the document source determines the parser."""

        if parser is None and parser_name:
            self.set_parser(parser_name)

        self.source = None
        """`docutils.io` IO object, source of input data."""

        self.input = None
        """Raw text input; either a single string or, for more complex cases,
        a collection of strings."""

    def set_parser(self, parser_name):
        """Set `self.parser` by name."""
        parser_class = parsers.get_parser_class(parser_name)
        self.parser = parser_class()

    def read(self, source, parser, settings):
        self.source = source
        if not self.parser:
            self.parser = parser
        self.settings = settings
        self.input = self.source.read()
        self.parse()
        return self.document

    def parse(self):
        """Parse `self.input` into a document tree."""
        self.document = document = self.new_document()
        self.parser.parse(self.input, document)
        document.current_source = document.current_line = None

    def new_document(self):
        """Create and return a new empty document tree (root node)."""
        document = utils.new_document(self.source.source_path, self.settings)
        return document


_reader_aliases = {}

def get_reader_class(reader_name):
    """Return the Reader class from the `reader_name` module."""
    reader_name = reader_name.lower()
    if _reader_aliases.has_key(reader_name):
        reader_name = _reader_aliases[reader_name]
    module = __import__(reader_name, globals(), locals())
    return module.Reader
