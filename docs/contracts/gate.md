# gate.contract — deterministic, nothing learned, only narrows

`gate/` imports nothing from `reflex/`, `llm/`, `presence/`, `connectors/` (CI lint). Every verdict carries the gate's build hash. There is no `allow`.

## Verbs and closed reasons

```
SILENT     nothing_moved · below_floor · already_shown · quiet_hours
FLAG       binding_day · contested_external · breach_forecast · silence_price · contradiction · money_unverified
ASK        irreversible · contested · coverage_weak · licence_below · exposure_cap · jury_disagrees · never_auto_contact
DRAFT      licence_L1 · money_not_connected · counterparty_external
ONE_CLICK  licence_L2 · inverse_window_ok
ACT        licence_L3_canary · licence_L4 · inverse_window_ok · support_decided
HOLD       state_stale_pending · resident_hold · hold_window_running
RECHECK    state_version_moved · remote_version_moved · verdict_unavailable
```

## Inputs, in the order they are checked

1. the intent's class and surface; 2. the state version it was planned against (moved ⇒ `RECHECK`); 3. the row's support (contested ⇒ never `ACT`); 4. capacity coverage (WEAK ⇒ no feasibility-bearing `ACT`); 5. the connector's reversibility and inverse window; 6. the licence rung for `(class, surface, seat)`; 7. `never_auto_contact` and quiet-hours policy; 8. the jury's verdict for irreversibles; 9. **last:** exposure cap and budget.

## Classes (v1), ordered by verdict latency then inverse window

| class | inverse | verdict source | latency | ceiling |
|---|---|---|---|---|
| `list.create / reorder / defer` | yes | owner edit | minutes | L4 |
| `cal.move_internal` | yes | owner undo | minutes | L4 |
| `cal.protect` | yes | undo | minutes | L4 |
| `mail.draft` | n/a | sent-as-is / edited (diff) / discarded | minutes | L1 from day one — the dense grader |
| `mail.nudge` | hold, then compensable | reply or silence | days | L3 |
| `money.chase` | compensable | payment / complaint | days–weeks | L1 without the verdict connector; L3 with |
| `cal.accept_external / counter` | compensable | acceptance; the meeting happens | days | L2 |
| `mail.send_commitment` | irreversible | kept / slipped | days–weeks | ASK, wager shown |
| `mail.renegotiate` / `commitment.drop` | irreversible | counterparty | weeks | ASK forever; jury on send |

## The licence

`L0 OBSERVE · L1 DRAFT · L2 ONE_CLICK · L3 CANARY · L4 LICENSED · L5 RESERVED`. A rung is earned per `(class, surface, seat)` from `Grade` rows with `salted: true`; the salt is held by the governor process, not the plane. Widening: one rung at a time after a cancellable delay; narrowing: on any evidence, immediately. A licence table older than `licence.max_age` narrows every class toward L1 inside the gate (absence narrows). Corrections outweigh approvals (`grade.edited` × 3, `grade.undone` × 5 against `sent_as_is` × 1 in the e-process, registered in `isobar.lock`).

## κ

`κ = attention_minutes_consumed / outcomes` per week, from `grade` and `hold` rows (a wake opened and dismissed is attention consumed; a hold is not). Printed every Monday; a rising κ over two weeks demotes the resident to a query interface for the following week and prints why.
