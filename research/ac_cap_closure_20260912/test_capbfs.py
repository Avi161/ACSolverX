"""Tests for the cap-bounded AC closure BFS.

    pytest research/ac_cap_closure_20260912/test_capbfs.py -v -s

(a) fast engine == pure-Python reference, as state sets, on 30 random
    AC-trivial presentations at caps 6..10;
(b) a CLOSED component really is closed: every reference-generated neighbour of
    every member is a member; and (b2) the bounded-connector move set coincides
    with brute-force AC2 over all conjugators up to length 4;
(c) component(cap c) is a subset of component(cap c + 1);
(d) three short AC19 rows: find the minimal cap that solves and verify the
    certificate with ``verify_path``;
(e) AK(3) is not solved at caps 7..11 and the components there are closed;
(f) BFS from (r1, r2) and from (r2, r1) give the same state set;
(g) the packing boundary: caps above 16 are refused, and at cap 16 with two
    length-16 relators (a 32-letter unreduced product, the most the int64
    accumulator holds) the kernel's first layer equals the reference neighbour
    set; ``verify_path`` refuses an input with nothing to verify.
"""

from __future__ import annotations

import csv
import os
import random
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import capbfs                                    # noqa: E402
import capbfs_reference as ref                   # noqa: E402
import verify_path                               # noqa: E402

AK3 = ("xxxYYYY", "xyxYXY")
AC19_CSV = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "AC19_extended_aut_min.csv")

#: AK(3) component sizes at caps 7..11 -- also quoted in README.md
AK3_SIZES = {7: 1, 8: 1, 9: 814, 10: 4188, 11: 21388}


def random_trivial_presentations(n, seed=12345, max_len=8, max_moves=6):
    """``n`` distinct AC-trivial presentations built by random moves from (x, y)."""
    rng = random.Random(seed)
    out, seen = [], set()
    while len(out) < n:
        st = ref.TRIVIAL
        for _ in range(rng.randint(1, max_moves)):
            nb = [c for _, c in ref.neighbours(st, max_len)
                  if len(c[0]) <= max_len and len(c[1]) <= max_len]
            st = rng.choice(nb)
        key = (ref.word_to_str(st[0]), ref.word_to_str(st[1]))
        if st == ref.TRIVIAL or key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


PANEL = random_trivial_presentations(30)


# --------------------------------------------------------------------------
# (a) fast engine agrees with the reference, exactly
# --------------------------------------------------------------------------
@pytest.mark.parametrize("r1,r2", PANEL, ids=["%s|%s" % p for p in PANEL])
def test_a_fast_matches_reference(r1, r2):
    checked = 0
    for cap in range(6, 11):
        if max(len(r1), len(r2)) > cap:
            continue
        fast = capbfs.bfs(r1, r2, cap, 1_000_000, True, collect_states=True)
        slow = ref.bfs(r1, r2, cap, 1_000_000, True)
        assert capbfs.state_key_strings(fast) == ref.state_key_strings(slow), (
            "state sets differ for %s/%s at cap %d" % (r1, r2, cap))
        assert fast["states"] == slow["states"]
        assert fast["solved"] == slow["solved"]
        assert fast["closed"] == slow["closed"]
        assert fast["min_total_length_seen"] == slow["min_total_length_seen"]
        checked += 1
    assert checked > 0


def test_a_panel_is_ac_trivial():
    """The panel really is AC-trivial: every member solves at some cap <= 12."""
    for r1, r2 in PANEL:
        cap = max(len(r1), len(r2))
        while cap <= 12:
            if capbfs.bfs(r1, r2, cap, 500_000, True)["solved"]:
                break
            cap += 1
        else:
            pytest.fail("panel member %s/%s never solved up to cap 12" % (r1, r2))


# --------------------------------------------------------------------------
# (b) CLOSED means closed under the reference move generator
# --------------------------------------------------------------------------
@pytest.mark.parametrize("r1,r2,cap", [
    ("xyXY", "x", 7),
    ("xxY", "xy", 7),
    ("xy", "Xy", 6),
    (AK3[0], AK3[1], 9),
])
def test_b_component_is_closed(r1, r2, cap):
    res = capbfs.bfs(r1, r2, cap, 1_000_000, stop_when_solved=False,
                     collect_states=True)
    assert res["closed"], "expected a closed component for %s/%s cap %d" % (r1, r2, cap)
    assert not res["budget_exhausted"]
    states = [tuple(ref.str_to_word(w) for w in key.split(","))
              for key in capbfs.state_key_strings(res)]
    member = set(states)
    assert len(member) == res["states"]
    for st in states:
        assert st[0] and st[1], "empty relator in a discovered state"
        assert max(len(st[0]), len(st[1])) <= cap
        for child in ref.neighbour_set(st, cap):
            assert child in member, (
                "state %s escapes the component via %s"
                % (ref.pair_to_strs(st), ref.pair_to_strs(child)))


# --------------------------------------------------------------------------
# (b2) the restricted move set IS the full AC2 move set
# --------------------------------------------------------------------------
def _brute_neighbours(state, cap, max_u):
    """AC2 by brute force: all rotations of +-r_i, +-r_j and ALL conjugators."""
    out = set()
    conns = ref.connectors(max_u)
    for i in (0, 1):
        ri, rj = state[i], state[1 - i]
        for si in (1, -1):
            wi = ri if si == 1 else ref.inv_word(ri)
            for a in range(len(wi)):
                A = ref.rot(wi, a)
                for e in (1, -1):
                    oj = rj if e == 1 else ref.inv_word(rj)
                    for p in range(len(oj)):
                        P = ref.rot(oj, p)
                        for u in conns:
                            R = ref.cyc_reduce(A + u + P + ref.inv_word(u))
                            if 1 <= len(R) <= cap:
                                out.add(ref.canon_pair(R, rj))
    return out


@pytest.mark.parametrize("r1,r2,cap", [
    (AK3[0], AK3[1], 12),
    (AK3[0], AK3[1], 14),
    ("xy", "Xy", 10),
    ("x", "y", 9),
    ("xxy", "xyxyxY", 12),
    ("YXXyx", "YYXyX", 11),
])
def test_b2_move_set_is_the_full_ac2_move_set(r1, r2, cap):
    """The bounded connector rule loses nothing and invents nothing.

    Every AC2 move ``r_i -> r_i * (u r_j**e u**-1)`` with an ARBITRARY conjugator
    ``u`` (here: all ``|u| <= 4``), applied to any rotation of ``r_i`` or
    ``r_i**-1``, lands inside the model's neighbourhood -- and the model
    produces nothing that such a move cannot.
    """
    state = ref.canon_pair(ref.str_to_word(r1), ref.str_to_word(r2))
    model = ref.neighbour_set(state, cap)
    for max_u in range(0, 5):
        assert _brute_neighbours(state, cap, max_u) <= model
    assert model == _brute_neighbours(state, cap, 4)


# --------------------------------------------------------------------------
# (c) monotonicity in the cap
# --------------------------------------------------------------------------
@pytest.mark.parametrize("r1,r2,caps", [
    (AK3[0], AK3[1], (9, 10, 11)),
    ("xyXY", "x", (5, 6, 7)),
    ("xxY", "xy", (5, 6, 7)),
])
def test_c_monotone_in_cap(r1, r2, caps):
    sets = {}
    for cap in caps:
        res = capbfs.bfs(r1, r2, cap, 2_000_000, stop_when_solved=False,
                         collect_states=True)
        assert res["closed"], "cap %d component not exhausted" % cap
        sets[cap] = set(capbfs.state_key_strings(res))
    for lo, hi in zip(caps, caps[1:]):
        assert sets[lo] <= sets[hi], (
            "component(cap %d) is not contained in component(cap %d)" % (lo, hi))


# --------------------------------------------------------------------------
# (d) solved detection + certificate
# --------------------------------------------------------------------------
def _ac19_rows(n):
    rows = []
    with open(AC19_CSV, newline="") as fh:
        for row in csv.DictReader(fh):
            rows.append((row["name"], row["r1"], row["r2"]))
            if len(rows) >= n:
                break
    return rows


def test_d_minimal_solving_cap_and_certificate(capsys):
    rows = _ac19_rows(3)
    assert len(rows) == 3
    for name, r1, r2 in rows:
        floor_cap = max(len(r1), len(r2))
        solved = None
        for cap in range(floor_cap, floor_cap + 8):
            res = capbfs.bfs(r1, r2, cap, 1_000_000, True)
            if res["solved"]:
                solved = (cap, res)
                break
            assert res["closed"] or res["budget_exhausted"]
        assert solved is not None, "%s never solved" % name
        cap, res = solved
        # minimality: no smaller admissible cap solves it
        for smaller in range(floor_cap, cap):
            assert not capbfs.bfs(r1, r2, smaller, 1_000_000, True)["solved"]
        report = verify_path.verify_result(capbfs.json_ready(res))
        assert report["ok"]
        assert report["max_relator_length"] <= cap
        # the reference finds a path at the same cap, and it verifies too
        sref = ref.bfs(r1, r2, cap, 1_000_000, True)
        assert sref["solved"]
        rep2 = verify_path.verify_result(
            {k: v for k, v in sref.items() if not k.startswith("_")})
        assert rep2["ok"]
        with capsys.disabled():
            print("\n  (d) %-8s %s,%s  minimal cap %d  steps %d (ref %d)"
                  % (name, r1, r2, cap, report["steps"], rep2["steps"]))


def test_d_tampered_certificate_is_rejected():
    res = capbfs.json_ready(capbfs.bfs("YXXyx", "YYXyX", 5, 1_000_000, True))
    assert res["solved"]
    assert verify_path.verify_result(res)["ok"]
    bad = dict(res, path=[dict(res["path"][0], a=(res["path"][0]["a"] + 1))]
               + list(res["path"][1:]))
    with pytest.raises(verify_path.VerificationError):
        verify_path.verify_result(bad)


# --------------------------------------------------------------------------
# (e) AK(3)
# --------------------------------------------------------------------------
def test_e_ak3_closed_and_unsolved(capsys):
    sizes = {}
    for cap in range(7, 12):
        res = capbfs.bfs(AK3[0], AK3[1], cap, 5_000_000, stop_when_solved=True)
        assert not res["solved"], "AK(3) reported solved at cap %d" % cap
        assert res["closed"], "AK(3) component not exhausted at cap %d" % cap
        assert not res["budget_exhausted"]
        assert res["frontier_size_at_stop"] == 0
        assert res["min_total_length_seen"] == 13
        sizes[cap] = res["states"]
    with capsys.disabled():
        print("\n  (e) AK(3) component sizes: "
              + ", ".join("cap %d: %d" % (c, sizes[c]) for c in sorted(sizes)))
    assert sizes == AK3_SIZES


def test_e_ak3_matches_reference_at_cap_9():
    fast = capbfs.bfs(AK3[0], AK3[1], 9, 1_000_000, True, collect_states=True)
    slow = ref.bfs(AK3[0], AK3[1], 9, 1_000_000, True)
    assert capbfs.state_key_strings(fast) == ref.state_key_strings(slow)


# --------------------------------------------------------------------------
# (f) the state is an unordered pair
# --------------------------------------------------------------------------
@pytest.mark.parametrize("r1,r2,cap", [
    (AK3[0], AK3[1], 10),
    ("xyXY", "x", 7),
    ("YXXyx", "YYXyX", 6),
] + [(p[0], p[1], 8) for p in PANEL[:5]])
def test_f_unordered_pair(r1, r2, cap):
    a = capbfs.bfs(r1, r2, cap, 1_000_000, stop_when_solved=False,
                   collect_states=True)
    b = capbfs.bfs(r2, r1, cap, 1_000_000, stop_when_solved=False,
                   collect_states=True)
    assert a["initial"] == b["initial"]
    assert capbfs.state_key_strings(a) == capbfs.state_key_strings(b)
    assert a["states"] == b["states"]
    assert a["closed"] == b["closed"] and a["solved"] == b["solved"]


# --------------------------------------------------------------------------
# throughput (reported, not asserted tightly)
# --------------------------------------------------------------------------
def test_throughput_ak3_cap14(capsys):
    capbfs.bfs("xy", "Xy", 8, 1000, True)          # warm the JIT
    res = capbfs.bfs(AK3[0], AK3[1], 14, 1_000_000, stop_when_solved=True)
    with capsys.disabled():
        print("\n  AK(3) cap 14: %d states, closed=%s, %.2f s, %.0f popped nodes/s"
              % (res["states"], res["closed"], res["seconds"],
                 res["nodes_per_second"]))
    assert res["nodes_per_second"] >= 20_000


# --------------------------------------------------------------------------
# (g) the packing boundary
# --------------------------------------------------------------------------
def test_g_cap_above_16_is_refused():
    """The int64 accumulator is exact for <= 32 letters, i.e. cap <= 16."""
    assert capbfs.MAX_CAP == 16
    for cap in (17, 24, 31):
        with pytest.raises(ValueError):
            capbfs.bfs(AK3[0], AK3[1], cap, 1000, True)
    with pytest.raises(ValueError):
        capbfs.bfs("x", "y", 32, 1000, True)
    assert capbfs.bfs("x", "y", 16, 1000, True)["solved"]


def _is_cyclically_reduced(s):
    return ref.word_to_str(ref.cyc_reduce(ref.str_to_word(s))) == s


def _boundary_state(rng):
    """Two cyclically reduced length-16 relators sharing a prefix of length
    16 - k (k in 4..8), so that rot(r1) . rot(r2^-1) cancels the shared prefix
    and leaves a legal child of length 2k <= 16: the first layer is nonempty
    and every move concatenates exactly 32 letters before reduction."""
    while True:
        r1 = "".join(rng.choice("xXyY") for _ in range(16))
        if not _is_cyclically_reduced(r1):
            continue
        k = rng.randint(4, 8)
        r2 = r1[:16 - k] + "".join(rng.choice("xXyY") for _ in range(k))
        if r2 != r1 and _is_cyclically_reduced(r2):
            return r1, r2


@pytest.mark.parametrize("seed", range(8))
def test_g_first_layer_is_exact_at_the_32_letter_boundary(seed):
    """Two length-16 relators at cap 16: every move concatenates 32 letters
    before cyclic reduction, the most the packed accumulator can hold.  The
    children of the root recorded by the kernel (parent index 0) must equal
    the reference neighbour set, minus the root itself (BFS never re-inserts
    a known state)."""
    r1, r2 = _boundary_state(random.Random(1000 + seed))
    assert len(r1) == len(r2) == 16
    root = ref.canon_pair(ref.str_to_word(r1), ref.str_to_word(r2))
    expected = {tuple(ref.pair_to_strs(c)) for c in ref.neighbour_set(root, 16)}
    expected.discard(tuple(ref.pair_to_strs(root)))
    assert expected, "construction failed to give the root any children"
    res = capbfs.bfs(r1, r2, 16, 20_000, stop_when_solved=False,
                     collect_states=True)
    kids = {res["_states"][t] for t in range(1, res["states"])
            if res["_parents"][t] == 0}
    assert kids == expected


def test_g_verify_path_refuses_an_input_with_nothing_to_verify(tmp_path):
    unsolved = capbfs.json_ready(capbfs.bfs(AK3[0], AK3[1], 9, 100_000, True))
    assert not unsolved["solved"]
    solved = capbfs.json_ready(capbfs.bfs("YXXyx", "YYXyX", 5, 100_000, True))
    assert solved["solved"]
    import json
    empty = tmp_path / "unsolved.jsonl"
    empty.write_text(json.dumps(unsolved) + "\n")
    full = tmp_path / "solved.json"
    full.write_text(json.dumps(solved) + "\n")
    # an edited batch with every row marked unsolved is not a pass
    assert verify_path.main([str(empty)]) == 3
    assert verify_path.main(["--allow-empty", str(empty)]) == 0
    assert verify_path.main([str(full)]) == 0
    assert verify_path.main([str(full), str(empty)]) == 0
    assert verify_path.main([]) == 2
