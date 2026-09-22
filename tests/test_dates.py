"""Deterministic date and amount extraction — the CODE stage."""
from datetime import datetime, timezone

from isobard.dates import extract_amount, extract_due, extract_invoice_id, extract_quote_id


def ns(y, m, d, h=10):
    return int(datetime(y, m, d, h, tzinfo=timezone.utc).timestamp() * 1e9)


def day(x):
    return datetime.fromtimestamp(x / 1e9, tz=timezone.utc).date()


def test_by_friday_from_a_wednesday():
    due, span = extract_due("I will send it by Friday.", ns(2026, 9, 16))   # Wed
    assert day(due).isoformat() == "2026-09-18" and span.lower().endswith("friday")


def test_next_week_is_next_friday():
    due, _ = extract_due("You'll have them next week.", ns(2026, 9, 16))
    assert day(due).isoformat() == "2026-09-25"


def test_in_30_days():
    due, _ = extract_due("invoice attached, due in 30 days", ns(2026, 8, 13))
    assert day(due).isoformat() == "2026-09-12"


def test_iso_and_ordinal():
    assert day(extract_due("deadline 2026-10-03 firm", ns(2026, 9, 1))[0]).isoformat() == "2026-10-03"
    assert day(extract_due("still on for the 30th?", ns(2026, 9, 13))[0]).isoformat() == "2026-09-30"


def test_no_date():
    assert extract_due("thanks, no action needed", ns(2026, 9, 1)) is None


def test_amount_and_ids():
    assert extract_amount("proposal, $23,400 total") == (2340000, "USD")
    assert extract_amount("$8,150.25 due") == (815025, "USD")
    assert extract_invoice_id("Invoice #1041 — $8,150") == "INV-1041"
    assert extract_quote_id("see quote 5521") == "Q-5521"
    assert extract_invoice_id("no ids here") is None
