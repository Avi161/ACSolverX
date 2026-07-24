"""``hcompact.greedy_search_hcompact`` claims to be the SAME SEARCH as
``hsolve.greedy_search_h(keep_path=False)`` in a packed-arena layout — pop for pop, not merely
solve for solve. These tests are the durable form of ``verify_hcompact.py``'s 468-search sweep.

The string assertions are deliberate and safe here despite the repo rule about min/max relator
strings: that rule is about the HEAVY solver, whose min/max are tie-broken over a ``set`` and
follow ``PYTHONHASHSEED``. ``hsolve``'s are first-seen values updated on strict inequality only —
fully deterministic — and equality of the first-seen strings is what pins DISCOVERY order, which
``solved``/``nodes_explored`` alone cannot (they would survive a flipped tie-break that happens
not to change the solve).
"""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from experiments.heuristic_search.hlab import load_split             # noqa: E402
from experiments.heuristic_search.hsolve import (                    # noqa: E402
    LEAN_SMALL_BUDGET, RECOMMENDED, greedy_search_h,
)
from experiments.heuristic_search.hcompact import (                  # noqa: E402
    greedy_search_hcompact,
)

MAX_BUDGET = 500          # repo-wide test ceiling discipline (hard cap 1,000)
MRL = 48

# Every returned field except path/path_moves (structurally empty on the compact side —
# asserted separately) — INCLUDING the first-seen relator string pairs.
FIELDS = ("solved", "nodes_explored", "path_length", "min_relator_length",
          "min_relator", "max_relator_length", "max_relator",
          "max_relator_length_expanded", "max_relator_expanded")


@pytest.fixture(scope="module")
def sample_rows():
    return load_split("train")[:8]


# The two non-shipped configs exist to exercise branches the shipped three never reach
# (advisor review): the depth post-processing on every push, and the no-INF-segment fallback
# (seg = n_seg, score = L) in both solvers.
DEPTH_CFG = {"segments": [{"upto": None,
                           "w": {"L": 1.0, "K": 2.53, "MK": 6.418, "S": 8.458,
                                 "xyimb": 3.292},
                           "depth": 0.125}]}
FALLBACK_CFG = {"segments": [{"upto": 14, "w": {"L": 1.0, "K": 3.0}}]}


@pytest.mark.parametrize("cfg", [
    pytest.param(None, id="baseline"),
    pytest.param(RECOMMENDED, id="recommended"),
    pytest.param(LEAN_SMALL_BUDGET, id="lean_small_budget"),
    pytest.param(DEPTH_CFG, id="depth_term"),
    pytest.param(FALLBACK_CFG, id="segment_fallback"),
])
def test_every_field_matches_hsolve_including_first_seen_strings(sample_rows, cfg):
    solved_any = False
    for r in sample_rows:
        a = greedy_search_h(r["r1"], r["r2"], MAX_BUDGET, max_relator_length=MRL,
                            config=cfg, keep_path=False)
        b = greedy_search_hcompact(r["r1"], r["r2"], MAX_BUDGET,
                                   max_relator_length=MRL, config=cfg)
        for f in FIELDS:
            assert a[f] == b[f], (r["name"], f, a[f], b[f])
        assert b["path"] == [] and b["path_moves"] == [], r["name"]
        solved_any = solved_any or a["solved"]
    if cfg in (RECOMMENDED, LEAN_SMALL_BUDGET):
        # The solved branch is where a tie-break divergence AFTER the first-seen strings lock
        # would surface (it moves nodes_explored/path_length) -- pin it per shipped ordering.
        assert solved_any, "no row solved -- the solved branch went unexercised"


def test_growth_preserves_the_search(sample_rows):
    """Force the reservation to be exceeded mid-search (``reserve_states=1`` floors the
    arena at ~10.6k slots) so the grow-copy-rehash path runs several doublings, then require
    the result to still match ``hsolve`` on every field. A rehash that lost a visited state
    would re-discover it and shift ``depth`` and every subsequent tie-break; a grow that
    dropped ``score``/``seg`` would reorder every state still in the heap.
    """
    r = sample_rows[0]
    a = greedy_search_h(r["r1"], r["r2"], MAX_BUDGET, max_relator_length=MRL,
                        config=RECOMMENDED, keep_path=False)
    b = greedy_search_hcompact(r["r1"], r["r2"], MAX_BUDGET, max_relator_length=MRL,
                               config=RECOMMENDED, reserve_states=1)
    for f in FIELDS:
        assert a[f] == b[f], (f, a[f], b[f])


def test_chunk_boundary_preserves_the_search(sample_rows, monkeypatch):
    """At the production ``_HB_CHECK_EVERY = 1024`` every budget <= 1,000 search runs as a
    SINGLE ``_run_chunk_h`` call, so the return-to-Python re-entry -- stats round-tripping
    through ``st[]``, score/seg surviving the boundary -- is never crossed by the other tests.
    Shrink the chunk so a 500-node burn crosses it four times and require total agreement.
    """
    import experiments.heuristic_search.hcompact as hc
    monkeypatch.setattr(hc, "_HB_CHECK_EVERY", 100)
    for r in sample_rows[:3]:
        a = greedy_search_h(r["r1"], r["r2"], MAX_BUDGET, max_relator_length=MRL,
                            config=RECOMMENDED, keep_path=False)
        b = greedy_search_hcompact(r["r1"], r["r2"], MAX_BUDGET, max_relator_length=MRL,
                                   config=RECOMMENDED)
        for f in FIELDS:
            assert a[f] == b[f], (r["name"], f, a[f], b[f])


def test_unknown_feature_raises_like_hsolve():
    bad_cfg = {"segments": [{"upto": None, "w": {"L": 1.0, "nonsuch": 2.0}}]}
    with pytest.raises(KeyError):
        greedy_search_hcompact("xyxYXy", "xyXY", 50, max_relator_length=24,
                               config=bad_cfg)
