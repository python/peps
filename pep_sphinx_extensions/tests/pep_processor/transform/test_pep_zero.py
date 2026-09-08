import pytest
from docutils import nodes

from pep_sphinx_extensions.pep_processor.transforms import pep_zero


@pytest.mark.parametrize(
    ("test_input", "expected"),
    [
        (
            nodes.reference(
                "", text="user@example.com", refuri="mailto:user@example.com"
            ),
            "user at example.com",
        ),
        (
            nodes.reference("", text="Introduction", refid="introduction"),
            '<reference refid="introduction">Introduction</reference>',
        ),
    ],
)
def test_generate_list_url(test_input, expected):
    out = pep_zero._mask_email(test_input)

    assert str(out) == expected
