"""``hsolve.greedy_search_h`` is meant to be a drop-in replacement for
``greedy_baseline.greedy_search`` inside the production pipeline (``run_baseline.py`` writes a
results row from exactly that dict), with the heap ordering swapped for a tuned heuristic. This
file is what stands between that claim and a Colab run silently writing malformed rows. Four
separate things could break it and nothing else here would catch them:

1. **The dict contract.** ``config=None`` is documented as reproducing the length-only baseline
   exactly, key for key. If a key is missing, renamed, or a scalar field drifts, every downstream
   consumer of a results row (``verify_results.py``, resume, W&B) breaks the moment this ordering
   is switched on -- and only then, hours into a run.

2. **Agreement with the research harness.** ``hfast.search_fast`` is what every number in this
   program's reports was measured with. If ``greedy_search_h`` pops differently from it under the
   same tuned config, the recommendation and the production path have quietly diverged and the
   reports describe a search nobody would actually run.

3. **The certificates are real.** A ``path`` reported as solved must replay -- independently,
   through ``moves_to_states``, which knows nothing about how the path was produced -- to a
   trivial pair. A search that reports ``solved`` with a path that does not replay would corrupt
   every downstream row silently.

4. **The config is not silently ignored.** Nothing else in this file would notice if
   ``greedy_search_h`` accepted ``config`` and then dropped it on the floor -- every test above
   would still pass, because ``config=None`` IS supposed to look like the baseline. So this file
   also proves, on a presentation the baseline cannot solve at this budget, that a tuned config
   changes the search; and that a config naming a feature this module does not know raises rather
   than silently scoring it as zero.

Mirrors ``verify_hsolve.py``'s three claims (this file covers the same ground under pytest) and
adds the two extra guards above.
"""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from experiments.heuristic_search.hlab import load_split             # noqa: E402
from experiments.heuristic_search.hfast import search_fast           # noqa: E402
from experiments.heuristic_search.perbin import bin_of               # noqa: E402
from experiments.heuristic_search.hsolve import (                    # noqa: E402
    LEAN_SMALL_BUDGET, RECOMMENDED, greedy_search_h,
)
from experiments.search.greedy_baseline import (                     # noqa: E402
    greedy_search, moves_to_states, str_to_move,
)

MAX_BUDGET = 500          # the repo-wide test ceiling; matches test_hfast.py's MAX_BUDGET
MRL = 48                  # the cap the research harness (search_fast) is measured at

# The scalar fields greedy_search_h must reproduce exactly -- everything greedy_search returns
# EXCEPT the min/max relator string pairs, which are tie-broken over a set and follow
# PYTHONHASHSEED (repo rule: assert their lengths, never the strings).
SCALAR_FIELDS = ("solved", "nodes_explored", "path_length", "min_relator_length",
                 "max_relator_length", "max_relator_length_expanded")


@pytest.fixture(scope="module")
def train_rows():
    return load_split("train")


@pytest.fixture(scope="module")
def sample_rows(train_rows):
    """8 of train's 40 -- enough to see a spread of solved/unsolved outcomes without paying for
    the full split three times over (this file runs three separate config sweeps over it)."""
    return train_rows[:8]


# ------------------------------------------------------------------------- 1. the dict contract

def test_config_none_reproduces_greedy_search_key_for_key_and_field_for_field(sample_rows):
    """The whole point of ``greedy_search_h`` is that a caller switching orderings does not have
    to touch anything downstream. A missing or renamed key must fail loudly here, not inside
    ``run_baseline.py`` hours into a Colab run -- hence asserting the KEY SETS match, not just
    iterating over one dict's keys (which would silently ignore an extra or missing key on the
    other side).
    """
    for r in sample_rows:
        want = greedy_search(r["r1"], r["r2"], MAX_BUDGET, max_relator_length=MRL)
        got = greedy_search_h(r["r1"], r["r2"], MAX_BUDGET, max_relator_length=MRL, config=None)

        assert set(got) == set(want), (
            r["name"], sorted(set(want) ^ set(got)))
        for field in SCALAR_FIELDS:
            assert got[field] == want[field], (r["name"], field, want[field], got[field])
        # The path itself, not just its length -- a length-only pin would miss a path that is the
        # right size but wrong moves.
        assert got["path"] == want["path"], r["name"]
        assert got["path_moves"] == want["path_moves"], r["name"]


# --------------------------------------------------------------- 2. agreement with the harness

@pytest.mark.parametrize("cfg", [
    pytest.param(RECOMMENDED, id="recommended"),
    pytest.param(LEAN_SMALL_BUDGET, id="lean_small_budget"),
])
def test_a_tuned_config_matches_search_fast_the_research_harness_every_result_was_measured_with(
        sample_rows, cfg):
    """``search_fast`` is what EXP-01..20's numbers came from. If ``greedy_search_h`` disagreed
    with it under the same ordering, the reports and the production path would describe two
    different searches -- this is the seam that keeps them one search.
    """
    for r in sample_rows:
        harness = search_fast(r["r1"], r["r2"], MAX_BUDGET, cfg, MRL)
        prod = greedy_search_h(r["r1"], r["r2"], MAX_BUDGET, max_relator_length=MRL, config=cfg)

        assert harness["solved"] == prod["solved"], r["name"]
        assert harness["nodes"] == prod["nodes_explored"], r["name"]
        # Both sides are None when unsolved, so this is safe unconditionally.
        assert harness["path_length"] == prod["path_length"], r["name"]
        assert harness["min_total"] == prod["min_relator_length"], r["name"]


# ------------------------------------------------------------------ 3. certificates are real

def test_every_solved_certificate_replays_independently_to_a_trivial_pair(sample_rows):
    """The most important test in this file. A returned ``path`` is not trusted on its own word --
    it is decoded back into Definition 2.1 moves and replayed through ``moves_to_states``, a
    function that knows nothing about how ``greedy_search_h`` produced the path. A self-consistent
    bug in the search (e.g. reporting ``solved`` on a state that was never actually reduced to a
    trivial pair) cannot survive this check, because the replay recomputes every state from
    scratch off the moves alone.

    Swept across ``recommended``/``lean_small_budget``/baseline so the certificate check is not
    resting on a single ordering's solves; ``checked > 0`` is asserted so this cannot pass
    vacuously if a future change stopped every config from solving anything at this budget.
    """
    checked = 0
    for cfg_name, cfg in (("recommended", RECOMMENDED), ("lean_small_budget", LEAN_SMALL_BUDGET),
                          ("baseline", None)):
        for r in sample_rows:
            got = greedy_search_h(r["r1"], r["r2"], MAX_BUDGET, max_relator_length=MRL,
                                  config=cfg)
            if not got["solved"]:
                continue
            checked += 1
            moves = [str_to_move(m) for m in got["path_moves"]]
            states = moves_to_states(r["r1"], r["r2"], moves, cyclic_reduce=True)
            replayed = [list(s) for s in states]
            assert replayed == got["path"], (cfg_name, r["name"])
            last = states[-1]
            assert len(last[0]) == 1 and len(last[1]) == 1, (cfg_name, r["name"], last)

    assert checked > 0, "no solved certificates were produced -- this test would pass vacuously"


# ------------------------------------------------------------------------- 4. config is not inert

def test_recommended_ordering_actually_changes_the_search_on_a_mid_bin_presentation(train_rows):
    """Nothing above would notice if ``greedy_search_h`` accepted ``config`` and silently ignored
    it -- ``config=None`` is SUPPOSED to look like the baseline, so a bug that dropped ``config``
    on the floor would make every other test in this file pass while the heuristic did nothing.

    Picked from difficulty bins 4-7 (``perbin.bin_of``, graded under plain length ordering): an
    easy row (bin 0-3) solves immediately either way and would make this vacuous.

    Recorded case (verified empirically at BUDGET=500, MRL=48): ``ms544`` is bin 5. Under
    ``config=None`` (length-only) it exhausts the budget unsolved (500 nodes). Under
    ``RECOMMENDED`` it solves in 160 nodes -- both ``solved`` and ``nodes_explored`` differ.
    """
    by_name = {r["name"]: r for r in train_rows}
    r = by_name["ms544"]
    assert 4 <= bin_of("ms544") <= 7

    base = greedy_search_h(r["r1"], r["r2"], MAX_BUDGET, max_relator_length=MRL, config=None)
    rec = greedy_search_h(r["r1"], r["r2"], MAX_BUDGET, max_relator_length=MRL, config=RECOMMENDED)

    assert base["solved"] is False and base["nodes_explored"] == MAX_BUDGET
    assert rec["solved"] is True and rec["nodes_explored"] == 160
    assert rec["nodes_explored"] != base["nodes_explored"] or rec["solved"] != base["solved"]


# ------------------------------------------------------------- 5. keep_path=False is result-pure

def test_keep_path_false_changes_memory_only_never_the_search(sample_rows):
    """``keep_path=False`` swaps the parent map for a visited set (1.53x less RAM, measured) and
    is documented as changing NOTHING about the search itself. That claim is what lets a run
    written in one mode resume in the other, and what makes the certificate recoverable by a
    deterministic re-run -- so a divergence here would corrupt results silently, and only at the
    budgets where the low-memory mode is actually used. Pinned both ways: every scalar field
    identical, and the path genuinely absent (not merely shorter) when the map is off.

    Swept under ``RECOMMENDED`` because it solves several of these rows at this budget; the
    ``any(...)`` assert keeps the solved branch -- the one with the early return -- from going
    unexercised if a future change stopped everything solving.
    """
    outcomes = []
    for r in sample_rows:
        with_path = greedy_search_h(r["r1"], r["r2"], MAX_BUDGET, max_relator_length=MRL,
                                    config=RECOMMENDED, keep_path=True)
        without = greedy_search_h(r["r1"], r["r2"], MAX_BUDGET, max_relator_length=MRL,
                                  config=RECOMMENDED, keep_path=False)
        for field in SCALAR_FIELDS:
            assert without[field] == with_path[field], (r["name"], field)
        assert without["path"] == [] and without["path_moves"] == [], r["name"]
        outcomes.append(with_path["solved"])
    assert any(outcomes), "no row solved -- the early-return branch was never exercised"


# ------------------------------------------------------------------- 6. unknown feature rejected

def test_a_config_naming_an_unknown_feature_raises_instead_of_silently_scoring_zero():
    """``compile_config`` (called inside ``greedy_search_h``) indexes weights by ``FEATURES``
    position; a typo'd feature name inside a segment's ``w`` dict must ``KeyError`` loudly rather
    than the config silently contributing zero to every state's score -- exactly the mistake a
    config author could make when hand-writing a segment.
    """
    bad_cfg = {"segments": [{"upto": None, "w": {"L": 1.0, "nonsuch": 2.0}}]}
    with pytest.raises(KeyError):
        greedy_search_h("xyxYXy", "xyXY", 50, max_relator_length=24, config=bad_cfg)
