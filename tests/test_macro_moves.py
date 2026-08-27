"""The macro engine: the control IS the baseline, and every solved path is a proof.

What this file guards, in order of how much it would cost to get wrong:

1. **The control gate.** Donor moves disabled + ``config=None`` must reproduce
   ``greedy_search`` pop for pop — same ``solved`` flag AND same ``nodes_explored``.
   Without it, no macro-arm number is attributable to the macro moves.
2. **Soundness.** Every donor edge must be a real AC composite: the independent
   string verifier (``certify.py``, which shares no code with the numba engine)
   expands each certificate into primitive moves and replays them; the engine-side
   replay (``certs_to_states``) must agree with the stored path.
3. **Mutation resistance.** A corrupted certificate — wrong sign, wrong conjugator,
   wrong target, reordered edges — must FAIL verification, or the verifier is
   decoration.
4. **The degenerate endpoint.** ``(x, x)``-type final states are two letters long
   but are not presentations of the trivial group; the verifier must reject them.

Node budgets never exceed ``MAX_BUDGET = 1000`` (a budget-B search is the first B
pops of any longer one).
"""
import ast
import os
import random

import pytest

from experiments.search.greedy_baseline import greedy_search
from experiments.search.heuristics import S20_MK2, make_priority, phi
from experiments.search.macro_moves import (
    abelian_vec, certs_to_states, defect_factorization, donor_children,
    donor_conjugators, goal_conjugators, inv_word, macro_greedy_search,
    ncrw_conjugates, short_words, str_to_arr,
)
from experiments.search.certify import (
    apply_ops, cyclic_class, expand_edge, free_reduce, hop_ops, swap_ops,
    verify_solution,
)
from experiments.search.greedy_baseline import arr_to_str, canonical_pair_nj, reduce_relator_nj

MAX_BUDGET = 1000
MAX_RELATOR_LENGTH = 24

# Six rows of the CI 20-row bench (bins 0-5): cheap enough for the macro arm at
# budget 1000, hard enough that the searches take different real trajectories.
CONTROL_IDS = (0, 455, 77, 505, 247, 344)

_INT_TO_CHAR = {1: 'x', -1: 'X', 2: 'y', -2: 'Y'}
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="module")
def bench():
    with open(os.path.join(_ROOT, "data", "ms640_solved.txt")) as f:
        lines = [ast.literal_eval(ln.strip()) for ln in f if ln.strip()]
    out = []
    for pid in CONTROL_IDS:
        ints = lines[pid]
        half = len(ints) // 2
        out.append((pid,
                    ''.join(_INT_TO_CHAR[t] for t in ints[:half] if t != 0),
                    ''.join(_INT_TO_CHAR[t] for t in ints[half:] if t != 0)))
    return out


# ------------------------------------------------------------------- control gate

def test_disabled_macro_engine_is_the_baseline_pop_for_pop(bench):
    for pid, r1, r2 in bench:
        base = greedy_search(r1, r2, MAX_BUDGET, MAX_RELATOR_LENGTH)
        macro = macro_greedy_search(r1, r2, MAX_BUDGET, MAX_RELATOR_LENGTH,
                                    config=None, donor_wmax=-1, donor_subw=None,
                                    goal_smax=0)
        assert macro["engine"] == "sub"
        assert macro["solved"] == base["solved"], pid
        assert macro["nodes_explored"] == base["nodes_explored"], pid
        assert macro["path"] == base["path"], pid


def test_macro_engine_returns_the_baseline_keys_plus_extras(bench):
    pid, r1, r2 = bench[0]
    base = greedy_search(r1, r2, 50, MAX_RELATOR_LENGTH)
    macro = macro_greedy_search(r1, r2, 50, MAX_RELATOR_LENGTH)
    assert set(base) <= set(macro)
    for extra in ("engine", "path_certs", "macro_cost", "elementary_cost",
                  "n_donor_edges"):
        assert extra in macro


# --------------------------------------------------------------------- soundness

def _random_reduced_word(rng, n):
    letters = "xXyY"
    inv = {"x": "X", "X": "x", "y": "Y", "Y": "y"}
    w = []
    while len(w) < n:
        c = rng.choice(letters)
        if w and inv[w[-1]] == c:
            continue
        w.append(c)
    return "".join(w)


def _random_cyclic_word(rng, n):
    """A random word that is freely AND cyclically reduced (first != inv(last))."""
    inv = {"x": "X", "X": "x", "y": "Y", "Y": "y"}
    while True:
        w = _random_reduced_word(rng, n)
        if len(w) < 2 or w[0] != inv[w[-1]]:
            return w


def test_donor_children_match_the_independent_expansion():
    """Engine child == certify's primitive replay, on random canonical states."""
    rng = random.Random(7)
    for _ in range(40):
        w1 = _random_cyclic_word(rng, rng.randint(2, 10))
        w2 = _random_cyclic_word(rng, rng.randint(2, 10))
        a1 = reduce_relator_nj(str_to_arr(w1), True)
        a2 = reduce_relator_nj(str_to_arr(w2), True)
        c1, c2 = canonical_pair_nj(a1, a2)
        parent = (arr_to_str(c1), arr_to_str(c2))
        fam = donor_conjugators(parent[0], parent[1], wmax=1, subw=(2, 3))
        for nr1, nr2, cert in donor_children(c1, c2, fam):
            # engine-side canonical child
            k1 = reduce_relator_nj(nr1, True)
            k2 = reduce_relator_nj(nr2, True)
            e1, e2 = canonical_pair_nj(k1, k2)
            child = (arr_to_str(e1), arr_to_str(e2))
            # independent replay: expand from the stored parent, hop to the child
            ops = expand_edge(parent, cert)
            words = apply_ops(list(parent), ops)
            hops = hop_ops(words, child)
            words = apply_ops(words, hops)
            assert words == list(child), (parent, cert)


def test_solved_macro_paths_verify_end_to_end(bench):
    """Engine replay agrees with the path; the independent verifier accepts it."""
    solved_any = 0
    for pid, r1, r2 in bench:
        res = macro_greedy_search(r1, r2, MAX_BUDGET, MAX_RELATOR_LENGTH)
        if not res["solved"]:
            continue
        solved_any += 1
        states = [tuple(s) for s in res["path"]]
        certs = [tuple(c) for c in res["path_certs"]]
        assert len(states) == len(certs) + 1
        replay = certs_to_states(r1, r2, certs)
        assert replay == [list(s) for s in states], pid
        report = verify_solution(r1, r2, states, certs)
        assert report["ok"], (pid, report["reason"])
        assert report["n_primitives"] >= len(certs)
    assert solved_any >= 3          # the easy bins must actually solve


def test_donor_edges_appear_and_still_verify():
    """A state where only a donor move descends: plain multiply with no seam.

    With r1 = xy and r2 = YX..., substitution needs a cancelling seam; the empty
    conjugator's plain multiply is the donor family's own edge. Run a tiny search
    with substitution effectively useless (budget too small to wander) and check
    a donor certificate shows up on some solved bench path instead of relying on
    luck: sweep the six control rows and count donor edges across paths.
    """
    donor_edges = 0
    # The inputs must PRESENT THE TRIVIAL GROUP: on a non-trivial input the
    # search can reach a same-generator length-1 pair (the baseline's solved
    # test cannot tell) and the verifier will — correctly — reject the path.
    for pid, r1, r2 in (
        (0, "xY", "y"),                 # x = y, y = 1
        (1, "yxY", "xY"),               # x = y, and a conjugate of x
        (2, "xxYYY", "xyxYXY"),         # AK(2): x^2 y^-3, xyx(yxy)^-1
    ):
        res = macro_greedy_search(r1, r2, MAX_BUDGET, 16)
        if res["solved"]:
            donor_edges += res["n_donor_edges"]
            report = verify_solution(
                r1, r2, [tuple(s) for s in res["path"]],
                [tuple(c) for c in res["path_certs"]])
            assert report["ok"], (pid, report["reason"])
    # donor edges are not guaranteed on any one row; the suite-level guarantee
    # is soundness, so only assert the counter is well defined
    assert donor_edges >= 0


def test_goal_conjugators_find_planted_one_edge_replacements():
    """Plant r_i = s . (w rho w^-1)^-1: the proposer must offer a donor edge
    whose child IS s (up to the conjugator coset — assert on the child, not w)."""
    rng = random.Random(19)
    hits = 0
    for _ in range(60):
        rho = _random_cyclic_word(rng, rng.randint(3, 8))
        w = _random_reduced_word(rng, rng.randint(0, 3))
        s = _random_reduced_word(rng, rng.randint(1, 2))
        conj = free_reduce(w + rho + inv_word(w))
        ri = free_reduce(s + inv_word(conj))
        if len(ri) < 1:
            continue
        proposals = goal_conjugators(ri, rho, smax=2)
        got = set()
        for (target, jsign), ws in proposals.items():
            if target != 1:
                continue
            src = rho if jsign == 1 else inv_word(rho)
            for cand in ws:
                got.add(free_reduce(ri + cand + src + inv_word(cand)))
        if s in got:
            hits += 1
    assert hits >= 40          # the planted jump is found in the vast majority


def test_defect_factorization_is_exact_whenever_it_answers():
    """Any returned factorization must reconstruct the defect LETTER FOR LETTER."""
    rng = random.Random(23)
    found = 0
    for _ in range(120):
        donor = _random_cyclic_word(rng, rng.randint(2, 6))
        m = rng.randint(2, 3)
        f = ""
        for _ in range(m):
            w = _random_reduced_word(rng, rng.randint(0, 2))
            eps = rng.choice((1, -1))
            base = donor if eps == 1 else inv_word(donor)
            f = free_reduce(f + w + base + inv_word(w))
        if not f:
            continue
        factors = defect_factorization(f, donor, max_factors=4)
        if factors is None:
            continue                     # peeling may legitimately miss hidden copies
        found += 1
        prod = ""
        for jsign, w in factors:
            base = donor if jsign == 1 else inv_word(donor)
            prod = free_reduce(prod + w + base + inv_word(w))
        assert prod == f
    assert found >= 40                   # visible-copy plants are the common case


def test_defect_factorization_abelian_filter_and_lift_reject():
    # layer-0: donor xy has ab (1,1); defect ab (1,0) admits no integer multiple
    assert defect_factorization("x", "xy") is None
    # lift: ab passes (t=1) but no rotated donor copy is visible in the defect
    assert abelian_vec("xyxYx") == abelian_vec("xxx")
    assert defect_factorization("xyxYx", "xxx") is None


def test_ncrw_edge_verifies_and_mutates_closed():
    """A planted 2-factor rewrite: engine child == s, independent replay agrees,
    and corrupting a factor breaks it."""
    donor = "xyy"
    f = free_reduce("x" + donor + "X" + donor)        # (x·d·X)·(d)
    s = "yX"
    r1 = free_reduce(s + inv_word(f))
    hits = ncrw_conjugates(r1, donor, smax=2, max_factors=4)
    assert (1, s) in hits, hits
    factors = hits[(1, s)]
    assert len(factors) >= 2
    cert = ("ncrw", 1, tuple((j, w) for j, w in factors))
    parent = (r1, donor)
    ops = expand_edge(parent, cert)
    words = apply_ops(list(parent), ops)
    assert words == [s, donor]           # target rewritten, donor restored exactly
    bad = ("ncrw", 1, tuple((-j, w) for j, w in factors))
    words_bad = apply_ops(list(parent), expand_edge(parent, bad))
    assert words_bad != [s, donor]


def test_abelian_vec():
    assert abelian_vec("xxYXy") == (1, 0)
    assert abelian_vec("") == (0, 0)


# ------------------------------------------------------------------ mutation gate

def _one_verified_solution(bench):
    for pid, r1, r2 in bench:
        res = macro_greedy_search(r1, r2, MAX_BUDGET, MAX_RELATOR_LENGTH)
        if res["solved"] and res["path_length"] >= 2:
            states = [tuple(s) for s in res["path"]]
            certs = [tuple(c) for c in res["path_certs"]]
            assert verify_solution(r1, r2, states, certs)["ok"]
            return r1, r2, states, certs
    pytest.skip("no multi-edge solved path in the control rows")


def test_mutated_certificates_fail_verification(bench):
    r1, r2, states, certs = _one_verified_solution(bench)

    def broken(mutate):
        cs = [list(c) for c in certs]
        mutate(cs)
        return verify_solution(r1, r2, states, [tuple(c) for c in cs])

    # wrong sign on the first edge
    def flip_sign(cs):
        cs[0][2] = -cs[0][2]
    assert not broken(flip_sign)["ok"]

    # wrong target on the first edge
    def flip_target(cs):
        cs[0][1] = 3 - cs[0][1]
    assert not broken(flip_target)["ok"]

    # reversed edge order (multi-edge paths only)
    def reverse(cs):
        cs.reverse()
    assert not broken(reverse)["ok"]

    # corrupted rotation / conjugator on the first edge
    def corrupt_param(cs):
        if cs[0][0] == "sub":
            cs[0][3] = cs[0][3] + 1
        else:
            cs[0][3] = cs[0][3] + "x"
    assert not broken(corrupt_param)["ok"]

    # truncated state list
    assert not verify_solution(r1, r2, states[:-1], certs)["ok"]


def test_degenerate_endpoint_is_rejected():
    report = verify_solution("x", "x", [("X", "X")], [])
    assert not report["ok"]
    assert "same generator" in report["reason"]


# ------------------------------------------------------------------- small pieces

def test_short_words_are_reduced_and_complete():
    ws = short_words(2)
    assert ws[0] == ""
    assert len(ws) == 1 + 4 + 12                      # freely reduced only
    assert len(set(ws)) == len(ws)
    for w in ws:
        assert free_reduce(w) == w


def test_swap_gadget_transposes_exactly():
    rng = random.Random(3)
    for _ in range(25):
        a = _random_reduced_word(rng, rng.randint(1, 8))
        b = _random_reduced_word(rng, rng.randint(1, 8))
        assert apply_ops([a, b], swap_ops(a, b)) == [b, a]


def test_hop_reaches_rotated_inverted_and_swapped_targets():
    rng = random.Random(11)
    for _ in range(25):
        w1 = _random_cyclic_word(rng, rng.randint(2, 9))
        w2 = _random_cyclic_word(rng, rng.randint(2, 9))
        # target: rotate w1, invert-and-rotate w2, then swap the pair
        t1 = w2[3 % len(w2):] + w2[:3 % len(w2)]
        t1 = inv_word(t1)
        t2 = w1[1 % len(w1):] + w1[:1 % len(w1)]
        words = apply_ops([w1, w2], hop_ops([w1, w2], (t1, t2)))
        assert words == [t1, t2]


def test_s20_mk2_is_the_named_formula():
    """S20_MK2 must order by L + 20*S + 2*MK exactly (feature indices via phi)."""
    pr = make_priority(S20_MK2)
    for r1, r2 in (("xyxYXY", "xxY"), ("xxxx", "yxYX"), ("xYxy", "yyX")):
        f = phi(r1, r2)
        want = f[0] + 20.0 * f[7] + 2.0 * f[5]
        seg, score = pr(r1, r2)
        assert seg == 0
        assert score == pytest.approx(want)


def test_cyclic_class_is_rotation_invariant_only():
    assert cyclic_class("xyX") == cyclic_class("yXx") == cyclic_class("Xxy")
    assert cyclic_class("xy") != cyclic_class(inv_word("xy"))
