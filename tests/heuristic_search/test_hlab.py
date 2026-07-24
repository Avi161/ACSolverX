"""The gate every number in the hyperparameter program stands on.

Two separate claims, and the program is uninterpretable without both:

  * the **baseline config** is the baseline search -- same solved flag and same ``nodes_explored``
    as ``greedy_search``, presentation by presentation, at **every cap the program uses**. Raising
    ``max_relator_length`` changes the baseline itself, so a gate run only at 24 would say nothing
    about the runs at 48 or 64 where the actual research happens.
  * the **features** agree with the ones already shipped and analysed in ``hsearch.py`` /
    ``experiments/clustering``. ``hlab.phi`` recomputes them in a single pass for speed; if that
    pass drifted, every configuration built on it would be optimising a different quantity than
    the one the clustering work found signal in, and nothing downstream would mean what it says.

Everything else here guards the two ways a config can silently stop being a valid heap key: a
segment structure that leaves a state uncovered, and mixed tuple shapes that make heapq compare
incomparable things mid-search.
"""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from experiments.heuristic_search.hlab import (  # noqa: E402
    BASELINE_CONFIG, FEATURES, LabSolver, bench66, cfg_name, load_split,
    make_priority, phi, run_one, word_stats,
)
from experiments.heuristic_search.hsearch import feats  # noqa: E402
from experiments.search.greedy_baseline import greedy_search  # noqa: E402

MAX_BUDGET = 500          # the local ceiling for a test; the research runs go to 1,000


@pytest.fixture(scope="module")
def rows():
    return bench66()


@pytest.fixture(scope="module")
def sample(rows):
    """A spread of the benchmark: easy, hard, and genuinely-unsolved."""
    lad = [r for r in rows if r["source"] == "ladder"]
    return lad[:4] + lad[-4:] + [r for r in rows if r["source"] == "reach"][:2]


# ------------------------------------------------------------------- gate (a): control parity

@pytest.mark.parametrize("mrl", [24, 48, 64])
@pytest.mark.parametrize("budget", [100, MAX_BUDGET])
def test_baseline_config_is_the_baseline_search_pop_for_pop(sample, mrl, budget):
    """At every cap the program uses. A control that merely ties is not the same search."""
    p = make_priority(BASELINE_CONFIG)
    for r in sample:
        a = greedy_search(r["r1"], r["r2"], budget, max_relator_length=mrl)
        b = run_one(r["r1"], r["r2"], budget, p, mrl)
        assert bool(a["solved"]) == bool(b["solved"]), f"{r['name']} mrl{mrl} @{budget}"
        assert a["nodes_explored"] == b["nodes"], f"{r['name']} mrl{mrl} @{budget}"


@pytest.mark.parametrize("mrl", [24, 64])
def test_min_total_matches_the_baselines_min_relator_length(sample, mrl):
    """``min_total`` is the progress metric for the open problems -- it must be the repo's own.

    ``greedy_baseline`` reports ``min_relator_length`` as the SUM of the pair (line 931), not the
    shorter relator. Scoring the reach rows against ``bar_to_beat`` with any other quantity would
    compare against a bar that was never set for it.
    """
    p = make_priority(BASELINE_CONFIG)
    for r in sample:
        a = greedy_search(r["r1"], r["r2"], 200, max_relator_length=mrl)
        b = run_one(r["r1"], r["r2"], 200, p, mrl)
        assert a["min_relator_length"] == b["min_total"], f"{r['name']} mrl{mrl}"


# ------------------------------------------------------------------- gate (b): feature parity

def test_phi_agrees_with_the_shipped_feats_on_every_benchmark_state(rows):
    """The four features hsearch.py shipped must be bit-identical here, on real states."""
    for r in rows:
        f = phi(r["r1"], r["r2"])
        L, K, MK, S = feats(r["r1"], r["r2"])
        assert f[FEATURES.index("L")] == L, r["name"]
        assert f[FEATURES.index("K")] == K, r["name"]
        assert f[FEATURES.index("MK")] == MK, r["name"]
        assert f[FEATURES.index("S")] == pytest.approx(S), r["name"]


def test_phi_agrees_with_the_clustering_definitions():
    """The features were chosen by the clustering analysis; they must still be those features."""
    from experiments.clustering.features import knot_number
    for r1, r2 in (("X", "YYYXyyx"), ("YXYxyx", "YYYYxxx"), ("YYYXyyX", "YXXXyxx")):
        f = phi(r1, r2)
        assert f[FEATURES.index("K")] == knot_number(r1) + knot_number(r2)
        assert f[FEATURES.index("MK")] == max(knot_number(r1), knot_number(r2))


def test_word_stats_closes_the_cyclic_seam():
    """A run wrapping the ring is ONE block; two would let the key read the canonicaliser's cut."""
    assert word_stats("xxyyxx")[1:3] == (1, 1)        # x-runs join across the seam
    assert word_stats("xxyyxx")[3] == (4,)
    assert word_stats("xyxy")[1:3] == (2, 2)
    assert word_stats("xxxx")[1:3] == (1, 0)
    assert word_stats("xXxX")[1:3] == (1, 0)          # X and x are the same generator
    assert word_stats("")[1:3] == (0, 0)


def test_phi_is_exactly_rotation_invariant(rows):
    """A relator is a ring. If phi moved under rotation it would be scoring the seam position."""
    for r in rows[:12]:
        r1, r2 = r["r1"], r["r2"]
        base = phi(r1, r2)
        for k in range(1, len(r2)):
            assert phi(r1, r2[k:] + r2[:k]) == base, f"{r['name']} rotated by {k}"


def test_pure_powers_have_zero_knots():
    """A word in one generator has no knots at all -- not one. The clustering work fixed this once."""
    assert phi("xxxx", "yyy")[FEATURES.index("K")] == 0.0
    assert phi("xxxx", "yyy")[FEATURES.index("MK")] == 0.0


# ------------------------------------------------------------------------- key well-formedness

def test_every_segmented_config_returns_heap_comparable_keys(rows):
    """Mixed shapes across segments must never make heapq compare an int against a tuple."""
    cfgs = [
        BASELINE_CONFIG,
        {"segments": [{"upto": 16, "w": {"L": 1.0}}, {"upto": None, "w": {"K": 4.0, "L": 1.0}}]},
        {"segments": [{"upto": 8, "w": {"L": 1.0}}, {"upto": 20, "w": {"S": 2.0}},
                      {"upto": None, "w": {f: 1.0 for f in FEATURES}}]},
        {"segments": [{"upto": 4, "w": {"L": 1.0}}]},          # deliberately covers almost nothing
    ]
    states = [(r["r1"], r["r2"]) for r in rows] + [("x", "y")]
    for cfg in cfgs:
        p = make_priority(cfg)
        keys = [p(a, b) for a, b in states]
        sorted(keys)                       # raises TypeError if the shapes are incomparable
        assert all(isinstance(k[0], int) for k in keys), cfg_name(cfg)


def test_a_config_whose_segments_do_not_cover_a_state_still_orders_it(rows):
    """The fall-through bucket exists so an under-specified config degrades, never crashes."""
    p = make_priority({"segments": [{"upto": 4, "w": {"L": 1.0}}]})
    long_key = p("YYYXyyX", "YXXXyxx")                 # total 14, past the only segment
    short_key = p("x", "y")                            # total 2, inside it
    assert short_key[0] == 0 and long_key[0] == 1
    assert short_key < long_key


def test_segment_index_dominates_the_score(rows):
    """Every state in an earlier segment must outrank every state in a later one, whatever the
    weights say. That domination IS the endgame semantics -- without it a huge score in segment 0
    could outrank a small one in segment 1 and the threshold would mean nothing."""
    p = make_priority({"segments": [{"upto": 12, "w": {"L": 1e9}},
                                    {"upto": None, "w": {"L": 1.0}}]})
    inside = p("YYYXyy", "Yx")                          # total 8 -> segment 0, enormous score
    outside = p("YYYXyyX", "YXXXyxx")                   # total 14 -> segment 1, tiny score
    assert inside[1] > outside[1]
    assert inside < outside


def test_known_orderings_are_points_in_the_config_space(sample):
    """The tuner can only return something already known to work if the space contains it."""
    from experiments.heuristic_search.hsearch import PRIORITIES, hsearch
    knots_first = {"segments": [{"upto": None, "w": {"K": 1e6, "L": 1.0}}]}
    p = make_priority(knots_first)
    for r in sample[:5]:
        a = hsearch(r["r1"], r["r2"], 200, PRIORITIES["knots_first"], max_relator_length=24)
        b = run_one(r["r1"], r["r2"], 200, p, 24)
        assert bool(a["solved"]) == bool(b["solved"]), r["name"]
        assert a["nodes_explored"] == b["nodes"], r["name"]


# ------------------------------------------------------------------------------ the split file

def test_the_frozen_split_is_a_partition_and_stays_frozen():
    """train/test/reach must tile the 66 exactly. A drifting split invalidates every held-out
    number reported against it, silently and after the fact."""
    with open(os.path.join(ROOT, "tests", "heuristic_search", "logs", "splits.json")) as f:
        sp = json.load(f)
    names = {r["name"] for r in bench66()}
    tr, te, re_ = set(sp["train"]), set(sp["test"]), set(sp["reach"])
    assert len(tr) == 40 and len(te) == 20 and len(re_) == 6
    assert not (tr & te) and not (tr & re_) and not (te & re_)
    assert tr | te | re_ == names


def test_the_split_is_stratified_across_every_difficulty_bin():
    """4 train / 2 test in each of the 10 bins -- so neither side is handed the easy problems."""
    by = {r["name"]: r for r in bench66()}
    tr, te = load_split("train"), load_split("test")
    for b in range(10):
        assert sum(1 for r in tr if by[r["name"]]["bin"] == b) == 4, f"bin {b} train"
        assert sum(1 for r in te if by[r["name"]]["bin"] == b) == 2, f"bin {b} test"
