from pathlib import Path

from docutils import nodes
from docutils import transforms


class PEPReferenceRoleTitleText(transforms.Transform):
    """Add title text of document titles to reference role references."""

    default_priority = 730

    def apply(self) -> None:
        if not Path(self.document["source"]).match("pep-*"):
            return  # not a PEP file, exit early
        for node in self.document.findall(nodes.reference):
            if "_title_tuple" not in node:
                continue

            # get pep number and section target (fragment)
            pep_num, fragment = node.attributes.pop("_title_tuple")
            filename = f"pep-{pep_num:0>4}"

            # Cache target_ids
            env = self.document.settings.env
            try:
                target_ids = env.document_ids[filename]
            except KeyError:
                env.document_ids[filename] = target_ids = env.get_doctree(filename).ids

            # Create title text string. We hijack the 'reftitle' attribute so
            # that we don't have to change things in the HTML translator
            node["reftitle"] = env.titles[filename].astext()
            try:
                node["reftitle"] += f" § {target_ids[fragment][0].astext()}"
            except KeyError:
                pass
