"""Misc. config variables for the PEP extensions module."""
import re

__version__ = '1.0.0'
pep_stem = "pep-{:0>4}"
pep_url = f"{pep_stem}.html"
pep_vcs_url = f"https://github.com/python/peps/blob/master/{pep_stem}.txt"
rcs_keyword_substitutions = [(re.compile(r"\$[a-zA-Z]+: (.+) \$$"), r"\1")]