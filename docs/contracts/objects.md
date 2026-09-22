# objects.contract — the typed objects

*Single definition. `isobard/contracts.py` (Pydantic v2) and `solver/isobar_types.h` (C structs) MUST round-trip every fixture under `tests/fixtures/objects/` byte-for-byte (M0 gate). Field order is normative for canonical JSON and for the content address.*

Identifiers: `id` is `blake2b-128(CANON-JSON(content fields))` where content is immutable (Observation, Cell, Hold, Wager, Grade); UUIDv7 elsewhere. Times: UTC nanoseconds (`i64`). Money: minor units (`i64`) + ISO-4217.

```
Observation {
  id, lane ∈ {mail, cal, list, tick, compose, contacts, money, location},
  source, external_id, src_rev (monotone: equal ⇒ no-op, lower ⇒ refused),
  occurred_ns, ingested_ns, actor_ids[], thread_id?, payload_ref, digest,
  intake_trust ∈ {operator, trusted, untrusted}, injection_shape: bool
}

Cell {                                       -- the reflex's output for one Observation
  observation_id, provider, provider_fp, questions_version,
  fields: { name → { value, p ∈ [0,1], provenance ∈ {HIGH, MOD, LOW_absent, LOW_conflict} } },
  latency_us
}

Join {
  observation_id,
  candidates: [ { kind ∈ {commitment, actor, thread, money_object}, id, p } ],
  method ∈ {exact, lexical, embed_rerank_reflex}, exact_key?
}

Commitment {                                 -- canonical; a Row is its solver projection
  id, debtor_actor, creditor_actor, kind ∈ {deliverable, payment, quote, response, appointment, document, approval, purchase, other},
  deliverable_text, project?, money_object?, release_ns?, due: { earliest?, latest?, p_hard }, 
  effort: { opt_min, nom_min, cons_min, source ∈ {explicit, class_prior, history, owner, model}, confidence },
  dependencies[], required_seats[], tier_key (from the people registry),
  state ∈ {candidate, active, waiting, scheduled, in_progress, at_risk, discharged, cancelled, superseded, contested},
  evidence[] (observation ids), p_promoted, state_version
}

Row {                                        -- SoA in the solver; 32 B scalar + int8[128] + f32 scale
  entity (actor id → int), cls, kind, dur_slots (sampled per future from effort), src, t_release_slot, t_due_slot,
  p_hard, work, dep, inc_cell, law_flags, tier_weight, emb_int8[128], emb_scale, p_join[] 
}

Field {
  tick_id, state_version, N, M, v[M] (as deltas on the tape), u[N], es[N], risk[N], argmax_cell[N],
  contra[] { a, b?, kind ∈ {OVERCOMMIT, DOUBLEBOOK, DEPENDENCY, DEADLINE, DUPLICATE, TRAVEL, PAID}, weight, p? },
  stock_prices { UNPLACED, UNADJUDICATED, WAITING }, binding_days[], 
  delta_v_norm (‖Δv‖ of the last event), arithmetic { bytes, ms, gbs, peak_gbs, fraction }, iters, arm
}

Future {                                     -- never on the tape individually; summarised in Foresight
  seed, move, sampled { dur[], due_hard[], join[], arrivals[], latency[], overrun[], calendar_truth, travel[], payment[] },
  J, J_terms { hard, soft, ext, backlog, wait, ask, churn, buffer, frag, overtime }, breaches[]
}

Foresight {
  tick_id, K, H, iters_future, seed,
  survival[N] { p, lo, hi },
  moves: [ { move ∈ MENU, target?, param?, J_mean, J_std, J_pess } ],
  pipper: { move, forecast_J, do_nothing_J, band },
  compute { universes_per_s, ms, device ∈ {cpu, gpu}, tiers_dropped[] }
}

FieldDelta {                                 -- one typed line per tick for the resident's lane; ≤ 128 tokens
  tick_id, text: "[field] Thu14 0.61→0.83 BIND · #17 sup 1.2→4.1 CONTESTED · #22 breach .61 · wait:Lopez .40 · Δv .37"
}

Hold {                                       -- LIFELINE v5 §6.3, verbatim
  boundary_id, lane, tape_pos, seat ∈ {FIELD_WATCH, COMPOSER, SENTINEL},
  margins { emit, hold, wake, ask, glance }, verdict ∈ {SILENT, FLAG, ASK, DRAFT, WAKE, HOLD, UNSAY},
  reason (closed enum, see gate.contract), gear ∈ {0,1,2,3}, latency_us,
  aired[]?, killed?, trigger ∈ {evidence, key, tick}
}

Verdict { intent_id, verb ∈ {SILENT, FLAG, ASK, DRAFT, ONE_CLICK, ACT, HOLD, RECHECK}, reason, class, licence_rung,
          exposure_after, inverse_window_s?, gate_build_hash, state_version }

Intent  = ScheduleDelta { event_id | new, from_slot?, to_slot, attendees[]?, reason_code }
        | DraftIntent   { thread_id, act ∈ {accept, decline, counter, nudge, confirm, request}, proposed_ns?,
                          disclosed_reason (policy enum), tone (policy enum), commitment_id? }
        | TaskDelta     { op ∈ {create, complete, defer, reorder}, commitment_id, due_ns?, note? }

Effect  { id, intent_id, target, payload, inverse | "irreversible", precondition { state_version, remote_version? },
          idempotency_key, hold_window_s, state ∈ {planned, held, fired, verified, failed, unknown, unwound} }

Receipt { effect_id, fired_ns, remote_result, verified: bool, verification_source }

Wager   { effect_id?, commitment_id, forecast_survival { p, lo, hi }, horizon_ns, shown: bool, graded_ns?, outcome? }

Grade   { subject ∈ {effect, wake, draft, wager, move}, subject_id,
          kind ∈ {sent_as_is, edited, discarded, undone, ignored, acted_within, kept, slipped, replied, silent, paid, complaint},
          diff?, t_delta_s?, salted: bool, ns }

Actor / Place / MoneyObject — see registry.contract.
```

**Two rules.** A `p` is never compared to a constant above the gate (it is sampled). A `Grade` with `salted: false` never enters a licence computation (it may enter calibration).
