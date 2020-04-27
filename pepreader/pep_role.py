import re

from typing import List, Tuple, Dict

from docutils import nodes
from docutils.nodes import Node, system_message
from docutils.parsers.rst.states import Inliner
from docutils.utils import unescape

from sphinx import addnodes
from sphinx.errors import SphinxError
from sphinx.locale import _

import pepreader

if False:
    # For type annotation
    from typing import Type  # for python3.5.1
    from sphinx.builders import Builder
    from sphinx.config import Config
    from sphinx.environment import BuildEnvironment

class PEPRole:
    """A base class for reference roles.

    The reference roles can accpet ``link title <target>`` style as a text for
    the role.  The parsed result; link title and target will be stored to
    ``self.title`` and ``self.target``.
    """
    has_explicit_title = None   #: A boolean indicates the role has explicit title or not.
    disabled = False            #: A boolean indicates the reference is disabled.
    title = None                #: The link title for the interpreted text.
    target = None               #: The link target for the interpreted text.

    # \x00 means the "<" was backslash-escaped
    explicit_title_re = re.compile(r'^(.+?)\s*(?<!\x00)<(.*?)>$', re.DOTALL)

    # From ReferenceRole
    def __call__(self, name: str, rawtext: str, text: str, lineno: int,
                 inliner: Inliner, options: Dict = {}, content: List[str] = []
                 ) -> Tuple[List[Node], List[system_message]]:
        # if the first character is a bang, don't cross-reference at all
        self.disabled = text.startswith('!')

        matched = self.explicit_title_re.match(text)
        if matched:
            self.has_explicit_title = True
            self.title = unescape(matched.group(1))
            self.target = unescape(matched.group(2))
        else:
            self.has_explicit_title = False
            self.title = unescape(text)
            self.target = unescape(text)

        # From SphinxRole
        self.rawtext = rawtext
        self.text = unescape(text)
        self.lineno = lineno
        self.inliner = inliner
        self.options = options
        self.content = content

        # guess role type
        if name:
            self.name = name.lower()
        else:
            self.name = self.env.temp_data.get('default_role')
            if not self.name:
                self.name = self.env.config.default_role
            if not self.name:
                raise SphinxError('cannot determine default role!')

        return self.run()

    @property
    def env(self) -> "BuildEnvironment":
        """Reference to the :class:`.BuildEnvironment` object."""
        return self.inliner.document.settings.env

    @property
    def config(self) -> "Config":
        """Reference to the :class:`.Config` object."""
        return self.env.config

    def get_source_info(self, lineno: int = None) -> Tuple[str, int]:
        if lineno is None:
            lineno = self.lineno
        return self.inliner.reporter.get_source_and_line(lineno)  # type: ignore

    def set_source_info(self, node: Node, lineno: int = None) -> None:
        node.source, node.line = self.get_source_info(lineno)

    def run(self) -> Tuple[List[Node], List[system_message]]:
        target_id = 'index-%s' % self.env.new_serialno('index')
        entries = [('single', _('Python Enhancement Proposals; PEP %s') % self.target,
                    target_id, '', None)]

        index = addnodes.index(entries=entries)
        target = nodes.target('', '', ids=[target_id])
        self.inliner.document.note_explicit_target(target)

        try:
            refuri = self.build_uri()
            reference = nodes.reference('', '', internal=False, refuri=refuri, classes=['pep'])
            if self.has_explicit_title:
                reference += nodes.strong(self.title, self.title)
            else:
                title = "PEP " + self.title
                reference += nodes.strong(title, title)
        except ValueError:
            msg = self.inliner.reporter.error('invalid PEP number %s' % self.target,
                                              line=self.lineno)
            prb = self.inliner.problematic(self.rawtext, self.rawtext, msg)
            return [prb], [msg]

        return [index, target, reference], []

    def build_uri(self) -> str:
        base_url = self.inliner.document.settings.pep_base_url
        ret = self.target.split('#', 1)
        if len(ret) == 2:
            return base_url + (pepreader.pep_url + '#{}').format(int(ret[0]), ret[1])
        else:
            return base_url + pepreader.pep_url.format(int(ret[0]))