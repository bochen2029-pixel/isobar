"""The hand lane (SPEC r0.2 §5): the forward parser keeps the note and the quoted original apart; every capture
reaches a terminal state; the three grade cases fire on the planted forwards; pastes link by key or are carried
UNRESOLVED; a note compiles as testimony; the reply is typed; the audit proves F-SEALED; a tick resolves by exact id."""
import json
from pathlib import Path

import pytest

from connectors.direct.hand import parse_forward
from gym.owner_solo import generate
from isobard.field import find_instrument
from isobard.plane import Plane, hand_audit, replay_verify

try:
    find_instrument()
    HAVE = True
except FileNotFoundError:
    HAVE = False

pytestmark = pytest.mark.skipif(not HAVE, reason="solver not built")


def test_parse_forward_separates_note_from_quoted_original():
    body = ("track this — Sam mentioned a site visit\n\n---------- Forwarded message ---------\n"
            "From: Sam Okafor <sam@okafor.example>\nDate: Tue, 15 Sep 2026 10:00:00 +0000\nSubject: Site visit notes\nTo: Bo Owner <owner@isobar.example>\n\n"
            "Sharing my notes from the site visit for your records. No reply needed.\n")
    f = parse_forward("Fwd: Site visit notes", body)
    assert f.is_forward and f.note == "track this — Sam mentioned a site visit"
    assert f.original_from_email == "sam@okafor.example" and f.original_subject == "site visit notes"
    assert f.quoted_body.startswith("Sharing my notes") and f.original_mid is None and f.original_date_ns
    g = parse_forward("a paste sent by mail", "just a line the owner typed\n")
    assert not g.is_forward and g.note == "just a line the owner typed" and g.quoted_body == ""
    h = parse_forward("FW: x", "-----Original Message-----\nFrom: a@b.example\nSent: Monday\nTo: me\nSubject: x\n\nbody here\n")
    assert h.is_forward and h.quoted_body == "body here" and h.original_from_email == "a@b.example"


@pytest.fixture(scope="module")
def gym(tmp_path_factory):
    out = tmp_path_factory.mktemp("gym_hand")
    generate(out, seed=7)
    return out


@pytest.fixture(scope="module")
def run(gym):
    p = Plane(gym, store=gym / "store_hand", reflex="stub", competence=1.0, seed=7, bench=False)
    r = p.run(glass=False, ticks=5, tick_hours=6.0)
    truth = json.loads((gym / "truth.json").read_text(encoding="utf-8"))
    caps = json.loads((p.store / "folds" / "captures.json").read_text(encoding="utf-8"))
    return p, r, truth, caps


def _cap_by_external(p: Plane, ext: str) -> dict:
    for cid, c in p.captures.items():
        pass
    # captures are keyed by observation id; find via the tape's observation rows
    from isobard.tape import Tape
    for _, row in Tape(p.store).rows():
        if row.kind == "observation" and row.body.get("lane") == "hand" and row.body.get("external_id") == ext:
            return p.captures[row.body["id"]].model_dump()
    raise KeyError(ext)


def test_every_capture_is_admitted_once_and_reaches_a_terminal_state(run):
    p, r, truth, caps = run
    assert len(caps) == 6, "three forwards and three pastes, admitted once across five ticks"
    assert r["capture_states"]["SEALED"] == 0 and r["capture_states"]["PARSED"] == 0
    ok, rows = hand_audit(p.store)
    assert ok, rows
    assert all(x["terminal"] and x["within_budget"] for x in rows)


def test_the_three_grade_cases_fire_once_each(run):
    p, r, truth, caps = run
    assert r["grade_cases"] == {"seen_dismissed": 1, "unseen": 1, "seen_in_state": 1}
    H = truth["hand"]
    f1 = _cap_by_external(p, H["seen_dismissed"]["mid"])
    assert f1["grade_case"] == "seen_dismissed" and f1["state"] == "UNRESOLVED" and f1["note_kind"] == "look_instruction"
    f2 = _cap_by_external(p, H["unseen"]["mid"])
    assert f2["grade_case"] == "unseen" and f2["state"] == "LINKED" and f2["join_method"] == "creates"
    assert any(g.channel == "domain:portal.example" for g in p.coverage)
    f3 = _cap_by_external(p, H["seen_in_state"]["mid"])
    assert f3["grade_case"] == "seen_in_state" and f3["state"] == "DUPLICATE" and f3["note_kind"] == "policy_hint"
    assert p.stats["policy_candidates"] == 1 and p.stats["grades_declared"] == 2   # dismissed → cell grade; in-state → row grade; unseen → coverage
    # the policy hint was recorded as a CANDIDATE and never applied: Lopez's tier is still what tiers.yaml says
    from isobard.tape import Tape
    pol = [row for _, row in Tape(p.store).rows() if row.kind == "policy"]
    assert pol and all(not row.body.get("applied") and row.body.get("candidate") for row in pol)


def test_pastes_link_by_key_or_are_carried_unresolved_then_resolve_by_exact_id(run):
    p, r, truth, caps = run
    H = truth["hand"]
    p1 = _cap_by_external(p, H["paste_linked"]["file"])
    assert p1["state"] == "LINKED" and p1["join_method"] == "lexical"
    linked = p.commitments[p1["linked_to"]]
    assert "drawings" in linked.deliverable_text.lower()
    p2 = _cap_by_external(p, H["paste_resolves"]["file"])
    assert p2["state"] == "RESOLVED" and p2["join_method"] == "exact" and p2["keys"].get("ids") == "Q-5521"
    assert p.commitments[p2["linked_to"]].money_object == "Q-5521"
    p3 = _cap_by_external(p, H["paste_stays"]["file"])
    assert p3["state"] == "UNRESOLVED" and p3["unresolved_row"] in p.commitments and p.commitments[p3["unresolved_row"]].state == "unresolved"
    # the resolution happened on the tick that admitted the future mail, and its cone was invalidated
    ticks = r["ticks"]
    assert ticks[4]["arrived"] == 1 and len(ticks[4]["resolved"]) == 1 and all(len(t["resolved"]) == 0 for t in ticks[:4])
    assert r["stats"]["captures_resolved"] == 1 and r["stats"]["captures_unresolved"] == 2


def test_replies_are_typed_and_the_field_moved_on_every_tick(run):
    p, r, truth, caps = run
    assert r["stats"]["replies"] == 6
    texts = [(p.store / "hand" / "replies" / f"{c['receipt']}.txt").read_text(encoding="utf-8") for c in caps.values()]
    assert all(t.startswith("sealed   ") for t in texts) and any("unresolved (re-asked each tick)" in t for t in texts)
    assert any("linked   #" in t for t in texts)
    for t in r["ticks"]:
        assert t["delta_v_norm"] > 0, "time alone consumes slack: the field must move on every tick"
    assert all(t["stock_prices"]["UNRESOLVED"] > 0 for t in r["ticks"])


def test_replay_is_byte_identical_including_captures(run):
    p, r, truth, caps = run
    ok, report = replay_verify(p.store)
    assert ok, report
    assert any("captures.json: byte-identical" in line for line in report)
