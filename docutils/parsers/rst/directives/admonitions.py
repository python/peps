# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
Admonition directives.
"""

__docformat__ = 'reStructuredText'


from docutils.parsers.rst import states
from docutils import nodes


def admonition(node_class, name, arguments, options, content, lineno,
               content_offset, block_text, state, state_machine):
    text = '\n'.join(content)
    admonition_node = node_class(text)
    if text:
        state.nested_parse(content, content_offset, admonition_node)
        return [admonition_node]
    else:
        error = state_machine.reporter.error(
            'The "%s" admonition is empty; content required.' % (name),
            nodes.literal_block(block_text, block_text), line=lineno)
        return [error]

def attention(*args):
    return admonition(nodes.attention, *args)

attention.content = 1

def caution(*args):
    return admonition(nodes.caution, *args)

caution.content = 1

def danger(*args):
    return admonition(nodes.danger, *args)

danger.content = 1

def error(*args):
    return admonition(nodes.error, *args)

error.content = 1

def important(*args):
    return admonition(nodes.important, *args)

important.content = 1

def note(*args):
    return admonition(nodes.note, *args)

note.content = 1

def tip(*args):
    return admonition(nodes.tip, *args)

tip.content = 1

def hint(*args):
    return admonition(nodes.hint, *args)

hint.content = 1

def warning(*args):
    return admonition(nodes.warning, *args)

warning.content = 1
