# Author:    Adam Chodorowski
# Contact:   chodorowski@users.sourceforge.net
# Revision:  $Revision$
# Date:      $Date$
# Copyright: This module has been placed in the public domain.

"""
Swedish language mappings for language-dependent features of Docutils.
"""

__docformat__ = 'reStructuredText'


from docutils import nodes


labels = {
    'author':       u'F\u00f6rfattare',
    'authors':      u'F\u00f6rfattare',
    'organization': u'Organisation',
    'address':      u'Adress',
    'contact':      u'Kontakt',
    'version':      u'Version',
    'revision':     u'Revision',
    'status':       u'Status',
    'date':         u'Datum',
    'copyright':    u'Copyright',
    'dedication':   u'Dedikation',
    'abstract':     u'Sammanfattning',
    'attention':    u'Observera!',
    'caution':      u'Varning!',
    'danger':       u'FARA!',
    'error':        u'Fel',
    'hint':         u'V\u00e4gledning',
    'important':    u'Viktigt',
    'note':         u'Notera',
    'tip':          u'Tips',
    'warning':      u'Varning',
    'contents':     u'Inneh\u00e5ll' }
"""Mapping of node class name to label text."""

bibliographic_fields = {
    # 'Author' and 'Authors' identical in Swedish; assume the plural:
    u'f\u00f6rfattare': nodes.authors,
    u'organisation':    nodes.organization,
    u'adress':          nodes.address,
    u'kontakt':         nodes.contact,
    u'version':         nodes.version,
    u'revision':        nodes.revision,
    u'status':          nodes.status,
    u'datum':           nodes.date,
    u'copyright':       nodes.copyright,
    u'dedikation':      nodes.topic, 
    u'sammanfattning':  nodes.topic }
"""Field name (lowcased) to node class name mapping for bibliographic fields
(field_list)."""

author_separators = [';', ',']
"""List of separator strings for the 'Authors' bibliographic field. Tried in
order."""
