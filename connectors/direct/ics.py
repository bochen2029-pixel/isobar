"""calendar lane from an .ics export (any provider). Recurrences are expanded within the horizon at
ingest (the rule is provenance); all-day events consume zero slots; TENTATIVE carries p_accept."""
from __future__ import annotations

import re
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator, Optional

from isobard.contracts import Observation, blake128

_DT = re.compile(r"^(\d{4})(\d{2})(\d{2})(?:T(\d{2})(\d{2})(\d{2})(Z?))?$")


def parse_dt(v: str) -> tuple[int, bool]:
    """Returns (utc_ns, all_day). Naive local times are treated as UTC at M0 (owner.tz arrives with the lock)."""
    v = v.strip()
    m = _DT.match(v)
    if not m:
        raise ValueError(v)
    y, mo, d = int(m[1]), int(m[2]), int(m[3])
    if m[4] is None:
        return int(datetime(y, mo, d, tzinfo=timezone.utc).timestamp() * 1e9), True
    dt = datetime(y, mo, d, int(m[4]), int(m[5]), int(m[6]), tzinfo=timezone.utc)
    return int(dt.timestamp() * 1e9), False


def _unfold(lines: list[str]) -> list[str]:
    out: list[str] = []
    for ln in lines:
        if ln.startswith((" ", "\t")) and out:
            out[-1] += ln[1:]
        else:
            out.append(ln.rstrip("\r"))
    return out


class IcsConnector:
    id = "ics"
    lanes = ("cal",)
    consent_class = "standard"

    def __init__(self, path: Path, horizon_days: int = 14, source_name: str = "ics"):
        self.path = Path(path)
        self.horizon_days = horizon_days
        self.source_name = source_name

    def capabilities(self) -> list:
        return []

    def events(self) -> Iterator[dict]:
        cur: Optional[dict] = None
        for ln in _unfold(self.path.read_text(encoding="utf-8", errors="replace").splitlines()):
            if ln == "BEGIN:VEVENT":
                cur = {}
            elif ln == "END:VEVENT" and cur is not None:
                yield cur
                cur = None
            elif cur is not None and ":" in ln:
                k, v = ln.split(":", 1)
                key = k.split(";", 1)[0].upper()
                cur[key] = v
                if ";" in k:
                    cur[key + "_PARAMS"] = k.split(";", 1)[1]

    def backfill(self, since_ns: int = 0, cursor: Optional[str] = None) -> Iterator[tuple[Observation, dict]]:
        now = time.time_ns()
        horizon_end = now + self.horizon_days * 86400 * 10**9
        for ev in self.events():
            try:
                start, all_day = parse_dt(ev.get("DTSTART", ""))
                end, _ = parse_dt(ev.get("DTEND", ev.get("DTSTART", "")))
            except ValueError:
                continue
            instances = [(start, end)]
            rr = ev.get("RRULE", "")
            if rr:
                freq = re.search(r"FREQ=(\w+)", rr)
                count = re.search(r"COUNT=(\d+)", rr)
                step = {"DAILY": 1, "WEEKLY": 7}.get(freq[1] if freq else "", 0)
                if step:
                    n = int(count[1]) if count else 60
                    instances = [(start + k * step * 86400 * 10**9, end + k * step * 86400 * 10**9) for k in range(n)]
            uid = ev.get("UID", blake128(str(ev).encode()))
            for k, (s, e) in enumerate(instances):
                if s < since_ns or s > horizon_end:
                    continue
                text = f"SUMMARY: {ev.get('SUMMARY','')}\nSTART: {s}\nEND: {e}\nLOCATION: {ev.get('LOCATION','')}\nSTATUS: {ev.get('STATUS','')}\nATTENDEES: {ev.get('ATTENDEE','')}\nDESCRIPTION: {ev.get('DESCRIPTION','')}"
                obs = Observation(lane="cal", source=self.source_name, external_id=f"{uid}#{k}", src_rev=int(ev.get("SEQUENCE", "0") or 0),
                                  occurred_ns=s, ingested_ns=now, payload_ref="inline:" + text, digest=blake128(text.encode()),
                                  intake_trust="operator").with_id()
                yield obs, {"summary": ev.get("SUMMARY", ""), "start_ns": s, "end_ns": e, "all_day": all_day,
                            "location": ev.get("LOCATION", ""), "status": ev.get("STATUS", "CONFIRMED"),
                            "p_accept": 0.6 if ev.get("STATUS", "").upper() == "TENTATIVE" else 1.0,
                            "attendees": re.findall(r"mailto:([^;,\s]+)", ev.get("ATTENDEE", "") + " " + ev.get("DESCRIPTION", ""), re.I),
                            "recurring": bool(rr), "uid": uid, "description": ev.get("DESCRIPTION", "")}

    def delta(self, cursor: str) -> Iterator[tuple[Observation, dict]]:
        return self.backfill(int(cursor) if cursor else 0)
