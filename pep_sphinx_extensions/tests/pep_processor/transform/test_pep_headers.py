import pytest

from pep_sphinx_extensions.pep_processor.transforms import pep_headers


@pytest.mark.parametrize(
    "test_input, expected",
    [
        ("my-mailing-list@example.com", "my-mailing-list@example.com"),
        ("python-tulip@googlegroups.com", "https://groups.google.com/g/python-tulip"),
        ("db-sig@python.org", "https://mail.python.org/mailman/listinfo/db-sig"),
        ("import-sig@python.org", "https://mail.python.org/pipermail/import-sig/"),
        (
            "python-announce@python.org",
            "https://mail.python.org/archives/list/python-announce@python.org/",
        ),
    ],
)
def test_generate_list_url(test_input, expected):
    out = pep_headers._generate_list_url(test_input)

    assert out == expected


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (
            "https://mail.python.org/pipermail/python-3000/2006-November/004190.html",
            ("Python-3000", "message"),
        ),
        (
            "https://mail.python.org/archives/list/python-dev@python.org/thread/HW2NFOEMCVCTAFLBLC3V7MLM6ZNMKP42/",
            ("Python-Dev", "thread"),
        ),
        (
            "https://mail.python.org/mailman3/lists/capi-sig.python.org/",
            ("Capi-SIG", "list"),
        ),
        (
            "https://mail.python.org/mailman/listinfo/web-sig",
            ("Web-SIG", "list"),
        ),
        (
            "https://discuss.python.org/t/pep-643-metadata-for-package-source-distributions/5577",
            ("Discourse", "thread"),
        ),
        (
            "https://discuss.python.org/c/peps/",
            ("PEPs Discourse", "category"),
        ),
    ],
)
def test_process_pretty_url(test_input, expected):
    out = pep_headers._process_pretty_url(test_input)

    assert out == expected


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (
            "https://example.com/",
            "https://example.com/ not a link to a recognized domain to prettify",
        ),
        (
            "https://mail.python.org",
            "https://mail.python.org not a link to a list, message or thread",
        ),
        (
            "https://discuss.python.org/",
            "https://discuss.python.org not a link to a Discourse thread or category",
        ),
    ],
)
def test_process_pretty_url_invalid(test_input, expected):
    with pytest.raises(ValueError, match=expected):
        pep_headers._process_pretty_url(test_input)


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (
            "https://mail.python.org/pipermail/python-3000/2006-November/004190.html",
            "Python-3000 message",
        ),
        (
            "https://mail.python.org/archives/list/python-dev@python.org/thread/HW2NFOEMCVCTAFLBLC3V7MLM6ZNMKP42/",
            "Python-Dev thread",
        ),
        (
            "https://mail.python.org/mailman3/lists/capi-sig.python.org/",
            "Capi-SIG list",
        ),
        (
            "https://mail.python.org/mailman/listinfo/web-sig",
            "Web-SIG list",
        ),
        (
            "https://discuss.python.org/t/pep-643-metadata-for-package-source-distributions/5577",
            "Discourse thread",
        ),
        (
            "https://discuss.python.org/c/peps/",
            "PEPs Discourse category",
        ),
    ],
)
def test_make_link_pretty(test_input, expected):
    out = pep_headers._make_link_pretty(test_input)

    assert out == expected
