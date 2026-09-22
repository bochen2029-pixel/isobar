"""People: tier is policy; resolution by identity; mention on the list lane. Money: verdict supersedes mail."""
from pathlib import Path

from isobard.contracts import MoneyObject
from isobard.registries import Money, People, norm_email


def _tiers(tmp_path: Path) -> Path:
    p = tmp_path / "tiers.yaml"
    p.write_text("version: 1\ndefault_tier: 3\ntiers:\n  1: {silence_price_floor: 1.0}\n  3: {silence_price_floor: 0.3}\n"
                 "actors:\n  - {identity: lopez@acme.example, tier: 1, relation: client}\nnever_auto_contact: [mom@family.example]\n", encoding="utf-8")
    return p


def test_tier_is_policy_never_inferred(tmp_path):
    pp = People(_tiers(tmp_path))
    a = pp.upsert("Maria Lopez", "Lopez@Acme.example", source="mail", ns=1)
    assert a.tier == 1 and a.relation == "client" and a.confirmed_by == "owner" and pp.tier_weight(a.id) == 2.0
    b = pp.upsert("Sam Okafor", "sam@okafor.example", source="mail", ns=1)
    assert b.tier == 3 and pp.tier_weight(b.id) == 1.0 and b.silence_price_floor == 0.3
    m = pp.upsert("Mom", "mom@family.example", source="contacts", ns=1)
    assert m.never_auto_contact


def test_resolution_by_identity_then_domain_name(tmp_path):
    pp = People(_tiers(tmp_path))
    a = pp.upsert("Maria Lopez", "lopez@acme.example", source="contacts", ns=1)
    assert pp.upsert("Maria Lopez", "LOPEZ@acme.example", source="mail", ns=2).id == a.id
    assert pp.upsert("Maria Lopez", "maria.lopez@acme.example", source="mail", ns=3).id == a.id   # same name, same domain
    assert pp.upsert("Maria Lopez", "maria@other.example", source="mail", ns=4).id != a.id        # different domain: a candidate, never a merge
    assert norm_email("Bo.Chen+x@gmail.com") == "bochen@gmail.com"


def test_mention_names_exactly_one_actor(tmp_path):
    pp = People(_tiers(tmp_path))
    pp.upsert("Bo Owner", "owner@isobar.example", source="owner", ns=0, is_owner=True)
    d = pp.upsert("Dan Henderson", "dan@henderson.example", source="contacts", ns=1)
    pr = pp.upsert("Priya Nair", "priya@nairlabs.example", source="contacts", ns=1)
    assert pp.mention("send Dan the revised loading dock drawings") == d.id
    assert pp.mention("review Priya's install plan") == pr.id
    assert pp.mention("pay the ISP bill") is None
    assert pp.mention("Dan and Priya both") is None      # ambiguous: never a guess


def test_money_verdict_supersedes_mail_and_partition_never_sums():
    m = Money(verdict_connected=False)
    inv = m.upsert(MoneyObject(id="INV-1", kind="invoice", counterparty="a", amount_minor=1000, status="sent", status_source="mail_inference"))
    assert not inv.payment_status_connected and m.partition()["apparent_overdue_not_connected"] == 1000
    m.verdict_connected = True
    m.apply_verdict("INV-1", "paid", 5)
    assert inv.status == "paid" and inv.status_source == "verdict_connector" and inv.payment_status_connected
    # mail may not override a verdict
    m.upsert(MoneyObject(id="INV-1", kind="invoice", counterparty="a", amount_minor=1000, status="overdue", status_source="mail_inference"))
    assert inv.status == "paid"
    p = m.partition()
    assert p["confirmed_receivable"] == 0 and p["apparent_overdue_not_connected"] == 0
