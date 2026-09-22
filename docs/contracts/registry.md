# registry.contract — people, places, money

*Registries are rows the field reads: seeded by one small read, grown by the lanes, corrected by the owner. No agents, no loop, no authority. Every row carries `provenance[]` and `confirmed_by ∈ {owner, inferred, verdict}`. Writes are tape rows of kind `registry`; the current registry is a fold.*

```
Actor {
  id, kind ∈ {person, org, agent},
  identities: [ { kind ∈ {email, phone, handle, external_id}, value, source, first_seen_ns } ],
  display_name, org_id?,
  tier ∈ {1, 2, 3, 4, unknown}            -- OWNER POLICY from tiers.yaml; a model's proposal is a candidate row
  relation ∈ {client, vendor, partner, family, colleague, agent, unknown},   -- closed vocabulary (v1)
  places[] (place ids), 
  stats { arrivals_per_week, reply_latency { n, p10_s, p50_s, p90_s }, promises_kept, promises_slipped },
  silence_price_floor (from tier), never_auto_contact: bool (policy),
  confirmed_by, provenance[]
}

Place {
  id, name, aliases[], geometry { lat, lon, radius_m }, address?,
  role ∈ {home, work, client, vendor, site, frequent, sensitive},
  actors[], hours?, access_notes?,
  travel_edges: [ { to: place_id, minutes: int, source ∈ {routing, owner, history}, cached_ns } ],
  confirmed_by, provenance[]
}

MoneyObject {
  id, kind ∈ {quote, proposal, invoice, bill, payment, credit, refund},
  counterparty (actor id), amount_minor, currency, issued_ns?, due_ns?,
  status ∈ {draft, sent, acknowledged, accepted, declined, paid, partially_paid, overdue, unknown},
  status_source ∈ {verdict_connector, mail_inference, owner},
  payment_status_connected: bool,          -- false ⇒ the glass labels every figure "payment status not connected"
  evidence[] (observation ids), commitment_id?,
  confirmed_by, provenance[]
}
```

## Resolution ladder (people)

`exact external id → exact identity (email, phone) → thread membership → domain + name → lexical → embedding → reranker → owner`. A merge that involves a money-bearing or promise-bearing identity below the `domain + name` rung is a **proposal** (`same_as` with p) until the owner confirms or a second independent identity arrives. Transitive closure over proposals is forbidden.

## What the field reads

| registry | read as | where |
|---|---|---|
| Actor.tier | `tier_weight` multiplying lateness in `place_cost` | field |
| Actor.tier, stats | the per-counterparty silence price in `WAITING`; arrival and reply-latency distributions | field, multiverse |
| Actor.never_auto_contact | a −inf mask on `NUDGE`/`COUNTER` for that counterparty | gate |
| Place.travel_edges | travel cells consumed between allocations at different places; `K_TRAVEL` in the stencil; travel buffers as masks | field |
| Place (location lane, consented) | `calendar_truth` measured per event | multiverse |
| MoneyObject.status (verdict) | discharge of payment commitments; `K_PAID`; the WAITING price `amount × age × tier` | field |
| MoneyObject.status_source | the found-money partition on the glass: confirmed_receivable / apparent_overdue (labelled) / proposal_pipeline / vendor_credit — never summed | glass |

## Files the owner edits

- `tiers.yaml` — the tier table and `never_auto_contact` list. Importance is policy, never inferred.
- `places.yaml` — confirmed home, work and sensitive places (excluded from any location capture by policy).

## Typed faults

`verdict_unavailable` (money connector down: findings degrade to `mail_inference`, labelled, never guessed) · `edge_unavailable` (routing down: travel cells fall back to the owner-set default per place pair, labelled) · `identity_ambiguous` (two candidates above the floor: a candidate row, never a merge).
