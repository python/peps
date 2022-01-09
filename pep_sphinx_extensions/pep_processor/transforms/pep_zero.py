from __future__ import annotations

from docutils import nodes
from docutils import transforms


class PEPZero(transforms.Transform):
    """Schedule PEP 0 processing."""

    # Run during sphinx post processing
    default_priority = 760

    def apply(self) -> None:
        # Walk document and then remove this node
        visitor = PEPZeroSpecial(self.document)
        self.document.walk(visitor)
        self.startnode.parent.remove(self.startnode)


class PEPZeroSpecial(nodes.SparseNodeVisitor):
    """Perform the special processing needed by PEP 0:

    - Mask email addresses.
    - Link PEP numbers in the second column of 4-column tables to the PEPs themselves.

    """

    def __init__(self, document: nodes.document):
        super().__init__(document)
        self.pep_table: int = 0
        self.entry: int = 0

    def unknown_visit(self, node: nodes.Node) -> None:
        """No processing for undefined node types."""
        pass

    @staticmethod
    def visit_reference(node: nodes.reference) -> None:
        """Mask email addresses if present."""
        node.replace_self(_mask_email(node))

    @staticmethod
    def visit_field_list(node: nodes.field_list) -> None:
        """Skip PEP headers."""
        if "rfc2822" in node["classes"]:
            raise nodes.SkipNode

    def visit_tgroup(self, node: nodes.tgroup) -> None:
        """Set column counter and PEP table marker."""
        self.pep_table = node["cols"] == 4
        self.entry = 0  # reset column number

    def visit_colspec(self, node: nodes.colspec) -> None:
        self.entry += 1
        if self.pep_table and self.entry == 2:
            node["classes"].append("num")

    def visit_row(self, _node: nodes.row) -> None:
        self.entry = 0  # reset column number

    def visit_entry(self, node: nodes.entry) -> None:
        self.entry += 1
        if self.pep_table and self.entry == 2 and len(node) == 1:
            node["classes"].append("num")
            # if this is the PEP number column, replace the number with a link to the PEP
            para = node[0]
            if isinstance(para, nodes.paragraph) and len(para) == 1:
                pep_str = para.astext()
                try:
                    pep_num = int(pep_str)
                except ValueError:
                    return
                ref = self.document.settings.pep_url.format(pep_num)
                para[0] = nodes.reference("", pep_str, refuri=ref)


def _mask_email(ref: nodes.reference, pep_num: int | None = None) -> nodes.reference:
    """Mask the email address in `ref` and return a replacement node.

    `ref` is returned unchanged if it contains no email address.

    If given an email not explicitly whitelisted, process it such that
    `user@host` -> `user at host`.

    If given a PEP number `pep_num`, add a default email subject.

    """
    if "refuri" not in ref or not ref["refuri"].startswith("mailto:"):
        return ref
    non_masked_addresses = {"peps@python.org", "python-list@python.org", "python-dev@python.org"}
    if ref["refuri"].removeprefix("mailto:").strip() not in non_masked_addresses:
        ref[0] = nodes.raw("", ref[0].replace("@", "&#32;&#97;t&#32;"), format="html")
    if pep_num is None:
        return ref[0]  # return email text without mailto link
    ref["refuri"] += f"?subject=PEP%20{pep_num}"
    return ref
