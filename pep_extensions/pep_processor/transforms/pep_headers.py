import re
from pathlib import Path

from docutils import nodes
from docutils import transforms
from docutils.transforms import peps

from pep_extensions.pep_processor.transforms import pep_zero
import pep_extensions.config

pep_url = pep_extensions.config.pep_url


class DataError(Exception):
    pass


# PEPHeaders is identical to docutils.transforms.peps.Headers excepting bdfl-delegate, sponsor & superseeded-by
class PEPHeaders(transforms.Transform):

    """
    Process fields in a PEP's initial RFC-2822 header.
    """

    default_priority = 330

    def apply(self):
        if not len(self.document):
            # @@@ replace these DataErrors with proper system messages
            raise DataError("Document tree is empty.")

        if not Path(self.document["source"]).match("pep-*"):
            # not a PEP file
            return

        header = self.document[0]
        if not isinstance(header, nodes.field_list) or "rfc2822" not in header["classes"]:
            raise DataError("Document does not begin with an RFC-2822 header; it is not a PEP.")

        pep = None
        pep_field = header[0]
        if pep_field[0].astext().lower() == "pep":  # should be the first field
            value = pep_field[1].astext()
            try:
                pep = int(value)
            except ValueError:
                pep = value
                msg = self.document.reporter.warning(
                    f"'PEP' header must contain an integer; '{pep}' is an  invalid value.",
                    base_node=pep_field,
                )
                msgid = self.document.set_id(msg)
                prb = nodes.problematic(value, value or "(none)", refid=msgid)
                prbid = self.document.set_id(prb)
                msg.add_backref(prbid)
                if len(pep_field[1]):
                    pep_field[1][0][:] = [prb]
                else:
                    pep_field[1] += nodes.paragraph("", "", prb)

        if pep is None:
            raise DataError('Document does not contain an RFC-2822 "PEP" ' "header.")

        if pep == 0:
            # Special processing for PEP 0.
            pending = nodes.pending(pep_zero.PEPZero)
            self.document.insert(1, pending)
            self.document.note_pending(pending)

        # If there are less than two headers in the preamble, or if Title is absent
        if len(header) < 2 or header[1][0].astext().lower() != "title":
            raise DataError("No title!")

        fields_to_remove = []
        for field in header:
            name = field[0].astext().lower()
            body = field[1]
            if len(body) > 1:
                raise DataError(f"PEP header field body contains multiple elements:\n{field.pformat(level=1)}")
            elif len(body) == 1:
                if not isinstance(body[0], nodes.paragraph):
                    raise DataError(f"PEP header field body may only contain a single paragraph:\n{field.pformat(level=1)}")
            else:
                # body is empty
                continue

            para = body[0]
            if name in ("author", "bdfl-delegate", "sponsor"):
                for node in para:
                    if isinstance(node, nodes.reference):
                        node.replace_self(peps.mask_email(node))
            elif name == "discussions-to":
                for node in para:
                    if isinstance(node, nodes.reference):
                        node.replace_self(peps.mask_email(node, pep))
            elif name in ("replaces", "superseded-by", "requires"):
                newbody = []
                space = nodes.Text(" ")
                for refpep in re.split(r",?\s+", body.astext()):
                    pepno = int(refpep)
                    newbody.append(nodes.reference(
                        refpep, refpep,
                        refuri=(self.document.settings.pep_base_url + pep_url.format(pepno))))
                    newbody.append(space)
                para[:] = newbody[:-1]  # drop trailing space
            elif name in ("last-modified", "content-type", "version"):
                fields_to_remove.append(field)

        for field in fields_to_remove:
            field.parent.remove(field)
