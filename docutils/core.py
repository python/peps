# Authors: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
Calling the ``publish_*`` convenience functions (or instantiating a
`Publisher` object) with component names will result in default
behavior.  For custom behavior (setting component options), create
custom component objects first, and pass *them* to
``publish_*``/`Publisher`.
"""

__docformat__ = 'reStructuredText'

import sys
from docutils import Component
from docutils import frontend, io, readers, parsers, writers
from docutils.frontend import OptionParser, ConfigParser


class Publisher:

    """
    A facade encapsulating the high-level logic of a Docutils system.
    """

    def __init__(self, reader=None, parser=None, writer=None,
                 source=None, source_class=io.FileInput,
                 destination=None, destination_class=io.FileOutput,
                 settings=None):
        """
        Initial setup.  If any of `reader`, `parser`, or `writer` are not
        specified, the corresponding ``set_...`` method should be called with
        a component name (`set_reader` sets the parser as well).
        """

        self.reader = reader
        """A `readers.Reader` instance."""

        self.parser = parser
        """A `parsers.Parser` instance."""

        self.writer = writer
        """A `writers.Writer` instance."""

        self.source = source
        """The source of input data, an `io.Input` instance."""

        self.source_class = source_class
        """The class for dynamically created source objects."""

        self.destination = destination
        """The destination for docutils output, an `io.Output` instance."""

        self.destination_class = destination_class
        """The class for dynamically created destination objects."""

        self.settings = settings
        """An object containing Docutils settings as instance attributes.
        Set by `self.process_command_line()` or `self.get_settings()`."""

    def set_reader(self, reader_name, parser, parser_name):
        """Set `self.reader` by name."""
        reader_class = readers.get_reader_class(reader_name)
        self.reader = reader_class(parser, parser_name)
        self.parser = self.reader.parser

    def set_writer(self, writer_name):
        """Set `self.writer` by name."""
        writer_class = writers.get_writer_class(writer_name)
        self.writer = writer_class()

    def set_components(self, reader_name, parser_name, writer_name):
        if self.reader is None:
            self.set_reader(reader_name, self.parser, parser_name)
        if self.parser is None:
            if self.reader.parser is None:
                self.reader.set_parser(parser_name)
            self.parser = self.reader.parser
        if self.writer is None:
            self.set_writer(writer_name)

    def setup_option_parser(self, usage=None, description=None,
                            settings_spec=None, **defaults):
        #@@@ Add self.source & self.destination to components in future?
        option_parser = OptionParser(
            components=(settings_spec, self.parser, self.reader, self.writer),
            usage=usage, description=description)
        config = ConfigParser()
        config.read_standard_files()
        config_settings = config.get_section('options')
        frontend.make_paths_absolute(config_settings,
                                     option_parser.relative_path_settings)
        defaults.update(config_settings)
        option_parser.set_defaults(**defaults)
        return option_parser

    def get_settings(self, usage=None, description=None,
                     settings_spec=None, **defaults):
        """
        Set and return default settings (overrides in `defaults` keyword
        argument).

        Set components first (`self.set_reader` & `self.set_writer`).
        Explicitly setting `self.settings` disables command line option
        processing from `self.publish()`.
        """
        option_parser = self.setup_option_parser(usage, description,
                                                 settings_spec, **defaults)
        self.settings = option_parser.get_default_values()
        return self.settings

    def process_command_line(self, argv=None, usage=None, description=None,
                             settings_spec=None, **defaults):
        """
        Pass an empty list to `argv` to avoid reading `sys.argv` (the
        default).

        Set components first (`self.set_reader` & `self.set_writer`).
        """
        option_parser = self.setup_option_parser(usage, description,
                                                 settings_spec, **defaults)
        if argv is None:
            argv = sys.argv[1:]
        self.settings = option_parser.parse_args(argv)

    def set_io(self, source_path=None, destination_path=None):
        if self.source is None:
            self.set_source(source_path=source_path)
        if self.destination is None:
            self.set_destination(destination_path=destination_path)

    def set_source(self, source=None, source_path=None):
        if source_path is None:
            source_path = self.settings._source
        else:
            self.settings._source = source_path
        self.source = self.source_class(self.settings, source=source,
                                        source_path=source_path)

    def set_destination(self, destination=None, destination_path=None):
        if destination_path is None:
            destination_path = self.settings._destination
        else:
            self.settings._destination = destination_path
        self.destination = self.destination_class(
            self.settings, destination=destination,
            destination_path=destination_path)

    def apply_transforms(self, document):
        document.transformer.populate_from_components(
            (self.source, self.reader, self.reader.parser, self.writer,
             self.destination))
        document.transformer.apply_transforms()

    def publish(self, argv=None, usage=None, description=None,
                settings_spec=None, settings_overrides=None):
        """
        Process command line options and arguments (if `self.settings` not
        already set), run `self.reader` and then `self.writer`.  Return
        `self.writer`'s output.
        """
        if self.settings is None:
            self.process_command_line(argv, usage, description, settings_spec,
                                      **(settings_overrides or {}))
        elif settings_overrides:
            self.settings._update(settings_overrides, 'loose')
        self.set_io()
        document = self.reader.read(self.source, self.parser, self.settings)
        self.apply_transforms(document)
        output = self.writer.write(document, self.destination)
        if self.settings.dump_settings:
            from pprint import pformat
            print >>sys.stderr, '\n::: Runtime settings:'
            print >>sys.stderr, pformat(self.settings.__dict__)
        if self.settings.dump_internals:
            from pprint import pformat
            print >>sys.stderr, '\n::: Document internals:'
            print >>sys.stderr, pformat(document.__dict__)
        if self.settings.dump_transforms:
            from pprint import pformat
            print >>sys.stderr, '\n::: Transforms applied:'
            print >>sys.stderr, pformat(document.transformer.applied)
        if self.settings.dump_pseudo_xml:
            print >>sys.stderr, '\n::: Pseudo-XML:'
            print >>sys.stderr, document.pformat().encode(
                'raw_unicode_escape')
        return output


default_usage = '%prog [options] [<source> [<destination>]]'
default_description = ('Reads from <source> (default is stdin) and writes to '
                       '<destination> (default is stdout).')

def publish_cmdline(reader=None, reader_name='standalone',
                    parser=None, parser_name='restructuredtext',
                    writer=None, writer_name='pseudoxml',
                    settings=None, settings_spec=None,
                    settings_overrides=None, argv=None,
                    usage=default_usage, description=default_description):
    """
    Set up & run a `Publisher`.  For command-line front ends.

    Parameters:

    - `reader`: A `docutils.readers.Reader` object.
    - `reader_name`: Name or alias of the Reader class to be instantiated if
      no `reader` supplied.
    - `parser`: A `docutils.parsers.Parser` object.
    - `parser_name`: Name or alias of the Parser class to be instantiated if
      no `parser` supplied.
    - `writer`: A `docutils.writers.Writer` object.
    - `writer_name`: Name or alias of the Writer class to be instantiated if
      no `writer` supplied.
    - `settings`: Runtime settings object.
    - `settings_spec`: Extra settings specification; a `docutils.SettingsSpec`
      subclass.  Used only if no `settings` specified.
    - `settings_overrides`: A dictionary containing program-specific overrides
      of component settings.
    - `argv`: Command-line argument list to use instead of ``sys.argv[1:]``.
    - `usage`: Usage string, output if there's a problem parsing the command
      line.
    - `description`: Program description, output for the "--help" option
      (along with command-line option descriptions).
    """
    pub = Publisher(reader, parser, writer, settings=settings)
    pub.set_components(reader_name, parser_name, writer_name)
    pub.publish(argv, usage, description, settings_spec, settings_overrides)

def publish_file(source=None, source_path=None,
                 destination=None, destination_path=None,
                 reader=None, reader_name='standalone',
                 parser=None, parser_name='restructuredtext',
                 writer=None, writer_name='pseudoxml',
                 settings=None, settings_spec=None, settings_overrides=None):
    """
    Set up & run a `Publisher`.  For programmatic use with file-like I/O.

    Parameters:

    - `source`: A file-like object (must have "read" and "close" methods).
    - `source_path`: Path to the input file.  Opened if no `source` supplied.
      If neither `source` nor `source_path` are supplied, `sys.stdin` is used.
    - `destination`: A file-like object (must have "write" and "close"
      methods).
    - `destination_path`: Path to the input file.  Opened if no `destination`
      supplied.  If neither `destination` nor `destination_path` are supplied,
      `sys.stdout` is used.
    - `reader`: A `docutils.readers.Reader` object.
    - `reader_name`: Name or alias of the Reader class to be instantiated if
      no `reader` supplied.
    - `parser`: A `docutils.parsers.Parser` object.
    - `parser_name`: Name or alias of the Parser class to be instantiated if
      no `parser` supplied.
    - `writer`: A `docutils.writers.Writer` object.
    - `writer_name`: Name or alias of the Writer class to be instantiated if
      no `writer` supplied.
    - `settings`: Runtime settings object.
    - `settings_spec`: Extra settings specification; a `docutils.SettingsSpec`
      subclass.  Used only if no `settings` specified.
    - `settings_overrides`: A dictionary containing program-specific overrides
      of component settings.
    """
    pub = Publisher(reader, parser, writer, settings=settings)
    pub.set_components(reader_name, parser_name, writer_name)
    if settings is None:
        settings = pub.get_settings(settings_spec=settings_spec)
    if settings_overrides:
        settings._update(settings_overrides, 'loose')
    pub.set_source(source, source_path)
    pub.set_destination(destination, destination_path)
    pub.publish()

def publish_string(source, source_path=None, destination_path=None, 
                   reader=None, reader_name='standalone',
                   parser=None, parser_name='restructuredtext',
                   writer=None, writer_name='pseudoxml',
                   settings=None, settings_spec=None,
                   settings_overrides=None):
    """
    Set up & run a `Publisher`, and return the string output.
    For programmatic use with string I/O.

    For encoded string output, be sure to set the "output_encoding" setting to
    the desired encoding.  Set it to "unicode" for unencoded Unicode string
    output.

    Parameters:

    - `source`: An input string; required.  This can be an encoded 8-bit
      string (set the "input_encoding" setting to the correct encoding) or a
      Unicode string (set the "input_encoding" setting to "unicode").
    - `source_path`: Path to the file or object that produced `source`;
      optional.  Only used for diagnostic output.
    - `destination_path`: Path to the file or object which will receive the
      output; optional.  Used for determining relative paths (stylesheets,
      source links, etc.).
    - `reader`: A `docutils.readers.Reader` object.
    - `reader_name`: Name or alias of the Reader class to be instantiated if
      no `reader` supplied.
    - `parser`: A `docutils.parsers.Parser` object.
    - `parser_name`: Name or alias of the Parser class to be instantiated if
      no `parser` supplied.
    - `writer`: A `docutils.writers.Writer` object.
    - `writer_name`: Name or alias of the Writer class to be instantiated if
      no `writer` supplied.
    - `settings`: Runtime settings object.
    - `settings_spec`: Extra settings specification; a `docutils.SettingsSpec`
      subclass.  Used only if no `settings` specified.
    - `settings_overrides`: A dictionary containing program-specific overrides
      of component settings.
    """
    pub = Publisher(reader, parser, writer, settings=settings,
                    source_class=io.StringInput,
                    destination_class=io.StringOutput)
    pub.set_components(reader_name, parser_name, writer_name)
    if settings is None:
        settings = pub.get_settings(settings_spec=settings_spec)
    if settings_overrides:
        settings._update(settings_overrides, 'loose')
    pub.set_source(source, source_path)
    pub.set_destination(destination_path=destination_path)
    return pub.publish()
