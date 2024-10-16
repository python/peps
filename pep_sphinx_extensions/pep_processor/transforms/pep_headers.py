from pathlib import Path
import re

from docutils import nodes
from docutils import transforms
from sphinx import errors

from pep_sphinx_extensions.pep_processor.transforms import pep_zero
from pep_sphinx_extensions.pep_processor.transforms.pep_zero import _mask_email
from pep_sphinx_extensions.pep_zero_generator.constants import (
    SPECIAL_STATUSES,
    STATUS_ACCEPTED,
    STATUS_ACTIVE,
    STATUS_DEFERRED,
    STATUS_DRAFT,
    STATUS_FINAL,
    STATUS_PROVISIONAL,
    STATUS_REJECTED,
    STATUS_SUPERSEDED,
    STATUS_WITHDRAWN,
    TYPE_INFO,
    TYPE_PROCESS,
    TYPE_STANDARDS,
)

ABBREVIATED_STATUSES = {
    STATUS_DRAFT: "Proposal under active discussion and revision",
    STATUS_DEFERRED: "Inactive draft that may be taken up again at a later time",
    STATUS_ACCEPTED: "Normative proposal accepted for implementation",
    STATUS_ACTIVE: "Currently valid informational guidance, or an in-use process",
    STATUS_FINAL: "Accepted and implementation complete, or no longer active",
    STATUS_WITHDRAWN: "Removed from consideration by sponsor or authors",
    STATUS_REJECTED: "Formally declined and will not be accepted",
    STATUS_SUPERSEDED: "Replaced by another succeeding PEP",
    STATUS_PROVISIONAL: "Provisionally accepted but additional feedback needed",
}

ABBREVIATED_TYPES = {
    TYPE_STANDARDS: "Normative PEP with a new feature for Python, implementation "
    "change for CPython or interoperability standard for the ecosystem",
    TYPE_INFO: "Non-normative PEP containing background, guidelines or other "
    "information relevant to the Python ecosystem",
    TYPE_PROCESS: "Normative PEP describing or proposing a change to a Python "
    "community process, workflow or governance",
}

class PEPParsingError(errors.SphinxError):
    pass


# PEPHeaders is identical to docutils.transforms.peps.Headers excepting bdfl-delegate, sponsor & superseeded-by
class PEPHeaders(transforms.Transform):
    """Process fields in a PEP's initial RFC-2822 header."""

    # Run before pep_processor.transforms.pep_title.PEPTitle
    default_priority = 330

    def apply(self) -> None:
        if not Path(self.document["source"]).match("pep-*"):
            return  # not a PEP file, exit early

        if not len(self.document):
            raise PEPParsingError("Document tree is empty.")

        header = self.document[0]
        if not isinstance(header, nodes.field_list) or "rfc2822" not in header["classes"]:
            raise PEPParsingError("Document does not begin with an RFC-2822 header; it is not a PEP.")

        # PEP number should be the first field
        pep_field = header[0]
        if pep_field[0].astext().lower() != "pep":
            raise PEPParsingError("Document does not contain an RFC-2822 'PEP' header!")

        # Extract PEP number
        pep_num_str = pep_field[1].astext()
        try:
            pep_num = int(pep_num_str)
        except ValueError:
            raise PEPParsingError(f"PEP header must contain an integer. '{pep_num_str}' is invalid!")

        # Special processing for PEP 0.
        if pep_num == 0:
            pending = nodes.pending(pep_zero.PEPZero)
            self.document.insert(1, pending)
            self.document.note_pending(pending)

        # If there are less than two headers in the preamble, or if Title is absent
        if len(header) < 2 or header[1][0].astext().lower() != "title":
            raise PEPParsingError("No title!")

        fields_to_remove = []
        self.document["headers"] = headers = {}
        for field in header:
            row_attributes = {sub.tagname: sub.rawsource for sub in field}
            headers[row_attributes["field_name"]] = row_attributes["field_body"]

            name = field[0].astext().lower()
            body = field[1]
            if len(body) == 0:
                # body is empty
                continue
            elif len(body) > 1:
                msg = f"PEP header field body contains multiple elements:\n{field.pformat(level=1)}"
                raise PEPParsingError(msg)
            elif not isinstance(body[0], nodes.paragraph):  # len(body) == 1
                msg = f"PEP header field body may only contain a single paragraph:\n{field.pformat(level=1)}"
                raise PEPParsingError(msg)

            para = body[0]
            if name in {"author", "bdfl-delegate", "pep-delegate", "sponsor"}:
                # mask emails
                for node in para:
                    if not isinstance(node, nodes.reference):
                        continue
                    node.replace_self(_mask_email(node))
            elif name in {"discussions-to", "resolution", "post-history"}:
                # Prettify mailing list and Discourse links
                for node in para:
                    if (not isinstance(node, nodes.reference)
                            or not node["refuri"]):
                        continue
                    # If the Resolution header is already a link, don't prettify it
                    if name == "resolution" and node["refuri"] != node[0]:
                        continue
                    # Have known mailto links link to their main list pages
                    if node["refuri"].lower().startswith("mailto:"):
                        node["refuri"] = _generate_list_url(node["refuri"])
                    parts = node["refuri"].lower().split("/")
                    if len(parts) <= 2 or parts[2] not in LINK_PRETTIFIERS:
                        continue
                    pretty_title = _make_link_pretty(str(node["refuri"]))
                    if name == "post-history":
                        node["reftitle"] = pretty_title
                    else:
                        node[0] = nodes.Text(pretty_title)
            elif name in {"replaces", "superseded-by", "requires"}:
                # replace PEP numbers with normalised list of links to PEPs
                new_body = []
                for pep_str in re.split(r",?\s+", body.astext()):
                    target = self.document.settings.pep_url.format(int(pep_str))
                    if self.document.settings.builder == "dirhtml":
                        target = f"../{target}"
                    new_body += [nodes.reference("", pep_str, refuri=target), nodes.Text(", ")]
                para[:] = new_body[:-1]  # drop trailing space
            elif name == "topic":
                new_body = []
                for topic_name in body.astext().split(","):
                    if topic_name:
                        target = f"topic/{topic_name.lower().strip()}"
                        if self.document.settings.builder == "html":
                            target = f"{target}.html"
                        else:
                            target = f"../{target}/"
                        new_body += [
                            nodes.reference("", topic_name, refuri=target),
                            nodes.Text(", "),
                        ]
                if new_body:
                    para[:] = new_body[:-1]  # Drop trailing space/comma
            elif name == "status":
                para[:] = [
                    nodes.abbreviation(
                        body.astext(),
                        body.astext(),
                        explanation=_abbreviate_status(body.astext()),
                    )
                ]
            elif name == "type":
                para[:] = [
                    nodes.abbreviation(
                        body.astext(),
                        body.astext(),
                        explanation=_abbreviate_type(body.astext()),
                    )
                ]
            elif name in {"last-modified", "content-type", "version"}:
                # Mark unneeded fields
                fields_to_remove.append(field)

            # Remove any trailing commas and whitespace in the headers
            if para and isinstance(para[-1], nodes.Text):
                last_node = para[-1]
                if last_node.astext().strip() == ",":
                    last_node.parent.remove(last_node)
                else:
                    para[-1] = last_node.rstrip().rstrip(",")

        # Remove unneeded fields
        for field in fields_to_remove:
            field.parent.remove(field)


def _generate_list_url(mailto: str) -> str:
    list_name_domain = mailto.lower().removeprefix("mailto:").strip()
    list_name = list_name_domain.split("@")[0]

    if list_name_domain.endswith("@googlegroups.com"):
        return f"https://groups.google.com/g/{list_name}"

    if not list_name_domain.endswith("@python.org"):
        return mailto

    # Active lists not yet on Mailman3; this URL will redirect if/when they are
    if list_name in {"csv", "db-sig", "doc-sig", "python-list", "web-sig"}:
        return f"https://mail.python.org/mailman/listinfo/{list_name}"
    # Retired lists that are closed for posting, so only the archive matters
    if list_name in {"import-sig", "python-3000"}:
        return f"https://mail.python.org/pipermail/{list_name}/"
    # The remaining lists (and any new ones) are all on Mailman3/Hyperkitty
    return f"https://mail.python.org/archives/list/{list_name}@python.org/"


def _process_list_url(parts: list[str]) -> tuple[str, str]:
    item_type = "list"

    # HyperKitty (Mailman3) archive structure is
    # https://mail.python.org/archives/list/<list_name>/thread/<id>
    if "archives" in parts:
        list_name = (
            parts[parts.index("archives") + 2].removesuffix("@python.org"))
        if len(parts) > 6 and parts[6] in {"message", "thread"}:
            item_type = parts[6]

    # Mailman3 list info structure is
    # https://mail.python.org/mailman3/lists/<list_name>.python.org/
    elif "mailman3" in parts:
        list_name = (
            parts[parts.index("mailman3") + 2].removesuffix(".python.org"))

    # Pipermail (Mailman) archive structure is
    # https://mail.python.org/pipermail/<list_name>/<month>-<year>/<id>
    elif "pipermail" in parts:
        list_name = parts[parts.index("pipermail") + 1]
        item_type = "message" if len(parts) > 6 else "list"

    # Mailman listinfo structure is
    # https://mail.python.org/mailman/listinfo/<list_name>
    elif "listinfo" in parts:
        list_name = parts[parts.index("listinfo") + 1]

    # Not a link to a mailing list, message or thread
    else:
        raise ValueError(
            f"{'/'.join(parts)} not a link to a list, message or thread")

    return list_name, item_type


def _process_discourse_url(parts: list[str]) -> tuple[str, str]:
    item_name = "discourse"

    if len(parts) < 5 or ("t" not in parts and "c" not in parts):
        raise ValueError(
            f"{'/'.join(parts)} not a link to a Discourse thread or category")

    first_subpart = parts[4]
    has_title = not first_subpart.isnumeric()

    if "t" in parts:
        item_type = "message" if len(parts) > (5 + has_title) else "thread"
    elif "c" in parts:
        item_type = "category"
        if has_title:
            item_name = f"{first_subpart.replace('-', ' ')} {item_name}"

    return item_name, item_type


# Domains supported for pretty URL parsing
LINK_PRETTIFIERS = {
    "mail.python.org": _process_list_url,
    "discuss.python.org": _process_discourse_url,
}


def _process_pretty_url(url: str) -> tuple[str, str]:
    parts = url.lower().strip().strip("/").split("/")
    try:
        item_name, item_type = LINK_PRETTIFIERS[parts[2]](parts)
    except KeyError as error:
        raise ValueError(
            f"{url} not a link to a recognized domain to prettify") from error
    item_name = item_name.title().replace("Sig", "SIG").replace("Pep", "PEP")
    return item_name, item_type


def _make_link_pretty(url: str) -> str:
    item_name, item_type = _process_pretty_url(url)
    return f"{item_name} {item_type}"


def _abbreviate_status(status: str) -> str:
    if status in SPECIAL_STATUSES:
        status = SPECIAL_STATUSES[status]

    try:
        return ABBREVIATED_STATUSES[status]
    except KeyError:
        raise PEPParsingError(f"Unknown status: {status}")


def _abbreviate_type(type_: str) -> str:
    try:
        return ABBREVIATED_TYPES[type_]
    except KeyError:
        raise PEPParsingError(f"Unknown type: {type_}")
