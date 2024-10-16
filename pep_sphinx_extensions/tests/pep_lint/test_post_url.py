import check_peps  # NoQA: inserted into sys.modules in conftest.py
import pytest


@pytest.mark.parametrize(
    "line",
    [
        "list-name@python.org",
        "distutils-sig@python.org",
        "csv@python.org",
        "python-3000@python.org",
        "ipaddr-py-dev@googlegroups.com",
        "python-tulip@googlegroups.com",
        "https://discuss.python.org/t/thread-name/123456",
        "https://discuss.python.org/t/thread-name/123456/",
        "https://discuss.python.org/t/thread_name/123456",
        "https://discuss.python.org/t/thread_name/123456/",
        "https://discuss.python.org/t/123456/",
        "https://discuss.python.org/t/123456",
    ],
)
def test_validate_discussions_to_valid(line: str):
    warnings = [
        warning for (_, warning) in check_peps._validate_discussions_to(1, line)
    ]
    assert warnings == [], warnings


@pytest.mark.parametrize(
    "line",
    [
        "$pecial+chars@python.org",
        "a-discussions-to-list!@googlegroups.com",
    ],
)
def test_validate_discussions_to_list_name(line: str):
    warnings = [
        warning for (_, warning) in check_peps._validate_discussions_to(1, line)
    ]
    assert warnings == ["Discussions-To must be a valid mailing list"], warnings


@pytest.mark.parametrize(
    "line",
    [
        "list-name@python.org.uk",
        "distutils-sig@mail-server.example",
    ],
)
def test_validate_discussions_to_invalid_list_domain(line: str):
    warnings = [
        warning for (_, warning) in check_peps._validate_discussions_to(1, line)
    ]
    assert warnings == [
        "Discussions-To must be a valid thread URL or mailing list"
    ], warnings


@pytest.mark.parametrize(
    "body",
    [
        "",
        (
            "01-Jan-2001, 02-Feb-2002,\n              "
            "03-Mar-2003, 04-Apr-2004,\n              "
            "05-May-2005,"
        ),
        (
            "`01-Jan-2000 <https://mail.python.org/pipermail/list-name/0000-Month/0123456.html>`__,\n              "
            "`11-Mar-2005 <https://mail.python.org/archives/list/list-name@python.org/thread/abcdef0123456789/>`__,\n              "
            "`21-May-2010 <https://discuss.python.org/t/thread-name/123456/654321>`__,\n              "
            "`31-Jul-2015 <https://discuss.python.org/t/123456>`__,"
        ),
        "01-Jan-2001, `02-Feb-2002 <https://discuss.python.org/t/123456>`__,\n03-Mar-2003",
    ],
)
def test_validate_post_history_valid(body: str):
    warnings = [warning for (_, warning) in check_peps._validate_post_history(1, body)]
    assert warnings == [], warnings


@pytest.mark.parametrize(
    "body",
    [
        "31-Jul-2015 <https://discuss.python.org/t/123456>`__,",
        "`31-Jul-2015 <https://discuss.python.org/t/123456>",
    ],
)
def test_validate_post_history_unbalanced_link(body: str):
    warnings = [warning for (_, warning) in check_peps._validate_post_history(1, body)]
    assert warnings == [
        "post line must be a date or both start with “`” and end with “>`__”"
    ], warnings


@pytest.mark.parametrize(
    "line",
    [
        "https://mail.python.org/archives/list/list-name@python.org/thread/abcXYZ123",
        "https://mail.python.org/archives/list/list-name@python.org/thread/abcXYZ123/",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123/",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123#Anchor",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123/#Anchor",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123#Anchor123",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123/#Anchor123",
        "`16-Oct-2024 <https://mail.python.org/archives/list/list-name@python.org/thread/abcXYZ123>`__",
    ],
)
def test_validate_resolution_valid(line: str):
    warnings = [warning for (_, warning) in check_peps._validate_resolution(1, line)]
    assert warnings == [], warnings


@pytest.mark.parametrize(
    "line",
    [
        "https://mail.python.org/archives/list/list-name@python.org/thread",
        "https://mail.python.org/archives/list/list-name@python.org/message",
        "https://mail.python.org/archives/list/list-name@python.org/thread/",
        "https://mail.python.org/archives/list/list-name@python.org/message/",
        "https://mail.python.org/archives/list/list-name@python.org/thread/abcXYZ123#anchor",
        "https://mail.python.org/archives/list/list-name@python.org/thread/abcXYZ123/#anchor",
        "https://mail.python.org/archives/list/list-name@python.org/message/#abcXYZ123",
        "https://mail.python.org/archives/list/list-name@python.org/message/#abcXYZ123/",
        "https://mail.python.org/archives/list/list-name@python.org/spam/abcXYZ123",
        "https://mail.python.org/archives/list/list-name@python.org/spam/abcXYZ123/",
    ],
)
def test_validate_resolution_invalid(line: str):
    warnings = [warning for (_, warning) in check_peps._validate_resolution(1, line)]
    assert warnings == ["Resolution must be a valid thread URL"], warnings


@pytest.mark.parametrize(
    "line",
    [
        "01-Jan-2000 <https://mail.python.org/pipermail/list-name/0000-Month/0123456.html>`__",
        "`01-Jan-2000 <https://mail.python.org/pipermail/list-name/0000-Month/0123456.html>",
    ],
)
def test_validate_resolution_unbalanced_link(line: str):
    warnings = [warning for (_, warning) in check_peps._validate_resolution(1, line)]
    assert warnings == [
        "Resolution line must be a link or both start with “`” and end with “>`__”"
    ], warnings


@pytest.mark.parametrize(
    "thread_url",
    [
        "https://discuss.python.org/t/thread-name/123456",
        "https://discuss.python.org/t/thread-name/123456/",
        "https://discuss.python.org/t/thread_name/123456",
        "https://discuss.python.org/t/thread_name/123456/",
        "https://discuss.python.org/t/thread-name/123456/654321/",
        "https://discuss.python.org/t/thread-name/123456/654321",
        "https://discuss.python.org/t/123456",
        "https://discuss.python.org/t/123456/",
        "https://discuss.python.org/t/123456/654321/",
        "https://discuss.python.org/t/123456/654321",
        "https://discuss.python.org/t/1",
        "https://discuss.python.org/t/1/",
        "https://mail.python.org/pipermail/list-name/0000-Month/0123456.html",
        "https://mail.python.org/archives/list/list-name@python.org/thread/abcXYZ123",
        "https://mail.python.org/archives/list/list-name@python.org/thread/abcXYZ123/",
    ],
)
def test_thread_checker_valid(thread_url: str):
    warnings = [
        warning for (_, warning) in check_peps._thread(1, thread_url, "<Prefix>")
    ]
    assert warnings == [], warnings


@pytest.mark.parametrize(
    "thread_url",
    [
        "http://link.example",
        "list-name@python.org",
        "distutils-sig@python.org",
        "csv@python.org",
        "python-3000@python.org",
        "ipaddr-py-dev@googlegroups.com",
        "python-tulip@googlegroups.com",
        "https://link.example",
        "https://discuss.python.org",
        "https://discuss.python.org/",
        "https://discuss.python.org/c/category",
        "https://discuss.python.org/t/thread_name/123456//",
        "https://discuss.python.org/t/thread+name/123456",
        "https://discuss.python.org/t/thread+name/123456#",
        "https://discuss.python.org/t/thread+name/123456/#",
        "https://discuss.python.org/t/thread+name/123456/#anchor",
        "https://discuss.python.org/t/thread+name/",
        "https://discuss.python.org/t/thread+name",
        "https://discuss.python.org/t/thread-name/123abc",
        "https://discuss.python.org/t/thread-name/123abc/",
        "https://discuss.python.org/t/thread-name/123456/123abc",
        "https://discuss.python.org/t/thread-name/123456/123abc/",
        "https://discuss.python.org/t/123/456/789",
        "https://discuss.python.org/t/123/456/789/",
        "https://discuss.python.org/t/#/",
        "https://discuss.python.org/t/#",
        "https://mail.python.org/pipermail/list+name/0000-Month/0123456.html",
        "https://mail.python.org/pipermail/list-name/YYYY-Month/0123456.html",
        "https://mail.python.org/pipermail/list-name/0123456/0123456.html",
        "https://mail.python.org/pipermail/list-name/0000-Month/0123456",
        "https://mail.python.org/pipermail/list-name/0000-Month/0123456/",
        "https://mail.python.org/pipermail/list-name/0000-Month/",
        "https://mail.python.org/pipermail/list-name/0000-Month",
        "https://mail.python.org/archives/list/list-name@python.org/thread/abcXYZ123#anchor",
        "https://mail.python.org/archives/list/list-name@python.org/thread/abcXYZ123/#anchor",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123/",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123#anchor",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123/#anchor",
        "https://mail.python.org/archives/list/list-name@python.org/spam/abcXYZ123",
        "https://mail.python.org/archives/list/list-name@python.org/spam/abcXYZ123/",
    ],
)
def test_thread_checker_invalid(thread_url: str):
    warnings = [
        warning for (_, warning) in check_peps._thread(1, thread_url, "<Prefix>")
    ]
    assert warnings == ["<Prefix> must be a valid thread URL"], warnings


@pytest.mark.parametrize(
    "thread_url",
    [
        "https://mail.python.org/archives/list/list-name@python.org/thread/abcXYZ123",
        "https://mail.python.org/archives/list/list-name@python.org/thread/abcXYZ123/",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123/",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123#Anchor",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123/#Anchor",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123#Anchor123",
        "https://mail.python.org/archives/list/list-name@python.org/message/abcXYZ123/#Anchor123",
    ],
)
def test_thread_checker_valid_allow_message(thread_url: str):
    warnings = [
        warning
        for (_, warning) in check_peps._thread(
            1, thread_url, "<Prefix>", allow_message=True
        )
    ]
    assert warnings == [], warnings


@pytest.mark.parametrize(
    "thread_url",
    [
        "https://mail.python.org/archives/list/list-name@python.org/thread",
        "https://mail.python.org/archives/list/list-name@python.org/message",
        "https://mail.python.org/archives/list/list-name@python.org/thread/",
        "https://mail.python.org/archives/list/list-name@python.org/message/",
        "https://mail.python.org/archives/list/list-name@python.org/thread/abcXYZ123#anchor",
        "https://mail.python.org/archives/list/list-name@python.org/thread/abcXYZ123/#anchor",
        "https://mail.python.org/archives/list/list-name@python.org/message/#abcXYZ123",
        "https://mail.python.org/archives/list/list-name@python.org/message/#abcXYZ123/",
        "https://mail.python.org/archives/list/list-name@python.org/spam/abcXYZ123",
        "https://mail.python.org/archives/list/list-name@python.org/spam/abcXYZ123/",
    ],
)
def test_thread_checker_invalid_allow_message(thread_url: str):
    warnings = [
        warning
        for (_, warning) in check_peps._thread(
            1, thread_url, "<Prefix>", allow_message=True
        )
    ]
    assert warnings == ["<Prefix> must be a valid thread URL"], warnings


@pytest.mark.parametrize(
    "thread_url",
    [
        "list-name@python.org",
        "distutils-sig@python.org",
        "csv@python.org",
        "python-3000@python.org",
        "ipaddr-py-dev@googlegroups.com",
        "python-tulip@googlegroups.com",
        "https://discuss.python.org/t/thread-name/123456",
        "https://discuss.python.org/t/thread-name/123456/",
        "https://discuss.python.org/t/thread_name/123456",
        "https://discuss.python.org/t/thread_name/123456/",
        "https://discuss.python.org/t/123456/",
        "https://discuss.python.org/t/123456",
    ],
)
def test_thread_checker_valid_discussions_to(thread_url: str):
    warnings = [
        warning
        for (_, warning) in check_peps._thread(
            1, thread_url, "<Prefix>", discussions_to=True
        )
    ]
    assert warnings == [], warnings


@pytest.mark.parametrize(
    "thread_url",
    [
        "https://discuss.python.org/t/thread-name/123456/000",
        "https://discuss.python.org/t/thread-name/123456/000/",
        "https://discuss.python.org/t/thread_name/123456/000",
        "https://discuss.python.org/t/thread_name/123456/000/",
        "https://discuss.python.org/t/123456/000/",
        "https://discuss.python.org/t/12345656/000",
        "https://discuss.python.org/t/thread-name",
        "https://discuss.python.org/t/thread_name",
        "https://discuss.python.org/t/thread+name",
    ],
)
def test_thread_checker_invalid_discussions_to(thread_url: str):
    warnings = [
        warning
        for (_, warning) in check_peps._thread(
            1, thread_url, "<Prefix>", discussions_to=True
        )
    ]
    assert warnings == ["<Prefix> must be a valid thread URL"], warnings


def test_thread_checker_allow_message_discussions_to():
    with pytest.raises(ValueError, match="cannot both be True"):
        list(
            check_peps._thread(
                1, "", "<Prefix>", allow_message=True, discussions_to=True
            )
        )
