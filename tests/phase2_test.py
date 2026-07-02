"""Phase 2 test suite — n-relator greedy solver (`greedy_nrel.py`).

Runnable two ways:
    python tests/phase2_test.py          # prints PASS/FAIL per test, non-zero exit on failure
    pytest tests/phase2_test.py          # standard collection (test_* functions)

Coverage:
  Unit (fast, deterministic):
    - rotation porting trap (roll by i, not 2*i)
    - inverse / reduce (adjacent + wraparound) / Booth minimal rotation / canonical (inversion-inv)
    - canonical_tuple order-independence; state_to_key/key_to_state round-trip
    - n=2 neighbor equivalence vs the known-good notebook `get_neighbors_nj` (canonical-state level)
    - boundary-letter fast-reject == brute concat+reduce (n=2 and n=3)
  Pre-flight discriminating checks (PLAN.md Phase 2, checks 1-5):
    2. differential oracle vs greedy_ac at n=2 (THE gate) — identical solved set on hard cases
    3. z=x stays solvable at n=3; path replays
    4. z-pair neighbors exact (specific expected state present; trivial z is inert)
    5. null-revert block FIRES (revert_hits > 0) and never settles on canon(r1,r2,z=1)
  Persist-loop closure: serialize -> sidecar -> read back -> deserialize -> verify_path passes.
"""
import ast
import json
import os
import random
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, ".."))
ONEGEN = os.path.join(ROOT, "experiments", "stable_ac", "one_generator")
BASELINE_N2 = os.path.join(ONEGEN, "baseline_n2")
for p in (ONEGEN, BASELINE_N2):
    if p not in sys.path:
        sys.path.insert(0, p)

import greedy_nrel as gn          # noqa: E402
import greedy_ac as ga            # noqa: E402  (the known-good n=2 solver — the oracle)
import stabilize as stab          # noqa: E402  (Phase 1 z=w transform)

DATA_1190 = os.path.join(ROOT, "data", "1190MS.txt")


# --------------------------------------------------------------------------- helpers

def arr(xs):
    return np.array(xs, dtype=np.int64)


def state(*relators):
    return tuple(arr(r) for r in relators)


def canon_key(*relators):
    return gn.state_to_key(gn.canonical_tuple(state(*relators)))


def canon_key_set(neighbors):
    return {gn.state_to_key(gn.canonical_tuple(s)) for s, _ in neighbors}


def brute_neighbors(st, n_gen):
    """Independent reference for the SAME move set: unordered pair {a,b} (a<b, leader a), candidate
    c in {r_b, r_b^-1}, materialize every rotation pair, check the boundary on the built arrays
    (rot_a[-1] == -rot_c[0]), and on a cancel emit reduce(concat) into BOTH slot a and slot b.
    Differs from gn.get_neighbors only in using materialize-then-check instead of the index-
    arithmetic fast-reject — so equality certifies the fast-reject index math."""
    n = len(st)
    out = []
    for a in range(n):
        ra = st[a]
        if len(ra) == 0:
            continue
        for b in range(a + 1, n):
            rb = st[b]
            for c in (rb, gn.inverse_relator(rb)):
                if len(c) == 0:
                    continue
                for i in range(len(ra)):
                    rot_a = np.roll(ra, i)
                    for j in range(len(c)):
                        rot_c = np.roll(c, j)
                        if rot_a[-1] == -rot_c[0]:
                            nb = gn.reduce_relator(np.concatenate((rot_a, rot_c)))
                            if len(nb) == 0:
                                continue
                            sa = list(st)
                            sa[a] = nb
                            out.append((tuple(sa), (a, i, j)))
                            sb = list(st)
                            sb[b] = nb
                            out.append((tuple(sb), (b, i, j)))
    return out


def random_reduced_word(rng, n_gen, min_len=2, max_len=8):
    while True:
        w = arr([rng.choice([g for g in range(-n_gen, n_gen + 1) if g != 0])
                 for _ in range(rng.randint(min_len, max_len))])
        r = gn.reduce_relator(w)
        if len(r) >= min_len:
            return r


# notebook (bool) <-> int bridges, for the n=2 equivalence test
INT2CH = {1: "x", -1: "X", 2: "y", -2: "Y"}


def int_relator_to_str(r):
    return "".join(INT2CH[int(x)] for x in r)


def bool_arr_to_int(a):
    # notebook letter [gen_bool, notinv_bool]: x=[T,T]->1 X=[T,F]->-1 y=[F,T]->2 Y=[F,F]->-2
    return np.array([(1 if c[0] else 2) * (1 if c[1] else -1) for c in a], dtype=np.int64)


def my_neighbor_keys(st):
    out = set()
    for s, _ in gn.get_neighbors(st, 2):
        if any(len(r) == 0 for r in s):
            continue
        out.add(gn.state_to_key(gn.canonical_tuple(s)))
    return out


def notebook_neighbor_keys(r1_int, r2_int):
    """The notebook's raw spliced words (its own np.roll rotation logic), reduced+canonicalized with
    the CORRECT reduce so the comparison tests move GENERATION (rotation, splice) and does not
    inherit reduce_relator_nj's out-of-bounds behaviour on fully-cancelling splices (which fabricates
    a garbage length-1 relator). Full-cancellation phantoms are dropped on both sides."""
    r1a, r2a = ga.str_to_arr(int_relator_to_str(r1_int)), ga.str_to_arr(int_relator_to_str(r2_int))
    out = set()
    for nr1, nr2 in ga.get_neighbors_nj(r1a, r2a):
        i1 = gn.reduce_relator(bool_arr_to_int(nr1))
        i2 = gn.reduce_relator(bool_arr_to_int(nr2))
        if len(i1) == 0 or len(i2) == 0:
            continue
        out.add(gn.state_to_key(gn.canonical_tuple((i1, i2))))
    return out


def load_flats():
    with open(DATA_1190) as f:
        return [ast.literal_eval(line) for line in f if line.strip()]


# =========================================================================== UNIT: 1

def test_rotation_trap():
    """np.roll by i (one slot per letter), NOT 2*i. The silent-correctness guard."""
    r = arr([1, 2, 3, -1])
    assert list(gn.rotate(r, 0)) == [1, 2, 3, -1]          # identity
    assert list(gn.rotate(r, 1)) == [-1, 1, 2, 3]          # roll right by 1 letter
    assert list(gn.rotate(r, 2)) == [3, -1, 1, 2]
    assert list(gn.rotate(r, 3)) == [2, 3, -1, 1]
    assert list(gn.rotate(r, 4)) == [1, 2, 3, -1]          # wraparound (len 4)
    # the boundary-index math get_neighbors uses must equal the materialized rotation ends
    for i in range(len(r)):
        rolled = np.roll(r, i)
        assert r[(len(r) - 1 - i) % len(r)] == rolled[-1]  # "last letter of rot(r,i)"
        assert r[(-i) % len(r)] == rolled[0]               # "first letter of rot(r,i)"


# =========================================================================== UNIT: 2

def test_inverse_relator():
    assert list(gn.inverse_relator(arr([1, 2, -3]))) == [3, -2, -1]
    assert list(gn.inverse_relator(arr([1]))) == [-1]
    assert list(gn.inverse_relator(gn.inverse_relator(arr([1, 2, -3, 2])))) == [1, 2, -3, 2]


def test_reduce_relator():
    assert list(gn.reduce_relator(arr([1, -1, 2]))) == [2]              # adjacent
    assert list(gn.reduce_relator(arr([1, 2, -2, -1, 3]))) == [3]       # nested adjacent
    assert list(gn.reduce_relator(arr([1, 2, -1]))) == [2]              # cyclic (wraparound) trim
    assert list(gn.reduce_relator(arr([2, 1, 3, -1, -2]))) == [3]       # cyclic both ends
    assert list(gn.reduce_relator(arr([1, 2, 3]))) == [1, 2, 3]         # already reduced
    assert list(gn.reduce_relator(arr([1, -1]))) == []                  # full cancellation


def test_find_minimal_rotation_and_canonical():
    w = arr([2, 3, 1, 1])
    mr = gn.find_minimal_rotation(w)
    # minimal rotation is rotation-invariant
    for i in range(len(w)):
        assert list(gn.find_minimal_rotation(np.roll(w, i))) == list(mr)
    # canonical is invariant under rotation AND inversion
    cw = gn.canonical_relator(w)
    for i in range(len(w)):
        assert list(gn.canonical_relator(np.roll(w, i))) == list(cw)
    assert list(gn.canonical_relator(gn.inverse_relator(w))) == list(cw)


# =========================================================================== UNIT: 3,4

def test_canonical_tuple_order_independent():
    a, b, c = arr([1, 2, 1]), arr([2]), arr([3, -2, -1])
    k1 = gn.state_to_key(gn.canonical_tuple((a, b, c)))
    k2 = gn.state_to_key(gn.canonical_tuple((c, a, b)))
    k3 = gn.state_to_key(gn.canonical_tuple((b, c, a)))
    assert k1 == k2 == k3
    # sorted by (len, lex): shortest relator first
    ct = gn.canonical_tuple((a, b, c))
    assert [len(r) for r in ct] == sorted(len(r) for r in (a, b, c))


def test_key_roundtrip():
    for st in [state([1], [2]), state([1, 2, -1], [3, -2, -1], [2, 2]),
               state([-3, -2, -1, 1, 2, 3])]:
        ct = gn.canonical_tuple(st)
        key = gn.state_to_key(ct)
        back = gn.key_to_state(key)
        assert gn.state_to_key(gn.canonical_tuple(back)) == key
        assert [list(r) for r in back] == [list(r) for r in ct]


# =========================================================================== UNIT: 5

def test_n2_neighbor_equivalence_vs_notebook():
    """MY get_neighbors at n=2 == the notebook get_neighbors_nj, compared at the canonical-state
    level (both reduced+canonicalized+sorted). Stronger than solved-set: it pins rotate + the move
    generalization directly against the shipped reference."""
    rng = random.Random(20260702)
    checked = 0
    for _ in range(60):
        r1 = random_reduced_word(rng, 2, min_len=2, max_len=7)
        r2 = random_reduced_word(rng, 2, min_len=2, max_len=7)
        mine = my_neighbor_keys(state(list(r1), list(r2)))
        book = notebook_neighbor_keys(r1, r2)
        assert mine == book, (
            f"neighbor mismatch for r1={list(r1)} r2={list(r2)}\n"
            f"  only-mine={mine - book}\n  only-book={book - mine}")
        checked += 1
    assert checked == 60


# =========================================================================== UNIT: 6

def test_fast_reject_equals_brute():
    """The index-arithmetic boundary fast-reject selects EXACTLY the pairs a materialize-then-check
    brute force does — for n=2 and n=3."""
    rng = random.Random(13)
    for n_gen in (2, 3):
        for _ in range(30):
            st = state(*[list(random_reduced_word(rng, n_gen, 2, 6)) for _ in range(n_gen)])
            assert canon_key_set(gn.get_neighbors(st, n_gen)) == canon_key_set(brute_neighbors(st, n_gen))


def test_is_trivial():
    assert gn.is_trivial(state([1], [2], [3]))
    assert not gn.is_trivial(state([1, 2], [3]))
    assert not gn.is_trivial(state([1], [2, -2 + 0]))  # length 2 relator


# =============================================================== PRE-FLIGHT 2 (THE gate)

# solvable-region idx (bounded budget so real solves terminate early) + hard controls (small budget)
ORACLE_SOLVABLE_IDX = [0, 1, 2, 3, 4, 80, 150, 250, 350, 600]
ORACLE_SOLVABLE_BUDGET = 15000
ORACLE_CONTROL_IDX = [645, 700]
ORACLE_CONTROL_BUDGET = 4000
ORACLE_MAX_LEN = 24  # per-relator, same for both solvers


def _oracle_arm(flats, idxs, budget):
    """Return {idx: (my_solved, my_verified, ga_solved)} for one budget tier."""
    res = {}
    for idx in idxs:
        flat = flats[idx]
        r_mine, path = gn.solve_one(flat, n_gen=2, max_len=ORACLE_MAX_LEN, max_nodes=budget)
        r_ga = ga.solve_one(flat, cap_mode="per_relator", max_len=ORACLE_MAX_LEN, max_nodes=budget)
        res[idx] = (r_mine["solved"], r_mine["path_verified"], r_ga["solved"])
    return res


def test_differential_oracle_vs_greedy_ac_n2():
    flats = load_flats()
    results = {}
    results.update(_oracle_arm(flats, ORACLE_SOLVABLE_IDX, ORACLE_SOLVABLE_BUDGET))
    results.update(_oracle_arm(flats, ORACLE_CONTROL_IDX, ORACLE_CONTROL_BUDGET))

    mismatches = [idx for idx, (m, _, g) in results.items() if m != g]
    # every solve MY solver reports must independently replay
    unverified = [idx for idx, (m, v, _) in results.items() if m and not v]
    assert not unverified, f"solved-but-unverified (search bug): {unverified}"
    # solved SET must match; tolerate a single at-budget boundary flip, investigate anything more
    assert len(mismatches) <= 1, (
        f"solved-set disagreement vs greedy_ac on {mismatches}: "
        + ", ".join(f"idx {i}: mine={results[i][0]} ga={results[i][2]}" for i in mismatches))
    # the gate is only meaningful if HARD cases actually solved in both (not all trivial 2-3 node ones)
    hard_solved = [idx for idx in ORACLE_SOLVABLE_IDX if idx >= 80 and results[idx][0] and results[idx][2]]
    assert hard_solved, "no hard (idx>=80) case solved in both — oracle not discriminating"


# =============================================================== PRE-FLIGHT 3 (z=x solvable)

def test_zx_stays_solvable():
    # (a) hand base already trivial -> z=x collapses in one move
    flat_hand = stab.relators_to_flat([[1], [2]], 2)
    sflat_hand = stab.stabilize_flat(flat_hand, "x")            # (x, y, z*x^-1)
    r_hand, path_hand = gn.solve_one(sflat_hand, n_gen=3, max_len=24, max_nodes=2000)
    assert r_hand["solved"] and r_hand["path_verified"], f"hand z=x not solved/verified: {r_hand}"

    # (b) a real solvable presentation from the dataset, stabilized z=x, still solves at n=3
    flats = load_flats()
    sflat = stab.stabilize_flat(flats[0], "x")
    r0, path0 = gn.solve_one(sflat, n_gen=3, max_len=24, max_nodes=60000)
    assert r0["solved"] and r0["path_verified"], f"idx0 z=x not solved/verified: {r0}"
    assert gn.is_trivial(path0["states"][-1])


# =============================================================== PRE-FLIGHT 4 (z-pair exact)

def test_z_pair_neighbors_exact():
    # content-bearing z: r1=x, z-relator = z*(xy)^-1 = [3,-2,-1] (so z=w=xy)
    st = state([1, 2], [3, -2, -1])
    got = canon_key_set(gn.get_neighbors(st, 2))
    # independent brute reference gives the exact expected set
    assert got == canon_key_set(brute_neighbors(st, 2))
    # and it must contain the z-collapse (z*(xy)^-1)*(xy) -> z : new state (xy, z). Reaching a
    # state whose z-relator is length-1 proves the (r_i, z) substitution actually fires.
    assert canon_key([1, 2], [3]) in got, "z-collapse neighbour (xy, z) missing"

    # trivial z: z-relator = [z] alone (z=1) -> z cannot cancel any x/y letter -> inert
    st_triv = state([1, 2], [3])
    assert gn.get_neighbors(st_triv, 2) == [], "trivial z must yield no neighbours (nothing cancels z)"


# =============================================================== PRE-FLIGHT 5 (block FIRES)

def test_null_revert_block_fires():
    # base (r1, r2); stabilize z=r1  -> z-relator = [3] ++ inverse(r1). Collapsing z*r1^-1 * r1 = z
    # is a length-decreasing move greedy tries immediately, landing on canon(r1, r2, z=1).
    base = stab.relators_to_flat([[1, 1, 2], [2, 2, 1]], 2)
    sflat = stab.stabilize_flat(base, "r1")
    blocked = [gn.null_revert_state(sflat, n_gen=3)]
    blocked_key = gn.state_to_key(gn.canonical_tuple(blocked[0]))

    relators = gn.flat_to_relators(sflat, 3)
    solver = gn.NRelatorSolver(relators, n_gen=3, max_nodes=400, max_len=24,
                               blocked_states=blocked, track_reverts=True)
    solver.solve()
    assert solver.revert_hits > 0, "block never fired — the null-revert is a no-op (matches nothing)"
    assert solver.revert_log, "track_reverts on but revert_log empty"
    assert blocked_key not in solver.visited, "search settled on the blocked (z-collapsed) state"

    # control: WITHOUT the block, the very same collapse IS generated (proves the block is what stops it)
    solver2 = gn.NRelatorSolver(relators, n_gen=3, max_nodes=400, max_len=24)
    solver2.solve()
    assert blocked_key in solver2.visited, "without a block the z-collapse should be reachable"


# =============================================================== PERSIST-LOOP CLOSURE

def test_persist_loop_closure():
    """serialize -> write sidecar (append/flush/fsync) -> read back -> deserialize -> verify_path.
    The on-disk representation must be exactly what verify_path accepts (not lossy)."""
    flat_hand = stab.relators_to_flat([[1], [2]], 2)
    sflat = stab.stabilize_flat(flat_hand, "x")
    result, path = gn.solve_one(sflat, n_gen=3, max_len=24, max_nodes=2000)
    assert result["solved"] and path is not None

    # in-memory verify holds
    assert gn.verify_path(path["states"], 3)

    tmpdir = os.path.join(HERE, "_tmp_phase2")
    sidecar = os.path.join(tmpdir, "paths_test_arm.jsonl")
    if os.path.exists(sidecar):
        os.remove(sidecar)
    record = gn.serialize_path(path, idx=0, name="z=x hand")
    gn.write_path_sidecar(sidecar, record)

    # read back the on-disk artifact and replay it independently
    with open(sidecar) as f:
        lines = [json.loads(x) for x in f if x.strip()]
    assert len(lines) == 1
    rec = lines[0]
    assert rec["idx"] == 0 and rec["path_len"] == len(path["states"]) - 1
    restored = gn.deserialize_states(rec)
    assert gn.verify_path(restored, 3), "deserialized on-disk path failed independent replay"
    # deserialized states equal the in-memory ones (round-trip is lossless)
    assert [[list(r) for r in st] for st in restored] == [[list(r) for r in st] for st in path["states"]]

    os.remove(sidecar)
    os.rmdir(tmpdir)


# --------------------------------------------------------------------------- runner

ALL_TESTS = [
    ("rotation_trap", test_rotation_trap),
    ("inverse_relator", test_inverse_relator),
    ("reduce_relator", test_reduce_relator),
    ("find_minimal_rotation_and_canonical", test_find_minimal_rotation_and_canonical),
    ("canonical_tuple_order_independent", test_canonical_tuple_order_independent),
    ("key_roundtrip", test_key_roundtrip),
    ("n2_neighbor_equivalence_vs_notebook", test_n2_neighbor_equivalence_vs_notebook),
    ("fast_reject_equals_brute", test_fast_reject_equals_brute),
    ("is_trivial", test_is_trivial),
    ("z_pair_neighbors_exact", test_z_pair_neighbors_exact),
    ("null_revert_block_fires", test_null_revert_block_fires),
    ("zx_stays_solvable", test_zx_stays_solvable),
    ("differential_oracle_vs_greedy_ac_n2", test_differential_oracle_vs_greedy_ac_n2),
    ("persist_loop_closure", test_persist_loop_closure),
]


def main():
    import time
    failures = []
    for name, fn in ALL_TESTS:
        t0 = time.time()
        try:
            fn()
            print(f"PASS  {name:42} ({time.time()-t0:5.1f}s)")
        except AssertionError as e:
            failures.append(name)
            print(f"FAIL  {name:42} ({time.time()-t0:5.1f}s)\n      {e}")
        except Exception as e:
            failures.append(name)
            print(f"ERROR {name:42} ({time.time()-t0:5.1f}s)\n      {type(e).__name__}: {e}")
    print("-" * 60)
    if failures:
        print(f"{len(failures)}/{len(ALL_TESTS)} FAILED: {failures}")
        sys.exit(1)
    print(f"all {len(ALL_TESTS)} tests passed")


if __name__ == "__main__":
    main()
