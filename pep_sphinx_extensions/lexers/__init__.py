# This file is placed in the public domain or under the
# CC0-1.0-Universal license, whichever is more permissive.

from __future__ import annotations

from typing import TYPE_CHECKING

from .pep823_lexer import Py823ConsoleLexer, Py823Lexer
from .pep824_lexer import Py824Lexer

if TYPE_CHECKING:
    from pygments.lexer import Lexer


pep_lexers: list[type[Lexer]] = [
    Py823ConsoleLexer,
    Py823Lexer,
    Py824Lexer,
]
