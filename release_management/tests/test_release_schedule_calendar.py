import datetime as dt

from release_management import ReleaseInfo, serialize

FAKE_RELEASE = ReleaseInfo(
    stage='X.Y.Z final',
    state='actual',
    date=dt.date(2000, 1, 1),
    note='These characters need escaping: \\ , ; \n',
)


def test_create_release_calendar_has_calendar_metadata() -> None:
    # Act
    cal_lines = serialize.create_release_schedule_calendar().split('\r\n')

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


def test_create_release_calendar_first_event() -> None:
    # Act
    releases = [(9999, FAKE_RELEASE)]
    cal_lines = serialize.release_schedule_calendar_lines(releases)

    # Assert
    assert cal_lines[5] == 'BEGIN:VEVENT'
    assert cal_lines[6].startswith('DTSTAMP:')
    assert cal_lines[6].endswith('Z')
    assert cal_lines[7] == 'UID:python-X.Y.Zfinal@releases.python.org'
    assert cal_lines[8] == 'DTSTART;VALUE=DATE:20000101'
    assert cal_lines[9] == 'SUMMARY:Python X.Y.Z final'
    assert cal_lines[10] == (
        'DESCRIPTION:Note: These characters need escaping: \\\\ \\, \\; \\n'
    )
    assert cal_lines[11] == 'URL:https://peps.python.org/pep-9999/'
    assert cal_lines[12] == 'END:VEVENT'
