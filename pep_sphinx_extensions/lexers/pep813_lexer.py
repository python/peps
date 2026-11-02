# This file is placed in the public domain or under the
# CC0-1.0-Universal license, whichever is more permissive.

"""Custom lexer for PEP 813."""

# This lexer is most useful while PEP 813 is being discussed.
# If it breaks in the future, it can be safely replaced by plain
# Python or text lexers.

from pygments.lexer import DelegatingLexer, inherit
from pygments.lexers.python import (
    PythonLexer,
    PythonTracebackLexer,
    _PythonConsoleLexerBase,
)
from pygments.token import Other, String


class Py813Lexer(PythonLexer):
    name = "py813"

    tokens = {
        "expr-inside-fstring": [
            # The ``!p`` conversion, without a format specifier
            (r"(=\s*)?(\!p)\}", String.Interpol, "#pop"),
            # The ``!p`` conversion, with a format specifier
            (r"(=\s*)?(\!p):", String.Interpol, "#pop"),
            inherit,
        ],
    }


class Py813ConsoleLexer(DelegatingLexer):
    name = "py813-console"

    def __init__(self, **options):
        pylexer = Py813Lexer
        tblexer = PythonTracebackLexer

        class _ReplaceInnerCode(DelegatingLexer):
            def __init__(self, **options):
                super().__init__(
                    pylexer, _PythonConsoleLexerBase, Other.Code, **options
                )

        super().__init__(tblexer, _ReplaceInnerCode, Other.Traceback, **options)


def register():
    return [Py813Lexer, Py813ConsoleLexer]
