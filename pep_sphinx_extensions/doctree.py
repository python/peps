# This file is placed in the public domain or under the
# CC0-1.0-Universal license, whichever is more permissive.

from __future__ import annotations

import pickle
from pathlib import Path

from docutils import nodes

document_cache: dict[Path, dict[str, str]] = {}


def pep_abstract(document: nodes.document) -> str:
    """Return the first paragraph of the PEP abstract.
    If not found, return the first paragraph of the introduction.
    """
    introduction = ""
    for node in document.findall(nodes.section):
        title_node = node.next_node(nodes.title)
        if title_node is None:
            continue

        if title_node.astext() == "Abstract":
            if (para_node := node.next_node(nodes.paragraph)) is not None:
                return para_node.astext().strip().replace("\n", " ")
            return ""
        if title_node.astext() == "Introduction":
            introduction = node.next_node(nodes.paragraph).astext().strip().replace("\n", " ")

    return introduction


def get_from_doctree(full_path: Path, text: str) -> str:
    """Retrieve a header value from a pickled doctree, with caching."""
    # Try and retrieve from cache
    if full_path in document_cache:
        return document_cache[full_path].get(text, "")

    # Else load doctree
    document = pickle.loads(full_path.read_bytes())
    # Store the headers (populated in the PEPHeaders transform)
    document_cache[full_path] = path_cache = document.get("headers", {})
    # Store the Abstract
    path_cache["Abstract"] = pep_abstract(document)
    # Return the requested key
    return path_cache.get(text, "")
