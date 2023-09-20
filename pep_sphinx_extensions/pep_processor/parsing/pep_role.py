from docutils import nodes
from sphinx import roles


class PEPRole(roles.ReferenceRole):
    """Override the :pep: role"""

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        # Get PEP URI from role text.
        pep_str, _, fragment = self.target.partition("#")
        try:
            pep_num = int(pep_str)
        except ValueError:
            msg = self.inliner.reporter.error(f'invalid PEP number {self.target}', line=self.lineno)
            prb = self.inliner.problematic(self.rawtext, self.rawtext, msg)
            return [prb], [msg]
        pep_base = self.inliner.document.settings.pep_url.format(pep_num)
        if self.inliner.document.settings.builder == "dirhtml":
            pep_base = "../" + pep_base
        if "topic" in self.get_location():
            pep_base = "../" + pep_base
        if fragment:
            ref_uri = f"{pep_base}#{fragment}"
        else:
            ref_uri = pep_base
        if self.has_explicit_title:
            title = self.title
        else:
            title = f"PEP {pep_num}"

        return [
            nodes.reference(
                "", title,
                internal=True,
                refuri=ref_uri,
                classes=["pep"],
                _title_tuple=(pep_num, fragment)
            )
        ], []
