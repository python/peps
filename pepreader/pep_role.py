from sphinx import roles
import pepreader


class PEPRole(roles.PEP):

    def build_uri(self) -> str:
        base_url = self.inliner.document.settings.pep_base_url
        ret = self.target.split('#', 1)
        if len(ret) == 2:
            return base_url + (pepreader.pep_url + '#{}').format(int(ret[0]), ret[1])
        else:
            return base_url + pepreader.pep_url.format(int(ret[0]))
