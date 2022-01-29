from pathlib import Path

from docutils import nodes
from docutils import transforms


class PEPSectionLinker(transforms.Transform):
    """Link section headings to themselves."""

    default_priority = 720

    def apply(self) -> None:
        if not Path(self.document["source"]).match("pep-*"):
            return  # not a PEP file, exit early
        _link_section_headings(self.document[0][3:])  # skip PEP title, headers, and <hr/>


def _link_section_headings(children: list[nodes.Node]):
    for section in children:
        if not isinstance(section, nodes.section):
            continue

        # remove all pre-existing hyperlinks in the title (e.g. PEP references)
        title = section[0]
        while (link_node := title.next_node(nodes.reference)) is not None:
            link_node.replace_self(link_node[0])

        title["refid"] = section["ids"][0]   # Add a link to self

        _link_section_headings(section.children)  # recurse to sub-sections
