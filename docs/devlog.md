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

## 2026-09-22 · M0, the lift's edits and the X-ray (later the same day)

**The lift, step two — the ISOBAR rows.** Surgical edits to `solver/isobar_field.cu`, all marked `ISOBAR`: a third stock `STOCK_WAITING` (a waiting row sits there cheap and budgeted, or spills to UNPLACED dear; a placeable row never sits there); `tier_w[N]` multiplying lateness in `place_cost`; `paid[N]` and `waiting[N]`; `K_PAID` in the stencil with oracle **O8** (every planted paid-but-open row fires, nothing else) and **O8b** (the WAITING stock is priced under a planted binding budget); **lie 3** drops the verdict column and O8 must fail; `host_view(LatHost)` so the selftest's host traversals never dereference device pointers — **the original's GPU selftest segfaulted for exactly this reason (exit 139), a latent defect the lift found; the CPU build hid it because `dev_alloc` is `calloc` there**; the stream triad now streams 128 MB per array (the original's 1<<22 floats × 3 = 48 MB was exactly the AD103's L2, and the "peak" it printed — 1,592 GB/s — was an L2 number, 2.4× the card's DRAM; the corrected triad reads 551–612 GB/s); the `--tick` binary IPC (a 64-byte header, SoA arrays, `field.json` + `field.bin`, `--prev` for Δv, movers only where |dv| > 1e-9); and, after the X-ray, the DOUBLEBOOK check skipped inside stock columns (two rows waiting on one counterparty share the WAITING stock by construction).

**Numbers.** 8/8 oracles on cl, nvcc sm_89 and WSL g++ 13; O1 worst residual 4.8e-07 (cl), 9.5e-07 (nvcc); O3 row err 2.5e-06, column overflow 4.7e-06; O8 48/48 planted, 0 extras; O8b WAITING price 8.00 on 288 waiting rows; lie 3: K_PAID fired 0 vs 48 → FAILED (correct).

**Traps, the day they bit (continued).**
5. `mailbox.mbox` under the compat32 policy hands back an `email.header.Header` object for any non-ASCII header (the gym's "Invoice #1041 — $8,150"); `Header + str` raises. Every header now passes through `_hdr()` (RFC 2047 decoded, surrogates recovered, always a `str`).
6. `self.truth = truth or {}` in `StubReflex` — the plane hands the stub an *empty* dict to fill later, `or {}` replaces it with a fresh one, and the stub answers the null defaults for every message. Symptom: is_commitment True on 11 of 185 (the 4 % wrong answers), zero commitments, a proposal pipeline of $23,400 with no proposal finding. Fixed with `truth if truth is not None else {}`. Cost: two full runs.
7. **The arity law, violated in my own code twice.** (a) The plane applied a `discharge` on any join candidate, so a stub-wrong `is_discharge` on a message whose only join was an *embedding neighbour* discharged the nearest open commitment — which, since background questions are answered the next day, was always a plant. (b) `promote_mail` returned early on an unkeyed discharge, so the plant's own commitment was never created either. Both now require a keyed join (exact or lexical); the embedding's candidates ride the row as `join_candidates` and never change state. The scan went from 0 findings to 7/7.
8. A Windows byte-range lock is mandatory: locking byte 0 blocked readers too (see trap 3); the lock lives at 2^40.
9. The instrument listed all M cells as "movers" on a zero-Δv tick (no threshold on |dv|). Fixed in C++; caught by `test_field`.
10. The scorer counted a *spurious* finding that shared type and counterparty with a plant as a recovery, so low-competence noise inflated recall (c = 0.55 "recovered" 3/7 with 18 findings at precision 0.17). Recovery now requires the plant's own message marker in the finding's commitment; the 3-seed sweep is monotone: 1.33 → 3.67 → 4.67 → 6.00 → 7.00.
11. The arithmetic line printed "104.8 % of peak — bandwidth-bound" on the CPU for a 15-row lattice: the counted per-pair bytes (136 MB) are cache traffic, not DRAM; the working set is 5.75 KB. The receipt now carries `roofline.regime` keyed on the working set, and "the card is justified" is printed only in the streaming regime above the floor.
12. `cmd /c build.cmd` from Git Bash still does nothing (MSYS path rewriting); PowerShell with the absolute path every time.

**Measured on the gym (c = 1.0).** 185 messages → 850 tape rows in 6.9 s (fsync per row); 39 exact + 1 lexical joins of 40 messages with an antecedent (100 %); 90 embed-rung candidate sets, 0 merges; 48 promoted, 40 discharged (every background question closed by the owner's next-day reply through the thread key), 1 injection flagged; the field: N = 15, M = 395, 17 ms on the CPU reference vs 44 ms on the GPU binary (launch-bound); WAITING 4.03, UNADJUDICATED 5.31; 1 contradiction (K_DUPLICATE = the join's own duplicate candidate, two instruments agreeing); coverage WEAK at 15 % of the workday booked; replay byte-identical. Full receipt: `receipts/M0_GATE_2026-09-22.md`.

**Decided.** (i) The CPU reference is the tier for one owner (under 10⁶ pairs); the card's case is the M1 multiverse. (ii) Discharges and merges only on keyed joins — the arity law in code. (iii) Instruction-shaped mail enters as `contested`, which never reaches the field or the scan. (iv) The support split (3.0) and T = 0.25 do not describe a person's mostly-free week; both re-measured at M1 (BACKLOG B10). (v) The stub at c = 1.0 proves the pipeline; the sweep proves the pipeline degrades with the reflex and not on its own; F-JEV waits for the owner's 200 labels and the Laya weights.
