# solver.contract — `isobar_field` and `isobar_foresee`

*Two single-translation-unit instruments, C++17/CUDA, `-DISOBAR_CPU` for the serial reference. Called by `isobard` as subprocesses. Lifted from `C:/fusor1/ledger_lattice/ledger_lattice.cu` and `C:/fusor1/FlightComputer/src/flight_computer.cu`; the lift keeps their oracles and adds ISOBAR's rows.*

## Build

```
nvcc -O3 -std=c++17 -arch=sm_89 -o isobar_field   solver/isobar_field.cu      (sm_120 for RTX 50; sm_90 H100)
nvcc -O3 -std=c++17 -x c++ -DISOBAR_CPU -o isobar_field_cpu solver/isobar_field.cu   (or any C++17 compiler)
nvcc -O3 -std=c++17 -arch=sm_89 -o isobar_foresee solver/isobar_foresee.cu
g++  -O2 -std=c++17 -x c++ -DISOBAR_CPU solver/isobar_foresee.cu -o isobar_foresee_cpu
```
On Windows: `solver/build.cmd` inside a VS 2022 `vcvars64` environment; the CPU builds MUST succeed with no CUDA toolkit present.

## IPC

Input: one memory-mapped file `lattice.bin` (little-endian, SoA, 64-byte aligned sections) plus `lattice.json` (header: N, seats, slots, stocks, T, late_penalty, iters, seed, arm, state_version, tier weights, law masks as bitsets, slot kind keys). Output: `field.bin` (`u`, `v`, `es`, `risk`, `argmax_cell`, `contra[]`) and `field.json` (stock prices, binding days, arithmetic line, iters, `delta_v_norm` if `--prev field.bin` is given). Exit codes: `0` ok · `2` bad input (typed reason on stderr) · `3` oracle failure (which one) · `4` device unavailable (CPU path must be used) · `5` an oracle passed its own lie.

```
isobar_field   --tick lattice.bin [--prev field_prev.bin] [--arm 0|1] [--iters 40] [--out field.bin]
isobar_field   --selftest [--lie N] [--seed S]
isobar_field   --bench                       # measured stream-triad peak + the arithmetic line
isobar_foresee --run lattice.bin field.bin moves.json --K 4096 --H 14 --iters 8 --seed S [--out foresight.json]
isobar_foresee --rehearse lattice.bin field.bin row.json --K 256      # warm-started; the composer's wager
isobar_foresee --backtest lattice.bin move.json --H 14 --seed S       # paired arrived: candidate vs do-nothing
isobar_foresee --parity  lattice.bin moves.json                       # CPU vs GPU, worst relative |ΔJ|
isobar_foresee --selftest [--lie N]
```

## Laws the instrument enforces

- `place_cost()` is the only place the cost of a row in a cell is defined; `__host__ __device__`; read by the Sinkhorn, the support meter, the stencil, the report, the rollout.
- Duals only; the plan is never materialised; two arms, one canvas, one bitmask.
- Every column, stocks included, takes the dual update; finish on a row pass.
- int8 storage, fp32 accumulation; fixed-point `uint64` histograms and moments; counter-based RNG; no float atomics.
- The stencil is local: contention bucketed by cell; identity bucketed by entity (a second stencil); travel bucketed by place pair.
- Peak bandwidth is measured every `--bench`; a constant is refused.
- The rollout leaf is shared by the CPU reference and the GPU kernel; parity is an oracle.

## Oracles (each with a lie arm; `--lie N` must FAIL oracle N or exit 5)

| # | oracle | gate | lie |
|---|---|---|---|
| O1 | one dynamics source: `z_direct` vs `z_dual` | max |Δ| < 1e-3 | perturb one traversal |
| O2 | determinism: `memcmp` of duals, two runs | identical | inject a wall-clock read |
| O3 | conservation: rows ship supply; no real column overflows; curve published | 1e-2 / 1e-2 | skip the final row pass |
| O4 | stocks priced under squeeze | all stock duals > 1e-6 | stock capacity → ∞ |
| O5 | int8 round-trip cosine over 200 vectors | ≥ 0.995 | quantise with a wrong scale |
| O6 | unkeyed duplicate recall on planted pairs | ≥ 70 % | negate planted embeddings |
| O7 | CPU/GPU parity on rankings and J | worst rel |ΔJ| ≤ 1e-6, pipper agrees | change one config hash |
| O8 | K_PAID: no chase set contains a verdict-paid object | zero | drop the verdict column |
| O9 | the deploy is graded on arrived, paired outcomes; a good move beats do-nothing, a bad one does not | as planted | grade on the forecast instead |
| O-MONO | metrics smooth and monotone across the stub competence sweep | monotone | shuffle competence labels |

## Budgets [D, to be replaced at M1]

Field: N=120, M=395, 40 iters ≈ 3.8 M pair-evaluations ≈ 1.1 GB moved ≈ 3 ms GPU / 30 ms CPU. FORESEE: K=4,096 × H=14 × 8 iters ≈ 22 G pair-evaluations ≈ 1–5 s GPU (one thread per universe) / ~20 s on 16 cores; rehearsal K=256 ≈ 0.1–0.3 s GPU. Named next step: one block per universe with a shared-memory Sinkhorn (5–10×).
