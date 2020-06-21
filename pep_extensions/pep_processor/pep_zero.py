from docutils import nodes
from docutils import transforms
from docutils.transforms import peps
import pep_extensions.config

pep_url = pep_extensions.config.pep_url


class PEPZero(transforms.Transform):

    """
    Special processing for PEP 0.
    """

    default_priority = 760

    def apply(self):
        visitor = PEPZeroSpecial(self.document)
        self.document.walk(visitor)
        self.startnode.parent.remove(self.startnode)


class PEPZeroSpecial(nodes.SparseNodeVisitor):

    """
    Perform the special processing needed by PEP 0:

    - Mask email addresses.
    - Link PEP numbers in the second column of 4-column tables to the PEPs
      themselves.
    """

    def __init__(self, document: nodes.document):
        super().__init__(document)
        self.pep_table: int = 0
        self.entry: int = 0

    def unknown_visit(self, node: nodes.Node) -> None:
        pass

    @staticmethod
    def visit_reference(node: nodes.reference) -> None:
        node.replace_self(peps.mask_email(node))

    @staticmethod
    def visit_field_list(node: nodes.field_list) -> None:
        if 'rfc2822' in node['classes']:
            raise nodes.SkipNode

    def visit_tgroup(self, node: nodes.tgroup) -> None:
        self.pep_table = node['cols'] == 4
        self.entry = 0

    def visit_colspec(self, node: nodes.colspec) -> None:
        self.entry += 1
        if self.pep_table and self.entry == 2:
            node['classes'].append('num')

    def visit_row(self, _node: nodes.row) -> None:
        self.entry = 0

    def visit_entry(self, node: nodes.entry) -> None:
        self.entry += 1
        if self.pep_table and self.entry == 2 and len(node) == 1:
            node['classes'].append('num')
            p = node[0]
            if isinstance(p, nodes.paragraph) and len(p) == 1:
                text = p.astext()
                try:
                    pep = int(text)
                    ref = self.document.settings.pep_base_url + pep_url.format(pep)
                    p[0] = nodes.reference(text, text, refuri=ref)
                except ValueError:
                    pass
