"""Independent, adversarial, black-box test suite for ``greedy_nrel.py``.

This suite was written WITHOUT reading the internal logic of ``greedy_nrel.py`` or the
author's own ``tests/phase2_test.py``. Every reference oracle here is rebuilt from the
mathematical definition of the Andrews-Curtis substitution (GS-Sub) move set, free/cyclic
reduction, word inversion, and lexicographic-minimal-rotation canonicalisation. The module
under test is exercised ONLY through its public API and its outputs are re-mapped through
these independent oracles before any comparison.

Core design principle (do not trust the module's own canonical form): both sides of every
equivalence comparison are re-canonicalised with THIS file's ``canon_word`` / ``canon_state``,
which use a plain O(L^2) brute-force minimal rotation over a fixed total order (Python tuple
ordering). The module's internal total order is therefore irrelevant -- we compare equivalence
CLASSES, never raw canonical arrays across implementations.

The paper's original n=2 njit greedy (``baseline_n2/greedy_ac.py``) is used ONLY as a second,
independent reference for the n=2 move set. Its ``reduce_relator_nj`` has a documented
reads-past-end bug on fully-cancelling words, so we NEVER use it to reduce: we take its raw
spliced neighbour words and reduce them with OUR own reducer, dropping any that collapse to
empty.

Run:  cd <repo root> && python tests/phase2_independent_test.py     (also works under pytest)
"""
import ast
import json
import os
import random
import sys
import time
import traceback

import numpy as np

# --------------------------------------------------------------------------------------
# paths / imports
# --------------------------------------------------------------------------------------
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
ONEGEN = os.path.join(REPO, "experiments", "stable_ac", "one_generator")
BASE_N2 = os.path.join(REPO, "experiments", "stable_ac", "baseline_n2")
for _p in (ONEGEN, BASE_N2):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import greedy_nrel as G      # noqa: E402  module under test
import stabilize as S        # noqa: E402  phase-1 stabiliser (contract-level under test)
import greedy_ac as GA       # noqa: E402  independent n=2 reference oracle

DATA = os.path.join(REPO, "data")
STAB = os.path.join(DATA, "stabilized")
TMPDIR = os.path.join(HERE, "_tmp_independent")

random.seed(20260702)

INT2CHAR = {1: "x", -1: "X", 2: "y", -2: "Y"}
CHAR2INT = {v: k for k, v in INT2CHAR.items()}


# ======================================================================================
# INDEPENDENT ORACLES (built from the math, in signed-int Python-list space)
# ======================================================================================
def reduce_word(w):
    """Free reduction (delete adjacent inverse pairs) then cyclic reduction
    (delete matching inverse letters at the two ends). Unique result. Plain-Python stack.
    Ignores any 0 padding defensively."""
    stack = []
    for a in w:
        a = int(a)
        if a == 0:
            continue
        if stack and stack[-1] == -a:
            stack.pop()
        else:
            stack.append(a)
    i, j = 0, len(stack) - 1
    while i < j and stack[i] == -stack[j]:
        i += 1
        j -= 1
    return stack[i:j + 1]


def inverse_word(w):
    """Inverse of a word: reverse and negate every letter."""
    return [-int(a) for a in reversed(list(w))]


def _rotations(word):
    L = len(word)
    return [tuple(word[i:] + word[:i]) for i in range(L)]


def canon_word(w):
    """Canonical form of a relator's equivalence class: lexicographically-minimal rotation
    over BOTH the word and its inverse, under a fixed total order (Python tuple ordering).
    Brute force over all rotations -- obviously correct, order O(L^2). Returns a tuple.
    Empty word -> ()."""
    w = reduce_word(w)
    if not w:
        return ()
    cands = _rotations(w) + _rotations(inverse_word(w))
    return min(cands)


def canon_state(words):
    """Canonical, order-independent key of a whole state: canonicalise each relator, sort
    relators by (length, tuple). ``words`` is an iterable of int-lists/arrays."""
    cs = [canon_word(list(map(int, r))) for r in words]
    cs.sort(key=lambda t: (len(t), t))
    return tuple(cs)


def brute_neighbors(words, drop_empty=True):
    """Independent brute-force GS-Sub neighbour generator. For every ORDERED pair (a,b),
    a!=b (covers both leader directions), candidate c in {r_b, inverse(r_b)}, and every
    cyclic rotation of r_a and c, if last(rot_ra) == -first(rot_c) then
    neighbour = reduce(concat(rot_ra, rot_c)); produce two states -- one replacing a, one
    replacing b. Returns a SET of canon_state keys (empties dropped)."""
    n = len(words)
    red = [reduce_word(list(map(int, w))) for w in words]
    out = set()
    for a in range(n):
        for b in range(n):
            if a == b:
                continue
            ra = red[a]
            for c in (red[b], inverse_word(red[b])):
                La, Lc = len(ra), len(c)
                if La == 0 or Lc == 0:
                    continue
                for i in range(La):
                    rota = ra[i:] + ra[:i]
                    for j in range(Lc):
                        rotc = c[j:] + c[:j]
                        if rota[-1] == -rotc[0]:
                            neigh = reduce_word(rota + rotc)
                            for mod in (a, b):
                                new = list(red)
                                new[mod] = neigh
                                cs = [canon_word(x) for x in new]
                                if drop_empty and any(len(x) == 0 for x in cs):
                                    continue
                                cs.sort(key=lambda t: (len(t), t))
                                out.add(tuple(cs))
    return out


def nrel_neighbor_classes(state, n_gen):
    """greedy_nrel.get_neighbors output -> set of canon_state keys via OUR canon (empties dropped)."""
    out = set()
    for ns, _mv in G.get_neighbors(state, n_gen):
        cs = [canon_word(list(map(int, r))) for r in ns]
        if any(len(x) == 0 for x in cs):
            continue
        cs.sort(key=lambda t: (len(t), t))
        out.add(tuple(cs))
    return out


def greedy_ac_neighbor_classes(r1_ints, r2_ints):
    """Independent n=2 reference: greedy_ac.get_neighbors_nj raw splices -> reduce with OUR
    reducer (NOT reduce_relator_nj) -> drop empties -> canon classes."""
    a1 = np.array([GA.char_to_array[INT2CHAR[i]] for i in r1_ints], dtype=bool)
    a2 = np.array([GA.char_to_array[INT2CHAR[i]] for i in r2_ints], dtype=bool)
    out = set()
    for nr1, nr2 in GA.get_neighbors_nj(a1, a2):
        w1 = _boolarr_to_ints(nr1)
        w2 = _boolarr_to_ints(nr2)
        r1r, r2r = reduce_word(w1), reduce_word(w2)
        if not r1r or not r2r:
            continue
        cs = [canon_word(r1r), canon_word(r2r)]
        cs.sort(key=lambda t: (len(t), t))
        out.add(tuple(cs))
    return out


def _boolarr_to_ints(arr):
    out = []
    for c in arr:
        b0, b1 = bool(c[0]), bool(c[1])
        ch = ("x" if b1 else "X") if b0 else ("y" if b1 else "Y")
        out.append(CHAR2INT[ch])
    return out


def independent_replay(states, n_gen):
    """Independent path replayer using ONLY our move logic + our reducer (NOT G.verify_path).
    Every consecutive (s_k, s_{k+1}) must be a legal move (canon(s_{k+1}) in brute_neighbors(s_k))
    and the final state must be trivial (all relators length 1). Returns (ok, reason)."""
    if not states or len(states) < 1:
        return False, "empty path"
    for k in range(len(states) - 1):
        cur = [list(map(int, r)) for r in states[k]]
        nxt_key = canon_state(states[k + 1])
        if nxt_key not in brute_neighbors(cur):
            return False, f"illegal move at step {k}"
    final = states[-1]
    if not all(len(r) == 1 for r in final):
        return False, "endpoint not trivial (a relator has length != 1)"
    return True, None


def rand_word(max_len=8, gens=(1, 2)):
    """A random NON-EMPTY freely+cyclically reduced word over +/-gens."""
    for _ in range(200):
        L = random.randint(1, max_len)
        w = []
        for _ in range(L):
            g = random.choice(gens)
            w.append(g if random.random() < 0.5 else -g)
        r = reduce_word(w)
        if r:
            return r
    return [random.choice(gens)]


def strs_to_flat(r1s, r2s, half=24):
    r1 = [CHAR2INT[c] for c in r1s]
    r2 = [CHAR2INT[c] for c in r2s]
    return r1 + [0] * (half - len(r1)) + r2 + [0] * (half - len(r2))


def read_lines(path, k=None):
    out = []
    with open(path) as f:
        for i, line in enumerate(f):
            if k is not None and i >= k:
                break
            out.append(ast.literal_eval(line))
    return out


# ======================================================================================
# TESTS
# ======================================================================================
def test_01_primitives_reduce_inverse():
    """reduce_relator / inverse_relator agree exactly with our from-scratch oracles on
    random words AND hand-picked full-cancellation / wrap-around edge cases."""
    edge = [
        [1, -1], [1, 2, -2, -1], [2, 1, -1, -2], [1, -1, 2, -2],       # -> empty
        [1, 2, 3, -2, -1],                                              # wrap-around -> [3]
        [1, 2, -1],                                                     # cyclic -> [2]
        [2, 3, -2],                                                     # cyclic -> [3]
        [1], [3], [-2],                                                 # single letter
        [1, 2, 1, -2, -1, -2],                                          # already reduced
        [-2, -2, -1, 2, 1],                                             # a real dataset relator
    ]
    rand = [rand_word(10, gens=(1, 2, 3)) + [random.choice([1, -1, 2, -2, 3, -3])]
            for _ in range(300)]
    problems = []
    for w in edge + rand:
        arr = np.array(w, dtype=np.int64)
        mine = reduce_word(w)
        try:
            got = [int(x) for x in G.reduce_relator(arr)]
        except Exception as e:  # a CRASH on a valid word is itself a finding
            problems.append(f"reduce_relator CRASH on {w}: {e!r}")
            continue
        if got != mine:
            problems.append(f"reduce_relator({w}) -> {got}, expected {mine}")
        # inverse: exact reverse+negate
        try:
            ginv = [int(x) for x in G.inverse_relator(arr)]
        except Exception as e:
            problems.append(f"inverse_relator CRASH on {w}: {e!r}")
            continue
        if ginv != inverse_word(w):
            problems.append(f"inverse_relator({w}) -> {ginv}, expected {inverse_word(w)}")
    assert not problems, "PRIMITIVE MISMATCHES:\n  " + "\n  ".join(problems[:20])


def test_02_rotation_convention():
    """rotate(rel, i) is a RIGHT cyclic shift by i (== np.roll), for i incl 0 and wrap-around.
    Pins the shift-by-i vs shift-by-2i silent-corruption trap."""
    base = np.array([1, 2, 3, 4, 5], dtype=np.int64)
    problems = []
    for i in [0, 1, 2, 4, 5, 7, 11]:
        got = [int(x) for x in G.rotate(base, i)]
        exp = [int(x) for x in np.roll(base, i)]
        if got != exp:
            problems.append(f"rotate(base,{i}) -> {got}, np.roll -> {exp}")
    # explicit right-by-1 (NOT by 2)
    r1 = [int(x) for x in G.rotate(np.array([1, 2, 3, 4]), 1)]
    if r1 != [4, 1, 2, 3]:
        problems.append(f"rotate([1,2,3,4],1) -> {r1}, expected [4,1,2,3] (right shift by 1)")
    assert not problems, "ROTATION CONVENTION:\n  " + "\n  ".join(problems)


def test_03_canonical_invariance_and_class():
    """canonical_relator is invariant under rotation AND inversion (maps a word, all its
    rotations, and its inverse to the SAME array). Independently: two words are canonical-equal
    in greedy_nrel IFF they are in the same class under OUR brute-force definition."""
    problems = []
    words = [rand_word(9, gens=(1, 2, 3)) for _ in range(150)]
    for w in words:
        arr = np.array(w, dtype=np.int64)
        base = G.canonical_relator(arr)
        for i in range(len(w)):
            rot = G.canonical_relator(G.rotate(arr, i))
            if not np.array_equal(base, rot):
                problems.append(f"canonical not rotation-invariant for {w} at i={i}")
                break
        inv = G.canonical_relator(G.inverse_relator(arr))
        if not np.array_equal(base, inv):
            problems.append(f"canonical not inversion-invariant for {w}")
    # class agreement: (nrel canonical arrays equal) iff (our canon equal)
    for _ in range(300):
        w1 = rand_word(7, gens=(1, 2, 3))
        w2 = rand_word(7, gens=(1, 2, 3))
        nrel_same = np.array_equal(G.canonical_relator(np.array(w1)),
                                   G.canonical_relator(np.array(w2)))
        mine_same = (canon_word(w1) == canon_word(w2))
        if nrel_same != mine_same:
            problems.append(f"class disagreement: {w1} vs {w2} nrel_same={nrel_same} mine={mine_same}")
    assert not problems, "CANONICAL:\n  " + "\n  ".join(problems[:20])


def test_04_n2_moveset_vs_greedy_ac():
    """n=2 move set: three-way agreement (minus self-loop parent class):
    greedy_nrel == greedy_ac(reference) == our brute-force. Establishes brute is trustworthy
    at n=2 before we rely on it at n=3. Also asserts greedy_nrel's set is a SUBSET of the
    exhaustive legal set (no illegal neighbour = the hard, definite-bug direction)."""
    # n=2 reference (greedy_ac) supports only generators x,y -> gens (1,2) here.
    hand = [
        ([1, 2], [1, 2]),                      # r1 == r2
        ([1, 2, -1], [1, -2]),
        ([1, 1, 2], [-2, -1, -1]),             # shared / opposed boundaries
        ([1, -2, 1], [2, -1, -2]),
        ([1], [2]),
        ([1, 2, 1], [2, 1, 2]),
    ]
    cases = hand + [(rand_word(7, gens=(1, 2)), rand_word(7, gens=(1, 2))) for _ in range(80)]
    problems = []
    for r1, r2 in cases:
        r1, r2 = reduce_word(r1), reduce_word(r2)
        if not r1 or not r2:
            continue
        state = (np.array(r1, dtype=np.int64), np.array(r2, dtype=np.int64))
        parent = canon_state([r1, r2])
        nrel = nrel_neighbor_classes(state, 2)
        ref = greedy_ac_neighbor_classes(r1, r2)
        brute = brute_neighbors([r1, r2])
        # brute must reproduce the trusted reference exactly (minus parent self-loop)
        if (brute - {parent}) != (ref - {parent}):
            problems.append(f"BRUTE!=greedy_ac for ({r1},{r2}): "
                            f"only_brute={sorted(brute-ref-{parent})[:3]} only_ac={sorted(ref-brute-{parent})[:3]}")
        # greedy_nrel must match the reference (minus parent self-loop)
        if (nrel - {parent}) != (ref - {parent}):
            problems.append(f"NREL!=greedy_ac for ({r1},{r2}): "
                            f"only_nrel={sorted(nrel-ref-{parent})[:3]} only_ac={sorted(ref-nrel-{parent})[:3]}")
        # hard direction: every emitted neighbour is mathematically legal
        if not nrel.issubset(brute):
            problems.append(f"NREL emitted ILLEGAL neighbour for ({r1},{r2}): {sorted(nrel-brute)[:3]}")
    assert not problems, "n=2 MOVESET:\n  " + "\n  ".join(problems[:20])


def test_05_n3_move_validity():
    """n=3 move set (no direct reference): greedy_nrel neighbour classes == our brute-force
    classes (minus parent self-loop), AND greedy_nrel subset brute (no illegal move). Plus a
    structural check: each returned neighbour differs from the parent in EXACTLY one relator
    (the modified_index), the others are byte-identical, and the modified relator is reduced."""
    problems = []
    for _ in range(45):
        words = [rand_word(6, gens=(1, 2, 3)) for _ in range(3)]
        state = tuple(np.array(w, dtype=np.int64) for w in words)
        parent = canon_state(words)
        nrel = nrel_neighbor_classes(state, 3)
        brute = brute_neighbors(words)
        if not nrel.issubset(brute):
            problems.append(f"NREL emitted ILLEGAL n=3 neighbour for {words}: {sorted(nrel-brute)[:2]}")
        if (nrel - {parent}) != (brute - {parent}):
            only_n = sorted(nrel - brute - {parent})[:2]
            only_b = sorted(brute - nrel - {parent})[:2]
            problems.append(f"n=3 set mismatch for {words}: only_nrel={only_n} only_brute={only_b}")
        # structural check on raw output
        for ns, mv in G.get_neighbors(state, 3):
            mi = int(mv[0])
            if not (0 <= mi < 3):
                problems.append(f"bad modified_index {mi} for {words}")
                continue
            for j in range(3):
                if j != mi and not np.array_equal(ns[j], state[j]):
                    problems.append(f"non-modified relator {j} changed (mi={mi}) for {words}")
            modw = [int(x) for x in ns[mi]]
            if reduce_word(modw) != modw:
                problems.append(f"modified relator NOT reduced (mi={mi}) for {words}: {modw}")
    assert not problems, "n=3 MOVE VALIDITY:\n  " + "\n  ".join(problems[:20])


def test_06_solve_paths_replay_independently():
    """Highest-value check: run solve_one on real solvable presentations (n=2 from 1190MS,
    n=3 from stabilized z_x / z_y). For every reported solve, replay path_obj['states'] with
    OUR OWN move logic (NOT G.verify_path): every step legal + final trivial. A solve whose
    path does not independently replay is a real bug."""
    problems = []
    checked = {"n2": 0, "n3": 0}

    n2_lines = read_lines(os.path.join(DATA, "1190MS.txt"), 200)
    for idx in [0, 2, 10, 30, 100, 150, 180]:
        res, path = G.solve_one(n2_lines[idx], 2, max_len=24, max_nodes=20000)
        if not res["solved"]:
            continue
        ok, reason = independent_replay(path["states"], 2)
        checked["n2"] += 1
        if not ok:
            problems.append(f"n=2 idx {idx}: independent replay FAILED ({reason})")
        if not G.is_trivial(path["states"][-1]):
            problems.append(f"n=2 idx {idx}: is_trivial(final) is False but solved=True")
        if res.get("path_verified") is not True:
            problems.append(f"n=2 idx {idx}: solved but path_verified != True ({res.get('path_verified')})")

    for fname in ("1190MS_z_x.txt", "1190MS_z_y.txt"):
        lines = read_lines(os.path.join(STAB, fname), 4)
        for idx in range(min(3, len(lines))):
            res, path = G.solve_one(lines[idx], 3, max_len=24, max_nodes=30000)
            if not res["solved"]:
                continue
            ok, reason = independent_replay(path["states"], 3)
            checked["n3"] += 1
            if not ok:
                problems.append(f"n=3 {fname} idx {idx}: independent replay FAILED ({reason})")
            if not G.is_trivial(path["states"][-1]):
                problems.append(f"n=3 {fname} idx {idx}: is_trivial(final) False but solved=True")

    assert checked["n2"] >= 3 and checked["n3"] >= 3, \
        f"too few solves actually replayed: {checked}"
    assert not problems, "SOLVE REPLAY:\n  " + "\n  ".join(problems[:20])


def test_07_solved_set_agreement_n2():
    """Solved SET agreement vs greedy_ac (cap_mode='per_relator', max_len=24) on a curated
    n=2 sample incl hard-but-solvable cases (idx 380/470/560, hundreds-thousands of nodes,
    solved with margin under budget 8000) and unsolvable AK(3)/Length-14 controls at a small
    budget. Compares solved flags only -- never node counts / path lengths."""
    lines = read_lines(os.path.join(DATA, "1190MS.txt"))
    problems = []
    max_nodes_seen = 0
    solvable = [0, 2, 10, 30, 100, 380, 470, 560]
    for idx in solvable:
        rn, _ = G.solve_one(lines[idx], 2, max_len=24, max_nodes=8000)
        ra = GA.solve_one(lines[idx], cap_mode="per_relator", max_len=24, max_nodes=8000)
        max_nodes_seen = max(max_nodes_seen, rn["nodes_explored"])
        if rn["solved"] != ra["solved"]:
            problems.append(f"idx {idx}: nrel.solved={rn['solved']} ac.solved={ra['solved']}")
    # unsolvable controls at a tiny budget (neither should solve; both must agree)
    controls = {
        "AK(3)": strs_to_flat("xyxYXY", "xxxYYYY"),
        "Len14#1": strs_to_flat("XyyxYYY", "XyxxyXX"),
    }
    for name, flat in controls.items():
        rn, _ = G.solve_one(flat, 2, max_len=24, max_nodes=100)
        ra = GA.solve_one(flat, cap_mode="per_relator", max_len=24, max_nodes=100)
        if rn["solved"] != ra["solved"]:
            problems.append(f"control {name}: nrel.solved={rn['solved']} ac.solved={ra['solved']}")
        if rn["solved"] or ra["solved"]:
            problems.append(f"control {name} unexpectedly solved at budget 100 "
                            f"(nrel={rn['solved']}, ac={ra['solved']})")
    assert max_nodes_seen > 200, \
        f"agreement sample never exercised a hard search (max nodes {max_nodes_seen})"
    assert not problems, "SOLVED-SET AGREEMENT:\n  " + "\n  ".join(problems[:20])


def test_08_null_revert_block_fires_and_removes_state():
    """The null-revert block must actually FIRE (revert_hits>0) and keep the blocked
    (z-collapsed) canonical state OUT of .visited -- while WITHOUT the block that same state
    IS reachable. Distinguishes a working block from a vacuous no-op."""
    stab_lines = read_lines(os.path.join(STAB, "1190MS_z_r1.txt"), 40)
    problems = []
    fired_any = False
    for flat in stab_lines[:12]:
        rels = G.flat_to_relators(flat, 3, 24)
        nr = G.null_revert_state(flat, 3, 24)
        nr_key = G.state_to_key(G.canonical_tuple(nr))

        s0 = G.NRelatorSolver(rels, 3, max_nodes=4000, max_len=24, track_reverts=True)
        s0.solve()
        reachable_without = nr_key in s0.visited

        s1 = G.NRelatorSolver(rels, 3, max_nodes=4000, max_len=24,
                              blocked_states=[nr], track_reverts=True)
        s1.solve()
        blocked_present = nr_key in s1.visited

        if not reachable_without:
            continue  # this line never reaches the null-revert state; not a useful sample
        if s1.revert_hits <= 0:
            problems.append(f"block did NOT fire (revert_hits={s1.revert_hits}) though state was reachable")
        else:
            fired_any = True
        if blocked_present:
            problems.append("blocked null-revert state STILL appears in .visited with block on")
    assert fired_any, "block never fired on any sampled line -- test is vacuous, cannot trust it"
    assert not problems, "NULL-REVERT BLOCK:\n  " + "\n  ".join(problems[:20])


def test_09_stabilization_contract():
    """stabilize_flat: length 72; first 48 == input; third relator decodes back to the intended
    word w (strip leading z=3, invert the rest, canon-compare to w); round-trip through
    flat_to_relators / relators_to_flat is identity. All four z specs on several dataset lines."""
    lines = read_lines(os.path.join(DATA, "1190MS.txt"), 6)
    problems = []
    for flat in lines:
        r1, r2 = [list(map(int, x)) for x in G.flat_to_relators(flat, 2, 24)]
        expected_w = {"x": [1], "y": [2], "r1": reduce_word(r1), "r2": reduce_word(r2)}
        for spec in ("x", "y", "r1", "r2"):
            stab = S.stabilize_flat(flat, spec)
            if len(stab) != 72:
                problems.append(f"spec {spec}: length {len(stab)} != 72")
                continue
            if list(stab[:48]) != list(flat[:48]):
                problems.append(f"spec {spec}: first 48 ints changed")
            third = [x for x in stab[48:] if x != 0]
            if not third or third[0] != 3:
                problems.append(f"spec {spec}: third relator does not start with z=3: {third}")
                continue
            recovered = inverse_word(third[1:])          # w = inverse(inverse(w))
            if canon_word(recovered) != canon_word(expected_w[spec]):
                problems.append(f"spec {spec}: recovered w {recovered} != expected {expected_w[spec]}")
            # round-trip identity
            rels = S.flat_to_relators(stab, 3, 24)
            flat2 = S.relators_to_flat(rels, 3, 24)
            if list(flat2) != list(stab):
                problems.append(f"spec {spec}: flat<->relators round-trip not identity")
    assert not problems, "STABILIZATION CONTRACT:\n  " + "\n  ".join(problems[:20])


def test_10_persistence_round_trip():
    """serialize_path -> write JSONL -> read back -> deserialize_states -> OUR independent
    replayer accepts it AND it equals the in-memory states array-for-array."""
    os.makedirs(TMPDIR, exist_ok=True)
    fpath = os.path.join(TMPDIR, "paths_roundtrip.jsonl")
    if os.path.exists(fpath):
        os.remove(fpath)
    problems = []
    try:
        lines = read_lines(os.path.join(DATA, "1190MS.txt"), 200)
        wrote = 0
        for idx in [0, 30, 100]:
            res, path = G.solve_one(lines[idx], 2, max_len=24, max_nodes=20000)
            if not res["solved"]:
                continue
            rec = G.serialize_path(path, idx, name=f"ind_{idx}")
            json.dumps(rec)  # must be JSON-serialisable -> a raise here is a finding
            G.write_path_sidecar(fpath, rec)
            wrote += 1
        assert wrote >= 2, "did not produce enough solved paths to round-trip"

        with open(fpath) as f:
            recs = [json.loads(line) for line in f if line.strip()]
        assert len(recs) == wrote, f"JSONL line count {len(recs)} != records written {wrote}"

        for rec in recs:
            idx = rec["idx"]
            states = G.deserialize_states(rec)
            ok, reason = independent_replay(states, 2)
            if not ok:
                problems.append(f"idx {idx}: deserialized path failed independent replay ({reason})")
            # equality vs a fresh in-memory solve of the same idx
            _res, path = G.solve_one(lines[idx], 2, max_len=24, max_nodes=20000)
            mem = path["states"]
            if len(mem) != len(states):
                problems.append(f"idx {idx}: deserialized #states {len(states)} != in-memory {len(mem)}")
                continue
            for a, b in zip(mem, states):
                if not all(np.array_equal(np.asarray(x), np.asarray(y)) for x, y in zip(a, b)):
                    problems.append(f"idx {idx}: deserialized state != in-memory state")
                    break
    finally:
        if os.path.exists(fpath):
            os.remove(fpath)
        try:
            os.rmdir(TMPDIR)
        except OSError:
            pass
    assert not problems, "PERSISTENCE ROUND-TRIP:\n  " + "\n  ".join(problems[:20])


def test_11_misc_adversarial_invariants():
    """(a) no state in .visited exceeds max_len; (b) canonical_tuple is order-independent
    (shuffled relators -> same key); (c) key round-trip state_to_key(key_to_state(k)) == k."""
    problems = []
    # (a) length cap respected across .visited
    lines = read_lines(os.path.join(DATA, "1190MS.txt"), 200)
    for idx in [100, 180]:
        rels = G.flat_to_relators(lines[idx], 2, 24)
        solver = G.NRelatorSolver(rels, 2, max_nodes=6000, max_len=24)
        solver.solve()
        for key in solver.visited:
            st = G.key_to_state(key)
            for r in st:
                if len(r) > 24:
                    problems.append(f"idx {idx}: visited state has relator length {len(r)} > max_len 24")
                    break
    # (b) canonical_tuple order-independence
    for _ in range(50):
        words = [rand_word(6, gens=(1, 2, 3)) for _ in range(3)]
        state = [np.array(w, dtype=np.int64) for w in words]
        base_key = G.state_to_key(G.canonical_tuple(tuple(state)))
        shuf = state[:]
        random.shuffle(shuf)
        shuf_key = G.state_to_key(G.canonical_tuple(tuple(shuf)))
        if base_key != shuf_key:
            problems.append(f"canonical_tuple NOT order-independent for {words}")
    # (c) key round-trip stability
    for _ in range(50):
        words = [rand_word(6, gens=(1, 2, 3)) for _ in range(3)]
        state = tuple(np.array(w, dtype=np.int64) for w in words)
        k = G.state_to_key(G.canonical_tuple(state))
        k2 = G.state_to_key(G.key_to_state(k))
        if k != k2:
            problems.append(f"key round-trip unstable for {words}")
    assert not problems, "MISC INVARIANTS:\n  " + "\n  ".join(problems[:20])


# ======================================================================================
# runner
# ======================================================================================
TESTS = [
    ("01 primitives reduce/inverse", test_01_primitives_reduce_inverse),
    ("02 rotation convention", test_02_rotation_convention),
    ("03 canonical invariance & class", test_03_canonical_invariance_and_class),
    ("04 n=2 move set vs greedy_ac + brute", test_04_n2_moveset_vs_greedy_ac),
    ("05 n=3 move validity vs brute", test_05_n3_move_validity),
    ("06 solve paths replay independently", test_06_solve_paths_replay_independently),
    ("07 solved-set agreement n=2", test_07_solved_set_agreement_n2),
    ("08 null-revert block fires", test_08_null_revert_block_fires_and_removes_state),
    ("09 stabilization contract", test_09_stabilization_contract),
    ("10 persistence round-trip", test_10_persistence_round_trip),
    ("11 misc adversarial invariants", test_11_misc_adversarial_invariants),
]


def main():
    print("=" * 78)
    print("INDEPENDENT black-box adversarial suite for greedy_nrel.py")
    print("=" * 78)
    n_pass = n_fail = n_err = 0
    for name, fn in TESTS:
        t0 = time.time()
        try:
            fn()
            print(f"[PASS] {name:44s} ({time.time()-t0:5.1f}s)")
            n_pass += 1
        except AssertionError as e:
            print(f"[FAIL] {name:44s} ({time.time()-t0:5.1f}s)")
            print("       " + str(e).replace("\n", "\n       "))
            n_fail += 1
        except Exception:
            print(f"[ERROR] {name:43s} ({time.time()-t0:5.1f}s)")
            print("       " + traceback.format_exc().replace("\n", "\n       "))
            n_err += 1
    print("=" * 78)
    print(f"SUMMARY: {n_pass} passed, {n_fail} failed, {n_err} errored, {len(TESTS)} total")
    print("=" * 78)
    return 0 if (n_fail == 0 and n_err == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
