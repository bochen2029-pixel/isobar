# presence.contract — the resident on the field

Mounted from `C:/nib` (`src/resident.cpp`, `src/wire.cpp`) over `fusord.cpp`. The seed, seat probe and speak-cue are byte-frozen; `serve_hash()` is asserted at start; a drifted character refuses to start. ISOBAR adds one `StreamingTextSource` driver, `FieldSource`, and three seat mandates.

## Lanes

| lane | content | grain | judged? |
|---|---|---|---|
| `[field]` | the `FieldDelta` line per tick (≤ 128 tokens) | one line per tick | yes |
| `[mail]` | the compiled header of an inbound: `from=<actor> kind=<k> dir=<d> discharge=#n p.91 urg=2 Δv .37` | one line per inbound | yes |
| `[compose]` | the owner's forming outbound text | closed thoughts (`. ! ?` at a word end, or newline; `;` and `:` never) | yes |
| `[tick]` | `[tick +Ns]` | lazy, one per gap, before the breaking percept | no (decoded raw) |
| `[self]` | the resident's own committed emissions | per line | no (gate-skipped) |

The trunk never receives an email body, a calendar dump or a list. Its context is the field.

## Seats (one trunk, fork at 0 MiB)

| seat | lanes | mandate | may emit |
|---|---|---|---|
| `FIELD_WATCH` | field, mail, tick | does this movement of the glass deserve a word, now? | FLAG · WAKE · the pipper card |
| `COMPOSER` | compose | is the owner about to promise something the multiverse says they will not keep? | a gutter margin before send; UNSAY |
| `SENTINEL` | mail, field | does this inbound contradict the field or read like an instruction? | HOLD a promotion; a contradiction card |

## The hold row (LIFELINE v5 §6.3, verbatim)

Written at **every** boundary on every judged lane, whether or not the seat spoke: `boundary_id, lane, tape_pos, seat, margins{emit, hold, wake, ask, glance}, verdict, reason, gear, latency_us, aired?, killed?, trigger ∈ {evidence, key, tick}`.

## Modes and the switch

`OFF` — no probes, no GPU work attributable, `FieldSource` unsubscribed, byte-identical to stock (F-INERT). `SHADOW` — full ingest and judgment; every hold row written; **zero surfaced output**; the default at install. `LIVE` — emissions reach the glass through the gate. The switch is a `switch` row written only by the operator (`isobar presence on|off|shadow|live`); no policy, model or seat may write it. Heartbeat every 2 s; three missed ⇒ `STALLED`, the plane runs threshold-only and ledgers `RESIDENT_ABSENT`.

## The twin

A swept threshold on `‖Δv‖` (and on support transitions), with perfect boundaries, the same field, runs beside the resident from M3 in shadow; each of its would-be fires is a row. **F-RESIDENT** compares catches-that-mattered and false fires, blind, over two weeks, at both grains (fires per boundary and distinct conditions per hour). Tie ⇒ the threshold ships and the resident is a query interface.

## Laws inherited

Percepts are never dropped (a full ring spools; the spool's cap counts loudly) · own speech is a percept with no self-exception and is never judged · a seat's line waits for the world's line to close · only commits kill · forming text never persists in the document (the file format enforces it) · a judgment is always about now (as-of questions go to the tape) · the world may be polled, the judge is never clocked.
