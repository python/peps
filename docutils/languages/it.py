# Author: Nicola Larosa
# Contact: docutils@tekNico.net
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
Italian-language mappings for language-dependent features of Docutils.
"""

__docformat__ = 'reStructuredText'


from docutils import nodes


labels = {
      'author': 'Autore',
      'authors': 'Autori',
      'organization': 'Organizzazione',
      'address': 'Indirizzo',
      'contact': 'Contatti',
      'version': 'Versione',
      'revision': 'Revisione',
      'status': 'Status',
      'date': 'Data',
      'copyright': 'Copyright',
      'dedication': 'Dedica',
      'abstract': 'Riassunto',
      'attention': 'Attenzione!',
      'caution': 'Cautela!',
      'danger': '!PERICOLO!',
      'error': 'Errore',
      'hint': 'Suggerimento',
      'important': 'Importante',
      'note': 'Nota',
      'tip': 'Consiglio',
      'warning': 'Avvertenza',
      'contents': 'Indice'}
"""Mapping of node class name to label text."""

bibliographic_fields = {
      'autore': nodes.author,
      'autori': nodes.authors,
      'organizzazione': nodes.organization,
      'indirizzo': nodes.address,
      'contatti': nodes.contact,
      'versione': nodes.version,
      'revisione': nodes.revision,
      'status': nodes.status,
      'data': nodes.date,
      'copyright': nodes.copyright,
      'dedica': nodes.topic,
      'riassunto': nodes.topic}
"""Field name (lowcased) to node class name mapping for bibliographic fields
(field_list)."""

author_separators = [';', ',']
"""List of separator strings for the 'Authors' bibliographic field. Tried in
order."""
