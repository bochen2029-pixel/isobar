# connector.contract — lanes in, effects out, nothing interpreted

```python
class Connector(Protocol):
    id: str                                   # 'gmail' | 'outlook' | 'imap' | 'gcal' | 'outlook_cal' | 'caldav'
                                              # 'todoist' | 'mstodo' | 'gtasks' | 'textfile'
                                              # 'contacts_google' | 'contacts_ms' | 'contacts_vcf'
                                              # 'stripe' | 'quickbooks' | 'xero' | 'bankfeed'
                                              # 'location_phone' (consent)
    def lanes(self) -> list[Lane]: ...        # subset of {mail, cal, list, contacts, money, location}
    def consent_class(self) -> Consent: ...   # standard | contacts | location | money
    async def backfill(self, since_ns: int, cursor: str | None) -> AsyncIterator[Observation]: ...
    async def delta(self, cursor: str) -> AsyncIterator[Observation]: ...
    def capabilities(self) -> list[EffectCapability]: ...
    async def prepare(self, intent: Intent) -> PreparedEffect: ...
    async def execute(self, prepared: PreparedEffect) -> Receipt: ...
    async def verify(self, effect: Effect) -> Receipt: ...   # re-read the remote object; postcondition
```

```
EffectCapability { target, reversibility ∈ {reversible, compensable_low, compensable, irreversible},
                   inverse_template?, hold_window_s, requires_verdict? }
```

## Laws

1. **Transport only.** A connector normalises to `Observation` and never emits an assertion. Anything it cannot carry is a typed refusal (`UNSUPPORTED_FIELD`), never a guess.
2. **Idempotent by `(source, external_id, src_rev)`.** Equal `src_rev` ⇒ no-op; lower ⇒ refused and logged.
3. **Two implementations per lane** from M0: a hosted broker (Composio) and a direct/open adapter. The plane MUST run with either alone.
4. **Reversibility is declared here and only here.** The gate reads `capabilities()`; a caller cannot assert an inverse.
5. **Money connectors are read-only verdict sources.** `capabilities()` returns `[]`. A payment effect does not exist in v1.
6. **Contacts is a seed, not a stream.** One read; growth comes from mail and calendar identities.
7. **Location is consent-gated** (I13): user-invoked or scheduled, visibly on, processed local-first, excluded from named sensitive places; `backfill` refuses without a consent row on the tape.
8. **Credentials never enter a microVM.** Attachments open in the branch; connectors do not.
9. **Verify after execute.** A `Receipt` with `verified: false` marks the effect `unknown`, never `fired`.

## Default capability tables (v1)

| lane | target | reversibility | inverse | hold |
|---|---|---|---|---|
| mail | `draft.create` | reversible | delete draft | 0 |
| mail | `send.nudge` | compensable_low | follow-up correction | 600 s |
| mail | `send.commitment` | **irreversible** | — | 600 s, ASK |
| cal | `event.move_internal` | reversible | move back | 600 s |
| cal | `event.create_internal` | reversible | delete | 600 s |
| cal | `event.accept_external` / `counter` | compensable | decline / re-propose | 600 s |
| list | `task.create/complete/defer/reorder` | reversible | inverse op | 0 |
| money | — | read-only | — | — |
