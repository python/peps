from __future__ import annotations

from typing import TYPE_CHECKING

from docutils import nodes
from pygments.lexers.python import PythonLexer
from pygments.token import Keyword, Name
from sphinx import addnodes

if TYPE_CHECKING:
    from collections.abc import Iterator

    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment

_LANG_PREFIX = "python+soft-keywords:"


def _keywords_from_language(language: str) -> tuple[str, ...] | None:
    if not language.startswith(_LANG_PREFIX):
        return None
    keywords = tuple(w for w in language[len(_LANG_PREFIX) :].split(",") if w)
    return keywords or None


def _soft_keyword_lexer(keywords: tuple[str, ...]) -> type[PythonLexer]:
    words = frozenset(keywords)

    class SoftKeywordPythonLexer(PythonLexer):
        name = f"Python (+ {', '.join(keywords)})"
        aliases: list[str] = []
        filenames: list[str] = []  # don't shadow the real Python lexer
        mimetypes: list[str] = []
        url = ""

        def get_tokens_unprocessed(
            self, text: str, stack: tuple[str, ...] = ("root",)
        ) -> Iterator[tuple[int, object, str]]:
            for index, token, value in super().get_tokens_unprocessed(text, stack):
                if value in words and token in Name:
                    yield index, Keyword, value
                else:
                    yield index, token, value

    return SoftKeywordPythonLexer


def _init_env(app: Sphinx, env: BuildEnvironment, docnames: list[str]) -> None:
    if not hasattr(env, "pep_soft_keywords"):
        env.pep_soft_keywords = {}


def _collect_languages(app: Sphinx, doctree: nodes.document) -> None:
    found = set()
    for node in doctree.findall(nodes.literal_block):
        if keywords := _keywords_from_language(node.get("language", "")):
            found.add(keywords)
    for node in doctree.findall(addnodes.highlightlang):
        if keywords := _keywords_from_language(node.get("lang", "")):
            found.add(keywords)

    if found:
        app.env.pep_soft_keywords[app.env.docname] = found
    else:
        app.env.pep_soft_keywords.pop(app.env.docname, None)


def _merge_info(
    app: Sphinx,
    env: BuildEnvironment,
    docnames: list[str],
    other: BuildEnvironment,
) -> None:
    env.pep_soft_keywords.update(getattr(other, "pep_soft_keywords", {}))


def _register_lexers(app: Sphinx, env: BuildEnvironment) -> None:
    for keyword_sets in env.pep_soft_keywords.values():
        for keywords in keyword_sets:
            app.add_lexer(_LANG_PREFIX + ",".join(keywords), _soft_keyword_lexer(keywords))


def setup(app: Sphinx) -> dict[str, bool]:
    app.connect("env-before-read-docs", _init_env)
    app.connect("doctree-read", _collect_languages)
    app.connect("env-merge-info", _merge_info)
    app.connect("env-updated", _register_lexers)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
