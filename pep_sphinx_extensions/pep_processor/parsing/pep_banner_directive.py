"""Roles to insert custom admonitions pointing readers to canonical content."""

from __future__ import annotations

from docutils import nodes
from docutils.parsers import rst

PYPA_SPEC_BASE_URL = "https://packaging.python.org/en/latest/specifications/"
TYPING_SPEC_BASE_URL = "https://typing.readthedocs.io/en/latest/spec/"


class PEPBanner(rst.Directive):
    """Insert a special banner admonition in a PEP document."""

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True
    option_spec = {}

    admonition_pre_template = ""
    admonition_pre_text = ""
    admonition_post_text = ""

    admonition_class = nodes.important
    css_classes = []

    def run(self) -> list[nodes.admonition]:

        if self.arguments:
            link_content = self.arguments[0]
            pre_text = self.admonition_pre_template.format(
                link_content=link_content)
        else:
            pre_text = self.admonition_pre_text

        close_button_node = nodes.paragraph('', '', nodes.Text('×'), classes=['close-button'])
        close_button_node['classes'].append('close-button')

        pre_text_node = nodes.paragraph(pre_text)
        pre_text_node.line = self.lineno
        pre_node, pre_msg = self.state.inline_text(pre_text, self.lineno)
        pre_text_node.extend(pre_node + pre_msg)

        post_text = self.admonition_post_text
        post_text_node = nodes.paragraph(post_text)
        post_text_node.line = self.lineno
        post_node, post_msg = self.state.inline_text(post_text, self.lineno)
        post_text_node.extend(post_node + post_msg)

        source_lines = [pre_text] + list(self.content or []) + [post_text]
        admonition_node = self.admonition_class(
            "\n".join(source_lines), classes=["pep-banner"] + self.css_classes)

        admonition_node.append(pre_text_node)
        admonition_node.append(close_button_node)
        if self.content:
            self.state.nested_parse(
                self.content, self.content_offset, admonition_node)
        admonition_node.append(post_text_node)

        return [admonition_node]


class CanonicalDocBanner(PEPBanner):
    """Insert an admonition pointing readers to a PEP's canonical docs."""

    admonition_pre_template = (
        "This PEP is a historical document. "
        "The up-to-date, canonical documentation can now be found "
        "at {link_content}."
    )
    admonition_pre_text = (
        "This PEP is a historical document. "
        "The up-to-date, canonical documentation can now be found elsewhere."
    )
    admonition_post_text = (
        "See :pep:`1` for how to propose changes."
    )

    css_classes = ["canonical-doc", "sticky-banner"]


class CanonicalPyPASpecBanner(PEPBanner):
    """Insert a specialized admonition for PyPA packaging specifications."""

    admonition_pre_template = (
        "This PEP is a historical document. "
        "The up-to-date, canonical spec, {link_content}, is maintained on "
        f"the `PyPA specs page <{PYPA_SPEC_BASE_URL}>`__."
    )
    admonition_pre_text = (
        "This PEP is a historical document. "
        "The up-to-date, canonical specifications are maintained on "
        f"the `PyPA specs page <{PYPA_SPEC_BASE_URL}>`__."
    )
    admonition_post_text = (
        "See the `PyPA specification update process "
        "<https://www.pypa.io/en/latest/specifications/#handling-fixes-and-other-minor-updates>`__ "
        "for how to propose changes."
    )
    admonition_class = nodes.attention

    css_classes = ["canonical-pypa-spec", "sticky-banner"]


class CanonicalTypingSpecBanner(PEPBanner):
    """Insert a specialized admonition for the typing specification."""

    admonition_pre_template = (
        "This PEP is a historical document. "
        "The up-to-date, canonical spec, {link_content}, is maintained on "
        f"the `typing specs site <{TYPING_SPEC_BASE_URL}>`__."
    )
    admonition_pre_text = (
        "This PEP is a historical document. "
        "The up-to-date, canonical specifications are maintained on "
        f"the `typing specs site <{TYPING_SPEC_BASE_URL}>`__."
    )
    admonition_post_text = (
        "See the `typing specification update process "
        "<https://typing.readthedocs.io/en/latest/spec/meta.html>`__ "
        "for how to propose changes."
    )
    admonition_class = nodes.attention

    css_classes = ["canonical-typing-spec", "sticky-banner"]


class DeprecatedBanner(PEPBanner):
    """Generic admonition for deprecated PEPs."""

    admonition_class = nodes.warning
    admonition_pre_template = "{link_content}"
    admonition_pre_text = "This PEP has been deprecated."
    css_classes = ["sticky-banner", "deprecated"]


class RejectedBanner(DeprecatedBanner):
    """Insert an admonition for rejected PEPs."""

    admonition_pre_text = "This PEP has been rejected."
    css_classes = ["sticky-banner", "deprecated", "rejected"]


class SupersededBanner(PEPBanner):
    """Insert an admonition for superseded PEPs."""

    admonition_pre_template = "This PEP has been superseded by :pep:`{link_content}`."
    admonition_pre_text = "This PEP has been superseded."
    css_classes = ["sticky-banner", "deprecated", "superseded"]


class WithdrawnBanner(PEPBanner):
    """Insert an admonition for withdrawn PEPs."""

    admonition_pre_text = "This PEP has been withdrawn."
    css_classes = ["sticky-banner", "deprecated", "withdrawn"]
