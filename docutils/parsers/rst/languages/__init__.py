# Author: David Goodger
# Contact: goodger@users.sourceforge.net
# Revision: $Revision$
# Date: $Date$
# Copyright: This module has been placed in the public domain.

"""
This package contains modules for language-dependent features of
reStructuredText.
"""

__docformat__ = 'reStructuredText'

_languages = {}

def get_language(language_code):
    if _languages.has_key(language_code):
        return _languages[language_code]
    try:
        module = __import__(language_code, globals(), locals())
    except ImportError:
        return None
    _languages[language_code] = module
    return module
