# reflex/ — the boundary compiler

**Nothing here is built** except the question set. Contract: `docs/contracts/reflex.md`. The question set is `questions.yaml` (version 1, 17 questions; `same_as_candidate` is asked per candidate from the join, not in the main pass).

```
questions.yaml
providers/
  laya.py        default: local, Apache-2.0, `pip install laya`, Router(preload=True); one compile() per inbound
  jev.py         TypeSafe API adapter; the vendor's calibration is measured on the same 200 emails, never trusted
  llm_enum.py    a cheap LLM constrained to the enum — the deletion-condition comparator, never the default
  trunk_head.py  a second head on the resident (later rung)
  stub.py        StubReflex(c): the planted-truth answer with probability c, calibrated wrong otherwise — the gym's reflex
calibration/     the reliability fits per (provider, question, band): 8 bins, monotonicity test, min n per band
```

## Laws

One pass per inbound · `p` is sampled, never thresholded, above the gate · provenance is causal (`HIGH / MOD / LOW_absent / LOW_conflict`) · evidence is nonce-framed and redacted before any provider · a non-monotone question is `uncalibrated` and sampled at the class prior · dates, amounts and ids never come from the reflex.

## The first measurement (M0)

200 owner-labelled emails, frozen before any provider is run: per-question precision/recall and the reliability curve for `laya`, `jev` (if keyed) and `llm_enum` at equal cost. The result decides the default provider and whether the reflex slot is served by the enum (its deletion condition).
