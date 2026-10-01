# This file is placed in the public domain or under the
# CC0-1.0-Universal license, whichever is more permissive.

from __future__ import annotations

import importlib
import pkgutil
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pygments.lexer import Lexer


def get_custom_lexers() -> list[type[Lexer]]:
    lexers: list[type[Lexer]] = []
    for module_info in pkgutil.walk_packages(__path__, prefix=f"{__name__}."):
        module = importlib.import_module(module_info.name)
        if (register_func := getattr(module, "register", None)) is None:
            continue
        lexers.extend(register_func())
    return lexers
