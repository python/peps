from __future__ import annotations

from docutils import nodes
from docutils import transforms


class PEPZero(transforms.Transform):
    """Schedule PEP 0 processing."""

    # Run during sphinx post-processing
    default_priority = 760

    def apply(self) -> None:
        # Walk document and mask email addresses if present.
        for reference_node in self.document.findall(nodes.reference):
            reference_node.replace_self(_mask_email(reference_node))
        # Remove this node
        self.startnode.parent.remove(self.startnode)


def _mask_email(ref: nodes.reference) -> nodes.reference:
    """Mask the email address in `ref` and return a replacement node.

    `ref` is returned unchanged if it contains no email address.

    If given an email not explicitly whitelisted, process it such that
    `user@host` -> `user at host`.

    The returned node has no refuri link attribute.

    """
    if not ref.get("refuri", "").startswith("mailto:"):
        return ref
    return nodes.raw("", ref[0].replace("@", "&#32;&#97;t&#32;"), format="html")
