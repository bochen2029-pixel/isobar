"""list lane from a todo.txt or a markdown checklist — the owner's testimony lane at its simplest.

Lines:  `- [ ] send Lopez the revised proposal due:2026-09-25`   `x 2026-09-20 pay the ISP bill`
        `(A) call mom`   `- [x] done thing`
"""
from __future__ import annotations

import hashlib
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, Optional

from isobard.contracts import Observation, blake128

_DUE = re.compile(r"\bdue:(\d{4}-\d{2}-\d{2})\b")
_PRI = re.compile(r"^\(([A-Z])\)\s+")


class TextListConnector:
    id = "textfile"
    lanes = ("list",)
    consent_class = "standard"

    def __init__(self, path: Path, source_name: str = "textfile"):
        self.path = Path(path)
        self.source_name = source_name

    def capabilities(self) -> list:
        return [{"target": "list.create", "reversibility": "reversible", "inverse_template": "list.delete", "hold_window_s": 0}]

    def backfill(self, since_ns: int = 0, cursor: Optional[str] = None) -> Iterator[tuple[Observation, dict]]:
        now = time.time_ns()
        mtime_ns = int(self.path.stat().st_mtime_ns)
        for n, raw in enumerate(self.path.read_text(encoding="utf-8", errors="replace").splitlines()):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            done = False
            if line.startswith("- [x]") or line.startswith("- [X]"):
                done, line = True, line[5:].strip()
            elif line.startswith("- [ ]"):
                line = line[5:].strip()
            elif line.startswith("x "):
                done, line = True, re.sub(r"^x\s+(\d{4}-\d{2}-\d{2}\s+)?", "", line)
            elif line.startswith("- "):
                line = line[2:].strip()
            pri = _PRI.match(line)
            priority = pri[1] if pri else None
            line = _PRI.sub("", line)
            due = _DUE.search(line)
            due_ns = int(datetime.strptime(due[1], "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() * 1e9) if due else None
            text = _DUE.sub("", line).strip()
            ext = hashlib.blake2b(f"{n}:{text}".encode(), digest_size=8).hexdigest()
            obs = Observation(lane="list", source=self.source_name, external_id=ext, src_rev=0, occurred_ns=mtime_ns,
                              ingested_ns=now, payload_ref="inline:" + raw, digest=blake128(raw.encode()),
                              intake_trust="operator").with_id()
            yield obs, {"text": text, "done": done, "due_ns": due_ns, "priority": priority, "line": n}

    def delta(self, cursor: str) -> Iterator[tuple[Observation, dict]]:
        return self.backfill(int(cursor) if cursor else 0)
