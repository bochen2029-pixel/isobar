# reflex.contract — the boundary compiler

```python
class SemanticReflex(Protocol):
    provider_id: str; provider_fp: str
    async def compile(self, evidence: str, questions: QuestionSet) -> Cell: ...   # ALL questions in one call
    async def noul(self, question: str, evidence: str) -> tuple[bool, float]: ...
    async def choice(self, question: str, options: Sequence[str], evidence: str) -> tuple[str, float]: ...
    async def score(self, question: str, levels: Sequence[str], evidence: str) -> tuple[str, float, list[float]]: ...
```

Providers (plugins under `reflex/providers/`): `laya` (default; local; `pip install laya`, Router with preload; ~33–40 ms per state [V, HF card]), `jev` (TypeSafe API; the vendor's calibration claim is measured, never trusted), `llm_enum` (a cheap LLM constrained to the enum — the deletion-condition comparator), `trunk_head` (a second head on the resident; later).

## The question set

`reflex/questions.yaml` is data and is versioned (`questions_version` on every Cell). Dates, amounts, ids come from deterministic extraction; the reflex only says whether one was mentioned.

## Laws

1. **One pass per inbound.** `compile()` asks every question in one call; per-question calls exist for the join's last mile and for re-asking open commitments.
2. **Calibrated, then audited.** Each answer carries `p`; the plane fits a reliability curve per `(provider, question, band)` on this owner's arrived outcomes (8 bins, monotonicity test). A non-monotone question is `uncalibrated` and sampled at its class prior.
3. **Sampled, never thresholded** above the gate.
4. **Provenance is causal**: `HIGH` grounded in the text · `MOD` domain prior · `LOW_absent` (missing evidence ⇒ a WANT row) · `LOW_conflict` (contradictory text ⇒ the residual / a jury).
5. **Framed as data.** Evidence is wrapped in a per-call nonce frame; the provider never sees a tool, a path or a policy.
6. **Redacted.** Sensitive identifiers are replaced by stable tokens before any remote provider; the local provider sees the redacted form too, so behaviour is identical across providers.
7. **Deletion condition:** `llm_enum` ties calibrated accuracy at equal cost on the 200-email set ⇒ the reflex slot is served by the enum.
