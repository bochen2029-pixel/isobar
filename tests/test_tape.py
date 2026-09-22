"""The tape: chain, second writer refused by the OS, torn tail, corruption caught, global order."""
import subprocess
import sys
from pathlib import Path

import pytest

from isobard.tape import GENESIS, Segment, SecondWriter, Tape, TapeError

ROOT = Path(__file__).resolve().parents[1]


def test_append_and_verify(tmp_path):
    t = Tape(tmp_path, writer="plane", fsync=False)
    r0 = t.append("observation", "o1", {"a": 1}, ts=100)
    r1 = t.append("cell", "c1", {"b": [1, 2]}, ts=101)
    assert r0.prev == GENESIS and r1.prev == r0.hash and r1.seq == 1
    t.close()
    ok, report = Tape(tmp_path).verify()
    assert ok, report
    assert "2 rows" in report[0]


def test_unknown_kind_refused(tmp_path):
    t = Tape(tmp_path, writer="plane", fsync=False)
    with pytest.raises(TapeError):
        t.append("opinion", "x", {})
    t.close()


def test_second_writer_is_refused_by_the_os(tmp_path):
    t = Tape(tmp_path, writer="plane", fsync=False)
    t.append("tick", "t", {"gap_s": 1}, ts=1)
    seg = tmp_path / "tape" / "segments" / "plane.seg"
    code = (
        "import sys; sys.path.insert(0, %r)\n"
        "from isobard.tape import Segment, SecondWriter\n"
        "from pathlib import Path\n"
        "try:\n"
        "    Segment(Path(%r), writer=True, fsync=False); print('ACQUIRED')\n"
        "except SecondWriter:\n"
        "    print('REFUSED')\n"
    ) % (str(ROOT), str(seg))
    out = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=60)
    assert "REFUSED" in out.stdout, out.stdout + out.stderr
    t.close()
    out2 = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=60)
    assert "ACQUIRED" in out2.stdout, out2.stdout + out2.stderr


def test_torn_tail_is_detected_exposed_and_truncated_before_append(tmp_path):
    t = Tape(tmp_path, writer="plane", fsync=False)
    t.append("observation", "o1", {"a": 1}, ts=5)
    t.append("observation", "o2", {"a": 2}, ts=6)
    t.close()
    seg = tmp_path / "tape" / "segments" / "plane.seg"
    good = seg.stat().st_size
    with open(seg, "ab") as f:
        f.write(b'{"seq":2,"kind":"observation","ref":"o3","ts":7,"body":{"a":3},"prev":"')  # torn mid-row
    r = Segment(seg)
    assert r.torn is not None and r.torn.good_bytes == good and r.last_seq == 1
    ok, msg = r.verify()
    assert ok and "2 rows" in msg
    w = Segment(seg, writer=True, fsync=False)          # truncates the tail first
    assert w.torn is None and seg.stat().st_size == good
    w.append("observation", "o3", {"a": 3}, ts=8)
    w.close()
    ok, msg = Segment(seg).verify()
    assert ok and "3 rows" in msg


def test_a_flipped_byte_is_caught_at_its_seq(tmp_path):
    t = Tape(tmp_path, writer="plane", fsync=False)
    for i in range(5):
        t.append("cell", f"c{i}", {"i": i}, ts=10 + i)
    t.close()
    seg = tmp_path / "tape" / "segments" / "plane.seg"
    data = bytearray(seg.read_bytes())
    lines = data.split(b"\n")
    # corrupt the body of seq 2: change "i":2 to "i":9 (same length, so the JSON still parses)
    lines[2] = lines[2].replace(b'"i":2', b'"i":9')
    seg.write_bytes(b"\n".join(lines))
    ok, msg = Segment(seg).verify()
    assert not ok and "seq 2" in msg


def test_global_order_across_writers_is_by_ts_then_writer(tmp_path):
    a = Tape(tmp_path, writer="a", fsync=False); b = Tape(tmp_path, writer="b", fsync=False)
    a.append("tick", "t", {"n": 1}, ts=100)
    b.append("tick", "t", {"n": 2}, ts=50)
    a.append("tick", "t", {"n": 3}, ts=75)
    a.close(); b.close()
    order = [(w, r.body["n"]) for w, r in Tape(tmp_path).rows()]
    assert order == [("b", 2), ("a", 3), ("a", 1)]
    m = Tape(tmp_path).manifest()
    assert {s["segment"] for s in m["segments"]} == {"a.seg", "b.seg"}
