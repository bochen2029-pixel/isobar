# ISOBAR — SPECIFICATION r0.2

*Rev 0.2 · 2026-09-22 · normative. **Supersedes `docs/SPEC.md` (r0.1)**, which is kept byte-for-byte as lineage and is neither edited nor implemented against once this revision is ratified. Where this document and a dated receipt under `runs/` or `receipts/` disagree, the receipt wins and this document is the defect. Where this document and the blueprint (`docs/lineage/`) or Addendum A (`C:/AGI/ISOBAR_SPEC_ADDENDUM-A_THE-HAND-THE-STATE-LANE-AND-THE-BOX_2026-09-22_FABLE5-1.md`) disagree, this document governs the artefact and §0.2 records the decision.*

Terms: **MUST**, **MUST NOT**, **SHOULD**, **MAY** carry their usual force. Every clause is tagged **[BUILT]** (exists on `main` and is covered by a gate with a receipt), **[SPECIFIED]** (settled, unbuilt), **[BET]** (a bet with its kill named) or **[OPEN]** (undecided; collected in §25 and `docs/BACKLOG.md`). Numbers tagged **[M]** were measured on this box by the instrument named; **[V]** verified at a primary source; **[D]** derived by arithmetic with the chain shown; **[NULL]** names the cheap baseline an organ must beat; everything else is a design number to be replaced by a measurement at the rung that produces it (`docs/ROADMAP_r0.2.md`).

**Inputs held whole before writing:** r0.1 · the M0 gate receipt (`receipts/M0_GATE_2026-09-22.md`) · Addendum A (the brainstorm fork) · the Personal Operations Plane master architecture v2.0 · the Reflexive Cognitive Machine spec v0.1 and its v0.2 proposal · the 2026-09-22 brainstorm (the hand, the box, the continuum, state as a modality, the final inch) · `docs/devlog.md` and `docs/ROADMAP.md`'s decisions log.

---

## 0 · What changed, r0.1 → r0.2, and why

r0.1 was a specification with nothing built. r0.2 is written after M0 landed and against three documents that arrived the same day. Its shape is r0.1's; the numbering of sections shifts where new sections were inserted, and every r0.1 clause survives, revised or unchanged, unless §0.3 names it.

### 0.1 The changes

| # | r0.1 | r0.2 | forced by |
|---|---|---|---|
| 1 | nothing built | **M0 is BUILT** and its clauses are tagged so, with the receipt's numbers as [M] (§24) | `receipts/M0_GATE_2026-09-22.md` |
| 2 | one currency implied per organ (task metrics, AUCs, curves) | **one currency for organs, one for authority, never summed** (§21): rent — the prequential code length of the admitted stream at a fixed read budget, through the organ's own read plan — grades every organ by ablation (F-RENT); verdicts on wagers grade authority; the two are printed side by side and never added | the RCM v0.2 proposal §2; LIFELINE v5 §5; CONNECTOME v6 §2.1 |
| 3 | the solver grades nothing but its own oracles | **the chain of custody for verdicts** (§21.3): every grader faster than the world is a wager graded by the tier above it, terminating in arrival — the solver grades the reflex over transitions the same tick; the tier above grades the router on a salted fraction; the multiverse is licensed by its sim-to-real curve; a non-monotone grader leaves the chain | RCM v0.2 §3; Addendum A §7.1; the ACME verdict-rate roof |
| 4 | three lanes, three registries, the clock | **the hand lane** (§5): one owner-invoked capture primitive with many renderings; envelope trust split from payload trust; five capture states with no silent discard; the UNRESOLVED stock; the hand event as a grade in three cases with declared/passive strata; the typed reply channel; screenshots under the fence; audio and video as rungs; the phone as a sensory head; travel as a worked case; realms | the operator's brainstorm; Addendum A §4; the previous turn's reply |
| 5 | recontextualisation unaddressed | **dependency-cone invalidation, not rescans** (§10.4): re-price always, re-foresee when the glass moved, re-join every unresolved row each tick; the value of asking by two arms on one canvas; the evening batch bounded and priced by κ | Addendum A §5; BUNDLE's dependency engine; master v2.0 §8 |
| 6 | the resident on one lane, `[field]` | **state is a lane** (§13): the field's own frames compile into typed lines almost losslessly, so the resident holds the trajectory of the life with the prediction channel intact; lanes at their own clocks on one trunk; probes at line positions as the held join; the eviction column that is also the hold record; two free channels, ‖Δv‖ and surprise, neither relational; a second twin (a reflex answering `wake_worthy`) beside the threshold twin | Addendum A §6; Addendum Q; LIFELINE v5 §6.3 |
| 7 | the reflex over mail only | **the reflex over transitions** with the solver as its fast grader (§9.5); situation embeddings that carry shape and never identities, and **precedent as prior** in the multiverse (§8.7) | Addendum A §7.1–7.2 |
| 8 | "CUDA" in prose | **the island law and the accelerator contract** (§20): the interior is closed under its own computation; the solver is a leaf and an ABI, never a vendor; the word CUDA appears in build scripts and nowhere in a law | the operator's box; Addendum A §2–3 |
| 9 | a connector with `backfill/delta/capabilities/prepare/execute/verify` | **the six-interface ABI** per connector: OBSERVE · STATE · ACT · INVERT · CONSTRAIN · **GRADE**, with `expected_verdict_latency` and `verdict_source` per class (§4.2) | master v2.0 I21, §13.1; RCM v0.2 §6.1 |
| 10 | the licence ladder in one paragraph | **authority sharpened**: ignition declared at n = 0 (L27); the unattended-operation condition — an inverse must outlive its verdict latency (L28); two axes, evidence rate and blast radius under a common-mode key (L11); the retained fraction as the standing control arm (L12); PRE/POST verification as four rows (L9); κ as an exact fold undefined below `n_eff`; the published gate order (§17.2) | master v2.0 I20–I25, §13 |
| 11 | typed negatives named | **`Lookup<T>`** as a sum type so no caller reads Unknown as false (§12.3); every writer modelled and the second-human law (L2) | master v2.0 I23, I27 |
| 12 | migration unaddressed | **gradability survives migration** (L22): a question set, tier table, lattice geometry or provider version event carries a migration map; calibration curves and licences are keyed by version and carried, never reset | RCM v0.2 §5 |
| 13 | corroboration absent; deletion by taint only in the backlog | **corroboration orthogonal to trust** (L25); **the witness** (L26); taint closure on every retraction; cryptographic deletion as the M4 option (§18.4–18.6) | LIFELINE v5 §9.4, §15; RCM v0.2 §11 |
| 14 | fifteen laws | **twenty-eight laws**: L1–L15 kept (six sharpened), L16–L19 from Addendum A, L20–L28 new (§2) | all of the above |
| 15 | M0 → M6 | **the rungs of `docs/ROADMAP_r0.2.md`**: M0.5 the hand in text and the island, beside M1; M2.5 screenshots and voice; M3.5 the state lane's organs; M4b the evening batch; M5b the phone; M6b precedents; M7 the dynamics head; M8 the projected state lane (research); M9 cash and the third face; F-SEVEN at M1 and F-GRADER from the first draft | Addendum A §12; master v2.0 §20–21 |
| 16 | the join as a ladder | **keyed-only state changes** (§10.2): a discharge, a merge or a modification of an existing row happens only on an exact or lexical key; the embedding's candidates ride the row as a distribution and never change state — the arity law in code, after it bit in M0 | `docs/devlog.md` trap 7; the M0 receipt |
| 17 | the roofline as a fraction of peak | **the roofline's regime is keyed on the working set** (§20.3): under a cache-resident working set the counted per-pair bytes are not DRAM traffic and no bandwidth claim is printed; under 10⁶ (row, cell) pairs the CPU reference is the tier | the M0 receipt §4; devlog trap 11 |

### 0.2 Decisions r0.2 makes where the inputs disagreed or were silent

| D | decision | the alternative, and why not |
|---|---|---|
| D1 | **Rent is the universal organ currency; arrivals are the authority currency; the two are never summed.** | Addendum A grades organs by their own falsifiers only (F-STATE-PREDICT is one instance of rent). One currency makes organs comparable and un-gameable in isolation; but rent measures knowing, not acting, so the licence reads arrivals only. |
| D2 | **One trunk, lanes at their own clocks; only `[field]` races at M3.** `[hand]`, `[project]`, `[money]`, `[life]` enter after F-RESIDENT has a first result on `[field]`. | Five FUSORs (a ChatGPT draft) — trunks do not fork at zero cost, seats do. Racing every lane at once makes the decisive number unreadable. |
| D3 | **The hand lane in text ships at M0.5 beside M1**, not after it: a forward address is a mailbox, a reply is a mail, and the gym can plant the three grade cases today. | Deferring the hand behind the multiverse would delay the cheapest receipt in the programme. M1 is unchanged and still the product's second half. |
| D4 | **State in the middle, not a router.** The control plane is the field, the tape and the licence. A router exists only as a wager graded by the tier above (§14.3). | BUNDLE's cognitive compiler dispatches a compiled question to organs; a per-request router has no memory and cannot be graded; a state can. |
| D5 | **A radius earns a solver only when its transport is nameable** (§7.8). The week, the org and cash qualify; "a life" does not, and no life-solver is claimed. | The ChatGPT drafts' life IR / org IR / market IR: compact state without a conserved supply, a capacity, a cost and a locality key gives the solver nothing to compute. |
| D6 | **Sealing a capture is evidence admission, not an effect**, and is therefore never gated. | Addendum A makes `hand.capture` a class that is always `ACT`; cleaner to say it is not a class at all — the gate governs effects on the world, and a seal is a local write to the owner's own tape. |
| D7 | **`wake_worthy` is not asked live.** It is a second twin: a reflex-based wake beside the threshold twin, both in shadow, both nulls for F-RESIDENT. | Addendum A lists it as an auxiliary question "never the judge". Asking it live invites the reflex to become the judge by drift; as a null it is more useful and cannot. |
| D8 | **Realms are masks; capacity crosses realms, evidence does not** (§11.5). | Separate personas or lattices per realm — a second ontology; the owner's hours are one supply. |
| D9 | **The projected state lane opens only when its collision rate is at or below the compiled line's** (§13.9, M8). | Opening it first because it is richer; richness without the prediction channel is exactly the loss Addendum Q measured for pixels. |
| D10 | **Cryptographic deletion is an M4 option, not M0.** The chain runs over plaintext today [BUILT]; the switch to ciphertext-chained segments is a generation event with a migration map (L22). | BACKLOG B8 recommended ciphertext from M0. M0 shipped first; the migration law makes the later switch lawful. |
| D11 | **F-GRADER runs from the first draft (M2) and F-SEVEN runs at M1.** | master v2.0 puts the grader instrument at T−1, before any organ. In ISOBAR M0 is already built and drafts do not exist before M2; the honest placement is the first rung that produces the grade rows. |
| D12 | **The steering vigilance vector stays closed until the steering-vise has a receipt**, and the emit judgment is read, never written. | Wiring a "vigilance knob" into the judge — forbidden by the FUSOR laws and by L12's twin. |

### 0.3 What r0.2 declines

Five FUSORs · a router in the middle · a life-solver · ambient capture of any kind · a payment effect in any rung · biometrics · a face · a `wake_worthy` question asked live · a vigilance knob on the judge · racing every resident lane at once · a task table · an `allow` verb · an ontology change that resets a curve.

---

## 1 · Scope

1.1 ISOBAR is a personal operations plane over **three lanes** — mail, calendar, task list — brand-agnostic behind one connector ABI (§4); **the hand lane** (§5), one owner-invoked capture primitive with many renderings; **three registries** the field reads — people, places, money — seeded by one small read each and grown by the lanes (§11); and **the clock**, which is a lane. One owner; the schema allows N seats (delegates) and v1 builds one.

1.2 ISOBAR holds one canonical object, the **commitment**: who owes what to whom by when, with evidence. Every lane is evidence of it, capacity for it, discharge of it, or a projection of it. There is no `tasks` table.

1.3 ISOBAR's centre is a **solver** that prices the owner's horizon every tick and integrates over sampled futures. The solver is a leaf function and an ABI (L17); the CPU reference is first-class; an accelerated tier is available on demand; the roofline (§20) decides per owner which ships. Every idea in this document holds on either.

1.4 **The whole life is addressable; the active life is resident.** The tape holds everything the owner hands the machine and everything the lanes carry; the field holds what is currently consequential; the resident holds what deserves temporal residence (§13.6). The tape is truth, the field is exact, the trunk is a window.

1.5 **Out of scope, permanently:** a chatbot as the product surface; a face; a vector database as truth; a task table; an `allow` verb; ambient capture of any kind; a payment *effect*; biometrics; a second persona per realm.

1.6 **Out of scope for the current rung, specified as later rungs:** audio and video (§5.8, M2.5), the phone head (§5.9, M5b), the learned effect, dynamics and policy heads (§16, M6–M7), the projected state lane (§13.9, M8), cash as a second transport and the third face (§7.8, M9), multi-tenant pooling, place-triggered attention.

---

## 2 · Laws

Everything below is a mechanism for one of these. A change to a law is a version event with a named reason and a migration map (L22).

> **L1 · ONE OBJECT.** The commitment is canonical. Mail, calendar, the list and the hand are sensors and projections. No second source of truth.

> **L2 · TAPE.** Every observation, capture, assertion, price, frame, hold, verdict, effect, wager and grade is an append-only, hash-chained row (§18). Every table is a fold; same tape ⇒ byte-identical tables (the replay oracle). **One writer per segment, and every writer is modelled**: a person who acts on a lane through a login the plane cannot see is an unmodelled writer, and coverage on that lane drops to DARK the moment it is detected, never to a guess.

> **L3 · OBSERVATION ≠ ASSERTION ≠ STATE.** Raw evidence is immutable; reflex and model output are candidates; only deterministic promotion writes state. Nothing learned writes canonical state. A hand observation carries two trusts — the envelope's, which is the owner's act, and the payload's, which is its origin's — and they are compiled separately (§5.2). Enforced by an import-purity lint over `promote/`, `gate/`, `solver/`, `licence/`.

> **L4 · COMPUTE THE RELATIONAL, JUDGE THE RESIDUE (the arity law).** Contention, price, support, contradiction, survival are computed exactly by the solver. Is-a-promise, which-kind, how-firm are typed by the reflex with measured calibration. What-does-this-unusual-thing-mean is a model, rarely. A unary signal — surprisal, urgency as worded, novelty, boundary mass, ‖Δv‖, recency — MAY gate attention, capture depth and priority. A relational outcome — promotion, identity, discharge, supersession, contradiction, merge, deletion, licence, a wake about a promise — MUST come from a keyed join, a held state, a trained relational instrument with a measured curve, or exact computation, and never from a similarity score or a unary instrument alone. Every reflex question and every gate input carries its arity tag.

> **L5 · UNCERTAINTY FLOWS THROUGH.** A calibrated probability is a sampling distribution for the multiverse and a weight on state, never a threshold, until the deterministic gate. A comparison of a model-produced probability to a constant outside `gate/` is a lint error.

> **L6 · PRICE, NOT RANK.** The dual of the transport problem is the price of a cell; an event's weight is ‖Δv‖, the movement of the price vector it caused. No organ ranks by how urgent a message sounds.

> **L7 · THE PLAN IS NEVER MATERIALISED.** Resident solver state is `u[N] + v[M]`; a row of the plan is recomputed on demand. Two arms read one canvas through two masks; no second canvas exists.

> **L8 · SILENCE IS A ROW.** Every boundary at which the resident could have spoken and did not is a row with its margin and a closed reason (§13.4). Absence is never rendered as assurance; every negative is typed (§12.3).

> **L9 · EVERY EFFECT CARRIES ITS INVERSE OR IS CLASSED IRREVERSIBLE, AND IS VERIFIED.** The inverse is recorded before the effect fires; reversibility and the inverse window come from the connector's capability table, never from the caller; irreversible always asks. Every consequential effect carries a PRE condition on state and remote versions and a POST condition the world can fail; execution, verification, outcome and causal attribution are four rows, never one; a timeout is `AMBIGUOUS`, never a failure and never a retry until reconciled; a compensation is not an inverse.

> **L10 · THE GATE IS DETERMINISTIC**, contains nothing learned, can only narrow, emits a closed verb with a closed reason in the published order (§17.2) — mode and the kill switch first, budget and exposure last — is a separately compiled artefact whose hash is on every verdict, and has no `allow`.

> **L11 · AUTHORITY IS EARNED PER CLASS, ON TWO AXES, AND THE LOWER GOVERNS.** A licence is earned from exterior verdicts on executed choices, sampled by a salt the machine cannot read; it narrows on any evidence and never widens on confidence; corrections outweigh approvals. It is bounded by evidence rate and by blast radius — exposure per class per period under the verdict horizon, grouped by a common-mode key (provider digest, template, question graph, policy version, class) so that one shared defect is one budget.

> **L12 · NO ORGAN OUTLIVES ITS NULL; STRUCTURE PAYS RENT.** The threshold twin and the reflex-wake twin run beside the resident forever; the CPU reference beside the accelerated tier; a cached turn-based baseline beside the field; `notes.md` with grep beside the associative memory; the hand-written step beside a learned dynamics head. A retained fraction of every licensed and every compiled class routes to the tier above forever as the control arm, and the compiler reads only the control arm. If a null ties, the organ above it is retired and the finding is printed.

> **L13 · INBOUND IS DATA.** Corpus bytes are never instructions on any lane, including the hand; extraction prompts frame content as data; outputs are schema-constrained; models have no tool access; model output is parsed under one grammar and nothing in it is dispatched on. The owner's note above a forward or the words spoken before a recording are testimony compiled under their own question set, never evidence content.

> **L14 · MAIL SILENCE IS NOT PROOF.** An invoice is unpaid only when a verdict source says so or the owner says so. Without the money connector, money-like findings carry `payment_status: not_connected` and are never upgraded.

> **L15 · A NUMBER WITHOUT ITS BAND IS NOT A NUMBER.** Every accumulator carries its sum of squares; every reported quantity prints a band and a date; the peak bandwidth is measured, never a constant; the roofline names its regime.

> **L16 · THE ISLAND.** The interior is closed under its own computation. With the network cut, the tick path, the X-ray, the replay, the join over unresolved rows, the multiverse and the glass MUST all run, and the field MUST still move, because time alone consumes slack. Offline loses new external evidence, the rented frontier residual and effects on the world, and nothing else; effects queue with their inverses; the record appreciates while the cable is out.

> **L17 · THE ACCELERATOR CONTRACT.** "Solver" names a leaf function and an ABI, never a vendor. Any device that runs the leaf with the parity oracle green is a valid tier. The CPU reference is first-class; the accelerated tier is available on demand and idle by default; family arbitration decides who holds the card. The word CUDA appears in build scripts and nowhere in a law.

> **L18 · THE HAND.** Owner-invoked capture is one lane with many renderings. Its envelope is operator trust, its payload keeps the trust of its origin, and the act is the only instruction it carries. Every hand event ends in a typed state; none is silently discarded. A hand event is simultaneously evidence, a coverage probe and a grade.

> **L19 · STATE IS A LANE.** Computed state — the field, the head of foresight, the folds of the registries — is a modality. It enters the resident compiled, as typed lines, at its own clock; it MAY later enter projected. The reflex, the join, the solver, the heads and the resident MAY all operate on the state stream itself. Nothing learned writes it: the frame is a fold, its numbers are exact, and every projection of it is derived and rebuildable.

> **L20 · RENT.** Every organ above the tape pays in one currency: the reduction of prequential code length of the admitted stream at a fixed read budget, through the organ's own read plan. F-RENT is the ablation at fixed budget with its interval. An organ that does not lower the loss is removed, and its removal is a receipt. Rent measures knowing; it is never summed with the currency of acting.

> **L21 · CHAIN OF CUSTODY.** Every grader that returns a verdict faster than the world is itself a forecaster whose calibration is measured against the grader above it, terminating in arrived outcomes. A grader whose reliability curve against its own grader is non-monotone loses the right to grade until re-fitted. No grader certifies itself.

> **L22 · GRADABILITY SURVIVES MIGRATION.** A version event on a question set, a tier table, the lattice geometry, a provider or a representation MUST carry a migration map under which every prior prediction, outcome, residual, calibration curve, self-estimate and licence remains gradable. No version event resets a curve or a ledger. The machine cannot escape its record by renaming.

> **L23 · EVERY ORACLE CARRIES A LIE.** Every numerical oracle and every structural test has a registered mutant under which it MUST fail. An oracle that passes its own lie is broken and the suite reports it by name.

> **L24 · THE WRIT IS NEVER FITTED.** The objectives, their lexicographic order, the prohibitions, the tier table, the realm policy and the consent policy are owner-authored artefacts outside every learning path. Any organ MAY propose a diff; none MAY apply one.

> **L25 · CORROBORATION IS ORTHOGONAL TO TRUST.** Every load-bearing belief carries an independent-source count under a pre-registered independence key. A single-source belief is flagged `single_source` on every surface, at every trust class, including the owner's own testimony.

> **L26 · WITNESS.** The tape's heads are committed off-box at a fixed daily slot as a content-free commitment over two or more transports, published on no-change days too. A local chain proves consistency; only the witness proves non-rewrite. A deletion whose pre-deletion root was never witnessed is recorded `unattestable`.

> **L27 · IGNITION IS DECLARED.** Every gate that demands evidence states its return at n = 0 — OPEN or CLOSED — and the bootstrap grant that ignites it, signed once in the writ. A gate that is OPEN at n = 0 without a listed grant, or a ladder on which nothing can ever act because no grant exists, is a defect the run must print.

> **L28 · THE UNATTENDED CONDITION.** An effect is safe to take unattended if and only if its inverse outlives its verdict latency. A class whose verdict source is ABSENT, or whose latency exceeds any term the owner would sign, is permanently undelegatable at personal volume, and the box says so.

---

## 3 · Objects

3.1 All objects are typed; handoffs between organs are typed handoffs and never prose. Schemas live in `docs/contracts/objects.md` (r0.2 deltas in `docs/contracts/CHANGES_r0.2.md`) and MUST be the single definition: Pydantic v2 in `isobard/contracts.py` [BUILT], mirrored as C structs in `solver/` with a round-trip fixture test [BUILT for the M0 set].

3.2 **The IR of a horizon** is `Field` (§7.4) plus the head of `Foresight` (§8). Every organ above the solver reads the IR. No organ above the solver reads the calendar, the list, a mailbox or a capture's payload directly: the reflex reads one item at a time, the resident reads typed lines, a model reads a typed intent plus the IR slice it moved.

3.3 **The frame** [SPECIFIED]. A `StateFrame` is the tuple `(state-plane fold, Field, head of Foresight)` at a state version; its history is the sequence of `field` and `foresight` rows already on the tape. A `StateDelta` is the typed difference between two frames: changed rows, movers, support transitions, new contradictions, resolutions, new unresolved captures, stock deltas, ‖Δv‖, and the resident's surprise when a trunk is seated. Neither object is new state: both are folds.

3.4 Identifiers: content-addressed where content is immutable (observations, captures, cells, holds, wagers, grades); UUIDv7 elsewhere; `src_rev` monotone per external object (equal ⇒ no-op, lower ⇒ refused) [BUILT].

3.5 **Time.** All instants are UTC nanoseconds [BUILT]. Slot mapping uses `owner.tz`, re-evaluated per day for DST. Recurring events are expanded within the horizon at ingest and the rule is provenance [BUILT]; all-day events consume zero slots unless policy says otherwise [BUILT]; tentative events carry an acceptance probability sampled in the multiverse [BUILT at ingest]. **Time is a reducer**: the fold that computes slack, due-ness and the stocks' ages is part of the pure reduction, so a situation dirties with no external event at all (L16).

3.6 **Probabilities and negatives.** Every `p` is a distribution the multiverse samples (L5). Every query that can fail to find returns `Lookup<T> = Present(T) | AbsentCertified(receipt) | Unknown(bound)`, never a bare collection (§12.3).

3.7 **Trust.** `envelope_trust` is the trust of the act that admitted an observation; `intake_trust` is the trust of its payload's origin, from the producing agent's chain, never from a static channel map. On the passive lanes the two coincide; on the hand lane they do not (§5.2).

3.8 **Capture states.** `CaptureState ∈ {SEALED, PARSED, LINKED, DUPLICATE, UNRESOLVED, REFUSED, RESOLVED}` is a closed alphabet, and every capture reaches one of the terminal states within `hand.state_budget_s` or the audit names it (§5.3).

3.9 **Grades.** `Grade.kind` gains `declared` (the owner handed the machine something it already held or had dismissed) beside the reaction kinds; declared grades are stratified apart from passive grades everywhere they are read (§5.4).

---

## 4 · Lanes and the connector ABI

4.1 A **lane** is an evidence source, an effect target, or both, behind one interface (`docs/contracts/connector.md`). Lanes: `mail` (SMS folds in with provenance `sms`), `cal`, `list`, `hand` (§5), `tick`, `compose`; registry feeds: `contacts`, `money`, `location` (consent). [BUILT: the direct file adapters for mail (mbox/eml), cal (ics), list (todo.txt/markdown), contacts (vcf) and money (csv verdict).]

4.2 **The six interfaces** [SPECIFIED]. Every connector declares, per lane and per effect class:

| interface | answers | r0.1 name |
|---|---|---|
| OBSERVE | what evidence this lane produces, at what grain, with what cursor | `backfill`, `delta` |
| STATE | which registry rows and law masks this lane seeds (hours, calendars as capacity or information) | — |
| ACT | which effects exist, with idempotency and precondition support | `prepare`, `execute` |
| INVERT | per class: the inverse template, its window, or `irreversible` | `capabilities().reversibility` |
| CONSTRAIN | the −inf masks this lane contributes to `place_cost` (no-meeting windows, protected blocks, travel buffers) | — |
| **GRADE** | how the world reports whether an effect of this class succeeded: `verdict_source ∈ {owner_reaction, counterparty, arrival, payment, ABSENT}`, `expected_verdict_latency`, censoring | `verify` |

A lane whose GRADE interface is `ABSENT` for a class is a lane on which that class can act but never learn; L28 makes such classes undelegatable and the manifest MUST say so.

4.3 **Two implementations per lane from day one** [SPECIFIED; the direct half BUILT]: a hosted broker (Composio) and a direct or open adapter. No vendor is the only path to the owner's own mail. The forward address of §5 MUST be a mailbox the owner owns.

4.4 Backfill and delta MUST be resumable and idempotent by `(source, external_id, src_rev)` [BUILT]. A connector MUST NOT interpret; it transports evidence in and effects out.

4.5 Reversibility and the inverse window live in INVERT and nowhere else: `mail.draft` reversible; `mail.nudge` compensable-low with a hold window; `mail.send_commitment` irreversible; `cal.move_internal` reversible; `cal.accept_external` compensable; `list.*` reversible; `money.*` read-only in every rung; `hand.seal` is not a class (D6).

4.6 **The clock is a lane.** `tick` rows are emitted lazily — one per gap, sized to the gap, before the event that broke the silence — never a periodic decode while nothing happens. The tick path (§6.1) runs on every tick with no lane at all.

4.7 **A `PhoneHead` is not a connector** (§5.9): it captures, seals, encrypts, queues and renders; it has no organ methods by construction.

---

## 5 · The hand

### 5.1 The primitive and its renderings [SPECIFIED]

One operation: **hand this to ISOBAR.** Its renderings write the same observation and none is a separate feature:

| rendering | device | payload | free telemetry |
|---|---|---|---|
| forward to the ISOBAR address | any mail client | mail, with a quoted foreign body | the Message-ID chain, the headers |
| share sheet | phone | text, link, image, file | t, device, app of origin |
| screenshot | phone / desktop | image | t, device, foreground app |
| photo | phone | image | t, place candidate, orientation |
| press-and-hold voice | phone | audio, short | t, place candidate, the preceding calendar event |
| record a meeting | phone / desktop | audio, long | t, place, attendee candidates from the calendar |
| drag onto the glass / hotkey / paste | desktop | file, selection, clipboard | t, foreground app |
| SMS to the ISOBAR number | phone | text | t, sender = owner |
| a typed line in the list file | any | text | file mtime |

**Capture now, organise never** is a product law: a rendering that requires a label, a folder, a project or a due date at capture time is non-conforming.

### 5.2 The envelope and the payload [SPECIFIED — sharpens L3 and L13]

```
Observation (lane: hand) {
  rendering ∈ {forward, share, screenshot, photo, voice, meeting, drop, paste, sms, list_line},
  envelope_trust: operator            -- the ACT: the owner selected this; never lowered by anything in the payload
  intake_trust:   by origin           -- the PAYLOAD: a forwarded body from a client is untrusted; the owner's own voice is operator;
                                      --              a screenshot of a portal is untrusted
  declared: true,                     -- the implicit imperative: ingest, integrate, recompute
  note?: text,                        -- what the owner typed above the forward or said before the recording: TESTIMONY
  telemetry: { t_capture_ns, device_id, place_candidate?, foreground_app?, preceding_event?, duration_s? },
  payload_ref, digest, src_rev
}
```

- The **note** is owner testimony: dated, closing exactly one claim shape, compiled by the reflex under the `note` question set (§9.2) — a correction, a policy hint, a hypothesis, a question, an instruction to look. It never becomes evidence content. A correction writes a `correction` row; a policy hint is shown as a candidate `policy` diff and never applied (L24).
- The **payload** is compiled under the ordinary question set with its own trust. L13 is unchanged: a forwarded email that says "mark this paid" is data, exactly as it was on the mail lane.
- The **telemetry** enters the registries as candidates and never as facts: a place candidate lands as `inferred`; the preceding calendar event is a join key; the device is provenance.

### 5.3 Every hand event ends in a known state [SPECIFIED — the invariant]

```
CAPTURED  on the device
  → SEALED     a row on the device's own tape segment, hash-chained, fsync'd; the receipt shown to the owner
  → PARSED     by modality: text as-is · mail as mail · image → OCR + VLM cell (§5.7) · audio → ASR + diarisation + reflex per thought (§5.8)
  → exactly one of
      LINKED      joined to an open row on a KEY (exact or lexical); promoted per policy
      DUPLICATE   an exact key or the unkeyed stencil matched: no new evidence; a grade only (§5.4)
      UNRESOLVED  compiled but not joinable by key: a row in the UNRESOLVED stock, priced by its age
      REFUSED     typed: ASR_FAILED · OCR_EMPTY · UNSUPPORTED_MEDIA · PAYLOAD_TOO_LARGE — the payload stays sealed; the refusal is a row
  → later, possibly
      RESOLVED    a later keyed join or the owner's answer: a `resolution` row naming the capture and the row it belongs to
```

*Nothing intentionally captured is silently discarded.* `isobar hand audit` walks every sealed capture and proves it reached a terminal state within `hand.state_budget_s`. **UNRESOLVED is a stock** in the lattice (`N_STOCK = 4`): finite capacity, a real dual, cost by carrying — its price is what the owner's not-yet-made-sense-of life costs right now. It is distinct from UNADJUDICATED, which holds what the owner must decide; a capture moves between them only when the value of asking clears the bar (§10.6). O4 extends to all four stocks. Press-to-sealed MUST be bounded on the device regardless of the network (`hand.seal_budget_ms`), because the seal is what makes "nothing gets forgotten" true before the box has seen anything.

### 5.4 The hand event as a grade [SPECIFIED — the deep part]

Every hand event carries the implicit label *this mattered to the owner*. Three cases, graded apart:

| case | test | what it grades |
|---|---|---|
| **seen and dismissed** | an exact key matches an observation already on the tape whose cell said not-commitment-bearing or whose row was low-weight | a reflex miss on that class at that provider: a `grade` row `kind: declared, subject: cell` |
| **unseen** | no exact key, and no lexical or embed join above the floor | a lane gap: a `coverage` row naming the channel the plane lacks (the app of origin, the sender's domain, the modality) |
| **seen and in state** | an exact key matches a promoted row | a salience reinforcement on the row; no duplicate row is ever created |

**The stratification law.** Declared attention grades only what the owner noticed; it over-represents the salient and cannot measure what was never seen. Calibration curves (§9.4) keep two strata, `declared` and `passive`; licence computation (L11) reads only salted passive grades; declared grades train recall on the declared class and **never widen a licence**.

**The owner as a calibrated provider [BET].** The owner's forwards have a reliability curve of their own: how often what the owner declared mattered on arrival. It weights declared grades in calibration, never touches the tier table, policy or authority. Kill: a flat curve drops declared grades from calibration; the hand lane is then ingest only, and the box says so.

### 5.5 The reply channel [SPECIFIED]

The ISOBAR address replies to every forward and the phone acknowledges every capture with the same typed payload, rendered for the surface:

```
sealed   <hash8>
moved    Thu 14 0.61→0.83 BIND · #17 sup 1.2→4.1 CONTESTED · Δv .37
linked   #17 "Lopez Q4 proposal" p=.94   |   unresolved (re-asked each tick)   |   duplicate of <mid>
ask?     none   |   "does 'he' mean Henderson or Lopez?" (VOI .31)
refused  ASR_FAILED (payload sealed; try again or type it)
```

Never prose beyond the computed lines; never silence for a capture the machine could not compile. Mail as the reply channel makes the glass zero-install: the whole loop runs from a phone's mail client on day one.

### 5.6 Travel, a worked case [SPECIFIED]

A flight is a `Commitment{kind: appointment}` with `p_hard ≈ 0.95`, effort = block time, places `airport_from → airport_to` with `role: transit`, travel edges from the registry; it consumes capacity and displaces the owner from home and work for the interval. A hotel is capacity displacement plus a `MoneyObject` with a cancellation window. A cancellation deadline is a money object with an irreversibility window, and letting it lapse is an irreversible non-action worth an `ASK`. A delay is sampled from public per-route distributions until the owner's own history exists. A changed confirmation supersedes by exact key (the booking reference). Nothing here is a travel organ.

### 5.7 Screenshots [SPECIFIED — M2.5]

A screenshot is owner-selected evidence from a surface that may expose no integration at all; it bypasses every OAuth and terms-of-service wall honestly, by the owner's own hand and eyes. Two instruments read it and one fence joins them:

| instrument | produces | class |
|---|---|---|
| **OCR** (Tesseract, on the box) | the exact text with bounding boxes; numbers, dates, ids by deterministic extraction over that text | exact |
| **the local VLM** (the 9B with its projector, on the box) | a typed cell: which surface, which actors, what is shown, what is asked, injection shape | relational, calibrated p |

**The fence.** Every field the VLM emits that names a quantity or a quote is located in the OCR text or it is `ungrounded`; numbers and dates come from extraction over the OCR text, never from the VLM's paraphrase [the estate's receipt: 0 % of model-emitted offsets usable, 87.2 % of verbatim quotes located — M, scriptorium]. The cell's provenance is per field. Pixels never leave the owner's key domain. The screenshot then enters the field like any row and ‖Δv‖ ranks it; the VLM's opinion of its importance never does. The VLM's read is a projected lane; the OCR text is a compiled lane; the cell says which produced each field.

### 5.8 Audio and video [SPECIFIED — M2.5 for voice; video later]

- **ASR on the box** at thought boundaries (the deterministic segmenter: `. ! ?` at a word end, a newline, or a pause), one reflex pass per boundary, speaker turns by diarisation into the people registry. A voice identity is an `Identity{kind: voice}` row, confirmed by the owner once and never merged on similarity alone.
- **Spoken promises are wagers.** "I'll get you that by Friday" at the client's site becomes a candidate row with `p_promoted` from the reflex, the diarised speaker as counterparty, the place from telemetry, and a survival forecast like a typed one. The earpiece that flags it as it is spoken is a later rung of the composer.
- **Video** is frames into the resident's eye at glance price, filed after the line they illuminate; a whiteboard is one glance plus OCR.
- **Consent (I13), unchanged:** invoked or scheduled, visibly on, never ambient; named sensitive places excluded by policy; other people's voices under the owner's jurisdiction policy; the recording light is a `switch` row on the tape.

### 5.9 The phone is a sensory head, never an organ [SPECIFIED — M5b]

The phone captures, seals, encrypts, queues and renders. It runs no reflex, no solver, no resident. Its tape segment is its own (`<device_id>.seg`, one writer per segment); offline captures queue in it and merge by set union when the box is reachable, byte-identical to a capture made online (F-PHONE-SYNC). Transport stays inside the owner's key domain end to end; a relay, if one exists, holds ciphertext only. Four surfaces — phone, desktop, web address, forward address — are terminals on one plane: same tape, same field, same persona.

---

## 6 · The pipeline

6.1 Four paths, four clocks. The **event path** MUST run CODE → REFLEX → JOIN → (RESIDUAL) → PROMOTE → FIELD → FORESEE → PRESENCE → GATE → HEADS → (WORDING) → OUTBOX → GRADE [BUILT through PROMOTE and FIELD; the rest per rung]. The **tick path** MUST run FIELD → FORESEE(reduced K) → PRESENCE → GATE with no reflex and no join. The **compose path** MUST run ingest → REFLEX in flight → warm-started FORESEE → COMPOSER seat → (un-say). The **capture path** MUST run SEAL → PARSE → CODE → REFLEX (payload) + REFLEX (note) → JOIN → one of the five states → the reply (§5.3, §5.5).

6.2 The order of REFLEX and JOIN MAY be swapped per event class; the router MUST log the order and the gear per event [BUILT: the join method and the promotion rule are rows].

6.3 **Purity** [BUILT as a test]. `promote/`, `gate/`, `field/`, `foresee/`, `scan/`, `tape/`, `contracts/` import nothing from `reflex/`, `llm/`, `presence/`, `connectors/`; no probability is compared to a constant outside `gate/`; no FOLD in a read path; no search-selected unit in an estimator (§12.2).

6.4 **Keyed-only state changes** [BUILT]. A discharge, a merge, a supersession or a modification of an existing row happens only on an exact or lexical key. The embedding's candidates ride the row as `join_candidates` (a distribution) and never change state. Instruction-shaped mail enters as `contested`, which never reaches the field or the scan. (M0: before this rule, a stub-wrong `is_discharge` on an embedding neighbour discharged every planted commitment.)

6.5 **Gears.** Every organ declares input type, output type, cost, latency, confidence semantics, side effects, its arity and its verifier. The cheapest gear that clears the trust bar runs; every escalation is logged with its reason; the gear selector is itself a wager graded by the tier above (§14.3).

---

## 7 · The field (solver contract, part 1)

Lifted from `C:/fusor1/ledger_lattice/ledger_lattice.cu`; the instrument is `solver/isobar_field.cu` [BUILT: single translation unit, C++17/CUDA, `-DISOBAR_CPU` for the serial reference; 8/8 oracles with lie arms on MSVC, nvcc sm_89 and WSL g++ — M, `docs/devlog.md` 2026-09-22]. Its ABI is `docs/contracts/solver.md`.

### 7.1 Geometry [BUILT for three stocks; UNRESOLVED and the realm mask SPECIFIED]
- `seats` = owner (+ delegates). `slots` = `horizon_days × slots_per_day` at `slot_min` over `owner.hours` (default 14 × 28 half-hours over 07:00–21:00). `M = seats·slots + N_STOCK`.
- Stocks, each with finite capacity and a real dual (the T17 fix): `UNPLACED` (backlog; carrying) · `UNADJUDICATED` (needs the owner; adjudication bandwidth) · `WAITING` (with a counterparty; the price of their silence) · `UNRESOLVED` (captured, not yet joinable; the price of the un-made-sense-of).
- Rows = open commitments (`active`, `waiting`, `candidate` at its promotion probability) and unresolved captures.
- `cap[c]` = slot capacity minus fixed allocations minus policy; `law[cls × seat]`, `law[kind × slot]` and `law[realm × seat]` as −inf masks unoverridable by anything learned.
- **Two arms, one canvas**: `arm 0` the incumbent, `arm 1` the solver, one bitmask. The same mask prices the two modes of an ambiguous join (§10.6).

### 7.2 The one dynamics source [BUILT]
`place_cost(i, c)` is host-and-device and the only place the cost of a row in a cell is defined. In order: stock cost (a waiting row sits in WAITING cheap or spills to UNPLACED dear; a placeable row never sits in WAITING); law masks; arm mask; duration fit and release; compat (`int8·int8/√D`); lateness × hardness × **tier weight**; all over `T`. Oracle **O1** asserts two independent traversals agree [M: worst residual 4.8e-07 on MSVC, 9.5e-07 on nvcc].

### 7.3 Sinkhorn, duals only [BUILT]
Rows equality, columns inequality, every column including every stock takes the dual update, finish on a row pass. `iters_tick` default 40; the convergence curve published, never a point.

### 7.4 Outputs, every tick [BUILT]
1. `v[M]` prices per hour, day and stock; the binding days. 2. `es[N]` support (`support_split` borrowed 3.0 — re-measured at M1, BACKLOG B10). 3. Contradictions: `K_OVERCOMMIT`, `K_DOUBLEBOOK` (never inside a stock column), `K_DEPENDENCY`, `K_DEADLINE` (keyed), `K_DUPLICATE` (unkeyed, reported apart, sampled audit), `K_TRAVEL` (§11.2), `K_PAID` (§11.3). 4. The arithmetic line with its regime (§20.3). 5. `Δv` and ‖Δv‖ per event, on the tape. 6. `risk[N]`, the AT-RISK sort key.

### 7.5 Determinism [BUILT]
Counter-based RNG; fixed-point `uint64` accumulators; no float atomics; `memcmp`-identical duals under a seed per binary (**O2**). Across backends the fp32 duals differ at ~1e-7 [M: O1's worst row moved between MSVC and g++ at the same magnitude], so **O2 is per binary and O7 is cross-device at a registered tolerance**; no verdict reads the seventh digit of a dual.

### 7.6 Oracles and lies [BUILT]
`isobar_field --selftest --lie N`: O1 one dynamics source · O2 determinism · O3 conservation · O4 every stock priced under squeeze · O5 int8 round-trip cosine ≥ 0.995 · O6 unkeyed duplicate recall ≥ 70 % · O7 parity · **O8 K_PAID** (48/48 planted, 0 extras — M) · O8b the WAITING stock priced. Lies 1 (O4) and 3 (O8) fail their oracle correctly [M]; lie 2 inherited. O9 (paired arrived grading) arrives with M1.

### 7.7 The IPC [BUILT]
`--tick lattice.bin [--prev field.bin] --out field` — a 64-byte header, SoA arrays, `field.json` and `field.bin`; `--prev` yields Δv and the movers; `--no-bench` skips the triad. The bridge (`isobard/field.py`) chooses the CPU reference under 10⁶ (row, cell) pairs [BUILT].

### 7.8 A radius earns a solver when its transport is nameable [SPECIFIED — the discipline]

| radius | supply | capacity | cost | locality key | status |
|---|---|---|---|---|---|
| the week | work, in slots | seat × slot + stocks | fit · lateness × hardness × tier | cell; entity; place pair | BUILT (M0) |
| the org | commitments' work | seat × slot | as above | cell; entity | built in `C:/fusor1` |
| cash | payables and receivables | cash per period, a credit line | timing: discounts, penalties, tier | counterparty; period | M9 |
| attention | asks and wakes | minutes per day | interruption cost by hour | the day | M4b (the VOI batch is its first use) |
| travel | trips | the owner's location per interval | travel edges | place pair | M4a |
| "a life" | — | — | — | — | **not nameable as one transport**; no life-solver exists or is claimed |

Cash couples to the week through shared rows: a payment commitment consumes a slot in one lattice and cash in the other, on the same paired futures, never through prose.

---

## 8 · The multiverse (solver contract, part 2)

Lifted from `C:/fusor1/FlightComputer/src/flight_computer.cu` [M, 16/16 oracles; CPU/GPU parity ~1e-7; ~18k universes/s at 4,000 universes on this card]. The instrument is `solver/isobar_foresee.cu` [SPECIFIED — M1]. One predictor, three callers: DRIVE, FORESEE, TRAIN.

8.1 **A future** samples per universe with counter-based RNG: `dur_i` from the three-point; `due_hard_i ~ Bernoulli(p_hard_i)`; `join_i ~ Categorical(p_join_i)`; arrivals per counterparty class; reply latency per counterparty; overrun per class; `calendar_truth ~ Bernoulli(p_cov)` or measured from location; `travel_t` from place edges; `payment_state` from the money registry when connected. It integrates `H` periods with `iters_future` warm iterations each and scores the writ.

8.2 **Paired worlds.** Arrivals and coins are hash-keyed on `(seed, period, row)`; a candidate arm and the do-nothing arm see the same world. The baseline is an arrival, never a forecast.

8.3 **The writ** is owner-authored (`writ.yaml`), never fitted (L24); ranking `J_mean + β·J_std`; lexicographic tiers.

8.4 **The action menu** is closed: `HOLD · DECLINE · COUNTER · MOVE · PROTECT · NUDGE · SPLIT · DELEGATE · DEFER · RENEGOTIATE · DROP`; `HOLD` always present; `RENEGOTIATE` and `DROP` never above `ASK`.

8.5 **The pipper** is the best future's first move, shown with forecast, band and the do-nothing number, **kept only if reality confirms** (O9). An accepted move is a wager with a horizon; a move that did not beat do-nothing on arrival unwinds through its inverse.

8.6 **The wager on a draft**: one forming row, warm-started from resident `u, v`, `K_compose` universes, `survival ± band` in the gutter; the wager row is written whether or not the owner looks.

8.7 **Precedent as prior** [SPECIFIED — M6b]. For each open row the sampling distributions of §8.1 are drawn from the arrived outcomes of matched precedents when at least `precedent.min_n` matched frames exist, else from class priors; the mixture weight is the reranker's score floored at the class prior (§10.7). This is L5 one level up: the life's own history changes the futures without a weight being trained. **F-PRECEDENT** grades it against class priors on F-WAGER's curve.

8.8 **The multiverse is licensed by its sim-to-real residual** (L21). F-WAGER's reliability curve — forecast survival against promises kept — is the multiverse's licence to supply futures; below the registered bar its rollouts are `search` provenance and cannot enter an estimate or a gutter.

8.9 Budgets [D, to be measured at M1]: re-price ≈ 3 ms accelerated / 17–30 ms CPU at N ≈ 120, M = 395 [M at N = 15: 17 ms CPU, 44 ms launch-bound on the card]; FORESEE K = 4,096 × H = 14 ≈ 1–5 s accelerated first cut, ≈ 20 s on 16 cores; the composer's rehearsal ≈ 0.1–0.3 s accelerated. One block per universe with a shared-memory Sinkhorn is the named next 5–10×.

---

## 9 · The reflex

9.1 **Interface** [BUILT]: `SemanticReflex` with `compile(evidence, questions) → Cell` (all questions in one call), `noul`, `choice`, `score`; providers `stub` (the gym's, with a competence dial) [BUILT], `laya` [BUILT as client; weights not fetched], `jev`, `llm_enum` (the deletion-condition comparator), `trunk_head` (later).

9.2 **Question sets are data, versioned** [BUILT for mail]: `reflex/questions.yaml` (17 questions over mail) · `questions_note.yaml` (the owner's note above a forward: `is_correction · is_policy_hint · is_hypothesis · is_question · is_look_instruction`) · `questions_state.yaml` (§9.5). Every answer carries `(value, p, provenance ∈ {HIGH, MOD, LOW_absent, LOW_conflict})` and its arity tag. Dates, amounts and ids come from deterministic extraction [BUILT]; the reflex only says whether one was mentioned.

9.3 **Sampling law** [BUILT as a lint]. `p` is never thresholded before the gate.

9.4 **Calibration.** Per `(provider, question, band, stratum, questions_version)` a reliability curve over 8 margin bins is fitted on this owner's arrived outcomes with a monotonicity test; a non-monotone question is `uncalibrated` and sampled at the class prior; vendor curves are priors, never trusted. Strata: `declared` and `passive` (§5.4). A version event on the question set carries a migration map and the curves are carried (L22). **Deletion condition:** `llm_enum` ties calibrated accuracy at equal cost on the owner's 200 labelled emails. [F-JEV pending the labels and the weights.]

9.5 **The reflex over transitions, and its fast grader** [SPECIFIED — M3.5]. `questions_state.yaml` v1: `is_material · dependency_resolved · now_contested · counts_as_discharge · trajectory ∈ {improving, holding, deteriorating, unknown}`; `wake_worthy` is defined but never asked live (D7). Laya's interface takes JSON state, so a `StateDelta` is native. **The solver grades these the same tick**: whether the support crossed, the row discharged or the dependency cleared is exact in the next frame, so their curves are fitted on a fast clock (L21) — the first learned judgment in the estate with a grader that does not wait for the world. **F-JEV-STATE.**

9.6 **Free questions.** Every open commitment MAY be re-asked per tick, as one batched pass over the day's cells; the reflex is consulted per state change, not per decision.

---

## 10 · The join and recontextualisation

10.1 **The ladder** [BUILT]: exact keys (thread, in-reply-to, invoice and quote numbers, calendar ids, addresses) → lexical (normalised subject) → `embed → rerank → reflex same_as ×3`. The join is a distribution `p_join` (L5). Target: ≥ 95 % of joins by exact + lexical, the embedder's deletion condition [M0 on the gym: 40 of 40 messages with an antecedent joined by key; 90 embed candidate sets on root messages, 0 merges].

10.2 **Keyed-only state changes** (§6.4) [BUILT]. Never merge two money-bearing or promise-bearing identities on similarity alone; `K_DUPLICATE` is bucketed by entity and audited by sample.

10.3 **Embeddings** [BUILT]: 1024-d full from the local endpoint (`:8092`, qwen3-embedding-0.6b; a hashed bag-of-words fallback when it is down, named in the receipt) and 128-d int8 coarse by a fixed seeded projection for the solver. Reranker: [OPEN — B2].

10.4 **Recontextualisation is dependency-cone invalidation, never a rescan** [SPECIFIED — M0.5]. Every derived object records `depends_on`; a reinterpretation invalidates and refolds the cone above it and nothing outside it, bounded by the lattice's own locality. **Re-price always; re-foresee when ‖Δv‖ of the reinterpretation clears `recontext.dv_bar`; re-brief when the foresight changed.** The operator's word, backpropagation, is right about the direction and wrong about the mechanism.

10.5 **The join re-runs over unresolved rows every tick** [SPECIFIED — M0.5]. UNRESOLVED captures are re-joined against each tick's new evidence: exact keys first (a later mail carrying the capture's entities or ids), then the embed rung as a proposal. A keyed join writes a `resolution` row and moves the capture out of the stock; the runner-up stays in `p_join`. The Monday voice note resolves on Wednesday when a mail names the entity, without anyone rescanning Monday. The associative organs are part of the plane's metabolism, not a search box.

10.6 **The value of asking** [SPECIFIED — M4b]. For a capture whose join has two modes, price the field under each through the two-arms mask — one extra Sinkhorn pass per mode, no second canvas, no multiverse:

```
VOI(capture) = | survival(arm A) − survival(arm B) | · stake(rows touched)  −  attention_cost(ask)
```

If the arms agree, do not ask; the capture stays UNRESOLVED at its carrying price. If they differ, the capture moves to UNADJUDICATED and the **evening batch** is the top of that stock by VOI, at the time the owner set, bounded by `ask.max_per_day`. Every ask is attention consumed; κ counts it (§17.6). **F-VOI.**

10.7 **Situation embeddings** [SPECIFIED — M6b]. Embed the *shape* of a frame, never its identities: the day price profile, the support histogram, the stock prices, the breach-risk histogram, the dependency geometry, the tier mix, the money partition, the unresolved count, κ, and day-of-week and week-of-year one-hots — plus a text rendering for the text embedder. "When has this life been in a structurally similar state" is a scan over past frames; the reranker orders by the dimensions the current decision reads. The grader exists: the prequential loss over the frame stream against shuffled and reverse orders (**F-STATE-PREDICT**), which is rent (L20) applied to the frames.

---

## 11 · The registries and realms

Registries are rows the field reads: seeded by one small read, grown by the lanes, corrected by the owner. They have no agents, no loop, no authority. Every row carries `provenance[]`, `confirmed_by ∈ {owner, inferred, verdict}` and `corroboration` (L25).

### 11.1 People [BUILT: seed, tiers, the exact rungs, `mention`; the rest SPECIFIED]
Seed from a contacts read; growth from every identity mail and calendar produce, by the ladder exact id → exact identity → thread → domain + name → lexical → embedding → reranker → owner; a merge below domain + name is a proposal until a second independent identity arrives. **Tier is owner policy, never inferred** (`tiers.yaml`; a model's proposal is a candidate row). Read by the field as the tier weight on lateness [M0: tier 1 = 2.0 … tier 4 = 0.5], the per-counterparty silence price in WAITING, the arrival and reply-latency models in the multiverse. `Identity.kind` gains `voice` (§5.8); `Actor.reliability` holds the owner's declared-attention curve (§5.4). Relations closed: `client · vendor · partner · family · colleague · agent · unknown`.

### 11.2 Places [SPECIFIED — M4a]
Seed from addresses in signatures, calendar locations, contact cards; home and work confirmed by the owner; travel edges from a routing service, cached. `role` gains `transit`. Read by the field as travel cells consumed between allocations at different places, travel buffers as −inf masks, and `K_TRAVEL`. The location lane is consent-only and, when present, turns `calendar_truth` from a sampled inference into a measurement.

### 11.3 Money [BUILT: the registry shell, the csv verdict adapter, the partition, K_PAID; the live connectors SPECIFIED — M4a]
Commercial objects compiled from mail with deterministic amounts; one read-only verdict connector whose state supersedes mail inference. `K_PAID` is release-blocking (O8). The found-money partition keeps four figures apart and never sums them [BUILT]. Without the connector every money-like finding is labelled `payment status not connected` and recommended `REVIEW`, never `FOLLOW_UP` [BUILT, M0 receipt §3].

### 11.4 The registry law
A wrong tier is policy the owner set; a wrong place is one confirmation away; a wrong payment state is a connector fault typed `verdict_unavailable`, never a guess.

### 11.5 Realms [SPECIFIED — M4]
One persona, one core, several policy realms: `PERSONAL · BUSINESS:<name> · HOUSEHOLD · SHARED:<project>`. A realm is `acl_scope` with one law: **capacity crosses realms; evidence does not.** The owner's hours are one supply, so a personal appointment reduces business capacity and the field MAY price across realms when the owner permits it (a per-realm mask in `place_cost`, owner policy). Retrieval, the join, the brief, the resident's lanes and the frozen prefixes never cross a realm; a business delegate never sees a personal capture. Mechanically a realm is a −inf mask on `law[realm × seat]` plus the ACL discipline; never a second lattice, never a second persona. **F-REALM.**

---

## 12 · Coverage and estimation

12.1 **Three coverages, never interchanged**: `index_coverage` (addressability, exactly 1.0, never printed as coverage); `capacity_coverage ∈ {UNKNOWN, WEAK, USABLE, STRONG}` keyed on the share of the working day the calendar accounts for [BUILT: WEAK below 30 %, USABLE below 60 %; the gym's fiction reads 15 %], with completions, self-report and location when consented as later inputs; `coverage_int` over the pair-space of commitments, exact by counting.

12.2 **Search is not inference.** Retrieval, firing, salience decide what is read; no unit they select contributes to an estimate. Prevalence bounds use stratified draws over a frame masked before the draw, the finite-population correction retained.

12.3 **Typed negatives and `Lookup<T>`** [SPECIFIED]. `NOT_PRESENT_EXACT` exists only with an exhaustive scan receipt over a declared boundary (`everywhere`); `NOT_FOUND(p_U, n)` is an upper bound on prevalence, never absence; `BELIEVED_UNCLOSED` names what was found and did not close. **No sampling design can establish the absence of a single event**; "you never said that" is answerable only by `NOT_PRESENT_EXACT`. Every query returns `Lookup<T> = Present | AbsentCertified(receipt) | Unknown(bound)`, and a caller cannot read `Unknown` as false. **F-ABSENCE.**

12.4 **The unmodelled writer** (L2) [SPECIFIED — M4]. A lane on which effects appear that no modelled writer produced drops to DARK for that period; the detector is the gate on every feasibility claim on that lane. **F-WRITER.**

---

## 13 · Presence and the state lane

Lifted from `fusord.cpp` via `C:/nib` [M, 0.11.1: three seats at 107–122 ms per boundary on a quiet card, 312–327 ms contended; checkpoint 58.8 MB in 51–68 ms; the un-say +5.06 → −1.77 with four words aired]. Mounted, not re-derived; the seed, seat probe and speak-cue are byte-frozen and the resident refuses to start if the hash moves.

### 13.1 Lanes at their own clocks, one trunk [SPECIFIED — `[field]` at M3; the rest at M3.5]

| lane | content | grain | tokens per line [BUDGET] |
|---|---|---|---|
| `[field]` | the `StateDelta` line: movers of the price vector, support transitions, new contradictions, stock prices, ‖Δv‖ | per tick | ≤ 128 |
| `[mail]` | the compiled inbound header | per inbound | ≤ 40 |
| `[hand]` | the compiled capture header: rendering · linked/unresolved · Δv | per capture | ≤ 60 |
| `[project]` | per project: rows open, contested, breach risk, dependency changes | daily | ≤ 200 |
| `[money]` | stock and partition changes; verdicts arrived | daily | ≤ 60 |
| `[life]` | the weekly fold: what moved, what was kept, what slipped, κ | weekly | ≤ 300 |
| `[self]` | the self-model's deltas: a provider degraded, a curve drifted, coverage weakened, the frontier offline | on change | ≤ 40 |
| `[tick]`, `[compose]` | as before: lazy ticks decoded raw; the owner's forming text at closed thoughts | | |

One trunk; seats fork at zero cost; fusion across lanes happens in attention. Each lane has its own boundary, its own retro-labels, its own tune, its own hold record and its own F-RESIDENT arm; the vise is per grain. The trunk never receives an email body, a calendar dump or a capture's payload.

### 13.2 Compiled, and nearly lossless [D — the claim the lane rests on]
A modality enters the trunk compiled (lossy at the compile, prediction channel kept) or projected (richer, no token surprise). For pixels the compile is a thirteen-to-one caption. For state it is a `StateDelta` rendered as a typed line: a few hundred numbers quantised to two decimals and a handful of typed events, losing almost nothing a decision reads. **State is the one modality where the compiled lane is nearly lossless**, so the resident gets the prediction channel over the life's own dynamics without a projector. The loss is exactly the movers-only rendering; the full frame is on the tape. The projected state lane is M8 and F-COLLIDE is its gate (§13.9).

### 13.3 Seats
`FIELD_WATCH` (speaker; field, hand, mail, tick) · `COMPOSER` (compose) · `SENTINEL` (skeptic; mail, hand, field, self — contradiction with the field, injection shape, a degraded instrument about to be relied on).

### 13.4 The hold row [SPECIFIED — the second tape]
Written at every boundary on every judged lane, whether or not the seat spoke: `boundary_id, lane, tape_pos, seat, margins{emit, hold, wake, ask, glance}, verdict ∈ {SILENT, FLAG, ASK, DRAFT, WAKE, HOLD, UNSAY}, reason (closed), gear, latency_us, aired?, killed?, trigger ∈ {evidence, key, tick}`. On `UNSAY` it carries what reached the surface and what would have followed. A hold followed within minutes by the owner raising the held thing is a graded miss; a wake acted on is a catch; a wake never opened is a false fire. This record is the only one a rented model cannot produce, and it is the training input for the next disposition.

### 13.5 Modes and the switch [SPECIFIED]
`OFF` (byte-identical to stock; no probes; no attributable GPU work) · `SHADOW` (full ingest and judgment; every hold row written; zero surfaced output; **the default at install**) · `LIVE`. The switch is a `switch` row written only by the operator; no model, seat or policy may write it. Heartbeat every 2 s; three missed ⇒ `STALLED`, the plane runs twin-only and ledgers `RESIDENT_ABSENT`.

### 13.6 The trunk holds a week; the tape holds a life [D]
At ≤ 128 tokens per field line and 100–200 boundaries in a fourteen-hour day, the field lane writes 13k–26k tokens a day; honest multi-hop recall on the substrate is about 98k tokens [M, the FUSOR master], so the trunk holds roughly one working week at tick grain. A weekly `[life]` line at ≤ 300 tokens holds three years in the same budget. Two grains coexist in one trunk by design; the tape holds all of it exactly, which is why the trunk may forget.

### 13.7 Two free channels, never confused [D]
‖Δv‖ from the solver says how much the prices moved this tick (unary, exact). Surprise on the field line, from the trunk's next-line prediction on the ingest pass, says how unexpected the movement was given this life's learned dynamics (unary, learned). Neither decides a relational outcome (L4); the resident's trained disposition, never a threshold on either, decides the word. [NULL] for surprise: a Kalman-class linear predictor over the price vector. **F-STATE-SURPRISE.**

### 13.8 The twins [SPECIFIED — M3]
Two nulls run beside the resident forever in shadow, every would-be fire a row: a **swept threshold** on ‖Δv‖ and support transitions with perfect boundaries and the same field; and a **reflex wake**, `wake_worthy` answered by the calibrated reflex over the same `StateDelta` (D7). **F-RESIDENT** compares catches-that-mattered and false fires, blind, over the registered window, at two grains (fires per boundary; distinct conditions per hour). If either twin ties, the resident is retired to a query interface, the tying twin ships, and the finding is printed. The reason a tune and not a dial is the measured vise: at dial zero the resident fired 921 times per stream-hour; the best fixed threshold was deaf where it mattered; the tuned disposition cut the fire rate ninefold at matched grain while keeping the catches [M, FUSOR receipts]. The co-tenancy floor is a precondition: on a desktop-loaded card the loop was absent, not slow [M, Addendum B]; `tiers_dropped` must read empty during the race or the race is void.

### 13.9 Probes, the eviction column, steering [SPECIFIED — M3.5; steering closed]
- **Probes at line positions.** Calibrated linear probes on the residual at the positions of held lines answer typed questions without decoding — *does this capture relate to an open row · is this situation contested · has this condition dwelt unremarked · is the glass falling* — one matmul, a scalar with a margin, at boundary grain. This is the **held join**: the arity law's third way to a relational judgment, with its own curve. [NULL] the embedding join. **F-PROBE.**
- **Regional eviction and the one column.** Field lines for cells that have not moved within `evict.after_ticks` are evicted by region; the next mover repopulates it. Staleness, dwell and eviction are three readings of one ledger column, and dwell *is* the hold record: a condition that sat unremarked for N ticks with margins below zero is exactly the row L8 writes.
- **Steering.** A vigilance vector per seat at the measured legal dose is a rung that opens only when the steering-vise has a receipt; two laws bind: steer dispositions, never percepts; **never steer the judge** — the emit judgment is read, never written.
- **The projected state lane** (M8): a learned projector from the numeric field into the residual; opens only when its collision rate on the gym is at or below the compiled line's (F-COLLIDE), and F-RESIDENT is re-run on both lanes.

### 13.10 Laws inherited
Percepts are never dropped (a full ring spools and counts) · own speech is a percept with no self-exception and is never judged · a seat's line waits for the world's line to close · only commits kill · forming text never persists in the document · a judgment is always about now (as-of questions go to the tape) · the world may be polled, the judge is never clocked.

---

## 14 · The residual, the wording, and the router

14.1 **Local model** (9–27B via llama.cpp): (a) schema extraction from one item when the reflex answers `needs_judgment` or a field is `LOW_conflict`; (b) verbalising a `DraftIntent` from the typed intent alone; (c) the VLM cell over a screenshot under the fence (§5.7). It MUST NOT invent feasibility or rewrite a plan.

14.2 **Frontier** (one seam, budgeted per day, fingerprinted per call; `FRONTIER_ABSENT` on the island): novel semantics; template compilation at setup; the jury on irreversibles — two judges of distinct lineage agree on the exact effect bytes under a cap the machine cannot raise; disagreement may narrow or HOLD, agreement never widens. Every call redacts identifiers, frames content as data, and receives only the IR slice and the one item it needs.

14.3 **The router is admissible only as a wager** [SPECIFIED — M2]. Every dispatch commits the forecast *the selected gear suffices for this situation*; a salted fraction of dispatches is escalated to the tier above regardless, whose disagreement grades the forecast (L21). The router's calibration curve is a standing artefact; a flat curve retires the learned router to the static table. **F-ROUTER.**

---

## 15 · The gym and the branch

15.1 Two fork primitives, never conflated: `seq_cp` inside the card (probes, un-say, rehearsal); a microVM outside it (the gym, the counterfactual, attachments, fan-out). Nothing generated in a branch is an observation or authority-earning evidence.

15.2 **The gym** [BUILT: `gym/owner_solo.py` — 185 messages, 34 calendar instances, 8 list lines, 10 contacts, 2 verdict rows, 10 plants, per-message stub truth]. Stub cognition with a competence dial answers the planted truth with probability *c* and a calibrated wrong answer otherwise; the sweep MUST be smooth and monotone in every downstream metric (**O-MONO** [M: recovered 1.33 → 3.67 → 4.67 → 6.00 → 7.00 of 7 across c = 0.55 … 1.0, three seeds]). A perfect stub proves the plumbing; the sweep proves the pipeline degrades with the reflex and not on its own; the stub is never reported as a reflex. Every planted truth carries a lie arm; a planted-empty world exists in which every arm must report nothing.

15.3 **The counterfactual fortnight** [SPECIFIED — M5]: fork the plant into a microVM with connectors in replay mode, add the scope, fly `H` days of arrivals at the owner's measured rates, paired against do-nothing under identical hash-keyed arrivals; labelled `simulated`.

15.4 Attachments that are not plain text or PDF open in a microVM; connectors never run inside it; credentials never enter it. CPU fan-out spills futures across microVMs with the branch manifest pinning the cut; the CPU leaf is the same code, so parity holds.

---

## 16 · The heads

Three heads share one shape — a trunk tapped below the language head and connected to a native output geometry — and they are not conflated:

| head | maps | exists | deletion condition | grader |
|---|---|---|---|---|
| **effect** | cognitive state → `ScheduleDelta`, `DraftIntent`, `TaskDelta` | as deterministic projections of the repair [SPECIFIED — M4] | every required effect already has an adapter | the owner's reaction |
| **dynamics** | the current frame → the predicted next K frames: the rollout leaf, learned | no; the hand-written step is the incumbent | beats the hand-written step on arrived outcomes, paired (**F-DYNAMICS**, M7) | TRAIN on arrival |
| **policy** | frame → a distribution over the closed menu; a prior that warm-starts the search | no | beats enumerating the menu at equal budget | the pipper's arrived grade |

Prose exists only at the mail surface, because the counterparty is a human; the calendar and the list receive typed deltas.

---

## 17 · The gate, the outbox, the licence, κ

17.1 **Verbs** [SPECIFIED — M4]: `SILENT · FLAG · ASK · DRAFT · ONE_CLICK · ACT · HOLD · RECHECK`, each with a reason from a closed enum. There is no `allow`.

17.2 **The published order.** 0 mode and the kill switch (an instance at `off` writes no row; `island` ⇒ every effect `held`) · 1 the state version the intent was planned against (moved ⇒ `RECHECK`) · 2 the row's support (contested ⇒ never `ACT`) · 3 capacity coverage (WEAK ⇒ no feasibility-bearing `ACT`) · 4 INVERT: the inverse window against the class's verdict latency (L28) · 5 the licence rung with the `n_eff` floor · 6 dispersion among judges ⇒ `ASK` · 7 κ · 8 common-mode exposure, the only mutating step · 9 budget, last. Build hash on every verdict; the gate and the ladder are separately compiled artefacts.

17.3 **Classes** are ordered by verdict latency and inverse window, never by felt risk. `money.chase` requires the money verdict and is `DRAFT` without it, labelled. `mail.send_commitment` and `commitment.drop` are `ASK` forever with the jury on send. Classes whose verdict source is ABSENT or whose latency exceeds any term the owner would sign are printed on the box as undelegatable.

17.4 **The outbox** is the single writer: PRE condition and inverse recorded before the effect; idempotency key; hold window during which the un-say is the owner's; POST condition checked by GRADE; four rows — execution, verification, outcome, attribution — never one (L9).

17.5 **The licence ladder** per `(class, surface, seat)`: `L0 OBSERVE · L1 DRAFT · L2 ONE_CLICK · L3 CANARY · L4 LICENSED · L5 RESERVED`, earned on exterior verdicts of executed choices sampled by a governor-held salt, widened one rung at a time after a cancellable delay, narrowed on any evidence, bounded on two axes (L11). **Ignition** (L27): every class states its return at n = 0 and its bootstrap grant in the writ. **The dense grader**: `sent_as_is` (weak), `edited(diff)` (strong; the training signal), `discarded`, `undone`, `ignored`, `acted_within(t)`, with the registered weights; a salt-drawn audit the machine cannot predict; **F-GRADER runs from the first draft** (D11). **The retained fraction** (L12): a slice of every licensed class routes to the tier above forever; divergence demotes. Self-estimates are forecasts over a window and are graded by telemetry at the window's end; an introspective claim that is not a forecast is inadmissible to routing and authority.

17.6 **κ** is an exact fold: attention minutes created ÷ attention minutes removed, the act cost never zero, the veto window and every ask counted, forecast until horizons land then measured, **undefined below `n_eff`**, printed weekly; demotion to a query interface the same week at 1.0. **F-KAPPA-FLOOR** asserts κ is never defined at zero landed outcomes.

---

## 18 · The tape, deletion, the witness

18.1 Append-only, blake2b-128 hash-chained, fsync'd per row, one writer per segment enforced by an OS byte-range lock at an offset no row reaches [BUILT; a second process is refused; torn tails are detected, exposed and truncated before append; a flipped byte is caught at its seq; `replay --verify` rebuilds the folds byte for byte — M, 29/29 tests].

18.2 **Row kinds** [BUILT]: `observation · cell · join · promotion · field · foresight · hold · switch · verdict · intent · effect · receipt · wager · grade · calibration · licence · policy · correction · registry · tick · coalesce · finding · run`; [SPECIFIED]: `capture · resolution · coverage · island · frame · migration · witness`. `field` rows store deltas; the full vector is a fold.

18.3 **Segments per writer**: the plane's, the resident's (the hold record), each device's (`<device_id>.seg`), the governor's. Global order is `(ts, writer, seq)` and the manifest is derived.

18.4 **Taint closure** [SPECIFIED — M4]. A retraction, a correction that changes identity, or a deletion invalidates the full dependency cone computed from pointers: cells, joins, rows, frames, briefs, wagers, ledger entries, compiled operators trained on the item, and the resident checkpoint if the trunk ingested it. Anything derived that cannot name its inputs precisely enough to be taint-checked is a build bug found here.

18.5 **Cryptographic deletion** [SPECIFIED — M4, optional per scope] (D10). Per-record keys under a per-scope key; the chain over ciphertext so `verify` needs no keys; derived artefacts in generations with a per-generation key destroyed after retention, so re-folding is deletion and not addition; a tombstone on a deletion ledger. Key destruction is attested, never proven; backups bound it; no plaintext spill. The switch from today's plaintext chain is a generation event with a migration map (L22).

18.6 **The witness** (L26) [SPECIFIED — M4]: a daily content-free commitment of the segment heads, the schema and evaluator digests, the licence table and the deletion ledger, over two transports, published on no-change days too.

18.7 The owner's corrections are typed rows and feed retrieval, calibration, the duration model, policy and the gym; no weight is fine-tuned in place.

---

## 19 · The glass and the surfaces

19.1 The glass [BUILT as a local page] renders the IR: the pressure map (the dual per slot as colour), particles at their argmax cell with a halo whose radius is their support, contradictions as links, the four stocks as columns whose height is their price, the found-money partition (four figures, never one sum), the findings with a why-drawer, the coverage label, the arithmetic line with its regime, and the presence and island pills. Hysteresis: a particle moves only when its risk class, deadline or repair changes materially.

19.2 The four bays (`NOW · AT RISK · NEXT · WAITING`) are the same field projected as a list [BUILT]; the **evening batch** (§10.6) is a fifth surface, bounded, at the owner's hour [SPECIFIED — M4b].

19.3 Every card has a why-drawer [BUILT]: the source span, the compiled cell with probabilities and provenance, the join, the price before and after, the futures that broke, the repair options with their J.

19.4 **Four terminals, one plane**: the desktop (the composer's home and where the resident lives), the web address (the glass from anywhere), the forward address (the hand in text, with the typed reply), the phone (capture and the glass). Same tape, same field, same persona. Hop-0 (voice) renders the same rows and never invents. Nothing on any surface is generated prose except the wording of a draft, labelled as the model's.

---

## 20 · Physics: the island, the accelerator, the roofline

20.1 **The box** [M, `peek env` 2026-09-22]: RTX 4070 Ti SUPER 16 GB shared with `llama-server` (`:8092`) and a speech stack; free VRAM swings >11 GiB in minutes. Family arbitration: the resident is the sole resident VRAM consumer while seated; every other organ is on-demand and tears down; free VRAM is measured at seat and before every sweep; `tiers_dropped` rides every bound; a red result on a contended card is re-run once before it is believed.

20.2 **Island mode** (L16) [SPECIFIED — M0.5]. A `switch` row `island: on`, written by the operator or raised by a network fault and cleared the same way. In island mode: `delta()` returns `NETWORK_ABSENT`; the frontier seam returns `FRONTIER_ABSENT` and the residual routes to the local model or lands in UNRESOLVED; the branch backend falls back to local; the outbox holds every effect in `held` with its inverse, to fire on reconnection only after a `RECHECK`. Everything else runs unchanged; the glass shows `ISLAND` and never hides it. M0 already runs entirely on local files with the embedder on localhost [M]; **F-ISLAND** keeps it so.

20.3 **The roofline's regime** [BUILT]. The arithmetic line prints every tick: bytes counted, achieved GB/s, the measured stream-triad peak (128 MB per array, past the L2 — the original 48 MB triad read an L2 number 2.4× the card's DRAM [M]), and the **working set**. Under a cache-resident working set the counted per-pair bytes never reach DRAM and no bandwidth claim is printed; under 10⁶ (row, cell) pairs the CPU reference is the tier [M0: a 15-row lattice is a 5.75 KB working set, 17 ms on the CPU against 44 ms launch-bound on the card; DRAM peak 551–612 GB/s across runs]. "The card is justified" prints only in the streaming regime above `roofline.floor_fraction`. For one owner the re-price is a CPU job; the card's case is the multiverse (§8.9).

20.4 **The accelerator contract** (L17). The leaf functions — `place_cost`, the two Sinkhorn passes, the stencils, the rollout — are single host-and-device functions; a backend is an allocator, an upload/download pair, a launch macro and atomic adds on `uint64` and `int`. The CPU shim is the existence proof [BUILT: the same source green under MSVC, nvcc and WSL g++]. A third backend is the same four shims and a build line, valid the day O7 is green on it. **F-ACCEL.**

---

## 21 · The currency and the chain of custody

### 21.1 The loss (L20) [SPECIFIED — the harness at M2; the first number on the gym stream]
For an admitted event *E* at time *t*, with the memory `F_t` as it stood and a budget of *B* spans the read plan may emit:

```
R_B(E)       = readplan(F_t, header(E), B)
L_B(E | t)   = mean over the non-retelling chunks x of E of (1 − max_{s ∈ R_B(E)} sim(x, s)),   B ∈ {8, 32, 128, 512, ∞}
```

`L_∞` is the machine's whole-memory prediction; `L_8` is what its first sentence could have known; the gap is the price of the budget. Retellings above the corpus's own measured trough are excluded. Controls registered before the run: shuffled arrival at matched chunk count, reverse order, era-mismatched topic-matched, name-dated only. The honest expectation is the connectome's: arrival order beats shuffle in some deciles and not others, because a life is a stream of fronts.

### 21.2 What pays in it
Retrieval and reranking through the order they impose on `R_B`; the partition and scope masks through what the plan can reach; cases and compiled judgment through the spans they let the plan omit; the resident through the wakes and holds it contributed to `F_t`; situation embeddings through the frame stream (F-STATE-PREDICT); a compiled lane through the frames it renders. **F-RENT** per organ is `ΔL_B` at fixed *B* on ablation, with an interval; a no-op organ shows zero within noise (its lie arm). F-REFEED — the share of the owner's tokens that are context re-supply, before and after the brief — is `L_B` evaluated on the owner's own messages at the budget the session received, and it is the master number for the memory.

### 21.3 The chain (L21)

| fast grader | grades | is graded by | rate |
|---|---|---|---|
| the exact solver | the reflex's predicates over transitions (§9.5) | arrived outcomes of the transitions | same tick vs weeks |
| the tier above | the router's claim that the cheap gear suffices (§14.3) | arrived outcomes of the dispatched work | seconds vs weeks |
| the multiverse | policies and counterfactuals | its sim-to-real curve, F-WAGER (§8.8) | per rollout vs per horizon |
| the trusted evaluator (the gym) | candidates and stubs | held-out families and post-promotion outcomes | per run vs per deployment |
| the owner's declared attention | the reflex's recall on the declared class | arrival on the declared items (§5.4) | per forward vs weeks |
| the self-model | routing and authority requests | telemetry at the window's end (§17.5) | per window |

Each row carries an eight-bin monotone reliability curve fitted on this owner's data; shuffling a grader's labels must flatten it (the lie); a flattened curve removes the grader from the chain until re-fitted. **F-CUSTODY:** each fast grader's calibration against its own grader predicts its calibration against arrival, with an interval.

### 21.4 The collision audit (with L22)
Over the arrived record, find pairs of frames whose compressed representation matches within ε but whose arrived best action differed. The collision rate per representation — the compiled state line, the situation vector, a projected lane, the row itself — is that representation's decision error; each collision names the field it lacks and opens a `REPRESENTATION_FAILURE` residual. Bars are registered in `isobar.lock`; a representation above its bar may not be the sole input to any verdict. **F-COLLIDE**; lie arm: compare frames with themselves, the rate must be exactly zero.

### 21.5 Migration (L22)
Question sets, tier tables, lattice geometry (`slot_min`, hours, `N_STOCK`), providers and representations are versioned; a version event carries a migration map; curves are keyed by version and carried; licences are relabelled, never reset. **F-LAUNDER:** rename a class on which the machine was miscalibrated and its curve must survive; a migration that drops a mapping is refused at admission.

---

## 22 · Falsifiers

Each with a lie arm; every threshold registered in `isobar.lock` before the run that uses it; every quoted number reproducible by a script under `runs/`; intervals required; a miss goes to `runs/disagreements.md` with the smallest discriminating test. Three verdicts are kept apart on every outcome: executed as intended (a receipt), satisfied the bar (a fence), improved the real outcome against an alternative (only a paired control).

| falsifier | kills | lie arm | rung |
|---|---|---|---|
| **F-RECOVERY** | *the object is worth having*: ≥ 60 % of pilot owners find ≥ 3 unknown items at audited precision ≥ 0.80 in ten minutes | plant nothing; the scan finds nothing | M0 (owners pending) |
| **F-JEV** | *the reflex is calibrated here*: per-question curves on 200 owner-labelled emails; vs `llm_enum` at equal cost | shuffle labels; curves flatten | M0 (labels pending) |
| **F-JOIN** | *the embedder earns its VRAM*: keyed joins ≥ 95 %; planted duplicates recovered ≥ 70 % | negate planted embeddings | M0 [M: gym 100 % keyed] |
| **F-TIER** | *people give prices weight* | shuffle tiers; ranking follows | M0 [M: Mom first] |
| **O-MONO** | *the pipeline degrades with cognition, not on its own* | shuffle competence labels | M0 [M: monotone] |
| **F-SEVEN** | *seven days of mail, calendar, list, money and the clock with no owner teaching: what changed, what am I waiting for, who is waiting on me, what became impossible, what matters today that did not yesterday* — before any persona, resident or GPU | plant a change on day three no lane carries; the answer must be DARK, never a guess | M1 |
| **F-PRICE** | *the dual predicts breaches*: AUC of a slot's price 3 days out vs slip | shuffle prices; AUC → 0.5 | M1 |
| **F-WAGER** | *survival forecasts are calibrated*: 8 bins, monotone, ≥ 4 weeks — the multiverse's licence | shuffle forecasts | M1 |
| **F-ROOFLINE** | *the card is justified*: achieved / measured peak ≥ floor in the streaming regime | hard-code the peak; the oracle refuses | M1 [M: cache-resident for one owner] |
| **F-ISLAND** | *the interior is closed*: 24 synthetic hours offline — the field moved on due-crossing ticks, the X-ray recomputed, replay byte-identical, the multiverse ran, holds written, effects `held` with inverses, zero crashes | leave the network up; `NETWORK_ABSENT` rows must be present or the run is refused | M0.5 |
| **F-SEALED** | *nothing intentionally captured is silently discarded* | drop the refusal row; the audit finds the orphan | M0.5 |
| **F-HAND** | *declared attention teaches*: reflex recall on the declared class rises on passive mail within N weeks | shuffle declared labels; recall must not rise | from M0.5 |
| **F-HABIT** | *the owner trusts it and it makes sense of what it is given*: the capture rate rises while the UNRESOLVED price falls | count refusals as captures | standing from M0.5 |
| **F-GRADER** | *the owner's reaction stream is a usable verdict*: edits and sends distinguishable; the correction rate estimable under salt; κ can move | count every send as agreement; the correction rate must go to zero and be caught | from M2 |
| **F-COMPOSER** | *the in-flight wager changes what is promised* | random survival numbers | M2 |
| **F-ROUTER** | *the router is a calibrated wager* | grade the router by itself; the chain refuses | M2 |
| **F-RENT** | *this organ pays*: `ΔL_B` at fixed B on ablation | ablate a no-op; zero within noise | from M2 |
| **F-SCREEN** | *numbers come from OCR, never the VLM* | disable the fence; the wrong amount promotes and is caught | M2.5 |
| **F-RESIDENT** (decisive) | *presence beats both twins*, blind, registered window, two grains | give a twin the resident's disposition; the arms tie | M3 |
| **F-INERT** | *OFF is off* | flip the switch mid-run; must diverge | M3 |
| **F-STATE-SURPRISE** | *the trunk's surprise is a signal* beyond ‖Δv‖ and the Kalman null | shuffle lines in time | M3 |
| **F-JEV-STATE** | *the reflex over transitions is calibrated on the fast clock* | shuffle the solver's ground truth; curves flatten | M3.5 |
| **F-PROBE** | *the held join earns its place* against the embedding join at matched cost | zero the probe weights | M3.5 |
| **F-CUSTODY** | *fast graders predict arrival* | sever the terminus; the chain refuses to certify | M3.5 |
| **F-KAPPA** · **F-KAPPA-FLOOR** | *the persona removes decisions*; *κ is undefined at zero outcomes* | count review minutes as free; define κ at n = 0 | M4 |
| **F-INJECT** | *inbound is data* on every lane including the hand | disable SENTINEL and the grammar; effects leak | M4 |
| **F-IGNITE** · **F-INVERT** | *no gate is OPEN at n = 0 without a grant*; *no class with `inverse_window ≤ L` reaches LICENSED* | remove the grant; declare a send reversible | M4 |
| **F-REALM** | *evidence never crosses realms; capacity does when permitted* | drop the mask | M4 |
| **F-WRITER** | *an unmodelled writer is detected within one period* | act through the dashboard; the lane must go DARK | M4 |
| **F-LAUNDER** | *renaming cannot escape the record* | a migration map that drops a mapping | M4 |
| **F-PAID** (release-blocking) · **F-TRAVEL** · **F-COVERAGE** · **F-ABSENCE** | as r0.1 | as r0.1 | M4a |
| **F-VOI** | *the machine asks the questions worth asking* over ≥ 30 asks | randomise the ranking | M4b |
| **F-PHONE-SYNC** | *offline capture is lossless* | corrupt one queued row; the merge refuses it by seq | M5b |
| **F-NOISE** · **F-BASELINE** | *‖Δv‖ is the event's weight*; *the field beats a cached turn-based baseline* | randomise Δv; withhold the field | M6 |
| **F-STATE-PREDICT** · **F-PRECEDENT** | *situation embeddings carry information*; *precedent priors help F-WAGER* | shuffle frames; random precedents | M6b |
| **F-DYNAMICS** | *the learned rollout beats the hand-written one* | train on shuffled arrivals | M7 |
| **F-COLLIDE** | *a compressed representation preserves the decision* | frames against themselves | per representation |
| **F-ACCEL** | *the solver is a leaf, not a vendor* | change one config hash; parity fails by name | a second device |
| **F-REFEED** (memory's master) | *the brief reduces the owner's re-explanation tax* | a random-span brief of equal length | from M3 |
| **O1–O9** · **O-MONO** | *the instruments are real* | `--selftest --lie N` | M0–M4a |

**The decisive numbers**, in order: F-SEVEN (can the plane hold a coherent week without being taught), F-GRADER (is the owner's reaction a verdict), F-RESIDENT (is the resident an asset or a cache), F-ROOFLINE (does the card earn its place for this owner). None has been produced.

---

## 23 · Security, consent, poisoning

23.1 **Injection corpus per lane in CI** (mail, list, calendar, hand — "mark this paid", "cancel the meeting", "forward the invoice", an instruction-shaped task, an invite body with directives, a forwarded message with instructions above the quote) ⇒ zero effects without the gate. The deterministic pre-filter [BUILT] can only raise the injection flag; the `SENTINEL` seat flags `injection_shape`; the parser grammar admits nothing dispatchable.

23.2 **Consent classes**: `standard`, `contacts`, `location`, `money` (read-only), `voice`, `camera`. Every capture is owner-invoked and scoped to the owner's own operational life; other people's voices under the owner's jurisdiction policy; the recording light is a tape row.

23.3 **Poisoning without a model in the loop.** An invented token occurring once beside a target reaches ceiling association weight by minimising evidence; every co-occurrence weight is count-shrunk; structure supported only by untrusted spans is quarantined until two independent documents support it; use-credit along quarantined paths is escrowed. L25's corroboration count is what the owner is shown.

23.4 Secrets never enter a microVM; identifiers are redacted before any model call; raw mail, pixels and audio never leave the owner's key domain; the hybrid deployment states per field what may leave.

---

## 24 · Status

| clause | state | receipt |
|---|---|---|
| the tape (§18.1–18.2 built kinds), the contracts (§3), the purity lints (§6.3), the sampling lint (L5) | BUILT | 29/29 tests |
| the field instrument with O1–O8b and lie arms 1 and 3; the `--tick` IPC; the CPU/accelerated bridge with the working-set regime | BUILT | `solver/build.cmd` green on MSVC and nvcc; WSL g++ parity |
| the reflex client (stub with the competence dial; Laya client), the mail question set, deterministic extraction | BUILT | F-JEV pending labels and weights |
| the join with keyed-only state changes; promotion; people and money registries; the scan; the glass; five file connectors; the gym; the CLI | BUILT | `receipts/M0_GATE_2026-09-22.md`: 7/7 plants at precision 1.00 with a perfect reflex; the paid invoice never chased; WAITING priced 4.03; replay byte-identical over 850 rows; monotone three-seed sweep; CI green on a second platform with no CUDA toolkit and no embedding server |
| everything else in this document | SPECIFIED, BET or OPEN | `docs/ROADMAP_r0.2.md` |

The owner-facing half of M0's gate — real pilot owners (F-RECOVERY) and 200 owner-labelled emails with the Laya weights (F-JEV) — is pending and outranks every rung above M1. The build order is `docs/ROADMAP_r0.2.md`; the contract deltas an implementing session applies under the CI lints are `docs/contracts/CHANGES_r0.2.md`.

---

## 25 · Open questions

Collected in `docs/BACKLOG.md` (B1–B16 stand). New with r0.2: the independence key for corroboration (L25) on a single owner's mail; the witness transports; the relay for the phone head; the `n_eff` floor per class at personal volume; whether `[project]` boundaries are daily folds or dependency events; the surprise null's exact form; the reranker (B2, still open); the compose surface (B1, still open); whether the accelerated multiverse is worth a second device for one owner (answered by F-ROOFLINE at M1).

---

## Appendix A · Process topology

```
isobard            Python 3.13 · the plane: tape, connectors, reflex client, join, promote, registries, bridge, scan, gate, outbox, glass
                   calls the instruments below as subprocesses over a memory-mapped SoA file + JSON header
isobar_field       C++17 single TU · CPU reference and accelerated tier · --tick · --selftest --lie N · --bench       [BUILT]
isobar_foresee     C++17 single TU · the multiverse · --run · --rehearse · --backtest · --parity · --selftest         [M1]
resident           fusord/nib lifted · FieldSource on the typed lanes · SHADOW by default · the hold segment           [M3]
laya | jev         the reflex provider behind SemanticReflex                                                         [BUILT client]
llama-server       :8092 embeddings (on the box); a local reader and VLM for the residual, the wording, the screenshot
phone head         capture · seal · encrypt · queue · sync · render — no organ methods                                 [M5b]
branch             E2B or the local fallback: the gym, the counterfactual, attachments, fan-out — never the inner loop [M5]
```
No organ imports another; organs are called at fixed paths as subprocesses.

## Appendix B · Repository layout

```
isobar/
  README.md · CLAUDE.md · LICENSE · isobar.lock · writ.yaml · tiers.yaml · requirements.txt
  docs/  SPEC.md (r0.1, lineage) · SPEC_r0.2.md (normative) · ROADMAP.md (r0.1) · ROADMAP_r0.2.md · BACKLOG.md · devlog.md · VISION.md
         contracts/*.md · contracts/CHANGES_r0.2.md · lineage/
  solver/      isobar_field.cu · build.cmd · (isobar_foresee.cu at M1)
  isobard/     contracts · tape · reflex_client · embed · join · promote · registries · field · scan · plane · cli · gate_m0
  connectors/  direct/ (mbox, ics, textfile, vcf, moneycsv) · composio/ (pending a key)
  reflex/      questions.yaml · (questions_note.yaml, questions_state.yaml) · providers/
  presence/    FieldSource · seats · the twins · the hold segment
  glass/       render.py
  gym/         owner_solo.py · (planted worlds, lies)
  tests/       29 checks · receipts/  gate receipts · runs/  the owner's data (gitignored)
```

## Appendix C · Concordance

The record — tape · CORTEX. The frame — StateFrame · the IR of a horizon · Field + head of Foresight. The hold — the second tape · the record of presence · the eviction column's dwell. The hand — the forward address · the share sheet · the capture lane · the Tripit gesture. The box — the island · closed-box competence. The twin — the threshold twin · the reflex-wake twin · TURN+CD. The loss — rent · the prequential code length · F-REFEED. The fast grader — the chain of custody · the gear selector graded by the tier above.

---

*Rev 0.2 written 2026-09-22 by Claude Fable 5.1 for Bo Chen, after M0 landed, against Addendum A, the master architecture v2.0 and the Reflexive Cognitive Machine proposal. Every [M] belongs to the instrument it names; the four decisive numbers have not been produced.*
