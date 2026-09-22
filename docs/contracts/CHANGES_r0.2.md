# contracts · CHANGES r0.2

*The deltas `docs/SPEC_r0.2.md` makes to the r0.1 contracts. Not applied here: an implementing session applies each under the CI lints (purity, the sampling lint, the round-trip fixtures) at the rung named, and the contract file gains a version line when it changes. Every field added is [SPECIFIED] unless marked [BUILT].*

## objects.contract

| change | rung |
|---|---|
| `Observation` gains `envelope_trust ∈ {operator, trusted, untrusted}` (the act), `declared: bool`, `rendering?`, `note?: text`, `telemetry?: {t_capture_ns, device_id, place_candidate?, foreground_app?, preceding_event?, duration_s?}`; `intake_trust` keeps its meaning as the payload's trust | M0.5 |
| new `CaptureState ∈ {SEALED, PARSED, LINKED, DUPLICATE, UNRESOLVED, REFUSED, RESOLVED}`; new `Capture { observation_id, state, refusal?: {ASR_FAILED, OCR_EMPTY, UNSUPPORTED_MEDIA, PAYLOAD_TOO_LARGE}, resolved_to?: commitment_id }` | M0.5 |
| new `StateFrame` and `StateDelta` (SPEC §3.3); both are folds, never state | M1 |
| `Grade.kind` gains `declared`; `Grade` gains `stratum ∈ {declared, passive}` | M0.5 |
| every derived object gains `depends_on: [Ref]` | M0.5 |
| `Finding.finding_type` gains `UNRESOLVED_CAPTURE` | M0.5 |
| `Effect` gains `pre: {state_version, remote_version?}`, `post: {observable, window_s}`; the four-row lifecycle `execution · verification · outcome · attribution` | M4 |
| `Lookup<T> = Present(T) | AbsentCertified(receipt) | Unknown(bound)` for every query that can fail to find | M4 |
| new `SituationVector` (SPEC §10.7); `Identity.kind` gains `voice`; `Place.role` gains `transit`; `Actor.reliability` (the owner's declared-attention curve) | M2.5 / M4a / M6b |
| every belief-bearing object gains `corroboration: {independent_docs, independent_channels, single_source: bool}` | M4 |
| `Hold` and `Wager` unchanged [BUILT in contracts.py]; `Hold` gains `lane` values for the new lanes | M3.5 |

## connector.contract

| change | rung |
|---|---|
| the six interfaces OBSERVE · STATE · ACT · INVERT · CONSTRAIN · **GRADE**; per effect class `verdict_source ∈ {owner_reaction, counterparty, arrival, payment, ABSENT}`, `expected_verdict_latency`, `inverse_window`, `censoring` | M4 |
| lane `hand` with its renderings; consent classes gain `voice`, `camera` | M0.5 / M2.5 |
| `PhoneHead { capture() → sealed receipt, queue(), sync(), render(glass) }` — no organ methods by construction | M5b |
| `delta()` returns the typed refusal `NETWORK_ABSENT` on the island | M0.5 |
| the forward address MUST be a mailbox the owner owns; Composio is the second implementation, never the only | M0.5 |

## solver.contract

| change | rung |
|---|---|
| `N_STOCK = 4` (`UNRESOLVED`); O4 extended to all four stocks; `lattice.bin` header `n_stock` | M0.5 |
| a `realm` mask word per seat in `law`; the header gains `realm_mask_words` | M4 |
| O7 registered as cross-device at a tolerance; O2 per binary [BUILT semantics, contract wording] | M1 |
| the backend shims enumerated (allocator · upload/download · launch macro · atomic add on `uint64` and `int`) as the accelerator contract; the word CUDA confined to build lines | M1 |
| `isobar_foresee`: `--run`, `--rehearse`, `--backtest`, `--parity`; O9; precedent-mixture inputs per row | M1 / M6b |
| `isobar_cash.cu` as a second instrument on the same shims; coupling through shared row ids | M9 |

## registry.contract

| change | rung |
|---|---|
| `Actor.identities[].kind` gains `voice`; `Actor.reliability {curve, n, stratum: declared}` | M2.5 / M0.5 |
| `Place.role` gains `transit`; travel edges cached with `cached_ns` [BUILT field] | M4a |
| realms: `acl_scope` values `PERSONAL · BUSINESS:<name> · HOUSEHOLD · SHARED:<project>`; the law *capacity crosses realms, evidence does not* | M4 |
| precedent tables: `(frame_id, situation_vector, arrived_outcomes)` | M6b |
| every row gains `corroboration` | M4 |

## writ.contract

| change | rung |
|---|---|
| ignition per class: `{class: {n0: OPEN|CLOSED, bootstrap_grant: …}}` signed once (L27) | M4 |
| realm policy: which realms may share capacity | M4 |
| `never_auto_contact` and the tier table unchanged [BUILT in tiers.yaml] | — |

## tape.contract

| change | rung |
|---|---|
| row kinds gain `capture · resolution · coverage · island · frame · migration · witness` | M0.5 / M1 / M4 |
| per-device segments `<device_id>.seg`; the resident's hold segment; the governor's segment | M5b / M3 / M4 |
| `hand audit` verb: every capture to a terminal state within `hand.state_budget_s` | M0.5 |
| taint closure on `correction`, retraction and deletion; the deletion ledger and tombstones; the generation event for the ciphertext chain (optional, per scope) | M4 |
| the witness commitment schema `{seq, date, segment_heads, schema_digest, evaluator_digest, licence_root, deletion_root, prev}` | M4 |

## gate.contract

| change | rung |
|---|---|
| the published order (SPEC §17.2): mode/kill first … budget last; `island` ⇒ every effect `held` | M4 |
| `ASK` gains reasons `batched_evening`, `never_auto_contact`; `HOLD` gains `island_held` | M4b / M4 |
| the class table gains `verdict_source`, `expected_verdict_latency`, `undelegatable: bool` (printed) | M4 |
| ignition, the `n_eff` floor, the two axes with the common-mode key, the retained fraction | M4 |
| κ as the exact fold, undefined below `n_eff` | M4 |
| sealing a capture is not a class (D6) | M0.5 |

## presence.contract

| change | rung |
|---|---|
| lanes `[hand]`, `[project]`, `[money]`, `[life]`, `[self]` with their grains and token budgets; one trunk | M2.5 / M3.5 |
| the two twins: the swept threshold and the reflex wake; every would-be fire a row | M3 |
| `probe(question, line_positions) → (scalar, margin)` | M3.5 |
| the eviction column `{region, last_written, dwell, evicted_at}` shared with the hold record | M3.5 |
| the vigilance vector under the never-steer-the-judge law, closed until the steering-vise has a receipt | closed |
| the co-tenancy precondition on any race: `tiers_dropped` empty | M3 |

## reflex.contract

| change | rung |
|---|---|
| `questions_note.yaml` (`is_correction · is_policy_hint · is_hypothesis · is_question · is_look_instruction`) | M0.5 |
| `questions_state.yaml` (`is_material · dependency_resolved · now_contested · counts_as_discharge · trajectory`; `wake_worthy` defined, never asked live) | M3.5 |
| every question carries an arity tag; a relational question is admissible only over a keyed candidate set | M0.5 |
| calibration keyed by `(provider, question, band, stratum, questions_version)`; the fast-grader hook `grade_from_frame(next_frame)` | M0.5 / M3.5 |
| the owner as a provider: `declared_attention` with its curve | M0.5 |

## isobar.lock (keys added; values TODO until their rung)

`island` · `accelerator.backends` · `hand.{seal_budget_ms, state_budget_s, reply_channel}` · `recontext.dv_bar` · `ask.{max_per_day, voi_floor, window}` · `evict.after_ticks` · `precedent.min_n` · `collide.bars` · `realms` · `surprise.null: kalman` · `custody.{bins: 8, monotone_required: true}` · `rent.{budgets: [8, 32, 128, 512, inf], controls}` · `migration.required: true` · `witness.{slot, transports}` · `lattice.stocks` gains `UNRESOLVED` [applied in this revision].

## CLI verbs added

`isobar hand audit` · `isobar island on|off` · `isobar foresee --rehearse|--backtest` (M1) · `isobar presence twins` (M3) · `isobar rent --organ X --budget B` (M2) · `isobar migrate --from v --to v --map file` (M4).

## Tests to add (each with a mutant, L23)

the sampling lint extended to every new module · the arity tag lint on question sets · `hand audit` completeness · the island integration test (network cut) · the migration-map refusal · the corroboration render · the four-stock O4 · the keyed-only join property test (a similarity-only discharge must be refused with `ARITY_VIOLATION`).
