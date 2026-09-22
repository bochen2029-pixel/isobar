"""Deterministic date and amount extraction — the CODE stage. The reflex only says whether a
deadline was mentioned; the VALUE comes from here, never from a model."""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Optional

_WEEKDAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
_ISO = re.compile(r"\b(20\d{2})-(\d{2})-(\d{2})\b")
_MDY = re.compile(r"\b(\d{1,2})/(\d{1,2})(?:/(20\d{2}))?\b")
_ORD = re.compile(r"\b(?:on |by |before )?(?:the )?(\d{1,2})(?:st|nd|rd|th)\b", re.I)
_WD = re.compile(r"\b(?:by |on |before |until |due )?(next )?(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b", re.I)
_IN = re.compile(r"\bin (\d{1,3}) (day|days|week|weeks|hour|hours)\b", re.I)
_REL = re.compile(r"\b(today|tomorrow|end of (?:the )?day|eod|end of (?:the )?week|next week|end of (?:the )?month)\b", re.I)
_MONEY = re.compile(r"(?:\$|USD\s?)\s?(\d{1,3}(?:,\d{3})+|\d+)(?:\.(\d{2}))?", re.I)
_INV = re.compile(r"\b(?:invoice|inv)\s*#?\s*(\d{3,7})\b", re.I)
_QUOTE = re.compile(r"\b(?:quote|proposal)\s*#?\s*(\d{3,7})\b", re.I)


def _dt(ns: int) -> datetime:
    return datetime.fromtimestamp(ns / 1e9, tz=timezone.utc)


def _ns(dt: datetime) -> int:
    return int(dt.timestamp() * 1e9)


def extract_due(text: str, ref_ns: int) -> Optional[tuple[int, str]]:
    """Returns (due_ns, span_text) for the first date-like mention, relative to the message's time."""
    ref = _dt(ref_ns)
    m = _ISO.search(text)
    if m:
        return _ns(datetime(int(m[1]), int(m[2]), int(m[3]), 17, tzinfo=timezone.utc)), m[0]
    m = _MDY.search(text)
    if m:
        y = int(m[3]) if m[3] else ref.year
        try:
            return _ns(datetime(y, int(m[1]), int(m[2]), 17, tzinfo=timezone.utc)), m[0]
        except ValueError:
            pass
    m = _REL.search(text)
    if m:
        k = m[1].lower()
        if k == "today" or k.startswith("end of") and "day" in k or k == "eod":
            d = ref.replace(hour=17, minute=0)
        elif k == "tomorrow":
            d = (ref + timedelta(days=1)).replace(hour=17, minute=0)
        elif "week" in k and "next" in k:
            d = (ref + timedelta(days=(7 - ref.weekday()) + 4)).replace(hour=17, minute=0)   # next Friday
        elif "week" in k:
            d = (ref + timedelta(days=(4 - ref.weekday()) % 7)).replace(hour=17, minute=0)
        else:
            nxt = (ref.replace(day=1) + timedelta(days=32)).replace(day=1)
            d = (nxt - timedelta(days=1)).replace(hour=17, minute=0)
        return _ns(d), m[0]
    m = _IN.search(text)
    if m:
        n, unit = int(m[1]), m[2].lower()
        delta = timedelta(days=n) if unit.startswith("day") else timedelta(weeks=n) if unit.startswith("week") else timedelta(hours=n)
        return _ns(ref + delta), m[0]
    m = _WD.search(text)
    if m:
        wd = _WEEKDAYS.index(m[2].lower())
        ahead = (wd - ref.weekday()) % 7
        if ahead == 0 or m[1]:
            ahead += 7 if (m[1] or ahead == 0) else 0
        d = (ref + timedelta(days=ahead)).replace(hour=17, minute=0)
        return _ns(d), m[0]
    m = _ORD.search(text)
    if m:
        day = int(m[1])
        if 1 <= day <= 31:
            try:
                d = ref.replace(day=day, hour=17, minute=0)
                if d < ref:
                    nxt = (ref.replace(day=1) + timedelta(days=32)).replace(day=day)
                    d = nxt.replace(hour=17, minute=0)
                return _ns(d), m[0]
            except ValueError:
                pass
    return None


def extract_amount(text: str) -> Optional[tuple[int, str]]:
    m = _MONEY.search(text)
    if not m:
        return None
    whole = int(m[1].replace(",", ""))
    cents = int(m[2]) if m[2] else 0
    return whole * 100 + cents, "USD"


def extract_invoice_id(text: str) -> Optional[str]:
    m = _INV.search(text)
    return f"INV-{m[1]}" if m else None


def extract_quote_id(text: str) -> Optional[str]:
    m = _QUOTE.search(text)
    return f"Q-{m[1]}" if m else None
