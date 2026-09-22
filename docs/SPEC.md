# ISOBAR — SPECIFICATION

> **Superseded on 2026-09-22 by `docs/SPEC_r0.2.md`, which is normative. This file is r0.1, kept byte-for-byte as lineage below this banner; nothing under it was edited.**

*Rev 0.1 · 2026-09-22 · normative. Where this document and `C:/AGI/ISOBAR_THE-PRICED-WEEK_…md` (the blueprint, copied to `docs/lineage/`) disagree, this one governs the artefact and the blueprint governs the intent. Where either disagrees with a dated receipt under `runs/`, the receipt wins and the document is the defect.*

Terms: **MUST**, **MUST NOT**, **SHOULD**, **MAY** carry their usual force. Every clause is tagged **[BUILT]** (exists and is covered by a gate), **[SPECIFIED]** (settled, unbuilt) or **[OPEN]** (undecided; collected in §22 and `docs/BACKLOG.md`). **Nothing in this revision is BUILT.** Numbers tagged **[M]** were measured on this box by the instrument named; **[D]** are derived; everything else is a design number to be replaced by a measurement at the milestone that produces it (`docs/ROADMAP.md`).

---

## 1 · Scope

1.1 ISOBAR is a personal operations plane over **three lanes** — mail, calendar, task list — brand-agnostic behind one connector contract (§4), **three registries** the field reads — people, places, money — seeded by one small read each and grown by the lanes (§10), and **the clock**, which is a lane. One owner; the schema allows N seats (delegates) and v1 builds one.

1.2 ISOBAR holds one canonical object, the **commitment**: who owes what to whom by when, with evidence. The lanes are evidence of it, capacity for it, or a projection of it. There is no `tasks` table.

1.3 ISOBAR's centre is a **solver** that prices the owner's horizon every tick and integrates over sampled futures. The GPU is the interactive tier; the CPU path is first-class and the reference; the roofline (§19) decides which ships for a given owner. Every idea in this document holds on either.

1.4 **Out of scope, permanently:** a chatbot as the product surface; a face; a vector database as truth; a task table; an `allow` verb; ambient capture of any kind; a payment *effect* (money connectors are read-only verdict sources in every rung).

1.5 **Out of scope for REV 0 (v1):** audio, images, SMS beyond folding into the mail lane, the learned effect heads, the parametric tier, multi-tenant pooling, place-triggered attention.

---

## 2 · Laws

Everything below is a mechanism for one of these. A change to a law is a version event with a named reason.

> **L1 · ONE OBJECT.** The commitment is canonical. Mail, calendar and the list are sensors and projections. No second source of truth.

> **L2 · TAPE.** Every observation, assertion, price, hold, verdict, effect, wager and grade is an append-only, hash-chained row (§16). Every table is a fold; same tape ⇒ byte-identical tables (the replay oracle).

> **L3 · OBSERVATION ≠ ASSERTION ≠ STATE.** Raw evidence is immutable; reflex and model output are candidates; only deterministic promotion writes state. Nothing learned writes canonical state. Enforced by an import-purity lint over `promote/`, `gate/`, `solver/`.

> **L4 · COMPUTE THE RELATIONAL, JUDGE THE RESIDUE.** Contention, price, support, contradiction, survival are computed exactly by the solver. Is-a-promise, which-kind, how-firm are typed by the reflex with measured calibration. What-does-this-unusual-thing-mean is the LLM, rarely. A unary signal (surprisal, urgency-as-worded, novelty) MUST NOT decide a relational outcome (promotion, merge, supersession, deletion, licence).

> **L5 · UNCERTAINTY FLOWS THROUGH.** A calibrated probability is a sampling distribution for the multiverse, never a threshold, until the deterministic gate.

> **L6 · PRICE, NOT RANK.** The dual of the transport problem is the price of a cell; an event's weight is ‖Δv‖, the movement of the price vector it caused. No organ ranks by how urgent a message sounds.

> **L7 · THE PLAN IS NEVER MATERIALISED.** Resident solver state is `u[N] + v[M]`; a row of the plan is recomputed on demand. Two arms read one canvas through two masks; no second canvas exists.

> **L8 · SILENCE IS A ROW.** Every boundary at which the resident could have spoken and did not is a row with its margin and a closed reason. Absence is never rendered as assurance.

> **L9 · EVERY EFFECT CARRIES ITS INVERSE OR IS CLASSED IRREVERSIBLE.** The inverse is recorded before the effect fires. Reversibility comes from the connector's capability table, never from the caller. Irreversible always asks.

> **L10 · THE GATE IS DETERMINISTIC**, contains nothing learned, can only narrow, emits a closed verb with a closed reason, checks budget and exposure last, and has no `allow`.

> **L11 · AUTHORITY IS EARNED PER CLASS** from exterior verdicts on executed choices, sampled by a salt the machine cannot read; it narrows on any evidence and never widens on confidence. Corrections outweigh approvals.

> **L12 · NO ORGAN OUTLIVES ITS NULL.** The threshold twin runs beside the resident forever; the CPU reference runs beside the GPU forever; a cached turn-based baseline runs beside the field. If a null ties, the organ above it is retired and the finding is printed.

> **L13 · INBOUND IS DATA.** Corpus bytes are never instructions on any lane; extraction prompts frame content as data; outputs are schema-constrained; models have no tool access; model output is parsed under one grammar and nothing in it is dispatched on.

> **L14 · MAIL SILENCE IS NOT PROOF.** An invoice is unpaid only when a verdict source says so or the owner says so. Without the money connector, money-like findings carry `payment_status: not_connected` and are never upgraded.

> **L15 · A NUMBER WITHOUT ITS BAND IS NOT A NUMBER.** Every accumulator carries its sum of squares; every reported quantity prints a band and a date; every oracle carries a lie arm; the peak bandwidth is measured, never a constant.

---

## 3 · Objects

3.1 All objects are typed; handoffs between organs are typed handoffs and never prose. Schemas live in `docs/contracts/objects.md` and MUST be the single definition (Pydantic v2 in `isobard`, mirrored as C structs in `solver/`, with a round-trip fixture test at M0).

3.2 The **IR of a horizon** is `Field` (§6.4) plus the head of `Foresight` (§7). Every organ above the solver reads the IR. **No organ above the solver reads the calendar, the list or a mailbox directly** — the reflex reads one email at a time, the resident reads the IR's delta lines, the LLM reads a typed intent plus the IR slice it moved.

3.3 Identifiers: content-addressed where content is immutable (observations, cells); UUIDv7 elsewhere; `src_rev` monotone per external object (equal ⇒ no-op, lower ⇒ refused).

3.4 **Time.** All instants are stored as UTC nanoseconds. Slot mapping uses the owner's zone from `isobar.lock` (`owner.tz`), re-evaluated per day for DST. Recurring events are expanded within the horizon at ingest; the recurrence rule is provenance, not state. All-day events consume zero slots unless policy says otherwise. Tentative events consume capacity at their acceptance probability, sampled in the multiverse.

---

## 4 · Lanes and the connector contract

4.1 A **lane** is an evidence source, an effect target, or both, behind one interface (`docs/contracts/connector.md`). Lanes in v1: `mail` (SMS folds in with provenance `sms`), `cal`, `list`, `tick`, `compose`; registry feeds: `contacts`, `money`, `location` (consent).

4.2 **Two implementations per lane from day one** [SPECIFIED]: a hosted broker (Composio) and a direct or open adapter (IMAP/Graph/Gmail API; CalDAV/Graph/Google Calendar; Todoist/MS To Do/Google Tasks/plain text). No vendor is the only path to the owner's own mail.

4.3 Backfill and delta MUST be resumable and idempotent by `(source, external_id, src_rev)`. A connector MUST NOT interpret; it transports evidence in and effects out.

4.4 Reversibility lives in `capabilities()` and nowhere else: `mail.draft` reversible; `mail.send` compensable-low for a nudge and `irreversible` for a commitment-bearing reply; `cal.move` reversible; `cal.accept_external` compensable; `list.*` reversible; `money.*` read-only.

4.5 **The clock is a lane.** `tick` rows are emitted lazily — one per gap, sized to the gap, before the event that broke the silence — never a periodic decode while nothing happens.

---

## 5 · The pipeline

5.1 Three paths, three clocks (blueprint §3). The **event path** MUST run CODE → REFLEX → JOIN → (RESIDUAL) → PROMOTE → FIELD → FORESEE → PRESENCE → GATE → HEADS → (WORDING) → OUTBOX → GRADE. The **tick path** MUST run FIELD → FORESEE(reduced K) → PRESENCE → GATE with no reflex and no join. The **compose path** MUST run ingest → REFLEX in flight → warm-started FORESEE → COMPOSER seat → (un-say).

5.2 The order of REFLEX and JOIN MAY be swapped per event class (classify-then-retrieve for bulk backfill; retrieve-then-classify for replies on known threads). The router MUST log the order and the gear per event.

5.3 **Purity.** `promote/`, `gate/` and `solver/` MUST import nothing from `reflex/`, `llm/`, `presence/` or `connectors/` (lint at CI). No FOLD in a read path; no search-selected unit in an estimator (§11.2).

5.4 **Gears.** Every organ declares input type, output type, cost, latency, confidence semantics, side effects and its verifier. The cheapest gear that clears the trust bar runs; every escalation is logged with its reason.

---

## 6 · The field (solver contract, part 1)

Lifted from `C:/fusor1/ledger_lattice/ledger_lattice.cu` [M, six oracles with lie arms, 2026-09-06]. The instrument is `solver/isobar_field.cu`, a single translation unit, C++17/CUDA, `-DISOBAR_CPU` for the serial reference. Its ABI is `docs/contracts/solver.md`.

### 6.1 Geometry [SPECIFIED]
- `seats` = owner (+ delegates). `slots` = `horizon_days × slots_per_day` at `slot_min` granularity over `owner.hours` (default 14 × 28 half-hours over 07:00–21:00). `M = seats·slots + 3`.
- Stocks, each with **finite** capacity and a real dual (the T17 fix): `UNPLACED` (backlog; carrying cost), `UNADJUDICATED` (needs the owner; adjudication bandwidth), `WAITING` (with a counterparty; the price of their silence).
- Rows = open commitments: `active`, `waiting`, `candidate` (candidates enter at their promotion probability, §8.4).
- `cap[c]` = slot capacity minus fixed allocations minus policy (focus blocks, no-meeting windows, hours); `law[cls × seat]` and `law[kind × slot]` as −inf masks unoverridable by anything learned.
- **Two arms, one canvas:** `arm 0` = the incumbent (each row's `inc_cell` from the calendar/list), `arm 1` = the solver. One bitmask.

### 6.2 The one dynamics source [SPECIFIED]
`place_cost(i, c)` is `__host__ __device__` and the only place the cost of a row in a cell is defined. It MUST apply, in order: stock cost; law masks; arm mask; duration fit and release; compat (`int8·int8/√D` between the row embedding and the slot's kind key); lateness × hardness; the **tier weight** from the people registry (§10.1); all over `T`. The Sinkhorn, the support meter, the stencil and the report MUST read this one function; oracle **O1** asserts two independent traversals agree (gate `1e-3`).

### 6.3 Sinkhorn, duals only [SPECIFIED]
Rows equality, columns inequality (scale down only), every column including stocks takes the dual update, **finish on a row pass** (ending on a column pass fails O1 at `6e-2` and O3 at `1e-2` [M, ledger_lattice 2026-09-06]). Warm iterations per tick from `isobar.lock` (`iters_tick`, default 40); convergence curve published, never a point (O3's curve: 60 iters marginal, 400 plateau [M]).

### 6.4 Outputs, every tick [SPECIFIED]
1. `v[M]` price vector, aggregated per hour, day and stock; the binding constraints.
2. `es[N]` support spectrum `exp(H_i)`; the decided/contested split re-measured here (`support_split`, borrowed 3.0, first thing to re-measure).
3. Contradictions: `K_OVERCOMMIT`, `K_DOUBLEBOOK`, `K_DEPENDENCY`, `K_DEADLINE` (keyed, self-certifying), `K_DUPLICATE` (unkeyed, model judgment, reported separately with confidence, sampled audit), `K_TRAVEL` (§10.2), `K_PAID` (§10.3).
4. The arithmetic line: bytes moved, achieved GB/s, fraction of **measured** peak (stream triad), the kill condition printed either way.
5. `Δv` and `‖Δv‖` per event, stored on the tape.
6. `risk[N]` breach forecaster (price of the landing cell × slack deficit), the AT-RISK sort key.

### 6.5 Determinism [SPECIFIED]
Counter-based RNG; fixed-point `uint64` accumulators; no float atomics; `memcmp`-identical duals under a seed (**O2**). CPU and GPU MUST run the same leaf; parity is an oracle (**O7**, worst relative |Δ| ≤ 1e-6).

### 6.6 Oracles and lies [SPECIFIED]
`isobar_field --selftest --lie N`: O1 one dynamics source · O2 determinism · O3 conservation (rows ship supply; no column overflows; curve published) · O4 stocks priced (both/all stock duals > 0 under squeeze) · O5 int8 round-trip cosine ≥ 0.995 · O6 unkeyed duplicate recall ≥ 70 % on planted pairs · O7 parity · **O8 K_PAID** (a planted paid object never appears in a chase set). An oracle that passes its own lie exits nonzero and names itself.

---

## 7 · The multiverse (solver contract, part 2)

Lifted from `C:/fusor1/FlightComputer/src/flight_computer.cu` [M, 16/16 oracles; CPU/GPU parity ~1e-7; ~18k universes/s at 4,000 universes on this card]. The instrument is `solver/isobar_foresee.cu`. One predictor, three callers: DRIVE, FORESEE, TRAIN.

7.1 **A future** [SPECIFIED] samples per universe with counter-based RNG: `dur_i` from the three-point per row; `due_hard_i ~ Bernoulli(p_hard_i)`; `join_i ~ Categorical(p_join_i)`; arrivals per counterparty class; reply latency per counterparty; meeting overrun per class; `calendar_truth ~ Bernoulli(p_cov)` or measured from location (§10.2); `travel_t` from place edges; `payment_state` from the money registry when connected. It integrates `H` periods with `iters_future` warm iterations each and scores the writ.

7.2 **Paired worlds.** Arrivals and coins are hash-keyed on `(seed, period, row)`; a candidate arm and the do-nothing arm MUST see the same world. The baseline is an arrival, never a forecast.

7.3 **The writ** is owner-authored in `writ.yaml` (`docs/contracts/writ.md`), never fitted; ranking is `J_mean + β·J_std`; lexicographic tiers (hard breaches; external promises; fewest renegotiations; least churn; buffer).

7.4 **The action menu** is closed: `HOLD · DECLINE · COUNTER · MOVE · PROTECT · NUDGE · SPLIT · DELEGATE · DEFER · RENEGOTIATE · DROP`. `HOLD` is always present. `RENEGOTIATE` and `DROP` are never proposed above `ASK`.

7.5 **The pipper** is the best future's first move. It MUST be shown with forecast, band and the do-nothing arm's number. It is **kept only if reality confirms**: an accepted move is a wager with a horizon; on arrival the outcome is compared to the forecast; a move that did not beat do-nothing unwinds through its inverse; TRAIN sharpens durations, arrivals, latencies and the reflex reliability curves. Oracle **O9**: the deploy is graded on arrived outcomes, paired.

7.6 **The wager on a draft** [SPECIFIED]: adding one forming row warm-starts from resident `u, v`; a reduced run (`K_compose`, default 256) returns `survival ± band` for the composer seat. The wager row is written whether or not the owner looks at it.

7.7 Budgets [D, to be measured at M1]: field re-price ≈ 3 ms GPU / 30 ms CPU at N=120, M=395; FORESEE K=4,096, H=14 ≈ 1–5 s GPU first cut, ≈ 20 s on 16 cores; compose rehearsal ≈ 0.1–0.3 s GPU. The one-block-per-universe shared-memory Sinkhorn is the named next 5–10×.

---

## 8 · The reflex

8.1 **Interface** (`docs/contracts/reflex.md`): `SemanticReflex` with `noul(question, evidence) → (bool, p)`, `choice(question, options, evidence) → (option, p)`, `score(question, levels, evidence) → (level, p, distribution)`, batched so one inbound is one call. Providers are plugins: `laya` (default open; 421M ModernBERT, ~33 ms [V, HF card]), `jev` (TypeSafe API), `trunk_head` (a second head on the resident, later), `llm_enum` (the deletion-condition comparator).

8.2 **The question set** is data: `reflex/questions.yaml` (17 questions; blueprint §6.1). Every answer carries `(value, p, provenance ∈ {HIGH, MOD, LOW_absent, LOW_conflict})`. Dates and amounts come from deterministic extraction; the reflex only says whether one was mentioned.

8.3 **Sampling law.** `p` is never thresholded before the gate; it is written to the row as a distribution the multiverse samples (L5).

8.4 **Calibration.** Per `(provider, question, band)` a reliability curve over 8 margin bins is fitted on this owner's arrived outcomes with a monotonicity test; a non-monotone question is `uncalibrated` and its output is sampled at the class prior. Vendor curves are never trusted. **Deletion condition:** a cheap LLM constrained to an enum ties calibrated accuracy at equal cost.

8.5 **Free questions.** Every open commitment MAY be re-asked, per tick, "has anything since your last check discharged you?" as one batched pass over the day's cells; the reflex is consulted per state change, not per decision.

---

## 9 · The join

9.1 Exact keys first (thread id, in-reply-to, invoice/quote numbers, calendar ids, addresses), then lexical, then `embed → rerank → reflex same_as ×3`. The join is a distribution `p_join` (L5). Target: ≥ 95 % of joins resolved by exact + lexical (the embedder's deletion condition).

9.2 Embeddings: 128-d int8 coarse (resident) and 1024-d int8 full, from the local endpoint (`:8092`, qwen3-embedding-0.6b [M, on the box]); scan resident, exact, bit-identical to the CPU (the connectome's `cx-index` discipline). Reranker: [OPEN] (`bge-reranker` class local, or the reflex itself over top-8).

9.3 **Never** merge two money-bearing or promise-bearing identities on similarity alone. The unkeyed duplicate (`K_DUPLICATE`) is bucketed by entity, not by cell, and audited by sample.

---

## 10 · The registries

Registries are rows the field reads: seeded by one small read, grown by the lanes, corrected by the owner. **They have no agents, no loop, no authority.** Schemas: `docs/contracts/registry.md`.

### 10.1 People [SPECIFIED]
- Seed: a contacts read (consent `contacts`). Growth: every identity mail and calendar produce, merged by the resolution ladder (exact id → exact identity → thread → domain+name → lexical → embedding → reranker → owner).
- **Tier is owner policy, never inferred.** The tier table is a file the owner edits (`tiers.yaml`); a proposed tier from any model is a candidate row until confirmed.
- Read by the field as: the tier weight in `place_cost`; the per-counterparty **silence price** in `WAITING`; the arrival and reply-latency models per counterparty class in the multiverse; relations the writ may name.
- v1 relations vocabulary is closed: `client · vendor · partner · family · colleague · agent · unknown`.

### 10.2 Places [SPECIFIED]
- Seed: addresses parsed from mail signatures, calendar locations, contact cards; home and work confirmed by the owner. Growth: located events and written addresses. Travel edges from a routing service, cached, between every pair of places appearing in one horizon.
- Read by the field as: **travel cells** consumed between allocations at different places; **travel buffers** as −inf masks; **`K_TRAVEL`** in the stencil (two allocations closer in time than their edge).
- The location lane is consent-only (I13) and, when present, turns `calendar_truth` from a sampled inference into a measurement (was the owner where the calendar said, when it said). Without it, `calendar_truth` is sampled at the coverage estimate and bands widen; "your week fits" is never claimed at coverage WEAK.

### 10.3 Money [SPECIFIED]
- Seed: commercial objects compiled from mail (quotes, proposals, invoices, bills, payment requests) with deterministic amounts. Verdict: one read-only connector (Stripe / QuickBooks / Xero / bank or card feed) whose state **supersedes** mail inference.
- L14 enforced in the stencil: **`K_PAID`** — no chase set may contain an object the verdict source says is paid; release-blocking oracle O8 with a planted lie.
- The glass's found-money partition MUST keep the types apart and never sum them: `confirmed_receivable` (verdict) · `apparent_overdue` (mail-only, labelled) · `proposal_pipeline` · `vendor_credit`.
- Read by the field as: discharge evidence for payment commitments; the WAITING price for money items (`amount × age × tier`); for a person, discharge of purchases and bills.

### 10.4 The registry law
Every registry row carries `provenance[]` and `confirmed_by ∈ {owner, inferred, verdict}`. A wrong tier is policy the owner set; a wrong place is one confirmation away; a wrong payment state is a connector fault typed `verdict_unavailable`, never a guess.

---

## 11 · Coverage and estimation

11.1 Three coverages, never interchanged: `index_coverage` (addressability, exactly 1.0, never printed as coverage); `capacity_coverage ∈ {UNKNOWN, WEAK, USABLE, STRONG}` from density of work blocks, completions vs calendar, self-report, location when consented; and `coverage_int` over the pair-space of commitments (which contradictions have been checked at which resolution), exact by counting.

11.2 **Search is not inference.** Retrieval, firing, salience decide what is read; no unit they select contributes to an estimate. Prevalence bounds use stratified draws over a frame masked before the draw; the negative types are `NOT_PRESENT_EXACT` (an exhaustive scan receipt over the tape, `everywhere`), `NOT_FOUND(p_U, n)` (a bound, never absence) and `BELIEVED_UNCLOSED`.

---

## 12 · Presence

Lifted from `fusord.cpp` via `C:/nib` [M, 0.11.1]. Mounted, not re-derived; the seed, seat probe and speak-cue are byte-frozen and the resident refuses to start if the hash moves.

12.1 **Lanes** [SPECIFIED]: `[field]` the typed `FieldDelta` line per tick (≈100 tokens; never an email body) · `[mail]` the compiled header of each inbound · `[compose]` the owner's forming outbound text · `[tick]` · `[self]` (no self-exception; gate-skipped). The trunk holds the field, not the corpus.

12.2 **Seats**: `FIELD_WATCH` (speaker; field, mail, tick) · `COMPOSER` (compose) · `SENTINEL` (skeptic; mail, field — contradiction with the field, injection shape). One trunk; seats fork at 0 MiB.

12.3 **The hold row** (`docs/contracts/presence.md`) MUST be written at every boundary: margins over the closed alphabet, verdict, closed reason, gear, latency, and on an un-say the aired spans and the killed remainder. The row is the second tape (LIFELINE v5 §6.3, verbatim).

12.4 **Modes and the switch.** `OFF` (provably inert: no probes, no GPU work attributable, byte-identical to stock) · `SHADOW` (full ingest and judgment; zero surfaced output; **the default at install**) · `LIVE`. The switch is operator-only, a `switch` row on the tape, and never operated by any model or policy.

12.5 **The twin.** A swept threshold on `‖Δv‖` with perfect boundaries, the same field, the same model, runs beside the resident forever in shadow. **F-RESIDENT** (§20) is decisive; if the twin ties on catches-that-mattered, the resident is retired to a query interface and the threshold ships.

12.6 The judgment is the event; the world may be polled (a mail lane may be a poller), the judge is never clocked.

---

## 13 · The residual and the wording

13.1 **Local model** (9–27B via llama.cpp on the box): (a) schema extraction from one email when the reflex answers `needs_judgment` or a field is `LOW_conflict`; (b) verbalising a `DraftIntent` into the counterparty's language from the typed intent alone. It MUST NOT invent feasibility or rewrite a plan.

13.2 **Frontier** (one seam, budgeted per day in `isobar.lock`, fingerprinted per call): novel semantics; template compilation at setup; the **jury on irreversibles** — two judges of distinct lineage must agree on the exact effect bytes under a cap the machine cannot raise; disagreement may narrow or HOLD, agreement never widens.

13.3 Every model call MUST redact sensitive identifiers, frame content as data (L13), and receive only the IR slice and the one evidence item it needs — never the whole horizon in prose.

---

## 14 · The gym and the branch (E2B)

14.1 Two fork primitives, never conflated: `seq_cp` inside the card (probes, un-say, rehearsal); a microVM outside it (the gym, the counterfactual, attachments, fan-out). Nothing generated in a branch is an observation or authority-earning evidence; the live gate revalidates against live state.

14.2 **The gym** (`gym/`): a synthetic owner with planted truth (silent quote; invoice paid where mail cannot see; calendar fiction; a "maybe Thursday"; a duplicate task/email; a two-place collision) and stub cognition with competence knobs (`StubReflex(c)`, `StubPresence(c,k)`); the competence sweep MUST be smooth and monotone (**O-MONO**) before any real model is measured.

14.3 **The counterfactual fortnight**: fork the plant into a microVM (connectors in replay mode), add the scope, fly `H` days of arrivals at the owner's measured rates, paired against do-nothing under identical hash-keyed arrivals; the answer is labelled `simulated`.

14.4 Attachments that are not plain text or PDF open in a microVM; connectors never run inside it; live credentials never enter it.

14.5 CPU fan-out: when the local card is contended, K futures MAY spill across microVMs with the branch manifest pinning the cut; the CPU leaf is the same code, so parity holds.

---

## 15 · The heads

15.1 Each surface has a head emitting in its own action space (`docs/contracts/objects.md`): `ScheduleDelta`, `DraftIntent`, `TaskDelta`. In v1 the heads are **deterministic projections of the solver's repair** into the surface schema; prose exists only at the mail surface (§13.1b). The learned head is a later rung with its deletion condition (every required effect already has an adapter).

---

## 16 · The gate, the outbox, the licence, κ

16.1 **Verbs**: `SILENT · FLAG · ASK · DRAFT · ONE_CLICK · ACT · HOLD · RECHECK`, each with a reason from a closed enum (`docs/contracts/gate.md`). The gate reads: the licence for this class on this surface; the exposure cap; the inverse window; the state version the intent was planned against (stale ⇒ `RECHECK`); capacity coverage; the row's support (contested ⇒ never `ACT`). Budget and exposure are checked last. Build hash on every verdict.

16.2 **Classes** are ordered by verdict latency and inverse window, never by felt risk (blueprint §12 table). `chase_invoice` requires the money verdict; without it `DRAFT` only, labelled.

16.3 **The outbox** is the single writer: inverse recorded before the effect; idempotency key; precondition; hold window during which the un-say is the owner's; receipt.

16.4 **The licence ladder** per class: `L0 OBSERVE · L1 DRAFT · L2 ONE_CLICK · L3 CANARY · L4 LICENSED · L5 RESERVED`, earned on exterior verdicts of executed choices sampled by a governor-held salt, narrowed on any evidence. The dense grader is the owner's reaction to every draft: sent-as-is (weak), edited with diff (strong; the training signal), discarded, undone, acted-within-`t`. Rare classes are printed as undelegatable at personal volume.

16.5 **κ** = attention minutes consumed per outcome, printed weekly from the tape; a rising κ demotes the resident to a query interface the same week.

---

## 17 · The tape

17.1 Append-only, blake2b-128 hash-chained, fsync'd, **one writer per segment** (a second writer on a held segment is refused by the OS). Row kinds: `observation · cell · join · promotion · field · foresight · hold · switch · verdict · intent · effect · receipt · wager · grade · calibration · licence · policy · correction · registry`.

17.2 `field` rows store deltas of `v`, `es`, and the contradiction set, never the full vector per tick. Same tape ⇒ byte-identical tables; `isobar replay --verify` is a standing gate.

17.3 The owner's corrections are typed rows and feed retrieval, calibration, the duration model, policy and the gym; no weight is fine-tuned in place.

---

## 18 · The glass and Hop-0

18.1 The glass (`glass/`) renders the IR: the horizon as a pressure map (the dual per slot as colour), commitments as particles at their argmax cell with a halo whose radius is their support, contradictions as links, the three stocks as columns whose height is their price, the found-money partition, and the pipper with its band and the do-nothing number. Hysteresis: a particle moves only when its risk class, deadline or repair changes materially.

18.2 The four bays (`NOW · AT RISK · NEXT · WAITING`) are the same field projected as a list, ordered by slack at coverage USABLE and by due otherwise; owner edits enter as observations from source `owner`.

18.3 Every card has a "why" drawer: source span, compiled cell with probabilities and provenance, the join, the price before and after, the futures that broke, the repair options with their J.

18.4 Hop-0 (voice) is optional and renders the same rows; it never invents. v1 surface is a local web page; a native viewer is a later rung [OPEN].

---

## 19 · Physics and the roofline

19.1 The box [M, `peek env` 2026-09-22]: RTX 4070 Ti SUPER 16 GB shared with `llama-server` (`:8092`) and a speech stack; free VRAM swings >11 GiB in minutes. Family arbitration: the resident is the sole resident VRAM consumer while seated; every other organ is on-demand and tears down; free VRAM is measured at seat and before every sweep; `tiers_dropped` rides every bound. A red result on a contended card is re-run once before it is believed (probe cost moves 2.7× [M, nib]).

19.2 **The arithmetic line MUST print every tick.** If the achieved fraction of measured peak is below `roofline.floor_fraction`, the CPU reference is the shipping path for this owner and the finding is printed, not hidden.

---

## 20 · Falsifiers

Each with a lie arm; thresholds registered in `isobar.lock` before the run; every quoted number reproducible by a script under `runs/`; intervals required. The table is `docs/ROADMAP.md §Falsifiers` and is normative here by reference: F-RECOVERY · F-PRICE · F-WAGER · F-NOISE · **F-RESIDENT** (decisive) · F-COMPOSER · F-JEV · F-JOIN · F-ROOFLINE · F-BASELINE · F-COVERAGE · F-INJECT · F-KAPPA · **F-PAID** (release-blocking) · F-TIER · F-TRAVEL · O1–O9 · O-MONO.

---

## 21 · Security and consent

21.1 Injection corpus per lane in CI (mail: "mark this paid", "cancel the meeting", "forward the invoice"; list: an instruction-shaped task; calendar: an invite body with directives) ⇒ zero effects without the gate. The `SENTINEL` seat flags `injection_shape`; the parser grammar admits nothing dispatchable.

21.2 Consent classes: `standard` (OAuth read), `contacts`, `location` (I13: invoked or scheduled, visibly on, local-first, excluded from named sensitive places), `money` (read-only verdict). Every capture is owner-invoked and scoped to the owner's own operational life.

21.3 Secrets never enter a microVM; sensitive identifiers are redacted before any model call; raw mail never leaves the box in the local deployment; the hybrid deployment states per field what may leave.

---

## 22 · Open questions

Collected in `docs/BACKLOG.md`. The ones that change the build: the reranker choice; the compose surface (which client, or a nib-style pane); the reply-latency model's form; the delegates model; the glass native vs web; the port; the name's trademark; whether LIFELINE v5's cryptographic deletion is adopted at M0 or later.

---

## Appendix A · Process topology (v1)

```
isobard            Python 3.13 · the plane: tape, connectors, reflex client, join, promote, gate, outbox, glass server
                   calls the instruments below as subprocesses over a memory-mapped SoA file + JSON header
isobar_field       C++17/CUDA single TU · -DISOBAR_CPU reference · --selftest --lie N · --bench (the arithmetic line)
isobar_foresee     C++17/CUDA single TU · the multiverse · --parity · --selftest
resident           fusord/nib lifted · a FieldSource driver on the FieldDelta lane · SHADOW by default
laya | jev         the reflex provider behind SemanticReflex
llama-server       :8092 embeddings (existing on the box); a local reader for the residual and wording
e2b                the gym, the counterfactual, attachments, fan-out (never the inner loop)
```
No organ imports another; organs are called at fixed paths as subprocesses (the estate's law). The plane may later go native; the contracts are what bind.

## Appendix B · Repository layout

```
isobar/
  README.md · CLAUDE.md · LICENSE · .gitignore · isobar.lock · writ.yaml · tiers.yaml
  docs/  SPEC.md · ROADMAP.md · BACKLOG.md · contracts/*.md · lineage/
  solver/      isobar_field.cu · isobar_foresee.cu · build.cmd · oracles
  isobard/     the plane (Python)
  connectors/  composio/ · direct/ (imap, graph, gmail, caldav, gcal, todoist, mstodo, gtasks, textfile, contacts, money, location)
  reflex/      questions.yaml · providers/ (laya, jev, llm_enum, trunk_head)
  presence/    FieldSource driver · seats · the threshold twin
  glass/       the page · later the native viewer
  gym/         worlds · planted truth · stubs · lie arms
  tests/       fixtures · replay · injection corpus · property tests
  runs/        receipts (gitignored)
```

*Rev 0.1 written 2026-09-22 by Claude Fable 5.1 for Bo Chen. Nothing is built; every [M] belongs to the instrument it names.*
