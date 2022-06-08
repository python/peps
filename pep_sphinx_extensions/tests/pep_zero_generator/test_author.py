import pytest

from pep_sphinx_extensions.pep_zero_generator import author
from pep_sphinx_extensions.tests.utils import AUTHORS_OVERRIDES


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (
            ("First Last", "first@example.com"),
            author.Author(
                last_first="Last, First", nick="Last", email="first@example.com"
            ),
        ),
        (
            ("Guido van Rossum", "guido@example.com"),
            author.Author(
                last_first="van Rossum, Guido (GvR)",
                nick="GvR",
                email="guido@example.com",
            ),
        ),
        (
            ("Hugo van Kemenade", "hugo@example.com"),
            author.Author(
                last_first="van Kemenade, Hugo",
                nick="van Kemenade",
                email="hugo@example.com",
            ),
        ),
        (
            ("Eric N. Vander Weele", "eric@example.com"),
            author.Author(
                last_first="Vander Weele, Eric N.",
                nick="Vander Weele",
                email="eric@example.com",
            ),
        ),
        (
            ("Mariatta", "mariatta@example.com"),
            author.Author(
                last_first="Mariatta", nick="Mariatta", email="mariatta@example.com"
            ),
        ),
        (
            ("First Last Jr.", "first@example.com"),
            author.Author(
                last_first="Last, First, Jr.", nick="Last", email="first@example.com"
            ),
        ),
        pytest.param(
            ("First Last", "first at example.com"),
            author.Author(
                last_first="Last, First", nick="Last", email="first@example.com"
            ),
            marks=pytest.mark.xfail,
        ),
    ],
)
def test_parse_author_email(test_input, expected):
    out = author.parse_author_email(test_input, AUTHORS_OVERRIDES)

    assert out == expected


def test_parse_author_email_empty_name():
    with pytest.raises(ValueError, match="Name is empty!"):
        author.parse_author_email(("", "user@example.com"), AUTHORS_OVERRIDES)
