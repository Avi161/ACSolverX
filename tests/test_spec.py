"""acx.search: the spec backend against main's baseline, budget-prefix invariance, the cap."""
import sys

import pytest
from conftest import dataset, golden_entries

from acx.core.config import SearchConfig
from acx.core.moves import enumerate_moves, source_word
from acx.core.words import Presentation, canonical_rels, parse, reduce, rotate, state_bytes
from acx.search import BackendUnavailable, search
from acx.verify import replay

# Every golden entry that costs well under a second, plus the deepest solve inside budget 1,000
# (ms640 #551, 990 nodes) at both caps. The other slow rows exhaust their budget unsolved.
CASES = [e for e in golden_entries() if e["tier"] == "fast"
         or (e["pres_id"] == 551) or (e["pres_id"] == 627)]


@pytest.mark.parametrize("e", CASES, ids=lambda e: f"{e['dataset'][5:9]}{e['pres_id']}-c{e['cap']}"
                         f"{'' if e['cyclic'] else '-lin'}")
def test_matches_main_baseline_golden(e):
    pres = dataset(e["dataset"])[e["pres_id"]]
    r = search(pres, SearchConfig(budget=e["budget"], cap=e["cap"], cyclic=e["cyclic"]))
    got = {"solved": r.solved, "nodes_explored": r.pops, "path_length": r.path_length,
           "min_relator_length": r.stats["min_total"], "max_relator_length": r.stats["max_total"],
           "max_relator_length_expanded": r.stats["max_total_expanded"],
           "max_relator_expanded": list(r.stats["max_expanded"])}
    assert got == {k: e[k] for k in got}


@pytest.mark.parametrize("priority", ["length", "s20_mk2"])
@pytest.mark.parametrize("pid", [7, 120, 466])
def test_budget_prefix_invariance(ms640, priority, pid):
    """A run at budget B is exactly the first B pops of any longer run."""
    cfg = SearchConfig(priority=priority, budget=60, trace=True)
    short = search(ms640[pid], cfg)
    long = search(ms640[pid], cfg.replace(budget=180))
    assert long.trace[:short.pops] == short.trace
    if short.solved:
        assert (long.pops, long.path) == (short.pops, short.path)


def over_cap_children(trace, cap):
    """The state bytes of the over-cap child of every move of every expanded (non-final) popped state, from scratch."""
    children = []
    for strs in trace:
        rels = tuple(map(parse, strs))
        if all(len(r) == 1 for r in rels):
            break
        for m in enumerate_moves(rels):
            new = reduce(rotate(rels[m.i], m.k1) + rotate(source_word(rels, m), m.k2))
            if len(new) > cap or any(len(r) > cap for k, r in enumerate(rels) if k != m.i):
                children.append(state_bytes(canonical_rels(rels[:m.i] + (new,) + rels[m.i + 1:])))
    return children


@pytest.mark.parametrize("cap", [12, 16])
def test_cap_is_applied_at_generation_and_counted(ms640, cap):
    r = search(ms640[322], SearchConfig(cap=cap, budget=150, trace=True))
    assert all(len(w) <= cap for strs in r.trace[1:] for w in strs)
    assert r.stats["cap_dropped"] == len(over_cap_children(r.trace, cap)) > 0
    free = search(ms640[322], SearchConfig(cap=None, budget=150))
    assert free.stats["cap_dropped"] == 0


# At cap 12 and budget 150: the moves that drop a child, the distinct states among those children, and the states
# that would have popped. A counter that took each move for a new state would count more than the distinct ones.
DUPLICATES = [("length", 322, 5790, 4613, 82), ("length", 435, 4732, 3279, 134), ("s20_mk2", 322, 2664, 2225, 0),
              ("s20_mk2", 435, 2808, 1898, 3), ("s20_mk2", 144, 2272, 1972, 2)]


@pytest.mark.parametrize("backend", ["spec", "fast"])
@pytest.mark.parametrize("priority, pid, moves, distinct, would_pop", DUPLICATES)
def test_duplicate_dropped_children_are_one_state(ms640, backend, priority, pid, moves, distinct, would_pop):
    """Several moves can give one over-cap child: ``cap_dropped`` counts the moves, ``cap_would_pop`` the states."""
    cfg = SearchConfig(priority=priority, cap=12, budget=150, backend=backend, trace=True)
    r = search(ms640[pid], cfg)
    children = over_cap_children(r.trace, 12)
    assert (r.stats["cap_dropped"], len(children), len(set(children))) == (moves, moves, distinct)
    assert r.stats["cap_would_pop"] == would_pop <= distinct


def test_start_over_the_cap_rejects_every_child():
    p = Presentation.parse("xxxxxxyXYXYX", "xyXyXY")
    r = search(p, SearchConfig(cap=8, budget=10))
    assert r.pops == 1 and not r.solved
    assert r.stats["cap_dropped"] == len(list(enumerate_moves(r.start.rels)))


def test_s20_mk2_solves_and_differs_from_length(ms640):
    a = search(ms640[322], SearchConfig(budget=300))
    b = search(ms640[322], SearchConfig(priority="s20_mk2", budget=300))
    assert a.solved and b.solved and a.pops != b.pops


def test_engine_api(ms640):
    r = search(("YYXyx", "Yx"), budget=100)
    assert r.solved and r.pops == 3 and r.start == Presentation.parse("YYXyx", "Yx").canonical()
    assert r.end.is_trivial() and r.stats["backend"] == "spec"
    assert search(ms640[0], capture_path=False).path is None


def test_three_generators():
    r = search(Presentation.parse("xY", "yZ", "zyX"), SearchConfig(budget=200))
    assert r.solved and r.end.n_gen == 3 and r.end.is_trivial()


def test_missing_fast_backend_is_a_clear_error(monkeypatch):
    monkeypatch.setitem(sys.modules, "acx.search.fast", None)        # as if numba were not installed
    with pytest.raises(BackendUnavailable):
        search(("YYXyx", "Yx"), backend="fast")


@pytest.mark.parametrize("backend", ["spec", "fast"])
def test_a_start_with_det_not_one_is_never_solved(backend):
    """``(X, X)`` is all length 1 but not trivial: the unsolvable start stays unsolved, with or without a path."""
    for kw in ({}, {"capture_path": False}):
        r = search(Presentation.parse("X", "x"), SearchConfig(backend=backend, budget=50, **kw))
        assert not r.solved and r.path is None and r.end is None


@pytest.mark.parametrize("backend", ["spec", "fast"])
@pytest.mark.parametrize("rels", [("XYx", "YXy"), ("XYx", "yXYY"), ("XXY", "XYxyx"), ("Xyxx", "xYX")])
def test_linear_start_is_a_fixed_point_that_replays(rels, backend):
    """With ``cyclic=False`` ``reduced().canonical()`` of these starts is not stable; the search starts at the
    stable form, so ``Result.start`` and the raw row both replay the path."""
    p = Presentation.parse(*rels)
    r = search(p, SearchConfig(cyclic=False, cap=None, budget=3000, backend=backend))
    assert r.solved and r.start == r.start.reduced(False).canonical()
    for start in (p, r.start):
        assert replay(start, r.path, cyclic=False)[-1].is_trivial()
