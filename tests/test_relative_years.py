"""Calendar-year offsets and compound relative durations."""

from datetime import date

import pytest

from nldate import parse


@pytest.mark.parametrize(
    ("expression", "reference", "expected"),
    [
        ("2 years ago", date(2026, 11, 4), date(2024, 11, 4)),
        ("2 years from now", date(2026, 11, 4), date(2028, 11, 4)),
        ("in two years", date(2024, 2, 29), date(2026, 2, 28)),
        ("2 years ago", date(2024, 2, 29), date(2022, 2, 28)),
        ("1 year from today", date(2024, 2, 29), date(2025, 2, 28)),
        ("4 years from today", date(2024, 2, 29), date(2028, 2, 29)),
        ("100 years after Feb. 29, 2000", date(2026, 1, 1), date(2100, 2, 28)),
        ("400 years after Feb. 29, 2000", date(2026, 1, 1), date(2400, 2, 29)),
        ("2 years later", date(2024, 2, 29), date(2026, 2, 28)),
        ("two years hence", date(2024, 2, 29), date(2026, 2, 28)),
        ("2 years, 3 months from now", date(2024, 2, 29), date(2026, 5, 29)),
        ("2 years,3 months ago", date(2024, 2, 29), date(2021, 11, 29)),
        (
            "2 years, 3 months, and 4 days after 2024/2/29",
            date(2026, 1, 1),
            date(2026, 6, 2),
        ),
        ("2 years and 1 day after 2024-02-29", date(2026, 1, 1), date(2026, 3, 1)),
        ("1 year and 2 months after yesterday", date(2026, 11, 4), date(2028, 1, 3)),
        ("2 YEARS, 1 MONTH FROM TOMORROW", date(2024, 1, 30), date(2026, 2, 28)),
        ("in 1 year", date(2023, 3, 1), date(2024, 3, 1)),
    ],
)
def test_calendar_year_offsets(
    expression: str, reference: date, expected: date
) -> None:
    assert parse(expression, reference) == expected


@pytest.mark.parametrize(
    "expression",
    [
        "2 years, ago",
        "2 years,, 1 month ago",
        "2 years and ago",
        "2 years nonsense",
        "10000 years from now",
    ],
)
def test_invalid_year_offsets(expression: str) -> None:
    with pytest.raises(ValueError):
        parse(expression, date(2024, 2, 29))
