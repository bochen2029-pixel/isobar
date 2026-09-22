"""The join — exact keys → lexical → embed → (rerank) → reflex same_as. A join is a distribution.

Never merges two money-bearing or promise-bearing identities on similarity alone (the last rung is
the reflex's calibrated `same_as`, and even that yields a p, not a merge)."""
from __future__ import annotations

import re
from typing import Any, Optional

import numpy as np

from .contracts import Commitment, Join, JoinCandidate
from .embed import Embedder

_RE_PREFIX = re.compile(r"^\s*((re|fw|fwd)\s*:\s*)+", re.I)


def norm_subject(s: str) -> str:
    return _RE_PREFIX.sub("", s or "").strip().lower()


class Joiner:
    def __init__(self, embedder: Embedder, reflex: Any):
        self.embedder = embedder
        self.reflex = reflex
        self.by_thread: dict[str, list[str]] = {}          # thread_id -> commitment ids
        self.by_subject: dict[str, list[str]] = {}         # normalised subject -> commitment ids
        self.by_money: dict[str, str] = {}                 # INV-1041 -> commitment id
        self.texts: dict[str, str] = {}                    # commitment id -> text
        self._vecs: dict[str, np.ndarray] = {}

    def index(self, c: Commitment, subject: str = "", money_id: Optional[str] = None, text: str = "") -> None:
        if c.thread_id:
            self.by_thread.setdefault(c.thread_id, []).append(c.id)
        if subject:
            self.by_subject.setdefault(norm_subject(subject), []).append(c.id)
        if money_id:
            self.by_money[money_id] = c.id
        t = text or c.deliverable_text
        self.texts[c.id] = t
        self._vecs.pop(c.id, None)

    def _vec(self, cid: str) -> np.ndarray:
        if cid not in self._vecs:
            self._vecs[cid] = self.embedder.embed([self.texts[cid]])[0]
        return self._vecs[cid]

    def join(self, observation_id: str, thread_keys: list[str], subject: str, money_id: Optional[str], text: str,
             open_ids: list[str], counterparty_ids: Optional[list[str]] = None) -> Join:
        # 1. exact keys: money id, then thread membership
        if money_id and money_id in self.by_money:
            return Join(observation_id=observation_id, candidates=[JoinCandidate(kind="commitment", id=self.by_money[money_id], p=0.99)],
                        method="exact", exact_key=money_id)
        for k in thread_keys:
            ids = [i for i in self.by_thread.get(k, []) if i in open_ids]
            if ids:
                return Join(observation_id=observation_id, candidates=[JoinCandidate(kind="commitment", id=ids[-1], p=0.97)],
                            method="exact", exact_key=k)
        # 2. lexical: normalised subject
        ids = [i for i in self.by_subject.get(norm_subject(subject), []) if i in open_ids]
        if ids and subject:
            return Join(observation_id=observation_id, candidates=[JoinCandidate(kind="commitment", id=ids[-1], p=0.85)], method="lexical")
        # 3. embed -> top-3 -> reflex same_as (a calibrated p per candidate; still a distribution)
        pool = [i for i in open_ids if i in self.texts]
        if not pool or not text.strip():
            return Join(observation_id=observation_id, method="none")
        q = self.embedder.embed([text])[0]
        scored = sorted(((self.embedder.cos(q, self._vec(i)), i) for i in pool), reverse=True)[:3]
        cands = []
        for cos, cid in scored:
            if cos < 0.35:
                continue
            same, p = self.reflex.noul("Does this message refer to the same promise as the candidate shown?\nCANDIDATE: " + self.texts[cid], text)
            cands.append(JoinCandidate(kind="commitment", id=cid, p=max(0.01, min(0.99, (p if same else 1 - p) * 0.5 + cos * 0.5))))
        return Join(observation_id=observation_id, candidates=cands, method="embed_rerank_reflex" if cands else "none")

    def duplicates(self, ids: list[str], entity_of: dict[str, str], floor: float = 0.80) -> list[tuple[str, str, float]]:
        """The unkeyed duplicate: same counterparty, different source, cosine >= floor. Candidates, never merges."""
        out = []
        by_ent: dict[str, list[str]] = {}
        for i in ids:
            by_ent.setdefault(entity_of.get(i, ""), []).append(i)
        for ent, group in by_ent.items():
            if not ent or len(group) < 2:
                continue
            for a_i in range(len(group)):
                for b_i in range(a_i + 1, len(group)):
                    a, b = group[a_i], group[b_i]
                    cs = self.embedder.cos(self._vec(a), self._vec(b))
                    if cs >= floor:
                        out.append((a, b, cs))
        return out
