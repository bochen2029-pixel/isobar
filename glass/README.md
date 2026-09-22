# glass/ — the interface

**Nothing here is built.** v1 is a local web page served by `isobard` (port: BACKLOG B6). A native viewer is a later rung (BACKLOG B5).

## What it draws (all from the IR, never from the calendar)

- **The pressure map.** The horizon as a grid of slots; the dual `v[c]` as colour (isobars); binding days named. Hours the owner has protected are hatched; travel cells are drawn as travel.
- **Particles.** Each open commitment at its argmax cell; the halo's radius is its support (`exp(H)`): decided placements are points, contested ones are fuzzy. Colour by direction (we owe / they owe). Contradictions as links, typed.
- **The stocks.** Three columns on the right whose heights are their prices: backlog · waiting on me · waiting on them (top three silences named, with the counterparty tier).
- **The money partition.** `confirmed receivable · apparent overdue (payment status not connected) · proposal pipeline · vendor credit` — four figures, never one sum.
- **The pipper.** One proposed move, its forecast, its band, the do-nothing number, one key to accept, one to dismiss (both are grades).
- **The four bays.** NOW · AT RISK · NEXT · WAITING, the same field as a list, ordered by slack at coverage USABLE and by due otherwise; owner edits enter as observations from source `owner`.
- **The why-drawer** on every card: the source span, the compiled cell with probabilities and provenance, the join, the price before and after, the futures that broke, the repair options with their J.
- **The coverage label**: `capacity uncertain` at WEAK with widened bands; never "your week fits" at WEAK.
- **The switch and the pill**: `RESIDENT SHADOW · LIVE · OFF · STALLED`, always visible, never animated unless a state changed.

## Laws

Hysteresis: a particle moves only when its risk class, deadline or repair changes materially, never on a 1.7 % objective change. Every number carries its band. Nothing on the page is generated prose except the wording of a draft, which is labelled as the LLM's. The page reads `field/latest.bin` and the tape folds; it never computes.
