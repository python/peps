from docutils.nodes import Node
import sphinx.writers.html5 as html5


class PEPTranslator(html5.HTML5Translator):
    def depart_label(self, node):
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

    def unknown_visit(self, node: Node) -> None:
        pass
