# Authors:   David Goodger; Gunnar Schwant
# Contact:   goodger@users.sourceforge.net
# Revision:  $Revision$
# Date:      $Date$
# Copyright: This module has been placed in the public domain.

"""
German language mappings for language-dependent features of Docutils.
"""

__docformat__ = 'reStructuredText'

from docutils import nodes


labels = {
    'author': 'Autor',
    'authors': 'Autoren',
    'organization': 'Organisation',
    'address': 'Adresse',
    'contact': 'Kontakt',
    'version': 'Version',
    'revision': 'Revision',
    'status': 'Status',
    'date': 'Datum',
    'dedication': 'Widmung',
    'copyright': 'Copyright',
    'abstract': 'Zusammenfassung',
    'attention': 'Achtung!',
    'caution': 'Vorsicht!',
    'danger': '!GEFAHR!',
    'error': 'Fehler',
    'hint': 'Hinweis',
    'important': 'Wichtig',
    'note': 'Bemerkung',
    'tip': 'Tipp',
    'warning': 'Warnung',
    'contents': 'Inhalt'}
"""Mapping of node class name to label text."""

bibliographic_fields = {
    'autor': nodes.author,
    'autoren': nodes.authors,
    'organisation': nodes.organization,
    'adresse': nodes.address,
    'kontakt': nodes.contact,
    'version': nodes.version,
    'revision': nodes.revision,
    'status': nodes.status,
    'datum': nodes.date,
    'copyright': nodes.copyright,
    'widmung': nodes.topic,
    'zusammenfassung': nodes.topic}
"""Field name (lowcased) to node class name mapping for bibliographic fields
(field_list)."""

author_separators = [';', ',']
"""List of separator strings for the 'Authors' bibliographic field. Tried in
order."""
