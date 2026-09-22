"""The field bridge: lattice.bin round-trips through the instrument, a tick prints the arithmetic
line, and two ticks on the same lattice give byte-identical duals (O2 through the IPC)."""
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pytest

from isobard.contracts import Commitment, Due, Effort
from isobard.embed import Embedder
from isobard.field import N_STOCK, FieldBridge, Horizon, find_instrument

try:
    find_instrument()
    HAVE = True
except FileNotFoundError:
    HAVE = False

pytestmark = pytest.mark.skipif(not HAVE, reason="solver/build/isobar_field*.exe not built (run solver/build.cmd)")


def _ns(y, m, d, h=9):
    return int(datetime(y, m, d, h, tzinfo=timezone.utc).timestamp() * 1e9)


def _rows():
    t0 = _ns(2026, 9, 22)
    return [
        Commitment(id="c1", debtor_actor="me", creditor_actor="lopez", kind="deliverable", deliverable_text="revised proposal for Lopez",
                   release_ns=t0, due=Due(latest_ns=_ns(2026, 9, 25, 17), p_hard=0.7), effort=Effort(opt_min=120, nom_min=300, cons_min=600), state="active", p_promoted=0.9),
        Commitment(id="c2", debtor_actor="me", creditor_actor="mom", kind="response", deliverable_text="answer mom about Sunday",
                   release_ns=t0, due=Due(latest_ns=_ns(2026, 9, 23, 17), p_hard=0.3), effort=Effort(opt_min=5, nom_min=15, cons_min=30), state="active", p_promoted=0.8),
        Commitment(id="c3", debtor_actor="ferry", creditor_actor="me", kind="response", deliverable_text="lead time on fittings from Ferry",
                   release_ns=t0, due=Due(), effort=Effort(opt_min=5, nom_min=15, cons_min=30), state="waiting", p_promoted=0.85),
    ]


def test_tick_round_trip_and_determinism(tmp_path):
    hz = Horizon(_ns(2026, 9, 22), horizon_days=14)
    br = FieldBridge(tmp_path, Embedder(), hz)
    rows = _rows()
    lattice, meta = br.build(rows, allocations=[(14, 16), (42, 44)], tier_w={"lopez": 2.0, "mom": 2.0, "ferry": 1.4}, paid_ids=set(),
                             actor_index={"lopez": 1, "mom": 2, "ferry": 3, "me": 4}, texts={}, src_of={"c1": 0, "c2": 0, "c3": 0})
    assert meta["N"] == 3 and meta["M"] == hz.nslot + N_STOCK and N_STOCK == 4 and meta["waiting_mass"] > 0
    d1, _ = br.tick(lattice, bench=False)
    assert d1["N"] == 3 and d1["M"] == meta["M"] and len(d1["v"]) == meta["M"] and len(d1["es"]) == 3
    assert d1["stock_prices"]["WAITING"] > 0, "the WAITING stock must be priced when the silence budget binds"
    assert "UNRESOLVED" in d1["stock_prices"]
    assert "sink_ms" in d1["arithmetic"] and d1["arithmetic"]["measured_peak"] is False
    f = br.to_contract(d1, state_version=1)
    assert f.N == 3 and f.arithmetic is not None and f.stock_prices["WAITING"] == d1["stock_prices"]["WAITING"]
    # booked cells are near-zero capacity: no row's argmax lands in an allocated slot
    assert not any(14 <= c < 16 or 42 <= c < 44 for c in d1["argmax_cell"])
    # determinism through the IPC: a second tick on the same lattice, same duals bit-for-bit
    (tmp_path / "field.bin").unlink()
    d2, _ = br.tick(lattice, bench=False)
    assert d2["v"] == d1["v"] and d2["u"] == d1["u"]
    # a third tick with --prev reports a zero Δv against itself
    d3, _ = br.tick(lattice, bench=False)
    assert d3["delta_v_norm"] == 0.0 and d3["movers"] == []
    line = br.field_delta_line(d3, rows)
    assert line.startswith("[field]") and "wait" in line


def test_coarse_int8_round_trip_cosine():
    e = Embedder()
    full = e._hash(["the quick brown fox", "a completely different sentence about invoices", "the quick brown fox again"])
    q, s = e.coarse_int8(full)
    assert q.shape == (3, 128) and q.dtype == np.int8
    back = q.astype(np.float32) * s[:, None]
    for i in range(3):
        c = full[i] @ e._proj
        c = c / (np.linalg.norm(c) + 1e-9)
        assert Embedder.cos(c, back[i]) >= 0.995
