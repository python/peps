from __future__ import annotations

from pathlib import Path

from docutils import nodes
from docutils import transforms
from docutils.transforms import parts


class PEPContents(transforms.Transform):
    """Add TOC placeholder and horizontal rule after PEP title and headers."""

    # Use same priority as docutils.transforms.Contents
    default_priority = 380

    def apply(self) -> None:
        if not Path(self.document["source"]).match("pep-*"):
            return  # not a PEP file, exit early
        # Create the contents placeholder section
        title = nodes.title("", "", nodes.Text("Contents"))
        contents_section = nodes.section("", title)
        if not self.document.has_name("contents"):
            contents_section["names"].append("contents")
        self.document.note_implicit_target(contents_section)

        # Add a table of contents builder
        pending = nodes.pending(Contents)
        contents_section += pending
        self.document.note_pending(pending)

        # Insert the toc after title and PEP headers
        self.document.children[0].insert(2, contents_section)

        # Add a horizontal rule before contents
        transition = nodes.transition()
        self.document[0].insert(2, transition)


class Contents(parts.Contents):
    """Build Table of Contents from document."""
    def __init__(self, document: nodes.document, startnode: nodes.Node | None = None):
        super().__init__(document, startnode)

        # used in parts.Contents.build_contents
        self.toc_id = None
        self.backlinks = None

    def apply(self) -> None:
        contents = self.build_contents(self.document[0][4:])  # skip PEP title, headers, <hr/>, and contents
        if contents:
            self.startnode.replace_self(contents)
        else:
            # if no contents, remove the empty placeholder
            self.startnode.parent.parent.remove(self.startnode.parent)

    def build_contents(self, node: nodes.Node | list[nodes.Node], _level: None = None):
        entries = []
        children = getattr(node, "children", node)

        for section in children:
            if not isinstance(section, nodes.section):
                continue

            title = section[0]

            # remove all pre-existing hyperlinks in the title (e.g. PEP references)
            while (link_node := title.next_node(nodes.reference)) is not None:
                link_node.replace_self(link_node[0])
            ref_id = section['ids'][0]
            title["refid"] = ref_id  # Add a link to self
            entry_text = self.copy_and_filter(title)
            reference = nodes.reference("", "", refid=ref_id, *entry_text)
            item = nodes.list_item("", nodes.paragraph("", "", reference))

            item += self.build_contents(section)  # recurse to add sub-sections
            entries.append(item)
        if entries:
            return nodes.bullet_list('', *entries)
        return []
