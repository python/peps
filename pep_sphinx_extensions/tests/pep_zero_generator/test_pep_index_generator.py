from pep_sphinx_extensions.pep_zero_generator import parser, pep_index_generator

from ..conftest import PEP_ROOT


def test_create_pep_json():
    peps = [parser.PEP(PEP_ROOT / "pep-0008.rst")]

    out = pep_index_generator.create_pep_json(peps)

    assert '"url": "https://peps.python.org/pep-0008/"' in out


def test_build_release_peps_links_individual_versions_from_joint_release_pep():
    peps = [
        parser.PEP(PEP_ROOT / "pep-0361.rst"),  # "2.6, 3.0" joint release PEP
    ]

    release_peps = pep_index_generator.build_release_peps(peps)

    assert release_peps == {"2.6": 361, "3.0": 361}
