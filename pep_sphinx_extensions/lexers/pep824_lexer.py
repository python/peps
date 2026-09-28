# This file is placed in the public domain or under the
# CC0-1.0-Universal license, whichever is more permissive.

"""Custom lexer for PEP 824."""

# This lexer is most useful while PEP 824 is being discussed.
# If it breaks in the future, it can be safely replaced by plain
# Python or text lexers.

from pygments.lexer import inherit
from pygments.lexers.python import PythonLexer
from pygments.token import Operator


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


def register():
    return [Py824Lexer]
