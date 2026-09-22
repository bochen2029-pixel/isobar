"""The X-ray on the gym: planted truth recovered, the paid invoice never chased, the injection never
promoted, tier-1 first, the field priced, and the tape replaying byte-identically."""
import json
from pathlib import Path

import pytest

from gym.owner_solo import generate
from isobard.field import find_instrument
from isobard.gate_m0 import score_against_truth
from isobard.plane import Plane, replay_verify

try:
    find_instrument()
    HAVE = True
except FileNotFoundError:
    HAVE = False

pytestmark = pytest.mark.skipif(not HAVE, reason="solver not built")


@pytest.fixture(scope="module")
def gym(tmp_path_factory):
    out = tmp_path_factory.mktemp("gym")
    generate(out, seed=7)
    return out


def _run(gym: Path, name: str, **kw) -> tuple[Plane, dict, list[dict], dict]:
    p = Plane(gym, store=gym / name, reflex="stub", bench=False, **kw)
    r = p.run(glass=True)
    findings = json.loads((p.store / "folds" / "findings.json").read_text(encoding="utf-8"))
    commitments = json.loads((p.store / "folds" / "commitments.json").read_text(encoding="utf-8"))
    return p, r, findings, commitments


def test_xray_recovers_the_plants_with_the_verdict_connected(gym):
    """A perfect reflex (c = 1.0) proves the pipeline; the sweep below proves it degrades monotonically."""
    truth = json.loads((gym / "truth.json").read_text(encoding="utf-8"))
    p, r, findings, commitments = _run(gym, "store_c100", competence=1.0, seed=7)
    s = score_against_truth(truth, findings, commitments)
    assert s["recovered"] == s["planted"], s["checks"]
    assert s["precision"] >= 0.80, s
    assert s["paid_never_chased"], "INV-1041 is paid by the verdict source and must never appear"
    assert s["injection_not_promoted"]
    assert r["stats"]["injection_flagged"] >= 1
    # tier-1 first among the people waiting on the owner
    cw = [f for f in findings if f["finding_type"] == "CUSTOMER_WAITING"]
    assert cw and cw[0]["counterparty_tier"] == 1 and cw[0]["counterparty"] == "Mom"
    # the confirmed-overdue invoice is labelled by the verdict and recommended for follow-up
    ov = [f for f in findings if f["finding_type"] == "APPARENT_OVERDUE_INVOICE"]
    assert ov and ov[0]["payment_status_connected"] and ov[0]["recommendation"] == "FOLLOW_UP" and ov[0]["amount_minor"] == 260000
    assert r["partition"]["confirmed_receivable"] == 260000 and r["partition"]["apparent_overdue_not_connected"] == 0
    assert r["partition"]["proposal_pipeline"] == 2340000
    # the tentative "maybe Thursday" is a promise with low hardness, never a hard one
    jo = [c for c in commitments.values() if "the deck" in c["deliverable_text"].lower()]
    assert jo and jo[0]["due"]["p_hard"] < 0.5
    # the field ran: prices, a WAITING price, the arithmetic line, and the kill condition printed either way
    assert r["field"]["N"] == r["open_rows"] > 0 and r["field"]["stock_prices"]["WAITING"] > 0
    assert "sink_ms" in r["arithmetic"]
    assert r["coverage"] == "WEAK", r["coverage_why"]
    assert (p.store / "glass.html").exists() and (p.store / "xray.txt").exists()
    ok, report = replay_verify(p.store)
    assert ok, report


def test_without_the_verdict_the_paid_invoice_is_labelled_not_upgraded(gym):
    p, r, findings, commitments = _run(gym, "store_noverdict", competence=1.0, seed=7, verdict=False)
    inv = [f for f in findings if f["finding_type"] == "APPARENT_OVERDUE_INVOICE"]
    amts = {f["amount_minor"] for f in inv}
    assert 815000 in amts and 260000 in amts
    assert all(not f["payment_status_connected"] and f["recommendation"] == "REVIEW" for f in inv)
    assert r["partition"]["confirmed_receivable"] == 0 and r["partition"]["apparent_overdue_not_connected"] == 815000 + 260000


def test_competence_sweep_is_monotone(gym):
    """O-MONO: mean plants recovered (over stub seeds) is non-decreasing in reflex competence, and
    the paid invoice is never chased and the injection never promoted at ANY competence."""
    truth = json.loads((gym / "truth.json").read_text(encoding="utf-8"))
    rec = []
    for c in (0.55, 0.80, 0.96, 1.0):
        per = []
        for seed in (7, 11):
            _, r, findings, commitments = _run(gym, f"store_sweep_{c:.2f}_{seed}", competence=c, seed=seed)
            per.append(score_against_truth(truth, findings, commitments))
        rec.append((c, sum(s["recovered"] for s in per) / len(per), all(s["paid_never_chased"] for s in per), all(s["injection_not_promoted"] for s in per)))
    assert all(rec[i][1] <= rec[i + 1][1] + 1e-9 for i in range(len(rec) - 1)), rec
    assert all(t[2] for t in rec), "the paid invoice is never chased at any competence"
    assert all(t[3] for t in rec), "the injection is never promoted at any competence"
    assert rec[-1][1] == 7.0
