# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
Directives for additional body elements.
"""

__docformat__ = 'reStructuredText'


import sys
from docutils import nodes


def topic(name, arguments, options, content, lineno,
          content_offset, block_text, state, state_machine):
    if not state_machine.match_titles:
        error = state_machine.reporter.error(
              'Topics may not be nested within topics or body elements.',
              nodes.literal_block(block_text, block_text), line=lineno)
        return [error]
    if not content:
        warning = state_machine.reporter.warning(
            'Content block expected for the "%s" directive; none found.'
            % name, nodes.literal_block(block_text, block_text),
            line=lineno)
        return [warning]
    title_text = arguments[0]
    textnodes, messages = state.inline_text(title_text, lineno)
    title = nodes.title(title_text, '', *textnodes)
    text = '\n'.join(content)
    topic_node = nodes.topic(text, title, *messages)
    if text:
        state.nested_parse(content, content_offset, topic_node)
    return [topic_node]

topic.arguments = (1, 0, 1)
topic.content = 1

def line_block(name, arguments, options, content, lineno,
               content_offset, block_text, state, state_machine,
               node_class=nodes.line_block):
    if not content:
        warning = state_machine.reporter.warning(
            'Content block expected for the "%s" directive; none found.'
            % name, nodes.literal_block(block_text, block_text), line=lineno)
        return [warning]
    text = '\n'.join(content)
    text_nodes, messages = state.inline_text(text, lineno)
    node = node_class(text, '', *text_nodes)
    return [node] + messages

line_block.content = 1

def parsed_literal(name, arguments, options, content, lineno,
                   content_offset, block_text, state, state_machine):
    return line_block(name, arguments, options, content, lineno,
                      content_offset, block_text, state, state_machine,
                      node_class=nodes.literal_block)

parsed_literal.content = 1
