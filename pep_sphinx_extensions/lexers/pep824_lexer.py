# This file is placed in the public domain or under the
# CC0-1.0-Universal license, whichever is more permissive.

"""Custom lexer for PEP 824."""

# This lexer is most useful while PEP 824 is being discussed.
# If it breaks in the future, it can be safely replaced by plain
# Python or text lexers.

from pygments.lexer import DelegatingLexer, inherit
from pygments.lexers.python import (
    PythonLexer,
    PythonTracebackLexer,
    _PythonConsoleLexerBase,
)
from pygments.token import Operator, Other


class Py824Lexer(PythonLexer):
    name = "py824"

    tokens = {
        "expr": [
            (r"\?\?(?=\s)", Operator.Word),
            (r"otherwise\b", Operator.Word),
            (r"\?", Operator),
            inherit,
        ],
    }


class Py824ConsoleLexer(DelegatingLexer):
    name = "py824-console"

    def __init__(self, **options):
        pylexer = Py824Lexer
        tblexer = PythonTracebackLexer

        class _ReplaceInnerCode(DelegatingLexer):
            def __init__(self, **options):
                super().__init__(
                    pylexer, _PythonConsoleLexerBase, Other.Code, **options
                )

        super().__init__(tblexer, _ReplaceInnerCode, Other.Traceback, **options)


def register():
    return [Py824Lexer, Py824ConsoleLexer]
