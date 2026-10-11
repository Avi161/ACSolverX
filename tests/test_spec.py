"""acx.search: the spec backend against main's baseline, budget-prefix invariance, the cap."""
import importlib.util

import pytest
from conftest import dataset, golden_entries

from acx.core.config import SearchConfig
from acx.core.moves import enumerate_moves, source_word
from acx.core.words import Presentation, parse, reduce, rotate
from acx.search import BackendUnavailable, search

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


def brute_cap_rejected(trace, cap):
    """Over-cap children of every expanded (non-final) popped state, counted from scratch."""
    n = 0
    for strs in trace:
        rels = tuple(map(parse, strs))
        if all(len(r) == 1 for r in rels):
            break
        for m in enumerate_moves(rels):
            new = reduce(rotate(rels[m.i], m.k1) + rotate(source_word(rels, m), m.k2))
            n += len(new) > cap or any(len(r) > cap for k, r in enumerate(rels) if k != m.i)
    return n


@pytest.mark.parametrize("cap", [12, 16])
def test_cap_is_applied_at_generation_and_counted(ms640, cap):
    r = search(ms640[322], SearchConfig(cap=cap, budget=150, trace=True))
    assert all(len(w) <= cap for strs in r.trace[1:] for w in strs)
    assert r.stats["cap_rejected"] == brute_cap_rejected(r.trace, cap) > 0
    free = search(ms640[322], SearchConfig(cap=None, budget=150))
    assert free.stats["cap_rejected"] == 0


def test_start_over_the_cap_rejects_every_child():
    p = Presentation.parse("xxxxxxyXYXYX", "xyXyXY")
    r = search(p, SearchConfig(cap=8, budget=10))
    assert r.pops == 1 and not r.solved
    assert r.stats["cap_rejected"] == len(list(enumerate_moves(r.start.rels)))


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


@pytest.mark.skipif(importlib.util.find_spec("acx.search.fast") is not None,
                    reason="the fast backend exists; its parity tests own it")
def test_missing_fast_backend_is_a_clear_error():
    with pytest.raises(BackendUnavailable):
        search(("YYXyx", "Yx"), backend="fast")
