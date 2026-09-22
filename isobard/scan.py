"""The Recovery Scan — the X-ray. Read-only. Every finding carries its reason, its evidence, the
counterparty and its tier, the age, the amount if confidently known with its payment-status label,
a confidence (a product of the cell probabilities that produced it — reported, never thresholded),
and a recommendation. Findings are ranked; none is hidden."""
from __future__ import annotations

from typing import Any, Optional

from .contracts import Actor, Commitment, Finding, MoneyObject

DAY_NS = 86400 * 10**9


def _days(a: Optional[int], b: int) -> Optional[float]:
    return None if a is None else round((b - a) / DAY_NS, 1)


def recovery_scan(now_ns: int, commitments: dict[str, Commitment], money: dict[str, MoneyObject], actors: dict[str, Actor],
                  owner_id: str, replies_by_thread: dict[str, int], notes: dict[str, dict], duplicates: list[tuple[str, str, float]],
                  quiet_days: float = 5.0) -> list[Finding]:
    out: list[Finding] = []
    seen_money: set[str] = set()

    def actor_name(aid: str) -> tuple[str, int]:
        a = actors.get(aid)
        return (a.display_name or aid, int(a.tier)) if a else (aid, 0)

    for c in commitments.values():
        if c.state in ("discharged", "cancelled", "superseded"):
            continue
        if c.kind == "appointment":
            continue
        counter = c.creditor_actor if c.debtor_actor == owner_id else c.debtor_actor
        cname, tier = actor_name(counter)
        last_reply = replies_by_thread.get(c.thread_id or "", None)
        silent_days = _days(c.release_ns, now_ns) if last_reply is None or (c.release_ns and last_reply < c.release_ns) else _days(last_reply, now_ns)
        note = notes.get(c.id, {})
        mo = money.get(c.money_object) if c.money_object else None
        base_why = {"rule": note.get("rule"), "direction": note.get("direction"), "p_promoted": round(c.p_promoted, 3),
                    "p_hard": round(c.due.p_hard, 3), "thread": c.thread_id, "state": c.state}

        # money-like objects first: silent proposals and apparent overdue invoices
        if mo and mo.id not in seen_money and c.debtor_actor != owner_id or (mo and mo.kind in ("quote", "proposal") and c.debtor_actor == owner_id):
            pass
        if mo and mo.id not in seen_money:
            seen_money.add(mo.id)
            if mo.kind in ("quote", "proposal") and mo.status in ("sent", "unknown") and (silent_days or 0) >= quiet_days:
                out.append(Finding(finding_type="SILENT_PROPOSAL", commitment_id=c.id, counterparty=cname, counterparty_tier=tier,
                                   amount_minor=mo.amount_minor, currency=mo.currency, payment_status_connected=mo.payment_status_connected,
                                   sent_ns=mo.issued_ns, last_meaningful_reply_ns=last_reply, days_silent=silent_days,
                                   confidence=round(min(0.99, c.p_promoted + 0.1), 3), evidence=list(c.evidence), recommendation="FOLLOW_UP",
                                   why={**base_why, "money": mo.model_dump(), "silent_days": silent_days}))
                continue
            if mo.kind == "invoice" and mo.status == "paid":
                continue  # the verdict said paid: never a finding (K_PAID)
            if mo.kind == "invoice" and mo.status in ("sent", "unknown", "overdue"):
                due = mo.due_ns or (mo.issued_ns + 30 * DAY_NS if mo.issued_ns else None)
                if due and due < now_ns:
                    out.append(Finding(finding_type="APPARENT_OVERDUE_INVOICE", commitment_id=c.id, counterparty=cname, counterparty_tier=tier,
                                       amount_minor=mo.amount_minor, currency=mo.currency, payment_status_connected=mo.payment_status_connected,
                                       sent_ns=mo.issued_ns, last_meaningful_reply_ns=last_reply, days_silent=_days(due, now_ns),
                                       confidence=round(min(0.99, c.p_promoted), 3), evidence=list(c.evidence),
                                       recommendation="FOLLOW_UP" if mo.payment_status_connected else "REVIEW",
                                       why={**base_why, "money": mo.model_dump(), "label": ("confirmed by the verdict source" if mo.status_source == "verdict_connector" else "payment status not connected — not upgraded to money owed")}))
                    continue

        # promises past due (we owe, due passed, not discharged)
        if c.debtor_actor == owner_id and c.due.latest_ns and c.due.latest_ns < now_ns:
            out.append(Finding(finding_type="PROMISE_PAST_DUE", commitment_id=c.id, counterparty=cname, counterparty_tier=tier,
                               sent_ns=c.release_ns, last_meaningful_reply_ns=last_reply, days_silent=_days(c.due.latest_ns, now_ns),
                               confidence=round(min(0.99, c.p_promoted * max(c.due.p_hard, 0.3) + 0.2), 3), evidence=list(c.evidence),
                               recommendation="DO", why={**base_why, "due_span": note.get("due_span"), "days_past_due": _days(c.due.latest_ns, now_ns)}))
            continue
        # a counterparty is waiting on the owner (they asked; the owner never replied)
        tw = note.get("they_wait", (False, 0.0))
        if c.debtor_actor == owner_id and c.state == "active" and (silent_days or 0) >= quiet_days and c.creditor_actor != owner_id and c.thread_id and c.thread_id not in replies_by_thread:
            out.append(Finding(finding_type="CUSTOMER_WAITING", commitment_id=c.id, counterparty=cname, counterparty_tier=tier,
                               sent_ns=c.release_ns, last_meaningful_reply_ns=None, days_silent=silent_days,
                               confidence=round(min(0.99, c.p_promoted * (0.5 + 0.5 * float(tw[1]))), 3), evidence=list(c.evidence),
                               recommendation="REPLY", why={**base_why, "they_wait": tw}))
            continue
        # the owner is waiting on a counterparty
        if c.state == "waiting" and (silent_days or 0) >= quiet_days:
            ww = note.get("we_wait", (False, 0.0))
            out.append(Finding(finding_type="WE_ARE_WAITING", commitment_id=c.id, counterparty=cname, counterparty_tier=tier,
                               sent_ns=c.release_ns, last_meaningful_reply_ns=last_reply, days_silent=silent_days,
                               confidence=round(min(0.99, c.p_promoted * (0.5 + 0.5 * float(ww[1]))), 3), evidence=list(c.evidence),
                               recommendation="FOLLOW_UP", why={**base_why, "we_wait": ww}))
            continue

    for a, b, cs in duplicates:
        ca, cb = commitments.get(a), commitments.get(b)
        if not ca or not cb:
            continue
        cname, tier = actor_name(ca.creditor_actor if ca.debtor_actor == owner_id else ca.debtor_actor)
        out.append(Finding(finding_type="DUPLICATE", commitment_id=a, counterparty=cname, counterparty_tier=tier, confidence=round(cs, 3),
                           evidence=list(ca.evidence) + list(cb.evidence), recommendation="MERGE",
                           why={"pair": [a, b], "cosine": round(cs, 3), "a": ca.deliverable_text[:80], "b": cb.deliverable_text[:80], "note": "candidate; a sampled audit grades precision"}))

    order = {"APPARENT_OVERDUE_INVOICE": 0, "SILENT_PROPOSAL": 1, "PROMISE_PAST_DUE": 2, "CUSTOMER_WAITING": 3, "WE_ARE_WAITING": 4, "DUPLICATE": 5}
    out.sort(key=lambda f: (order.get(f.finding_type, 9), f.counterparty_tier or 9, -(f.amount_minor or 0), -f.confidence))
    return out


def xray_text(findings: list[Finding], partition: dict[str, int], coverage: str, now_label: str) -> str:
    def usd(minor: int) -> str:
        return f"${minor/100:,.0f}"
    lines = [f"ISOBAR X-RAY · as of {now_label} · capacity coverage {coverage}", ""]
    lines.append(f"  {usd(partition['proposal_pipeline']):>10}  proposals with no reply (pipeline, not receivable)")
    lines.append(f"  {usd(partition['confirmed_receivable']):>10}  confirmed receivable (verdict source)")
    lines.append(f"  {usd(partition['apparent_overdue_not_connected']):>10}  invoices that appear overdue* (*payment status not connected)")
    counts: dict[str, int] = {}
    for f in findings:
        counts[f.finding_type] = counts.get(f.finding_type, 0) + 1
    lines.append(f"  {counts.get('CUSTOMER_WAITING', 0):>10}  people waiting on you")
    lines.append(f"  {counts.get('WE_ARE_WAITING', 0):>10}  things you are waiting on")
    lines.append(f"  {counts.get('PROMISE_PAST_DUE', 0):>10}  promises whose stated dates have passed")
    lines.append(f"  {counts.get('DUPLICATE', 0):>10}  duplicate candidates (mail vs list)")
    lines.append("")
    for f in findings:
        amt = f" {f.amount_minor/100:,.0f} {f.currency}" if f.amount_minor else ""
        lab = "" if f.payment_status_connected or not f.amount_minor else " [not connected]"
        lines.append(f"  {f.finding_type:<26} T{f.counterparty_tier} {f.counterparty:<16}{amt}{lab}  silent {f.days_silent}d  p={f.confidence:.2f}  → {f.recommendation}")
    return "\n".join(lines)
