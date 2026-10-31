"""Indicative dates from a complete, typed, uncommitted supplier offer.

Incomplete historical offers remain useful as conditional possibilities, but
cannot acquire a date from a current supplier calendar or a modal lead alone.
"""

from datetime import timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def _workday(start, weekdays):
    while start.isoweekday() not in weekdays:
        start += timedelta(days=1)
    return start


def _lead_date(order_date, days, weekdays):
    result = _workday(order_date, weekdays)
    for _ in range(days):
        result = _workday(result + timedelta(days=1), weekdays)
    return result


def estimate_supplier_offer(offer, as_of):
    """Return a nonbinding date range, or None if any dated input is unsafe."""
    calendar = offer.get("order_calendar_json")
    if not isinstance(calendar, dict) or calendar.get("holiday_dates") != []:
        return None
    weekdays = calendar.get("working_weekdays")
    if (not isinstance(weekdays, list) or not weekdays or
            any(type(day) is not int or day not in range(1, 8) for day in weekdays) or
            len(set(weekdays)) != len(weekdays)):
        return None
    leads = [offer.get(key) for key in ("lead_days_min", "lead_days_mode", "lead_days_max")]
    if any(type(value) is not int or value < 0 for value in leads) or leads != sorted(leads):
        return None
    try:
        zone = ZoneInfo(calendar["time_zone"])
        order_date = as_of.astimezone(zone).date()
    except (KeyError, TypeError, ValueError, ZoneInfoNotFoundError):
        return None
    earliest, mode, latest = (_lead_date(order_date, days, set(weekdays)) for days in leads)
    return {
        "supplier_item_id": offer["supplier_item_id"],
        "supplier_id": offer["supplier_id"],
        "source": "uncommitted_supplier_offer", "binding": False,
        "order_date": order_date,
        "earliest": earliest, "mode": mode, "latest": latest,
    }
