# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
Python Enhancement Proposal (PEP) Reader.
"""

__docformat__ = 'reStructuredText'


import sys
import os
import re
from docutils import nodes
from docutils.readers import standalone
from docutils.transforms import peps, references
from docutils.parsers import rst


class Reader(standalone.Reader):

    supported = ('pep',)
    """Contexts this reader supports."""

    settings_spec = (
        'PEP Reader Option Defaults',
        'The --pep-references and --rfc-references options (for the '
        'reStructuredText parser) are on by default.',
        ())

    default_transforms = (references.Substitutions,
                          peps.Headers,
                          peps.Contents,
                          references.ChainedTargets,
                          references.AnonymousHyperlinks,
                          references.IndirectHyperlinks,
                          peps.TargetNotes,
                          references.Footnotes,
                          references.ExternalTargets,
                          references.InternalTargets,)

    settings_default_overrides = {'pep_references': 1, 'rfc_references': 1}

    def __init__(self, parser=None, parser_name=None):
        """`parser` should be ``None``."""
        if parser is None:
            parser = rst.Parser(rfc2822=1, inliner=Inliner())
        standalone.Reader.__init__(self, parser, '')


class Inliner(rst.states.Inliner):

    """
    Extend `rst.Inliner` to for local PEP references.
    """

    pep_url = rst.states.Inliner.pep_url_local
