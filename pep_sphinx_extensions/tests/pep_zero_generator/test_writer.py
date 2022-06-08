from pathlib import Path

import pytest

from pep_sphinx_extensions.pep_zero_generator import parser, writer


def test_pep_zero_writer_emit_text_newline():
    pep0_writer = writer.PEPZeroWriter()
    pep0_writer.emit_text("my text 1")
    pep0_writer.emit_newline()
    pep0_writer.emit_text("my text 2")

    assert pep0_writer.output == ["my text 1", "", "my text 2"]


def test_pep_zero_writer_emit_title():
    pep0_writer = writer.PEPZeroWriter()
    pep0_writer.emit_title("My Title")
    pep0_writer.emit_subtitle("My Subtitle")

    assert pep0_writer.output == [
        "My Title",
        "========",
        "",
        "My Subtitle",
        "-----------",
        "",
    ]


@pytest.mark.parametrize(
    "test_input, expected",
    [
        (
            "pep-9000.rst",
            {
                "Fussyreverend, Francis": "one@example.com",
                "Soulfulcommodore, Javier": "two@example.com",
            },
        ),
        (
            "pep-9001.rst",
            {"Fussyreverend, Francis": "", "Soulfulcommodore, Javier": ""},
        ),
    ],
)
def test_verify_email_addresses(test_input, expected):
    # Arrange
    peps = [parser.PEP(Path(f"pep_sphinx_extensions/tests/peps/{test_input}"))]

    # Act
    out = writer._verify_email_addresses(peps)

    # Assert
    assert out == expected


def test_sort_authors():
    # Arrange
    authors_dict = {
        "Zebra, Zoë": "zoe@example.com",
        "lowercase, laurence": "laurence@example.com",
        "Aardvark, Alfred": "alfred@example.com",
    }

    # Act
    out = writer._sort_authors(authors_dict)

    # Assert
    assert out == ["Aardvark, Alfred", "lowercase, laurence", "Zebra, Zoë"]
