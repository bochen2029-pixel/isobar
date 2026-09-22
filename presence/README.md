# presence/ — the resident on the field

**Nothing here is built.** Contract: `docs/contracts/presence.md`. The resident is **mounted from `C:/nib`** (`src/resident.cpp`, `src/wire.cpp`, over `fusord.cpp`); this directory adds one driver and three mandates, and never re-derives the loop.

```
field_source.cpp    FieldSource: a StreamingTextSource driver that reads FieldDelta lines (and mail headers, ticks) from
                    the plane over a loopback socket and emits Deltas on the [field] / [mail] / [tick] lanes
seats.yaml          FIELD_WATCH · COMPOSER · SENTINEL mandates (text), pinned by hash into the tape at start
hold_writer.cpp     writes the Hold row (LIFELINE v5 §6.3) at every boundary to its own tape segment
switch.cpp          OFF / SHADOW / LIVE; operator-only; a `switch` row; heartbeat; STALLED
twin/               the threshold twin: a swept threshold on ‖Δv‖ and support transitions, perfect boundaries,
                    the same field; every would-be fire is a row; the F-RESIDENT scorer
compose/            the COMPOSER seat's surface (BACKLOG B1): nib's pane, an extension, or ISOBAR's own compose box
```

## Laws

The seed, seat probe and speak-cue are byte-frozen; `serve_hash()` is asserted at start. The trunk never receives an email body. Percepts are never dropped; a full ring spools and counts. Own speech is a percept, never judged. Ticks are lazy and decoded raw. Forming text never persists in the document. The switch is written only by the operator. **SHADOW is the default at install and the resident surfaces nothing until the operator flips it.** The twin runs beside it forever.

## The decisive number

F-RESIDENT: resident vs twin, catches-that-mattered and false fires, blind, two weeks, both grains. If the twin ties, the resident is retired to a query interface and this directory ships only `twin/`. That outcome is printed beside the laws it bought.
