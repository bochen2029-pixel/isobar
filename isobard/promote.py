"""Promotion — deterministic. Cell + Join + parsed evidence → Commitment rows with DISTRIBUTIONS.

Imports nothing learned (CI lint). Nothing here compares a probability to a constant: the cell's p
becomes the row's p_promoted, the hardness distribution becomes p_hard, the join stays a
distribution on the row. State comes from typed fields, never from confidence.
"""
from __future__ import annotations

import hashlib
from typing import Any, Optional

from .contracts import Cell, Commitment, Due, Effort, Join, Kind, MoneyObject
from .dates import extract_amount, extract_due, extract_invoice_id, extract_quote_id

# class priors for effort, minutes (opt, nom, cons) — replaced by the owner's history as it accrues
EFFORT_PRIOR = {
    "reply": (5, 15, 30), "review": (20, 45, 90), "prepare": (45, 120, 240), "produce": (120, 300, 600),
    "meet": (30, 60, 90), "travel": (60, 120, 240),
}
# hardness distribution: the reflex's choice, weighted by its p, becomes the row's p_hard
P_HARD = {"none": 0.05, "soft": 0.25, "firm": 0.55, "hard": 0.90}
KINDS: tuple[Kind, ...] = ("deliverable", "payment", "quote", "response", "appointment", "document", "approval", "purchase", "other")


def _cid(*parts: Any) -> str:
    return "c_" + hashlib.blake2b("|".join(map(str, parts)).encode(), digest_size=8).hexdigest()


def _f(cell: Cell, name: str, default: Any = None) -> tuple[Any, float]:
    f = cell.fields.get(name)
    return (f.value, f.p) if f else (default, 0.0)


def promote_mail(cell: Cell, join: Join, parsed: dict, owner_actor: str, sender_actor: str, recipients: list[str],
                 occurred_ns: int, observation_id: str, thread_id: str) -> tuple[Optional[Commitment], Optional[MoneyObject], dict]:
    """Returns (commitment | None, money_object | None, promotion_note)."""
    note: dict[str, Any] = {"rule": None}
    body = parsed.get("body", "")
    subject = parsed.get("headers", {}).get("Subject", "")
    is_c, p_c = _f(cell, "is_commitment_bearing", False)
    direction, p_dir = _f(cell, "direction", "none")
    kind, p_kind = _f(cell, "kind", "other")
    hardness, p_hard_c = _f(cell, "due_hardness", "none")
    effort_cls, _ = _f(cell, "effort_class", "reply")
    is_discharge, p_dis = _f(cell, "is_discharge", False)
    touches_money, p_money = _f(cell, "touches_money", False)
    inj, p_inj = _f(cell, "injection_shape", False)
    they_wait, p_tw = _f(cell, "counterparty_waiting", False)
    we_wait, p_ww = _f(cell, "we_are_waiting", False)
    outbound = bool(parsed.get("outbound"))

    money: Optional[MoneyObject] = None
    amt = extract_amount(body + " " + subject)
    inv = extract_invoice_id(body + " " + subject)
    quo = extract_quote_id(body + " " + subject)
    if touches_money or amt or inv:
        mkind = "invoice" if (inv or "invoice" in (body + subject).lower()) else ("proposal" if "proposal" in (body + subject).lower() else "quote")
        mid = inv or quo or ("M-" + hashlib.blake2b(observation_id.encode(), digest_size=4).hexdigest())
        counterparty = (recipients[0] if outbound and recipients else sender_actor)
        money = MoneyObject(id=mid, kind=mkind, counterparty=counterparty, amount_minor=amt[0] if amt else None,
                            currency=amt[1] if amt else None, issued_ns=occurred_ns if outbound else None,
                            status="sent" if outbound else "unknown", status_source="mail_inference", evidence=[observation_id])

    # a discharge closes what the join points at; the plane applies it (state change with the join's p)
    if is_discharge and join.candidates:
        note.update(rule="discharge", target=join.candidates[0].id, p=p_dis * join.candidates[0].p)
        return None, money, note

    if not is_c or direction == "none":
        note["rule"] = "not_commitment"
        return None, money, note

    # who owes whom, from the recipient's point of view (the owner)
    if outbound:
        debtor, creditor = (owner_actor, recipients[0] if recipients else sender_actor) if direction == "we_owe" else \
                           (recipients[0] if recipients else sender_actor, owner_actor)
    else:
        debtor, creditor = (owner_actor, sender_actor) if direction == "we_owe" else (sender_actor, owner_actor)
    if direction == "mutual":
        debtor, creditor = owner_actor, sender_actor

    due = extract_due(body, occurred_ns)
    o, n, c = EFFORT_PRIOR.get(effort_cls, EFFORT_PRIOR["reply"])
    kind_v: Kind = kind if kind in KINDS else "other"
    state = "waiting" if (debtor != owner_actor) else "active"
    if inj:
        state = "contested"                       # SENTINEL: instruction-shaped; never promotes past candidate
    cid = _cid(thread_id, debtor, creditor, kind_v, due[0] if due else "")
    row = Commitment(
        id=cid, debtor_actor=debtor, creditor_actor=creditor, kind=kind_v,
        deliverable_text=(subject + " — " + body[:160]).strip(" —"),
        money_object=money.id if money else None, release_ns=occurred_ns,
        due=Due(latest_ns=due[0] if due else None, p_hard=P_HARD.get(hardness, 0.05) * max(p_hard_c, 0.05) if due else 0.0),
        effort=Effort(opt_min=o, nom_min=n, cons_min=c, source="class_prior", confidence="low"),
        state=state, evidence=[observation_id], p_promoted=p_c * max(p_dir, 0.05), thread_id=thread_id,
    )
    if join.candidates and join.method != "none":
        note.update(rule="modifies", target=join.candidates[0].id, p=join.candidates[0].p)
    else:
        note["rule"] = "creates"
    note.update(direction=direction, they_wait=(they_wait, p_tw), we_wait=(we_wait, p_ww), due_span=due[1] if due else None)
    return row, money, note


def promote_list(parsed: dict, owner_actor: str, observation_id: str, occurred_ns: int) -> Commitment:
    text = parsed["text"]
    due_ns = parsed.get("due_ns")
    cid = _cid("list", text.lower())
    return Commitment(id=cid, debtor_actor=owner_actor, creditor_actor=owner_actor, kind="deliverable", deliverable_text=text,
                      release_ns=occurred_ns, due=Due(latest_ns=due_ns, p_hard=0.5 if due_ns else 0.0),
                      effort=Effort(opt_min=30, nom_min=60, cons_min=120, source="class_prior", confidence="low"),
                      state="discharged" if parsed.get("done") else "active", evidence=[observation_id], p_promoted=1.0)


def promote_cal(parsed: dict, owner_actor: str, observation_id: str) -> Commitment:
    cid = _cid("cal", parsed["uid"], parsed["start_ns"])
    dur = max(1, int((parsed["end_ns"] - parsed["start_ns"]) / 60e9))
    return Commitment(id=cid, debtor_actor=owner_actor, creditor_actor=(parsed.get("attendees") or [owner_actor])[0],
                      kind="appointment", deliverable_text=parsed["summary"], release_ns=parsed["start_ns"],
                      due=Due(earliest_ns=parsed["start_ns"], latest_ns=parsed["end_ns"], p_hard=0.9),
                      effort=Effort(opt_min=dur, nom_min=dur, cons_min=int(dur * 1.3) + 1, source="explicit", confidence="high"),
                      state="scheduled", evidence=[observation_id], p_promoted=parsed.get("p_accept", 1.0))
