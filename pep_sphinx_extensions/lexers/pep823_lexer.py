# This file is placed in the public domain or under the
# CC0-1.0-Universal license, whichever is more permissive.

"""Custom lexer for PEP 823."""

from pygments.lexer import DelegatingLexer, inherit
from pygments.lexers.python import (
    PythonLexer,
    PythonTracebackLexer,
    _PythonConsoleLexerBase,
)
from pygments.token import Operator, Other


class Py823Lexer(PythonLexer):
    name = "py823"

    tokens = {
        "expr": [
            (r"maybe\b", Operator.Word),
            (r"\?", Operator),
            inherit,
        ],
    }


class Py823ConsoleLexer(DelegatingLexer):
    name = "py823-console"

    def __init__(self, **options):
        pylexer = Py823Lexer
        tblexer = PythonTracebackLexer

        class _ReplaceInnerCode(DelegatingLexer):
            def __init__(self, **options):
                super().__init__(
                    pylexer, _PythonConsoleLexerBase, Other.Code, **options
                )

        super().__init__(tblexer, _ReplaceInnerCode, Other.Traceback, **options)


def register():
    return [Py823Lexer, Py823ConsoleLexer]
