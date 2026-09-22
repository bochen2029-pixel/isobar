"""The tape — the only truth (docs/contracts/tape.md).

Append-only, blake2b-128 hash-chained, fsync'd per record, ONE WRITER PER SEGMENT: the OS refuses a
second handle (a byte-range lock on the segment) — two Windows processes appending to one file lost
66/78/73 of 120 rows, both exiting 0 [M, scriptorium QC 2026-09-04], so this is enforced, not advised.

Row (one JSON line):  {"seq", "kind", "ref", "ts", "body", "prev", "hash"}
  hash = blake2b-128( prev ‖ kind ‖ ref ‖ ts ‖ canon(body) )
Torn tail: a final line without a newline, or one that fails to parse, is detected, exposed as the
readable prefix, reported benign, and truncated before any later append.
"""
from __future__ import annotations

import io
import json
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator, Optional

from .contracts import blake128, canon

KINDS = frozenset({
    "observation", "cell", "join", "promotion", "field", "foresight", "hold", "switch", "verdict",
    "intent", "effect", "receipt", "wager", "grade", "calibration", "licence", "policy", "correction",
    "registry", "tick", "coalesce", "finding", "run",
})
GENESIS = "0" * 32


class TapeError(Exception):
    pass


class SecondWriter(TapeError):
    """Raised when a segment is already held by another writer."""


# Windows byte-range locks are mandatory: a locked byte cannot be READ by another process either.
# So the writer's exclusive lock sits one byte at an offset no row will ever reach (2^40), where it
# blocks nothing but a second writer's attempt to take the same byte. Readers read data freely.
LOCK_OFFSET = 1 << 40


def _lock(fd: int) -> None:
    if sys.platform == "win32":
        import msvcrt
        pos = os.lseek(fd, 0, os.SEEK_CUR)
        os.lseek(fd, LOCK_OFFSET, os.SEEK_SET)
        try:
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        except OSError as e:
            raise SecondWriter(f"segment held by another writer: {e}") from e
        finally:
            os.lseek(fd, pos, os.SEEK_SET)
    else:
        import fcntl
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as e:
            raise SecondWriter(f"segment held by another writer: {e}") from e


def _unlock(fd: int) -> None:
    if sys.platform == "win32":
        import msvcrt
        pos = os.lseek(fd, 0, os.SEEK_CUR)
        os.lseek(fd, LOCK_OFFSET, os.SEEK_SET)
        try:
            msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        except OSError:
            pass
        finally:
            os.lseek(fd, pos, os.SEEK_SET)
    else:
        import fcntl
        fcntl.flock(fd, fcntl.LOCK_UN)


def row_hash(prev: str, kind: str, ref: str, ts: int, body: Any) -> str:
    pre = f"{prev}\x1f{kind}\x1f{ref}\x1f{ts}\x1f{canon(body)}".encode("utf-8")
    return blake128(pre)


@dataclass
class Row:
    seq: int
    kind: str
    ref: str
    ts: int
    body: Any
    prev: str
    hash: str

    def to_line(self) -> str:
        return canon({"seq": self.seq, "kind": self.kind, "ref": self.ref, "ts": self.ts,
                      "body": self.body, "prev": self.prev, "hash": self.hash}) + "\n"

    @classmethod
    def from_line(cls, line: str) -> "Row":
        d = json.loads(line)
        return cls(d["seq"], d["kind"], d["ref"], d["ts"], d["body"], d["prev"], d["hash"])


@dataclass
class Torn:
    """A torn tail: the readable prefix ends at `good_bytes`; `tail` is what was found after it."""
    good_bytes: int
    tail: bytes


class Segment:
    """One writer's append-only file. Open it as the writer (holds the lock) or as a reader."""

    def __init__(self, path: Path, writer: bool = False, fsync: bool = True):
        self.path = Path(path)
        self.fsync = fsync
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fd: Optional[int] = None
        self.last_seq = -1
        self.head = GENESIS
        self.torn: Optional[Torn] = None
        self._scan()
        if writer:
            self._fd = os.open(str(self.path), os.O_WRONLY | os.O_APPEND | os.O_CREAT | getattr(os, "O_BINARY", 0))
            try:
                _lock(self._fd)
            except SecondWriter:
                os.close(self._fd)
                self._fd = None
                raise
            if self.torn is not None:
                # truncate the torn tail BEFORE any later append (the contract)
                os.ftruncate(self._fd, self.torn.good_bytes)
                self.torn = None

    # ---- reading ----
    def _scan(self) -> None:
        self.last_seq = -1
        self.head = GENESIS
        self.torn = None
        if not self.path.exists():
            return
        data = self.path.read_bytes()
        good = 0
        for line in data.splitlines(keepends=True):
            if not line.endswith(b"\n"):
                self.torn = Torn(good, line)
                break
            try:
                r = Row.from_line(line.decode("utf-8"))
            except (json.JSONDecodeError, KeyError, UnicodeDecodeError):
                self.torn = Torn(good, line)
                break
            self.last_seq = r.seq
            self.head = r.hash
            good += len(line)
        else:
            return

    def rows(self) -> Iterator[Row]:
        if not self.path.exists():
            return
        with open(self.path, "rb") as f:
            for line in f:
                if not line.endswith(b"\n"):
                    return
                try:
                    yield Row.from_line(line.decode("utf-8"))
                except (json.JSONDecodeError, KeyError, UnicodeDecodeError):
                    return

    def verify(self) -> tuple[bool, str]:
        """Re-hash every row and check the chain. Needs zero keys."""
        prev = GENESIS
        n = 0
        for r in self.rows():
            if r.prev != prev:
                return False, f"prev-hash mismatch at seq {r.seq}"
            if r.seq != n:
                return False, f"seq gap at {r.seq} (expected {n})"
            if row_hash(r.prev, r.kind, r.ref, r.ts, r.body) != r.hash:
                return False, f"hash mismatch at seq {r.seq}"
            prev = r.hash
            n += 1
        return True, f"{n} rows, head {prev}"

    # ---- writing ----
    def append(self, kind: str, ref: str, body: Any, ts: Optional[int] = None) -> Row:
        if self._fd is None:
            raise TapeError("segment opened read-only")
        if kind not in KINDS:
            raise TapeError(f"unknown row kind {kind!r}")
        ts = time.time_ns() if ts is None else int(ts)
        seq = self.last_seq + 1
        h = row_hash(self.head, kind, ref, ts, body)
        row = Row(seq, kind, ref, ts, body, self.head, h)
        os.write(self._fd, row.to_line().encode("utf-8"))
        if self.fsync:
            os.fsync(self._fd)
        self.last_seq = seq
        self.head = h
        return row

    def close(self) -> None:
        if self._fd is not None:
            try:
                _unlock(self._fd)
            finally:
                os.close(self._fd)
                self._fd = None

    def __enter__(self) -> "Segment":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()


class Tape:
    """The store: store/tape/segments/<writer>.seg + MANIFEST (derived)."""

    def __init__(self, store: Path, writer: Optional[str] = None, fsync: bool = True):
        self.store = Path(store)
        self.segdir = self.store / "tape" / "segments"
        self.segdir.mkdir(parents=True, exist_ok=True)
        self.writer = writer
        self.seg: Optional[Segment] = None
        if writer is not None:
            self.seg = Segment(self.segdir / f"{writer}.seg", writer=True, fsync=fsync)

    def append(self, kind: str, ref: str, body: Any, ts: Optional[int] = None) -> Row:
        if self.seg is None:
            raise TapeError("tape opened read-only")
        return self.seg.append(kind, ref, body, ts)

    def segments(self) -> list[Path]:
        return sorted(self.segdir.glob("*.seg"))

    def rows(self) -> Iterator[tuple[str, Row]]:
        """Global order: (ts, writer, seq) — deterministic given the files."""
        heads: list[tuple[int, str, int, Row]] = []
        for p in self.segments():
            w = p.stem
            for r in Segment(p).rows():
                heads.append((r.ts, w, r.seq, r))
        heads.sort(key=lambda t: (t[0], t[1], t[2]))
        for ts, w, seq, r in heads:
            yield w, r

    def verify(self) -> tuple[bool, list[str]]:
        ok_all = True
        report = []
        for p in self.segments():
            s = Segment(p)
            ok, msg = s.verify()
            ok_all &= ok
            report.append(f"{p.name}: {'OK' if ok else 'FAIL'} — {msg}" + (f" (torn tail {len(s.torn.tail)} B, benign)" if s.torn else ""))
        return ok_all, report

    def manifest(self) -> dict[str, Any]:
        m: dict[str, Any] = {"segments": []}
        for p in self.segments():
            s = Segment(p)
            m["segments"].append({"segment": p.name, "last_seq": s.last_seq, "head": s.head,
                                  "bytes": p.stat().st_size, "torn": s.torn is not None})
        (self.store / "tape" / "MANIFEST").write_text(canon(m), encoding="utf-8")
        return m

    def close(self) -> None:
        if self.seg is not None:
            self.seg.close()
            self.seg = None
