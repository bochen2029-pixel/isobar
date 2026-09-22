"""L3 / the purity lint: nothing learned writes state, disposes, or gates — and no probability is
compared to a constant above the gate."""
import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PURE = ["isobard/promote.py", "isobard/field.py", "isobard/scan.py", "isobard/tape.py", "isobard/contracts.py"]
LEARNED = {"isobard.reflex_client", "isobard.llm", "isobard.presence", "connectors", "reflex", "presence", "laya", "torch", "transformers"}
GATE_FILES = {"isobard/gate.py"}


def _imports(tree: ast.AST) -> set[str]:
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            out |= {a.name for a in n.names}
        elif isinstance(n, ast.ImportFrom) and n.module:
            out.add(n.module)
    return out


def _is_p(node: ast.AST) -> bool:
    if isinstance(node, ast.Attribute):
        return node.attr == "p" or node.attr.startswith("p_")
    if isinstance(node, ast.Name):
        return node.id == "p" or node.id.startswith("p_")
    return False


def test_pure_modules_import_nothing_learned():
    for rel in PURE:
        tree = ast.parse((ROOT / rel).read_text(encoding="utf-8"))
        bad = {m for m in _imports(tree) if any(m == L or m.startswith(L + ".") or m.startswith("." + L.split(".")[-1]) for L in LEARNED)}
        assert not bad, f"{rel} imports learned organs: {bad}"


def test_no_probability_is_compared_to_a_constant_above_the_gate():
    offenders = []
    for py in (ROOT / "isobard").glob("*.py"):
        rel = py.relative_to(ROOT).as_posix()
        if rel in GATE_FILES:
            continue
        tree = ast.parse(py.read_text(encoding="utf-8"))
        for n in ast.walk(tree):
            if isinstance(n, ast.Compare):
                sides = [n.left] + list(n.comparators)
                if any(_is_p(s) for s in sides) and any(isinstance(s, ast.Constant) and isinstance(s.value, (int, float)) for s in sides):
                    offenders.append(f"{rel}:{n.lineno}")
    assert not offenders, f"a p is thresholded above the gate: {offenders}"
