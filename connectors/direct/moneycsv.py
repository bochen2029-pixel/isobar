"""A money VERDICT source from a CSV export (Stripe / QuickBooks / Xero / a bank feed all export one).

Read-only. `capabilities()` is empty in every rung. Columns: id,kind,counterparty_email,amount_minor,
currency,issued,due,status  — status ∈ {sent, paid, partially_paid, overdue, declined, accepted}.
"""
from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Optional


def _ns(s: str) -> Optional[int]:
    s = (s or "").strip()
    if not s:
        return None
    return int(datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() * 1e9)


class MoneyCsvVerdict:
    id = "money_csv"
    lanes = ("money",)
    consent_class = "money"

    def __init__(self, path: Path):
        self.path = Path(path)

    def capabilities(self) -> list:
        return []            # a verdict source: read-only, always

    def rows(self) -> Iterator[dict]:
        with open(self.path, newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                yield {"id": r["id"].strip(), "kind": r["kind"].strip(), "counterparty_email": r["counterparty_email"].strip().lower(),
                       "amount_minor": int(r["amount_minor"] or 0), "currency": r.get("currency", "USD").strip() or "USD",
                       "issued_ns": _ns(r.get("issued", "")), "due_ns": _ns(r.get("due", "")), "status": r["status"].strip()}
