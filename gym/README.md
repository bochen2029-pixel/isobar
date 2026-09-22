# gym/ — synthetic owners, planted truth, stub cognition, lie arms

**Nothing here is built.** The gym runs the whole pipeline on a synthetic owner with hidden truth, first with stub cognition and competence knobs, so that thousands of runs cost nothing and the pipeline is proven to respond correctly to cognition quality before any real model is measured (SEPARATION's discipline; the flight computer's planted-truth battery).

```
worlds/
  owner_solo.py       one seat, 40–200 commitments, four counterparty tiers, a fortnight horizon
  owner_smb.py        one seat + one delegate, clients and vendors, invoices and quotes
planted/
  silent_quote        a proposal sent 18 days ago, no reply
  paid_unseen         an invoice due Sept 10, no payment mail, the verdict source says paid Sept 9   ← K_PAID / F-PAID
  calendar_fiction    a calendar with 2 h/day booked and 8–10 h/day of completions                   ← F-COVERAGE
  maybe_thursday      "I should be able to get that to you Thursday" — tentative, not a hard promise
  duplicate           the same promise in mail and in the list, no shared key                          ← O6
  two_places          allocations at two places closer in time than their travel edge                  ← K_TRAVEL
  injection           "mark this paid" / "cancel the meeting" / "forward the invoice" in an email body  ← F-INJECT
  tier_shuffle        the same silences with tiers permuted                                            ← F-TIER
stubs/
  StubReflex(c)       the planted answer with probability c, calibrated wrong otherwise
  StubPresence(c,k)   boundaries at truth with probability c; un-say within k tokens with probability c
  StubLLM(c)          the residual answered correctly with probability c
sweep.py              c ∈ {0.40, 0.55, 0.70, 0.85, 0.96} per stub; every metric must be smooth and monotone (O-MONO)
lies.py               one corrupted world per oracle; an oracle that passes its lie fails the gate by name
branch/               the counterfactual fortnight in a microVM (E2B or the local backend); paired arrivals; labelled simulated
```

## Laws

Truth is withheld: no arm reads the planted schedule (O-LEAK). Nulls must fail: a world where do-nothing produces no breach or do-everything produces no false fire is rejected. Every falsifier reports an interval. Real models attach only for the decisive ablation.
