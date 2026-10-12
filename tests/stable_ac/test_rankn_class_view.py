"""Rank-4/5 arms (rankn_bf) and the relabeling-class view (class_view)."""

import json
import math
import os

import numpy as np

from experiments.equivalence_classes.lib import words as L
from experiments.stable_ac.rank3 import class_view as C
from experiments.stable_ac.rank3 import rankn_bf as N
from experiments.stable_ac.rank3 import run_rank3_bf as R
from experiments.stable_ac.solvern import Pres, search_n, word_to_str
from experiments.stable_ac.solvern_fast import search_n_fast

DATA = "data/ms640_solved.txt"
MS640 = R.load_ms640(DATA)


def test_rankn_arms_are_every_multiset_of_the_word_family():
    for rank, (k, m) in N.ARMS.items():
        ws, cs = N.combos(rank)
        assert len(ws) == len(set(ws)) == 3 ** m - 1
        assert len(cs) == len(set(cs)) == math.comb(len(ws) + k - 1, k)
        assert all(len(c) == k and list(c) == sorted(c) and 0 <= c[0] and c[-1] < len(ws)
                   for c in cs)
    assert [len(N.combos(r)[1]) for r in (4, 5)] == [351, 120]


def test_rankn_start_adds_one_generator_and_one_relator_per_word():
    p = N.start((1, 2), (2, -1), [(1,), (2, 2)])
    assert p.n_gen == 4
    assert tuple(p.relators) == ((1, 2), (2, -1), (-3, 1), (-4, 2, 2))
    assert tuple(N.start((1,), (2,), [(), ()]).relators) == ((1,), (2,), (-3,), (-4,))


def test_rankn_null_start_is_the_control_and_a_combo_matches_the_reference():
    for p, r1, r2 in MS640[::160]:
        base = N.triple(search_n_fast(Pres(2, (r1, r2)), N.BUDGET, cap=N.CAP, cyclic=True))
        for rank, (k, _) in N.ARMS.items():
            null = search_n_fast(N.start(r1, r2, [()] * k), N.BUDGET, cap=N.CAP, cyclic=True)
            assert N.triple(null) == base
            ws, cs = N.combos(rank)
            s = N.start(r1, r2, [ws[j] for j in cs[(7 * p + rank) % len(cs)]])
            fast = search_n_fast(s, 300, cap=N.CAP, cyclic=True)
            ref = search_n(s, 300, cap=N.CAP, cyclic=True)
            assert N.triple(fast) == N.triple(ref)


def test_rankn_task_and_merge_store_the_cap_counters(tmp_path, monkeypatch):
    monkeypatch.setattr(N, "OUT", str(tmp_path))
    monkeypatch.setattr(N, "BUDGET", 150)
    os.makedirs(tmp_path / "shards")
    rows = [MS640[0], MS640[320]]
    for row in rows:
        N.task((5,) + tuple(row))
    assert N.merge(5, rows) == []
    stem = os.path.join(str(tmp_path), f"rankn_bf_ms640_b150_cap{N.CAP}_r5")
    with np.load(stem + ".npz") as z:
        caps = np.stack([z[k].astype(np.int64) for k in R.CAP_FIELDS], axis=-1)
        base_cap, null_cap, cs = z["base_cap"], z["null_cap"], z["combos"]
    ws, _ = N.combos(5)
    for i, (p, r1, r2) in enumerate(rows):
        ref = search_n(Pres(2, (r1, r2)), 150, cap=N.CAP, cyclic=True)
        assert tuple(base_cap[i]) == N.counters(ref)
        ref = search_n(N.start(r1, r2, [()] * 3), 150, cap=N.CAP, cyclic=True)
        assert tuple(null_cap[i]) == N.counters(ref)
        for c in range(0, len(cs), 29):
            ref = search_n(N.start(r1, r2, [ws[j] for j in cs[c]]), 150,
                           cap=N.CAP, cyclic=True)
            assert tuple(caps[i, c]) == N.counters(ref)
    with open(stem + "_summary.json") as f:
        assert json.load(f)["null_cap_counter_mismatch_pres_ids"] == []


def test_classes_partition_ms640_and_every_twin_is_that_relabeling():
    ids = [p for p, _, _ in MS640]
    rel = {p: (r1, r2) for p, r1, r2 in MS640}
    cls, twins = C.classes(DATA, ids)
    sizes = np.bincount(cls)
    assert cls.shape == (640,) and sizes.min() >= 1 and len(sizes) == 319
    assert len(twins) == int((sizes * (sizes - 1) // 2).sum())
    imgs = dict(L.SIGNED_PERMS)
    for a, b, name, f in twins:
        pair = (word_to_str(rel[a][0]), word_to_str(rel[a][1]))
        assert a != b and cls[a] == cls[b]
        assert L.apply_pair(pair, imgs[name]) == L.canon_pair(*(word_to_str(r) for r in rel[b]))
        assert L.free_reduce(word_to_str(f(rel[a][0]))) == L.apply_hom(pair[0], imgs[name])


def test_gap_stats_counts_flips_and_relative_node_gaps():
    g = C.gap_stats(np.array([True, True, False, True]), np.array([True, False, False, True]),
                    np.array([10, 3, 0, 8]), np.array([5, 9, 0, 8]))
    assert (g["pairs"], g["solved_flag_differs"], g["both_solved"]) == (4, 1, 2)
    assert g["same_nodes"] == 0.5 and g["gap_median"] == 0.25


def test_start_noise_pairs_a_word_with_its_relabeled_image_only():
    mirror = lambda w: tuple(-g if abs(g) == 2 else g for g in w)
    twins = [(0, 1, "x->x,y->Y", mirror)]
    # x maps to x (kept); y maps to Y, the inverse of a stored word (skipped)
    g = C.start_noise(twins, {0: 0, 1: 1}, [(1,), (2,)],
                      np.array([[4, 9], [6, 2]]), np.ones((2, 2), dtype=bool))
    assert (g["pairs"], g["both_solved"]) == (1, 1)
    assert abs(g["gap_median"] - 2 / 6) < 1e-12


def test_view_counts_per_presentation_and_per_class():
    big = C.BIG
    cls = np.array([0, 0, 1, 1, 2])
    c_solved = np.array([True, False, False, False, True])
    c_nodes = np.array([10, 0, 0, 0, 50], dtype=np.int64)
    best = np.array([big, 5, 7, big, 45])
    v = C.view(cls, c_solved, c_nodes, best, 0.17)
    assert v["presentations"] == {
        "n": 5, "control": 2, "some_start": 3, "gained": 2,
        "gained_but_control_solves_a_copy": 1, "lost": 1, "cheaper": 3,
        "cheaper_beyond_noise": 2, "cheaper_than_every_copy_of_control": 3}
    assert v["classes"] == {"n": 3, "control": 2, "some_start": 3, "gained": 1, "lost": 0,
                            "cheaper": 3}


def test_best_nodes_ignores_unsolved_starts():
    nodes = np.array([[9, 4, 1000], [1000, 1000, 1000]], dtype=np.int64)
    solved = np.array([[True, True, False], [False, False, False]])
    assert C.best_nodes(nodes, solved).tolist() == [4, int(C.BIG)]
