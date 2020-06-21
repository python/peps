from docutils import nodes
import sphinx.writers.html5 as html5
import re
import logging
logger = logging.getLogger("sphinx")

class PEPTranslator(html5.HTML5Translator):
    compact_field_list = True
    phrases_and_newlines = re.compile(r'[^\n]+|\n')

    def __init__(self, *args):
        super(PEPTranslator, self).__init__(*args)
        logger.warning("PEP Translator")
        self.compact_simple: bool = False

    # Omit <p> tags to produce visually compact lists
    def should_be_compact_paragraph(self, node: nodes.paragraph) -> bool:
        """Determine if <p> tags around paragraph ``node`` can be omitted."""

        # Never compact paragraphs in document or compound.
        if isinstance(node.parent, (nodes.document, nodes.compound)):
            return False

        # Check for custom attributes in paragraph.
        for key, value in node.non_default_attributes().items():
            if key != 'classes' or value not in ([], ['first'], ['last'], ['first', 'last']):
                return False

        # Only first paragraph can be compact (ignoring initial label & invisible nodes)
        first = isinstance(node.parent[0], nodes.label)
        visible_siblings = [child for child in node.parent.children[first:] if not isinstance(child, nodes.Invisible)]
        if visible_siblings[0] is not node:
            return False

        if self.compact_simple or self.compact_field_list:
            return True

        parent_length = sum([1 for n in node.parent if not isinstance(n, (nodes.Invisible, nodes.label))])
        if self.compact_p and parent_length == 1:
            return True

        return False

    def visit_enumerated_list(self, node: nodes.enumerated_list) -> None:
        self.context.append(self.compact_simple)
        self.compact_simple = self.is_compactable(node)
        super().visit_enumerated_list(node)

    def depart_enumerated_list(self, node: nodes.enumerated_list) -> None:
        self.compact_simple = self.context.pop()
        super().depart_enumerated_list(node)

    def visit_paragraph(self, node: nodes.paragraph) -> None:
        """Remove <p> tags if possible (PEPs historically h )"""
        if self.should_be_compact_paragraph(node):
            self.context.append('')
        else:
            self.body.append(self.starttag(node, 'p', ''))
            self.context.append('</p>\n')

    def depart_paragraph(self, _: nodes.paragraph) -> None:
        """Add corresponding end tag from `visit_paragraph`. Node param isn't needed."""
        self.body.append(self.context.pop())

    def depart_label(self, node) -> None:
        if not self.settings.footnote_backlinks:
            self.body.append('</span>')
            self.body.append('</dt>\n<dd>')
            return

        # If only one reference to this footnote
        back_references = node.parent['backrefs']
        if len(back_references) == 1:
            self.body.append('</a>')

        # Close the tag
        self.body.append('</span>')

        # If more than one reference
        if len(back_references) > 1:
            back_links = [f'<a href="#{ref}">{i}</a>' for (i, ref) in enumerate(back_references, 1)]
            back_links_str = ", ".join(back_links)
            self.body.append(f"<span class='fn-backref'><em> ({back_links_str}) </em></span>")

        # Close the def tags
        self.body.append('</dt>\n<dd>')

    def unknown_visit(self, node: nodes.Node) -> None:
        pass
