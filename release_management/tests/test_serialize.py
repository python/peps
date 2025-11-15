import pytest
from icalendar import Calendar
from release_management import serialize


@pytest.mark.parametrize(
    ('test_input', 'expected'),
    [
        ('3.14.0 alpha 1', 'python-3.14.0alpha1@python.org'),
        ('3.14.0 beta 2', 'python-3.14.0beta2@python.org'),
        ('3.14.0 candidate 3', 'python-3.14.0candidate3@python.org'),
        ('3.14.1', 'python-3.14.1@python.org'),
    ],
)
def test_ical_uid(test_input, expected):
    assert serialize.ical_uid(test_input) == expected


def test_create_release_ical_returns_valid_icalendar():
    # Act
    ical_str = serialize.create_release_ical()

    # Assert
    # Non-empty string
    assert isinstance(ical_str, str)
    assert len(ical_str) > 0

    # Parseable as a valid iCalendar
    cal = Calendar.from_ical(ical_str)
    assert cal is not None


def test_create_release_ical_has_calendar_metadata():
    # Act
    ical_str = serialize.create_release_ical()

    # Assert
    cal = Calendar.from_ical(ical_str)

    # Check calendar metadata
    assert cal.get('version') == '2.0'
    assert cal.get('prodid') == '-//Python Software Foundation//Python releases//EN'
    assert cal.get('x-wr-calname') == 'Python releases'
    assert 'peps.python.org' in cal.get('x-wr-caldesc')


def test_create_release_ical_first_event():
    # Act
    ical_str = serialize.create_release_ical()

    # Assert
    cal = Calendar.from_ical(ical_str)
    first_event = cal.events[0]
    assert first_event.get('summary') == 'Python 1.6.0 alpha 1'
    assert str(first_event.get('dtstart').dt) == '2000-03-31'
    assert first_event.get('uid') == 'python-1.6.0alpha1@python.org'
    assert first_event.get('url') == 'https://peps.python.org/pep-0160/'


def test_create_release_ical_sorted_by_date():
    # Act
    ical_str = serialize.create_release_ical()

    # Assert
    cal = Calendar.from_ical(ical_str)
    dates = [event.get('dtstart').dt for event in cal.events]
    assert dates == sorted(dates)
