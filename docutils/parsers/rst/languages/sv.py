# Author:    Adam Chodorowski
# Contact:   chodorowski@users.sourceforge.net
# Revision:  $Revision$
# Date:      $Date$
# Copyright: This module has been placed in the public domain.

"""
Swedish language mappings for language-dependent features of reStructuredText.
"""

__docformat__ = 'reStructuredText'


directives = {
      u'observera': 'attention',
      u'varning': 'caution',
      u'fara': 'danger',
      u'fel': 'error',
      u'v\u00e4gledning': 'hint',
      u'viktigt': 'important',
      u'notera': 'note',
      u'tips': 'tip',
      u'varning': 'warning',
      # u'fr\u00e5gor': 'questions',
      # NOTE: A bit long, but recommended by http://www.nada.kth.se/dataterm/:
      # u'fr\u00e5gor-och-svar': 'questions',
      # u'vanliga-fr\u00e5gor': 'questions',  
      u'meta': 'meta',
      # u'bildkarta': 'imagemap',   # FIXME: Translation might be too literal.
      u'bild': 'image',
      u'figur': 'figure',
      u'r\u00e5': 'raw',            # FIXME: Translation might be too literal.
      u'inneh\u00e5ll': 'contents',
      # u'fotnoter': 'footnotes',
      # u'citeringar': 'citations',
      u'\u00e4mne': 'topic'}
"""Swedish name to registered (in directives/__init__.py) directive name
mapping."""
