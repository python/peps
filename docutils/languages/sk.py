# :Author: Miroslav Vasko
# :Contact: zemiak@zoznam.sk
# :Revision: $Revision$
# :Date: $Date$
# :Copyright: This module has been placed in the public domain.

"""
Slovak-language mappings for language-dependent features of Docutils.
"""

__docformat__ = 'reStructuredText'


from docutils import nodes


labels = {
      'author': u'Autor',
      'authors': u'Autori',
      'organization': u'Organiz\u00E1cia',
      'address': u'Adresa',
      'contact': u'Kontakt',
      'version': u'Verzia',
      'revision': u'Rev\u00EDzia',
      'status': u'Stav',
      'date': u'D\u00E1tum',
      'copyright': u'Copyright',
      'dedication': u'Venovanie',
      'abstract': u'Abstraktne',
      'attention': u'Pozor!',
      'caution': u'Opatrne!',
      'danger': u'!NEBEZPE\u010cENSTVO!',
      'error': u'Chyba',
      'hint': u'Rada',
      'important': u'D\u00F4le\u017Eit\u00E9',
      'note': u'Pozn\u00E1mka',
      'tip': u'Tip',
      'warning': u'Varovanie',
      'contents': u'Obsah'}
"""Mapping of node class name to label text."""

bibliographic_fields = {
      u'autor': nodes.author,
      u'autori': nodes.authors,
      u'organiz\u00E1cia': nodes.organization,
      u'adresa': nodes.address,
      u'kontakt': nodes.contact,
      u'verzia': nodes.version,
      u'rev\u00EDzia': nodes.revision,
      u'stav': nodes.status,
      u'D\u00E1tum': nodes.date,
      u'copyright': nodes.copyright,
      u'venovanie': nodes.topic,
      u'abstraktne': nodes.topic}
"""Field name (lowcased) to node class name mapping for bibliographic fields
(field_list)."""

author_separators = [';', ',']
"""List of separator strings for the 'Authors' bibliographic field. Tried in
order."""
