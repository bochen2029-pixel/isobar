# tape.contract — the only truth

Append-only, blake2b-128 hash-chained, fsync'd per record, **one writer per segment** (the OS refuses a second handle on a held segment). Every table `isobard` serves is a fold over the tape; `isobar replay --verify` rebuilds every table from byte 0 and asserts byte-identity (a standing gate from M0).

## Row

```
{ seq: u64, kind, ref, ts_ns, body: CANON-JSON, prev: blake2b-128, hash: blake2b-128 }
hash = blake2b-128( prev ‖ kind ‖ ref ‖ ts_ns ‖ body )
```
Chain runs over ciphertext where the scope is shreddable (BACKLOG B8 decides M0 vs M4); `verify` needs zero keys.

## Kinds

| kind | body | writer |
|---|---|---|
| `observation` | Observation | connectors |
| `cell` | Cell | reflex |
| `join` | Join | join |
| `promotion` | { commitment, from_state, to_state, rule, p_promoted, evidence[] } | promote (deterministic) |
| `field` | deltas of `v`, `es`, contra set; `‖Δv‖`; arithmetic line; state_version | solver |
| `foresight` | Foresight head: survival[], moves[], pipper, compute | solver |
| `hold` | Hold | presence |
| `switch` | { who: operator, from, to, wall_ms } | operator only |
| `verdict` | Verdict | gate |
| `intent` | Intent | heads |
| `effect` | Effect (inverse recorded here, BEFORE `receipt`) | outbox |
| `receipt` | Receipt | outbox |
| `wager` | Wager | outbox / composer |
| `grade` | Grade | grader (owner reaction, arrivals) |
| `calibration` | { provider, question, band, curve[8], monotone, n } | TRAIN |
| `licence` | { class, surface, rung, term, e_value, demotion_e } | governor |
| `policy` | { file, diff, who } | owner |
| `correction` | { target_kind, target_id, kind, previous, new } | owner |
| `registry` | Actor \| Place \| MoneyObject with confirmed_by | join / owner / verdict |
| `tick` | { gap_s } | clock |
| `coalesce` | { lane, dropped_count, reason } | any (loss is counted loudly) |

## Laws

1. Nothing is edited in place; a correction is a row.
2. `field` rows store deltas; the full vector is a fold.
3. `effect` precedes `receipt`; an effect whose inverse is not on the tape cannot fire.
4. The `switch` row is written only by the operator's action; presence, policy and models cannot write it.
5. Every row that a model authored is `narrative`; it never closes a claim; the glass shows it as such.
6. Torn tail: detected, prefix exposed, benign, truncated before any later append (nib's contract).

## Storage

```
store/
  tape/segments/<writer>.seg      append-only
  tape/MANIFEST                   derived: segment, first_seq, last_seq, head, bytes
  isobar.sqlite                   derived folds: commitments, actors, places, money, licences, calibrations, coverage
  vecs/coarse.i8 · full.i8        derived
  field/latest.bin                derived (the resident duals)
```
Delete `store/` except `tape/` and rebuild: the gate asserts byte-identity.
