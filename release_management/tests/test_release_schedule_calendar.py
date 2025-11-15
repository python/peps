import pytest

from release_management import serialize


@pytest.mark.parametrize(
    ('test_input', 'expected'),
    [
        ('3.14.0 alpha 1', 'python-3.14.0alpha1@releases.python.org'),
        ('3.14.0 beta 2', 'python-3.14.0beta2@releases.python.org'),
        ('3.14.0 candidate 3', 'python-3.14.0candidate3@releases.python.org'),
        ('3.14.1', 'python-3.14.1@releases.python.org'),
    ],
)
def test_ical_uid(test_input, expected):
    assert serialize.ical_uid(test_input) == expected


def test_create_release_calendar_has_calendar_metadata():
    # Act
    cal_lines = serialize.create_release_schedule_calendar().split('\n')

    # Assert

    # Check calendar metadata
    assert cal_lines[:5] == [
        'BEGIN:VCALENDAR',
        'VERSION:2.0',
        'PRODID:-//Python Software Foundation//Python release schedule//EN',
        'X-WR-CALDESC:Python releases schedule from https://peps.python.org',
        'X-WR-CALNAME:Python releases schedule',
    ]
    assert cal_lines[-2:] == [
        'END:VCALENDAR',
        '',
    ]


def test_create_release_calendar_first_event():
    # Act
    cal_lines = serialize.create_release_schedule_calendar().split('\n')

    # Assert
    assert cal_lines[5] == 'BEGIN:VEVENT'
    assert cal_lines[6].startswith('SUMMARY:Python ')
    assert cal_lines[7].startswith('DTSTART;VALUE=DATE:')
    assert cal_lines[8].startswith('UID:python-')
    assert cal_lines[8].endswith('@release.python.org')
    assert cal_lines[9].startswith('URL:https://peps.python.org/pep-')
    assert cal_lines[10].startswith('END:VEVENT')
