# solver/ — the two instruments

**Nothing here is built.** This directory will hold exactly two single-translation-unit programs, each lifted from an instrument that already passes its oracles on this box:

| file | lifted from | adds |
|---|---|---|
| `isobar_field.cu` | `C:/fusor1/ledger_lattice/ledger_lattice.cu` [M, O1–O6 with lies, 2026-09-06] | the WAITING stock; `tier_weight` and travel cells in `place_cost`; `K_TRAVEL`, `K_PAID` in the stencil (a second and third locality key: place pair, money object); `Δv` against `--prev`; the `FieldDelta` line emitter |
| `isobar_foresee.cu` | `C:/fusor1/FlightComputer/src/flight_computer.cu` [M, 16/16, parity ~1e-7] | the personal action menu; sampling of `due_hard`, `join`, `calendar_truth`, `travel`, `payment_state`; `--rehearse` warm-started from resident duals; `--backtest` paired arrived |

The contract is `docs/contracts/solver.md`. The rules that bind the code are in `CLAUDE.md` (the plan is never materialised; one dynamics source; fixed-point accumulators; measured peak; every oracle carries a lie; CPU reference first).

## Lift discipline

Copy the source file, rename, and change it by surgical edits that are each recorded in `docs/devlog.md` with the line they touched and why. Do not re-derive the Sinkhorn, the stencil, the RNG or the rollout leaf. Keep the original's section numbering and comments; add ISOBAR's sections after them. The first commit in this directory is the byte-identical copy with only the name changed and its `--selftest` green under `-DISOBAR_CPU`.

## Build (planned)

```
solver/build.cmd            # VS 2022 vcvars64: nvcc for sm_89 + the CPU reference with cl; both selftests; --bench
```
The CPU build MUST succeed on a machine with no CUDA toolkit.

## Oracles

O1 one dynamics source · O2 determinism · O3 conservation (curve published) · O4 stocks priced · O5 int8 precision · O6 duplicate recall · O7 CPU/GPU parity · O8 K_PAID · O9 paired arrived grading · O-MONO on the stub sweep. `--selftest --lie N` must fail oracle N by name.
