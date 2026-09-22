"""The hand lane in text (SPEC r0.2 §5): the forward address and the paste folder.

Two backends for the forward address — an mbox/eml export (the gym, and any client's export) and a
direct IMAP mailbox the owner owns (stdlib imaplib, read-only; refused with NETWORK_ABSENT on the
island). Both feed the same parser. A paste folder holds text captures dropped by hand.

A forward is two things stapled together (L3, L18): the owner's NOTE above the forward marker
(testimony, envelope trust operator) and the QUOTED ORIGINAL below it (evidence, payload trust by
origin). This module separates them and never interprets either.
"""
from __future__ import annotations

import email
import email.header
import email.utils
import hashlib
import imaplib
import mailbox
import os
import re
import socket
import time
from dataclasses import dataclass, field
from email.message import Message
from pathlib import Path
from typing import Any, Iterator, Optional

from isobard.contracts import Observation, blake128

# the markers mail clients put above a forwarded original, in the order they are tried
_MARKERS = [
    re.compile(r"^-{3,}\s*Forwarded message\s*-{3,}\s*$", re.I | re.M),          # Gmail
    re.compile(r"^-{3,}\s*Original Message\s*-{3,}\s*$", re.I | re.M),           # Outlook
    re.compile(r"^Begin forwarded message:\s*$", re.I | re.M),                   # Apple Mail
    re.compile(r"^-{3,}\s*Forwarded Message\s*-{3,}\s*$", re.I | re.M),          # Thunderbird
    re.compile(r"^From:\s.+\n(?:Sent|Date):\s.+\n(?:To:\s.+\n)?(?:Cc:\s.+\n)?Subject:\s.+$", re.I | re.M),  # a bare header block
]
_HDR = re.compile(r"^(From|Date|Sent|To|Cc|Subject|Message-ID|Message-Id)\s*:\s*(.+)$", re.I)
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", re.I)
_FWD_PREFIX = re.compile(r"^\s*((fwd?|fw|tr|wg)\s*:\s*)+", re.I)
_RE_PREFIX = re.compile(r"^\s*((re|fwd?|fw)\s*:\s*)+", re.I)


def _hdr(v: Any) -> str:
    if v is None:
        return ""
    try:
        s = str(email.header.make_header(email.header.decode_header(str(v))))
    except Exception:
        s = str(v)
    return s.encode("utf-8", "surrogateescape").decode("utf-8", "replace").replace("\n", " ").strip()


def _body(msg: Message) -> str:
    if msg.is_multipart():
        parts = []
        for p in msg.walk():
            if p.get_content_type() == "text/plain" and not p.get_filename():
                try:
                    parts.append(p.get_payload(decode=True).decode(p.get_content_charset() or "utf-8", "replace"))
                except Exception:
                    pass
        return "\n".join(parts)
    try:
        return msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8", "replace")
    except Exception:
        return str(msg.get_payload())


def norm_subject(s: str) -> str:
    return _RE_PREFIX.sub("", s or "").strip().lower()


@dataclass
class Forward:
    """A parsed forward: the owner's note and the quoted original, kept apart."""
    note: str
    quoted_headers: dict[str, str]
    quoted_body: str
    original_mid: Optional[str]
    original_from_email: str
    original_subject: str
    original_date_ns: Optional[int]
    forward_key: str          # blake(from_email | subject_norm)
    quoted_digest: str        # blake(normalised quoted body head)
    is_forward: bool


def parse_forward(subject: str, body: str) -> Forward:
    """Split a forward into the note above the marker and the quoted original below it."""
    text = body.replace("\r\n", "\n")
    cut = None
    for rx in _MARKERS:
        m = rx.search(text)
        if m and (cut is None or m.start() < cut):
            cut = m.start()
    if cut is None:
        # not a forward: the whole thing is the owner's own text (a paste sent by mail)
        return Forward(note=text.strip(), quoted_headers={}, quoted_body="", original_mid=None, original_from_email="",
                       original_subject=norm_subject(subject), original_date_ns=None,
                       forward_key=blake128(("|" + norm_subject(subject)).encode()), quoted_digest=blake128(b""), is_forward=False)
    note = text[:cut].strip()
    rest = text[cut:]
    # drop the marker line itself
    rest = rest.split("\n", 1)[1] if "\n" in rest else ""
    headers: dict[str, str] = {}
    lines = rest.split("\n")
    i = 0
    while i < len(lines):
        m = _HDR.match(lines[i].strip("> ").strip())
        if not m:
            if headers and lines[i].strip("> ").strip() == "":
                i += 1
                break
            if headers:
                break
            i += 1
            if i > 12:
                break
            continue
        headers[m.group(1).lower()] = m.group(2).strip()
        i += 1
    quoted_body = "\n".join(l.lstrip("> ") if l.startswith(">") else l for l in lines[i:]).strip()
    from_raw = headers.get("from", "")
    fm = _EMAIL.search(from_raw)
    from_email = fm.group(0).lower() if fm else ""
    subj = norm_subject(headers.get("subject", "") or _FWD_PREFIX.sub("", subject or ""))
    mid = headers.get("message-id")
    date_ns = None
    d = headers.get("date") or headers.get("sent")
    if d:
        try:
            dt = email.utils.parsedate_to_datetime(d)
            date_ns = int(dt.timestamp() * 1e9) if dt else None
        except Exception:
            date_ns = None
    head = re.sub(r"\s+", " ", quoted_body[:400]).strip().lower()
    return Forward(note=note, quoted_headers=headers, quoted_body=quoted_body, original_mid=mid.strip() if mid else None,
                   original_from_email=from_email, original_subject=subj, original_date_ns=date_ns,
                   forward_key=blake128((from_email + "|" + subj).encode()), quoted_digest=blake128(head.encode()), is_forward=True)


def network_available(host: str, port: int = 993, timeout: float = 3.0) -> bool:
    """A TCP reach test; honours ISOBAR_NETWORK=absent|present for the island test's software cut."""
    forced = os.environ.get("ISOBAR_NETWORK", "").lower()
    if forced == "absent":
        return False
    if forced == "present":
        return True
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


@dataclass
class HandMailbox:
    """The forward address. `backend='mbox'` reads an export; `backend='imap'` reads the owner's own mailbox."""
    address: str
    owner_email: str
    backend: str = "mbox"
    path: Optional[Path] = None
    imap_host: str = ""
    imap_user: str = ""
    imap_pass_env: str = "ISOBAR_HAND_IMAP_PASS"
    imap_folder: str = "INBOX"
    ingest_ns: Optional[int] = None
    max_bytes: int = 1_000_000
    refusals: list[dict[str, Any]] = field(default_factory=list)
    id = "hand_mbox"
    lanes = ("hand",)
    consent_class = "standard"

    def capabilities(self) -> list:
        return []           # the reply is not an effect on the world; it goes through the reply channel

    # ---- backends ----
    def _messages_mbox(self) -> Iterator[Message]:
        assert self.path is not None
        if self.path.is_dir():
            for p in sorted(self.path.glob("*.eml")):
                yield email.message_from_bytes(p.read_bytes())
        elif self.path.exists():
            for m in mailbox.mbox(str(self.path)):
                yield m

    def _messages_imap(self, cursor: Optional[str]) -> Iterator[Message]:
        if not network_available(self.imap_host):
            self.refusals.append({"code": "NETWORK_ABSENT", "host": self.imap_host, "ns": self.ingest_ns or time.time_ns()})
            return
        pw = os.environ.get(self.imap_pass_env, "")
        if not pw:
            self.refusals.append({"code": "CREDENTIALS_ABSENT", "env": self.imap_pass_env})
            return
        with imaplib.IMAP4_SSL(self.imap_host) as im:
            im.login(self.imap_user, pw)
            im.select(self.imap_folder, readonly=True)
            crit = f"(UID {int(cursor) + 1}:*)" if cursor else "ALL"
            typ, data = im.uid("search", None, crit)
            if typ != "OK":
                self.refusals.append({"code": "IMAP_SEARCH_FAILED"})
                return
            for uid in (data[0].split() if data and data[0] else []):
                typ, msg_data = im.uid("fetch", uid, "(RFC822)")
                if typ == "OK" and msg_data and isinstance(msg_data[0], tuple):
                    yield email.message_from_bytes(msg_data[0][1])

    def backfill(self, since_ns: int = 0, cursor: Optional[str] = None) -> Iterator[tuple[Observation, dict]]:
        now = self.ingest_ns or time.time_ns()
        msgs = self._messages_imap(cursor) if self.backend == "imap" else self._messages_mbox()
        for msg in msgs:
            frm = email.utils.parseaddr(_hdr(msg.get("From")))[1].lower()
            to = [a[1].lower() for a in email.utils.getaddresses([_hdr(msg.get("To")), _hdr(msg.get("Cc"))])]
            if self.address.lower() not in to:
                continue                     # only mail addressed to the hand address is a capture
            if frm != self.owner_email.lower():
                # mail to the hand address from anyone else is not the owner's act: it is data on the mail lane at best
                self.refusals.append({"code": "NOT_OWNER", "from": frm})
                continue
            mid = _hdr(msg.get("Message-ID")) or hashlib.blake2b(msg.as_bytes(), digest_size=8).hexdigest()
            subject = _hdr(msg.get("Subject"))
            body = _body(msg).encode("utf-8", "surrogateescape").decode("utf-8", "replace")
            d = _hdr(msg.get("Date"))
            try:
                dt = email.utils.parsedate_to_datetime(d) if d else None
                occ = int(dt.timestamp() * 1e9) if dt else now
            except Exception:
                occ = now
            if occ < since_ns:
                continue
            fwd = parse_forward(subject, body)
            payload_text = (f"From: {fwd.quoted_headers.get('from', '')}\nDate: {fwd.quoted_headers.get('date', fwd.quoted_headers.get('sent', ''))}\n"
                            f"Subject: {fwd.quoted_headers.get('subject', subject)}\n\n{fwd.quoted_body}") if fwd.is_forward else fwd.note
            payload = payload_text.encode("utf-8")
            obs = Observation(
                lane="hand", source=("hand_imap" if self.backend == "imap" else "hand_mbox"), external_id=mid, src_rev=0,
                occurred_ns=occ, ingested_ns=now, thread_id=fwd.original_mid or mid,
                payload_ref="inline:" + payload_text, digest=blake128(payload),
                intake_trust=("untrusted" if fwd.is_forward and fwd.original_from_email != self.owner_email.lower() else "operator"),
                envelope_trust="operator", declared=True, rendering=("forward" if fwd.is_forward else "paste"),
                note=(fwd.note or None) if fwd.is_forward else None,
                telemetry={"t_capture_ns": occ, "device_id": "mail", "client_subject": subject},
            ).with_id()
            yield obs, {"forward": fwd, "subject": subject, "body": body, "too_large": len(payload) > self.max_bytes,
                        "empty": (not fwd.quoted_body.strip()) if fwd.is_forward else (not fwd.note.strip())}

    def delta(self, cursor: str) -> Iterator[tuple[Observation, dict]]:
        return self.backfill(0, cursor)


@dataclass
class PasteFolder:
    """`hand/paste/*.txt`: text captures dropped by hand. A file name `YYYYMMDD-HHMM_anything.txt` carries its time."""
    path: Path
    ingest_ns: Optional[int] = None
    max_bytes: int = 1_000_000
    id = "hand_paste"
    lanes = ("hand",)
    consent_class = "standard"

    def capabilities(self) -> list:
        return []

    def backfill(self, since_ns: int = 0, cursor: Optional[str] = None) -> Iterator[tuple[Observation, dict]]:
        now = self.ingest_ns or time.time_ns()
        if not self.path.exists():
            return
        for p in sorted(self.path.glob("*.txt")):
            raw = p.read_bytes()
            text = raw.decode("utf-8", "replace")
            m = re.match(r"(\d{4})(\d{2})(\d{2})-(\d{2})(\d{2})_", p.name)
            if m:
                from datetime import datetime, timezone
                occ = int(datetime(int(m[1]), int(m[2]), int(m[3]), int(m[4]), int(m[5]), tzinfo=timezone.utc).timestamp() * 1e9)
            else:
                occ = int(p.stat().st_mtime_ns)
            if occ < since_ns:
                continue
            obs = Observation(lane="hand", source="hand_paste", external_id=p.name, src_rev=0, occurred_ns=occ, ingested_ns=now,
                              payload_ref="inline:" + text, digest=blake128(raw), intake_trust="operator", envelope_trust="operator",
                              declared=True, rendering="paste", telemetry={"t_capture_ns": occ, "device_id": "desktop", "file": p.name}).with_id()
            yield obs, {"text": text, "too_large": len(raw) > self.max_bytes, "empty": not text.strip()}

    def delta(self, cursor: str) -> Iterator[tuple[Observation, dict]]:
        return self.backfill(int(cursor) if cursor else 0)
