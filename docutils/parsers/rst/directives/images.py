# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
Directives for figures and simple images.
"""

__docformat__ = 'reStructuredText'


import sys
from docutils import nodes, utils
from docutils.parsers.rst import directives


align_values = ('top', 'middle', 'bottom', 'left', 'center', 'right')

def align(argument):
    return directives.choice(argument, align_values)

def image(name, arguments, options, content, lineno,
          content_offset, block_text, state, state_machine):
    reference = ''.join(arguments[0].split('\n'))
    if reference.find(' ') != -1:
        error = state_machine.reporter.error(
              'Image URI contains whitespace.',
              nodes.literal_block(block_text, block_text), line=lineno)
        return [error]
    options['uri'] = reference
    image_node = nodes.image(block_text, **options)
    return [image_node]

image.arguments = (1, 0, 1)
image.options = {'alt': directives.unchanged,
                 'height': directives.nonnegative_int,
                 'width': directives.nonnegative_int,
                 'scale': directives.nonnegative_int,
                 'align': align}

def figure(name, arguments, options, content, lineno,
           content_offset, block_text, state, state_machine):
    (image_node,) = image(name, arguments, options, content, lineno,
                         content_offset, block_text, state, state_machine)
    if isinstance(image_node, nodes.system_message):
        return [image_node]
    figure_node = nodes.figure('', image_node)
    if content:
        node = nodes.Element()          # anonymous container for parsing
        state.nested_parse(content, content_offset, node)
        first_node = node[0]
        if isinstance(first_node, nodes.paragraph):
            caption = nodes.caption(first_node.rawsource, '',
                                    *first_node.children)
            figure_node += caption
        elif not (isinstance(first_node, nodes.comment)
                  and len(first_node) == 0):
            error = state_machine.reporter.error(
                  'Figure caption must be a paragraph or empty comment.',
                  nodes.literal_block(block_text, block_text), line=lineno)
            return [figure_node, error]
        if len(node) > 1:
            figure_node += nodes.legend('', *node[1:])
    return [figure_node]

figure.arguments = (1, 0, 1)
figure.options = image.options
figure.content = 1
