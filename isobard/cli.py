"""isobar — the CLI.

    python -m isobard.cli about
    python -m isobard.cli scan   --owner DIR [--store DIR] [--reflex stub|laya] [--competence 0.9] [--no-verdict] [--no-bench] [--no-glass]
    python -m isobard.cli replay --store DIR --verify
    python -m isobard.cli sweep  --owner DIR [--competence 0.6,0.8,0.96]          # O-MONO on the stub
    python -m isobard.cli gym    --out DIR [--seed 7]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from isobard import __version__  # noqa: E402


def cmd_about(a: argparse.Namespace) -> int:
    from isobard.field import find_instrument
    from isobard.reflex_client import QuestionSet
    from isobard.embed import Embedder
    info: dict = {"name": "isobar", "version": __version__, "verbs": ["about", "scan", "replay", "sweep", "gym"],
                  "spec": "docs/SPEC.md", "lock": "isobar.lock"}
    try:
        exe = find_instrument()
        info["instrument"] = str(exe)
        if a.deep:
            r = subprocess.run([str(exe), "--selftest"], capture_output=True, text=True, timeout=600)
            info["instrument_selftest_exit"] = r.returncode
    except FileNotFoundError as e:
        info["instrument"] = f"MISSING: {e}"
    qs = QuestionSet.load()
    info["questions"] = {"version": qs.version, "count": len(qs.main()), "fingerprint": qs.fingerprint()}
    try:
        import laya  # noqa: F401
        info["laya"] = "installed (weights fetched on first Router use)"
    except Exception:
        info["laya"] = "not installed"
    e = Embedder()
    e.embed(["probe"])
    info["embedder"] = e.kind
    print(json.dumps(info, indent=1))
    return 0


def cmd_scan(a: argparse.Namespace) -> int:
    from isobard.plane import Plane
    p = Plane(Path(a.owner), store=Path(a.store) if a.store else None, reflex=a.reflex, competence=a.competence, seed=a.seed,
              verdict=not a.no_verdict, bench=not a.no_bench)
    r = p.run(glass=not a.no_glass)
    print((p.store / "xray.txt").read_text(encoding="utf-8"))
    ar, rl = r["arithmetic"], r["roofline"]
    verdict = ("cache-resident lattice (the counted bytes never reach DRAM): the roofline does not apply; the CPU reference is the tier for this owner"
               if rl["regime"] == "cache_resident" else
               ("BELOW THE 40% FLOOR: a DDR5 job for this owner" if rl["fraction"] < 0.40 else "bandwidth-bound: the card is justified"))
    print(f"field: N={r['field']['N']} M={r['field']['M']} iters={r['field']['iters']} on {rl['instrument']} · sink {ar.get('sink_ms', 0):.2f} ms · "
          f"{ar.get('bytes', 0) / 1e6:.1f} MB counted · {ar.get('gbs', 0):.1f} GB/s vs measured peak {ar.get('peak_gbs', 0):.1f} GB/s · {verdict}")
    print(f"stocks: {r['field']['stock_prices']} · binding days {r['field']['binding_days']} · embedder {r['embedder']} · reflex {r['reflex']}")
    print(f"tape: {r['tape_rows']} rows · {r['seconds']} s · store {p.store}")
    return 0


def cmd_replay(a: argparse.Namespace) -> int:
    from isobard.plane import replay_verify
    ok, report = replay_verify(Path(a.store))
    print("\n".join(report))
    print("REPLAY: byte-identical" if ok else "REPLAY: FAILED")
    return 0 if ok else 1


def cmd_sweep(a: argparse.Namespace) -> int:
    from isobard.plane import Plane
    from isobard.gate_m0 import score_against_truth
    owner = Path(a.owner)
    truth = json.loads((owner / "truth.json").read_text(encoding="utf-8"))
    seeds = [int(x) for x in a.seeds.split(",")]
    rows = []
    for c in [float(x) for x in a.competence.split(",")]:
        per = []
        for seed in seeds:
            store = owner / f"store_c{c:.2f}_s{seed}"
            p = Plane(owner, store=store, reflex="stub", competence=c, seed=seed, bench=False)
            p.run(glass=False)
            findings = json.loads((store / "folds" / "findings.json").read_text(encoding="utf-8"))
            per.append(score_against_truth(truth, findings, json.loads((store / "folds" / "commitments.json").read_text(encoding="utf-8"))))
        mean = lambda k: sum(s[k] for s in per) / len(per)  # noqa: E731
        row = {"c": c, "seeds": seeds, "recovered_mean": round(mean("recovered"), 2), "planted": per[0]["planted"], "precision_mean": round(mean("precision"), 3),
               "findings_mean": round(mean("findings"), 1), "paid_never_chased": all(s["paid_never_chased"] for s in per),
               "injection_not_promoted": all(s["injection_not_promoted"] for s in per), "per_seed": per}
        rows.append(row)
        print(f"c={c:.2f}  recovered {row['recovered_mean']:.2f}/{row['planted']}  precision {row['precision_mean']:.2f}  findings {row['findings_mean']:.1f}  "
              f"paid_never_chased={row['paid_never_chased']}  injection_not_promoted={row['injection_not_promoted']}  (seeds {seeds})")
    mono = all(rows[i]["recovered_mean"] <= rows[i + 1]["recovered_mean"] + 1e-9 for i in range(len(rows) - 1))
    print("O-MONO (mean recovered non-decreasing in competence):", "monotone" if mono else "NOT monotone")
    (owner / "sweep.json").write_text(json.dumps(rows, indent=1), encoding="utf-8")
    return 0 if mono else 1


def cmd_gym(a: argparse.Namespace) -> int:
    from gym.owner_solo import generate
    w = generate(Path(a.out), a.seed, a.days)
    print(f"gym: {len(w.msgs)} messages, {len(w.truth['plants'])} plants -> {a.out}")
    return 0


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")   # the console on this box is cp1252
        except Exception:
            pass
    ap = argparse.ArgumentParser(prog="isobar")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("about"); s.add_argument("--deep", action="store_true"); s.set_defaults(fn=cmd_about)
    s = sub.add_parser("scan"); s.add_argument("--owner", required=True); s.add_argument("--store"); s.add_argument("--reflex", default="stub")
    s.add_argument("--competence", type=float, default=0.9); s.add_argument("--seed", type=int, default=7)
    s.add_argument("--no-verdict", action="store_true"); s.add_argument("--no-bench", action="store_true"); s.add_argument("--no-glass", action="store_true")
    s.set_defaults(fn=cmd_scan)
    s = sub.add_parser("replay"); s.add_argument("--store", required=True); s.add_argument("--verify", action="store_true"); s.set_defaults(fn=cmd_replay)
    s = sub.add_parser("sweep"); s.add_argument("--owner", required=True); s.add_argument("--competence", default="0.6,0.8,0.96,1.0"); s.add_argument("--seeds", default="7,11,13")
    s.set_defaults(fn=cmd_sweep)
    s = sub.add_parser("gym"); s.add_argument("--out", required=True); s.add_argument("--seed", type=int, default=7); s.add_argument("--days", type=int, default=90)
    s.set_defaults(fn=cmd_gym)
    a = ap.parse_args(argv)
    return a.fn(a)


if __name__ == "__main__":
    sys.exit(main())
