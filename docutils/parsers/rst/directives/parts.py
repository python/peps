# Author: David Goodger, Dmitry Jemerov
# Contact: goodger@users.sourceforge.net
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
Directives for document parts.
"""

__docformat__ = 'reStructuredText'

from docutils import nodes
from docutils.transforms import parts
from docutils.parsers.rst import directives


backlinks_values = ('top', 'entry', 'none')

def backlinks(arg):
    value = directives.choice(arg, backlinks_values)
    if value == 'none':
        return None
    else:
        return value

def contents(name, arguments, options, content, lineno,
             content_offset, block_text, state, state_machine):
    """Table of contents."""
    if arguments:
        title_text = arguments[0]
        text_nodes, messages = state.inline_text(title_text, lineno)
        title = nodes.title(title_text, '', *text_nodes)
    else:
        messages = []
        title = None
    pending = nodes.pending(parts.Contents, {'title': title}, block_text)
    pending.details.update(options)
    state_machine.document.note_pending(pending)
    return [pending] + messages

contents.arguments = (0, 1, 1)
contents.options = {'depth': directives.nonnegative_int,
                    'local': directives.flag,
                    'backlinks': backlinks}

def sectnum(name, arguments, options, content, lineno,
            content_offset, block_text, state, state_machine):
    """Automatic section numbering."""
    pending = nodes.pending(parts.SectNum)
    pending.details.update(options)
    state_machine.document.note_pending(pending)
    return [pending]

sectnum.options = {'depth': int}
