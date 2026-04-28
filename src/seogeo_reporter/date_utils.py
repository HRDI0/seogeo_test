from __future__ import annotations

import calendar
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MonthRange:
    start_date: str
    end_date: str


def month_range(month: str) -> MonthRange:
    """Return YYYY-MM-01 and YYYY-MM-last_day with strict validation."""
    year, mon = _parse_month(month)
    last_day = calendar.monthrange(year, mon)[1]
    return MonthRange(
        start_date=f"{year:04d}-{mon:02d}-01",
        end_date=f"{year:04d}-{mon:02d}-{last_day:02d}",
    )


def previous_month(month: str) -> str:
    year, mon = _parse_month(month)
    if mon == 1:
        return f"{year - 1:04d}-12"
    return f"{year:04d}-{mon - 1:02d}"


def _parse_month(month: str) -> tuple[int, int]:
    try:
        year_str, mon_str = month.split("-", 1)
        year = int(year_str)
        mon = int(mon_str)
    except Exception as exc:
        raise ValueError(f"Invalid month format: {month}. Expected YYYY-MM") from exc

    if mon < 1 or mon > 12:
        raise ValueError(f"Invalid month: {month}. Month must be 01..12")
    return year, mon
