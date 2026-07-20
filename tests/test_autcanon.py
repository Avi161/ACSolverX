"""Cross-checks for the shared Aut(F2) orbit tool. Run: ``python3 -m ...tests.test_autcanon``.

``aut_canon`` (witness-carrying) and ``experiments/analysis/whitehead.py`` (independent, no
witness) use different letter orders, so they never share a representative *string* -- they are
cross-checked on the orbit PARTITION they induce, which is order-invariant.
"""
from experiments.analysis import whitehead as wh
from experiments.equivalence_classes.lib.autcanon import AUTOS, aut_canon, check, is_automorphism
from experiments.equivalence_classes.lib.words import apply_hom, cyc_reduce

BASES = [("YYYYXyyyx", "YYXYxYx"), ("YXYxyx", "YYYYxxx"), ("xyXY", "xYxy"), ("XXyxy", "Xyy")]


def _walk(pair, seed, steps=12):
    r1, r2, s = pair[0], pair[1], seed
    for _ in range(steps):
        s = (s * 1103515245 + 12345) & 0x7FFFFFFF
        r1, r2 = cyc_reduce(apply_hom(r1, AUTOS[s % len(AUTOS)])), cyc_reduce(apply_hom(r2, AUTOS[s % len(AUTOS)]))
        if not r1 or not r2:
            return pair
    return (r1, r2)


def _partition(reps):
    idx = {}
    return [idx.setdefault(r, len(idx)) for r in reps]


def test_pr_example():
    (_, rP, phi), (_, r2, _), (_, r3, _) = aut_canon(BASES[0]), aut_canon(("XXXXXXYxxxyxx", "YXXYxyxx")), aut_canon(BASES[1])
    assert rP == r2 and rP != r3 and check(BASES[0], rP, phi)


def test_same_partition_invariance_and_certificate():
    pool = [w for b in BASES for w in ([b] + [_walk(b, s) for s in range(1, 13)])]
    mine = [aut_canon(p) for p in pool]
    assert _partition([m[1] for m in mine]) == _partition([wh.canonical_form(p)[0] for p in pool])
    for p, (_, rep, phi) in zip(pool, mine):
        assert check(p, rep, phi)                              # certificate holds
    for b in BASES:                                            # rep is orbit-invariant
        assert len({aut_canon(_walk(b, s))[1] for s in range(1, 13)}) == 1


def test_level_cap_raises():
    try:
        aut_canon(BASES[0], level_cap=1)
        assert False, "expected RuntimeError on tiny level_cap"
    except RuntimeError:
        pass


def test_is_automorphism():
    assert not is_automorphism({"x": "x", "y": "x"})           # det 0, was a false positive
    assert is_automorphism({"x": "xy", "y": "y"})              # genuine Whitehead auto


if __name__ == "__main__":
    for _n, _f in sorted(globals().items()):
        if _n.startswith("test_") and callable(_f):
            _f()
            print("ok", _n)
    print("all passed")
