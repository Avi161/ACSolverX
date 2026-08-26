"""The pluggable-priority greedy: the control IS the baseline, and the features read the ring.

What this file guards, in order of how much it would cost to get wrong:

1. **The control gate.** ``config=None`` must reproduce ``greedy_search`` *pop for pop* — same
   ``solved`` flag AND same ``nodes_explored``. No other number here is interpretable if it fails.
2. **The drop-in contract.** The returned dict is ``greedy_search``'s, key for key.
3. **The certificate.** A solved path is stored as Definition 2.1 moves and must replay to a trivial
   state; the move inverts the *other* relator, so diffing consecutive states misreads it.
4. **The features.** The two ways they could read something other than the presentation are a
   miscounted cyclic seam and a heap key whose branches are not comparable.

Node budgets never exceed ``MAX_BUDGET = 1000``: a search at budget ``B`` is exactly the first ``B``
pops of any longer search, so a bigger budget buys a slower test, never different behaviour.
"""
import ast
import csv
import json
import os

import pytest

from experiments.search.greedy_baseline import greedy_search, moves_to_states, str_to_move
from experiments.search.heuristics import (
    BASELINE_CONFIG, FEATURES, S20_MK2, greedy_search_h, make_priority, phi, word_stats,
)

# A non-baseline config for the machinery tests below — deliberately NOT a recommendation, just
# unit weights on three features, so a drop-in/certificate test cannot be read as endorsing an
# ordering. Tests that mean the production ordering say S20_MK2.
PROBE_CONFIG = {"segments": [{"upto": None, "w": {"L": 1.0, "S": 1.0, "MK": 1.0}}]}

# The vector withdrawn as overfit. Held here as a literal ONLY so the guard below can assert it is
# gone from the module, and so the arms tables can be pinned to the weights that produced their
# heur_* columns. Nothing in the package defines it; do not reintroduce it there.
WITHDRAWN_WEIGHTS = {"L": 1.0, "K": 2.53, "MK": 6.418, "S": 8.458, "xyimb": 3.292}

MAX_BUDGET = 1000          # the ceiling; never raise it in a test
MAX_RELATOR_LENGTH = 24    # the layout of data/ms640_solved.txt (48 ints per line)

# These twenty ids are `benchmark/subsets/benchmark_subset_20.json`, verbatim and in file order —
# inlined rather than loaded so that what CI measures cannot change when that file does, and pinned
# against it by `test_bench_ids_are_the_shipped_subset_20`. How it was built, so the list can be
# audited rather than trusted: line numbers of `data/ms640_solved.txt`, binned into ten equal-width
# slices of log10(nodes_explored) for a 10^6-node baseline run (each bin 3.37x the one below), two
# rows per bin, picked to minimise Aut(F2)-equivalent pairs and then spread evenly over path length.
# Stratified rather than sampled, so the easy rows — where every ordering ties because the search
# ends in single digits — cannot dominate the comparison.
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
                            config=PROBE_CONFIG)
        assert list(a.keys()) == list(b.keys()), f"pres {pid}"
        for k in a:
            assert type(a[k]) is type(b[k]), f"pres {pid}, key {k}"


def test_unsolved_row_reports_no_certificate(bench):
    """An unsolved search must not claim a path; ``nodes_explored`` is the full budget."""
    pid, r1, r2 = bench[-1]                      # bin 9: unsolved far above this budget
    st = greedy_search_h(r1, r2, MAX_BUDGET, max_relator_length=MAX_RELATOR_LENGTH,
                         config=PROBE_CONFIG)
    assert st["solved"] is False and st["nodes_explored"] == MAX_BUDGET
    assert st["path"] == [] and st["path_moves"] == [] and st["path_length"] is None


# -------------------------------------------------------------------------------- 3. certificate

def test_every_solved_path_replays_to_a_trivial_state(bench):
    """Replay the stored moves from the start presentation; never diff consecutive states."""
    runs = _run(bench, S20_MK2, MAX_BUDGET, "s20mk2")
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


# ------------------------------------------------------- the guard against a tuned vector returning

def test_module_ships_no_overfit_weight_vector():
    """The withdrawn vector must not come back — under its old name or any new one.

    Two assertions rather than one, because a rename is the likely way it returns. The first pins
    the name gone; the second pins the *weights* gone, so re-landing them as ``BEST`` or ``TUNED``
    fails too.

    Deleted with it were two tests that asserted the shipped ordering solved a superset of the
    baseline and cost no more nodes on these twenty rows. Both were green and both were circular:
    fourteen of the twenty are in the slice that vector was tuned on, so they restated the tuning
    objective. A benchmark an ordering was fitted on cannot also validate it.
    """
    import experiments.search.heuristics as mod

    assert not hasattr(mod, "RECOMMENDED"), \
        "RECOMMENDED was withdrawn as overfit; do not reintroduce it"

    for name in dir(mod):
        cfg = getattr(mod, name)
        if not (isinstance(cfg, dict) and "segments" in cfg):
            continue
        for seg in cfg["segments"]:
            assert seg.get("w") != WITHDRAWN_WEIGHTS, \
                f"{name} is the withdrawn overfit vector under a new name"


def test_shipped_ordering_is_a_pure_function_of_the_state(bench):
    """S20_MK2 must score a state identically however the state was reached.

    This is the invariant that survives the deleted benchmark assertions, and it is the one worth
    testing: the visited set dedups on first discovery and there is no decrease-key, so a priority
    reading anything but the state would make pop order depend on discovery order.
    """
    prio = make_priority(S20_MK2)
    for _pid, r1, r2 in bench[:5]:
        assert prio(r1, r2) == prio(r1, r2)
        assert prio(r1, r2)[0] == 0                     # one segment, so always index 0


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


def test_shipped_config_is_the_formula_the_docs_publish():
    """HEURISTICS.md and ARMS.md publish `L + 20*S + 2*MK`. Pin it, so doc and code cannot drift.

    A doc describing an ordering nothing runs is worse than no doc: every number downstream is then
    attributed to a formula that was never executed.
    """
    assert S20_MK2 == {"segments": [{"upto": None, "w": {
        "L": 1.0, "S": 20.0, "MK": 2.0}}]}


def test_bench_ids_are_the_shipped_subset_20():
    """`BENCH` claims to be `benchmark_subset_20.json` in file order. Hold it to that.

    Inlined rather than loaded on purpose — CI must measure a fixed row list — so the claim needs a
    pin, or the comment above `BENCH` slowly becomes fiction. Missing file is a failure, not a skip.
    """
    with open(os.path.join(_ROOT, "benchmark", "subsets", "benchmark_subset_20.json")) as f:
        subset = json.load(f)["subset"]
    assert tuple(r["pres_id"] for r in subset) == BENCH


@pytest.mark.parametrize("n", [10, 20, 40, 60])
def test_subset_rows_are_line_indices_into_the_data_file(n):
    """`pres_id` addresses `data/ms640_solved.txt` by line, and `r1`/`r2` are that line decoded.

    The subsets are consumed as an input everywhere, so a row that has drifted from the data file
    would silently rebase every technique's numbers onto a different presentation.
    """
    with open(os.path.join(_ROOT, "data", "ms640_solved.txt")) as f:
        lines = f.read().splitlines()
    with open(os.path.join(_ROOT, "benchmark", "subsets", f"benchmark_subset_{n}.json")) as f:
        doc = json.load(f)
    assert doc["size"] == len(doc["subset"]) == n
    for row in doc["subset"]:
        flat = ast.literal_eval(lines[row["pres_id"]])
        half = len(flat) // 2
        r1, r2 = (''.join(_INT_TO_CHAR[v] for v in part if v)
                  for part in (flat[:half], flat[half:]))
        assert (r1, r2) == (row["r1"], row["r2"])


@pytest.mark.parametrize("n", [10, 20, 40, 60])
def test_untested_arm_rows_say_none_and_never_false(n):
    """An untested row must read as untested, never as a failed solve.

    ARMS.md documents `tested = False` => `-1` in every numeric arm column and `none` in every
    string one. A `False` there would score a search that was never run as one that lost, which
    understates the transformed arms on exactly the subsets they were never run on.

    Asserted over *every* column the contract covers rather than a chosen few — naming two of them
    would leave `bestcov_path`, `bestcov_z` and the whole `m10k_*` block free to say `False`.
    """
    identity = {"pres_id", "bin", "aut_class", "start_length", "r1", "r2", "tested"}
    path = os.path.join(_ROOT, "benchmark", "subsets", f"benchmark_subset_{n}_arms.csv")
    with open(path) as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == n
    untested = 0
    for row in rows:
        # The greedy ran on every row of every subset; only the transformed arms can be untested.
        assert row["greedy_solved"] == "True"
        if row["tested"] == "True":
            continue
        untested += 1
        for column, value in row.items():
            if column in identity or column.startswith("greedy_"):
                continue
            assert value in ("-1", "none"), f"{column} = {value!r} on untested row {row['pres_id']}"
    # subset-60 is the row list both campaigns ran, so it alone has nothing untested. Everywhere
    # else the guard has to actually fire — a vacuous pass here would prove nothing.
    assert (untested == 0) == (n == 60)


@pytest.mark.parametrize("n", [10, 20, 40, 60])
def test_arms_csv_and_json_are_the_same_table(n):
    """Each arms table ships twice. Two shipped representations that disagree is a real defect.

    The JSON also records the weight vector its `heur_*` columns were measured with — the vector
    since withdrawn as overfit. Pinning it keeps the columns readable: they are the output of THAT
    ordering, and an edit that relabelled them without re-running would be caught here.
    """
    stem = os.path.join(_ROOT, "benchmark", "subsets", f"benchmark_subset_{n}_arms")
    with open(stem + ".csv") as f:
        from_csv = list(csv.DictReader(f))
    with open(stem + ".json") as f:
        doc = json.load(f)
    assert doc["heuristic_weights"] == WITHDRAWN_WEIGHTS
    assert len(from_csv) == len(doc["rows"]) == n
    for c, j in zip(from_csv, doc["rows"]):
        # The CSV is the JSON stringified, so compare on that footing rather than re-typing it.
        assert c == {k: ("" if v is None else str(v)) for k, v in j.items()}


def test_every_feature_is_addressable_as_a_weight():
    """A name in FEATURES that no config can reference is a feature that silently does nothing."""
    for name in FEATURES:
        key = make_priority({"segments": [{"upto": None, "w": {name: 1.0}}]})("xxyy", "xy")
        assert key[0] == 0 and isinstance(key[1], float)


def test_priority_keys_stay_comparable_across_segments():
    """The leading segment index is load-bearing twice over.

    It makes every state below the boundary outrank every state above it, and it keeps two
    segments' scores, which are on unrelated scales, from ever being compared. S20_MK2 is one
    segment, but the schema allows more, so the shape is pinned here rather than left to a caller.
    """
    p = make_priority({"segments": [{"upto": 16, "w": {"L": 1.0}},
                                    {"upto": None, "w": {"L": 1.0, "K": 4.0}}]})
    short = p("xxyy", "xy")                           # L = 6  -> segment 0
    long_ = p("xxyyxxyyxxyy", "xyxyxyxy")             # L = 20 -> segment 1
    assert short[0] == 0 and long_[0] == 1
    assert short < long_                              # int-vs-int first: heapq never raises here
    assert isinstance(short[0], int) and isinstance(long_[0], int)
