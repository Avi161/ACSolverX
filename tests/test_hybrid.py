"""The hybrid solver (``acx.hybrid``): the source's numbers, backend parity, replayable certificates.

Reference numbers are the source's own runs (``origin/claude/vigilant-babbage-nnbuj0:
research/ac_hashfree_cascade_20260914/records/``, budget 1,000, penalty 5, dyn_ratio 0.5):
MS640 640/640 with 25,064 units (stage B 98, C 328, H 214 rows), and the AC19 Aut-minimal
census 72,779/72,779 with 2,489,726 units, 188 certificates using higher rank. The full census
(about 190 s on 4 workers, certification included) is not run here; its first 2,000 rows are.
"""
import time

import pytest

from acx import data
from acx.aut.whitehead import AUTOS
from acx.core.words import Presentation, parse
from acx.hybrid import HybridConfig, certify, decode_steps, encode_steps, solve
from acx.hybrid.cascade import NIELSEN
from acx.hybrid.frontier import backend, pack
from acx.verify import is_valid, replay

FAST = HybridConfig(certify=False)


def test_nielsen_indices():
    assert [AUTOS[k] for k in NIELSEN] == [tuple(map(parse, p)) for p in (("xy", "y"), ("xY", "y"),
                                                                          ("x", "yx"), ("x", "yX"))]


def test_frontier_backends_agree(ms640):
    (sx, st), (fx, ft) = backend("spec"), backend("fast")
    for pres in ms640[::16]:
        key = pack(pres.reduced().canonical().rels)
        for cap in (None, len(key) - 1, 6, 3):
            assert sx(key, cap) == fx(key, cap)
        for k in range(len(AUTOS)):
            assert st(key, k) == ft(key, k)


def test_ms640(ms640):
    solve(ms640[176], FAST)                                  # compile the kernels
    t = time.perf_counter()
    res = [solve(p, FAST) for p in ms640]
    seconds = time.perf_counter() - t
    print(f"MS640 hybrid: {sum(r.solved for r in res)}/640 in {seconds:.2f} s (source: 2.22-2.4 s)")
    assert all(r.solved and r.kind == "ac_path" for r in res)
    assert sum(r.units for r in res) == 25_064 and max(r.units for r in res) == 283
    assert [sum(r.stage == s for r in res) for s in "BCH"] == [98, 328, 214]
    paths = [certify(p, r.steps) for p, r in zip(ms640, res)]  # each replayed by acx.verify inside
    assert all(is_valid(p, path, normalize=False) for p, path in list(zip(ms640, paths))[::10])


def test_spec_backend_matches_fast(ms640):
    rows = [p for p in ms640 if solve(p, FAST).stage == "H"][::9]
    ac19 = {r.id: r.pres for r in data.load_csv("data/AC19_extended_aut_min.csv")[:1300]}
    rows += [ac19[i] for i in ("ac19_239", "ac19_714", "ac19_1286")]      # higher rank used
    assert len(rows) >= 25
    for p in rows:
        a, b = solve(p, FAST), solve(p, FAST, backend="spec")
        assert (a.units, a.steps) == (b.units, b.steps)


def test_rank_two_cap_is_counted_and_backends_agree(ms640):
    rows = [p for p in ms640 if solve(p, FAST).stage == "H"][::70]
    for cap, budget in ((6, 1000), (14, 1000), (None, 60)):
        for p in rows:
            a, b = (solve(p, FAST, r2_cap=cap, budget=budget, backend=be) for be in ("fast", "spec"))
            assert (a.solved, a.units, a.steps, a.stats["cap_rejected"]) == (b.solved, b.units, b.steps, b.stats["cap_rejected"])
        assert (sum(solve(p, FAST, r2_cap=cap, budget=budget).stats["cap_rejected"] for p in rows) > 0) == (cap is not None)
    with pytest.raises(ValueError):
        HybridConfig(r2_cap="24")


def test_ac19_aut_min_sample():
    rows = data.load_csv("data/AC19_extended_aut_min.csv")[:2000]
    res = [solve(r.pres) for r in rows]                      # certify=True: every path replayed
    assert all(r.solved and r.path is not None for r in res)
    assert sum(r.units for r in res) == 67_889
    assert [sum(r.stage == s for r in res) for s in ("terminal", "B", "C", "H")] == [1, 185, 581, 1233]
    stable = [(row, r) for row, r in zip(rows, res) if r.kind == "stable_cert"]
    assert len(stable) == 3
    row, r = stable[0]
    ops = [m["op"] for m in r.path]
    assert "stabilize" in ops and ops.count("stabilize") == ops.count("destabilize")
    assert replay(row.pres, r.path, normalize=False)[-1] == Presentation(2, ((1,), (2,)))
    assert certify(row.pres, decode_steps(encode_steps(r.steps))) == list(r.path)


def test_tampered_certificate_fails(ms640):
    p = ms640[300]
    steps = solve(p, FAST).steps
    with pytest.raises((ValueError, AssertionError)):
        certify(p, steps[:-1])
    with pytest.raises((ValueError, AssertionError)):
        certify(p, steps[1:])


def test_budget_is_respected(ms640):
    res = solve(ms640[636], FAST, budget=30)
    assert not res.solved and res.units <= 30 and res.path is None
