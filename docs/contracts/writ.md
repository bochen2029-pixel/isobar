# writ.contract — the goal, hand-authored, never fitted

`writ.yaml` is owner policy. The multiverse ranks futures by it; no training run reads or writes it; a change is a `policy` row on the tape with the diff.

```yaml
version: 1
tiers:                       # lexicographic in practice: a lower tier is decided before a higher one is consulted
  - [hard_breaches]
  - [external_promises_broken]
  - [renegotiations]
  - [churn]
  - [buffer, focus_fragmentation]
weights:                     # inside a tier, and for the scalar J the pipper reports
  w_hard: 8.0                # a hard-deadline breach
  w_soft: 2.0                # a soft-deadline breach
  w_ext: 4.0                 # an external promise broken (any hardness)
  w_backlog: 3.0             # UNPLACED mass
  w_wait: 1.0                # WAITING age, weighted by counterparty tier
  w_ask: 0.5                 # asks of the owner (UNADJUDICATED)
  w_churn: 0.7               # internal moves proposed
  w_buffer: 1.0              # contingency consumed (negative is good)
  w_frag: 0.5                # focus-block fragmentation
  w_overtime: 2.0            # work placed outside hours
pessimism:
  beta: 1.0                  # rank by J_mean + beta * J_std
policy:
  max_external_renegotiations_per_repair: 2
  prefer_internal_moves: true
  preserve_buffers: true
  quiet_hours: ["21:00", "07:00"]
```

**Laws.** The writ contains no learned term. A move that improves J but violates a law mask is infeasible, not expensive. The `tiers` order is the owner's; ISOBAR proposes changes only as a candidate diff shown with the outcomes that motivated it.
