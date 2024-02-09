import datetime as dt

from pep_sphinx_extensions.pep_processor.transforms import pep_footer

from ...conftest import PEP_ROOT


def test_add_source_link():
    out = pep_footer._add_source_link(PEP_ROOT / "pep-0008.rst")

    assert "https://github.com/python/peps/blob/main/peps/pep-0008.rst" in str(out)


def test_add_commit_history_info():
    out = pep_footer._add_commit_history_info(PEP_ROOT / "pep-0008.rst")

    assert str(out).startswith(
        "<paragraph>Last modified: "
        '<reference refuri="https://github.com/python/peps/commits/main/peps/pep-0008.rst">'
    )
    # A variable timestamp comes next, don't test that
    assert str(out).endswith("</reference></paragraph>")


def test_add_commit_history_info_invalid():
    out = pep_footer._add_commit_history_info(PEP_ROOT / "pep-not-found.rst")

    assert str(out) == "<paragraph/>"


def test_get_last_modified_timestamps():
    out = pep_footer._get_last_modified_timestamps()

    assert len(out) >= 585
    # Should be a Unix timestamp and at least this
    assert dt.datetime.fromisoformat(out["pep-0008"]).timestamp() >= 1643124055
