"""The field bridge — Commitments + registries → lattice.bin → isobar_field --tick → Field.

The horizon is `horizon_days` × `slots_per_day` half-hour cells for one seat, plus the three stocks.
A row's mass is its nominal effort in slots × p_promoted (a candidate enters at its probability,
never at a threshold). Calendar allocations reduce a cell's capacity. Waiting rows sit in the WAITING
stock whose dual is the price of silence. The arithmetic line prints every tick.
"""
from __future__ import annotations

import json
import math
import struct
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Optional

import numpy as np

from .contracts import Arithmetic, Commitment, Contra, Field_
from .embed import COARSE_D, Embedder

ROOT = Path(__file__).resolve().parents[1]
KIND_IDX = {"deliverable": 0, "payment": 1, "quote": 2, "response": 3, "appointment": 4, "document": 5, "approval": 6, "purchase": 7, "other": 8}
CONTRA_NAMES = ["OVERCOMMIT", "DOUBLEBOOK", "DEPENDENCY", "DEADLINE", "DUPLICATE", "PAID"]
STOCKS = ["UNPLACED", "UNADJUDICATED", "WAITING"]


CPU_BELOW_PAIRS = 1_000_000   # the roofline decides per owner: under a million (row, cell) pairs the CPU reference is the tier


def find_instrument(prefer: str = "gpu") -> Path:
    order = ("isobar_field.exe", "isobar_field_cpu.exe", "isobar_field_wsl") if prefer == "gpu" else ("isobar_field_cpu.exe", "isobar_field_wsl", "isobar_field.exe")
    for name in order:
        p = ROOT / "solver" / "build" / name
        if p.exists():
            return p
    raise FileNotFoundError("solver/build/isobar_field*.exe — run solver/build.cmd")


class Horizon:
    def __init__(self, now_ns: int, horizon_days: int = 14, hours: tuple[int, int] = (7, 21), slot_min: int = 30):
        self.now = datetime.fromtimestamp(now_ns / 1e9, tz=timezone.utc)
        self.start = self.now.replace(hour=hours[0], minute=0, second=0, microsecond=0)
        self.days = horizon_days
        self.h0, self.h1 = hours
        self.slot_min = slot_min
        self.per_day = int((self.h1 - self.h0) * 60 / slot_min)
        self.nslot = self.days * self.per_day

    def slot_of(self, ns: Optional[int], clamp: bool = True) -> int:
        if ns is None:
            return self.nslot - 1
        dt = datetime.fromtimestamp(ns / 1e9, tz=timezone.utc)
        day = (dt.date() - self.start.date()).days
        mins = (dt.hour - self.h0) * 60 + dt.minute
        s = day * self.per_day + int(mins / self.slot_min)
        if clamp:
            s = max(0, min(self.nslot - 1, s))
        return s

    def label(self, slot: int) -> str:
        day, k = divmod(slot, self.per_day)
        d = self.start + timedelta(days=day)
        h = self.h0 + (k * self.slot_min) // 60
        m = (k * self.slot_min) % 60
        return f"{d.strftime('%a %d')} {h:02d}:{m:02d}"

    def day_label(self, day: int) -> str:
        return (self.start + timedelta(days=day)).strftime("%a %d")


class FieldBridge:
    def __init__(self, workdir: Path, embedder: Embedder, horizon: Horizon, T: float = 0.25, late_penalty: float = 1.0,
                 iters: int = 40, waiting_budget_frac: float = 0.30, seed: int = 42):
        self.workdir = Path(workdir); self.workdir.mkdir(parents=True, exist_ok=True)
        self.embedder = embedder
        self.hz = horizon
        self.T, self.late_penalty, self.iters, self.wbf, self.seed = T, late_penalty, iters, waiting_budget_frac, seed
        self.exe = find_instrument()
        self.tick_id = 0

    def build(self, rows: list[Commitment], allocations: list[tuple[int, int]], tier_w: dict[str, float],
              paid_ids: set[str], actor_index: dict[str, int], texts: dict[str, str],
              src_of: Optional[dict[str, int]] = None) -> tuple[Path, dict]:
        hz = self.hz
        N, nseat, nslot, ncls = len(rows), 1, hz.nslot, len(KIND_IDX)
        M = nseat * nslot + 3
        entity = np.zeros(N, np.int32); cls = np.zeros(N, np.int16); dur = np.zeros(N, np.uint8); src = np.zeros(N, np.uint8)
        t_open = np.zeros(N, np.int32); t_due = np.zeros(N, np.int32); work = np.zeros(N, np.float32); dep = np.full(N, -1, np.int32)
        inc = np.full(N, -1, np.int32); flags = np.zeros(N, np.uint32); tw = np.ones(N, np.float32); paid = np.zeros(N, np.uint8); waiting = np.zeros(N, np.uint8)
        for i, c in enumerate(rows):
            counter = c.creditor_actor if c.debtor_actor != c.creditor_actor else c.debtor_actor
            entity[i] = actor_index.get(counter, 0)
            cls[i] = KIND_IDX.get(c.kind, 8)
            d = max(1, math.ceil(c.effort.nom_min / hz.slot_min))
            dur[i] = min(255, d)
            src[i] = (src_of or {}).get(c.id, 0)          # 0 mail · 1 list · 2 cal — the DUPLICATE stencil's second key
            t_open[i] = hz.slot_of(c.release_ns) if c.release_ns else 0
            t_due[i] = hz.slot_of(c.due.latest_ns) if c.due.latest_ns else nslot - 1
            work[i] = d * max(c.p_promoted, 0.02)
            tw[i] = tier_w.get(counter, 1.0)
            if c.id in paid_ids:
                paid[i] = 1
            if c.state == "waiting":
                waiting[i] = 1
                inc[i] = nseat * nslot + 2
            elif c.state == "scheduled" and c.due.earliest_ns:
                inc[i] = hz.slot_of(c.due.earliest_ns)
        # embeddings: full via the endpoint (or the fallback), 128-d int8 for the solver
        full = self.embedder.embed([texts.get(c.id, c.deliverable_text) for c in rows]) if N else np.zeros((0, 1024), np.float32)
        emb, emb_scale = (self.embedder.coarse_int8(full) if N else (np.zeros((0, COARSE_D), np.int8), np.zeros(0, np.float32)))
        seat_key = np.zeros((nseat, COARSE_D), np.int8); seat_scale = np.full(nseat, 1.0 / 127.0, np.float32)
        # capacity: 1.0 per free cell, minus calendar allocations (a booked cell keeps 1e-3 so the log is finite)
        cap = np.ones(M, np.float32)
        for s0, s1 in allocations:
            for s in range(max(0, s0), min(nslot, s1)):
                cap[s] = 1e-3
        total = float(work.sum()) or 1.0
        wmass = float(work[waiting == 1].sum())
        cap[nseat * nslot + 0] = max(0.5, total * 0.25)
        cap[nseat * nslot + 1] = max(0.5, total * 0.05)
        cap[nseat * nslot + 2] = max(0.5, min(wmass * 0.9, total * self.wbf)) if wmass > 0 else 0.5
        supply = work.copy()
        lawwords = (ncls * nseat + 31) // 32; armwords = (nseat + 31) // 32
        law = np.full(lawwords, 0xFFFFFFFF, np.uint32); arm_mask = np.zeros(armwords, np.uint32)
        hdr = struct.pack("<4sIiiiiffiiQfi8x", b"ISOB", 1, N, nseat, nslot, ncls, self.T, self.late_penalty, self.iters, 0, self.seed, 0.80, COARSE_D)
        assert len(hdr) == 64
        path = self.workdir / "lattice.bin"
        with open(path, "wb") as f:
            f.write(hdr)
            for arr in (entity, cls, dur, src, t_open, t_due, work, dep, inc, flags, tw, paid, waiting, emb.reshape(-1), emb_scale,
                        seat_key.reshape(-1), seat_scale, cap, supply, law, arm_mask):
                f.write(np.ascontiguousarray(arr).tobytes())
        self.exe = find_instrument(prefer="cpu" if N * M < CPU_BELOW_PAIRS else "gpu")
        meta = {"N": N, "M": M, "nslot": nslot, "per_day": hz.per_day, "total_work": total, "waiting_mass": wmass,
                "embedder": self.embedder.kind, "rows": [c.id for c in rows], "cap_stocks": [float(cap[nseat * nslot + k]) for k in range(3)],
                "instrument": self.exe.name}
        return path, meta

    def tick(self, lattice: Path, bench: bool = True) -> tuple[dict, Path]:
        prev = self.workdir / "field.bin"
        out = self.workdir / "field"
        cmd = [str(self.exe), "--tick", str(lattice), "--out", str(out)]
        if prev.exists():
            cmd += ["--prev", str(prev)]
        if not bench:
            cmd.append("--no-bench")
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if r.returncode != 0:
            raise RuntimeError(f"isobar_field exit {r.returncode}: {r.stderr[-800:]}")
        d = json.loads((self.workdir / "field.json").read_text(encoding="utf-8"))
        d["stdout"] = r.stdout.strip()
        self.tick_id += 1
        return d, out

    def to_contract(self, d: dict, state_version: int) -> Field_:
        contra = [Contra(a=c["a"], b=(None if c["b"] < 0 else c["b"]), kind=CONTRA_NAMES[c["kind"]], weight=c["w"]) for c in d.get("contra", [])]
        arith = d.get("arithmetic", {})
        return Field_(tick_id=self.tick_id, state_version=state_version, N=d["N"], M=d["M"], v=d["v"], u=d["u"], es=d["es"], risk=d["risk"],
                      argmax_cell=d["argmax_cell"], contra=contra, stock_prices=d.get("stock_prices", {}),
                      binding_days=self.binding_days(d), delta_v_norm=max(0.0, float(d.get("delta_v_norm", -1))),
                      arithmetic=Arithmetic(bytes=arith.get("bytes", 0), ms=arith.get("sink_ms", 0), gbs=arith.get("gbs", 0),
                                            peak_gbs=arith.get("peak_gbs", 0), fraction=arith.get("fraction", -1)),
                      iters=d.get("iters", 0), arm=d.get("arm", 0))

    def day_prices(self, d: dict) -> list[tuple[str, float]]:
        v = np.array(d["v"][: self.hz.nslot], dtype=np.float64)
        price = np.clip(-v, 0, None)
        out = []
        for day in range(self.hz.days):
            seg = price[day * self.hz.per_day: (day + 1) * self.hz.per_day]
            out.append((self.hz.day_label(day), float(seg.mean()) if len(seg) else 0.0))
        return out

    def binding_days(self, d: dict, k: int = 3) -> list[str]:
        dp = self.day_prices(d)
        return [lab for lab, price in sorted(dp, key=lambda t: -t[1])[:k] if price > 1e-6]

    def field_delta_line(self, d: dict, rows: list[Commitment], es_prev: Optional[list[float]] = None) -> str:
        parts = []
        for m in d.get("movers", [])[:3]:
            c = m["c"]
            lab = self.hz.label(c) if c < self.hz.nslot else STOCKS[c - self.hz.nslot]
            parts.append(f"{lab} {(-m['v'] + m['dv']):.2f}→{-m['v']:.2f}")
        es = d.get("es", [])
        if es_prev and len(es_prev) == len(es):
            for i, (a, b) in enumerate(zip(es_prev, es)):
                if (a < 3.0) != (b < 3.0) and i < len(rows):
                    parts.append(f"#{rows[i].id[-6:]} sup {a:.1f}→{b:.1f} {'CONTESTED' if b >= 3.0 else 'DECIDED'}")
        sp = d.get("stock_prices", {})
        parts.append(f"wait {sp.get('WAITING', 0):.2f}")
        dvn = d.get("delta_v_norm", -1)
        if dvn is not None and dvn >= 0:
            parts.append(f"Δv {dvn:.3f}")
        return "[field] " + " · ".join(parts)
