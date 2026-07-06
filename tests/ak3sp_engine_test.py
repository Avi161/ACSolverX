"""Own test suite for the ak3_stable_proof engine (author's suite — the independent
adversarial suite lives in tests/ak3sp_independent_test.py, written black-box by a
separate agent from the spec only).

Run: .venv/bin/python3 -m pytest tests/ak3sp_engine_test.py -q
"""
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
ENGINE = os.path.join(ROOT, "experiments", "stable_ac", "ak3_stable_proof")
ONEGEN = os.path.join(ROOT, "experiments", "stable_ac", "one_generator")
for p in (ENGINE, ONEGEN):
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np  # noqa: E402

import presentation as P  # noqa: E402
import stable_moves as SM  # noqa: E402
import stabilize as STAB  # noqa: E402  (existing module: cross-implementation oracle)
import greedy_nrel as gn  # noqa: E402
from certificate import make_certificate  # noqa: E402
from hmoves import AK3, APPENDIX_F_SEQ, P25, replay  # noqa: E402
from verify_certificate import verify  # noqa: E402
from wirtinger import (  # noqa: E402
    Cascade, W_CORRECTED, W_MISPRINT, eliminate_final_via_w, paper_family,
)

rng = random.Random(20260705)


def rand_word(n, n_gen=2):
    w = []
    while len(w) < n:
        c = rng.choice([g * s for g in range(1, n_gen + 1) for s in (1, -1)])
        if w and w[-1] == -c:
            continue
        w.append(c)
    return w


# --------------------------------------------------------------- presentation.py

def test_word_ops_match_stabilize_module():
    for _ in range(300):
        w = [rng.choice([1, -1, 2, -2, 3, -3]) for _ in range(rng.randrange(0, 14))]
        assert P.free_reduce(w) == STAB.free_reduce(w)
        assert P.cyclic_reduce(w) == STAB.cyclic_reduce(w)
        assert P.inverse_word(w) == STAB.inverse(w)


def test_canonical_word_invariance():
    for _ in range(200):
        w = P.cyclic_reduce(rand_word(rng.randrange(1, 12)))
        if not w:
            continue
        c = P.canonical_word(w)
        for k in range(len(w)):
            assert P.canonical_word(w[k:] + w[:k]) == c
        assert P.canonical_word(P.inverse_word(w)) == c


def test_canonical_word_matches_greedy_nrel():
    """Cross-implementation: our brute canonical == gn's Booth canonical (n_gen<=3)."""
    for _ in range(300):
        w = P.cyclic_reduce(rand_word(rng.randrange(1, 14), n_gen=3))
        if not w:
            continue
        ours = P.canonical_word(w)
        theirs = list(gn.canonical_relator(np.array(w, dtype=gn.INT_DTYPE)))
        assert ours == [int(x) for x in theirs], (w, ours, theirs)


def test_relabel_canonical_collapses_variants():
    state = (rand_word(7), rand_word(5))
    key = P.relabel_canonical_key(state, 2)
    for s in P.relabel_variants(state, 2):
        assert P.relabel_canonical_key(s, 2) == key


def test_abelianization_det_bareiss_vs_sympy():
    import sympy
    for _ in range(50):
        n = rng.randrange(1, 6)
        m = [[rng.randrange(-5, 6) for _ in range(n)] for _ in range(n)]
        assert P.det_bareiss(m) == int(sympy.Matrix(m).det())


# --------------------------------------------------------------- stable_moves.py

def test_stabilize_eliminate_round_trip():
    for _ in range(100):
        state = tuple(P.cyclic_reduce(rand_word(rng.randrange(2, 12))) for _ in range(2))
        if any(not r for r in state):
            continue
        w = P.free_reduce(rand_word(rng.randrange(0, 8)))
        s1, ng1, _ = SM.stabilize(state, 2, w)
        assert ng1 == 3 and len(s1) == 3
        # z occurs exactly once in the new relator -> eliminate it right back
        s2, ng2, _ = SM.eliminate(s1, 3, 3, 2)
        assert ng2 == 2
        assert P.relabel_canonical_key(s2, 2) == P.relabel_canonical_key(state, 2)


def test_moves_preserve_abelianization_det():
    for _ in range(100):
        state = tuple(P.cyclic_reduce(rand_word(rng.randrange(2, 10))) for _ in range(2))
        if any(not r for r in state):
            continue
        d0 = abs(P.abelianization_det(state, 2))
        w = P.free_reduce(rand_word(rng.randrange(0, 6)))
        s1, ng1, _ = SM.stabilize(state, 2, w)
        assert abs(P.abelianization_det(s1, ng1)) == d0
        s2, _ = SM.concat_move(state, 0, 1, rng.choice((1, -1)))
        assert abs(P.abelianization_det(s2, 2)) == d0
        s3, _ = SM.conjugation_move(state, rng.randrange(2), rng.choice((1, -1, 2, -2)))
        assert abs(P.abelianization_det(s3, 2)) == d0
        s4, _ = SM.invert_move(state, rng.randrange(2))
        assert abs(P.abelianization_det(s4, 2)) == d0


def test_find_eliminable_matches_brute():
    for _ in range(100):
        n_gen = rng.randrange(2, 5)
        state = tuple(P.cyclic_reduce(rand_word(rng.randrange(1, 10), n_gen))
                      for _ in range(n_gen))
        got = set(SM.find_eliminable(state, n_gen))
        want = {(g, ri) for ri, r in enumerate(state) for g in range(1, n_gen + 1)
                if sum(1 for a in r if abs(a) == g) == 1}
        assert got == want


def test_eliminate_precondition_raises():
    state = ([1, 2, 1, -2], [2, 2, 1])   # gen 1 occurs twice in r0
    try:
        SM.eliminate(state, 2, 1, 0)
        assert False, "should have raised"
    except ValueError:
        pass


def test_triviality_preserved_stabilize_eliminate_detour():
    """Cross-source: a known greedy-solvable presentation stays solvable after a
    stabilize+eliminate detour (idx 0 of 1190MS, solved by the baseline in <100k)."""
    import ast
    flat = ast.literal_eval(open(os.path.join(ROOT, "data", "1190MS.txt")).readline())
    rels = [list(r) for r in gn.flat_to_relators(flat, 2)]
    s1, ng1, _ = SM.stabilize(tuple(rels), 2, [1, 2, -1])
    s2, ng2, _ = SM.eliminate(s1, ng1, 3, 2)
    relators = [np.array(r, dtype=gn.INT_DTYPE) for r in s2]
    solver = gn.NRelatorSolver(relators, 2, max_nodes=100_000)
    path, nodes, _ = solver.solve()
    assert path is not None and gn.verify_path(path["states"], 2)


# --------------------------------------------------------------------- hmoves.py

def test_appendix_f_gate_exact():
    states, _ = replay(P25, APPENDIX_F_SEQ)
    assert [list(r) for r in states[-1]] == [list(r) for r in AK3]
    for s in states:
        assert abs(P.abelianization_det(list(s), 2)) == 1


def test_conjugation_changes_the_free_word():
    # y . xy . y^-1 free-reduces to yx — changed as a free word (a rotation), NOT
    # cyclically re-reduced back to the input (which would make AC'2 a no-op).
    s, _ = SM.conjugation_move(([1, 2], [2, 1, 2]), 0, 2)
    assert s[0] == [2, 1]
    s2, _ = SM.conjugation_move(([1, 2], [2, 1, 2]), 0, 1)
    assert s2[0] == [1, 1, 2, -1]


# ------------------------------------------------------------------ wirtinger.py

def test_w_relators_are_wirtinger_shaped():
    for W in (W_CORRECTED, W_MISPRINT):
        for i, r in enumerate(W, start=1):
            assert len(r) == 4 and r[0] == -i
            assert r[1] == -r[3] and abs(r[2]) != i


def test_paper_family_reproduces_printed_relators():
    c = paper_family()
    rels = sorted(c._state(), key=len)
    assert [len(r) for r in rels] == [3, 26, 34]
    assert P.canonical_word(rels[0]) == P.canonical_word([-1, 2, 3])


def test_cascade_certificate_verifies_and_tamper_rejected():
    c = paper_family()
    assert eliminate_final_via_w(c)
    cert = c.certificate("test_cascade")
    ok, errs = verify(cert)
    assert ok, errs[:3]
    import copy
    bad = copy.deepcopy(cert)
    bad["states"][5]["relators"][0][0] *= -1
    ok2, _ = verify(bad)
    assert not ok2


def test_misprint_cascade_differs_from_corrected():
    ca = paper_family(relators=W_CORRECTED)
    cb = paper_family(relators=W_MISPRINT)
    ka = P.canonical_state_key(ca._state())
    kb = P.canonical_state_key(cb._state())
    assert ka != kb


# ------------------------------------------------------------- verify_certificate

def test_verifier_rejects_bad_step_params():
    state = ([1, 2], [2, 1, 2])
    s1, st1 = SM.concat_move(state, 0, 1, 1)
    cert = make_certificate("t", "t", [(state, 2), (s1, 2)], [st1])
    ok, _ = verify(cert)
    assert ok
    import copy
    bad = copy.deepcopy(cert)
    bad["steps"][0]["sign"] = -1
    ok2, _ = verify(bad)
    assert not ok2
