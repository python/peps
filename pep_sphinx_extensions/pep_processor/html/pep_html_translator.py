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

    def visit_footnote_reference(self, node):
        self.body.append(self.starttag(node, "a", suffix="[",
            CLASS=f"footnote-reference {self.settings.footnote_references}",
            href=f"#{node['refid']}"
        ))

    def depart_footnote_reference(self, node):
        self.body.append(']</a>')

    def visit_label(self, node):
        # pass parent node to get id into starttag:
        self.body.append(self.starttag(node.parent, "dt", suffix="[", CLASS="label"))

        # footnote/citation backrefs:
        back_refs = node.parent["backrefs"]
        if self.settings.footnote_backlinks and len(back_refs) == 1:
            self.body.append(f'<a href="#{back_refs[0]}">')
            self.context.append(f"</a>]")
        else:
            self.context.append("]")

    def depart_label(self, node) -> None:
        """PEP link/citation block cleanup with italicised backlinks."""
        self.body.append(self.context.pop())
        back_refs = node.parent["backrefs"]
        if self.settings.footnote_backlinks and len(back_refs) > 1:
            back_links = ", ".join(f"<a href='#{ref}'>{i}</a>" for i, ref in enumerate(back_refs, start=1))
            self.body.append(f"<em> ({back_links}) </em>")

        # Close the def tags
        self.body.append("</dt>\n<dd>")

    def unknown_visit(self, node: nodes.Node) -> None:
        """No processing for unknown node types."""
        pass
