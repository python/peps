"""Roles to insert custom admonitions pointing readers to canonical content."""

from __future__ import annotations

from docutils import nodes
from docutils.parsers import rst


class CanonicalContent(rst.Directive):
    """Insert an admonition pointing readers to a PEP's canonical content."""

    has_content = True
    required_arguments = 0
    optional_arguments = 2
    final_argument_whitespace = True
    option_spec = {}

    default_canonical_link_title = "the Python docs"
    default_canonical_link_uri = "https://docs.python.org/"
    generic_canonical_link_title = "this link"
    use_default_link = True

    admonition_pre_template = (
        "This PEP is a historical document; the up-to-date, canonical "
        "documentation can now be found at `{link_title} <{link_uri}>`__."
    )
    admonition_pre_text = (
        "This PEP is a historical document; the up-to-date, canonical "
        "documentation can now be found elsewhere."
    )
    admonition_post_text = (
        "See :pep:`1` for how to propose changes."
    )


    def run(self) -> list[nodes.admonition]:

        if self.arguments or (self.use_default_link and not self.content):
            if self.arguments:
                link_title = self.generic_canonical_link_title
                link_uri = self.arguments[0]
                if len(self.arguments) >= 2:
                    link_title = self.arguments[1]
            else:
                link_title = self.default_canonical_link_title
                link_uri = self.default_canonical_link_uri

            pre_text = self.admonition_pre_template.format(
                link_uri=link_uri, link_title=link_title)

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
        admonition_node = nodes.important(
            "\n".join(source_lines), classes=["canonical-content"])

        admonition_node.append(pre_text_node)
        if self.content:
            self.state.nested_parse(
                self.content, self.content_offset, admonition_node)
        admonition_node.append(post_text_node)

        return [admonition_node]


class CanonicalContentPyPA(CanonicalContent):
    """Insert a specialized admonition for PyPA packaging specifications."""

    generic_canonical_link_title = "packaging"
    use_default_link = False

    admonition_pre_template = (
        "This PEP is a historical document; the up-to-date, canonical "
        "`{link_title} specification "
        "<https://packaging.python.org/en/latest/specifications/{link_uri}/>`__ "
        "is maintained on the `PyPA specs page "
        "<https://packaging.python.org/en/latest/specifications/index.html>`__."
    )
    admonition_pre_text = (
        "This PEP is a historical document; the up-to-date, canonical "
        "specification is maintained on the `PyPA specs page "
        "<https://packaging.python.org/en/latest/specifications/index.html>`__."
    )
    admonition_post_text = (
        "See the `PyPA specification update process "
        "<https://www.pypa.io/en/latest/specifications/#handling-fixes-and-other-minor-updates>`__ "
        "for how to propose changes."
    )
