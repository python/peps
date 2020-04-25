from docutils import nodes
from docutils.transforms import Transform
from docutils.parsers.rst import states, Directive


class PEPTitle(Transform):

    """
    Insert an empty table of contents topic and a transform placeholder into
    the document after the RFC 2822 header.
    """

    # needs to run before docutils.transforms.frontmatter.DocInfo
    default_priority = 335

    def apply(self):
        # Directory to hold the PEP's RFC2822 header details, to extract a titke string
        pep_header_details = {}

        # Iterate through the header fields, which are the first section of the document
        for field in self.document[0]:
            row_attributes = {}
            for sub in field:
                # Hold details of the attribute's tag against its details
                row_attributes[sub.tagname] = sub.rawsource
            # Collapse the dictionary by removing tag names
            pep_header_details[row_attributes["field_name"]] = row_attributes["field_body"]

        # Create the title string for the PEP
        pep_number = int(pep_header_details["PEP"])
        pep_title = pep_header_details["Title"]
        pep_title_string = f"PEP {pep_number} -- {pep_title}"

        # Generate the title section node and its properties
        pep_title_node = nodes.section()
        textnode = nodes.Text(pep_title_string, pep_title_string)
        titlenode = nodes.title(pep_title_string, '', textnode)
        name = states.normalize_name(titlenode.astext())
        pep_title_node['names'].append(name)
        pep_title_node += titlenode

        # Insert the title node as the root element, move children down
        document_children = self.document.children
        self.document.children = [pep_title_node]
        pep_title_node.extend(document_children)
        self.document.note_implicit_target(pep_title_node, pep_title_node)
