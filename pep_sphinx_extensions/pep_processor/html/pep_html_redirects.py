from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

    from sphinx.application import Sphinx


def prepare_redirect_pages(app: Sphinx) -> Iterator[tuple[str, dict, str]]:
    for path in Path(app.srcdir).glob("pep-????.???"):
        if path.suffix not in {".txt", ".rst"}:
            continue

        pep_num = int(path.stem[4:])
        yield str(pep_num), {"pep_file": path.stem, "pep_num": pep_num}, "redirect.html"
