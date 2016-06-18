# -*- coding: utf-8 -*-
import sys

if sys.version_info[0] > 2:
	text_type = str
else:
	text_type = unicode

title_length = 55
column_format = (u' %(type)1s%(status)1s %(number)4s  %(title)-' +
                    text_type(title_length) + u's %(authors)-s')

header = u"""PEP: 0
Title: Index of Python Enhancement Proposals (PEPs)
Version: N/A
Last-Modified: %s
Author: David Goodger <goodger@python.org>,
        Barry Warsaw <barry@python.org>
Status: Active
Type: Informational
Created: 13-Jul-2000
"""

intro = u"""
    This PEP contains the index of all Python Enhancement Proposals,
    known as PEPs.  PEP numbers are assigned by the PEP editors, and
    once assigned are never changed[1].  The Mercurial history[2] of
    the PEP texts represent their historical record.
"""

references = u"""
    [1] PEP 1: PEP Purpose and Guidelines
    [2] View PEP history online
        https://hg.python.org/peps/
"""

footer = u"""
Local Variables:
mode: indented-text
indent-tabs-mode: nil
sentence-end-double-space: t
fill-column: 70
coding: utf-8
End:"""
