from __future__ import annotations

import re
from typing import TYPE_CHECKING

from sphinx import jinja2glue

from pep_sphinx_extensions.config import pep_stem

if TYPE_CHECKING:
    from sphinx.builders import Builder
    from sphinx.theming import Theme

pep_title_pat = re.compile(r"(PEP \d+).*")


def _pep_id(pep_full_title: str) -> str:
    matches = pep_title_pat.match(pep_full_title.strip().upper())
    if not matches:
        return ""
    pep_num = matches.group(1).strip().removeprefix("PEP ")
    return pep_stem.format(pep_num).replace("-", " ").upper()


class PEPTemplateLoader(jinja2glue.BuiltinTemplateLoader):
    def init(self, builder: Builder, theme: Theme = None, dirs: list[str] = None):
        super().init(builder, theme, dirs)
        self.environment.filters["pep_id"] = _pep_id
