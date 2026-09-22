# CLAUDE.md — session rules for ISOBAR

You are implementing **ISOBAR**: a personal operations plane over mail, calendar and the task list, with a solver at its centre that prices the owner's horizon every tick and integrates over sampled futures, a typed reflex that compiles prose into calibrated cells, and a resident that watches the field. The machine-wide rules in `C:\Users\user\.claude\CLAUDE.md` apply on top (forward slashes in shell commands; heredocs are blocked by a hook — author files with Write, change them with Edit; never load this shared box).

Read `README.md` → `docs/SPEC_r0.2.md` (normative; `docs/SPEC.md` is r0.1, lineage) → `docs/ROADMAP_r0.2.md` (the rung you are on and its gate) → `docs/contracts/CHANGES_r0.2.md` (the contract deltas to apply under the lints) → `docs/BACKLOG.md` before writing a line. Read these before touching the organ they own:

- `C:/fusor1/ledger_lattice/ledger_lattice.cu` — **the field. Lift it; do not re-derive it.** The four transpositions, the one dynamics source, the six oracles with lie arms, the T17 fix, the convergence curve, the arithmetic line.
- `C:/fusor1/FlightComputer/src/flight_computer.cu` — **the multiverse. Lift it.** One predictor, three callers; the shared `__host__ __device__` rollout leaf; the paired arrived backtest; parity.
- `C:/nib` (`CLAUDE.md`, `docs/SPEC.md`, `src/resident.cpp`, `src/wire.cpp`) — **the resident. Mount it.** The seed is byte-frozen; the loop is lifted from `fusord.cpp`, not re-derived.
- `C:/AGI/LIFELINE_V5_…md` §6.3 — the hold row, verbatim.
- `C:/HELM_COMMITMENT_CONTROL_PRODUCT_AND_IMPLEMENTATION_SPEC_v1.0_2026-09-21.md` — the canonical object, promotion, the coverage gate, the critical tests (paid invoice; calendar fiction; collision; found money).

## Hard rules

1. **Nothing learned writes state, disposes, or gates.** `promote/`, `gate/`, `solver/` import nothing from `reflex/`, `llm/`, `presence/`, `connectors/`. The lint runs in CI and fails the build.
2. **The plan is never materialised.** Resident solver state is `u[N] + v[M]`. Two arms, one canvas, one bitmask. A second canvas is a bug.
3. **Probabilities are sampled, not thresholded, before the gate.** A `p` from the reflex or the join enters a row as a distribution the multiverse draws from. A threshold on `p` anywhere above the gate is a bug.
4. **Every effect carries its inverse before it fires**, or is classed irreversible and asks. Reversibility comes from the connector's capability table, never from the caller. There is no `allow`.
5. **Every oracle carries a lie.** `--selftest --lie N` runs oracle N against a deliberately corrupted world; an oracle that passes its own lie is broken and the build says so.
6. **A number without its band is not a number.** Fixed-point accumulators with sums of squares; counter-based RNG; no float atomics; `memcmp`-identical replay under a seed; CPU/GPU parity as an oracle; the peak bandwidth measured every run, never a constant.
7. **The CPU reference is first-class.** Every solver feature builds and passes under `-DISOBAR_CPU` first. The GPU is the interactive tier and the roofline decides. `--bench` prints the arithmetic line and the kill condition either way.
8. **The tape is the only truth.** Every observation, cell, join, promotion, field delta, hold, verdict, effect, wager and grade is a row. Same tape ⇒ byte-identical tables; `replay --verify` is a standing gate. One writer per segment.
9. **Presence is SHADOW by default.** The resident surfaces nothing until the operator flips the switch, and the switch is a tape row that no model or policy may write. The threshold twin on ‖Δv‖ runs beside it forever.
10. **Inbound is data.** No lane's content is an instruction; extraction prompts frame content as data; outputs are schema-constrained; model output is parsed under one grammar; nothing in it is dispatched on. The injection corpus per lane runs in CI.
11. **Mail silence is not proof.** Without the money verdict, money-like findings are labelled `payment_status: not_connected` and never upgraded. `K_PAID` is release-blocking.
12. **Tier is owner policy.** No model proposes a tier except as a candidate row the owner confirms. Importance is never inferred from sentiment.
13. **No organ is imported.** `everywhere`, `chunker`, `nib`, the embedding server, Laya, E2B are called at fixed paths as subprocesses or over their own contracts. Their versions are pinned in `isobar.lock`.
14. **The writ is hand-authored and never fitted.** `writ.yaml` is owner policy; the multiverse ranks by it; no training run touches it.

## Build and test discipline

- **One milestone per session.** Gate → receipt under `runs/` → commit before the context is half spent. Every gate step asserts on a return code; every test binary prints `N/N`; every quoted number has a script that reproduces it.
- **Versioned edits.** Never rewrite an existing source file whole; use surgical edits that fail atomically on a mismatch; write only new files whole; commit at every green step.
- **Stubs before models.** Every statistic is first produced in gym mode with stub cognition and competence knobs; a real model attaches only for the decisive ablation.
- **Numbers carry their date and their grain.** Keystroke-to-gutter, tick-to-price, K per second, VRAM taken and returned. A red result on a contended card is re-run once before it is believed.
- **One model on the card at a time.** The box is shared with `llama-server` and a speech stack; never kill another process to free VRAM.
- The devlog (`docs/devlog.md`, created at M0) is a lab notebook: what was tried, measured, decided, and the traps the day they bit. Never rewritten; corrections appended.

## Refusals

A ranked list presented as the product: no — the price map is. A threshold on a reflex probability above the gate: no. A learned component in the gate, promotion or the solver: no. A chase on an invoice the verdict source has not confirmed unpaid: no. A resident that surfaces anything in SHADOW: no. A frame-rate, a K-per-second or a catch-rate quoted without the script that produced it: no. Shipping the resident before the threshold twin has raced it blind: no — that is the whole point of the order.
