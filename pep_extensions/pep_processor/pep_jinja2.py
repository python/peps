from __future__ import annotations

import re
from sphinx import jinja2glue
from typing import TYPE_CHECKING, List

import pep_extensions.config as pep_config

if TYPE_CHECKING:
    # For type annotation
    from sphinx.builders import Builder
    from sphinx.theming import Theme

pep_title_pat = re.compile(r"(PEP \d+).*", flags=re.IGNORECASE)


def _pep_id(pep_full_title: str) -> str:
    matches = pep_title_pat.match(pep_full_title.strip())
    if not matches:
        return ""
    pep_short_title = matches.group(1).strip()
    pep_num = pep_short_title[4:]
    pep_id = pep_config.pep_stem.format(pep_num).replace("-", " ").upper()
    return pep_id


class PEPTemplateLoader(jinja2glue.BuiltinTemplateLoader):
    def init(self, builder: Builder, theme: Theme = None, dirs: List[str] = None) -> None:
        super(PEPTemplateLoader, self).init(builder, theme, dirs)
        self.environment.filters['pep_id'] = _pep_id