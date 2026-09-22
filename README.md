# ISOBAR — the priced week

**Your mail, your calendar and your list are not three apps. They are three sensors on one field of promises. ISOBAR prices that field every tick with a solver, rehearses every promise across thousands of futures before you make it, and keeps a mind resident on the field that speaks only when the glass falls.**

> On a ship the barometer is *the glass*. Isobars are the lines of equal pressure on its chart. Sailors say *the glass is falling* when weather is coming, and nobody had to ask.

## The ambition

Every tool for running a life or a small business ranks. A rank has no units, so nothing can tell you that Thursday afternoon is worth more than the reply you are about to promise for it. ISOBAR **prices**: the dual of a transport problem is what one more half-hour on Thursday is worth to every open promise, with a band, recomputed every tick. Pricing turns *no* into arithmetic.

Every tool judges urgency by how urgent a message sounds. ISOBAR **computes** it: an email's weight is how far it moved the price vector when its row entered the lattice. An email that moves no price is noise, however loud.

Every assistant is woken by a clock or a caller. ISOBAR keeps a **resident** mind on the field's own stream, so that time consuming slack moves the world and the mind notices with nobody asking. It holds by default, and every hold is a row with the margin it held by.

Every promise is a **wager**: rehearsed across sampled futures while you type it, sent with a survival forecast, graded when it lands. A promise the machine makes on your behalf is licensed only by the outcomes of promises it already kept, and the licence narrows on any evidence.

And the whole thing is a **box you own**. Cut the network and it still re-prices, still flies the multiverse, still replays its tape. What it loses offline is new evidence and a rented frontier model. What it keeps is your state.

Where it is going, in one line each:

- **Capture now, organize never.** One owner-invoked act — forward, share, photograph, speak, record, drop — with the clock, the place and the modality as free provenance. Nothing intentionally captured is ever silently discarded; what cannot be resolved sits in a stock whose price is what your un-made-sense-of life is costing you.
- **The whole life on the tape, the live week in the field.** A lifelong record underneath; the priced field as its active projection; the resident holding only what deserves temporal residence.
- **Computed state as a modality.** The field's own frames become a lane the reflex classifies, the embedder recalls precedents over, the solver rehearses trajectories through, and the resident integrates across time — one level above words.
- **Machine-to-machine.** When the counterparty runs one too, commitments cross as typed objects. Language stays at the human edge.
- **One face to the human, no faces inside the machine.** The persona is short, grounded and silent by default. Its identity lives in the record, so it survives the model underneath changing twenty times.

The laws that hold it together: the commitment is canonical; the tape is the only truth and every table is a fold; nothing learned writes state, disposes or gates; a probability is a distribution the multiverse samples, never a threshold, until the deterministic gate; every effect carries its inverse or asks; inbound is data, never instruction; mail silence is not proof an invoice is unpaid; and no organ outlives its null — the CPU reference beside the GPU, the threshold twin beside the resident, a cached turn-based baseline beside the field, forever.

## Status

> **M0 · the X-ray — built and green on the gym (2026-09-22).** The tape, the typed objects, the reflex client (stub + Laya), the join, deterministic promotion, the people and money registries, the lifted field instrument (`solver/isobar_field.cu`, 8/8 oracles with lie arms on MSVC, nvcc and g++), the bridge, the Recovery Scan, the glass, five file-based connectors, a synthetic owner with planted truth, and a CLI. On the gym the X-ray recovers **7/7 plants at precision 1.00** with a perfect reflex, the paid-by-verdict invoice is never chased, the WAITING stock is priced, the tape replays byte-identically, and the competence sweep is monotone. **29/29 tests.** Receipt: `receipts/M0_GATE_2026-09-22.md`. Pending for the owner-facing half of the gate: real pilot owners (F-RECOVERY) and 200 owner-labelled emails with the Laya weights (F-JEV). No real mailbox has been connected yet. Nothing here is a claim about a real owner.

| M | stage | state |
|---|---|---|
| **M0** | the X-ray: connect read-only, compile the mail, price the horizon, show the glass | **green on the gym** |
| M1 | the multiverse and the wager: every price a band, every promise a survival forecast, the pipper graded on arrival | next |
| M2 | the composer: the forecast in the gutter while the reply is typed; the un-say | |
| M3 | presence: the resident on the field lane, SHADOW first, raced blind against a threshold twin | |
| M4 | authority: the gate, the outbox with inverses, one-click sends, κ weekly | |
| M4a | places and money: travel in the lattice; the paid-invoice law as a release-blocking oracle | |
| M5 | the gym and the branch: planted truth, stub cognition, the counterfactual fortnight in a microVM | |
| M6 | the heads and the tune | |

**M0 + M1 is the product.** Everything after is presence, authority and learning, each mounted only past its gate.

## Run it

```
cmd /c C:\isobar\solver\build.cmd              (Windows, from PowerShell: builds the instrument on cl + nvcc, runs both selftests)
g++ -O2 -std=c++17 -x c++ -DISOBAR_CPU -o solver/build/isobar_field_wsl solver/isobar_field.cu   (any C++17 compiler: the CPU reference)
pip install -r requirements.txt
python -m pytest tests/                        29 checks: contracts · tape · dates · registries · purity · field · the gym end to end
python -m isobard.cli gym  --out runs/gym/owner1
python -m isobard.cli scan --owner runs/gym/owner1 --competence 1.0      the X-ray, the field, the glass (store/glass.html)
python -m isobard.cli replay --store runs/gym/owner1/store --verify      the folds rebuilt from the tape, byte for byte
python -m isobard.cli sweep --owner runs/gym/owner1                      O-MONO across stub competence and seeds
```

A real owner runs the same `scan` against a directory of brand-agnostic exports: `mail.mbox` (or `eml/`), `calendar.ics`, `todo.txt`, `contacts.vcf`, an optional `money.csv` verdict export, `tiers.yaml`, `owner.json`. Gmail, Outlook, IMAP, Google Calendar, CalDAV, Todoist, plain text: all of them export these.

## The organs, and what only each can do

| organ | the one thing only it does | mounted from |
|---|---|---|
| deterministic code | ids, dates, amounts, spans, thread keys | `isobard` |
| **the reflex** (Laya / Jev) | ~17 typed questions per email in one pass with calibrated probabilities; cannot emit a field outside the schema | `reflex/` |
| **embedder → reranker** | the join, after exact keys; the unkeyed duplicate no key reaches | a local embedding endpoint |
| **the solver** | prices, support, contradictions, and the integral over futures — the relational instrument that needs no training | `solver/` (lifted from the ledger lattice and the flight computer) |
| **the resident** (FUSOR) | present on the field's delta lane; hold, emit, un-say; the record of holds | `presence/` (mounted from nib / fusord) |
| local LLM | the residue the reflex could not type; wording a computed intent | llama.cpp |
| frontier LLM | novel semantics; a second judge on irreversibles | one seam, budgeted |
| E2B / microVMs | the gym, the counterfactual fortnight, attachments, CPU fan-out | never the inner loop |
| the heads (Qwen-Drive shape) | emit a `ScheduleDelta`, a `DraftIntent`, a `TaskDelta` — never prose about it | `isobard/heads` |

The coupling that makes it one machine rather than a pile of parts: the reflex's calibrated probabilities are **sampling distributions for the multiverse**, never thresholds, so a 0.6-confidence hard deadline is hard in 60 % of futures and the price of that slot reflects the doubt. Nothing collapses until the deterministic gate; arrived outcomes then grade the probabilities, which is the record that appreciates.

## Two things stated plainly

**The GPU is conditional.** For one owner the per-tick re-price is a cache-resident job and the receipt says so; the CPU reference is the tier, and the card earns its place on the interactive multiverse. Parity between them is an oracle. The requirement is not a vendor: it is that the architecture permanently exposes massively parallel non-neural computation as a first-class organ, on whatever accelerator runs the leaf with parity.

**Residency is conditional.** Whether a tuned resident beats a threshold on the price movement is the decisive unrun number (F-RESIDENT), and the null is built first. If the twin ties, the resident is retired and the threshold ships, and the finding is printed beside the laws it bought.

## Layout

```
README.md · CLAUDE.md · LICENSE · isobar.lock · writ.yaml · tiers.yaml · requirements.txt
docs/        SPEC.md (normative, r0.1) · VISION.md (non-normative) · ROADMAP.md · BACKLOG.md · devlog.md · contracts/ · lineage/
solver/      isobar_field.cu — C++17/CUDA, CPU reference, oracles with lie arms, the --tick IPC · build.cmd
isobard/     the plane (Python 3.13): contracts · tape · reflex client · join · promote · registries · field bridge · scan · plane · cli
connectors/  direct file adapters (mbox/eml, ics, todo.txt, vcf, money.csv); composio/ pending
reflex/      questions.yaml · providers/
presence/    the FieldSource driver · seats · the threshold twin (M3)
glass/       the rendered page
gym/         the synthetic owner with planted truth and per-message stub truth
tests/       29 checks · receipts/  gate receipts · runs/  the owner's own data (gitignored)
```

## Lineage

The field is [`ledger_lattice.cu`](https://github.com/bochen2029-pixel) (four FluidX3D transpositions; six oracles with lies; the priced stock columns). The multiverse is the flight computer (one predictor, three callers; the pipper; the paired arrived backtest). The resident is [nib](https://github.com/bochen2029-pixel/nib) over `fusord.cpp`, the FUSOR substrate. The canonical object, promotion, the coverage gate and the four bays come from HELM Commitment Control. The licence ladder, κ, the salt and the no-allow gate come from the Personal Operations Plane master architecture. The hold row is LIFELINE v5 §6.3. The head shape is Qwen-Drive. The reflex interface is the System One / Jev shape, with [Laya](https://huggingface.co/convaiinnovations/laya) as the open backend.

MIT © 2026 Bo Chen. Every number in this repository was printed by a program on one box and names the instrument that printed it; where a gate is pending it says so.
