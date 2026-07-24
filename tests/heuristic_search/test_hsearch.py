"""The pluggable-priority solver: the control IS the baseline, and the features read the ring.

The experiment this file guards compares heap orderings at a fixed node budget. That comparison
means nothing unless the control arm is the baseline search itself -- not a reimplementation that
happens to score the same -- so the first test asserts pop-for-pop equality rather than agreement
on the solved flag. Everything else here protects the priority functions from the two ways they
could silently read something other than the presentation: a seam miscount, and a tuple shape that
makes heapq compare an int against a tuple.
"""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from experiments.heuristic_search.hsearch import (  # noqa: E402
    PRIORITIES, blocks, feats, hsearch,
)
from experiments.run_baseline import load_dataset  # noqa: E402
from experiments.search.greedy_baseline import greedy_search  # noqa: E402

MAX_BUDGET = 500          # the local ceiling; never raise it in a test


@pytest.fixture(scope="module")
def bench():
    """The frozen difficulty-stratified benchmark subset -- 20 presentations across 10 bins."""
    with open(os.path.join(ROOT, "results", "benchmark", "subsets",
                           "benchmark_subset_20.json")) as f:
        ids = [r["pres_id"] for r in json.load(f)["subset"]]
    by = {p: (a, b) for p, a, b in load_dataset(os.path.join(ROOT, "data/ms640_solved.txt"))}
    return [(p, *by[p]) for p in ids]


@pytest.mark.parametrize("budget", [100, MAX_BUDGET])
def test_length_priority_is_the_baseline_pop_for_pop(bench, budget):
    """The control gate. Same solved flag AND same nodes_explored on every presentation.

    Scoring the same is not being the same: a subclass that changed the reduction, the cap or the
    tie-break could still tie on this benchmark and would make every reported delta meaningless.
    """
    for pid, r1, r2 in bench:
        a = greedy_search(r1, r2, budget, max_relator_length=24)
        b = hsearch(r1, r2, budget, PRIORITIES["length"], max_relator_length=24)
        assert bool(a["solved"]) == bool(b["solved"]), f"pres {pid} @{budget}"
        assert a["nodes_explored"] == b["nodes_explored"], f"pres {pid} @{budget}"


def test_blocks_close_the_cyclic_seam():
    """A run wrapping the seam is ONE block. Counting it twice would read the canonicaliser's cut."""
    assert blocks("xxyyxx") == ((4,), (2,))          # the two x-runs join around the ring
    assert blocks("xyxy") == ((1, 1), (1, 1))
    assert blocks("xxxx") == ((4,), ())
    assert blocks("") == ((), ())
    # Inverses are the same generator for block purposes -- X and x cannot start a new block.
    assert blocks("xXxX") == ((4,), ())


def test_block_features_are_rotation_invariant():
    """Every priority is a function of feats(); if feats() moved under rotation, so would the search.

    Rotation permutes the ORDER of the run lengths (``YYYXyyx`` rotated by 3 reads its y-runs as
    2,3 instead of 3,2) but not the multiset. Only the multiset is asserted here, because that is
    the whole of what the features consume -- counts and means, both order-insensitive. Asserting
    tuple equality instead would fail on correct code, and the fix would be to weaken the feature.
    """
    for w in ("YYYXyyx", "YXYxyx", "YYYYxxx", "xxyYXyx"):
        bx, byy = blocks(w)
        base = (sorted(bx), sorted(byy))
        for k in range(1, len(w)):
            rx, ry = blocks(w[k:] + w[:k])
            assert (sorted(rx), sorted(ry)) == base, f"{w} rotated by {k}"


def test_feats_is_exactly_rotation_invariant():
    """The priorities read feats(), so this is the invariance that actually binds the search."""
    for r1, r2 in (("X", "YYYXyyx"), ("YXYxyx", "YYYYxxx"), ("YYYXyyX", "YXXXyxx")):
        base = feats(r1, r2)
        for k in range(1, len(r2)):
            assert feats(r1, r2[k:] + r2[:k]) == base, f"{r2} rotated by {k}"


def test_knot_and_block_features_match_the_clustering_definitions():
    """hsearch recomputes the features for speed -- they must not drift from the analysis code."""
    from experiments.clustering.features import knot_number
    from experiments.clustering.rank_signals import candidates
    for r1, r2 in (("X", "YYYXyyx"), ("YXYxyx", "YYYYxxx"), ("YYYXyyX", "YXXXyxx")):
        L, K, MK, S = feats(r1, r2)
        assert L == len(r1) + len(r2)
        assert K == knot_number(r1) + knot_number(r2)
        assert MK == max(knot_number(r1), knot_number(r2))
        assert S == pytest.approx(candidates(r1, r2)["smaller mean block"])


def test_every_priority_returns_heap_comparable_keys(bench):
    """Mixed tuple shapes must never make heapq compare an int against a tuple.

    The endgame priorities emit (0, L) below the threshold and (1, ...) above it, so the leading
    int is what keeps the two branches orderable. This exercises each priority on states of both
    kinds and sorts the results, which is exactly what the heap does.
    """
    states = [(r1, r2) for _, r1, r2 in bench] + [("x", "y"), ("X", "YYYXyyx")]
    for name, p in PRIORITIES.items():
        keys = [p(r1, r2) for r1, r2 in states]
        sorted(keys)                                   # raises TypeError if shapes are incomparable
        assert all(k is not None for k in keys), name


@pytest.mark.parametrize("name", ["knots_first", "smb_first", "length+2.0*knots",
                                  "knots_first@endgame10"])
def test_alternative_priorities_run_and_stay_within_budget(bench, name):
    for pid, r1, r2 in bench[:6]:
        r = hsearch(r1, r2, 200, PRIORITIES[name], max_relator_length=24)
        assert r["nodes_explored"] <= 200, f"{name} overran the budget on pres {pid}"
        if r["solved"]:
            assert r["path_length"] >= 1


def test_endgame_threshold_reverts_to_pure_length_when_short():
    """Below T the ordering must be length alone, or the 'endgame' name is a lie."""
    p = PRIORITIES["knots_first@endgame10"]
    short_a, short_b = p("x", "y"), p("X", "YYYXyy")          # totals 2 and 7, both <= 10
    assert short_a[0] == 0 and short_b[0] == 0
    assert short_a < short_b                                   # ordered purely by total length
    long_key = p("YYYXyyX", "YXXXyxx")                         # total 14 > 10
    assert long_key[0] == 1
    assert short_b < long_key, "every endgame state must outrank every opening state"


# ------------------------------------------------------------------- the tuned multi-feature arm

TUNED = (8.0, 6.23, 0.84, 8.33)      # T, a_knots, a_maxknots, a_smb -- from tune_multi on subset-60


@pytest.fixture(scope="module")
def bench60():
    from experiments.heuristic_search.run_sweep import load, subset_ids
    return load(subset_ids(60))


def test_baseline_params_reproduce_the_length_ordering(bench60):
    """The tuner's zero vector must BE the control, or the search space cannot express 'no change'.

    A weight space that cannot return the baseline will always appear to beat it, so this is the
    tuning equivalent of the control gate above.
    """
    from experiments.heuristic_search.tune_multi import BASELINE, make_priority
    p = make_priority(BASELINE)
    for pid, r1, r2 in bench60[:8]:
        a = greedy_search(r1, r2, 100, max_relator_length=24)
        b = hsearch(r1, r2, 100, p, max_relator_length=24)
        assert bool(a["solved"]) == bool(b["solved"]), f"pres {pid}"
        assert a["nodes_explored"] == b["nodes_explored"], f"pres {pid}"


@pytest.mark.slow
def test_tuned_solution_paths_are_real_move_chains(bench60):
    """Every returned path must be a chain of legal S-moves ending at the trivial state.

    A heap ordering cannot invent a solution -- but a bug in the re-stated solve loop could return
    a path that skips an edge, and the solve rate is the headline number here. This regenerates the
    neighbour set at each step and requires the next state to be in it.
    """
    from experiments.heuristic_search.hsearch import HeuristicSolver
    from experiments.heuristic_search.tune_multi import make_priority
    from experiments.search.greedy_baseline import (
        canonical_pair_nj, get_neighbors_with_moves_nj, reduce_relator_nj, state_to_key,
        str_to_arr,
    )
    checked = 0
    for pid, r1, r2 in bench60:
        s = HeuristicSolver(r1, r2, priority=make_priority(TUNED), max_nodes=100,
                            max_relator_length=24)
        path, _, _, _ = s.solve()
        if path is None:
            continue
        checked += 1
        assert len(path[-1][0]) == 1 and len(path[-1][1]) == 1, f"pres {pid} ends untrivial"
        for a, b in zip(path, path[1:]):
            kids = set()
            for nr1, nr2, *_ in get_neighbors_with_moves_nj(str_to_arr(a[0]), str_to_arr(a[1])):
                x, y = reduce_relator_nj(nr1, True), reduce_relator_nj(nr2, True)
                if len(x) <= 24 and len(y) <= 24:
                    kids.add(state_to_key(canonical_pair_nj(x, y)))
            assert b in kids, f"pres {pid}: {a} -> {b} is not a legal move"
    assert checked >= 25, f"only {checked} solved paths checked -- the guard would be vacuous"


@pytest.mark.slow
def test_tuned_arm_beats_the_baseline_on_subset_60_and_never_loses(bench60):
    """Regression pin on the headline: 17/60 -> 30/60 at budget 100, with no presentation lost.

    'Never loses' is the part worth pinning -- a net gain can hide churn, and an ordering that
    trades solves is a different (and much weaker) claim than one that strictly dominates.
    """
    from experiments.heuristic_search.tune_multi import BASELINE, make_priority
    base, tuned = [], []
    for pid, r1, r2 in bench60:
        base.append(hsearch(r1, r2, 100, make_priority(BASELINE), max_relator_length=24)["solved"])
        tuned.append(hsearch(r1, r2, 100, make_priority(TUNED), max_relator_length=24)["solved"])
    lost = [i for i in range(len(base)) if base[i] and not tuned[i]]
    assert sum(base) == 17, f"baseline moved: {sum(base)}/60 -- diagnose before regenerating"
    assert sum(tuned) >= 28, f"tuned arm fell to {sum(tuned)}/60"
    assert not lost, f"tuned arm lost presentations {lost} the baseline solved"
