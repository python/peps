from pep_sphinx_extensions.pep_processor.html import pep_html_translator


def test_create_release_list():
    # Arrange
    release_dates = {
        "3.14.0 alpha 7": "2025-04-08",
        "3.14.0 beta 1": "2025-05-06",
        "3.14.0 beta 2": "2025-05-27",
        "3.14.0 beta 3": "2025-06-17",
        "3.14.0 beta 4": "2025-07-08",
        "3.14.0 candidate 1": "2025-07-22",
        "3.14.0 candidate 2": "2025-08-26",
        "3.14.0 final": "2025-10-07",
    }

    # Act
    result = pep_html_translator.create_release_list(release_dates)

    # Assert
    assert result.splitlines() == [
        '<ul class="simple"><li>3.14.0 alpha 7: Tuesday, 2025-04-08',
        "<li>3.14.0 beta 1: Tuesday, 2025-05-06 (No new features beyond this point.)",
        "<li>3.14.0 beta 2: Tuesday, 2025-05-27",
        "<li>3.14.0 beta 3: Tuesday, 2025-06-17",
        "<li>3.14.0 beta 4: Tuesday, 2025-07-08",
        "<li>3.14.0 candidate 1: Tuesday, 2025-07-22",
        "<li>3.14.0 candidate 2: Tuesday, 2025-08-26",
        "<li>3.14.0 final: Tuesday, 2025-10-07</ul>",
    ]
