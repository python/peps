from sphinx import roles

from pep_sphinx_extensions.config import pep_url


class PEPRole(roles.PEP):
    """Override the :pep: role"""

    def build_uri(self) -> str:
        """Get PEP URI from role text."""
        base_url = self.inliner.document.settings.pep_base_url
        pep_num, _, fragment = self.target.partition("#")
        pep_base = base_url + pep_url.format(int(pep_num))
        if fragment:
            return f"{pep_base}#{fragment}"
        return pep_base
