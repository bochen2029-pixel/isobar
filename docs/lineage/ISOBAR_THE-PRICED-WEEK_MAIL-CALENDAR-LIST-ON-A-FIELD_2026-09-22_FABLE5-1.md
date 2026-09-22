# ISOBAR — the priced week
## Mail, calendar and the list as one field: priced every tick, rehearsed across ten thousand futures, watched by a mind that is home, and spoken about only when the glass falls

**Date:** 2026-09-22 · Dallas · Claude Fable 5.1 for Bo Chen
**Status:** design / architecture / blueprint, [SPEC] throughout unless tagged. Name provisional (a barometer on a ship is "the glass"; isobars are the lines of equal pressure on the chart; sailors say *the glass is falling* when weather is coming and nobody had to ask).
**Scope:** three lanes — mail, calendar, task list — brand-agnostic (Gmail/Outlook/IMAP; Google/Outlook/CalDAV; Todoist/MS To Do/Google Tasks/plain text); **three registries the field reads — people, places, money** (§4a) — seeded by one small read each and grown by the lanes; the clock; one owner, optional delegates. SMS joins mail as the same semantic lane with a different provenance.
**Revision:** r1 (2026-09-22, later the same day): the three registries added; the implementation repo is `C:/isobar` and its `docs/SPEC.md` is normative where the two disagree.
**Mandatory organs, each doing the one thing only it can:** a **CUDA solver** (CPU reference, GPU interactive tier — the idea is the same on either), **JEV/Laya-class typed reflex**, **FUSOR** resident presence, **embedder + reranker**, local and frontier **LLMs**, **E2B** microVMs, and the **Qwen-Drive** head pattern for effects.
**Register:** **[M]** measured on this box, source named · **[V]** verified primary · **[D]** derived by arithmetic · **[SPEC]** designed · **[BET]** a bet with its kill.

---

# 0 · Thinking out loud — how this was derived

**0.1 · The three lanes are three places where fragments of one object live.** Mail: the evidence of promises made, received, and discharged. Calendar: capacity, plus the appointment class of promise. The list: the owner's own statements of what they owe. The master architecture already ruled this: the commitment is canonical; the lanes are evidence, capacity, and projection. So "process three streams" is the wrong problem. The problem is: what machine *holds the object* the three surfaces stand for, and what does each organ do to it that no other organ can.

**0.2 · What is actually hard, once you hold the object.** Not classification. Not scheduling one week, which is one CP-SAT solve in milliseconds. The hard things are relational and continuous: *does this request contend with that promise for the same Thursday; what is that Thursday worth right now; if I promise Friday, in what fraction of plausible futures do I keep it; which one move now buys the most robustness across those futures; and did the world just move in a way that deserves a word, when no message arrived to say so.* Every one of those is either a relation over the whole field or an integral over futures. Learned organs guess at them. A solver computes them.

**0.3 · What each mandatory organ uniquely does.**

| organ | the one thing only it does | what it must never do |
|---|---|---|
| deterministic code | exact ids, dates, amounts, spans, thread keys | judge |
| **JEV / Laya** | compile prose into ~20 typed fields with **calibrated** probabilities, in one parallel pass, at ~33–100 ms, without a field that is not in the schema | generate text; decide alone |
| **embedder → reranker** | the join: large universe → candidates → decision-relevant order; the unkeyed duplicate no key reaches | merge two money-bearing identities on similarity alone |
| **the solver** | compute the relational facts exactly: contention, price, support, contradiction, and the integral over futures; **the one relational instrument that needs no training** | read prose; be trusted where its inputs are fiction |
| **FUSOR** | be present: judge at boundaries on the free tail of the ingest pass, hold, un-say, and leave a record of every hold with its margin | be the event loop; write state; widen authority |
| local LLM | read the residue JEV could not type; word a computed intent | invent feasibility |
| frontier LLM | genuinely novel semantics; a second judge of distinct lineage on irreversibles | own state, policy, or the licence |
| **E2B** | fork a whole machine: the counterfactual fortnight, foreign attachments, the gym, fan-out | produce evidence; hold authority |
| Qwen-Drive pattern | emit in the surface's own action space — a schedule delta, a draft intent — never prose about it | be the intelligence |

**0.4 · The first inversion — price, not priority.** Every task manager ranks. A rank is a total order with no units; you cannot compare a request against a meeting against a promise on it. The dual of a transport problem is the **shadow price** of a cell: what one more unit of that hour is worth to the whole set of commitments, recomputed every tick, with a band. Pricing is what turns *no* into arithmetic: "Thursday afternoon is priced 0.83 and binding; accepting this breaks #17 in 61 % of futures." The ledger lattice already prints the price vector for a company [M, `ledger_lattice.cu` §11]. Nobody has printed it for a person.

**0.5 · The second inversion — computed urgency.** HELM's law says business priority is not "how urgent the email sounds," and then leaves the replacement to a policy layer. The replacement is arithmetic: an email's weight is **‖Δv‖, the movement of the price vector when its row entered the lattice.** An email that moves no price is noise, however loud; a two-line note that flips a support from decided to contested is the most important thing in the inbox. This is also the anti-alert-fatigue mechanism, because it is a property of the field, not of the message.

**0.6 · The third inversion — the resident watches the field, not the inbox.** The inbox fails FUSOR's own litmus test: it is sparse and small-state, the regime where residency loses [SEPARATION §16]. But the *field* is a live stream with a during: time consumes slack, so the duals rise on soon-slots without any message, supports drift, silence prices grow. Compile the field's deltas into a typed lane and seat the resident on *that*. Then the tick makes the world move, the trunk sees it, and the hold/emit judgment fires on evidence rather than on a clock or a caller — I16 made mechanical. And the trunk stays tiny: it reads two hundred floats' worth of lines per tick, never an email body.

**0.7 · The coupling — probabilities as distributions, the duals as the IR.** JEV's calibrated *p* per field is **not a threshold; it is the sampling distribution the multiverse integrates over.** A 0.6-confidence "due Friday, hard" is hard in 60 % of futures; a 0.7 join to #17 and 0.2 to #22 is sampled per future; the price of the slot reflects the expectation and the band reflects the doubt. Nothing is collapsed until the gate. Then arrived outcomes grade the probabilities (did the counterparty treat it as hard?) and the duration priors — the TRAIN caller — so the record appreciates. And the solver's outputs — the price vector, the support spectrum, the contradiction list — are the **machine-native intermediate representation of a week**: ~200 floats every organ reads instead of the calendar. The LLM never sees forty commitments in prose. That is R = 1 for the state plane, and it is the "clever sequence": every organ's output is the next organ's input *type*.

**0.8 · What the solver makes possible that nothing else can.** A person's week is not a schedule; it is a distribution over schedules, because durations, arrivals, replies and overruns are uncertain. The **multiverse** — thousands of sampled futures, each re-solved, ranked by a human-authored writ, the best future's first move as the pipper, kept only if reality confirms — is the flight computer [M, `flight_computer.cu`: ~18k universes/s on this card at 4,000 universes] pointed at one life. It answers *can I promise this* (survival across futures), *what one move now* (the pipper), and *what is this hour worth* (the dual), all with bands, in the time it takes to type the reply. Without the parallel solver you get one point estimate, nightly. With it you get the band on every price and the survival on every promise **as it is being typed** (§8.2). That is the thing that could not exist before.

**0.9 · The name.** The rendered surface is the two-week calendar drawn as a pressure map — the duals as isobars over the hours, commitments as particles whose halo is their support, silence as a rising column on the right. The system reads the glass continuously and speaks when it falls.

---

# 1 · The one idea

> **A person's operational life is a field with prices. Mail, calendar and the list are sensors on it. Every message is a perturbation whose weight is how far it moved the prices. Every promise is a wager rehearsed across ten thousand futures before it is sent and graded when it lands. A resident mind watches the field, not the inbox, and holds until the glass falls. The solver is not downstream of cognition; it is the encoder of state that every other organ reads.**

Three laws hold it together, inherited and sharpened:

- **Compute the relational, judge only the residue.** Contention, price, support, contradiction, survival: computed exactly by the solver. Is-this-a-promise, which-kind, how-firm: typed by the reflex with calibration. What-does-this-unusual-thing-mean: the LLM, rarely. *(The arity law, with a fourth option added: relational facts can be computed.)*
- **Uncertainty flows through, never collapses early.** Probabilities are sampled, not thresholded, until the deterministic gate.
- **Silence is a row.** Every hold, with its margin; every wager, with its forecast; every effect, with its inverse. The record is the moat; the cognition is the demo.

---

# 2 · The objects — what flows between organs

Everything below is typed, so that "piped" means typed handoff and not prose.

```
Observation   { id, lane ∈ {mail, cal, list, tick, compose}, src_rev, occurred, ingested, payload_ref, digest,
                intake_trust ∈ {operator, trusted, untrusted} }                       -- immutable; the tape
Cell          { field → (value, p, provenance ∈ {HIGH, MOD, LOW_absent, LOW_conflict}) } -- JEV's output, ~20 fields
Join          { candidates: [(commitment_id | actor_id | thread_id, p)], method ∈ {exact, lexical, embed→rerank→jev} }
Row           { entity, cls, kind, dur ~ (opt, nom, cons), src, t_release, t_due, p_hard, work, dep, inc_cell,
                law_flags, emb_int8[128], p_join[...] }                               -- a commitment as the lattice sees it
Field         { v[M] prices, u[N], es[N] support, risk[N] breach forecast, contra[], Δv, ‖Δv‖, arithmetic_line }
Future        { seed, sampled (dur, due_hard, join, arrivals, reply_latency, overrun, calendar_truth), J, breaches[] }
Foresight     { per commitment: survival p ± band; per candidate move: J_mean, J_std, J_pess; pipper; paired_backtest? }
FieldDelta    a compact typed line per tick for the resident's lane, e.g.
              [field] Thu14 0.61→0.83 BIND · #17 sup 1.2→4.1 CONTESTED · #22 breach .61 · wait:Lopez .40 · Δv .37
Hold          { boundary_id, seat, margins{emit, hold, wake, ask}, verdict, reason(closed), gear, aired?, killed? }
Verdict       one of SILENT · FLAG · ASK · DRAFT · ONE_CLICK · ACT · HOLD · RECHECK, with a closed reason
Intent        typed effect in the surface's action space: ScheduleDelta | DraftIntent | TaskDelta   (the heads)
Effect        { target, payload, inverse | irreversible, precondition (state version), idempotency_key, hold_window }
Wager         { effect_id, promise_row, forecast_survival ± band, horizon, graded_at?, outcome? }
Grade         { human reaction ∈ {sent_as_is, edited(diff), discarded, undone, ignored, acted_within(t)} | arrived outcome }

-- the three registries (§4a): rows the field reads, never lanes with their own machinery
Actor         { id, kind ∈ {person, org, agent}, identities[], tier (OWNER POLICY), relations[], places[],
                arrival_rate, reply_latency ~ history, silence_price_floor, provenance[] }
Place         { id, name, aliases[], geometry(lat, lon, radius), role ∈ {home, work, client, vendor, site, frequent},
                actors[], hours?, travel_edges[(place, minutes)], confirmed_by ∈ {owner, inferred}, provenance[] }
MoneyObject   { id, kind ∈ {quote, proposal, invoice, bill, payment, credit}, counterparty, amount_minor, currency,
                issued, due, status ∈ {draft, sent, acknowledged, accepted, declined, paid, partially_paid, overdue, unknown},
                status_source ∈ {verdict_connector, mail_inference, owner}, evidence[], commitment_id? }
```

**The IR of a week** is `Field` plus the top of `Foresight`. It is what the resident reads, what the LLM's draft context is built from, what the glass draws, and what the gate checks budgets against. No organ above the solver reads the calendar.

---

# 3 · The pipeline — three clocks, three paths

## 3.1 · The event path (an email, a calendar change, a list edit)

```
EVENT
 │
 ├─ 0 CODE       ids · thread · in-reply-to · dates · amounts · invoice numbers · spans           [µs]  exact
 ├─ 1 REFLEX     JEV: ~20 typed questions in ONE pass, calibrated p, provenance tag             [~40 ms]
 ├─ 2 JOIN       exact keys → lexical → embed (candidates) → rerank → JEV "same as k?" ×3      [~30 ms]
 ├─ 3 RESIDUAL   only if needs_judgment ∨ provenance LOW_conflict: local 9B schema extraction;
 │               frontier only for genuinely novel semantics                        [0.3–3 s, rare]
 ├─ 4 PROMOTE    deterministic: Cell + Join → Row with DISTRIBUTIONS, candidate/accepted by policy
 ├─ 5 FIELD      solver: re-price (duals only) · support spectrum · contradiction stencil · Δv     [ms]
 ├─ 6 FORESEE    solver: K futures × H periods, warm-started from resident duals; survival; pipper [0.1–5 s]
 ├─ 7 PRESENCE   FUSOR field-watch seat reads the FieldDelta line at a boundary: hold or emit, with margin
 ├─ 8 GATE       deterministic: verb from licence × exposure × inverse window × budget; nothing learned
 ├─ 9 HEADS      typed Intent in the surface's action space (ScheduleDelta | DraftIntent | TaskDelta)
 ├─ 10 WORDING   local LLM verbalises DraftIntent (mail only); frontier jury on irreversibles
 ├─ 11 OUTBOX    inverse recorded BEFORE the effect; hold window; receipt
 └─ 12 GRADE     the human's reaction (sent / edited+diff / discarded / undone) and arrived outcomes
                 → TRAIN: durations, arrivals, latencies, JEV reliability curves, licences, κ
```

Order is not fixed law: for a bulk backfill the reflex runs before the join (classify-then-retrieve, the stream is large and the question is a filter); for a reply on a known thread the join runs first (retrieve-then-classify, the judgment needs prepared context). The router logs the gear and the order per event.

## 3.2 · The tick path (no message)

```
TICK  →  5 FIELD  →  6 FORESEE (reduced K)  →  7 PRESENCE  →  8 GATE
```
No reflex, no join. Time moved the release and due windows relative to now; the duals of soon-slots rose; a WAITING item's silence price grew; a support crossed from decided to contested. The FieldDelta line has content; the resident judges it. **This is how it notices without being asked**, and it is the one path a turn-based system cannot have.

## 3.3 · The compose path (the human is typing a reply, accepting a meeting, adding a task)

```
KEYSTROKES  →  nib-style ingest (percepts at thought boundaries)
            →  1 REFLEX in flight on the forming promise (is_commitment · due · hardness · effort)
            →  fork the lattice, add the forming Row, 6 FORESEE warm-started at small K       [~0.1–0.3 s]
            →  7 PRESENCE composer seat: margin in the gutter BEFORE send
                  "you are promising Friday · survival 0.41 ± 0.07 · Monday 0.94"
            →  un-say: if the next words change the promise, the flag is withdrawn and the withdrawal is a row
```
The reply is a **wager**; it is rehearsed while it forms. This is the estate's un-say applied to the human's own promise, and it is the thing that hits home: the machine tells you, as you type, what your promise is worth.

---

# 4 · The field — the lattice for one life

Lifted from `ledger_lattice.cu` [M, oracles O1–O6 with lie arms, 2026-09-06], re-shaped for one owner. Four transpositions carried whole: the plan is never materialised (duals only: `u[N] + v[M]`, O(N+M) resident); int8 storage, fp32 accumulation, round-trip cosine an oracle; the counterfactual is a mask, not a copy (two arms, one canvas); locality is the lattice (contention is checked on a stencil, identity on a second stencil keyed by entity).

## 4.1 · Geometry

```
seats   : the owner (+ delegates, if any)                                     usually 1
slots   : H days × working half-hours (e.g. 14 × 28 = 392), horizon rolling
cells   : seat × slot                                                         M_real = 392
stocks  : UNPLACED       backlog — carrying cost, finite capacity            (the densify signal)
          UNADJUDICATED  needs the owner to decide — adjudication bandwidth  (the ASK budget, priced)
          WAITING        with a counterparty — the price of their silence    (NEW; Chase reads it)
M       = seats·slots + 3
rows    : open commitments (active, waiting, candidate) — N ≈ 40–200 for a busy owner
cap[c]  : half-hour capacity minus fixed calendar allocations, minus policy (focus blocks, no-meeting slots, hours)
law     : −inf masks, unoverridable by anything learned: kind × slot (calls in hours; deep work in focus blocks;
          nothing external in a protected block; travel buffers around location-bearing appointments)
```

**The two arms, one canvas.** `arm 0` = the incumbent: what the calendar and the list *say* (each row's `inc_cell`). `arm 1` = the solver: where the row *should* be. One bitmask, no second state; ticked in pairs. The gap between the arms is the value of re-wiring before anyone acts — for a person, the difference between your list's order and the priced order.

## 4.2 · The one dynamics source

```
place_cost(i, c):
  stock columns   → their finite carrying / adjudication / waiting cost (the T17 fix: every column takes the dual update)
  law[cls_i, c]   → −inf                       (before normalisation; nothing learned overrides)
  arm mask        → −inf in the solver arm for unlicensed seats
  duration fit    → −inf if slot + dur_i > horizon; −inf before t_release
  compat          → int8 dot(emb_i, slot_key_c)/√D      (deep vs shallow vs comms slots; the slot has a "kind" key)
  lateness        → −late_penalty · max(0, finish − t_due) · hardness_i
  counterparty    → tier weight from OWNER POLICY (importance is policy, never inferred)
  all over T      (transport temperature: the entropic regulariser)
```
The Sinkhorn, the support meter, the contradiction stencil and the report all read this one function; oracle O1 checks two independent traversals agree.

## 4.3 · The six outputs, every tick

| # | output | what it is for a person |
|---|---|---|
| 1 | **price vector** `v[M]` → per hour, per day, per stock | *which capacity is binding, now.* "Thursday 14–17 is priced 0.83." The stock prices: how much backlog is costing; how much is stuck waiting on you (UNADJUDICATED); how much is stuck waiting on *them* (WAITING) |
| 2 | **support spectrum** `exp(H_i)` per commitment | *decided vs contested.* Low support: the placement is obvious, the class is automatable, no word needed. High support: genuinely contested, the human decides. The split point is re-measured here, never borrowed (RAYFORMER's 3.0 is the first thing to re-measure [M, `ledger_lattice.cu` §11]) |
| 3 | **contradictions** | OVERCOMMIT (an hour holds more than it can) · DOUBLEBOOK (one entity, two places) · DEPENDENCY (starts before its predecessor can finish) · DEADLINE (finishes late) · **DUPLICATE** (the same promise in mail and in the list, no shared key — the unkeyed one, via embedding, reported separately with a confidence and a sampled audit, never folded into the keyed count) |
| 4 | **the arithmetic line** | bytes moved per tick, achieved GB/s, fraction of *measured* peak. Below the floor it is a DDR5 job — printed either way (§16) |
| 5 | **Δv** and ‖Δv‖ | *the event's computed weight.* Stored per event on the tape. The resident's lane and the glass's highlight both read it |
| 6 | **breach forecaster** `risk_i = price(landing cell) × slack deficit` | free by-product of the support pass; the AT-RISK bay is sorted by it |

## 4.4 · Calendar truth without location

With only three lanes, capacity is *inferred*, not measured. The capacity-coverage gate from HELM stands: density of work blocks, completions vs calendar, the owner's self-report → `coverage ∈ {UNKNOWN, WEAK, USABLE, STRONG}`. In ISOBAR this is not a switch that hides the price map; it is a **sampled variable in the multiverse** — `calendar_truth ~ Bernoulli(p_cov)` per future widens every band — so "your week fits" is never claimed at WEAK, and the glass shows the prices with their widened bands and the label *capacity uncertain*. Location, if the owner ever adds it, is the exterior grader of this variable; without it the grader is completions.

---

# 4a · The registries — people, places, money

Three things a person or a small business needs the machine to *know* that no lane carries as a stream: who matters, where things are, and whether the money moved. The master architecture's ruling holds: **these are registries, not lanes.** They are seeded by one small read each, grown by mail and calendar, corrected by the owner, and read by the field as rows. They have no agents, no loop of their own, and no authority. Each can be wrong in a typed way: a wrong tier is a policy the owner set; a wrong place is one confirmation away; a wrong payment state is a connector fault labelled as such.

## 4a.1 · People — what gives the prices weight

**Seed:** a contacts read (consent class `contacts`). **Growth:** every identity mail and calendar produce, merged by the resolution ladder — exact id → exact identity (email, phone) → thread → domain + name → lexical → embedding → reranker → owner; **never merged on similarity alone when money or a promise is involved.** **Tier is owner policy, never inferred**: "mom", "Lopez", "VIP client", "vendor we can wait on" are rows the owner sets once (importance is policy, not semantics).

What the field reads from it: the **tier weight** in `place_cost` (a promise to a tier-1 counterparty prices its lateness higher); the **silence price** per counterparty in the WAITING stock (Lopez's silence is not priced like a newsletter's); the **arrival and reply-latency models** per counterparty class in the multiverse (§5.1); and the **relations** the writ can name (a promise to a client of a partner inherits the partner's tier). For a person this is *who mom is and that she is tier 1*; for a small business it is clients, vendors, their importance and their history of answering.

## 4a.2 · Places — the exterior grader of the calendar, and the spatial lattice

**Seed:** addresses parsed from mail signatures, calendar locations and contact cards; home and work confirmed by the owner. **Growth:** every located calendar event and every address a counterparty writes. **Travel edges** from a routing service, cached, between every pair of places that appear in the same horizon. **The location lane exists only under consent** (I13: user-invoked or scheduled, visibly on, local-first, never ambient, excluded from named sensitive places) and only if the owner wants what it buys.

What the field reads from it: **travel as cells consumed** — an allocation at a client across town followed by one at a vendor fifteen minutes later consumes the travel time between them, and the stencil gains **K_TRAVEL**: two allocations at different places closer in time than their edge is a collision the calendar alone cannot see; **travel buffers** as −inf masks around location-bearing appointments; and, when location is consented, **`calendar_truth` becomes a measurement** — was the owner where the calendar said, when it said — instead of the sampled inference of §4.4. That single conversion is what makes the segment whose calendars are fiction servable. Later rung: place-triggered attention ("you are at the vendor; here is what is open with them").

## 4a.3 · Money — the verdict lane that stops the worst error

**Seed:** commercial objects compiled from mail by the reflex (quotes, proposals, invoices, bills, payment requests) with amounts from deterministic extraction. **The verdict:** one payment or accounting connector when connected — Stripe, QuickBooks, Xero, a bank or card feed — whose state **supersedes** any mail inference. **The law**, carried from HELM and enforced in the stencil: *mail silence is not proof an invoice is unpaid.* Without the connector, every money-like finding is typed `payment status not connected` and is never upgraded to "money owed"; with it, **K_PAID** — a chase never fires on an object the verdict source says is paid — is a release-blocking oracle with a planted lie.

What the field reads from it: **discharge evidence** for payment commitments (a payment closes the row); the **found-money partition** the glass shows — confirmed receivable · apparent-overdue (mail-only, labelled) · proposal pipeline · vendor credit — **never summed into one figure**; the WAITING stock's price for money items (the price of a client's silence on an invoice is the invoice's amount × its age × the counterparty tier); and for a person, the card or bank feed as discharge of purchases and bills. It is the cheapest exterior verdict there is, and for a small business the one that prevents the single worst thing the system can do: chasing an invoice that was paid through a channel mail cannot see.

## 4a.4 · The registry law

Registries are rows, not lanes. Every row carries provenance and `confirmed_by`. No registry has authority, a loop, or a model of its own; the reflex and the join write candidates into them, the owner confirms or corrects, the field reads them. The clock is the sixth thing and it is a lane: the tick that moves the field with no message.

---

# 5 · The multiverse — every promise a wager

Lifted from `flight_computer.cu` [M, 16/16 oracles; CPU/GPU parity to ~1e-7; ~18k universes/s on this card at 4,000 universes]: one predictor, three callers — DRIVE (render the period = the plan), FORESEE (fan out futures → rank → the pipper), TRAIN (when reality arrives, render backward). One shared `__host__ __device__` rollout leaf: the CPU reference and the GPU kernel are the same code, not the same equations.

## 5.1 · A future

One thread (or one block) per universe = a candidate move × a rollout. Each universe samples, with counter-based RNG (same seed ⇒ bit-identical):
```
dur_i          ~ three-point (opt, nom, cons) per row, from class prior → business history → owner correction
due_hard_i     ~ Bernoulli(p_hard_i)                   JEV's calibrated p, not a threshold
join_i         ~ Categorical(p_join_i)                 which commitment this evidence really belonged to
arrivals       ~ per-counterparty-class rate, learned from the tape (mail that creates commitments)
reply_latency  ~ per-counterparty history               (when will Lopez answer; the WAITING stock's clock)
overrun        ~ meeting-class prior                    (the 30-min call that takes 50)
calendar_truth ~ Bernoulli(p_cov)                       §4.4 — or MEASURED from the location lane when consented (§4a.2)
travel_t       ~ place edge (minutes) ± routing noise    consumed as cells between allocations at different places
payment_state  ~ the money registry's verdict when connected; else the mail inference at its stated p (§4a.3)
```
then integrates H periods: arrivals land, the field re-prices (8 warm iterations, not 400), the writ is scored, the world steps. Futures are hash-keyed, so **a candidate arm and a do-nothing arm see exactly the same world** — paired common random numbers — which is what lets the baseline be an arrival, not a forecast.

## 5.2 · The writ — human-authored, never fitted

```
J = w_hard·breaches_hard + w_soft·breaches_soft + w_ext·external_promises_broken
  + w_backlog·unplaced + w_wait·waiting_age + w_ask·asks_of_owner + w_churn·moves
  + w_buffer·(−contingency) + w_frag·focus_fragmentation + w_overtime·overtime
```
Lexicographic in practice: hard breaches, external promises, fewest renegotiations, least churn, buffer preserved. The weights are owner policy in a file; the multiverse ranks by `J_mean + β·J_std` (pessimism is a dial, not a model).

## 5.3 · The action menu

`HOLD` (do nothing — always present, the baseline arm) · `DECLINE` (a request, with the computed reason) · `COUNTER` (the slot with maximum survival) · `MOVE` (an internal block) · `PROTECT` (make a block unavailable to reactive work) · `NUDGE` (a WAITING item whose silence price crossed the bar — Chase) · `SPLIT` · `DELEGATE` (to another seat, if any) · `DEFER` (internal due) · `RENEGOTIATE` (external — always ASK) · `DROP` (irreversible — always ASK).

The best future's first move is **the pipper**. It is shown with its forecast and its band. It is **kept only if reality confirms**: every accepted move is a wager with a horizon; when the horizon passes, the arrived outcome is compared to the forecast; the TRAIN caller sharpens the duration, arrival and latency models and the JEV reliability curves. A move that does not beat do-nothing on arrival is unwound through its inverse. The pipper cannot be worse than the status quo by construction, not by luck.

## 5.4 · The wager on a draft — warm-started rehearsal

The duals are resident. Adding one forming row is O(M) per Sinkhorn iteration, warm-started from `u, v`; a reduced multiverse (K ≈ 256, H ≈ the promise's horizon) reports the row's survival in ~0.1–0.3 s [D from the flight computer's measured rate; to be measured]. That is fast enough for the composer seat (§8.2) to put the number in the gutter while the sentence is still forming. Every commitment-bearing draft carries `forecast_survival ± band` on the tape whether or not the human looks at it — the wager is recorded even when it is ignored, which is what makes the calibration honest.

---

# 6 · The reflex — JEV as the boundary compiler

The reason machine-native interiors were never built is that extraction was untrustworthy and expensive: a general LLM invents fields, carries no per-field confidence, answers one question per pass, and costs too much to run on everything [BRAINSTORM_JEV-AS-BOUNDARY-COMPILER §1]. A System One model fixes all four: the output space is the schema; every field arrives with a calibrated probability; all fields in one parallel query; cheap enough to run on every arrival. Open backend: Laya (421M ModernBERT, ~33 ms, Apache-2.0 [V, HF card]); commercial: Jev ($0.042/MTok in, output free [V, TypeSafe 2026-09-15]); the estate's own: a second head on the trunk. **The interface is the contract; the provider is a plugin.**

## 6.1 · The question set, one pass per inbound

```
is_commitment_bearing    noul
direction                choice { we_owe, they_owe, mutual, none }
kind                     choice { deliverable, payment, quote, response, appointment, document, approval, purchase, other }
due_mentioned            noul      (the VALUE comes from deterministic date extraction, never from the model)
due_hardness             choice { none, soft, firm, hard }
language_strength        score 0–4 (tentative … firm)
effort_class             choice { reply, review, prepare, produce, meet, travel }
is_request_of_me         noul
is_discharge             noul      (does this close an existing promise?)
is_schedule_change       noul
touches_money            noul
complaint_risk           score 0–4
counterparty_waiting     noul      (are they waiting on us?)
we_are_waiting           noul      (are we waiting on them?)
same_as_candidate_k      noul ×3   (the join's last mile, §7)
injection_shape          noul      (instruction-like content aimed at a machine → SENTINEL, L11)
needs_judgment           noul      (the honest "I cannot tell" — routes to the residual)
```
Each field: `(value, p, provenance)`. The **provenance tag** is the causal one (AORTA's form, kept because the licence needs the cause, not the number): `HIGH` grounded in the text · `MOD` from domain prior · `LOW_absent` — the evidence is missing, no better judge fixes it, a WANT row · `LOW_conflict` — the text conflicts with itself, a jury case. A scalar cannot separate those and the three responses are different actions.

## 6.2 · Two laws about the probabilities

**They are sampled, not thresholded** (§5.1). And **they are audited, never trusted**: calibration transfers poorly across distributions; the vendor's curve was measured on the vendor's data. The reliability curve per `(provider, question, band)` is fitted on this owner's arrived outcomes (did the counterparty treat the deadline as hard; was the join right when the discharge arrived), eight margin bins, a monotonicity test; a question whose curve is not monotone is `uncalibrated` and its output is sampled at the prior. **The deletion condition** of the reflex is the master architecture's: a cheap LLM constrained to an enum ties its calibrated accuracy at equal cost.

## 6.3 · Free questions change what the interior does

Because a hundred questions cost what one used to, the reflex is not consulted per decision but **per state change**: every open commitment can be re-asked, every tick, "has anything in the last day's mail discharged you?" — one parallel query over the day's compiled cells. The model leaves the decision loop and enters the representation loop. Nothing learned then disposes; it only describes.

---

# 7 · The join — embedder and reranker as address translation

Exact keys first (thread id, in-reply-to, invoice and quote numbers, calendar ids, email addresses) — the master architecture expects ≥ 95 % of joins here, which is the embedder's deletion condition. For the residue:

```
embed(evidence)            → top-64 candidates over commitments, actors, threads   (resident int8 scan, ms)
rerank(evidence, cands)    → top-3, decision-relevant order
JEV same_as_candidate_k ×3 → a calibrated p per candidate; the join is a DISTRIBUTION, sampled in §5.1
```
The reranker discriminates; the embedder proposes; the model adjudicates only residual ambiguity; **vector similarity alone never merges two money-bearing identities** [HELM §19]. The second stencil (§4.3 row 3) is the embedder's other job: the unkeyed **duplicate** — the same promise recorded once in mail and once in the list, joinable by nothing but its embedding — bucketed by entity (identity is not local in the lattice; contention is) and reported as a candidate with cosine, graded on recall against planted pairs, precision by sampled audit.

---

# 8 · Presence — FUSOR on the field

Lifted from `fusord.cpp` by way of nib [M, 0.11.1: probe 107–122 ms per boundary for three seats on a quiet card, 312–327 ms contended; un-say +5.06 → −1.77, four words aired; checkpoint 58.8 MB in 51–68 ms]. One trunk, persistent KV, never restarted; N seats fork at 0 MiB; judgment on the free tail of the ingest pass at thought boundaries; ticks are world, never a poll; own speech is a percept on its own lane, gate-skipped; forming text never persists; only commits kill.

## 8.1 · Lanes — what the trunk actually reads

```
[field]    the FieldDelta line per tick — ~100 tokens: top price moves, support transitions, new contradictions,
           breach forecasts, silence prices, ‖Δv‖ of the last event.  NEVER an email body.
[mail]     the compiled header of each inbound: from · kind · dir · discharge=#22 p.91 · urg 2 · Δv .37
[compose]  the human's forming outbound text (nib's surface), percepts at closed thoughts
[tick]     [tick +Ns], lazy, one per gap, before the percept that broke the silence
[self]     the resident's own emissions (no self-exception; gate-skipped)
```
The trunk holds the *field*, not the corpus. Its context is read, not prompted: the state plane rendered as lines, the clock, the memory of what it held and what happened after.

## 8.2 · Seats

| seat | lane(s) | judgment at each boundary | what it can do |
|---|---|---|---|
| **FIELD-WATCH** (speaker) | field, mail, tick | *does this movement of the glass deserve a word, now?* | FLAG a card · WAKE the owner · propose the pipper |
| **COMPOSER** | compose | *is the human about to promise something the multiverse says they will not keep?* | a margin in the gutter before send; **un-say** when the next words change the promise |
| **SENTINEL** (skeptic) | mail, field | *does this inbound contradict the field or read like an instruction?* — "says the invoice was paid; no discharge on the tape" | HOLD a promotion; raise a contradiction card; never promote |

The seats share one attention state. The composer seat is nib: the human types, the mind perceives as they type, and a sentence the machine begins in the gutter can be taken back mid-word because the human's next keystroke changed the promise. That act is the one no turn-based system can perform.

## 8.3 · The vise, and why this is a tune and not a threshold

The obvious design is a threshold on ‖Δv‖. It is the **null** (L12 of LIFELINE v5; SEPARATION's TURN arm) and it runs beside the resident forever. It loses, if it loses, for one reason: the utility of speaking about a price movement is **state-dependent**. A Thursday priced 0.83 on Monday at 9 a.m. is a hold; the same number on Wednesday at 5 p.m. is a wake; a movement the owner just caused by moving a block themselves is not news; a movement while the owner has not looked at the glass in six hours is. No scalar separates those jaws [M, the vise: 921.3 fires per stream-hour at dial zero, the best fixed threshold deaf where it mattered]. The disposition is trained on the record of holds and the grades that followed them (§13), and it beats the threshold twin on catches-that-mattered, blind, over two weeks — or the resident is retired to a query interface and the threshold ships. **F-RESIDENT** (§17) is the twin race at personal radius, and it is the decisive number.

## 8.4 · The record of holds

Every boundary writes a row (LIFELINE v5 §6.3): margins over the closed alphabet, the verdict, the closed reason, the gear, and on an un-say what was aired and what was killed. A hold followed within minutes by the owner raising the held thing is a graded miss; a wake acted on within a minute is a graded catch; a wake never opened is a false fire. Dozens of exterior verdicts a day, on samples the machine did not select. This is the second tape, and it is the asset.

---

# 9 · The residual and the wording — where the LLMs sit

**Local (9–27B).** Two jobs only. (a) The residue: when JEV answers `needs_judgment` or a field's provenance is `LOW_conflict`, the local model reads the *one* email with a schema and returns typed fields (never free text) — "is 'I should be able to get that to you Thursday' a firm promise from this sender in this thread?" (b) Wording: the DraftIntent (§11) is verbalised into the counterparty's language — accepted repair, computed date, disclosed reason, tone policy, prior thread — and nothing else; the LLM never invents feasibility, never rewrites the plan.

**Frontier (one seam, budgeted, fingerprinted).** Genuinely novel semantics that neither the reflex nor the local model can type; template compilation at setup (the owner's tone, standing policies compiled into the wording templates once); and the **jury on irreversibles** — two judges of distinct provenance lineage must agree on the exact effect bytes under a cap the machine cannot raise (governord). Disagreement among frontier models may *narrow* authority or force a HOLD; agreement never widens it.

**What no LLM does here:** read forty commitments in prose (it reads the Field); decide urgency (‖Δv‖ does); decide feasibility (the multiverse does); decide whether to speak (the resident does); hold authority (the gate does).

---

# 10 · The gym and the branch — E2B

Two fork primitives, never conflated: inside the card, `seq_cp` forks the trunk's attention state at 0 MiB (the resident's probes, the un-say, the draft rehearsal); outside it, a Firecracker microVM forks a whole machine (~1 s boot, ~1 s fork carrying running processes, pause/resume with no TTL [V, E2B docs]). E2B belongs in the gym and the counterfactual; it is never the inner loop; nothing generated inside a branch becomes an observation or authority-earning evidence.

1. **The gym before any model.** SEPARATION's discipline: a synthetic owner with planted truth — a silent quote, an invoice paid through a system mail cannot see, a calendar that is fiction, a promise buried in a "maybe Thursday" — and **stub cognition with competence knobs** (StubReflex(c), StubPresence(c,k)) so thousands of runs cost nothing and the pipeline is proven to respond correctly to cognition quality before a model touches it. Every oracle carries a lie arm.
2. **The counterfactual fortnight.** "Should I take this project?" → fork the plant (lattice, models, connectors in replay mode) into a microVM, add the project, fly fourteen days of arrivals at the owner's measured rates, **paired** against do-nothing under identical hash-keyed arrivals. Several scopes = several forks in parallel. The answer is a paired outcome with a band, and it is labelled *simulated*.
3. **Attachments.** Anything that is not plain text or PDF opens in a microVM; text comes out; the VM dies. Connectors never run inside it; live credentials never enter it.
4. **CPU fan-out for the multiverse.** When the local card is contended (it is shared), K futures spill across N microVMs — one process per universe batch, the branch manifest pinning the cut. The CPU reference leaf is the same code (§5), so parity holds.
5. **Training runs.** The disposition tune on the hold record and the JEV reliability fits run detached; the shipping resident is never trained in place (epochs are generations).

---

# 11 · The heads — the Qwen-Drive shape for effects

Qwen-Drive's lesson is not "a VLM can drive"; it is that a broadly pretrained representation can be tapped below the language head and connected to a domain-native output geometry [V, arXiv 2609.00111]. Here the domain is three surfaces, and each gets a head that emits **in the surface's own action space**, never prose about it:

```
calendar_head → ScheduleDelta { event_id | new, from_slot, to_slot, attendees?, reason_code }
mail_head     → DraftIntent   { thread, act ∈ {accept, decline, counter, nudge, confirm, request}, proposed_date?,
                                disclosed_reason ∈ policy set, tone ∈ policy set, commitment_row? (→ wager) }
task_head     → TaskDelta     { create | complete | defer | reorder, row_id, due?, note? }
```
In v1 the heads are **deterministic templates over the solver's repair** (HELM §32's "computed intent"): the pipper is already a typed move; the head is a projection of it into the surface's schema. The *learned* head — trained on the record of accepted effects — is a later rung with its own deletion condition (every required effect already has an adapter). The prose renderer (§9) exists only at the mail surface, because the counterparty is a human; the calendar and the list receive the typed delta directly. Two representation crossings — model writes a sentence, a parser turns it into an API call — are removed, because the consumer is a machine.

---

# 12 · The gate, the outbox, the licence, κ

**The gate** is deterministic, contains nothing learned, can only narrow, emits a closed verb with a closed reason, and checks budget and exposure last. Its inputs: the licence for *this class on this surface*, the exposure cap, the inverse window, the state version the intent was planned against (stale ⇒ RECHECK), the coverage state, and the support of the row (contested ⇒ never ACT). There is no `allow`.

**Classes, ordered by verdict latency and inverse window, never by felt risk** [the 2026-09-18 correction]:

| class | inverse | verdict source | latency | ceiling |
|---|---|---|---|---|
| create / reorder a task | yes | the owner's edit | minutes | ACT early |
| move an internal block | yes | the owner's undo | minutes | ACT early |
| protect a focus block | yes | undo | minutes | ACT |
| draft a reply | n/a | sent-as-is / edited (diff) / discarded | minutes | DRAFT from day one — **the dense grader** |
| nudge a WAITING item | hold window (10 min), then compensable | reply or silence | days | ONE_CLICK → CANARY |
| chase an apparently overdue invoice | compensable | payment or complaint | days–weeks | **requires the money verdict** (§4a.3); without the connector DRAFT only, labelled `payment status not connected` |
| accept / counter a meeting with an external party | compensable | attendee acceptance; the meeting happens | days | ONE_CLICK |
| send a commitment-bearing reply | **irreversible** | kept / slipped | days–weeks | ASK, with the wager shown |
| renegotiate / drop an external promise | irreversible | counterparty | weeks | ASK forever, jury on send |

**The outbox** is the single writer: the inverse is recorded before the effect fires; every effect carries an idempotency key and a precondition; a send waits its hold window during which the un-say is the owner's.

**The licence ladder** per class is earned on exterior verdicts of executed choices, sampled by a salt the machine cannot read, narrows on any evidence. The dense grader for a solo owner is their own reaction to every draft: sent as-is is weak evidence (people clear queues); an edit with its diff is strong evidence and the training signal, the same object. Rare classes (drop, renegotiate) are **permanently undelegatable at personal volume** and the honest product says so on the box.

**κ** — attention consumed per outcome — is printed weekly. A resident whose wakes rise without outcomes rising demotes to a query interface the same week. For a solo owner κ is not a metric; it is the P&L.

---

# 13 · The tape

Append-only, hash-chained, one writer per segment. Row kinds: `observation · cell · join · promotion · field (per tick, as deltas) · foresight (pipper + forecast) · hold · verdict · intent · effect · receipt · wager · grade · calibration · licence · policy · correction`. Every table is a fold; same tape ⇒ byte-identical tables (the replay oracle). The owner's corrections — "that wasn't a promise", "this takes 30 minutes not four hours", "never auto-chase this account" — are typed rows that feed retrieval, calibration, the duration model, policy and the gym; **no weight is fine-tuned in place**.

What compounds on this tape and nowhere else: the price history of every hour, the wager history with outcomes, the hold record with grades, the reliability curves per question, the owner's duration distributions per class. A better foundation model makes every one of them more valuable and none of them free.

---

# 14 · The glass — the interface

The two-week calendar drawn as a **pressure map**: the dual of each half-hour as colour (isobars), so a binding Thursday afternoon is visibly high pressure before anything is scheduled into it. Commitments as particles at their argmax cell with a halo whose radius is their **support** — decided placements are points, contested ones are fuzzy — so the owner sees at a glance which of their promises are settled and which are in play. Contradictions as red links. On the right, the three stocks as columns whose height is their price: backlog, *waiting on me*, *waiting on them* (with the top three silences named). Under it, **the pipper**: one proposed move, its forecast, its band, one key to accept, and the do-nothing arm's number beside it. Hysteresis: a particle moves only when its risk class, deadline or repair changes materially, never because the objective improved by 1.7 %.

The four bays (NOW · AT RISK · NEXT · WAITING) are the same field projected as a list, ordered by slack when coverage is USABLE and by due otherwise — the list lane rendered back, with the owner's edits entering as observations from source `owner`.

**Hop-0**, if the owner wants it, is voice over the same rows: "what's binding this week" reads the price vector; "can I take this on" runs the counterfactual and reads the survival; "push Henderson to Friday" is a TaskDelta through promotion. It renders and compiles; it never invents.

**The "why" drawer** on every card: the source span, the compiled cell with its probabilities and provenance, the join, the price before and after, the futures that broke, the repair options with their J. No black-box alerts.

---

# 15 · A Monday — the machine in motion

09:02 · Lopez, a client, writes: *"Thanks — if we could get the revised proposal by Thursday that would really help, we present Friday."* CODE finds the thread and the date. JEV in one pass: `is_commitment_bearing .96 · direction we_owe .93 · kind deliverable .91 · due_hardness firm .71 / hard .24 · effort produce .88 · counterparty_waiting .95 · discharge .02`. The join binds it to the open proposal commitment #17 (exact thread) at .98. PROMOTE writes the row with `p_hard = .24` and `dur ~ (3h, 5h, 8h)` from the owner's history for "prepare proposal, Lopez-class". FIELD re-prices: Thursday 09–17 rises 0.61 → 0.83 and becomes the binding day; #17's support goes 1.2 → 4.1 (contested, because the 5-hour nominal no longer fits the two free blocks); the DEADLINE stencil forecasts breach 0.61; ‖Δv‖ = 0.37, the largest movement this morning. FORESEE at K = 4,096: HOLD breaches #17 in 61 % of futures; MOVE the Wednesday internal review to Tuesday 14:00 drops that to 12 % with one internal move and zero external renegotiations; COUNTER with Friday-morning drops it to 4 % but touches the client. The pipper is MOVE. The FIELD-WATCH seat reads the FieldDelta line at the boundary; the margin clears zero (a binding day and a contested external promise, 09:00 on a Monday, the owner has the glass open) → FLAG. The gate reads the class (move internal block: licensed ACT at canary), the inverse (undo), the state version → ACT with a 10-minute hold. The calendar head emits `ScheduleDelta{review, Wed 14:00 → Tue 14:00, reason: protect #17}`. The card says: *"Lopez wants the proposal Thursday. I moved Wednesday's review to Tuesday so it fits; breach risk 61 % → 12 %. Undo?"* The owner does nothing; ten minutes later the move fires; the inverse is on the tape.

09:11 · The owner starts a reply: *"Absolutely, you'll have it Wednesday end of d—"*. The COMPOSER seat, reading the forming sentence, gets JEV in flight (`we_owe, deliverable, due Wednesday, hard .6`); the warm-started rehearsal at K = 256 says survival 0.41 ± 0.07 for Wednesday, 0.88 for Thursday noon. The gutter shows it before the sentence is finished. The owner backspaces to *"Thursday by noon."* The seat's flag is withdrawn mid-word; the withdrawal, the aired words and the killed remainder are a row. The reply goes out as a **wager**: forecast 0.88, horizon Thursday 12:00.

Tuesday 16:40 · No message. The tick lane says the Tuesday review ran fifty minutes over (calendar lane: the event was extended); slack on #17 fell; Thursday's price is 0.79 and the survival of the wager is now 0.74. The FIELD-WATCH seat holds — the number moved, the class did not, the owner is in a meeting — and the hold is a row with its margin. Wednesday 08:00 the same seat wakes: *"Lopez proposal: 74 % on the Thursday promise; a 90-minute block Wednesday 15:00 takes it to 93 %. Protect it?"* One key. Thursday 11:20 the proposal is sent (the discharge is JEV `is_discharge .97` on the outbound, joined to #17); the wager is graded KEPT; the duration observation (6.5 h) enters the owner's history; the reflex's `.24 hard` is graded against Lopez's Friday presentation having happened (hard was right); the licence for "move internal block" gains one graded outcome. Nothing was configured. Nothing was asked that the machine could compute.

---

# 16 · Physics — and the honest roofline

**This box** [M, `peek env` 2026-09-22]: RTX 4070 Ti SUPER 16 GB, shared with `llama-server` and a speech stack; free VRAM swings by >11 GiB within minutes. The resident 9B Q5 loads in 4.3–8.1 s; a three-seat probe costs 107–122 ms quiet, 312–327 ms contended [M, nib]. Laya: ~33–40 ms per state [V]. The resident int8 scan: 2.02 ms over 2M chunks [M, connectome].

**The field, per tick** [D]: N = 120, M = 395, 40 warm Sinkhorn iterations → 3.8 M pair-evaluations ≈ 1.1 GB moved → ~3 ms on the card, ~30 ms on the CPU. **For one owner the re-price is a CPU job, and the arithmetic line will say so.**

**The multiverse** [D, anchored on the flight computer's measured ~18k universes/s for its smaller universes]: K = 4,096 × H = 14 × 8 warm iterations over 120 × 395 ≈ 22 G pair-evaluations ≈ **1–5 s on the card as a first cut** (one thread per universe, strided scratch), ~20 s across 16 CPU cores, ~90 s single-threaded; the composer's reduced rehearsal (K = 256, short horizon, warm duals) ≈ 0.1–0.3 s on the card. The named next moves in `flight_computer.cu` — one *block* per universe with a shared-memory Sinkhorn, coalesced layout — are where a further 5–10× lives.

**What the GPU buys, stated exactly:** the band on every price and the survival on every promise **interactively** — after every email, during every keystroke — instead of a point estimate nightly. Below K ≈ 500 a CPU carries one owner; a team's lattice (5 seats, 600 rows) or the E2B-less design point needs the card. **The kill condition is printed every tick**: if the achieved fraction of *measured* peak bandwidth is under the floor, the card is decoration for this owner, the CPU reference ships, and every idea in this document survives unchanged — price not rank, wager not promise, field not inbox.

**Determinism**: counter-based RNG, fixed-point accumulators, no float atomics, `memcmp`-identical replay under a seed; CPU/GPU parity as an oracle; every reported quantity carries its sum of squares — a number without its band is not a number.

---

# 17 · Falsifiers — each with a lie arm

| falsifier | kills | measure | lie arm |
|---|---|---|---|
| **F-RECOVERY** (T0 gate) | *the object is worth having* | ≥ 60 % of pilot owners find ≥ 3 unknown items at owner-audited precision ≥ 0.80 in the first ten minutes | plant nothing; the scan must find nothing |
| **F-PRICE** | *the dual predicts breaches* | AUC of a slot's price 3 days out vs whether the commitment landing there slipped | shuffle prices across slots; AUC must fall to 0.5 |
| **F-WAGER** | *survival forecasts are calibrated* | reliability curve of forecast survival vs promises kept, 8 bins, monotone; over ≥ 4 weeks | shuffle forecasts; calibration must break |
| **F-NOISE** | *‖Δv‖ is the event's weight* | high-‖Δv‖ mail is acted on within the day and ≈0-‖Δv‖ mail is ignored by the owner too (their own reading log as grader) | randomise Δv; the correlation must vanish |
| **F-RESIDENT** (decisive) | *presence beats the threshold twin* | FIELD-WATCH vs a swept threshold on ‖Δv‖ (perfect boundaries, same field, same model), catches-that-mattered and false fires, blind, 2 weeks, both grains | give the twin the resident's disposition; the arms must tie |
| **F-COMPOSER** | *the in-flight wager changes what gets promised* | promise-kept rate and edit-before-send rate, gutter on vs off, paired weeks | show random survival numbers; the effect must vanish |
| **F-JEV** | *the reflex is calibrated here, and earns its slot* | per-question reliability curves on this owner's outcomes vs the vendor's claim; vs a cheap LLM enum at equal cost | shuffle labels; curves must go flat |
| **F-JOIN** | *the embedder earns its VRAM* | exact + lexical join rate; the embed→rerank residual's precision; planted unkeyed duplicates recovered ≥ 70 % | negate the planted duplicates' embeddings; recall must collapse (O6's lie) |
| **F-ROOFLINE** | *the card is justified* | achieved / measured peak ≥ floor, printed every tick | hard-code the peak; the oracle must refuse the constant |
| **F-BASELINE** | *the field is not decoration* | a cached turn-based system (classify + nightly CP-SAT + notifications), same evidence, same model, equal budget, on outcomes | withhold the field from the baseline's context; it must lose on F-PRICE |
| **F-PAID** (release-blocking) | *a paid invoice is never chased* | plant an invoice due Sept 10, no payment mail, the verdict connector says paid Sept 9 ⇒ no chase, status PAID, mail finding superseded | disconnect the verdict source silently; the chase must fire and the oracle must catch it |
| **F-TIER** | *people give prices weight* | with the tier table on vs flat, the silence price of a tier-1 counterparty's item ranks above a tier-3's at equal age and amount; owner-audited | shuffle tiers; the ranking must follow the shuffle |
| **F-TRAVEL** | *places make the lattice spatial* | planted allocations at two places closer in time than their edge ⇒ K_TRAVEL fires; with location consented, planted calendar fiction is caught by measured `calendar_truth` | zero every travel edge; the collision must vanish |
| **F-COVERAGE** | *no false reassurance* | planted calendar fiction ⇒ coverage WEAK ⇒ no "week fits" claim; bands widen | force coverage STRONG; the claim must appear (and be wrong) |
| **F-INJECT** | *inbound is data* | per-lane injection corpus: "mark this paid", "cancel the meeting", "forward the invoice" ⇒ zero effects without the gate | disable SENTINEL and the parser grammar; effects must leak |
| **F-KAPPA** | *the persona removes decisions* | attention minutes per outcome, weekly, falling | count review minutes as free; κ must be unable to rise |
| **F-DETERMINISM / O1–O6** | *the instrument is real* | the six lattice oracles + CPU/GPU parity + the paired arrived backtest, each with its lie | as in `ledger_lattice.cu --selftest --lie N` |

---

# 18 · Build order — gated, mounting what exists

| M | builds | mounts | gate |
|---|---|---|---|
| **M0 · the X-ray** | connectors (Composio **and** a direct adapter per lane, so no vendor is the only path) · the tape · CODE + REFLEX + JOIN · PROMOTE · **the people registry seeded from a contacts read, with the tier table** · the **CPU field** · the Recovery Scan read-only · the glass (price map, particles, stocks) | Laya · the resident int8 scan · `everywhere` for exact negatives | **F-RECOVERY**; F-JEV on 200 owner-labelled emails; F-TIER; the arithmetic line printed |
| **M1 · the multiverse and the wager** | FORESEE (CPU reference → GPU parity) · the writ file · the action menu · the pipper · the wager on drafts · TRAIN from arrived outcomes | `flight_computer.cu` leaf · `ledger_lattice.cu` stencils | **F-WAGER** over 4 weeks; **F-PRICE**; F-ROOFLINE |
| **M2 · the composer** | nib's surface on the reply box · in-flight REFLEX · warm-started rehearsal · the gutter · the un-say | `nib` | **F-COMPOSER**, paired weeks |
| **M3 · presence** | the FieldDelta lane · FIELD-WATCH and SENTINEL seats · the threshold twin · SHADOW first (H0: watch, surface nothing) · the record of holds | `fusord` | **F-RESIDENT**, 2 weeks blind — **or the resident is retired and the threshold ships** |
| **M4 · authority** | the gate · the outbox with inverses and hold windows · the licence ledger with the salt · ONE_CLICK sends · κ weekly | governord's seam | ≥ 20 one-click per class, edit distance ≤ 0.15, zero high-severity licence outcomes, κ falling |
| **M4a · places and money** | the places registry (addresses → confirmed home/work → travel edges) · K_TRAVEL in the stencil · travel buffers · the money registry with one verdict connector · K_PAID · the found-money partition on the glass · the location lane behind consent (optional) | a routing service (cached) · Stripe / QuickBooks / Xero / bank feed adapter | **F-PAID** (release-blocking); **F-TRAVEL**; `calendar_truth` measured vs sampled, printed side by side where location is consented |
| **M5 · the gym and the branch** | E2B stub-sweep gym with planted truth and lie arms · the counterfactual fortnight · attachment opening · CPU fan-out | `C:/e2b` | the stub sweep is smooth and monotone; a planted paid-invoice-the-mail-cannot-see never chases |
| **M6 · the heads and the tune** | typed heads over the repair · the disposition tune on the hold record · JEV reliability refits · learned durations per class | the WSL `emit` rig | F-NOISE; the tuned resident beats the threshold twin by more than in M3, or the tune is a funeral, printed |

**M0 + M1 is the product.** It prices the week and rehearses promises with no resident, no gate, and no tune, on a CPU if the roofline says so. Everything after it is presence, authority and learning, each mounted only past its gate.

---

# 19 · What is new, what is borrowed, what is not claimed

**New here.** The dual vector as the intermediate representation of a week that every organ reads instead of the calendar. ‖Δv‖ as computed urgency replacing judged urgency. JEV's probabilities as the multiverse's sampling distributions rather than thresholds, graded back by arrivals. The resident seated on the field's stream rather than the inbox, so the tick moves the world. The composer seat rehearsing a promise as it is typed, with the un-say. Silence priced as a stock, so Chase is arithmetic. The wager as the unit of record for a person's promises. The solver named as the relational instrument that needs no training.

**Borrowed, with receipts.** The lattice, the stocks, the two arms, the stencils and the six oracles from `ledger_lattice.cu`; one predictor, three callers, the multiverse, the pipper and the paired arrived backtest from `flight_computer.cu`; the loop, the seats, the seam, the un-say, the tick and the checkpoint from `fusord.cpp` via nib; the boundary-compiler role and the fourth gear from the Jev brainstorms; the commitment as canonical object, promotion, the capacity-coverage gate, the duration model and the four bays from HELM; the licence ladder, κ, the salt and the no-allow gate from the master architecture and governord; the two fork primitives from the resident-enterprise algebra; the head shape from Qwen-Drive.

**Not claimed.** That residency beats a threshold on ‖Δv‖ for one owner — that is F-RESIDENT and it is unrun. That the card is justified for one owner — the roofline decides and the CPU path is first-class. That the reflex's calibration holds on this distribution — it is refit per owner. That capacity is truthful without location — coverage is sampled and bands widen. That rare classes ever license — they do not, at personal volume, and the box says so. That any number in this document has met a real inbox — every [M] belongs to the instrument it names; ISOBAR's own first numbers arrive at M0.

---

# Appendix A · The connector contract (brand-agnostic)

```ts
interface Connector {
  id: 'gmail' | 'outlook' | 'imap' | 'gcal' | 'outlook_cal' | 'caldav' | 'todoist' | 'mstodo' | 'gtasks' | 'textfile' | …;
  lanes(): ('mail' | 'cal' | 'list' | 'contacts' | 'location' | 'money')[];   // the last three feed registries, not the field directly
  backfill(since, cursor?): AsyncIterable<Observation>;   // resumable, idempotent by (source, external_id, src_rev)
  delta(cursor): AsyncIterable<Observation>;
  capabilities(): EffectCapability[];                     // target · reversibility class · INVERSE · hold window
  consentClass(): 'standard' | 'contacts' | 'location' | 'money';
}
```
Money connectors are **verdict sources**: read-only in every rung of this document; a payment effect is `irreversible` and is not in v1's capability tables at all.
Two implementations per lane from day one (a hosted broker and a direct/open connector); reversibility lives in the capability table and nowhere else; `src_rev` monotone (equal = no-op, lower = refused).

# Appendix B · `isobar.lock` skeleton

```yaml
lattice:   { horizon_days: 14, slot_min: 30, hours: "07:00-21:00", stocks: [UNPLACED, UNADJUDICATED, WAITING],
             T: 0.25, late_penalty: 1.0, iters_tick: 40, iters_future: 8, support_split: TODO_measure (borrowed 3.0) }
writ:      { w_hard: 8, w_soft: 2, w_ext: 4, w_backlog: 3, w_wait: 1, w_ask: 0.5, w_churn: 0.7, w_buffer: 1, w_frag: 0.5,
             w_overtime: 2, beta_pess: 1.0 }                                   # OWNER POLICY; never fitted
multiverse:{ K: 4096, K_compose: 256, H: 14, rng: counter_based, parity_oracle: required, pipper_keep: paired_arrived_only }
reflex:    { provider: laya | jev | trunk_head, questions: 17, calibration: per_owner_per_question_8bins_monotone,
             uncalibrated_action: sample_at_prior, deletion_condition: llm_enum_ties_at_equal_cost }
join:      { exact_first: true, embed_topk: 64, rerank_topk: 3, jev_same_as: 3, duplicate_cos: measured_trough,
             merge_on_similarity_alone: forbidden }
presence:  { lanes: [field, mail, compose, tick, self], seats: [FIELD_WATCH, COMPOSER, SENTINEL], mode_default: SHADOW,
             twin: threshold_on_delta_v_swept, kill: F-RESIDENT }
gate:      { verbs: [SILENT, FLAG, ASK, DRAFT, ONE_CLICK, ACT, HOLD, RECHECK], allow: absent, contested_never_acts: true,
             classes_ordered_by: [verdict_latency, inverse_window] }
licence:   { salt: governor_held, grader: owner_reaction_and_arrivals, corrections_over_approvals: true,
             rare_classes: undelegatable_printed }
roofline:  { floor_fraction: 0.40, peak: measured_stream_triad_never_constant, cpu_reference: first_class }
tape:      { chain: blake2b-128, writer: one_per_segment, replay_oracle: byte_identical_tables }
```

---

*One field, three sensors, one solver that encodes it, one reflex that compiles into it, one mind that watches it, one gate that disposes. It prices your week, rehearses every promise before you make it, and speaks when the glass falls. Everything it says is a number with a band; everything it does carries its undo; everything it held is on the tape with the margin it held by. Run the roofline. Run the twin race. Print both.*
