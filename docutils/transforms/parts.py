# Authors: David Goodger, Ueli Schlaepfer, Dmitry Jemerov
# Contact: goodger@users.sourceforge.net
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
Transforms related to document parts.
"""

__docformat__ = 'reStructuredText'


import re
import sys
from docutils import nodes, utils
from docutils.transforms import TransformError, Transform


class SectNum(Transform):

    """
    Automatically assigns numbers to the titles of document sections.

    It is possible to limit the maximum section level for which the numbers
    are added.  For those sections that are auto-numbered, the "autonum"
    attribute is set, informing the contents table generator that a different
    form of the TOC should be used.
    """

    default_priority = 710
    """Should be applied before `Contents`."""

    def apply(self):
        self.maxdepth = self.startnode.details.get('depth', sys.maxint)
        self.startnode.parent.remove(self.startnode)
        self.update_section_numbers(self.document)

    def update_section_numbers(self, node, prefix=(), depth=0):
        depth += 1
        sectnum = 1
        for child in node:
            if isinstance(child, nodes.section):
                numbers = prefix + (str(sectnum),)
                title = child[0]
                # Use &nbsp; for spacing:
                generated = nodes.generated(
                    '', '.'.join(numbers) + u'\u00a0' * 3, CLASS='sectnum')
                title.insert(0, generated)
                title['auto'] = 1
                if depth < self.maxdepth:
                    self.update_section_numbers(child, numbers, depth)
                sectnum += 1


class Contents(Transform):

    """
    This transform generates a table of contents from the entire document tree
    or from a single branch.  It locates "section" elements and builds them
    into a nested bullet list, which is placed within a "topic".  A title is
    either explicitly specified, taken from the appropriate language module,
    or omitted (local table of contents).  The depth may be specified.
    Two-way references between the table of contents and section titles are
    generated (requires Writer support).

    This transform requires a startnode, which which contains generation
    options and provides the location for the generated table of contents (the
    startnode is replaced by the table of contents "topic").
    """

    default_priority = 720

    def apply(self):
        topic = nodes.topic(CLASS='contents')
        title = self.startnode.details['title']
        if self.startnode.details.has_key('local'):
            startnode = self.startnode.parent
            # @@@ generate an error if the startnode (directive) not at
            # section/document top-level? Drag it up until it is?
            while not isinstance(startnode, nodes.Structural):
                startnode = startnode.parent
        else:
            startnode = self.document
            if not title:
                title = nodes.title('', self.language.labels['contents'])
        if title:
            name = title.astext()
            topic += title
        else:
            name = self.language.labels['contents']
        name = utils.normalize_name(name)
        if not self.document.has_name(name):
            topic['name'] = name
        self.document.note_implicit_target(topic)
        self.toc_id = topic['id']
        if self.startnode.details.has_key('backlinks'):
            self.backlinks = self.startnode.details['backlinks']
        else:
            self.backlinks = self.document.settings.toc_backlinks
        contents = self.build_contents(startnode)
        if len(contents):
            topic += contents
            self.startnode.parent.replace(self.startnode, topic)
        else:
            self.startnode.parent.remove(self.startnode)

    def build_contents(self, node, level=0):
        level += 1
        sections = []
        i = len(node) - 1
        while i >= 0 and isinstance(node[i], nodes.section):
            sections.append(node[i])
            i -= 1
        sections.reverse()
        entries = []
        autonum = 0
        depth = self.startnode.details.get('depth', sys.maxint)
        for section in sections:
            title = section[0]
            auto = title.get('auto')    # May be set by SectNum.
            entrytext = self.copy_and_filter(title)
            reference = nodes.reference('', '', refid=section['id'],
                                        *entrytext)
            ref_id = self.document.set_id(reference)
            entry = nodes.paragraph('', '', reference)
            item = nodes.list_item('', entry)
            if self.backlinks == 'entry':
                title['refid'] = ref_id
            elif self.backlinks == 'top':
                title['refid'] = self.toc_id
            if level < depth:
                subsects = self.build_contents(section, level)
                item += subsects
            entries.append(item)
        if entries:
            contents = nodes.bullet_list('', *entries)
            if auto:
                contents.set_class('auto-toc')
            return contents
        else:
            return []

    def copy_and_filter(self, node):
        """Return a copy of a title, with references, images, etc. removed."""
        visitor = ContentsFilter(self.document)
        node.walkabout(visitor)
        return visitor.get_entry_text()


class ContentsFilter(nodes.TreeCopyVisitor):

    def get_entry_text(self):
        return self.get_tree_copy().get_children()

    def visit_citation_reference(self, node):
        raise nodes.SkipNode

    def visit_footnote_reference(self, node):
        raise nodes.SkipNode

    def visit_image(self, node):
        if node.hasattr('alt'):
            self.parent.append(nodes.Text(node['alt']))
        raise nodes.SkipNode

    def ignore_node_but_process_children(self, node):
        raise nodes.SkipDeparture

    visit_interpreted = ignore_node_but_process_children
    visit_problematic = ignore_node_but_process_children
    visit_reference = ignore_node_but_process_children
    visit_target = ignore_node_but_process_children
