import datetime as dt

import check_peps  # NoQA: inserted into sys.modules in conftest.py
import pytest


@pytest.mark.parametrize(
    "line",
    [
        # valid entries
        "01-Jan-2000",
        "29-Feb-2016",
        "31-Dec-2000",
        "01-Apr-2003",
        "01-Apr-2007",
        "01-Apr-2009",
        "01-Jan-1990",
    ],
)
def test_validate_created(line: str):
    warnings = [warning for (_, warning) in check_peps._validate_created(1, line)]
    assert warnings == [], warnings


@pytest.mark.parametrize(
    "date_str",
    [
        # valid entries
        "01-Jan-2000",
        "29-Feb-2016",
        "31-Dec-2000",
        "01-Apr-2003",
        "01-Apr-2007",
        "01-Apr-2009",
        "01-Jan-1990",
    ],
)
def test_date_checker_valid(date_str: str):
    warnings = [warning for (_, warning) in check_peps._date(1, date_str, "<Prefix>")]
    assert warnings == [], warnings


@pytest.mark.parametrize(
    "date_str",
    [
        # malformed
        "2000-01-01",
        "01 January 2000",
        "1 Jan 2000",
        "1-Jan-2000",
        "1-January-2000",
        "Jan-1-2000",
        "January 1 2000",
        "January 01 2000",
        "01/01/2000",
        "01/Jan/2000",  # 🇬🇧, 🇦🇺, 🇨🇦, 🇳🇿, 🇮🇪 , ...
        "Jan/01/2000",  # 🇺🇸
        "1st January 2000",
        "The First day of January in the year of Our Lord Two Thousand",
        "Jan, 1, 2000",
        "2000-Jan-1",
        "2000-Jan-01",
        "2000-January-1",
        "2000-January-01",
        "00 Jan 2000",
        "00-Jan-2000",
    ],
)
def test_date_checker_malformed(date_str: str):
    warnings = [warning for (_, warning) in check_peps._date(1, date_str, "<Prefix>")]
    expected = f"<Prefix> must be a 'DD-mmm-YYYY' date: {date_str!r}"
    assert warnings == [expected], warnings


@pytest.mark.parametrize(
    "date_str",
    [
        # too early
        "31-Dec-1989",
        "01-Apr-1916",
        "01-Jan-0020",
        "01-Jan-0023",
    ],
)
def test_date_checker_too_early(date_str: str):
    warnings = [warning for (_, warning) in check_peps._date(1, date_str, "<Prefix>")]
    expected = f"<Prefix> must not be before Python was invented: {date_str!r}"
    assert warnings == [expected], warnings


@pytest.mark.parametrize(
    "date_str",
    [
        # the future
        "31-Dec-2999",
        "01-Jan-2100",
        "01-Jan-2100",
        (dt.datetime.now() + dt.timedelta(days=15)).strftime("%d-%b-%Y"),
        (dt.datetime.now() + dt.timedelta(days=100)).strftime("%d-%b-%Y"),
    ],
)
def test_date_checker_too_late(date_str: str):
    warnings = [warning for (_, warning) in check_peps._date(1, date_str, "<Prefix>")]
    expected = f"<Prefix> must not be in the future: {date_str!r}"
    assert warnings == [expected], warnings
