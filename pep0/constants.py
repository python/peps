# -*- coding: utf-8 -*-
text_type = str
title_length = 55
author_length = 40
table_separator = "== ====  " + "="*title_length + " " + "="*author_length
column_format = (
    '%(type)1s%(status)1s %(number)4s  %(title)-{title_length}s %(authors)-s'
).format(title_length=title_length)

header = """\
PEP: 0
Title: Index of Python Enhancement Proposals (PEPs)
Version: N/A
Last-Modified: %s
Author: python-dev <python-dev@python.org>
Status: Active
Type: Informational
Content-Type: text/x-rst
Created: 13-Jul-2000
"""

intro = """\
This PEP contains the index of all Python Enhancement Proposals,
known as PEPs.  PEP numbers are assigned by the PEP editors[1_], and
once assigned are never changed.  The version control history [2_] of
the PEP texts represent their historical record.
"""

references = """\
.. [1] PEP 1: PEP Purpose and Guidelines
.. [2] View PEP history online: https://github.com/python/peps
"""

footer = """\
..
   Local Variables:
   mode: indented-text
   indent-tabs-mode: nil
   sentence-end-double-space: t
   fill-column: 70
   coding: utf-8
   End:\
"""
