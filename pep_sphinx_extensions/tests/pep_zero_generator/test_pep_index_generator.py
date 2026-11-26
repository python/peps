import json

import pytest

from pep_sphinx_extensions.pep_zero_generator import parser, pep_index_generator

from ..conftest import PEP_ROOT


def test_create_pep_json():
    peps = [parser.PEP(PEP_ROOT / "pep-0008.rst")]

    out = pep_index_generator.create_pep_json(peps)

    assert '"url": "https://peps.python.org/pep-0008/"' in out


@pytest.mark.parametrize(
    ("headers", "expected"),
    [
        pytest.param(
            "Post-History: `01-Jan-2026 <https://discuss.python.org/t/older/100>`__,\n"
            "              `02-Jan-2026 <https://discuss.python.org/t/current/200/3>`__,\n"
            "              03-Jan-2026\n",
            "https://discuss.python.org/t/current/200",
            id="last-linked-entry-is-a-reply",
        ),
        pytest.param(
            "Post-History: `02-Jan-2026 <https://example.com/thread/200/3>`__\n",
            "https://example.com/thread/200/3",
            id="other-forum",
        ),
        pytest.param(
            "Discussions-To: https://discuss.python.org/t/explicit/300\n"
            "Post-History: `02-Jan-2026 <https://discuss.python.org/t/current/200>`__\n",
            "https://discuss.python.org/t/explicit/300",
            id="explicit-link-takes-precedence",
        ),
        pytest.param(
            "Discussions-To: Pending\n"
            "Post-History: `02-Jan-2026 <https://discuss.python.org/t/current/200>`__\n",
            "Pending",
            id="explicit-pending-takes-precedence",
        ),
        pytest.param("Post-History: 02-Jan-2026\n", None, id="date-without-a-link"),
        pytest.param("", None, id="no-history"),
    ],
)
def test_create_pep_json_discussions_to(tmp_path, headers, expected):
    path = tmp_path / "pep-9000.rst"
    path.write_text(
        "PEP: 9000\nTitle: Test PEP\nAuthor: Example Author\n"
        f"Status: Draft\nType: Process\nCreated: 01-Jan-2026\n{headers}",
        encoding="utf-8",
    )

    metadata = json.loads(pep_index_generator.create_pep_json([parser.PEP(path)]))

    assert metadata["9000"]["discussions_to"] == expected


def test_build_release_peps_links_individual_versions_from_joint_release_pep():
    peps = [
        parser.PEP(PEP_ROOT / "pep-0361.rst"),  # "2.6, 3.0" joint release PEP
    ]

    release_peps = pep_index_generator.build_release_peps(peps)

    assert release_peps == {"2.6": 361, "3.0": 361}
