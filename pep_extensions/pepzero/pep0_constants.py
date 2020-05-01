from functools import partial

title_length = 55
author_length = 40
table_separator = "== ====  " + "="*title_length + " " + "="*author_length

# column format is called as a function with a mapping containing field values
column_format = partial(
    "{type}{status}{number: >5}  {title: <{title_length}} {authors}".format,
    title_length=title_length
)

header = """\
PEP: 0
Title: Index of Python Enhancement Proposals (PEPs)
Version: N/A
Last-Modified: {last_modified}
Author: python-dev <python-dev@python.org>
Status: Active
Type: Informational
Content-Type: text/x-rst
Created: 13-Jul-2000
"""

intro = """\
This PEP contains the index of all Python Enhancement Proposals,
known as PEPs.  PEP numbers are assigned by the PEP editors, and
once assigned are never changed [1_].  The version control history [2_] of
the PEP texts represent their historical record.
"""

references = """\
.. [1] PEP 1: PEP Purpose and Guidelines
.. [2] View PEP history online: https://github.com/python/peps
"""

footer = """\
..
   Local Variables:
   mode: indented-text
   indent-tabs-mode: nil
   sentence-end-double-space: t
   fill-column: 70
   coding: utf-8
   End:\
"""
