"""The registries — people, places, money — rows the field reads (docs/contracts/registry.md).

M0 builds people (seed from contacts, tiers from tiers.yaml, growth from mail identities, the
resolution ladder's exact rungs) and the money object shell (mail inference only, labelled
`payment_status_connected: false`). Places arrive at M4a. No registry has a loop or authority.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, Optional

import yaml

from .contracts import Actor, Identity, MoneyObject, Relation

ROOT = Path(__file__).resolve().parents[1]
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", re.I)
_PHONE = re.compile(r"\+?\d[\d\s().-]{7,}\d")


def norm_email(e: str) -> str:
    e = e.strip().lower()
    if "@" in e:
        local, dom = e.split("@", 1)
        if dom in ("gmail.com", "googlemail.com"):
            local = local.split("+", 1)[0].replace(".", "")
            dom = "gmail.com"
        return f"{local}@{dom}"
    return e


def norm_phone(p: str) -> str:
    return re.sub(r"[^\d+]", "", p)


def parse_addr(raw: str) -> tuple[str, str]:
    """'Lopez Acme <lopez@acme.example>' -> ('Lopez Acme', 'lopez@acme.example')."""
    m = _EMAIL.search(raw or "")
    email = norm_email(m.group(0)) if m else ""
    name = (raw or "").replace(m.group(0), "").strip(" <>\"'") if m else (raw or "").strip()
    return name, email


class People:
    """Seeded by one contacts read, grown by every identity mail and calendar produce, tiered by policy."""

    def __init__(self, tiers_path: Path = ROOT / "tiers.yaml"):
        self.by_id: dict[str, Actor] = {}
        self.by_identity: dict[tuple[str, str], str] = {}
        self.tiers = yaml.safe_load(tiers_path.read_text(encoding="utf-8")) if tiers_path.exists() else {}
        self.default_tier = int(self.tiers.get("default_tier", 3))
        self._policy: dict[str, dict] = {}
        for row in self.tiers.get("actors", []) or []:
            self._policy[norm_email(str(row.get("identity", "")))] = row
        self._never = {norm_email(x) for x in (self.tiers.get("never_auto_contact", []) or [])}
        self.owner_id: Optional[str] = None

    # ---- the ladder's exact rungs (M0): exact identity, then domain+name ----
    def resolve(self, name: str, email: str = "", phone: str = "") -> Optional[Actor]:
        if email and ("email", norm_email(email)) in self.by_identity:
            return self.by_id[self.by_identity[("email", norm_email(email))]]
        if phone and ("phone", norm_phone(phone)) in self.by_identity:
            return self.by_id[self.by_identity[("phone", norm_phone(phone))]]
        if email and name:
            dom = norm_email(email).split("@")[-1]
            for a in self.by_id.values():
                if a.display_name.lower() == name.lower() and any(i.value.endswith("@" + dom) for i in a.identities):
                    return a
        return None

    def upsert(self, name: str, email: str = "", phone: str = "", source: str = "mail", ns: int = 0,
               relation: Optional[Relation] = None, is_owner: bool = False) -> Actor:
        a = self.resolve(name, email, phone)
        if a is None:
            key = norm_email(email) if email else (norm_phone(phone) if phone else name.lower())
            aid = "act_" + re.sub(r"[^a-z0-9]+", "_", key)[:48]
            a = Actor(id=aid, display_name=name or key, confirmed_by="inferred", provenance=[source])
            self.by_id[aid] = a
        if email:
            self._add_identity(a, "email", norm_email(email), source, ns)
        if phone:
            self._add_identity(a, "phone", norm_phone(phone), source, ns)
        if name and not a.display_name:
            a.display_name = name
        if relation:
            a.relation = relation
        self._apply_policy(a)
        if is_owner:
            self.owner_id = a.id
            a.relation = "agent" if a.relation == "unknown" else a.relation
        return a

    def _add_identity(self, a: Actor, kind: str, value: str, source: str, ns: int) -> None:
        if not any(i.kind == kind and i.value == value for i in a.identities):
            a.identities.append(Identity(kind=kind, value=value, source=source, first_seen_ns=ns))
        self.by_identity[(kind, value)] = a.id

    def _apply_policy(self, a: Actor) -> None:
        """Tier is owner policy, never inferred: only tiers.yaml can set it."""
        for i in a.identities:
            row = self._policy.get(i.value)
            if row:
                a.tier = int(row.get("tier", self.default_tier))
                if row.get("relation"):
                    a.relation = row["relation"]
                a.confirmed_by = "owner"
            if i.value in self._never:
                a.never_auto_contact = True
        if a.tier == 0:
            a.tier = self.default_tier
        floors = self.tiers.get("tiers", {})
        a.silence_price_floor = float((floors.get(a.tier) or floors.get(str(a.tier)) or {}).get("silence_price_floor", 0.3))

    def tier_weight(self, actor_id: Optional[str]) -> float:
        """The multiplier on lateness in place_cost. Tier 1 = 2.0 … tier 4 = 0.5; unknown = 1.0."""
        a = self.by_id.get(actor_id or "")
        if a is None:
            return 1.0
        return {1: 2.0, 2: 1.4, 3: 1.0, 4: 0.5}.get(int(a.tier), 1.0)

    def seed_from_vcf(self, path: Path, ns: int = 0) -> int:
        n = 0
        cur: dict[str, str] = {}
        for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("BEGIN:VCARD"):
                cur = {}
            elif line.startswith("FN:"):
                cur["fn"] = line[3:].strip()
            elif line.upper().startswith("EMAIL"):
                cur.setdefault("email", line.split(":", 1)[-1].strip())
            elif line.upper().startswith("TEL"):
                cur.setdefault("tel", line.split(":", 1)[-1].strip())
            elif line.startswith("END:VCARD"):
                if cur.get("fn") or cur.get("email"):
                    self.upsert(cur.get("fn", ""), cur.get("email", ""), cur.get("tel", ""), source="contacts", ns=ns)
                    n += 1
        return n

    def rows(self) -> Iterable[Actor]:
        return self.by_id.values()


class Money:
    """Commercial objects from mail (inference) or a verdict connector (supersedes). No connector at M0."""

    def __init__(self, verdict_connected: bool = False):
        self.by_id: dict[str, MoneyObject] = {}
        self.verdict_connected = verdict_connected

    def upsert(self, mo: MoneyObject) -> MoneyObject:
        mo.payment_status_connected = self.verdict_connected
        cur = self.by_id.get(mo.id)
        if cur is None:
            self.by_id[mo.id] = mo
            return mo
        # the verdict connector supersedes any mail inference; mail never overrides a verdict
        if mo.status_source == "verdict_connector" or cur.status_source != "verdict_connector":
            for k, v in mo.model_dump().items():
                if v not in (None, [], "") and k != "id":
                    setattr(cur, k, v)
        return cur

    def apply_verdict(self, money_id: str, status: str, ns: int) -> None:
        """A payment or accounting feed says so. This is the only path to `paid` besides the owner."""
        mo = self.by_id.get(money_id)
        if mo is None:
            return
        mo.status = status  # type: ignore[assignment]
        mo.status_source = "verdict_connector"
        mo.confirmed_by = "verdict"
        mo.payment_status_connected = True

    def partition(self) -> dict[str, int]:
        """The found-money partition. Four figures. Never summed."""
        p = {"confirmed_receivable": 0, "apparent_overdue_not_connected": 0, "proposal_pipeline": 0, "vendor_credit": 0}
        for m in self.by_id.values():
            amt = m.amount_minor or 0
            if m.kind in ("quote", "proposal") and m.status in ("sent", "acknowledged", "unknown"):
                p["proposal_pipeline"] += amt
            elif m.kind == "invoice" and m.status in ("overdue", "sent", "unknown"):
                if m.status_source == "verdict_connector":
                    p["confirmed_receivable"] += amt
                else:
                    p["apparent_overdue_not_connected"] += amt
            elif m.kind == "credit":
                p["vendor_credit"] += amt
        return p
