import pytest
from docutils import nodes
from docutils.core import publish_doctree
from docutils.parsers.rst import Parser

from pep_sphinx_extensions.pep_processor.transforms import pep_headers
from pep_sphinx_extensions.pep_zero_generator.constants import (
    STATUS_ACCEPTED,
    STATUS_ACTIVE,
    STATUS_DEFERRED,
    STATUS_DRAFT,
    STATUS_FINAL,
    STATUS_PROVISIONAL,
    STATUS_REJECTED,
    STATUS_SUPERSEDED,
    STATUS_WITHDRAWN,
    TYPE_INFO,
    TYPE_PROCESS,
    TYPE_STANDARDS,
)


def _render_pep_headers(post_history, *, discussions_to=""):
    document = publish_doctree(
        f"PEP: 9000\nTitle: Test PEP\n{discussions_to}Status: Draft\n{post_history}",
        source_path="pep-9000.rst",
        parser=Parser(rfc2822=True),
        settings_overrides={"docinfo_xform": False},
    )
    pep_headers.PEPHeaders(document).apply()
    return document


@pytest.mark.parametrize(
    ("last_url", "expected_url", "label"),
    [
        pytest.param(
            "https://discuss.python.org/t/current/200/3",
            "https://discuss.python.org/t/current/200",
            "Discourse thread",
            id="reply-url",
        ),
        pytest.param(
            "https://discuss.python.org/t/200/3/",
            "https://discuss.python.org/t/200",
            "Discourse thread",
            id="reply-url-without-a-topic-slug",
        ),
        pytest.param(
            "https://discuss.python.org/t/current/200/",
            "https://discuss.python.org/t/current/200/",
            "Discourse thread",
            id="topic-url",
        ),
        pytest.param(
            "https://example.com/thread/200/3",
            "https://example.com/thread/200/3",
            "https://example.com/thread/200/3",
            id="other-forum",
        ),
    ],
)
def test_discussions_to_uses_last_post_history_link(last_url, expected_url, label):
    first_url = "https://discuss.python.org/t/older/100"
    document = _render_pep_headers(
        f"Post-History: `01-Jan-2026 <{first_url}>`__, "
        f"`02-Jan-2026 <{last_url}>`__, 03-Jan-2026\n"
    )

    fields = {field[0].astext(): field[1] for field in document[0]}
    links = list(fields["Discussions-To"].findall(nodes.reference))
    assert [(link["refuri"], link.astext()) for link in links] == [
        (expected_url, label)
    ]
    assert list(fields).index("Discussions-To") < list(fields).index("Status")
    assert [
        link["refuri"] for link in fields["Post-History"].findall(nodes.reference)
    ] == [first_url, last_url]
    assert "Discussions-To" not in document["headers"]


@pytest.mark.parametrize(
    ("value", "label", "expected_urls"),
    [
        pytest.param(
            "https://discuss.python.org/t/explicit/300",
            "Discourse thread",
            ["https://discuss.python.org/t/explicit/300"],
            id="explicit-link",
        ),
        pytest.param("Pending", "Pending", [], id="explicit-pending"),
    ],
)
def test_explicit_discussions_to_takes_precedence(value, label, expected_urls):
    document = _render_pep_headers(
        "Post-History: `02-Jan-2026 <https://discuss.python.org/t/current/200/3>`__\n",
        discussions_to=f"Discussions-To: {value}\n",
    )

    fields = {field[0].astext(): field[1] for field in document[0]}
    body = fields["Discussions-To"]
    assert body.astext() == label
    assert [link["refuri"] for link in body.findall(nodes.reference)] == expected_urls
    assert document["headers"]["Discussions-To"] == value


@pytest.mark.parametrize(
    "post_history",
    [
        pytest.param("Post-History: 02-Jan-2026\n", id="date-without-a-link"),
        pytest.param("Post-History: Pending\n", id="pending-history"),
        pytest.param("", id="no-history"),
    ],
)
def test_no_discussions_to_without_post_history_links(post_history):
    document = _render_pep_headers(post_history)

    assert "Discussions-To" not in {field[0].astext() for field in document[0]}


@pytest.mark.parametrize(
    ("test_input", "expected"),
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
    ("test_input", "expected"),
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
    ("test_input", "expected"),
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
    ("test_input", "expected"),
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


@pytest.mark.parametrize(
    ("test_input", "expected"),
    [
        (STATUS_ACCEPTED, "Normative proposal accepted for implementation"),
        (STATUS_ACTIVE, "Currently valid informational guidance, or an in-use process"),
        (STATUS_DEFERRED, "Inactive draft that may be taken up again at a later time"),
        (STATUS_DRAFT, "Proposal under active discussion and revision"),
        (STATUS_FINAL, "Accepted and implementation complete, or no longer active"),
        (STATUS_REJECTED, "Formally declined and will not be accepted"),
        ("April Fool!", "Formally declined and will not be accepted"),
        (STATUS_SUPERSEDED, "Replaced by another succeeding PEP"),
        (STATUS_WITHDRAWN, "Removed from consideration by sponsor or authors"),
        (STATUS_PROVISIONAL, "Provisionally accepted but additional feedback needed"),
    ],
)
def test_abbreviate_status(test_input, expected):
    out = pep_headers._abbreviate_status(test_input)

    assert out == expected


def test_abbreviate_status_unknown():
    with pytest.raises(pep_headers.PEPParsingError):
        pep_headers._abbreviate_status("an unknown status")


@pytest.mark.parametrize(
    ("test_input", "expected"),
    [
        (
            TYPE_INFO,
            "Non-normative PEP containing background, guidelines or other information "
            "relevant to the Python ecosystem",
        ),
        (
            TYPE_PROCESS,
            "Normative PEP describing or proposing a change to a Python community "
            "process, workflow or governance",
        ),
        (
            TYPE_STANDARDS,
            "Normative PEP with a new feature for Python, implementation change for "
            "CPython or interoperability standard for the ecosystem",
        ),
    ],
)
def test_abbreviate_type(test_input, expected):
    out = pep_headers._abbreviate_type(test_input)

    assert out == expected


def test_abbreviate_type_unknown():
    with pytest.raises(pep_headers.PEPParsingError):
        pep_headers._abbreviate_type("an unknown type")
