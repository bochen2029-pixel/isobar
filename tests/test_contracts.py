"""The typed objects round-trip, address by content, and refuse what the laws forbid."""
import json

import pytest
from pydantic import ValidationError

from isobard import contracts as c


def test_observation_content_id_is_stable_and_excludes_id():
    o = c.Observation(lane="mail", source="mbox", external_id="m1", occurred_ns=10, ingested_ns=11,
                      payload_ref="inline:hello", digest=c.blake128(b"hello")).with_id()
    again = c.Observation(**{**o.model_dump(), "id": "zzz"}).with_id()
    assert o.id == again.id and len(o.id) == 32


def test_round_trip_every_model_through_json():
    samples = {
        c.Observation: dict(lane="cal", source="ics", external_id="e1", occurred_ns=1, ingested_ns=2, payload_ref="inline:x", digest="ab"),
        c.Cell: dict(observation_id="o", provider="stub", provider_fp="fp", questions_version=1,
                     fields={"is_commitment_bearing": {"value": True, "p": 0.9, "provenance": "HIGH"}}),
        c.Commitment: dict(id="c1", debtor_actor="me", creditor_actor="lopez", kind="deliverable", deliverable_text="proposal"),
        c.Effect: dict(id="e", intent_id="i", target="cal.move", payload={"to": 3}, inverse={"to": 1}, precondition={"state_version": 4}, idempotency_key="k"),
        c.Actor: dict(id="a", display_name="Lopez", tier=1, relation="client"),
        c.MoneyObject: dict(id="m", kind="invoice", counterparty="a", amount_minor=815000, currency="USD"),
        c.Finding: dict(finding_type="SILENT_PROPOSAL", counterparty="a", confidence=0.96),
    }
    for model, kw in samples.items():
        obj = model(**kw)
        back = model.model_validate_json(obj.model_dump_json())
        assert back == obj
        assert json.loads(c.canon(obj.model_dump(mode="json"))) == obj.model_dump(mode="json")


def test_effect_without_inverse_is_refused():
    with pytest.raises(ValidationError):
        c.Effect(id="e", intent_id="i", target="mail.send", payload={}, inverse={}, precondition={}, idempotency_key="k")
    ok = c.Effect(id="e", intent_id="i", target="mail.send", payload={}, inverse="irreversible", precondition={}, idempotency_key="k")
    assert ok.inverse == "irreversible"


def test_effort_ordering_is_enforced():
    with pytest.raises(ValidationError):
        c.Effort(opt_min=60, nom_min=30, cons_min=90)
    c.Effort(opt_min=30, nom_min=60, cons_min=90)


def test_probabilities_are_bounded():
    with pytest.raises(ValidationError):
        c.CellField(value=1, p=1.2)


def test_extra_fields_are_refused():
    with pytest.raises(ValidationError):
        c.Actor(id="a", tier=1, urgency_sounds_high=True)
