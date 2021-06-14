from pathlib import Path

from docutils import nodes
import docutils.transforms as transforms


class PEPTitle(transforms.Transform):
    """Add PEP title and organise document hierarchy."""

    # needs to run before docutils.transforms.frontmatter.DocInfo and after
    # pep_processor.transforms.pep_title.PEPTitle
    default_priority = 335

    def apply(self) -> None:
        if not Path(self.document["source"]).match("pep-*"):
            return  # not a PEP file, exit early

        # Directory to hold the PEP's RFC2822 header details, to extract a title string
        pep_header_details = {}

        # Iterate through the header fields, which are the first section of the document
        for field in self.document[0]:
            # Hold details of the attribute's tag against its details
            row_attributes = {sub.tagname: sub.rawsource for sub in field}
            pep_header_details[row_attributes["field_name"]] = row_attributes["field_body"]

            # We only need the PEP number and title
            if pep_header_details.keys() >= {"PEP", "Title"}:
                break

        # Create the title string for the PEP
        pep_number = int(pep_header_details["PEP"])
        pep_title = pep_header_details["Title"]
        pep_title_string = f"PEP {pep_number} -- {pep_title}"  # double hyphen for en dash

        # Generate the title section node and its properties
        pep_title_node = nodes.section("", nodes.title("", pep_title_string, classes=["page-title"]), names=["pep-content"])

        # Insert the title node as the root element, move children down
        document_children = self.document.children
        self.document.children = [pep_title_node]
        pep_title_node.extend(document_children)
        self.document.note_implicit_target(pep_title_node, pep_title_node)
