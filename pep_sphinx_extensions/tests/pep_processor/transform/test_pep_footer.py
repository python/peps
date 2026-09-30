import datetime as dt

from pep_sphinx_extensions.pep_processor.transforms import pep_footer


def test_get_page_footer_context():
    out = pep_footer.get_page_footer_context("pep-0008")

    assert out["source_link"] == (
        "https://github.com/python/peps/blob/main/peps/pep-0008.rst"
    )
    assert out["commit_link"] == (
        "https://github.com/python/peps/commits/main/peps/pep-0008.rst"
    )
    # A variable timestamp, don't test the exact value
    assert out["last_modified"]


def test_get_page_footer_context_no_history():
    out = pep_footer.get_page_footer_context("pep-not-found")

    # No git history -> only the static source link
    assert out == {
        "source_link": "https://github.com/python/peps/blob/main/peps/pep-not-found.rst",
    }


def test_get_last_modified_timestamps():
    out = pep_footer._get_last_modified_timestamps()

    assert len(out) >= 585
    # Should be a Unix timestamp and at least this
    assert dt.datetime.fromisoformat(out["pep-0008"]).timestamp() >= 1643124055
