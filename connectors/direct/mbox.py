"""mail lane from an mbox file or a folder of .eml files. Any provider can export one."""
from __future__ import annotations

import email
import email.utils
import hashlib
import mailbox
import time
from email.message import Message
from pathlib import Path
from typing import Iterator, Optional

from isobard.contracts import Observation, blake128


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


def _ns(msg: Message) -> int:
    d = msg.get("Date")
    try:
        t = email.utils.parsedate_to_datetime(d) if d else None
        return int(t.timestamp() * 1e9) if t else time.time_ns()
    except Exception:
        return time.time_ns()


class MboxConnector:
    id = "mbox"
    lanes = ("mail",)
    consent_class = "standard"

    def __init__(self, path: Path, owner_email: str = "", source_name: str = "mbox"):
        self.path = Path(path)
        self.owner_email = owner_email.lower()
        self.source_name = source_name

    def capabilities(self) -> list:
        return []  # read-only export: no effects

    def _messages(self) -> Iterator[Message]:
        if self.path.is_dir():
            for p in sorted(self.path.glob("*.eml")):
                yield email.message_from_bytes(p.read_bytes())
        else:
            for m in mailbox.mbox(str(self.path)):
                yield m

    def backfill(self, since_ns: int = 0, cursor: Optional[str] = None) -> Iterator[tuple[Observation, dict]]:
        """Yields (Observation, parsed) where parsed carries the fields the plane's CODE stage uses."""
        now = time.time_ns()
        for msg in self._messages():
            occ = _ns(msg)
            if occ < since_ns:
                continue
            mid = (msg.get("Message-ID") or "").strip() or hashlib.blake2b(msg.as_bytes(), digest_size=8).hexdigest()
            body = _body(msg)
            headers = {k: msg.get(k, "") for k in ("From", "To", "Cc", "Subject", "Message-ID", "In-Reply-To", "References", "Date")}
            text = f"From: {headers['From']}\nTo: {headers['To']}\nSubject: {headers['Subject']}\nDate: {headers['Date']}\n\n{body}"
            payload = text.encode("utf-8")
            frm = email.utils.parseaddr(headers["From"])[1].lower()
            obs = Observation(
                lane="mail", source=self.source_name, external_id=mid, src_rev=0, occurred_ns=occ, ingested_ns=now,
                thread_id=(msg.get("In-Reply-To") or msg.get("References", "").split()[-1:] or [mid])[0].strip() if (msg.get("In-Reply-To") or msg.get("References")) else mid,
                payload_ref="inline:" + text, digest=blake128(payload),
                intake_trust="operator" if (self.owner_email and frm == self.owner_email) else "untrusted",
            ).with_id()
            yield obs, {"headers": headers, "body": body, "from_email": frm,
                        "to_emails": [a[1].lower() for a in email.utils.getaddresses([headers["To"], headers["Cc"]])],
                        "outbound": bool(self.owner_email and frm == self.owner_email)}

    def delta(self, cursor: str) -> Iterator[tuple[Observation, dict]]:
        return self.backfill(int(cursor) if cursor else 0)
