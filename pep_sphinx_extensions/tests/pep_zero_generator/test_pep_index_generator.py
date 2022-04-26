from pathlib import Path

from pep_sphinx_extensions.pep_zero_generator import parser, pep_index_generator
from pep_sphinx_extensions.tests.utils import AUTHORS_OVERRIDES


def test_create_pep_json():
    peps = [parser.PEP(Path("pep-0008.txt"), AUTHORS_OVERRIDES)]

    out = pep_index_generator.create_pep_json(peps)

    assert '"url": "https://peps.python.org/pep-0008/"' in out
