"""The plane at M0 — ingest → reflex → join → promote → registries → field → scan → glass, every step a
row on the tape, every table a fold (`replay_verify` rebuilds the folds from the tape and asserts
byte-identity).

Read-only against the world: nothing here has an effect. The owner directory holds brand-agnostic
exports: mail.mbox (or eml/), calendar.ics, todo.txt, contacts.vcf, money.csv (a verdict source),
tiers.yaml, owner.json, and — in the gym — stub_truth.json for the stub reflex.
"""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .contracts import Commitment, Finding, MoneyObject, Observation, canon
from .dates import extract_invoice_id, extract_quote_id
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
OPEN_STATES = ("active", "waiting", "candidate", "at_risk", "in_progress")


def _jsonable(o: Any) -> Any:
    if isinstance(o, tuple):
        return list(o)
    if isinstance(o, dict):
        return {k: _jsonable(v) for k, v in o.items()}
    if isinstance(o, list):
        return [_jsonable(v) for v in o]
    return o


class Plane:
    def __init__(self, owner_dir: Path, store: Optional[Path] = None, reflex: str = "stub", competence: float = 0.9, seed: int = 7,
                 verdict: bool = True, now_ns: Optional[int] = None, bench: bool = True, horizon_days: int = 14,
                 embed_endpoint: Optional[str] = None, since_days: int = 90):
        from connectors.direct import IcsConnector, MboxConnector, MoneyCsvVerdict, TextListConnector, VcfContacts  # fixed paths, never elsewhere
        self._C = dict(mbox=MboxConnector, ics=IcsConnector, text=TextListConnector, vcf=VcfContacts, money=MoneyCsvVerdict)
        self.owner_dir = Path(owner_dir)
        self.store = Path(store) if store else self.owner_dir / "store"
        self.store.mkdir(parents=True, exist_ok=True)
        owner = json.loads((self.owner_dir / "owner.json").read_text(encoding="utf-8")) if (self.owner_dir / "owner.json").exists() else {}
        self.owner_email = owner.get("email", "")
        self.owner_name = owner.get("name", "owner")
        if now_ns is not None:
            self.now_ns = now_ns
        elif "now" in owner:
            self.now_ns = int(datetime.fromisoformat(owner["now"]).timestamp() * 1e9)
        else:
            self.now_ns = time.time_ns()
        self.since_ns = self.now_ns - since_days * DAY_NS
        self.bench = bench
        self.verdict = verdict and (self.owner_dir / "money.csv").exists()
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
        self.commitments: dict[str, Commitment] = {}
        self.notes: dict[str, dict] = {}
        self.texts: dict[str, str] = {}
        self.src_of: dict[str, int] = {}
        self.root_of: dict[str, str] = {}
        self.last_owner: dict[str, int] = {}
        self.last_counter: dict[str, int] = {}
        self.allocations: list[tuple[int, int]] = []
        self.booked_min: float = 0.0
        self.stats: dict[str, Any] = {"mail": 0, "cal": 0, "list": 0, "contacts": 0, "cells": 0, "joins_exact": 0, "joins_lexical": 0,
                                      "joins_embed": 0, "joins_none": 0, "promoted": 0, "discharged": 0, "modified": 0, "not_commitment": 0,
                                      "injection_flagged": 0, "verdicts": 0, "reflex_us": 0}
        self.owner = self.people.upsert(self.owner_name, self.owner_email, source="owner", ns=self.now_ns, is_owner=True)
        self.owner.confirmed_by = "owner"
        self.state_version = 0

    # ---- the tape ----
    def _row(self, kind: str, ref: str, body: Any):
        self.clock += 1
        return self.tape.append(kind, ref, _jsonable(body), ts=self.clock)

    def _promotion(self, rule: str, c: Commitment, note: Optional[dict] = None, target: Optional[str] = None, p: float = 0.0) -> None:
        self.state_version += 1
        c.state_version = self.state_version
        self._row("promotion", c.id, {"rule": rule, "target": target, "p": p, "after": c.model_dump(), "note": note or {}})

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

    # ---- lanes ----
    def _thread_root(self, mid: str, irt: str) -> str:
        root = self.root_of.get(irt) if irt else None
        if root is None:
            root = irt if irt else mid
        self.root_of[mid] = root
        return root

    def ingest_mail(self) -> None:
        src = self.owner_dir / "mail.mbox" if (self.owner_dir / "mail.mbox").exists() else self.owner_dir / "eml"
        if not src.exists():
            return
        conn = self._C["mbox"](src, owner_email=self.owner_email, ingest_ns=self.now_ns)
        items = sorted(conn.backfill(self.since_ns), key=lambda t: (t[0].occurred_ns, t[0].external_id))
        for obs, parsed in items:
            h = parsed["headers"]
            body, subject = parsed["body"], h.get("Subject", "")
            text = f"Subject: {subject}\n\n{body}"
            if injection_shape(text):
                obs.injection_shape = True
                obs.with_id()
            self._row("observation", obs.id, obs.model_dump())
            self.stats["mail"] += 1
            mid = obs.external_id
            root = self._thread_root(mid, (h.get("In-Reply-To") or "").strip())
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
            self.stats["cells"] += 1
            self.stats["reflex_us"] += cell.latency_us
            self._row("cell", cell.id, cell.model_dump())
            if cell.fields.get("injection_shape") and cell.fields["injection_shape"].value:
                self.stats["injection_flagged"] += 1
            open_ids = [i for i, c in self.commitments.items() if c.state in OPEN_STATES]
            money_id = extract_invoice_id(subject + " " + body) or extract_quote_id(subject + " " + body)
            keys = [k for k in dict.fromkeys([root, (h.get("In-Reply-To") or "").strip(), mid]) if k]
            join = self.joiner.join(obs.id, keys, subject, money_id, (subject + "\n" + body[:400]).strip(), open_ids)
            self.stats[{"exact": "joins_exact", "lexical": "joins_lexical", "embed_rerank_reflex": "joins_embed", "none": "joins_none"}[join.method]] += 1
            self._row("join", obs.id, join.model_dump())
            row, mo, note = promote_mail(cell, join, parsed, self.owner.id, sender.id, recips, occ, obs.id, root)
            note["outbound"] = outbound
            if mo is not None:
                mo = self.money.upsert(mo)
            keyed = join.method in ("exact", "lexical")
            if note.get("rule") == "discharge" and not keyed:
                # the arity law: a discharge is a relational state change; the embedding only PROPOSES.
                # Recorded as a candidate on the tape; nothing closes.
                self._row("promotion", obs.id, {"rule": "discharge_candidate", "target": note.get("target"), "p": float(note.get("p", 0.0)), "after": None, "note": note})
                continue
            if note.get("rule") == "discharge":
                t = note.get("target")
                if t in self.commitments and self.commitments[t].state in OPEN_STATES:
                    c = self.commitments[t]
                    c.state = "discharged"
                    c.evidence.append(obs.id)
                    self.stats["discharged"] += 1
                    if c.money_object and c.money_object in self.money.by_id and self.money.by_id[c.money_object].status_source != "verdict_connector":
                        self.money.by_id[c.money_object].status = "acknowledged"   # mail says so; only a verdict says paid (L14)
                    self._promotion("discharge", c, note, target=t, p=float(note.get("p", 0.0)))
                continue
            if row is None:
                self.stats["not_commitment"] += 1
                self._row("promotion", obs.id, {"rule": note.get("rule", "not_commitment"), "target": None, "p": 0.0, "after": None, "note": note})
                continue
            if mo is not None:
                row.money_object = mo.id
                mo.commitment_id = row.id
            target = note.get("target") if (note.get("rule") == "modifies" and keyed) else None
            if not keyed and join.candidates:
                note["join_candidates"] = [(c.id, c.p) for c in join.candidates]   # the distribution rides the row; no merge
            if target and target in self.commitments and self.commitments[target].state in OPEN_STATES:
                c = self.commitments[target]
                if row.due.latest_ns:
                    c.due = row.due
                c.evidence.append(obs.id)
                if mo is not None and not c.money_object:
                    c.money_object = mo.id
                    mo.commitment_id = c.id
                self.stats["modified"] += 1
                self._promotion("modifies", c, note, target=target, p=float(note.get("p", 0.0)))
                continue
            if row.id in self.commitments:
                c = self.commitments[row.id]
                c.evidence.append(obs.id)
                self._promotion("reinforces", c, note, target=row.id, p=row.p_promoted)
                continue
            self.commitments[row.id] = row
            self.notes[row.id] = note
            self.texts[row.id] = row.deliverable_text
            self.src_of[row.id] = 0
            self.joiner.index(row, subject=subject, money_id=mo.id if mo else None, text=row.deliverable_text)
            self.stats["promoted"] += 1
            self._promotion("creates", row, note, p=row.p_promoted)

    def ingest_list(self) -> None:
        p = self.owner_dir / "todo.txt"
        if not p.exists():
            return
        for obs, parsed in self._C["text"](p, ingest_ns=self.now_ns).backfill():
            self._row("observation", obs.id, obs.model_dump())
            self.stats["list"] += 1
            c = promote_list(parsed, self.owner.id, obs.id, obs.occurred_ns)
            who = self.people.mention(parsed["text"])
            if who:
                c.creditor_actor = who
            self.commitments[c.id] = c
            self.notes[c.id] = {"rule": "list", "outbound": True, "direction": "we_owe", "mention": who}
            self.texts[c.id] = c.deliverable_text
            self.src_of[c.id] = 1
            self.joiner.index(c, text=c.deliverable_text)
            self._promotion("list", c, self.notes[c.id], p=1.0)

    def ingest_cal(self) -> None:
        p = self.owner_dir / "calendar.ics"
        if not p.exists():
            return
        for obs, parsed in self._C["ics"](p, horizon_days=self.hz.days, ingest_ns=self.now_ns).backfill(self.since_ns):
            self._row("observation", obs.id, obs.model_dump())
            self.stats["cal"] += 1
            c = promote_cal(parsed, self.owner.id, obs.id)
            att = [self.people.upsert("", a, source="cal", ns=parsed["start_ns"]).id for a in parsed.get("attendees", [])]
            if att:
                c.creditor_actor = att[0]
            self.commitments[c.id] = c
            self.notes[c.id] = {"rule": "cal", "outbound": True}
            self.src_of[c.id] = 2
            self._promotion("cal", c, self.notes[c.id], p=c.p_promoted)
            hz_start = int(self.hz.start.timestamp() * 1e9)
            if parsed["end_ns"] > hz_start and not parsed["all_day"]:
                s0, s1 = self.hz.slot_of(parsed["start_ns"]), self.hz.slot_of(parsed["end_ns"])
                if s1 > s0:
                    self.allocations.append((s0, s1))
                    self.booked_min += (parsed["end_ns"] - parsed["start_ns"]) / 60e9

    # ---- the field and the scan ----
    def open_rows(self) -> list[Commitment]:
        return [c for c in self.commitments.values() if c.state in OPEN_STATES and c.kind != "appointment"]

    def run_field(self) -> tuple[dict, list[Commitment], dict]:
        rows = self.open_rows()
        tier_w = {aid: self.people.tier_weight(aid) for aid in self.people.by_id}
        paid = {c.id for c in rows if c.money_object and self.money.by_id.get(c.money_object) and self.money.by_id[c.money_object].status == "paid"}
        actor_index = {aid: i + 1 for i, aid in enumerate(sorted(self.people.by_id))}
        lattice, meta = self.bridge.build(rows, self.allocations, tier_w, paid, actor_index, self.texts, src_of=self.src_of)
        d, _ = self.bridge.tick(lattice, bench=self.bench)
        f = self.bridge.to_contract(d, self.state_version)
        self._row("field", f"tick{f.tick_id}", f.model_dump())
        return d, rows, meta

    def coverage(self) -> tuple[str, dict]:
        """Capacity coverage: how much of the owner's working time the calendar accounts for. A calendar
        that covers 15 % of the day is fiction as a capacity signal (HELM's gate); the label rides every
        feasibility claim and the multiverse samples calendar_truth at this estimate (M1)."""
        workdays = max(1, self.hz.days * 5 // 7)
        days = len({s0 // self.hz.per_day for s0, _ in self.allocations})
        booked_h = self.booked_min / 60.0 / workdays
        implied_h = sum(c.effort.nom_min * c.p_promoted for c in self.open_rows()) / 60.0 / workdays
        share = booked_h / 8.0
        if days == 0:
            lab = "UNKNOWN"
        elif share < 0.30:
            lab = "WEAK"
        elif share < 0.60:
            lab = "USABLE"
        else:
            lab = "STRONG"
        return lab, {"booked_h_per_workday": round(booked_h, 2), "share_of_8h": round(share, 2), "implied_h_per_workday": round(implied_h, 2), "days_with_bookings": days}

    def run_scan(self) -> list[Finding]:
        open_ids = [c.id for c in self.open_rows()]
        entity_of = {c.id: (c.creditor_actor if c.debtor_actor == self.owner.id else c.debtor_actor) for c in self.open_rows()}
        dups = self.joiner.duplicates(open_ids, entity_of, floor=0.60)
        findings = recovery_scan(self.now_ns, self.commitments, self.money.by_id, self.people.by_id, self.owner.id,
                                 self.last_owner, self.last_counter, self.notes, dups)
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
        (folds / "field.json").write_text(canon({k: field_json[k] for k in ("N", "M", "v", "es", "stock_prices", "by_kind", "n_contra") if k in field_json}), encoding="utf-8")

    def run(self, glass: bool = True) -> dict:
        t0 = time.perf_counter()
        for a in self.people.rows():
            pass
        self.ingest_contacts()
        self.ingest_mail()
        self.ingest_list()
        self.ingest_cal()
        self.apply_money_verdict()
        for a in self.people.rows():
            self._row("registry", a.id, {"kind": "actor", **a.model_dump()})
        for m in self.money.by_id.values():
            self._row("registry", m.id, {"kind": "money", **m.model_dump()})
        d, rows, meta = self.run_field()
        findings = self.run_scan()
        cov, cov_why = self.coverage()
        partition = self.money.partition()
        now_label = datetime.fromtimestamp(self.now_ns / 1e9, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        text = xray_text(findings, partition, cov, now_label)
        (self.store / "xray.txt").write_text(text + "\n", encoding="utf-8")
        self.write_folds(findings, d)
        arith = d.get("arithmetic", {})
        working_set = int(d["N"] * (32 + 128 + 4) + d["M"] * 8 + (128 + 4))   # rows (scalars + int8 emb + scale) + duals/caps + seat keys
        receipt = {
            "owner": self.owner_email, "now": now_label, "reflex": self.provider.provider_fp, "embedder": self.embedder.kind,
            "verdict_connected": self.verdict, "stats": self.stats, "open_rows": len(rows), "commitments": len(self.commitments),
            "actors": len(self.people.by_id), "money_objects": len(self.money.by_id), "findings": len(findings),
            "finding_types": {t: sum(1 for f in findings if f.finding_type == t) for t in sorted({f.finding_type for f in findings})},
            "partition": partition, "coverage": cov, "coverage_why": cov_why,
            "field": {"N": d["N"], "M": d["M"], "iters": d["iters"], "stock_prices": d.get("stock_prices"), "by_kind": d.get("by_kind"),
                      "n_contra": d.get("n_contra"), "es_mean": d.get("es_mean"), "binding_days": self.bridge.binding_days(d),
                      "lattice_meta": {k: meta[k] for k in ("total_work", "waiting_mass", "cap_stocks", "embedder")}},
            "arithmetic": arith, "instrument": self.bridge.exe.name,
            "roofline": {"instrument": self.bridge.exe.name, "bytes_counted": arith.get("bytes", 0),
                         "working_set_bytes": working_set,
                         "regime": "cache_resident" if working_set < 32e6 else "streaming",
                         "fraction": arith.get("fraction", -1), "floor": 0.40,
                         "note": "the counted bytes are per-pair traffic; when the working set fits in cache they never reach DRAM and the fraction is not a bandwidth claim"},
            "seconds": round(time.perf_counter() - t0, 2),
            "tape_rows": self.tape.seg.last_seq + 1 if self.tape.seg else 0,
        }
        self._row("run", "M0-scan", receipt)
        (self.store / "receipt.json").write_text(json.dumps(receipt, indent=1), encoding="utf-8")
        if glass:
            from glass.render import render
            render(self.store, d, rows, findings, partition, self.hz, cov, cov_why, receipt, self.commitments, self.people.by_id, self.owner.id)
        self.tape.manifest()
        self.tape.close()
        return receipt


def replay_verify(store: Path) -> tuple[bool, list[str]]:
    """Rebuild the folds from the tape and assert byte-identity with what the run wrote."""
    tape = Tape(store)
    ok, report = tape.verify()
    if not ok:
        return False, report
    commitments: dict[str, dict] = {}
    findings: list[dict] = []
    for _, r in tape.rows():
        if r.kind == "promotion" and r.body.get("after"):
            commitments[r.body["after"]["id"]] = r.body["after"]
        elif r.kind == "finding":
            findings.append(r.body)
    folds = Path(store) / "folds"
    want_c = (folds / "commitments.json").read_text(encoding="utf-8")
    want_f = (folds / "findings.json").read_text(encoding="utf-8")
    got_c = canon(dict(sorted(commitments.items())))
    got_f = canon(findings)
    same_c, same_f = got_c == want_c, got_f == want_f
    report.append(f"folds/commitments.json: {'byte-identical' if same_c else 'DIFFERS'} ({len(commitments)} commitments)")
    report.append(f"folds/findings.json: {'byte-identical' if same_f else 'DIFFERS'} ({len(findings)} findings)")
    return ok and same_c and same_f, report
