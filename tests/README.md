# tests/ — what a green build proves

**Nothing here is built.** Every gate step asserts on a return code; every test binary prints `N/N`; a quoted number without a reproducing script under `runs/` is not a number.

```
fixtures/
  objects/         one JSON fixture per object; isobard/contracts.py and solver/isobar_types.h round-trip byte-for-byte
  connectors/      recorded, redacted backfills per adapter; replay must be byte-identical into the tape
  emails_200/      the owner-labelled reflex set (frozen before any provider runs)
  injection/       per-lane hostile corpus
replay/            tape → folds → byte-identity; torn-tail both directions; second-writer refused by the OS
purity/            the import lint: promote/, gate/, field/, foresee/ import nothing learned; no p compared to a constant above the gate
solver/            the oracles O1–O9 via the instruments' own --selftest --lie N; parity
properties/        adding an irrelevant commitment does not alter an unrelated slot's price beyond noise;
                   paraphrasing a message does not change the accepted commitment; a duplicate delivery does not change state;
                   moving an unrelated event does not change a distant plan; a p above the gate is never compared to a constant
falsifiers/        the scorers: F-RECOVERY, F-JEV, F-JOIN, F-TIER, F-PRICE, F-WAGER, F-ROOFLINE, F-COMPOSER, F-RESIDENT,
                   F-INERT, F-KAPPA, F-INJECT, F-PAID, F-TRAVEL, F-COVERAGE, F-NOISE, F-BASELINE — each with its lie arm
```

Run (planned): `python -m pytest` for the plane; `solver/build.cmd` runs the instruments' selftests; `isobar selftest` runs everything and prints one `N/N` line per battery.
