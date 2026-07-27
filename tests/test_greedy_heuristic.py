"""The pluggable-priority greedy: the control IS the baseline, and the features read the ring.

What this file guards, in order of how much it would cost to get wrong:

1. **The control gate.** ``greedy_search_h(config=None)`` must reproduce ``greedy_search`` *pop for
   pop* — same ``solved`` flag AND same ``nodes_explored`` on every presentation, at every budget.
   Agreeing on the solved flag is not enough: a subclass that changed the reduction, the cap or the
   heap tie-break could still tie on this benchmark, and every reported delta would then be
   measuring that change instead of the ordering. No other number here is interpretable if this
   fails.
2. **The drop-in contract.** The returned dict must be ``greedy_search``'s, key for key — a missing
   key surfaces only when a result row is written, i.e. hours into a run.
3. **The certificate.** A solved path is stored as Definition 2.1 moves and must replay, from the
   start presentation, to a trivial state. Replay is the only decoder: the move inverts the *other*
   relator, so diffing consecutive states misreads it.
4. **The features.** The two ways they could silently read something other than the presentation
   are a miscounted cyclic seam and a heap key whose branches are not comparable.

Node budgets never exceed ``MAX_BUDGET = 1000``. A search at budget ``B`` is exactly the first ``B``
pops of any longer search, so a bigger budget buys a slower test, never different behaviour.
"""
import ast
import os

import pytest

from experiments.search.greedy_baseline import greedy_search, moves_to_states, str_to_move
from experiments.search.heuristics import (
    BASELINE_CONFIG, FEATURES, LEAN_SMALL_BUDGET, RECOMMENDED, cfg_name, greedy_search_h,
    make_priority, phi, word_stats,
)

MAX_BUDGET = 1000          # the ceiling; never raise it in a test
MAX_RELATOR_LENGTH = 24    # the layout of data/ms640_solved.txt (48 ints per line)

# Twenty presentations of ms640, two from each of ten difficulty bins (binned by the node count a
# 10^6-node baseline run needed). Stratified rather than sampled, so the easy rows — where every
# ordering ties because the search ends in single digits — cannot dominate the comparison.
BENCH = (0, 455, 77, 505, 247, 344, 203, 380, 546, 537,
         538, 565, 602, 581, 568, 633, 605, 623, 634, 636)

_INT_TO_CHAR = {1: 'x', -1: 'X', 2: 'y', -2: 'Y'}
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@pytest.fixture(scope="module")
def bench():
    """``[(pres_id, r1, r2)]`` — each ms640 line is 48 ints, ``[r1(24) | r2(24)]``, 0 = pad."""
    with open(os.path.join(_ROOT, "data", "ms640_solved.txt")) as f:
        lines = [ast.literal_eval(ln.strip()) for ln in f if ln.strip()]
    out = []
    for pid in BENCH:
        ints = lines[pid]
        half = len(ints) // 2
        out.append((pid,
                    ''.join(_INT_TO_CHAR[t] for t in ints[:half] if t != 0),
                    ''.join(_INT_TO_CHAR[t] for t in ints[half:] if t != 0)))
    return out


_RUNS = {}


def _run(bench, config, budget, tag):
    """Every arm runs once per module; the search is deterministic, so caching is free.

    Keyed on ``(tag, budget)``, not ``tag`` alone: a later test that reuses a tag at a different
    budget would otherwise be handed the first budget's rows without anything raising.
    """
    if (tag, budget) not in _RUNS:
        _RUNS[(tag, budget)] = {pid: greedy_search_h(r1, r2, budget,
                                                     max_relator_length=MAX_RELATOR_LENGTH,
                                                     config=config)
                                for pid, r1, r2 in bench}
    return _RUNS[(tag, budget)]


# ------------------------------------------------------------------------------ 1. control gate

@pytest.mark.parametrize("budget", [100, MAX_BUDGET])
def test_length_config_is_the_baseline_pop_for_pop(bench, budget):
    """``config=None`` is not a search that scores like the baseline — it IS the baseline search."""
    for pid, r1, r2 in bench:
        a = greedy_search(r1, r2, budget, max_relator_length=MAX_RELATOR_LENGTH)
        b = greedy_search_h(r1, r2, budget, max_relator_length=MAX_RELATOR_LENGTH, config=None)
        assert bool(a["solved"]) == bool(b["solved"]), f"pres {pid} @{budget}"
        assert a["nodes_explored"] == b["nodes_explored"], f"pres {pid} @{budget}"
        assert a["path_length"] == b["path_length"], f"pres {pid} @{budget}"


def test_explicit_baseline_config_is_the_same_search(bench):
    """The all-length weight vector is inside the config space on purpose.

    A tuner whose space cannot express "no change" will always appear to beat its control.
    """
    for pid, r1, r2 in bench:
        a = greedy_search(r1, r2, 100, max_relator_length=MAX_RELATOR_LENGTH)
        b = greedy_search_h(r1, r2, 100, max_relator_length=MAX_RELATOR_LENGTH,
                            config=BASELINE_CONFIG)
        assert (bool(a["solved"]), a["nodes_explored"]) == \
               (bool(b["solved"]), b["nodes_explored"]), f"pres {pid}"


# --------------------------------------------------------------------------- 2. drop-in contract

def test_returns_exactly_the_baseline_dict(bench):
    """Same keys, same order, same types — on a solved row and on an unsolved one."""
    for pid, r1, r2 in [bench[0], bench[-1]]:
        a = greedy_search(r1, r2, 100, max_relator_length=MAX_RELATOR_LENGTH)
        b = greedy_search_h(r1, r2, 100, max_relator_length=MAX_RELATOR_LENGTH,
                            config=RECOMMENDED)
        assert list(a.keys()) == list(b.keys()), f"pres {pid}"
        for k in a:
            assert type(a[k]) is type(b[k]), f"pres {pid}, key {k}"


def test_unsolved_row_reports_no_certificate(bench):
    """An unsolved search must not claim a path; ``nodes_explored`` is the full budget."""
    pid, r1, r2 = bench[-1]                      # bin 9: unsolved far above this budget
    st = greedy_search_h(r1, r2, MAX_BUDGET, max_relator_length=MAX_RELATOR_LENGTH,
                         config=RECOMMENDED)
    assert st["solved"] is False and st["nodes_explored"] == MAX_BUDGET
    assert st["path"] == [] and st["path_moves"] == [] and st["path_length"] is None


# -------------------------------------------------------------------------------- 3. certificate

def test_every_solved_path_replays_to_a_trivial_state(bench):
    """Replay the stored moves from the start presentation; never diff consecutive states."""
    runs = _run(bench, RECOMMENDED, MAX_BUDGET, "rec")
    solved = [(pid, r1, r2) for pid, r1, r2 in bench if runs[pid]["solved"]]
    assert solved, "no solved row to verify — the benchmark or the budget changed"
    for pid, r1, r2 in solved:
        st = runs[pid]
        moves = [str_to_move(m) for m in st["path_moves"]]
        replayed = moves_to_states(r1, r2, moves)
        assert replayed == st["path"], f"pres {pid}: replay diverged from the reported path"
        assert len(st["path_moves"]) == st["path_length"] == len(st["path"]) - 1, f"pres {pid}"
        end = st["path"][-1]
        assert len(end[0]) == 1 and len(end[1]) == 1, f"pres {pid}: path does not end trivial"


# ------------------------------------------------------------------- the result the PR claims

@pytest.mark.parametrize("name,config", [("recommended", RECOMMENDED),
                                         ("lean", LEAN_SMALL_BUDGET)])
def test_preset_solves_a_superset_of_the_baseline(bench, name, config):
    """Strictly more presentations, and not one traded away.

    "More solved" alone would permit an ordering that wins two rows and loses two others; the
    superset assertion is what makes the headline a monotone improvement rather than a reshuffle.

    This is a **regression pin, not held-out validation**. Fourteen of these twenty rows are in the
    difficulty-stratified slice the shipped weights were selected on, so a green run says the
    presets still do what they did — it does not say they generalise. Read the green as "nothing
    regressed", and see HEURISTICS.md for the four-row held-out reading (1 -> 3).
    """
    base = _run(bench, None, MAX_BUDGET, "base")
    arm = _run(bench, config, MAX_BUDGET, name)
    lost = [p for p in base if base[p]["solved"] and not arm[p]["solved"]]
    assert not lost, f"{name} lost presentations the baseline solved: {lost}"
    assert sum(r["solved"] for r in arm.values()) > sum(r["solved"] for r in base.values())


def test_recommended_costs_no_more_nodes_where_both_solve(bench):
    """Compare nodes as a MEAN over the both-solved set, never as a sum.

    Each arm's both-solved set has its own size, so a sum ranks an arm that solves fewer
    presentations as the cheaper one.
    """
    base = _run(bench, None, MAX_BUDGET, "base")
    arm = _run(bench, RECOMMENDED, MAX_BUDGET, "rec")
    both = [p for p in base if base[p]["solved"] and arm[p]["solved"]]
    assert len(both) >= 5
    mean_base = sum(base[p]["nodes_explored"] for p in both) / len(both)
    mean_arm = sum(arm[p]["nodes_explored"] for p in both) / len(both)
    assert mean_arm <= mean_base


# ----------------------------------------------------------------------------------- 4. features

def test_word_stats_closes_the_cyclic_seam():
    """A run wrapping the seam is ONE block. Counting it twice would read the canonicaliser's cut."""
    assert word_stats("xxyyxx")[3:5] == ((4,), (2,))      # the two x-runs join around the ring
    assert word_stats("xyxy")[3:5] == ((1, 1), (1, 1))
    assert word_stats("xxxx")[3:5] == ((4,), ())          # a pure power: one block, no y-blocks
    assert word_stats("")[3:5] == ((), ())
    # A letter and its inverse are the same GENERATOR: X cannot start a new block after x.
    assert word_stats("xXxX")[3:5] == ((4,), ())


def test_phi_is_rotation_invariant():
    """Every feature reads the relator as a ring, so a rotation must not move the priority."""
    r1, r2 = "xxyXYy", "xyXYxy"
    base = phi(r1, r2)
    for k in range(1, len(r1)):
        assert phi(r1[k:] + r1[:k], r2) == base, f"rotation by {k} moved the feature vector"


def test_phi_hand_checked():
    """A worked example, so a refactor that shifts a feature index is caught by value, not shape."""
    f = dict(zip(FEATURES, phi("xxyy", "xy")))
    assert f["L"] == 6 and f["Lmin"] == 2 and f["Lmax"] == 4 and f["imbal"] == 2
    # xxyy -> one x-block and one y-block => 1 knot; xy -> likewise 1 knot.
    assert f["K"] == 2 and f["MK"] == 1 and f["mK"] == 1
    # x-runs (2, 1) mean 1.5; y-runs (2, 1) mean 1.5 -> both means equal.
    assert f["S"] == 1.5 and f["Bmax"] == 1.5
    assert f["nb"] == 4 and f["B1"] == 2 and f["Bmin"] == 1 and f["Bmaxrun"] == 2
    assert f["xyimb"] == 0.0                       # three x letters, three y letters
    # A pure power has no knots at all: one generator simply does not appear.
    assert dict(zip(FEATURES, phi("xxxx", "xy")))["K"] == 1


def test_every_feature_is_addressable_as_a_weight():
    """A name in FEATURES that no config can reference is a feature that silently does nothing."""
    for name in FEATURES:
        key = make_priority({"segments": [{"upto": None, "w": {name: 1.0}}]})("xxyy", "xy")
        assert key[0] == 0 and isinstance(key[1], float)


def test_priority_keys_stay_comparable_across_segments():
    """The leading segment index is load-bearing twice over.

    It makes every state below the boundary outrank every state above it — the endgame switch —
    and it keeps two segments' scores, which are on unrelated scales, from ever being compared.
    """
    p = make_priority(LEAN_SMALL_BUDGET)              # boundary at total length 16
    short = p("xxyy", "xy")                           # L = 6  -> segment 0
    long_ = p("xxyyxxyyxxyy", "xyxyxyxy")             # L = 20 -> segment 1
    assert short[0] == 0 and long_[0] == 1
    assert short < long_                              # int-vs-int first: heapq never raises here
    assert isinstance(short[0], int) and isinstance(long_[0], int)


def test_cfg_name_is_stable_under_dict_order():
    """The label is a log id, so it must not depend on the order the weights were written in."""
    a = {"segments": [{"upto": None, "w": {"L": 1.0, "K": 2.0}}]}
    b = {"segments": [{"upto": None, "w": {"K": 2.0, "L": 1.0}}]}
    assert cfg_name(a) == cfg_name(b)
    assert cfg_name(None) == cfg_name(BASELINE_CONFIG)
