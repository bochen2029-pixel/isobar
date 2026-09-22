"""F-ISLAND (SPEC r0.2 L16, §20.2): with the cable out the tick path, the X-ray, the replay and the re-join all run,
the field still moves, remote lanes refuse NETWORK_ABSENT, effects are held with their inverses. The lie arm: a run
that never cut the cable must not verify as an island run. The cut here is the software cut (ISOBAR_NETWORK=absent
or --island); the physical cut is the operator's to run."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from gym.owner_solo import generate
from isobard.field import find_instrument
from isobard.plane import Plane, replay_verify
from isobard.tape import Tape

try:
    find_instrument()
    HAVE = True
except FileNotFoundError:
    HAVE = False

pytestmark = pytest.mark.skipif(not HAVE, reason="solver not built")
ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def gym(tmp_path_factory):
    out = tmp_path_factory.mktemp("gym_island")
    generate(out, seed=7)
    return out


def _island_rows(store: Path) -> list[dict]:
    return [r.body for _, r in Tape(store).rows() if r.kind == "island"]


def test_island_run_keeps_computing_and_refuses_the_remote(gym):
    p = Plane(gym, store=gym / "store_island", reflex="stub", competence=1.0, seed=7, bench=False, island=True)
    r = p.run(glass=False, ticks=4, tick_hours=6.0)     # 24 synthetic hours
    assert r["island"] is True
    rows = _island_rows(p.store)
    codes = {}
    for b in rows:
        codes[b.get("code", "on")] = codes.get(b.get("code", "on"), 0) + 1
    assert codes.get("on") == 1
    assert codes.get("NETWORK_ABSENT", 0) >= 1 + 6, "the IMAP hand backend and every reply must be refused with NETWORK_ABSENT"
    assert codes.get("FRONTIER_ABSENT", 0) == 4, "one per tick"
    # effects are held with their inverses, never fired
    effects = [row.body for _, row in Tape(p.store).rows() if row.kind == "effect"]
    assert len(effects) == 6 and all(e["state"] == "held" and e["held_reason"] == "NETWORK_ABSENT" and e["inverse"] for e in effects)
    assert r["stats"]["replies_held"] == 6
    # everything local still ran: the X-ray, the field on every tick, the captures, the replay
    assert (p.store / "xray.txt").exists() and r["findings"] > 0
    assert all(t["delta_v_norm"] > 0 for t in r["ticks"])
    assert r["capture_states"]["LINKED"] + r["capture_states"]["DUPLICATE"] + r["capture_states"]["UNRESOLVED"] + r["capture_states"]["RESOLVED"] == 6
    ok, report = replay_verify(p.store)
    assert ok, report


def test_the_lie_arm_a_run_without_the_cut_does_not_verify_as_island(gym):
    env = {**os.environ, "ISOBAR_NETWORK": "present"}
    store = gym / "store_lie"
    cmd = [sys.executable, "-m", "isobard.cli", "scan", "--owner", str(gym), "--store", str(store), "--competence", "1.0", "--no-bench", "--no-glass", "--ticks", "1"]
    out = subprocess.run(cmd, cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=600)
    assert out.returncode == 0, out.stderr[-800:]
    rows = _island_rows(store)
    assert not any(b.get("on") for b in rows), "no switch row: the cable was never cut"
    v = subprocess.run([sys.executable, "-m", "isobard.cli", "island", "--store", str(store), "--verify"], cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=120)
    assert v.returncode == 1 and "REFUSED" in v.stdout


def test_the_cli_verifies_the_island_arm(gym):
    env = {**os.environ, "ISOBAR_NETWORK": "absent"}
    store = gym / "store_cli_island"
    cmd = [sys.executable, "-m", "isobard.cli", "scan", "--owner", str(gym), "--store", str(store), "--competence", "1.0", "--no-bench", "--no-glass", "--ticks", "1"]
    out = subprocess.run(cmd, cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=600)
    assert out.returncode == 0, out.stderr[-800:]
    v = subprocess.run([sys.executable, "-m", "isobard.cli", "island", "--store", str(store), "--verify"], cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=120)
    assert v.returncode == 0 and "verified" in v.stdout
    a = subprocess.run([sys.executable, "-m", "isobard.cli", "hand", "audit", "--store", str(store)], cwd=str(ROOT), env=env, capture_output=True, text=True, timeout=120)
    assert a.returncode == 0 and "every capture reached a terminal state" in a.stdout
