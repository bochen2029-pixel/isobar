# devlog — the lab notebook

*Never rewritten; corrections appended in the same voice. What was tried, what was measured, what was decided, and the traps the day they bit.*

## 2026-09-22 · M0 begins

**Toolchain probed.** Python 3.13.2 with pydantic 2.10.3, torch 2.11.0+cu128 (CUDA true), transformers 5.3.0. No `cl` on PATH; VS 2022 Community present at the path nib's `build.bat` uses; nvcc 13.1 on PATH. Embedding server up on `:8092`. No `laya`, no `composio` SDK; Composio's API key lives on a Cloudflare worker (bo-brain), not on this box — real mail via Composio waits on a key; the X-ray runs on file-based direct adapters and the gym today.

**Laya installed without deps.** The wheel is 41 KB (`laya-0.3.5-py3-none-any.whl`); every requirement (torch ≥ 2.0, transformers ≥ 4.48, safetensors, huggingface_hub, numpy) was already present, so `pip install --no-deps` touched nothing else. The model weights (`convaiinnovations/laya`, ~0.8 GB) are a separate download from huggingface.co, not yet pulled — the reflex runs on `StubReflex` until the operator says yes. API surface: `Router`, `Agent`, `email_questions`, `predict_shortlist`, `QTYPES`.

**The lift, step one.** `solver/isobar_field.cu` is the byte-identical copy of `C:/fusor1/ledger_lattice/ledger_lattice.cu` (sha256 `5a0d6edc…c4c53`). Built three ways, six oracles green on each:

| compiler | flags | O1 worst | O3 row / col | note |
|---|---|---|---|---|
| MSVC 19 (cl, VS 2022) | `/std:c++17 /O2 /TP /DLL_CPU` | 4.77e-07 @ row 43 | 1.92e-06 / 4.69e-06 | CPU reference |
| nvcc 13.1 | `-O3 -std=c++17 -arch=sm_89` | — (same battery, pass) | — | GPU tier |
| WSL g++ 13 | `-O2 -std=c++17 -x c++ -DLL_CPU` | 4.72e-07 @ row 199 | 1.92e-06 / 4.71e-06 | parity build |

The row that carries the worst O1 residual differs between cl and g++ (43 vs 199) at the same magnitude: floating-point summation order, not a defect; O2 (determinism) is per-binary, and cross-compiler byte-identity is *not* claimed (fixed-point accumulators make the histograms identical; the fp32 duals are compiler-dependent at 1e-7).

**Traps, the day they bit.**
1. `cmd /c build.cmd` from Git Bash prints the cmd banner and does nothing: MSYS rewrites `/c` into `C:\`. Run batch files from PowerShell with an absolute path (`cmd /c C:\isobar\solver\build.cmd`) — nib's HANDOFF §4.3 said so and it bit anyway.
2. `peek sh -- bash -c "cd … && g++ …"` compiled in the wrong directory: the `cd` was shredded on the way through. Use `wsl -d Ubuntu-24.04 --exec bash -c "…"` with absolute `/mnt/c/...` paths and no `cd` (the machine rules already say `--exec`).
3. A Windows byte-range lock is **mandatory**: locking byte 0 of the segment made a second process fail in `read_bytes()` with `PermissionError` before it ever reached the lock, so readers were blocked too. The writer's lock now sits at offset 2^40, a byte no row will ever reach; readers read freely and a second writer collides on that byte → `SecondWriter`. Test `test_second_writer_is_refused_by_the_os` spawns a real second process.
4. `vcvars64.bat` complains `'vswhere.exe' is not recognized` on this box and then works; harmless, but it turns PowerShell's exit status red under `2>&1`. Check the binaries' own exit codes.

**Decided.** Lift discipline holds: the first commit under `solver/` is the byte-identical copy with its own `LL_CPU` macro; `ISOBAR_CPU` is defined alongside so both generations of the source build. ISOBAR's rows (WAITING stock, tier weight, K_TRAVEL, K_PAID, Δv, `--tick` IPC, the FieldDelta line) come as surgical edits, each recorded here with the line it touched.
