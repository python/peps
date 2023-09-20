from pep_sphinx_extensions.pep_zero_generator import parser, pep_index_generator

from ..conftest import PEP_ROOT


def test_create_pep_json():
    peps = [parser.PEP(PEP_ROOT / "pep-0008.rst")]

    out = pep_index_generator.create_pep_json(peps)

    assert '"url": "https://peps.python.org/pep-0008/"' in out
