"""The dependency graph — recontextualisation is cone invalidation, never a rescan (SPEC r0.2 §10.4).

Every derived object names what it depends on (`depends_on`). When an object is reinterpreted — a
capture resolves, a verdict arrives, a correction lands — the cone ABOVE it (its transitive
dependents) is invalidated and refolded, and nothing outside the cone is touched. The graph is a
fold over the objects already on the tape; this module holds the in-memory index for one run.
"""
from __future__ import annotations

from collections import defaultdict, deque
from typing import Iterable


class DepGraph:
    def __init__(self) -> None:
        self.parents: dict[str, set[str]] = defaultdict(set)
        self.children: dict[str, set[str]] = defaultdict(set)

    def add(self, child: str, parents: Iterable[str]) -> None:
        for p in parents:
            if p and p != child:
                self.parents[child].add(p)
                self.children[p].add(child)

    def dependents(self, obj_id: str) -> set[str]:
        return set(self.children.get(obj_id, ()))

    def cone(self, obj_id: str) -> list[str]:
        """Transitive dependents of `obj_id`, in BFS order, excluding itself. Bounded by the graph."""
        seen: set[str] = set()
        out: list[str] = []
        q: deque[str] = deque(self.children.get(obj_id, ()))
        while q:
            x = q.popleft()
            if x in seen:
                continue
            seen.add(x)
            out.append(x)
            q.extend(self.children.get(x, ()))
        return out

    def size(self) -> tuple[int, int]:
        return len(self.parents), sum(len(v) for v in self.parents.values())
