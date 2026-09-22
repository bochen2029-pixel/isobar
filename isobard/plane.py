"""The plane at M0.5 — ingest → reflex → join → promote → registries → the hand → field → scan → replies →
glass, every step a row on the tape, every table a fold (`replay_verify` rebuilds the folds from the
tape and asserts byte-identity). A tick path advances the clock, admits what arrived meanwhile,
re-joins every unresolved capture, invalidates the dependency cone of anything that resolved, and
re-prices. Island mode holds every outbound effect with its reason and keeps everything else running.

Read-only against the world: nothing here has an effect except the reply channel, which is held on
the island. The owner directory holds brand-agnostic exports: mail.mbox (or eml/), calendar.ics,
todo.txt, contacts.vcf, money.csv (a verdict source), hand.mbox (forwards to the hand address),
hand/paste/*.txt, future.mbox (mail that arrives after `now`, for ticks), tiers.yaml, owner.json,
and — in the gym — stub_truth.json for the stub reflex.
"""
from __future__ import annotations

import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .contracts import (Capture, Cell, Commitment, CoverageGap, Effect, Finding, Grade, HandReply, MoneyObject,
                        Observation, blake128, canon)
from .dates import extract_invoice_id, extract_quote_id
from .deps import DepGraph
from .embed import Embedder
from .field import STOCKS, FieldBridge, Horizon
from .join import Joiner
from .promote import promote_cal, promote_list, promote_mail
from .reflex_client import LayaReflex, ReflexClient, StubReflex, injection_shape
from .registries import Money, People, parse_addr
from .scan import recovery_scan, xray_text
from .tape import Tape

ROOT = Path(__file__).resolve().parents[1]
DAY_NS = 86400 * 10**9
HOUR_NS = 3600 * 10**9
OPEN_STATES = ("active", "waiting", "candidate", "at_risk", "in_progress")
_TOK = re.compile(r"[a-z0-9]{3,}")
_STOP = {"the", "and", "for", "you", "your", "with", "this", "that", "from", "have", "has", "are", "was", "will", "can", "could",
         "please", "thanks", "hi", "let", "know", "get", "about", "next", "week", "said", "maybe", "need", "want", "wants", "re",
         "fwd", "fw", "our", "out", "not", "but", "all", "any", "some", "when", "what", "who", "how", "just", "also", "its", "it's"}
_IDS = re.compile(r"\b(?:INV|Q|PO|SO|REF|CASE)-?\d{3,7}\b", re.I)


def _jsonable(o: Any) -> Any:
    if isinstance(o, tuple):
        return list(o)
    if isinstance(o, dict):
        return {k: _jsonable(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_jsonable(v) for v in o]
    return o


def content_tokens(text: str) -> set[str]:
    return {t for t in _TOK.findall(text.lower()) if t not in _STOP and not t.isdigit()}


def ids_in(text: str) -> set[str]:
    out = set()
    for m in _IDS.findall(text):
        k = m.upper().replace("-", "")
        out.add(k[:3] + "-" + k[3:] if k.startswith("INV") else (k[:1] + "-" + k[1:] if k.startswith("Q") else k))
    return out


def body_head_digest(text: str) -> str:
    return blake128(re.sub(r"\s+", " ", (text or "")[:400]).strip().lower().encode())


class Plane:
    def __init__(self, owner_dir: Path, store: Optional[Path] = None, reflex: str = "stub", competence: float = 0.9, seed: int = 7,
                 verdict: bool = True, now_ns: Optional[int] = None, bench: bool = True, horizon_days: int = 14,
                 embed_endpoint: Optional[str] = None, since_days: int = 90, island: Optional[bool] = None):
        from connectors.direct import HandMailbox, IcsConnector, MboxConnector, MoneyCsvVerdict, PasteFolder, TextListConnector, VcfContacts
        self._C = dict(mbox=MboxConnector, ics=IcsConnector, text=TextListConnector, vcf=VcfContacts, money=MoneyCsvVerdict,
                       hand=HandMailbox, paste=PasteFolder)
        self.owner_dir = Path(owner_dir)
        self.store = Path(store) if store else self.owner_dir / "store"
        self.store.mkdir(parents=True, exist_ok=True)
        owner = json.loads((self.owner_dir / "owner.json").read_text(encoding="utf-8")) if (self.owner_dir / "owner.json").exists() else {}
        self.owner_email = owner.get("email", "")
        self.owner_name = owner.get("name", "owner")
        self.hand_address = owner.get("hand_address", "")
        self.hand_backend = owner.get("hand_backend", "mbox")
        self.hand_imap = owner.get("hand_imap", {})
        self.reply_smtp = owner.get("reply_smtp", {})       # {host, port, user, pass_env}; absent ⇒ replies are files
        if now_ns is not None:
            self.now_ns = now_ns
        elif "now" in owner:
            self.now_ns = int(datetime.fromisoformat(owner["now"]).timestamp() * 1e9)
        else:
            self.now_ns = time.time_ns()
        self.since_ns = self.now_ns - since_days * DAY_NS
        self.bench = bench
        self.verdict = verdict and (self.owner_dir / "money.csv").exists()
        # the island: forced by the flag, by the software cut, or raised by a network fault during the run
        forced = os.environ.get("ISOBAR_NETWORK", "").lower()
        self.island = bool(island) if island is not None else (forced == "absent")
        self.tape = Tape(self.store, writer="plane")
        self.clock = self.now_ns
        tiers = self.owner_dir / "tiers.yaml"
        self.people = People(tiers if tiers.exists() else ROOT / "tiers.yaml")
        self.money = Money(verdict_connected=self.verdict)
        self.stub_truth_by_obs: dict[str, dict] = {}
        st = self.owner_dir / "stub_truth.json"
        self.stub_truth_by_mid: dict[str, dict] = json.loads(st.read_text(encoding="utf-8")) if st.exists() else {}
        self.provider = StubReflex(competence, seed, truth=self.stub_truth_by_obs) if reflex == "stub" else LayaReflex()
        self.reflex = ReflexClient(self.provider)
        self.embedder = Embedder(endpoint=embed_endpoint) if embed_endpoint else Embedder()
        self.joiner = Joiner(self.embedder, self.provider)
        self.hz = Horizon(self.now_ns, horizon_days=horizon_days)
        self.bridge = FieldBridge(self.store / "field", self.embedder, self.hz, seed=seed)
        self.deps = DepGraph()
        self.commitments: dict[str, Commitment] = {}
        self.notes: dict[str, dict] = {}
        self.texts: dict[str, str] = {}
        self.src_of: dict[str, int] = {}
        self.root_of: dict[str, str] = {}
        self.last_owner: dict[str, int] = {}
        self.last_counter: dict[str, int] = {}
        self.allocations: list[tuple[int, int]] = []
        self.booked_min: float = 0.0
        # indexes for the three grade cases (SPEC r0.2 §5.4)
        self.obs_by_mid: dict[str, str] = {}
        self.obs_by_forward_key: dict[tuple[str, str], str] = {}
        self.obs_by_digest: dict[str, str] = {}
        self.cell_by_obs: dict[str, Cell] = {}
        self.row_by_obs: dict[str, str] = {}
        self.dismissed_obs: set[str] = set()
        self.obs_text: dict[str, str] = {}
        self.obs_ids: dict[str, set[str]] = {}
        # the hand
        self.captures: dict[str, Capture] = {}
        self.capture_text: dict[str, str] = {}
        self.capture_actor: dict[str, Optional[str]] = {}
        self.replies: dict[str, HandReply] = {}
        self.coverage: list[CoverageGap] = []
        self.held_effects: list[Effect] = []
        self.last_field: Optional[dict] = None
        self.tick_count = 0
        self.stats: dict[str, Any] = {"mail": 0, "cal": 0, "list": 0, "contacts": 0, "hand": 0, "cells": 0, "joins_exact": 0, "joins_lexical": 0,
                                      "joins_embed": 0, "joins_none": 0, "promoted": 0, "discharged": 0, "modified": 0, "not_commitment": 0,
                                      "injection_flagged": 0, "verdicts": 0, "reflex_us": 0, "captures_linked": 0, "captures_duplicate": 0,
                                      "captures_unresolved": 0, "captures_refused": 0, "captures_resolved": 0, "grades_declared": 0,
                                      "coverage_gaps": 0, "notes": 0, "corrections": 0, "policy_candidates": 0, "replies": 0, "replies_held": 0,
                                      "ticks": 0, "island_refusals": 0}
        self.owner = self.people.upsert(self.owner_name, self.owner_email, source="owner", ns=self.now_ns, is_owner=True)
        self.owner.confirmed_by = "owner"
        self.state_version = 0
        if self.island:
            self._row("island", "on", {"on": True, "reason": "flag" if island else "ISOBAR_NETWORK=absent", "ns": self.now_ns})

    # ---- the tape ----
    def _row(self, kind: str, ref: str, body: Any):
        self.clock += 1
        return self.tape.append(kind, ref, _jsonable(body), ts=self.clock)

    def _promotion(self, rule: str, c: Commitment, note: Optional[dict] = None, target: Optional[str] = None, p: float = 0.0) -> None:
        self.state_version += 1
        c.state_version = self.state_version
        self._row("promotion", c.id, {"rule": rule, "target": target, "p": p, "after": c.model_dump(), "note": note or {}})

    def _island_refusal(self, lane: str, code: str, detail: Optional[dict] = None) -> None:
        self.stats["island_refusals"] += 1
        self._row("island", lane, {"code": code, "lane": lane, "ns": self.now_ns, **(detail or {})})

    # ---- registries ----
    def ingest_contacts(self) -> None:
        p = self.owner_dir / "contacts.vcf"
        if not p.exists():
            return
        for card in self._C["vcf"](p).cards():
            self.people.upsert(card.get("fn", ""), card.get("email", ""), card.get("tel", ""), source="contacts", ns=self.now_ns)
            self.stats["contacts"] += 1

    def apply_money_verdict(self) -> None:
        p = self.owner_dir / "money.csv"
        if not self.verdict or not p.exists():
            return
        for r in self._C["money"](p).rows():
            actor = self.people.upsert("", r["counterparty_email"], source="money", ns=self.now_ns)
            mo = self.money.by_id.get(r["id"])
            if mo is None:
                mo = self.money.upsert(MoneyObject(id=r["id"], kind=r["kind"], counterparty=actor.id, amount_minor=r["amount_minor"], currency=r["currency"],
                                                   issued_ns=r["issued_ns"], due_ns=r["due_ns"], status=r["status"], status_source="verdict_connector",
                                                   confirmed_by="verdict", provenance=["money.csv"]))
            else:
                mo.amount_minor = mo.amount_minor or r["amount_minor"]
                mo.due_ns = r["due_ns"] or mo.due_ns
                mo.issued_ns = r["issued_ns"] or mo.issued_ns
            self.money.apply_verdict(mo.id, r["status"], self.now_ns)
            self.stats["verdicts"] += 1
            self._row("registry", mo.id, {"kind": "money", "verdict": r["status"], **mo.model_dump()})
            if r["status"] == "paid" and mo.commitment_id and mo.commitment_id in self.commitments:
                c = self.commitments[mo.commitment_id]
                if c.state in OPEN_STATES:
                    c.state = "discharged"
                    self.stats["discharged"] += 1
                    self._promotion("verdict_paid", c, {"source": "money.csv"}, target=c.id, p=1.0)

    # ---- the passive lanes ----
    def _thread_root(self, mid: str, irt: str) -> str:
        root = self.root_of.get(irt) if irt else None
        if root is None:
            root = irt if irt else mid
        self.root_of[mid] = root
        return root

    def _index_passive(self, obs: Observation, parsed: dict, root: str) -> None:
        h = parsed["headers"]
        self.obs_by_mid[obs.external_id] = obs.id
        self.obs_by_forward_key[(parsed.get("from_email", ""), _norm_subject(h.get("Subject", "")))] = obs.id
        self.obs_by_digest[body_head_digest(parsed.get("body", ""))] = obs.id
        self.obs_text[obs.id] = f"{h.get('Subject', '')}\n{parsed.get('body', '')}"
        self.obs_ids[obs.id] = ids_in(h.get("Subject", "") + " " + parsed.get("body", ""))

    def _register_row(self, row: Commitment, obs_id: str, subject: str, money_id: Optional[str], src: int, note: dict) -> None:
        self.commitments[row.id] = row
        self.notes[row.id] = note
        self.texts[row.id] = row.deliverable_text
        self.src_of[row.id] = src
        self.row_by_obs[obs_id] = row.id
        self.deps.add(row.id, row.depends_on or [obs_id])
        self.joiner.index(row, subject=subject, money_id=money_id, text=row.deliverable_text)

    def ingest_mail(self, path: Optional[Path] = None, until_ns: Optional[int] = None, source_name: str = "mbox") -> int:
        src = path or (self.owner_dir / "mail.mbox" if (self.owner_dir / "mail.mbox").exists() else self.owner_dir / "eml")
        if not src.exists():
            return 0
        conn = self._C["mbox"](src, owner_email=self.owner_email, source_name=source_name, ingest_ns=self.now_ns)
        items = sorted(conn.backfill(self.since_ns), key=lambda t: (t[0].occurred_ns, t[0].external_id))
        n = 0
        for obs, parsed in items:
            if until_ns is not None and obs.occurred_ns > until_ns:
                continue
            if obs.external_id in self.obs_by_mid:
                continue
            self._admit_mail(obs, parsed)
            n += 1
        return n

    def _admit_mail(self, obs: Observation, parsed: dict) -> None:
        h = parsed["headers"]
        body, subject = parsed["body"], h.get("Subject", "")
        text = f"Subject: {subject}\n\n{body}"
        if injection_shape(text):
            obs.injection_shape = True
        obs.envelope_trust = obs.intake_trust
        obs.with_id()
        self._row("observation", obs.id, obs.model_dump())
        self.stats["mail"] += 1
        mid = obs.external_id
        root = self._thread_root(mid, (h.get("In-Reply-To") or "").strip())
        self._index_passive(obs, parsed, root)
        occ = obs.occurred_ns
        name, email = parse_addr(h.get("From", ""))
        sender = self.people.upsert(name, email, source="mail", ns=occ)
        recips = []
        for raw in (h.get("To", "") + "," + h.get("Cc", "")).split(","):
            n2, e2 = parse_addr(raw)
            if e2:
                recips.append(self.people.upsert(n2, e2, source="mail", ns=occ).id)
        outbound = bool(parsed.get("outbound"))
        if outbound:
            self.last_owner[root] = max(self.last_owner.get(root, 0), occ)
        else:
            self.last_counter[root] = max(self.last_counter.get(root, 0), occ)
        if mid in self.stub_truth_by_mid:
            self.stub_truth_by_obs[obs.id] = self.stub_truth_by_mid[mid]
        cell = self.reflex.compile(obs.id, text)
        self.cell_by_obs[obs.id] = cell
        self.deps.add(cell.id, [obs.id])
        self.stats["cells"] += 1
        self.stats["reflex_us"] += cell.latency_us
        self._row("cell", cell.id, cell.model_dump())
        if cell.fields.get("injection_shape") and cell.fields["injection_shape"].value:
            self.stats["injection_flagged"] += 1
        self._join_and_promote(obs, cell, parsed, sender.id, recips, occ, root, subject, body, outbound, src=0)

    def _join_and_promote(self, obs: Observation, cell: Cell, parsed: dict, sender_id: str, recips: list[str], occ: int, root: str,
                          subject: str, body: str, outbound: bool, src: int) -> tuple[Optional[str], str, dict]:
        """Returns (row id or None, the promotion rule, the note). Keyed-only state changes (L4, §6.4)."""
        open_ids = [i for i, c in self.commitments.items() if c.state in OPEN_STATES]
        money_id = extract_invoice_id(subject + " " + body) or extract_quote_id(subject + " " + body)
        keys = [k for k in dict.fromkeys([root, (parsed.get("headers", {}).get("In-Reply-To") or "").strip(), obs.external_id]) if k]
        join = self.joiner.join(obs.id, keys, subject, money_id, (subject + "\n" + body[:400]).strip(), open_ids)
        join.depends_on = [obs.id]
        self.stats[{"exact": "joins_exact", "lexical": "joins_lexical", "embed_rerank_reflex": "joins_embed", "none": "joins_none"}[join.method]] += 1
        self._row("join", obs.id, join.model_dump())
        row, mo, note = promote_mail(cell, join, {**parsed, "body": body, "headers": {**parsed.get("headers", {}), "Subject": subject}, "outbound": outbound},
                                     self.owner.id, sender_id, recips, occ, obs.id, root)
        note["outbound"] = outbound
        if mo is not None:
            mo = self.money.upsert(mo)
        keyed = join.method in ("exact", "lexical")
        if note.get("rule") == "discharge" and not keyed:
            self._row("promotion", obs.id, {"rule": "discharge_candidate", "target": note.get("target"), "p": float(note.get("p", 0.0)), "after": None, "note": note})
            return None, "discharge_candidate", note
        if note.get("rule") == "discharge":
            t = note.get("target")
            if t in self.commitments and self.commitments[t].state in OPEN_STATES:
                c = self.commitments[t]
                c.state = "discharged"
                c.evidence.append(obs.id)
                self.stats["discharged"] += 1
                if c.money_object and c.money_object in self.money.by_id and self.money.by_id[c.money_object].status_source != "verdict_connector":
                    self.money.by_id[c.money_object].status = "acknowledged"
                self._promotion("discharge", c, note, target=t, p=float(note.get("p", 0.0)))
                self.row_by_obs[obs.id] = t
                return t, "discharge", note
            return None, "discharge_stale", note
        if row is None:
            self.stats["not_commitment"] += 1
            self.dismissed_obs.add(obs.id)
            self._row("promotion", obs.id, {"rule": note.get("rule", "not_commitment"), "target": None, "p": 0.0, "after": None, "note": note})
            return None, note.get("rule", "not_commitment"), note
        if mo is not None:
            row.money_object = mo.id
            mo.commitment_id = row.id
        target = note.get("target") if (note.get("rule") == "modifies" and keyed) else None
        if not keyed and join.candidates:
            note["join_candidates"] = [(c.id, c.p) for c in join.candidates]
        if target and target in self.commitments and self.commitments[target].state in OPEN_STATES:
            c = self.commitments[target]
            if row.due.latest_ns:
                c.due = row.due
            c.evidence.append(obs.id)
            c.depends_on = list(dict.fromkeys(c.depends_on + [obs.id, cell.id]))
            self.deps.add(c.id, [obs.id, cell.id])
            if mo is not None and not c.money_object:
                c.money_object = mo.id
                mo.commitment_id = c.id
            self.stats["modified"] += 1
            self._promotion("modifies", c, note, target=target, p=float(note.get("p", 0.0)))
            self.row_by_obs[obs.id] = target
            return target, "modifies", note
        if row.id in self.commitments:
            c = self.commitments[row.id]
            c.evidence.append(obs.id)
            self._promotion("reinforces", c, note, target=row.id, p=row.p_promoted)
            self.row_by_obs[obs.id] = row.id
            return row.id, "reinforces", note
        row.depends_on = [obs.id, cell.id]
        self._register_row(row, obs.id, subject, mo.id if mo else None, src, note)
        self.stats["promoted"] += 1
        self._promotion("creates", row, note, p=row.p_promoted)
        return row.id, "creates", note

    def ingest_list(self) -> None:
        p = self.owner_dir / "todo.txt"
        if not p.exists():
            return
        for obs, parsed in self._C["text"](p, ingest_ns=self.now_ns).backfill():
            # a typed line in the list file IS the hand's list_line rendering: owner-invoked, declared, operator envelope
            obs.rendering = "list_line"; obs.declared = True; obs.envelope_trust = "operator"
            obs.with_id()
            self._row("observation", obs.id, obs.model_dump())
            self.stats["list"] += 1
            c = promote_list(parsed, self.owner.id, obs.id, obs.occurred_ns)
            who = self.people.mention(parsed["text"])
            if who:
                c.creditor_actor = who
            c.depends_on = [obs.id]
            self._register_row(c, obs.id, "", None, 1, {"rule": "list", "outbound": True, "direction": "we_owe", "mention": who})
            self._promotion("list", c, self.notes[c.id], p=1.0)

    def ingest_cal(self) -> None:
        p = self.owner_dir / "calendar.ics"
        if not p.exists():
            return
        for obs, parsed in self._C["ics"](p, horizon_days=self.hz.days, ingest_ns=self.now_ns).backfill(self.since_ns):
            obs.envelope_trust = obs.intake_trust
            obs.with_id()
            self._row("observation", obs.id, obs.model_dump())
            self.stats["cal"] += 1
            c = promote_cal(parsed, self.owner.id, obs.id)
            att = [self.people.upsert("", a, source="cal", ns=parsed["start_ns"]).id for a in parsed.get("attendees", [])]
            if att:
                c.creditor_actor = att[0]
            c.depends_on = [obs.id]
            self.commitments[c.id] = c
            self.notes[c.id] = {"rule": "cal", "outbound": True}
            self.src_of[c.id] = 2
            self.deps.add(c.id, [obs.id])
            self._promotion("cal", c, self.notes[c.id], p=c.p_promoted)
            hz_start = int(self.hz.start.timestamp() * 1e9)
            if parsed["end_ns"] > hz_start and not parsed["all_day"]:
                s0, s1 = self.hz.slot_of(parsed["start_ns"]), self.hz.slot_of(parsed["end_ns"])
                if s1 > s0:
                    self.allocations.append((s0, s1))
                    self.booked_min += (parsed["end_ns"] - parsed["start_ns"]) / 60e9

    # ---- the hand lane (SPEC r0.2 §5) ----
    def _hand_sources(self) -> list:
        srcs = []
        if self.hand_address:
            if self.hand_backend == "imap":
                srcs.append(self._C["hand"](address=self.hand_address, owner_email=self.owner_email, backend="imap",
                                            imap_host=self.hand_imap.get("host", ""), imap_user=self.hand_imap.get("user", ""),
                                            imap_pass_env=self.hand_imap.get("pass_env", "ISOBAR_HAND_IMAP_PASS"), ingest_ns=self.now_ns))
            hm = self.owner_dir / "hand.mbox"
            if hm.exists() or (self.owner_dir / "hand_eml").exists():
                srcs.append(self._C["hand"](address=self.hand_address, owner_email=self.owner_email, backend="mbox",
                                            path=hm if hm.exists() else self.owner_dir / "hand_eml", ingest_ns=self.now_ns))
        pf = self.owner_dir / "hand" / "paste"
        if pf.exists():
            srcs.append(self._C["paste"](pf, ingest_ns=self.now_ns))
        return srcs

    def ingest_hand(self, until_ns: Optional[int] = None) -> int:
        n = 0
        for conn in self._hand_sources():
            if getattr(conn, "backend", "") == "imap" and self.island:
                self._island_refusal("hand_imap", "NETWORK_ABSENT", {"host": self.hand_imap.get("host", "")})
                continue
            for obs, parsed in sorted(conn.backfill(self.since_ns), key=lambda t: (t[0].occurred_ns, t[0].external_id)):
                if until_ns is not None and obs.occurred_ns > until_ns:
                    continue
                if obs.id in self.captures:
                    continue
                self._admit_capture(obs, parsed)
                n += 1
            for r in getattr(conn, "refusals", []):
                if r.get("code") == "NETWORK_ABSENT":
                    self._island_refusal("hand_imap", "NETWORK_ABSENT", r)
                else:
                    self._row("coalesce", "hand", {"lane": "hand", "dropped_count": 1, "reason": r.get("code", "refused"), **{k: v for k, v in r.items() if k != "code"}})
        return n

    def _admit_capture(self, obs: Observation, parsed: dict) -> None:
        # 1 · SEAL — the receipt the owner sees before the box has understood anything
        self.stats["hand"] += 1
        row = self._row("observation", obs.id, obs.model_dump())
        cap = Capture(id=obs.id, rendering=obs.rendering or "paste", state="SEALED", sealed_ns=self.now_ns, receipt=row.hash[:8])
        self.captures[obs.id] = cap
        self._row("capture", obs.id, cap.model_dump())
        if obs.external_id in self.stub_truth_by_mid:
            self.stub_truth_by_obs[obs.id] = self.stub_truth_by_mid[obs.external_id]
        if obs.external_id + ":note" in self.stub_truth_by_mid:
            self.stub_truth_by_obs[obs.id + ":note"] = self.stub_truth_by_mid[obs.external_id + ":note"]
        # 2 · REFUSED — typed, the payload stays sealed
        if parsed.get("too_large"):
            return self._refuse(cap, "PAYLOAD_TOO_LARGE")
        if parsed.get("empty"):
            return self._refuse(cap, "EMPTY")
        # 3 · PARSED
        fwd = parsed.get("forward")
        if fwd is not None and fwd.is_forward:
            payload_text = f"Subject: {fwd.original_subject}\n\n{fwd.quoted_body}"
            cap.keys = {"forward_key": fwd.forward_key, "quoted_digest": fwd.quoted_digest, **({"original_mid": fwd.original_mid} if fwd.original_mid else {})}
        else:
            payload_text = parsed.get("text") or (fwd.note if fwd is not None else "")
        found_ids = ids_in(payload_text)
        if found_ids:
            cap.keys["ids"] = ",".join(sorted(found_ids))
        self.capture_text[obs.id] = payload_text
        cap.state = "PARSED"
        self._row("capture", obs.id, cap.model_dump())
        # 4 · the NOTE is testimony: its own question set, never evidence content
        if obs.note:
            ncell = self.reflex.compile_note(obs.id, obs.note)
            self.stats["notes"] += 1
            self._row("cell", ncell.id, ncell.model_dump())
            kinds = [(k, f.p) for k, f in ncell.fields.items() if f.value]
            cap.note_kind = "none"
            if kinds:
                best = max(kinds, key=lambda t: t[1])[0]
                cap.note_kind = {"is_correction": "correction", "is_policy_hint": "policy_hint", "is_hypothesis": "hypothesis",
                                 "is_question": "question", "is_look_instruction": "look_instruction"}[best]
            if cap.note_kind == "correction":
                self.stats["corrections"] += 1
                self._row("correction", obs.id, {"kind": "owner_note", "text": obs.note, "target": None, "capture": obs.id})
            elif cap.note_kind == "policy_hint":
                self.stats["policy_candidates"] += 1
                self._row("policy", obs.id, {"candidate": True, "applied": False, "text": obs.note, "capture": obs.id})   # never applied (L24)
        # 5 · CODE + REFLEX over the payload, at the payload's own trust
        cell = self.reflex.compile(obs.id, payload_text)
        cell.depends_on = [obs.id]
        self.cell_by_obs[obs.id] = cell
        self.deps.add(cell.id, [obs.id])
        self.stats["cells"] += 1
        self.stats["reflex_us"] += cell.latency_us
        self._row("cell", cell.id, cell.model_dump())
        if injection_shape(payload_text) or (cell.fields.get("injection_shape") and cell.fields["injection_shape"].value):
            self.stats["injection_flagged"] += 1
        # 6 · the three grade cases (forwards only): every hand event is a grade
        seen_obs: Optional[str] = None
        if fwd is not None and fwd.is_forward:
            seen_obs = (self.obs_by_mid.get(fwd.original_mid or "") or self.obs_by_forward_key.get((fwd.original_from_email, fwd.original_subject))
                        or self.obs_by_digest.get(fwd.quoted_digest))
            if seen_obs and seen_obs in self.row_by_obs and self.commitments[self.row_by_obs[seen_obs]].state in OPEN_STATES:
                cap.grade_case = "seen_in_state"
                rid = self.row_by_obs[seen_obs]
                self._grade("commitment", rid, "seen_in_state")
                cap.state = "DUPLICATE"; cap.duplicate_of = seen_obs; cap.linked_to = rid; cap.join_method = "exact"
                self.stats["captures_duplicate"] += 1
                self._row("capture", obs.id, cap.model_dump())
                return self._reply(cap, duplicate_of=seen_obs[:8], linked=self._row_label(rid))
            if seen_obs:
                cap.grade_case = "seen_dismissed"
                self._grade("cell", self.cell_by_obs[seen_obs].id if seen_obs in self.cell_by_obs else seen_obs, "seen_dismissed")
            else:
                cap.grade_case = "unseen"
                dom = fwd.original_from_email.split("@")[-1] if fwd.original_from_email else "unknown"
                gap = CoverageGap(capture_id=obs.id, channel=f"domain:{dom}", sender=fwd.original_from_email or None, ns=self.now_ns)
                self.coverage.append(gap)
                self.stats["coverage_gaps"] += 1
                self._row("coverage", obs.id, gap.model_dump())
        # 7 · JOIN + PROMOTE: keyed only; the hand's entity+lexical rule for pastes; else the capture is carried UNRESOLVED
        actor_id: Optional[str] = None
        if fwd is not None and fwd.is_forward:
            oname, oemail = parse_addr(fwd.quoted_headers.get("from", ""))
            sender = self.people.upsert(oname, oemail, source="hand", ns=obs.occurred_ns) if oemail else self.owner
            outbound = (oemail.lower() == self.owner_email.lower()) if oemail else False
            recips = [self.owner.id]
            root = fwd.original_mid or obs.id
            rid, rule, note = self._join_and_promote(obs, cell, {"headers": {"From": fwd.quoted_headers.get("from", ""), "Subject": fwd.original_subject, "In-Reply-To": ""},
                                                                  "body": fwd.quoted_body, "from_email": oemail}, sender.id, recips, obs.occurred_ns, root,
                                                     fwd.original_subject, fwd.quoted_body, outbound, src=3)
            actor_id = sender.id if not outbound else None
        else:
            actor_id = self.people.mention(payload_text)
            rid, rule = self._link_paste(obs, cell, payload_text, actor_id, found_ids)
        self.capture_actor[obs.id] = actor_id
        if rid is not None:
            cap.state = "LINKED"; cap.linked_to = rid; cap.join_method = rule
            self.stats["captures_linked"] += 1
            self.deps.add(rid, [obs.id])
            self._row("capture", obs.id, cap.model_dump())
            return self._reply(cap, linked=self._row_label(rid))
        # UNRESOLVED: a row in the fourth stock, priced by its age; re-joined every tick
        urow = Commitment(id="c_cap_" + obs.id[:12], debtor_actor=self.owner.id, creditor_actor=actor_id or self.owner.id, kind="other",
                          deliverable_text=("[capture] " + payload_text.strip().replace("\n", " "))[:160], release_ns=obs.occurred_ns,
                          state="unresolved", evidence=[obs.id], p_promoted=1.0, depends_on=[obs.id, cell.id], capture_id=obs.id)
        urow.effort.opt_min, urow.effort.nom_min, urow.effort.cons_min = 5, 15, 30
        self._register_row(urow, obs.id, "", None, 3, {"rule": "unresolved_capture", "outbound": True, "capture": obs.id})
        self._promotion("unresolved_capture", urow, self.notes[urow.id], p=1.0)
        cap.state = "UNRESOLVED"; cap.unresolved_row = urow.id
        self.stats["captures_unresolved"] += 1
        self._row("capture", obs.id, cap.model_dump())
        return self._reply(cap, unresolved=True)

    def _link_paste(self, obs: Observation, cell: Cell, text: str, actor_id: Optional[str], found_ids: set[str]) -> tuple[Optional[str], str]:
        """A paste joins by KEY only: an exact id shared with an open row, or the same named actor plus shared content
        tokens, or ≥3 shared tokens with a rare one. Else it becomes a new row if the reflex read a promise, else UNRESOLVED."""
        rid = self._keyed_match(text, actor_id, found_ids)
        if rid:
            return rid, "lexical" if not (found_ids and any(i in (self.obs_ids_of_row(rid)) for i in found_ids)) else "exact"
        is_c = cell.fields.get("is_commitment_bearing")
        direction = cell.fields.get("direction")
        if is_c and is_c.value and direction and direction.value != "none":
            join_stub = type("J", (), {"candidates": [], "method": "none"})()
            from .contracts import Join
            j = Join(observation_id=obs.id, method="none", depends_on=[obs.id])
            row, mo, note = promote_mail(cell, j, {"headers": {"Subject": ""}, "body": text, "outbound": True}, self.owner.id, self.owner.id,
                                         [actor_id] if actor_id else [self.owner.id], obs.occurred_ns, obs.id, obs.id)
            if row is not None:
                if mo is not None:
                    mo = self.money.upsert(mo); row.money_object = mo.id; mo.commitment_id = row.id
                row.depends_on = [obs.id, cell.id]
                note["outbound"] = True
                self._register_row(row, obs.id, "", mo.id if mo else None, 3, note)
                self.stats["promoted"] += 1
                self._promotion("creates", row, note, p=row.p_promoted)
                return row.id, "creates"
        return None, "none"

    def obs_ids_of_row(self, rid: str) -> set[str]:
        out: set[str] = set()
        c = self.commitments.get(rid)
        if c and c.money_object:
            out.add(c.money_object)
        for e in (c.evidence if c else []):
            out |= self.obs_ids.get(e, set())
        return out

    def _keyed_match(self, text: str, actor_id: Optional[str], found_ids: set[str]) -> Optional[str]:
        open_rows = [c for c in self.commitments.values() if c.state in OPEN_STATES and c.kind != "appointment"]
        if found_ids:
            for c in open_rows:
                if found_ids & self.obs_ids_of_row(c.id):
                    return c.id
        toks = content_tokens(text)
        if not toks:
            return None
        df: dict[str, int] = {}
        row_toks: dict[str, set[str]] = {}
        for c in open_rows:
            rt = content_tokens(self.texts.get(c.id, c.deliverable_text) + " " + " ".join(self.obs_text.get(e, "") for e in c.evidence[:3]))
            row_toks[c.id] = rt
            for t in rt:
                df[t] = df.get(t, 0) + 1
        best: Optional[tuple[int, str]] = None
        for c in open_rows:
            shared = toks & row_toks[c.id]
            counter = c.creditor_actor if c.debtor_actor == self.owner.id else c.debtor_actor
            same_actor = actor_id is not None and counter == actor_id
            rare = any(df.get(t, 0) <= 2 for t in shared)
            ok = (same_actor and len(shared) >= 2) or (len(shared) >= 3 and rare)
            if ok and (best is None or len(shared) > best[0]):
                best = (len(shared), c.id)
        return best[1] if best else None

    def _row_label(self, rid: str) -> str:
        c = self.commitments.get(rid)
        return f"#{rid[-6:]} \"{(c.deliverable_text if c else '')[:48]}\" p={c.p_promoted:.2f}" if c else f"#{rid[-6:]}"

    def _grade(self, subject: str, subject_id: str, case: str) -> None:
        g = Grade(subject=subject, subject_id=subject_id, kind="declared", stratum="declared", salted=False, ns=self.now_ns, case=case)
        self.stats["grades_declared"] += 1
        self._row("grade", subject_id, g.model_dump())

    def _refuse(self, cap: Capture, reason: str) -> None:
        cap.state = "REFUSED"; cap.refusal = reason
        self.stats["captures_refused"] += 1
        self._row("capture", cap.id, cap.model_dump())
        self._reply(cap, refused=reason)

    def _reply(self, cap: Capture, **kw: Any) -> None:
        r = HandReply(capture_id=cap.id, sealed=cap.receipt, **kw)
        self.replies[cap.id] = r

    def finish_replies(self, field_json: Optional[dict]) -> None:
        """The reply carries what the capture moved: composed after the field ran. Held on the island if it must travel."""
        moved = None
        if field_json:
            line = self.bridge.field_delta_line(field_json, self.open_rows())
            moved = line.replace("[field] ", "")
        outdir = self.store / "hand" / "replies"
        outdir.mkdir(parents=True, exist_ok=True)
        # a reply must travel when the hand address is a remote mailbox; the SMTP leg is unbuilt at M0.5 (the file and the
        # receipt are the channel), so off the island a remote reply is written as a file and says so
        remote = bool(self.reply_smtp.get("host")) or self.hand_backend == "imap"
        for cid, r in self.replies.items():
            if r.moved is None:
                r.moved = moved
            if remote and self.island:
                r.held = "NETWORK_ABSENT"
                eff = Effect(id="reply_" + cid[:12], intent_id=cid, target="hand.reply", payload={"to": self.owner_email, "text": r.render()},
                             inverse={"noop": "a reply is idempotent by capture id"}, precondition={"state_version": self.state_version},
                             idempotency_key="reply:" + cid, state="held", held_reason="NETWORK_ABSENT")
                self.held_effects.append(eff)
                self._row("effect", eff.id, eff.model_dump())
                self._island_refusal("reply_channel", "NETWORK_ABSENT", {"capture": cid})
                self.stats["replies_held"] += 1
            (outdir / f"{r.sealed}.txt").write_text(r.render() + "\n", encoding="utf-8")
            self._row("receipt", cid, {"kind": "hand_reply", "capture": cid, "delivery": ("held" if r.held else ("file; smtp leg unbuilt at M0.5" if remote else "file")),
                                       **r.model_dump()})
            self.stats["replies"] += 1

    # ---- the tick path (SPEC r0.2 §6.1, §10.5) ----
    def tick(self, hours: float, future_mail: Optional[Path] = None) -> dict:
        """Advance the clock; admit what arrived meanwhile; re-join every unresolved capture; invalidate the cone of
        anything that resolved; re-price. Re-foresee is skipped with its reason until M1's instrument exists."""
        self.tick_count += 1
        self.stats["ticks"] += 1
        prev_now = self.now_ns
        self.now_ns = int(prev_now + hours * HOUR_NS)
        self.clock = max(self.clock, self.now_ns)
        self._row("tick", f"t{self.tick_count}", {"gap_s": int(hours * 3600), "from_ns": prev_now, "to_ns": self.now_ns})
        self.hz = Horizon(self.now_ns, horizon_days=self.hz.days)
        self.bridge.rehorizon(self.hz)
        arrived = 0
        fm = future_mail or (self.owner_dir / "future.mbox")
        if fm.exists():
            arrived = self.ingest_mail(fm, until_ns=self.now_ns, source_name="mbox_future")
        arrived_hand = self.ingest_hand(until_ns=self.now_ns)
        if self.island:
            self._island_refusal("frontier", "FRONTIER_ABSENT", {"tick": self.tick_count})
        resolved = self._rejoin_unresolved()
        dirty: set[str] = set()
        for cid in resolved:
            dirty |= set(self.deps.cone(cid))
        d, rows, meta = self.run_field()
        dv = float(d.get("delta_v_norm", -1))
        recontext = {"resolved": resolved, "cone_size": len(dirty), "reprice": True, "delta_v_norm": dv,
                     "reforesee": "skipped: no multiverse instrument until M1", "arrived_mail": arrived, "arrived_hand": arrived_hand}
        self._row("resolution", f"t{self.tick_count}", {"kind": "recontext", **recontext}) if resolved else None
        self._row("run", f"tick{self.tick_count}", {"kind": "tick", "now_ns": self.now_ns, "hours": hours, **recontext,
                                                    "stock_prices": d.get("stock_prices"), "island": self.island})
        return {"tick": self.tick_count, "now_ns": self.now_ns, "arrived": arrived, "arrived_hand": arrived_hand, "resolved": resolved,
                "delta_v_norm": dv, "stock_prices": d.get("stock_prices"), "field": d}

    def _rejoin_unresolved(self) -> list[str]:
        """Exact ids first, then the entity+lexical key, against every open row (including rows created since the capture)."""
        out = []
        for cap in list(self.captures.values()):
            if cap.state != "UNRESOLVED":
                continue
            text = self.capture_text.get(cap.id, "")
            found = ids_in(text)
            rid = self._keyed_match(text, self.capture_actor.get(cap.id), found)
            if rid is None or rid == cap.unresolved_row:
                continue
            method = "exact" if (found and found & self.obs_ids_of_row(rid)) else "lexical"
            cap.state = "RESOLVED"; cap.linked_to = rid; cap.resolved_ns = self.now_ns; cap.join_method = method
            self.stats["captures_resolved"] += 1
            self.stats["captures_unresolved"] -= 1
            self._row("capture", cap.id, cap.model_dump())
            self._row("resolution", cap.id, {"capture": cap.id, "row": rid, "method": method, "ns": self.now_ns, "ids": sorted(found)})
            urow = self.commitments.get(cap.unresolved_row or "")
            if urow is not None:
                urow.state = "superseded"
                self._promotion("resolved_into", urow, {"into": rid, "method": method}, target=rid, p=1.0)
            target = self.commitments[rid]
            target.evidence.append(cap.id)
            target.depends_on = list(dict.fromkeys(target.depends_on + [cap.id]))
            self.deps.add(rid, [cap.id])
            self._promotion("modifies", target, {"rule": "capture_resolved", "capture": cap.id, "method": method}, target=rid, p=1.0)
            out.append(cap.unresolved_row or cap.id)
            r = self.replies.get(cap.id)
            if r is not None:
                r.unresolved = False; r.linked = self._row_label(rid)
        return out

    # ---- the field and the scan ----
    def open_rows(self) -> list[Commitment]:
        return [c for c in self.commitments.values() if (c.state in OPEN_STATES or c.state == "unresolved") and c.kind != "appointment"]

    def run_field(self) -> tuple[dict, list[Commitment], dict]:
        rows = self.open_rows()
        tier_w = {aid: self.people.tier_weight(aid) for aid in self.people.by_id}
        paid = {c.id for c in rows if c.money_object and self.money.by_id.get(c.money_object) and self.money.by_id[c.money_object].status == "paid"}
        actor_index = {aid: i + 1 for i, aid in enumerate(sorted(self.people.by_id))}
        lattice, meta = self.bridge.build(rows, self.allocations, tier_w, paid, actor_index, self.texts, src_of=self.src_of)
        d, _ = self.bridge.tick(lattice, bench=self.bench)
        f = self.bridge.to_contract(d, self.state_version, depends_on=[c.id for c in rows])
        self.deps.add(f"field:{f.tick_id}", [c.id for c in rows])
        self._row("field", f"tick{f.tick_id}", f.model_dump())
        self.last_field = d
        return d, rows, meta

    def coverage_label(self) -> tuple[str, dict]:
        workdays = max(1, self.hz.days * 5 // 7)
        days = len({s0 // self.hz.per_day for s0, _ in self.allocations})
        booked_h = self.booked_min / 60.0 / workdays
        implied_h = sum(c.effort.nom_min * c.p_promoted for c in self.open_rows()) / 60.0 / workdays
        share = booked_h / 8.0
        lab = "UNKNOWN" if days == 0 else "WEAK" if share < 0.30 else "USABLE" if share < 0.60 else "STRONG"
        return lab, {"booked_h_per_workday": round(booked_h, 2), "share_of_8h": round(share, 2), "implied_h_per_workday": round(implied_h, 2), "days_with_bookings": days}

    def run_scan(self) -> list[Finding]:
        open_ids = [c.id for c in self.open_rows() if c.state != "unresolved"]
        entity_of = {c.id: (c.creditor_actor if c.debtor_actor == self.owner.id else c.debtor_actor) for c in self.open_rows()}
        dups = self.joiner.duplicates(open_ids, entity_of, floor=self.embedder.dup_floor)   # per embedder; the trough is measured on real data (B19)
        findings = recovery_scan(self.now_ns, self.commitments, self.money.by_id, self.people.by_id, self.owner.id,
                                 self.last_owner, self.last_counter, self.notes, dups)
        for cap in self.captures.values():
            if cap.state == "UNRESOLVED":
                who = self.capture_actor.get(cap.id)
                a = self.people.by_id.get(who or "")
                findings.append(Finding(finding_type="UNRESOLVED_CAPTURE", commitment_id=cap.unresolved_row, counterparty=(a.display_name if a else "—"),
                                        counterparty_tier=int(a.tier) if a else 0, days_silent=round((self.now_ns - cap.sealed_ns) / DAY_NS, 1),
                                        confidence=1.0, evidence=[cap.id], recommendation="RESOLVE", depends_on=[cap.id],
                                        why={"rendering": cap.rendering, "keys": cap.keys, "text": self.capture_text.get(cap.id, "")[:120],
                                             "note": "carried in the UNRESOLVED stock; re-joined by key every tick; the ask is priced at M4b"}))
        for f in findings:
            if not f.depends_on:
                f.depends_on = [x for x in [f.commitment_id] if x]
        for i, f in enumerate(findings):
            self._row("finding", f"{f.finding_type}:{f.commitment_id or i}", f.model_dump())
        return findings

    def write_folds(self, findings: list[Finding], field_json: dict) -> None:
        folds = self.store / "folds"
        folds.mkdir(exist_ok=True)
        (folds / "commitments.json").write_text(canon({k: v.model_dump() for k, v in sorted(self.commitments.items())}), encoding="utf-8")
        (folds / "actors.json").write_text(canon({k: v.model_dump() for k, v in sorted(self.people.by_id.items())}), encoding="utf-8")
        (folds / "money.json").write_text(canon({k: v.model_dump() for k, v in sorted(self.money.by_id.items())}), encoding="utf-8")
        (folds / "findings.json").write_text(canon([f.model_dump() for f in findings]), encoding="utf-8")
        (folds / "captures.json").write_text(canon({k: v.model_dump() for k, v in sorted(self.captures.items())}), encoding="utf-8")
        (folds / "field.json").write_text(canon({k: field_json[k] for k in ("N", "M", "v", "es", "stock_prices", "by_kind", "n_contra") if k in field_json}), encoding="utf-8")

    def receipt(self, d: dict, rows: list[Commitment], meta: dict, findings: list[Finding], t0: float) -> dict:
        cov, cov_why = self.coverage_label()
        partition = self.money.partition()
        now_label = datetime.fromtimestamp(self.now_ns / 1e9, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        arith = d.get("arithmetic", {})
        working_set = int(d["N"] * (32 + 128 + 4) + d["M"] * 8 + (128 + 4))
        return {
            "owner": self.owner_email, "now": now_label, "reflex": self.provider.provider_fp, "embedder": self.embedder.kind, "dup_floor": self.embedder.dup_floor,
            "verdict_connected": self.verdict, "island": self.island, "stats": self.stats, "open_rows": len(rows), "commitments": len(self.commitments),
            "actors": len(self.people.by_id), "money_objects": len(self.money.by_id), "findings": len(findings),
            "finding_types": {t: sum(1 for f in findings if f.finding_type == t) for t in sorted({f.finding_type for f in findings})},
            "partition": partition, "coverage": cov, "coverage_why": cov_why,
            "captures": {k: v.state for k, v in self.captures.items()},
            "capture_states": {s: sum(1 for c in self.captures.values() if c.state == s) for s in ("SEALED", "PARSED", "LINKED", "DUPLICATE", "UNRESOLVED", "REFUSED", "RESOLVED")},
            "grade_cases": {cs: sum(1 for c in self.captures.values() if c.grade_case == cs) for cs in ("seen_dismissed", "unseen", "seen_in_state")},
            "field": {"N": d["N"], "M": d["M"], "iters": d["iters"], "stock_prices": d.get("stock_prices"), "by_kind": d.get("by_kind"),
                      "n_contra": d.get("n_contra"), "es_mean": d.get("es_mean"), "binding_days": self.bridge.binding_days(d),
                      "lattice_meta": {k: meta[k] for k in ("total_work", "waiting_mass", "unresolved_mass", "cap_stocks", "embedder", "header_version")}},
            "arithmetic": arith, "instrument": self.bridge.exe.name,
            "roofline": {"instrument": self.bridge.exe.name, "bytes_counted": arith.get("bytes", 0), "working_set_bytes": working_set,
                         "regime": "cache_resident" if working_set < 32e6 else "streaming", "fraction": arith.get("fraction", -1), "floor": 0.40,
                         "note": "the counted bytes are per-pair traffic; when the working set fits in cache they never reach DRAM and the fraction is not a bandwidth claim"},
            "deps": {"objects": self.deps.size()[0], "edges": self.deps.size()[1]},
            "seconds": round(time.perf_counter() - t0, 2), "tape_rows": self.tape.seg.last_seq + 1 if self.tape.seg else 0,
        }

    def run(self, glass: bool = True, ticks: int = 0, tick_hours: float = 6.0) -> dict:
        t0 = time.perf_counter()
        self.ingest_contacts()
        self.ingest_mail()
        self.ingest_list()
        self.ingest_cal()
        self.ingest_hand()
        self.apply_money_verdict()
        for a in self.people.rows():
            self._row("registry", a.id, {"kind": "actor", **a.model_dump()})
        for m in self.money.by_id.values():
            self._row("registry", m.id, {"kind": "money", **m.model_dump()})
        d, rows, meta = self.run_field()
        self.finish_replies(d)
        tick_receipts = []
        for _ in range(int(ticks)):
            tick_receipts.append({k: v for k, v in self.tick(tick_hours).items() if k != "field"})
            d, rows, meta = self.last_field, self.open_rows(), meta
        findings = self.run_scan()
        cov, _ = self.coverage_label()
        now_label = datetime.fromtimestamp(self.now_ns / 1e9, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        text = xray_text(findings, self.money.partition(), cov, now_label)
        (self.store / "xray.txt").write_text(text + "\n", encoding="utf-8")
        self.write_folds(findings, d)
        receipt = self.receipt(d, rows, meta, findings, t0)
        receipt["ticks"] = tick_receipts
        self._row("run", "M0.5-scan", receipt)
        (self.store / "receipt.json").write_text(json.dumps(receipt, indent=1), encoding="utf-8")
        if glass:
            from glass.render import render
            render(self.store, d, rows, findings, self.money.partition(), self.hz, cov, receipt["coverage_why"], receipt, self.commitments, self.people.by_id, self.owner.id)
        self.tape.manifest()
        self.tape.close()
        return receipt


def _norm_subject(s: str) -> str:
    return re.sub(r"^\s*((re|fwd?|fw)\s*:\s*)+", "", s or "", flags=re.I).strip().lower()


def replay_verify(store: Path) -> tuple[bool, list[str]]:
    """Rebuild the folds from the tape and assert byte-identity with what the run wrote."""
    tape = Tape(store)
    ok, report = tape.verify()
    if not ok:
        return False, report
    commitments: dict[str, dict] = {}
    findings: list[dict] = []
    captures: dict[str, dict] = {}
    for _, r in tape.rows():
        if r.kind == "promotion" and r.body.get("after"):
            commitments[r.body["after"]["id"]] = r.body["after"]
        elif r.kind == "finding":
            findings.append(r.body)
        elif r.kind == "capture":
            captures[r.body["id"]] = r.body
    folds = Path(store) / "folds"
    same_c = canon(dict(sorted(commitments.items()))) == (folds / "commitments.json").read_text(encoding="utf-8")
    same_f = canon(findings) == (folds / "findings.json").read_text(encoding="utf-8")
    same_cap = True
    if (folds / "captures.json").exists():
        same_cap = canon(dict(sorted(captures.items()))) == (folds / "captures.json").read_text(encoding="utf-8")
        report.append(f"folds/captures.json: {'byte-identical' if same_cap else 'DIFFERS'} ({len(captures)} captures)")
    report.append(f"folds/commitments.json: {'byte-identical' if same_c else 'DIFFERS'} ({len(commitments)} commitments)")
    report.append(f"folds/findings.json: {'byte-identical' if same_f else 'DIFFERS'} ({len(findings)} findings)")
    return ok and same_c and same_f and same_cap, report


def hand_audit(store: Path, state_budget_s: int = 3600) -> tuple[bool, list[dict]]:
    """Walk every sealed capture on the tape and prove it reached a terminal state within the budget (F-SEALED)."""
    tape = Tape(store)
    first_ns: dict[str, int] = {}
    last: dict[str, dict] = {}
    first_terminal_ts: dict[str, int] = {}
    terminal = {"LINKED", "DUPLICATE", "UNRESOLVED", "REFUSED", "RESOLVED"}
    for _, r in tape.rows():
        if r.kind != "capture":
            continue
        cid = r.body["id"]
        first_ns.setdefault(cid, r.body.get("sealed_ns", r.ts))
        last[cid] = r.body
        if r.body["state"] in terminal and cid not in first_terminal_ts:
            first_terminal_ts[cid] = r.ts
    rows = []
    ok = True
    for cid, body in last.items():
        state = body["state"]
        # the budget bounds the time to the FIRST terminal state; a later RESOLVED is a transition out of UNRESOLVED, not a delay
        within = cid in first_terminal_ts and (first_terminal_ts[cid] - first_ns[cid]) / 1e9 <= state_budget_s
        good = state in terminal and within
        ok &= good
        rows.append({"capture": cid[:12], "rendering": body.get("rendering"), "state": state, "receipt": body.get("receipt"),
                     "refusal": body.get("refusal"), "linked_to": body.get("linked_to"), "terminal": state in terminal, "within_budget": within, "ok": good})
    return ok, rows
