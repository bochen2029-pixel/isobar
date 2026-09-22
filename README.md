# ISOBAR — the priced week

**Mail, calendar and the list as one field: priced every tick, rehearsed across futures before a promise is made, watched by a mind that is home, and spoken about only when the glass falls.**

> **Status: REV 0 · specification only (2026-09-22). Nothing is built. No number in this repository is ISOBAR's own; every measured figure belongs to the instrument it names (`ledger_lattice.cu`, `flight_computer.cu`, `nib`, `connectome`, Laya's card).** The normative document is `docs/SPEC.md`; the stages and their falsifiers are `docs/ROADMAP.md`; the open items are `docs/BACKLOG.md`; the rules for a session working here are `CLAUDE.md`; the concept document that set the design is `docs/lineage/`. The name is provisional (a barometer on a ship is *the glass*; isobars are the lines of equal pressure on its chart).

## The one idea

A person's operational life is a field with prices. Mail, calendar and the task list are sensors on it. Every message is a perturbation whose weight is how far it moved the prices. Every promise is a wager rehearsed across thousands of sampled futures before it is sent and graded when it lands. A resident mind watches the field, not the inbox, and holds until the glass falls. The solver is not downstream of cognition; it is the encoder of state that every other organ reads.

Three inversions, none of which any shipping product has:

- **Price, not rank.** The dual of a transport problem is what one more half-hour on Thursday is worth to every open promise, with a band, recomputed every tick. Pricing turns *no* into arithmetic.
- **Computed urgency.** An email's weight is ‖Δv‖, the movement of the price vector when its row entered the lattice — never how urgent it sounds. An email that moves no price is noise.
- **The resident watches the field.** Time consumes slack, so the field moves with no message arriving. That is how it notices what nobody named.

And one coupling that makes it one machine rather than a pile of parts: the reflex's calibrated probabilities are **sampling distributions for the multiverse**, never thresholds, so a 0.6-confidence hard deadline is hard in 60 % of futures and the price of that slot reflects the doubt. Nothing collapses until the deterministic gate; arrived outcomes then grade the probabilities, which is the record that appreciates.

## The six things, and the organs

Three lanes (mail · calendar · list), three registries the field reads (people · places · money), and the clock. Brand-agnostic behind one connector contract; SMS folds into mail.

| organ | the one thing only it does | mounted from |
|---|---|---|
| deterministic code | ids, dates, amounts, spans, thread keys | `isobard` |
| **the reflex** (Laya / Jev) | ~17 typed questions per email in one pass with calibrated probabilities; cannot emit a field outside the schema | `reflex/` |
| **embedder → reranker** | the join, after exact keys; the unkeyed duplicate no key reaches | `:8092` + `connectome`'s resident scan |
| **the solver** | prices, support, contradictions, and the integral over futures — the relational instrument that needs no training | `solver/` (lifted from `C:/fusor1`) |
| **the resident** (FUSOR) | present on the field's delta lane; hold, emit, un-say; the record of holds | `presence/` (lifted from `C:/nib`) |
| local LLM | the residue the reflex could not type; wording a computed intent | llama.cpp on the box |
| frontier LLM | novel semantics; a second judge on irreversibles | one seam, budgeted |
| E2B | the gym, the counterfactual fortnight, attachments, CPU fan-out | `C:/e2b` |
| the heads (Qwen-Drive shape) | emit a `ScheduleDelta`, a `DraftIntent`, a `TaskDelta` — never prose about it | `isobard/heads` |

## What it will do, in order (see `docs/ROADMAP.md`)

**M0 · the X-ray.** Connect read-only; compile 90 days of mail with the reflex; build the ledger; seed the people registry with a tier table; price the horizon on the CPU field; show the glass. Gate: pilot owners find ≥ 3 items they did not know about at audited precision ≥ 0.80.
**M1 · the multiverse and the wager.** Every price gets a band; every commitment-bearing draft carries a survival forecast; the pipper is graded on arrival.
**M2 · the composer.** The forecast in the gutter while the reply is being typed; the un-say.
**M3 · presence.** The resident on the field lane, SHADOW first, raced blind against a threshold twin for two weeks. **If the twin ties, the resident is retired and the threshold ships.**
**M4 · authority.** The gate, the outbox with inverses, one-click sends with a hold window, κ weekly.
**M4a · places and money.** Travel in the lattice; the paid-invoice law as a release-blocking oracle.
**M5–M6 · the gym, the branch, the heads, the tune.**

**M0 + M1 is the product.** Everything after is presence, authority and learning, each mounted only past its gate.

## Two things stated plainly

**The GPU is conditional.** For one owner the per-tick re-price is a CPU job and the arithmetic line will say so every tick; the card earns its place only on the interactive multiverse (the band on every price after every email; the survival on every promise as it is typed). The CPU reference is first-class and parity is an oracle.

**Residency is conditional.** The inbox is sparse; the field is not. Whether a tuned resident beats a threshold on ‖Δv‖ is the decisive unrun number (F-RESIDENT), and the null is built first.

## Layout

```
README.md · CLAUDE.md · LICENSE · isobar.lock · writ.yaml · tiers.yaml
docs/        SPEC.md (normative) · ROADMAP.md · BACKLOG.md · contracts/ · lineage/
solver/      isobar_field.cu · isobar_foresee.cu — C++17/CUDA, CPU reference, oracles with lie arms
isobard/     the plane (Python 3.13): tape · connectors · reflex client · join · promote · gate · outbox · glass server
connectors/  composio/ and direct/ adapters per lane; contacts, money, location feeds
reflex/      questions.yaml · providers/
presence/    the FieldSource driver · seats · the threshold twin
glass/       the interface
gym/         synthetic owners, planted truth, stub cognition, lie arms
tests/       fixtures · replay · injection corpus · property tests
runs/        receipts (gitignored)
```

## Lineage

The field is `C:/fusor1/ledger_lattice/ledger_lattice.cu` (four FluidX3D transpositions; six oracles with lies; the T17 stock fix). The multiverse is `C:/fusor1/FlightComputer/src/flight_computer.cu` (one predictor, three callers; the pipper; the paired arrived backtest). The resident is `C:/nib` over `fusord.cpp`. The canonical object, promotion, the coverage gate and the four bays are HELM Commitment Control. The licence ladder, κ, the salt and the no-allow gate are the Personal Operations Plane master architecture and `governord`. The hold row is LIFELINE v5 §6.3. The head shape is Qwen-Drive.

MIT © 2026 Bo Chen. Claims in this repository carry receipts or say plainly that they do not.
