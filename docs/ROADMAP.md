# ROADMAP — stages, gates, falsifiers

*Rev 0.1 · 2026-09-22. One milestone per session. A stage is done when its gate exits 0 and its receipt is under `runs/<stage>/`. Nothing advances until the previous stage has produced exterior outcome rows. Every falsifier below has a lie arm and a threshold registered in `isobar.lock` before the run that uses it.*

## The stages

| M | builds | mounts | gate (exit criteria) |
|---|---|---|---|
| **M0 · the X-ray** | the tape (segments, chain, `replay --verify`) · connectors: Composio **and** one direct adapter for mail, calendar, list, plus the contacts read · CODE + REFLEX (Laya) + JOIN (exact → lexical → embed → rerank → same_as) · PROMOTE · **the people registry with `tiers.yaml`** · `isobar_field` CPU reference with O1–O6, O8 and `--bench` · the Recovery Scan (read-only, 90 days) · the glass (price map, particles, stocks, four bays, why-drawer) | Laya · `:8092` · `everywhere` · `chunker` | **F-RECOVERY**: ≥ 60 % of pilot owners find ≥ 3 unknown items at owner-audited precision ≥ 0.80 in ten minutes · **F-JEV** on 200 owner-labelled emails (per-question reliability curves, monotone) · **F-TIER** · the arithmetic line printed every tick · `replay --verify` byte-identical · injection corpus green |
| **M1 · the multiverse and the wager** | `isobar_foresee` CPU reference then GPU with O7 parity · the writ file · the action menu · the pipper with band and do-nothing number · the wager row on every commitment-bearing draft · TRAIN from arrived outcomes (durations, arrivals, latencies) · O9 paired arrived backtest | `flight_computer.cu` leaf | **F-WAGER**: reliability curve of forecast survival vs promises kept over ≥ 4 weeks, 8 bins, monotone · **F-PRICE**: AUC of a slot's price 3 days out vs whether the commitment landing there slipped · **F-ROOFLINE** printed; the CPU/GPU decision recorded |
| **M2 · the composer** | nib's surface on the reply box (or the compose pane decided in BACKLOG) · in-flight REFLEX · warm-started rehearsal at `K_compose` · the gutter margin · the un-say with aired/killed rows | `nib` | **F-COMPOSER**: promise-kept rate and edit-before-send rate, gutter on vs off, paired weeks |
| **M3 · presence** | the `FieldDelta` lane · `FieldSource` driver · FIELD_WATCH and SENTINEL seats · the hold row at every boundary · the switch (OFF / SHADOW / LIVE) as a tape row · **the threshold twin** on ‖Δv‖ (swept) in shadow · κ printed weekly | `fusord` via nib's lift | **F-RESIDENT** (decisive): resident vs twin, catches-that-mattered and false fires, blind, 2 weeks, both grains — **or the resident is retired and the threshold ships**; F-INERT (OFF is byte-identical to stock) |
| **M4 · authority** | the gate (verbs, closed reasons, build hash on every verdict) · the outbox (inverse first, idempotency, hold window, receipt) · the licence ledger with a governor-held salt · ONE_CLICK sends · corrections-over-approvals grading · κ | `governord` seam | ≥ 20 one-click sends per class with edit distance ≤ 0.15 · zero high-severity licence outcomes · **F-KAPPA**: κ falling week over week · **F-INJECT** on every lane |
| **M4a · places and money** | the places registry (addresses → confirmed home/work → cached travel edges) · `K_TRAVEL` · travel buffers · the money registry with one read-only verdict connector · `K_PAID` (O8 live) · the found-money partition · the location lane behind consent (optional) | a routing service · Stripe / QuickBooks / Xero / bank feed | **F-PAID** (release-blocking) · **F-TRAVEL** · `calendar_truth` measured vs sampled printed side by side where location is consented · **F-COVERAGE** |
| **M5 · the gym and the branch** | `gym/`: synthetic owners with planted truth, stub cognition with competence knobs, lie arms · O-MONO sweep · the counterfactual fortnight in a microVM · attachment opening · CPU fan-out with the branch manifest | `C:/e2b` | the competence sweep smooth and monotone · a planted paid-invoice-the-mail-cannot-see never chases · a planted two-place collision fires K_TRAVEL · the fortnight is paired and labelled `simulated` |
| **M6 · the heads and the tune** | deterministic heads over the repair (`ScheduleDelta`, `DraftIntent`, `TaskDelta`) · the disposition tune on the hold record (offline, generations) · reflex reliability refits · learned durations per class · **F-BASELINE** (a cached turn-based system at equal evidence) | the WSL `emit` rig | **F-NOISE** · the tuned resident beats the twin by more than at M3, or the tune is a funeral, printed · **F-BASELINE**: the field beats the cached baseline on F-PRICE and outcomes, or the field is decoration |

**M0 + M1 is the product.** It prices the week and rehearses promises with no resident, no gate and no tune, on a CPU if the roofline says so.

## Falsifiers

| falsifier | kills | measure | lie arm | stage |
|---|---|---|---|---|
| **F-RECOVERY** | *the object is worth having* | ≥ 60 % of pilot owners find ≥ 3 unknown items at precision ≥ 0.80 | plant nothing; the scan must find nothing | M0 |
| **F-JEV** | *the reflex is calibrated here and earns its slot* | per-question reliability curves on this owner's outcomes; vs a cheap LLM enum at equal cost | shuffle labels; curves go flat | M0, refit M6 |
| **F-JOIN** | *the embedder earns its VRAM* | exact + lexical join rate ≥ 95 %; residual precision; planted unkeyed duplicates recovered ≥ 70 % | negate planted embeddings (O6's lie) | M0 |
| **F-TIER** | *people give prices weight* | tier-1 silence outranks tier-3 at equal age and amount, owner-audited | shuffle tiers; ranking follows | M0 |
| **F-PRICE** | *the dual predicts breaches* | AUC of price 3 days out vs slip | shuffle prices; AUC → 0.5 | M1 |
| **F-WAGER** | *survival forecasts are calibrated* | reliability curve, 8 bins, monotone, ≥ 4 weeks | shuffle forecasts | M1 |
| **F-ROOFLINE** | *the card is justified* | achieved / measured peak ≥ `floor_fraction`, every tick | hard-code the peak; the oracle refuses | M1 |
| **F-COMPOSER** | *the in-flight wager changes what is promised* | promise-kept and edit-before-send, gutter on/off, paired weeks | random survival numbers | M2 |
| **F-RESIDENT** | *presence beats the threshold twin* | catches-that-mattered and false fires, blind, 2 weeks, both grains | give the twin the resident's disposition; must tie | M3 |
| **F-INERT** | *OFF is off* | a scripted session replays byte-identical to stock; no GPU work attributable | flip the switch mid-run; must diverge | M3 |
| **F-KAPPA** | *the persona removes decisions* | attention minutes per outcome, weekly, falling | count review minutes as free | M4 |
| **F-INJECT** | *inbound is data* | per-lane corpus ⇒ zero effects without the gate | disable SENTINEL and the grammar; effects leak | M4 |
| **F-PAID** | *a paid invoice is never chased* | planted paid-where-mail-cannot-see ⇒ no chase, status PAID | disconnect the verdict silently; the chase fires and O8 catches it | M4a, release-blocking |
| **F-TRAVEL** | *places make the lattice spatial* | planted two-place collision fires K_TRAVEL | zero the edges; the collision vanishes | M4a |
| **F-COVERAGE** | *no false reassurance* | planted calendar fiction ⇒ coverage WEAK ⇒ no "week fits" | force STRONG; the claim appears | M4a |
| **O-MONO** | *the pipeline responds to cognition quality* | metrics smooth and monotone across the competence sweep | shuffle competence labels | M5 |
| **F-NOISE** | *‖Δv‖ is the event's weight* | high-Δv mail acted on within the day; ≈0-Δv ignored by the owner too | randomise Δv | M6 |
| **F-BASELINE** | *the field is not decoration* | a cached turn-based system at equal evidence loses on F-PRICE and outcomes | withhold the field from it | M6 |
| **O1–O9** | *the instrument is real* | one dynamics source · determinism · conservation · stocks priced · int8 precision · duplicate recall · parity · K_PAID · paired arrived grading | as in `ledger_lattice.cu --lie` | M0–M4a |

## Status

| M | state | receipt |
|---|---|---|
| **M0** | **built; green on the gym (2026-09-22)** — 29/29 tests; instrument 8/8 oracles on three compilers with lie arms; 7/7 plants at precision 1.00 with a perfect reflex; monotone sweep; replay byte-identical. **Owner-facing half pending:** F-RECOVERY on pilot owners, F-JEV on 200 owner-labelled emails with the Laya weights. Composio adapter not yet wired (no key on this box); direct file adapters carry M0 | `receipts/M0_GATE_2026-09-22.md` |
| M1 | next | — |

## Standing from M0

`replay --verify` on every commit · the arithmetic line on every tick · the injection corpus in CI · the threshold twin in shadow from M3 · κ weekly from M4 · the lie arms on every selftest.

## Decisions log

| date | decision | reason |
|---|---|---|
| 2026-09-22 | People, places and money enter as **registries** the field reads, never as lanes with agents | the master architecture's ruling; a lane with its own loop would be a second ontology |
| 2026-09-22 | The CPU reference is first-class; the GPU is the interactive tier; the roofline decides per owner | for one owner the per-tick re-price is a DDR5 job by arithmetic; the multiverse is where the card earns it |
| 2026-09-22 | The resident is SHADOW by default and is raced against a threshold twin before LIVE | SEPARATION's F2 at personal radius; the inbox is sparse |
| 2026-09-22 | v1 plane in Python 3.13; both solver instruments in C++17/CUDA; the resident mounted from nib | fastest honest path to M0; the contracts bind, the language does not |
| 2026-09-22 | `K_PAID` is release-blocking | the single worst error the product can make is chasing a paid invoice |
| 2026-09-22 | A discharge or a merge happens only on a **keyed** join (exact or lexical); the embedding's candidates ride the row and never change state | the arity law in code: identity is relational; a stub-wrong `is_discharge` on an embedding neighbour discharged every plant before this rule existed |
| 2026-09-22 | Instruction-shaped mail enters the tape only as `contested`, which never reaches the field or the scan | L13; the injection plant is flagged by the deterministic pre-filter regardless of the reflex |
| 2026-09-22 | Under 10⁶ (row, cell) pairs the **CPU reference is the tier**; the roofline's regime is keyed on the working set, not on counted per-pair bytes | a 15-row lattice is a 5.75 KB working set: 17 ms on the CPU, 44 ms launch-bound on the GPU; "the card is justified" prints only in the streaming regime above the floor |
| 2026-09-22 | The gate's recovery is scored by the plant's own message marker, never by type + counterparty | spurious findings at low competence otherwise counted as recoveries |
| 2026-09-22 | A perfect stub (c = 1.0) proves the pipeline; the seed-averaged sweep proves it degrades with the reflex; F-JEV is the only measurement of a reflex | the stub is not a reflex |
