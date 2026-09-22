# BACKLOG — open items, newest section first

*Rev 0.1 · 2026-09-22. An item leaves this file only by a decision recorded in `docs/ROADMAP.md §Decisions log` or by a clause in `docs/SPEC.md` moving from [OPEN] to [SPECIFIED].*

## Decisions that change the build (resolve before the stage that needs them)

| # | question | needed by | notes |
|---|---|---|---|
| B1 | **The compose surface.** Where does the composer seat live: a nib-style pane that owns the reply, a browser extension over the mail client's editor, or ISOBAR's own compose box in the glass? | M2 | nib's surface is built and measured; an extension reaches the owner's existing client but cannot guarantee the no-network build gate. The gutter needs keystroke-grain percepts either way. |
| B2 | **The reranker.** A local cross-encoder (bge-reranker class) vs the reflex itself over the top-8 (`same_as_candidate_k` ×8) vs none (exact + lexical + embed only, accepting the residual's error as a priced risk). | M0 | The reflex-as-reranker keeps one provider and gives a calibrated p per candidate for free; measure precision on the residual before adding a model. |
| B3 | **Reply-latency and arrival models.** Per-counterparty empirical quantiles with a class prior vs a fitted hazard model. | M1 | Start with quantiles (median, p10, p90, n) per counterparty, class prior below n = 5; a fitted model only if F-WAGER's calibration demands it. |
| B4 | **Delegates.** The schema allows N seats; v1 builds one. What is the minimum for a two-person business (owner + assistant): a second seat with its own calendar lane and a `DELEGATE` move, or a single seat with the assistant's calendar as reduced capacity? | M1 | The second human is where single-writer folds break (the 2026-09-18 critique); if a delegate edits the calendar directly it is evidence, not state, so the fold survives — but the licence per class must be per seat. |
| B5 | **The glass: web page vs native.** v1 is a local page served by `isobard`; the estate prefers one native exe. | M0 (page), later (native) | Decide the native rung after M3; the page is enough to run F-RECOVERY. |
| B6 | **The port.** `isobard` needs one; `:8092` (embeddings), `:8094` (cortexd), `:3080` (dsh) are taken. Proposal: `:8096`, pending the family `ports.lock`. Check `peek ports` first. | M0 | |
| B7 | **The name.** ISOBAR was a Dentsu digital-agency brand (retired ~2022); the mark may persist. Fallback: GLASS. | before any public artefact | Working name stays ISOBAR until then. |
| B8 | **Deletion.** Adopt LIFELINE v5 §15 (per-record keys, taint closure, tombstones, generation keying, the off-box witness) at M0, or plain tape + scope masks at M0 and crypto-shred later? | M0 | Adopting at M0 is cheaper than retrofitting a chain that already runs over plaintext. Recommendation: chain over ciphertext from M0, taint closure at M4. |
| B9 | **Slot granularity and hours.** 30-minute slots over 07:00–21:00 is the default; owners with split shifts or 15-minute consults need `slot_min: 15`. | M0 | M scales linearly; the arithmetic line will show the cost. |
| B10 | **The `support_split` and `T` at personal radius.** 3.0 is RAYFORMER's measured crossover, borrowed. Measured on the gym at M0: es_mean 126 — with a mostly free horizon every row can sit almost anywhere, so "contested" describes the calendar's emptiness, not the placement's doubt; and T = 0.25 is likely too hot for a person's week. | M1 | Publish the support histogram at several T; pick the trough; consider support relative to the row's feasible cells rather than absolute. |
| B15 | **The roofline model for small lattices.** The lift's arithmetic line counts per-pair bytes (embedding re-reads); for a working set that fits in cache those never reach DRAM. M0 keys the regime on the working set (< 32 MB ⇒ cache-resident, no bandwidth claim). The multiverse kernel at M1 is where the roofline should be measured, per universe-batch. | M1 | |
| B17 | **A `tick` verb that rehydrates a plane from the tape.** M0.5 runs ticks in-process after a scan (`scan --ticks N`); a standalone `isobar tick` must rebuild the plane's state from the tape (the folds) and continue. The fold exists (`replay_verify` rebuilds commitments, findings and captures); the rehydration of the joiner's indexes and the dependency graph is the work. | M1 | |
| B18 | **The IMAP and SMTP legs, live.** The hand's IMAP backend is written on stdlib and refused correctly on the island; the SMTP reply leg is unbuilt (the reply channel at M0.5 is the file and the tape receipt). Exercise both against a real mailbox the owner owns; on a send fault, hold the effect and raise the island for that lane. | first real owner | |
| B19 | **The duplicate floor.** 0.75 is a placeholder above the gym's noise (0.60 admitted a Priya pair at 0.63). Measure the trough of the top-1 cosine distribution on real rows (B10's discipline) and set it from the measurement. | first real owner | |
| B20 | **The reply's `moved` line and later resolutions.** Replies are composed once, after the first field; at scan time there is no prior field so `moved` carries the stock prices only, and a capture that resolves on a later tick is on the tape but not in its reply file. On a tick, the reply channel should send a second typed line (`resolved #… on <tick>`) for captures that changed state. | M4b | |
| B16 | **The mbox lane and real exports.** M0's direct adapter reads mbox/eml; Gmail Takeout and Outlook exports carry RFC 2047 headers, HTML-only bodies, and attachments — `_body()` takes text/plain only. Add an HTML-to-text fallback and an attachment manifest (names, sizes; contents open only in a branch, M5). | first real owner | |
| B11 | **What counts as "acted on" for grading a wake.** Opened the card within `t`; accepted the pipper; edited the draft; moved the block; replied to the counterparty. | M3 | The grade is exterior only if the machine did not select the sample; salt the wakes shown. |
| B12 | **Laya vs Jev as the default provider.** Open and local vs commercial API with the vendor's calibration claim. | M0 | Laya by default (no egress, no cost); Jev as a plugin measured on the same 200 emails. |
| B13 | **Tentative events and multi-calendar.** Capacity at acceptance probability; which calendars count as the owner's capacity vs information only. | M0 | Owner policy in `isobar.lock` (`calendars: [{id, role: capacity|info}]`). |
| B14 | **E2B credentials and the local branch backend.** Tests must not require E2B; a local container/WSL backend for the gym. | M5 | `peek sandbox` exists on the box. |

## Later rungs (not v1)

- Audio (the largest coverage hole: spoken promises) — consent lane, T3 in the master architecture.
- Images (receipts, whiteboards) with bounding-box provenance.
- Place-triggered attention ("you are at the vendor").
- The learned effect heads (Qwen-Drive shape, trained on the record of accepted effects) with the deletion condition "every required effect already has an adapter".
- The parametric tier (the disposition precipitated into weights) under LIFELINE v5's penetration licence.
- Pooled licences across tenants (L4) — needs ≥ 20 tenants on one class.
- The native viewer.

## Known hazards (from the estate's receipts)

- Two Windows processes appending to one file lost 66/78/73 of 120 rows, both exiting 0 [M, scriptorium QC] — one writer per segment, enforced by the OS.
- Model-emitted character offsets: 0 % usable; verbatim quotes: 87.2 % located [M] — the fence accepts quotes, never offsets.
- A hard-coded peak bandwidth was 1.216× overstated [M, ledger_lattice wave 3] — measure it every run.
- Finishing Sinkhorn on a column pass fails O1/O3 [M] — finish on a row pass.
- Louvain/Leiden partitions reshuffle across seeds (ARI 0.73–0.86) [M] — ISOBAR does not partition.
- The probe cost moves 2.7× with what else is on the card [M, nib] — re-run a red result once.
- A driven window that takes the keyboard eats the operator's typing [M, nib] — the composer's driver must be no-activate.
