# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
This package contains directive implementation modules.

The interface for directive functions is as follows::

    def directive_fn(name, arguments, options, content, lineno,
                     content_offset, block_text, state, state_machine):
        code...

    # Set function attributes:
    directive_fn.arguments = ...
    directive_fn.options = ...
    direcitve_fn.content = ...

Parameters:

- ``name`` is the directive type or name.

- ``arguments`` is a list of positional arguments.

- ``options`` is a dictionary mapping option names to values.

- ``content`` is a list of strings, the directive content.

- ``lineno`` is the line number of the first line of the directive.

- ``content_offset`` is the line offset of the first line of the content from
  the beginning of the current input.  Used when initiating a nested parse.

- ``block_text`` is a string containing the entire directive.  Include it as
  the content of a literal block in a system message if there is a problem.

- ``state`` is the state which called the directive function.

- ``state_machine`` is the state machine which controls the state which called
  the directive function.

Function attributes, interpreted by the directive parser (which calls the
directive function):

- ``arguments``: A 3-tuple specifying the expected positional arguments, or
  ``None`` if the directive has no arguments.  The 3 items in the tuple are
  ``(required, optional, whitespace OK in last argument)``:

  1. The number of required arguments.
  2. The number of optional arguments.
  3. A boolean, indicating if the final argument may contain whitespace.

  Arguments are normally single whitespace-separated words.  The final
  argument may contain whitespace if the third item in the argument spec tuple
  is 1/True.  If the form of the arguments is more complex, specify only one
  argument (either required or optional) and indicate that final whitespace is
  OK; the client code must do any context-sensitive parsing.

- ``options``: A dictionary, mapping known option names to conversion
  functions such as `int` or `float`.  ``None`` or an empty dict implies no
  options to parse.

- ``content``: A boolean; true if content is allowed.  Client code must handle
  the case where content is required but not supplied (an empty content list
  will be supplied).

Directive functions return a list of nodes which will be inserted into the
document tree at the point where the directive was encountered (can be an
empty list).

See `Creating reStructuredText Directives`_ for more information.

.. _Creating reStructuredText Directives:
   http://docutils.sourceforge.net/spec/howto/rst-directives.html
"""

__docformat__ = 'reStructuredText'

from docutils import nodes
from docutils.parsers.rst.languages import en as _fallback_language_module


_directive_registry = {
      'attention': ('admonitions', 'attention'),
      'caution': ('admonitions', 'caution'),
      'danger': ('admonitions', 'danger'),
      'error': ('admonitions', 'error'),
      'important': ('admonitions', 'important'),
      'note': ('admonitions', 'note'),
      'tip': ('admonitions', 'tip'),
      'hint': ('admonitions', 'hint'),
      'warning': ('admonitions', 'warning'),
      'topic': ('body', 'topic'),
      'line-block': ('body', 'line_block'),
      'parsed-literal': ('body', 'parsed_literal'),
      #'questions': ('body', 'question_list'),
      'image': ('images', 'image'),
      'figure': ('images', 'figure'),
      'contents': ('parts', 'contents'),
      'sectnum': ('parts', 'sectnum'),
      #'footnotes': ('parts', 'footnotes'),
      #'citations': ('parts', 'citations'),
      'target-notes': ('references', 'target_notes'),
      'meta': ('html', 'meta'),
      #'imagemap': ('html', 'imagemap'),
      'raw': ('misc', 'raw'),
      'include': ('misc', 'include'),
      'replace': ('misc', 'replace'),
      'restructuredtext-test-directive': ('misc', 'directive_test_function'),}
"""Mapping of directive name to (module name, function name).  The directive
name is canonical & must be lowercase.  Language-dependent names are defined
in the ``language`` subpackage."""

_modules = {}
"""Cache of imported directive modules."""

_directives = {}
"""Cache of imported directive functions."""

def directive(directive_name, language_module, document):
    """
    Locate and return a directive function from its language-dependent name.
    If not found in the current language, check English.
    """
    normname = directive_name.lower()
    messages = []
    if _directives.has_key(normname):
        return _directives[normname], messages
    try:
        canonicalname = language_module.directives[normname]
    except (KeyError, AttributeError):
        msg_text = ('No directive entry for "%s" in module "%s".'
                    % (directive_name, language_module.__name__))
        try:
            canonicalname = _fallback_language_module.directives[normname]
            msg_text += ('\nUsing English fallback for directive "%s".'
                         % directive_name)
        except KeyError:
            msg_text += ('\nTrying "%s" as canonical directive name.'
                         % directive_name)
            # The canonical name should be an English name, but just in case:
            canonicalname = normname
        warning = document.reporter.warning(
            msg_text, line=document.current_line)
        messages.append(warning)
    try:
        modulename, functionname = _directive_registry[canonicalname]
    except KeyError:
        return None, messages
    if _modules.has_key(modulename):
        module = _modules[modulename]
    else:
        try:
            module = __import__(modulename, globals(), locals())
        except ImportError:
            return None, messages
    try:
        function = getattr(module, functionname)
        _directives[normname] = function
    except AttributeError:
        return None, messages
    return function, messages

def flag(argument):
    """
    Check for a valid flag option (no argument) and return ``None``.

    Raise ``ValueError`` if an argument is found.
    """
    if argument and argument.strip():
        raise ValueError('no argument is allowed; "%s" supplied' % argument)
    else:
        return None

def unchanged(argument):
    """
    Return the argument, unchanged.

    Raise ``ValueError`` if no argument is found.
    """
    if argument is None:
        raise ValueError('argument required but none supplied')
    else:
        return argument  # unchanged!

def path(argument):
    """
    Return the path argument unwrapped (with newlines removed).

    Raise ``ValueError`` if no argument is found or if the path contains
    internal whitespace.
    """
    if argument is None:
        raise ValueError('argument required but none supplied')
    else:
        path = ''.join([s.strip() for s in argument.splitlines()])
        if path.find(' ') == -1:
            return path
        else:
            raise ValueError('path contains whitespace')

def nonnegative_int(argument):
    """
    Check for a nonnegative integer argument; raise ``ValueError`` if not.
    """
    value = int(argument)
    if value < 0:
        raise ValueError('negative value; must be positive or zero')
    return value

def format_values(values):
    return '%s, or "%s"' % (', '.join(['"%s"' % s for s in values[:-1]]),
                            values[-1])

def choice(argument, values):
    try:
        value = argument.lower().strip()
    except AttributeError:
        raise ValueError('must supply an argument; choose from %s'
                         % format_values(values))
    if value in values:
        return value
    else:
        raise ValueError('"%s" unknown; choose from %s'
                         % (argument, format_values(values)))
