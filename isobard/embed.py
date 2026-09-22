"""Embeddings for the join and the solver's int8 rows.

The local OpenAI-shaped endpoint on :8092 (qwen3-embedding-0.6b, already running on this box) is
used when up; otherwise a deterministic hashed bag-of-words embedding keeps the pipeline runnable
and the receipt says `embedder: hash-fallback`. Either way the solver gets 128-d int8 rows: a fixed
seeded random projection of the full vector, then per-vector int8 quantisation with an f32 scale
(the T2 transposition; O5 gates the round-trip cosine ≥ 0.995 on the solver side).
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import urllib.request
from typing import Optional

import numpy as np

ENDPOINT = "http://127.0.0.1:8092/v1/embeddings"
COARSE_D = 128
_TOK = re.compile(r"[a-z0-9]+")


class Embedder:
    def __init__(self, endpoint: str = ENDPOINT, timeout: float = 20.0, seed: int = 20260922):
        self.endpoint = endpoint
        self.timeout = timeout
        self.seed = seed
        self.kind = "unknown"
        self.dim = 0
        self._proj: Optional[np.ndarray] = None

    def _remote(self, texts: list[str]) -> Optional[np.ndarray]:
        try:
            req = urllib.request.Request(self.endpoint, data=json.dumps({"input": texts}).encode(), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=self.timeout) as r:
                d = json.loads(r.read().decode())
            vecs = np.array([row["embedding"] for row in d["data"]], dtype=np.float32)
            return vecs
        except Exception:
            return None

    @staticmethod
    def _hash(texts: list[str], dim: int = 1024) -> np.ndarray:
        out = np.zeros((len(texts), dim), dtype=np.float32)
        for i, t in enumerate(texts):
            for tok in _TOK.findall(t.lower()):
                h = hashlib.blake2b(tok.encode(), digest_size=8).digest()
                j = int.from_bytes(h[:4], "little") % dim
                s = 1.0 if h[4] & 1 else -1.0
                out[i, j] += s
            n = np.linalg.norm(out[i]) or 1.0
            out[i] /= n
        return out

    @property
    def dup_floor(self) -> float:
        """The unkeyed-duplicate cosine floor is a property of the embedding model, never inherited across models:
        bag-of-words cosines run lower than a trained embedder's. Placeholders until the trough is measured (B19)."""
        return 0.55 if self.kind == "hash-fallback" else 0.75

    def embed(self, texts: list[str]) -> np.ndarray:
        if not texts:
            return np.zeros((0, 1024), dtype=np.float32)
        import os
        vecs = None if os.environ.get("ISOBAR_EMBED", "").lower() == "hash" else self._remote(texts)
        if vecs is None:
            vecs = self._hash(texts)
            self.kind = "hash-fallback"
        else:
            self.kind = "qwen3-embedding-0.6b@8092"
        vecs = vecs / (np.linalg.norm(vecs, axis=1, keepdims=True) + 1e-9)
        self.dim = vecs.shape[1]
        return vecs

    def coarse_int8(self, full: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        """128-d int8 + f32 scale per row, via a fixed seeded Gaussian projection."""
        if self._proj is None or self._proj.shape[0] != full.shape[1]:
            rng = np.random.default_rng(self.seed)
            self._proj = (rng.standard_normal((full.shape[1], COARSE_D)) / math.sqrt(COARSE_D)).astype(np.float32)
        c = full @ self._proj
        c = c / (np.linalg.norm(c, axis=1, keepdims=True) + 1e-9)
        scale = (np.abs(c).max(axis=1) / 127.0 + 1e-12).astype(np.float32)
        q = np.clip(np.rint(c / scale[:, None]), -127, 127).astype(np.int8)
        return q, scale

    @staticmethod
    def cos(a: np.ndarray, b: np.ndarray) -> float:
        return float(np.dot(a, b) / ((np.linalg.norm(a) * np.linalg.norm(b)) + 1e-9))
