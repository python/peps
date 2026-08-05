from __future__ import annotations

from collections.abc import Iterable
import sys
from typing import TYPE_CHECKING, Any

from pygments.lexers.python import PythonLexer
from pygments.token import Keyword, Name
from sphinx import addnodes
from sphinx.util.docutils import SphinxDirective

if TYPE_CHECKING:
    from collections.abc import Iterator

    from docutils.nodes import Node
    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment

_LANG_PREFIX = "python+soft-keywords:"


def _language_name(keywords: tuple[str, ...]) -> str:
    return _LANG_PREFIX + ",".join(keywords)


def _soft_keyword_lexer(keywords: tuple[str, ...]) -> type[PythonLexer]:
    words = frozenset(keywords)

    class SoftKeywordPythonLexer(PythonLexer):
        name = f"Python (+ {', '.join(keywords)})"
        aliases: list[str] = []
        filenames: list[str] = []  # don't shadow the real Python lexer
        mimetypes: list[str] = []
        url = ""

        def get_tokens_unprocessed(
            self, text: str, stack: Iterable[str] = ("root",)
        ) -> Iterator[tuple[int, Any, str]]:
            for index, token, value in super().get_tokens_unprocessed(text, stack):
                if value in words and token in Name:
                    yield index, Keyword, value
                else:
                    yield index, token, value

    return SoftKeywordPythonLexer


class AddSoftKeyword(SphinxDirective):
    required_arguments = 1
    final_argument_whitespace = True  # several keywords in one directive

    def run(self) -> list[Node]:
        keywords = tuple(sorted(self.arguments[0].split()))
        self.env.pep_soft_keywords[self.env.docname] = keywords

        language = _language_name(keywords)
        self.env.temp_data["highlight_language"] = language
        return [
            addnodes.highlightlang(
                lang=language, force=False, linenothreshold=sys.maxsize
            )
        ]


def _init_env(app: Sphinx, env: BuildEnvironment, docnames: list[str]) -> None:
    if not hasattr(env, "pep_soft_keywords"):
        env.pep_soft_keywords = {}


def _merge_info(
    app: Sphinx,
    env: BuildEnvironment,
    docnames: list[str],
    other: BuildEnvironment,
) -> None:
    env.pep_soft_keywords.update(getattr(other, "pep_soft_keywords", {}))


def _register_lexers(app: Sphinx, env: BuildEnvironment) -> None:
    for keywords in set(env.pep_soft_keywords.values()):
        app.add_lexer(_language_name(keywords), _soft_keyword_lexer(keywords))


def setup(app: Sphinx) -> dict[str, bool]:
    app.add_directive("add-soft-keyword", AddSoftKeyword)
    app.connect("env-before-read-docs", _init_env)
    app.connect("env-merge-info", _merge_info)
    app.connect("env-updated", _register_lexers)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
