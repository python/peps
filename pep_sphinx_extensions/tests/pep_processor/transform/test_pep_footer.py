from pathlib import Path

from pep_sphinx_extensions.pep_processor.transforms import pep_footer


def test_add_source_link():
    out = pep_footer._add_source_link(Path("pep-0008.txt"))

    assert "https://github.com/python/peps/blob/main/pep-0008.txt" in str(out)


def test_add_commit_history_info():
    out = pep_footer._add_commit_history_info(Path("pep-0008.txt"))

    assert str(out).startswith(
        "<paragraph>Last modified: "
        '<reference refuri="https://github.com/python/peps/commits/main/pep-0008.txt">'
    )
    # A variable timestamp comes next, don't test that
    assert str(out).endswith("</reference></paragraph>")


def test_add_commit_history_info_invalid():
    out = pep_footer._add_commit_history_info(Path("pep-not-found.txt"))

    assert str(out) == "<paragraph/>"


def test_get_last_modified_timestamps():
    out = pep_footer._get_last_modified_timestamps()

    assert len(out) >= 585
    # Should be a Unix timestamp and at least this
    assert out["pep-0008.txt"] >= 1643124055
