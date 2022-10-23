"""Roles to insert custom admonitions pointing readers to canonical content."""

from __future__ import annotations

from docutils import nodes
from docutils.parsers import rst


PYPA_SPEC_BASE_URL = "https://packaging.python.org/en/latest/specifications/"


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
    css_classes = ["pep-banner"]


    def run(self) -> list[nodes.admonition]:

        if self.arguments:
            link_content = self.arguments[0]
            pre_text = self.admonition_pre_template.format(
                link_content=link_content)
        else:
            pre_text = self.admonition_pre_text

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
            "\n".join(source_lines), classes=self.css_classes)

        admonition_node.append(pre_text_node)
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

    css_classes = [*PEPBanner.css_classes, "canonical-doc"]



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

    css_classes = [*PEPBanner.css_classes, "canonical-pypa-spec"]
