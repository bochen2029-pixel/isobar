# connectors/ — lanes in, effects out, nothing interpreted

**Nothing here is built.** Contract: `docs/contracts/connector.md`. Two implementations per lane from M0 so no vendor is the only path to the owner's own mail.

```
composio/     mail · cal · list · contacts via the hosted broker (14 connections already minted on this box, 2026-09-20)
direct/
  imap.py         mail (IMAP/SMTP; any provider)
  gmail_api.py    mail
  graph_mail.py   mail (Microsoft Graph)
  caldav.py       cal (any CalDAV server)
  gcal.py         cal
  graph_cal.py    cal
  todoist.py      list
  mstodo.py       list
  gtasks.py       list
  textfile.py     list (a plain markdown/todo.txt file; the owner's testimony lane at its simplest)
  contacts_vcf.py contacts seed (vCard export); contacts_google.py; contacts_ms.py
  stripe.py · quickbooks.py · xero.py · bankfeed.py     money — READ-ONLY verdict sources; capabilities() == []
  location_phone.py                                     location — consent-gated; refuses without a consent row
```

## Laws

- A connector emits `Observation` and never an assertion; what it cannot carry is a typed refusal.
- Idempotent by `(source, external_id, src_rev)`; equal ⇒ no-op, lower ⇒ refused.
- Reversibility and inverses are declared in `capabilities()` and nowhere else.
- `verify()` re-reads the remote object after every effect; an unverified effect is `unknown`, never `fired`.
- Recurring calendar events are expanded within the horizon at ingest; the rule is provenance. Tentative events carry their acceptance probability. All-day events consume zero slots unless policy says otherwise.
- SMS, if a provider exposes it, enters the mail lane with provenance `sms`.
- Credentials live in the plane's keystore, never in a branch, never in a log.

## Testing

`tests/fixtures/connectors/` holds recorded backfills per adapter (redacted); every adapter replays its fixture byte-identically into the tape; the injection corpus per lane runs through every adapter.
