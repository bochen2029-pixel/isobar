"""contacts seed from a vCard export — one read; growth comes from mail and calendar identities."""
from __future__ import annotations

from pathlib import Path
from typing import Iterator


class VcfContacts:
    id = "contacts_vcf"
    lanes = ("contacts",)
    consent_class = "contacts"

    def __init__(self, path: Path):
        self.path = Path(path)

    def capabilities(self) -> list:
        return []

    def cards(self) -> Iterator[dict]:
        cur: dict = {}
        for line in self.path.read_text(encoding="utf-8", errors="replace").splitlines():
            u = line.upper()
            if u.startswith("BEGIN:VCARD"):
                cur = {}
            elif u.startswith("FN:"):
                cur["fn"] = line[3:].strip()
            elif u.startswith("EMAIL"):
                cur.setdefault("email", line.split(":", 1)[-1].strip())
            elif u.startswith("TEL"):
                cur.setdefault("tel", line.split(":", 1)[-1].strip())
            elif u.startswith("ORG:"):
                cur["org"] = line[4:].strip()
            elif u.startswith("ADR"):
                cur.setdefault("adr", line.split(":", 1)[-1].strip())
            elif u.startswith("CATEGORIES:"):
                cur["categories"] = line.split(":", 1)[-1].strip()
            elif u.startswith("END:VCARD"):
                if cur.get("fn") or cur.get("email"):
                    yield cur
