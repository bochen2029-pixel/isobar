# isobard/ — the plane

**Nothing here is built.** Python 3.13, stdlib + `pydantic` v2 + `sqlite3`; no framework, no ORM, no task queue until volume demands one. One process; the solver instruments and the resident are subprocesses at fixed paths; organs are never imported.

## Modules (planned)

```
contracts.py     the typed objects (docs/contracts/objects.md) — the single definition, mirrored in solver/isobar_types.h
tape/            segments (one writer each), chain, MANIFEST, replay --verify, the SQLite folds
ingest/          connector drivers → Observation; src_rev law; the injection tagger; the tick lane (lazy)
reflex_client/   SemanticReflex over the providers in reflex/providers; the batched compile; calibration fits
join/            exact keys → lexical → embed (:8092, resident int8 scan) → rerank → same_as; p_join
promote/         deterministic promotion: Cell + Join → Commitment/Row with distributions; NO imports from reflex/, llm/, presence/, connectors/
field/           writes lattice.bin/json; runs isobar_field; folds field rows (deltas); emits the FieldDelta line
foresee/         runs isobar_foresee (--run, --rehearse, --backtest); folds foresight rows; the pipper; wagers
registries/      people (resolution ladder, tiers.yaml), places (edges, places.yaml), money (verdict connector, partition)
gate/            verbs, closed reasons, licence lookup, exposure, inverse window; build hash on every verdict; NO learned imports
outbox/          inverse-first effects, idempotency, hold windows, verify, receipts
heads/           deterministic projections of the repair: ScheduleDelta, DraftIntent, TaskDelta
llm/             the local reader for the residual; the wording renderer; the frontier seam with the jury; redaction; nonce frames
grader/          owner reactions (sent/edited/discarded/undone/acted_within), arrivals, the salt handshake with the governor
train/           durations per class, arrivals and latencies per counterparty, reflex reliability curves — all as tape rows
glass_server/    the local page (port TODO_B6); the why-drawer; the four bays
cli.py           isobar ingest|replay|scan|field|foresee|presence|gate|about|selftest
```

## Laws enforced by lint (CI)

`promote/`, `gate/`, `field/`, `foresee/` import nothing from `reflex_client/`, `llm/`, `connectors/`, `presence/`. A `p` compared to a constant outside `gate/` is a lint error. An `Effect` written without an `inverse` or `"irreversible"` is a schema error.

## The CLI (planned)

```
isobar about                       the organ's self-description (JSON): verbs, health, versions, the switch state
isobar ingest --since 90d          backfill every connected lane; idempotent
isobar scan                        the Recovery Scan: read-only; the X-ray and the price map
isobar field                       one tick: re-price, stencil, Δv, the arithmetic line
isobar foresee [--K N --H D]       the multiverse; the pipper with band and do-nothing
isobar replay --verify             rebuild every fold from byte 0 and assert byte-identity
isobar presence on|off|shadow|live the switch (operator only; a tape row)
isobar kappa                       this week's κ
isobar selftest                    contracts round-trip, injection corpus, purity lint, solver oracles
```
