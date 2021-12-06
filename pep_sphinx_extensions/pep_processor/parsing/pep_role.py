from sphinx import roles

from pep_sphinx_extensions import config


class PEPRole(roles.PEP):
    """Override the :pep: role"""

    def build_uri(self) -> str:
        """Get PEP URI from role text."""
        pep_str, _, fragment = self.target.partition("#")
        pep_base = config.pep_url.format(int(pep_str))
        if fragment:
            return f"{pep_base}#{fragment}"
        return pep_base
