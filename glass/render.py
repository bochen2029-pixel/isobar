"""Render the IR as one self-contained page: the pressure map (the dual per slot as colour), the
particles (commitments at their argmax cell, halo = support), the three stocks, the found-money
partition (four figures, never summed), the four bays, the findings with a why-drawer, the coverage
label, and the arithmetic line. It reads the field; it never computes."""
from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any

from isobard.contracts import Actor, Commitment, Finding
from isobard.field import STOCKS, Horizon

CSS = """
body{font:14px/1.4 system-ui,Segoe UI,sans-serif;margin:0;padding:18px 22px;background:#0f1115;color:#e6e6e6}
h1{font-size:18px;margin:0 0 4px} h2{font-size:14px;margin:18px 0 6px;color:#9ec1ff;text-transform:uppercase;letter-spacing:.06em}
.sub{color:#9aa}
table.map{border-collapse:collapse;font-size:10px} table.map td{width:16px;height:16px;border:1px solid #1b1f27} table.map th{font-weight:normal;color:#9aa;text-align:left;padding-right:6px;white-space:nowrap}
.stocks{display:flex;gap:18px} .stock{background:#171a21;padding:8px 12px;border-radius:6px;min-width:150px} .stock b{display:block;font-size:20px}
.money{display:flex;gap:18px;flex-wrap:wrap} .money div{background:#171a21;padding:8px 12px;border-radius:6px} .money b{display:block;font-size:18px} .lab{color:#e0b060;font-size:11px}
ul.f{list-style:none;padding:0;margin:0} ul.f li{background:#171a21;margin:6px 0;padding:8px 12px;border-radius:6px} .t{color:#9ec1ff;font-weight:600} .tier{color:#e0b060}
details{margin-top:4px} pre{white-space:pre-wrap;font-size:11px;color:#bbb;max-height:260px;overflow:auto}
.bays{display:grid;grid-template-columns:repeat(4,1fr);gap:12px} .bay{background:#171a21;padding:8px 12px;border-radius:6px} .bay h3{margin:0 0 6px;font-size:12px;color:#9ec1ff}
.bay div{font-size:12px;padding:2px 0;border-bottom:1px solid #22262e} .p{display:inline-block;border-radius:50%;background:#59f;vertical-align:middle;margin-right:6px}
.arith{font-family:ui-monospace,Consolas,monospace;font-size:12px;background:#171a21;padding:8px 12px;border-radius:6px}
.kill{color:#ff8a65}
"""


def _usd(minor: int | None, cur: str | None = "USD") -> str:
    return "—" if minor is None else f"${minor / 100:,.0f}"


def render(store: Path, d: dict, rows: list[Commitment], findings: list[Finding], partition: dict, hz: Horizon, coverage: str,
           cov_why: dict, receipt: dict, commitments: dict[str, Commitment], actors: dict[str, Actor], owner_id: str) -> Path:
    nslot = hz.nslot
    v = d["v"][:nslot]
    price = [max(0.0, -x) if x > -1e29 else 0.0 for x in v]
    pmax = max(price) if price and max(price) > 0 else 1.0
    es = d.get("es", [])
    risk = d.get("risk", [])
    amc = d.get("argmax_cell", [])
    sp = d.get("stock_prices", {})
    ar = d.get("arithmetic", {})

    def name(aid: str) -> str:
        a = actors.get(aid)
        return html.escape(a.display_name or aid) if a else html.escape(aid)

    # the pressure map
    map_rows = []
    for day in range(hz.days):
        cells = []
        for k in range(hz.per_day):
            s = day * hz.per_day + k
            p = price[s] / pmax if s < len(price) else 0.0
            here = [i for i, c in enumerate(amc) if c == s]
            col = f"rgba(255,{int(200 - 160 * p)},{int(90 - 80 * p)},{0.15 + 0.85 * p:.2f})" if p > 0 else "#12151b"
            dot = f"<span class=p style='width:{6 + 2 * len(here)}px;height:{6 + 2 * len(here)}px'></span>" if here else ""
            cells.append(f"<td style='background:{col}' title='{html.escape(hz.label(s))} price {price[s] if s < len(price) else 0:.3f}'>{dot}</td>")
        map_rows.append(f"<tr><th>{html.escape(hz.day_label(day))}</th>{''.join(cells)}</tr>")

    # particles
    parts = []
    for i, c in enumerate(rows):
        cell = amc[i] if i < len(amc) else -1
        lab = hz.label(cell) if 0 <= cell < nslot else (STOCKS[cell - nslot] if cell >= nslot else "unplaced")
        sup = es[i] if i < len(es) else 0.0
        rk = risk[i] if i < len(risk) else 0.0
        cp = c.creditor_actor if c.debtor_actor == owner_id else c.debtor_actor
        parts.append(f"<div><span class=p style='width:{6 + min(20, sup * 3):.0f}px;height:{6 + min(20, sup * 3):.0f}px;opacity:{0.9 if sup < 3 else 0.45}'></span>"
                     f"{html.escape(c.deliverable_text[:70])} <span class=sub>· {name(cp)} · {html.escape(lab)} · support {sup:.1f} {'DECIDED' if sup < 3 else 'CONTESTED'} · breach {rk:.2f}</span></div>")

    # bays
    now = hz.now.timestamp() * 1e9
    bays: dict[str, list[str]] = {"NOW": [], "AT RISK": [], "NEXT": [], "WAITING": []}
    for i, c in enumerate(rows):
        rk = risk[i] if i < len(risk) else 0.0
        due = c.due.latest_ns
        line = f"{html.escape(c.deliverable_text[:60])} <span class=sub>{name(c.creditor_actor if c.debtor_actor == owner_id else c.debtor_actor)}</span>"
        if c.state == "waiting":
            bays["WAITING"].append(line)
        elif due and due < now + 2 * 86400e9:
            bays["NOW"].append(line)
        elif rk > 0.5:
            bays["AT RISK"].append(line)
        else:
            bays["NEXT"].append(line)

    # findings
    fl = []
    for f in findings:
        amt = f" · {_usd(f.amount_minor)}" + ("" if f.payment_status_connected or not f.amount_minor else " <span class=lab>payment status not connected</span>") if f.amount_minor else ""
        fl.append(f"<li><span class=t>{f.finding_type}</span> <span class=tier>T{f.counterparty_tier}</span> {html.escape(f.counterparty)}{amt}"
                  f" · silent {f.days_silent} d · p {f.confidence:.2f} · <b>{f.recommendation}</b>"
                  f"<details><summary>why</summary><pre>{html.escape(json.dumps(f.why, indent=1, default=str))}\nevidence: {html.escape(', '.join(f.evidence))}</pre></details></li>")

    frac = ar.get("fraction", -1)
    rl = receipt.get("roofline", {})
    if rl.get("regime") == "cache_resident":
        verdict = "<span class=kill>cache-resident lattice — the counted bytes never reach DRAM, the roofline does not apply, and the CPU reference is the tier for this owner. Printed either way.</span>"
    elif frac is not None and frac < 0.40:
        verdict = "<span class=kill>BELOW THE 40% FLOOR — for this owner the re-price is a CPU job, and the card is not justified by this workload. Printed either way.</span>"
    else:
        verdict = "bandwidth-bound: the card is justified"
    arith = (f"{html.escape(rl.get('instrument', ''))} · sinkhorn {d.get('iters')} iters · {ar.get('sink_ms', 0):.2f} ms · {ar.get('bytes', 0) / 1e6:.2f} MB counted · "
             f"{ar.get('gbs', 0):.1f} GB/s vs measured peak {ar.get('peak_gbs', 0):.1f} GB/s · " + verdict)

    page = f"""<!doctype html><meta charset=utf-8><title>ISOBAR · the glass</title><style>{CSS}</style>
<h1>ISOBAR · the glass <span class=sub>· {html.escape(receipt.get('now', ''))} · {html.escape(receipt.get('owner', ''))}</span></h1>
<div class=sub>capacity coverage <b>{coverage}</b> ({html.escape(json.dumps(cov_why))}) · reflex {html.escape(receipt.get('reflex', ''))} · embedder {html.escape(receipt.get('embedder', ''))} · instrument {html.escape(receipt.get('instrument', ''))}</div>
<h2>the pressure map — the dual of each half-hour, {hz.days} days × {hz.per_day} slots; dots are commitments at their argmax cell</h2>
<table class=map>{''.join(map_rows)}</table>
<h2>the stocks — prices</h2>
<div class=stocks><div class=stock>backlog (UNPLACED)<b>{sp.get('UNPLACED', 0):.3f}</b></div><div class=stock>waiting on me (UNADJUDICATED)<b>{sp.get('UNADJUDICATED', 0):.3f}</b></div><div class=stock>waiting on them (WAITING)<b>{sp.get('WAITING', 0):.3f}</b><span class=sub>the price of their silence</span></div></div>
<h2>the money partition — four figures, never summed</h2>
<div class=money><div>proposal pipeline<b>{_usd(partition['proposal_pipeline'])}</b></div><div>confirmed receivable<b>{_usd(partition['confirmed_receivable'])}</b><span class=sub>verdict source</span></div>
<div>apparent overdue<b>{_usd(partition['apparent_overdue_not_connected'])}</b><span class=lab>payment status not connected</span></div><div>vendor credit<b>{_usd(partition['vendor_credit'])}</b></div></div>
<h2>the X-ray — {len(findings)} findings, ranked; none hidden</h2>
<ul class=f>{''.join(fl) or '<li>nothing found</li>'}</ul>
<h2>the four bays</h2>
<div class=bays>{''.join(f"<div class=bay><h3>{k} · {len(vv)}</h3>{''.join(f'<div>{x}</div>' for x in vv) or '<div class=sub>—</div>'}</div>" for k, vv in bays.items())}</div>
<h2>particles — {len(rows)} open commitments in the lattice</h2>
{''.join(parts) or '<div class=sub>none</div>'}
<h2>the arithmetic line</h2>
<div class=arith>{arith}</div>
<p class=sub>Nothing on this page is generated prose. Every number carries its source in the why-drawer or on the tape ({receipt.get('tape_rows')} rows). The plane is read-only at M0: no effect exists.</p>
"""
    out = Path(store) / "glass.html"
    out.write_text(page, encoding="utf-8")
    return out
