# Author: Stefane Fermigier
# Contact: sf@fermigier.com
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
French-language mappings for language-dependent features of Docutils.
"""

__docformat__ = 'reStructuredText'


from docutils import nodes


labels = {
      'author': 'Auteur',
      'authors': 'Auteurs',
      'organization': 'Organisation',
      'address': 'Adresse',
      'contact': 'Contact',
      'version': 'Version',
      'revision': 'R\u00e9vision',
      'status': 'Statut',
      'date': 'Date',
      'copyright': 'Copyright',
      'dedication': 'D\u00e9dicace',
      'abstract': 'R\u00e9sum\u00e9',
      'attention': 'Attention!',
      'caution': 'Avertissement!',
      'danger': '!DANGER!',
      'error': 'Erreur',
      'hint': 'Indication',
      'important': 'Important',
      'note': 'Note',
      'tip': 'Astuce',
      'warning': 'Avertissement',
      'contents': 'Contenu'}
"""Mapping of node class name to label text."""

bibliographic_fields = {
      'auteur': nodes.author,
      'auteurs': nodes.authors,
      'organisation': nodes.organization,
      'adresse': nodes.address,
      'contact': nodes.contact,
      'version': nodes.version,
      'r\u00e9vision': nodes.revision,
      'status': nodes.status,
      'date': nodes.date,
      'copyright': nodes.copyright,
      'd\u00e9dicace': nodes.topic,
      'r\u00e9sum\u00e9': nodes.topic}
"""Field name (lowcased) to node class name mapping for bibliographic fields
(field_list)."""

author_separators = [';', ',']
"""List of separator strings for the 'Authors' bibliographic field. Tried in
order."""
