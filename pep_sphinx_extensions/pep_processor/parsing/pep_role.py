from sphinx import roles


class PEPRole(roles.PEP):
    """Override the :pep: role"""
    # TODO override the entire thing (internal should be True)

    def build_uri(self) -> str:
        """Get PEP URI from role text."""
        pep_str, _, fragment = self.target.partition("#")
        pep_base = self.inliner.document.settings.pep_url.format(int(pep_str))
        if fragment:
            return f"{pep_base}#{fragment}"
        return pep_base
