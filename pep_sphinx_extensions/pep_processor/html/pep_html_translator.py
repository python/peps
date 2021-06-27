from __future__ import annotations

from typing import TYPE_CHECKING

from docutils import nodes
import sphinx.writers.html5 as html5

if TYPE_CHECKING:
    from sphinx.builders import html


class PEPTranslator(html5.HTML5Translator):
    """Custom RST -> HTML translation rules for PEPs."""

    def __init__(self, document: nodes.document, builder: html.StandaloneHTMLBuilder):
        super().__init__(document, builder)
        self.compact_simple: bool = False

    @staticmethod
    def should_be_compact_paragraph(node: nodes.paragraph) -> bool:
        """Check if paragraph should be compact.

        Omitting <p/> tags around paragraph nodes gives visually compact lists.

        """
        # Never compact paragraphs that are children of document or compound.
        if isinstance(node.parent, (nodes.document, nodes.compound)):
            return False

        # Check for custom attributes in paragraph.
        for key, value in node.non_default_attributes().items():
            # if key equals "classes", carry on
            # if value is empty, or contains only "first", only "last", or both
            # "first" and "last", carry on
            # else return False
            if any((key != "classes", not set(value) <= {"first", "last"})):
                return False

        # Only first paragraph can be compact (ignoring initial label & invisible nodes)
        first = isinstance(node.parent[0], nodes.label)
        visible_siblings = [child for child in node.parent.children[first:] if not isinstance(child, nodes.Invisible)]
        if visible_siblings[0] is not node:
            return False

        # otherwise, the paragraph should be compact
        return True

    def visit_paragraph(self, node: nodes.paragraph) -> None:
        """Remove <p> tags if possible."""
        if self.should_be_compact_paragraph(node):
            self.context.append("")
        else:
            self.body.append(self.starttag(node, "p", ""))
            self.context.append("</p>\n")

    def depart_paragraph(self, _: nodes.paragraph) -> None:
        """Add corresponding end tag from `visit_paragraph`."""
        self.body.append(self.context.pop())

    def depart_label(self, node) -> None:
        """PEP link/citation block cleanup with italicised backlinks."""
        if not self.settings.footnote_backlinks:
            self.body.append("</span>")
            self.body.append("</dt>\n<dd>")
            return

        # If only one reference to this footnote
        back_references = node.parent["backrefs"]
        if len(back_references) == 1:
            self.body.append("</a>")

        # Close the tag
        self.body.append("</span>")

        # If more than one reference
        if len(back_references) > 1:
            back_links = [f"<a href='#{ref}'>{i}</a>" for i, ref in enumerate(back_references, start=1)]
            back_links_str = ", ".join(back_links)
            self.body.append(f"<span class='fn-backref''><em> ({back_links_str}) </em></span>")

        # Close the def tags
        self.body.append("</dt>\n<dd>")

    def unknown_visit(self, node: nodes.Node) -> None:
        """No processing for unknown node types."""
        pass
