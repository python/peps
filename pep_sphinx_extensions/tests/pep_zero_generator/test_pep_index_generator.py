from pathlib import Path

from pep_sphinx_extensions.pep_zero_generator import parser, pep_index_generator


def test_create_pep_json():
    peps = [parser.PEP(Path("pep-0008.txt"))]

    out = pep_index_generator.create_pep_json(peps)

    assert '"url": "https://peps.python.org/pep-0008/"' in out
