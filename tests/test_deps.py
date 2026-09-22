"""Recontextualisation is cone invalidation: only the dependents of a reinterpreted object are touched."""
from isobard.deps import DepGraph


def test_cone_is_transitive_dependents_only():
    g = DepGraph()
    g.add("cell1", ["obs1"])
    g.add("row1", ["obs1", "cell1"])
    g.add("row2", ["obs2"])
    g.add("field:1", ["row1", "row2"])
    g.add("finding1", ["row1"])
    cone = set(g.cone("obs1"))
    assert cone == {"cell1", "row1", "field:1", "finding1"}
    assert "row2" not in cone and "obs2" not in cone
    assert set(g.cone("row2")) == {"field:1"}
    assert g.cone("finding1") == []
    assert g.size() == (5, 7)


def test_self_and_empty_parents_are_ignored():
    g = DepGraph()
    g.add("a", ["a", "", "b"])
    assert g.parents["a"] == {"b"} and g.cone("b") == ["a"]
