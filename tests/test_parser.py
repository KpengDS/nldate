from datetime import date, timedelta

import pytest

from nldate import parse


def test_today():
    assert parse("today", date(2026, 11, 4)) == date(2026, 11, 4)


def test_tomorrow():
    assert parse("tomorrow", date(2026, 11, 4)) == date(2026, 11, 5)


def test_yesterday():
    assert parse("yesterday", date(2026, 11, 4)) == date(2026, 11, 3)


def test_in_five_days():
    assert parse("in 5 days", date(2026, 11, 4)) == date(2026, 11, 9)


def test_three_days_ago():
    assert parse("3 days ago", date(2026, 11, 4)) == date(2026, 11, 1)


def test_next_tuesday():
    assert parse("next Tuesday", date(2026, 11, 4)) == date(2026, 11, 10)


def test_last_monday():
    assert parse("last Monday", date(2026, 11, 4)) == date(2026, 11, 2)


def test_absolute_date():
    assert parse("December 1st, 2025") == date(2025, 12, 1)


def test_days_before_date():
    assert parse("5 days before December 1st, 2025") == date(2025, 11, 26)


def test_two_weeks_from_tomorrow():
    assert parse("two weeks from tomorrow", date(2026, 11, 4)) == date(2026, 11, 19)


def test_invalid_input():
    with pytest.raises(ValueError):
        parse("not a date")


def test_empty_string():
    with pytest.raises(ValueError):
        parse("")