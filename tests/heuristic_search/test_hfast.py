"""``hfast.search_fast`` is a numba rewrite of ``hlab.LabSolver`` and must be observationally
identical to it -- not "scores similarly", but pops the same states in the same order and reports
the same numbers. This file is that pin.

**The baseline (length-only) config is a vacuous guard for this rewrite.** Ordering by length
always pops the shortest available state, so a baseline search never lets a relator grow past
where it started -- it never reaches the ten-thousand-candidate expansions
``expand_and_score_nj`` exists to speed up, and never puts any pressure on the packed-key
tie-break. A config that agrees with the slow solver only on ``BASELINE_CONFIG`` would pass
whether or not the fast kernel is correct (see ``hfast.py``'s and ``verify_fast.py``'s own
docstrings). The real gate is agreement on **structural** configs that deliberately let relators
grow toward the cap -- so the first substantive test below checks, empirically, that the sample
actually gets pushed into that regime before trusting the equality check that follows it.

Three things could silently break in this particular rewrite and nothing else here would catch
them: the packed ``bytes`` key could sort differently from the ``(r1_str, r2_str)`` string tuple
``LabSolver`` uses, which would shift the heap's ``(priority, depth, key)`` tie-break; the numba
feature kernel (``_feats_nj``) could drift from ``hlab.phi`` on some block-structure edge case;
and a two-segment config could compute its segment index in a different place (``expand_and_
score_nj`` scores every child before Python ever sees one) and disagree with the slow solver about
which segment a state falls in. Each gets its own test.
"""
import os
import sys

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from experiments.heuristic_search.hlab import (              # noqa: E402
    BASELINE_CONFIG, FEATURES, N_FEAT, LabSolver, load_split, make_priority, phi, run_one,
)
from experiments.heuristic_search.hfast import (              # noqa: E402
    _feats_nj, _pack, compile_config, search_fast,
)
from experiments.heuristic_search.perbin import bin_of        # noqa: E402
from experiments.search.greedy_baseline import str_to_arr     # noqa: E402

MAX_BUDGET = 500          # the repo-wide test ceiling; matches test_hlab.py's MAX_BUDGET
MRL = 48                  # the cap the structural configs are meant to be measured at

FIELDS = ("solved", "nodes", "path_length", "min_total", "max_pop")

# Four ways to let a relator grow instead of shrink: a negative weight on imbalance / the longer
# relator / the shorter relator rewards states that DON'T sort by length, and a heavy knot weight
# reorders around a feature length never determines. These are the configs the numba rewrite
# actually needs to get right.
_CFG_IMBAL = {"segments": [{"upto": None, "w": {"L": 1.0, "imbal": -2.0}}]}
_CFG_LMAX = {"segments": [{"upto": None, "w": {"L": 1.0, "Lmax": -4.0}}]}
_CFG_LMIN = {"segments": [{"upto": None, "w": {"L": 1.0, "Lmin": -8.0}}]}
_CFG_K = {"segments": [{"upto": None, "w": {"L": 1.0, "K": 4.0}}]}

STRUCTURAL_CONFIGS = [
    pytest.param(_CFG_IMBAL, id="imbal"),
    pytest.param(_CFG_LMAX, id="Lmax"),
    pytest.param(_CFG_LMIN, id="Lmin"),
    pytest.param(_CFG_K, id="K"),
]
# K alone solves several sampled presentations in a handful of nodes (a heavy knot bonus can walk
# straight to a trivial pair), which proves nothing about the runaway regime. imbal/Lmax/Lmin are
# the configs the precondition check below demands actually reach the cap.
GROWTH_CONFIGS = [_CFG_IMBAL, _CFG_LMAX, _CFG_LMIN]

SEGMENTED_CONFIG = {"segments": [{"upto": 16, "w": {"L": 1.0}},
                                  {"upto": None, "w": {"L": 1.0, "Lmax": -3.0}}]}


@pytest.fixture(scope="module")
def train_rows():
    return load_split("train")


@pytest.fixture(scope="module")
def structural_sample(train_rows):
    """4 of train's 40 -- two from the easy end, two from the hard end -- so the structural gate
    is not exercised only on the presentations most likely to solve before growing at all."""
    return train_rows[:2] + train_rows[-2:]


@pytest.fixture(scope="module")
def harvested_states(train_rows):
    """Real ``(r1_str, r2_str)`` states exactly as ``LabSolver`` produces them: reduced,
    canonicalised, and drawn from both the short (baseline) and long (structural) regimes so the
    feature-kernel and packed-key tests below see more than the easy case.

    Search is deterministic, so this fixture is exactly reproducible run to run.
    """
    cfgs = (BASELINE_CONFIG, _CFG_IMBAL)
    seen = set()
    for r in train_rows[:2]:
        for cfg in cfgs:
            p = make_priority(cfg)
            s = LabSolver(r["r1"], r["r2"], p, max_nodes=150, max_relator_length=32,
                           cyclic_reduce=True)
            s.solve()
            seen |= set(s.visited.keys())
    return sorted(seen)


def _feats_via_kernel(r1_str, r2_str, mrl=MRL):
    """Reach ``_feats_nj`` exactly the way ``search_fast`` reaches it: pack the pair, strip the
    ``pack_key`` separator back out into one codes buffer, and hand it scratch arrays sized like
    the kernel's own (``2*mrl + 2``, never just ``len(r1)+len(r2)``)."""
    a1, a2 = str_to_arr(r1_str), str_to_arr(r2_str)
    key = _pack(a1, a2)
    sep = key.index(0)
    la, lb = sep, len(key) - sep - 1
    codes = np.frombuffer(key.replace(b"\x00", b""), dtype=np.uint8)
    r_isx = np.empty(2 * mrl + 2, dtype=np.bool_)
    r_len = np.empty(2 * mrl + 2, dtype=np.int64)
    # Sized from N_FEAT, never a literal: the feature vector has been extended once already
    # (a second family at index 13), and numba does not bounds-check, so a stale literal here
    # would have the kernel writing past the end of this buffer instead of failing loudly.
    out = np.empty(N_FEAT, dtype=np.float64)
    _feats_nj(codes, 0, la, lb, r_isx, r_len, out)
    return tuple(out)


# --------------------------------------------------------------- precondition: the regime fires

def test_the_growth_configs_actually_push_the_sample_past_the_short_regime(structural_sample):
    """If nothing below ever grows a relator, the equality test right after this one would pass
    whether or not the fast kernel is correct -- see the module docstring. This reads
    ``search_fast`` (not the slow solver) on purpose: it is not checking correctness, only that
    this sample+config combination leaves the regime the baseline can never reach, which is a
    property of the search trajectory itself and cheap to check either way.

    ``any`` across the sample, per config, is deliberate -- ``imbal``/``Lmax``/``Lmin`` do not all
    saturate every presentation (an easy one can still solve quickly), but each must saturate at
    least one for the sample to be doing its job.
    """
    for cfg in GROWTH_CONFIGS:
        results = [search_fast(r["r1"], r["r2"], MAX_BUDGET, cfg, MRL) for r in structural_sample]
        assert any(not res["solved"] and res["max_pop"] == MRL for res in results), cfg


# ------------------------------------------------------------------------- the structural gate

@pytest.mark.parametrize("cfg", STRUCTURAL_CONFIGS)
def test_search_fast_agrees_with_labsolver_field_for_field_on_configs_that_let_relators_grow(
        structural_sample, cfg):
    """The important test in this file. Every field the two implementations report -- not just
    ``solved`` -- must match: ``nodes`` and ``max_pop`` pin the pop order and the expansion cap,
    ``path_length`` pins the reconstructed path, ``min_total`` pins the progress signal the
    genuinely-unsolved presentations rely on."""
    p = make_priority(cfg)
    for r in structural_sample:
        slow = run_one(r["r1"], r["r2"], MAX_BUDGET, p, MRL)
        fast = search_fast(r["r1"], r["r2"], MAX_BUDGET, cfg, MRL)
        for field in FIELDS:
            assert slow[field] == fast[field], (
                f"{r['name']} field={field}: slow={slow} fast={fast}")


def test_search_fast_agrees_with_labsolver_on_a_two_segment_config_too(structural_sample):
    """The segment index is computed in a different place in each implementation --
    ``make_priority`` scores it in the Python callback ``LabSolver`` pushes with, while
    ``expand_and_score_nj`` picks the segment for every child inside the numba kernel, before
    Python ever sees the state. A single-segment agreement says nothing about that boundary.
    """
    p = make_priority(SEGMENTED_CONFIG)
    fast_results = []
    for r in structural_sample:
        slow = run_one(r["r1"], r["r2"], MAX_BUDGET, p, MRL)
        fast = search_fast(r["r1"], r["r2"], MAX_BUDGET, SEGMENTED_CONFIG, MRL)
        fast_results.append(fast)
        for field in FIELDS:
            assert slow[field] == fast[field], (
                f"{r['name']} field={field}: slow={slow} fast={fast}")
    # And confirm the boundary itself was actually crossed -- a max_pop this far past the
    # segment's upto=16 ceiling proves some popped state's total length exceeded it, so segment 1
    # was genuinely selected at least once rather than every state landing in segment 0.
    assert any(f["max_pop"] > 16 for f in fast_results)


# ------------------------------------------------------------------------- the feature kernel

def test_feats_nj_equals_phi_on_every_harvested_state(harvested_states):
    """Exact equality, not ``approx`` -- checked empirically across these states (and separately
    across 48,561 states spanning six presentations and two structural configs at mrl 48) with
    zero float divergence anywhere. Both implementations compute the same sums in the same order
    (one pass over the runs, low block count before high), so there is no accumulation-order ULP
    gap to relax for; if one ever turns up, tighten this comment rather than the assertion.
    """
    for r1, r2 in harvested_states:
        assert _feats_via_kernel(r1, r2) == phi(r1, r2), (r1, r2)


def test_feats_nj_matches_phi_on_pure_powers_and_the_cyclic_seam_merge():
    """Edge cases named in ``_feats_nj``'s own docstring as easy to get subtly wrong. These are
    constructed directly rather than harvested -- a short search is not guaranteed to visit them.
    """
    cases = [
        ("xxx", "y"),        # r1 is a pure power: one generator absent from r1 alone -> 0 knots
        ("xxx", "xxxxx"),    # y absent from the WHOLE PAIR -> the "only one mean" branch in both
                              # phi (`not xs or not ys`) and _feats_nj (`n_xs == 0 or n_ys == 0`)
        ("xxyyxx", "xyxy"),  # r1's leading and trailing x-blocks are one ring-wrapping run, not
                              # two -- the seam merge _runs_nj and word_stats both special-case
    ]
    for r1, r2 in cases:
        assert _feats_via_kernel(r1, r2) == phi(r1, r2), (r1, r2)


# --------------------------------------------------------------------------- the packed key

def test_packed_keys_sort_identically_to_the_string_tuples_hlab_uses(harvested_states):
    """This is what keeps the heap's ``(priority, depth, key)`` tie-break unchanged when ``key``
    switches from a ``(str, str)`` tuple to packed ``bytes`` -- if the two orderings ever
    disagreed, a tie between equal priorities would break differently and the two solvers could
    diverge from that pop onward even though every other piece of them agrees.
    """
    packed = [(_pack(str_to_arr(a), str_to_arr(b)), (a, b)) for a, b in harvested_states]
    by_string = sorted(harvested_states)
    by_packed = [pair for _, pair in sorted(packed, key=lambda kv: kv[0])]
    assert by_packed == by_string


# ------------------------------------------------------------------------------- continuity

def test_baseline_config_still_reproduces_the_baseline_search_at_budget_100(structural_sample):
    """Necessary, not sufficient. This is the same pop-for-pop shape ``test_hlab.py`` already
    pins for ``LabSolver`` itself; it says nothing about the structural regime above, which never
    fires under length-only ordering and is the actual gate for this rewrite.
    """
    p = make_priority(BASELINE_CONFIG)
    for r in structural_sample:
        slow = run_one(r["r1"], r["r2"], 100, p, 24)
        fast = search_fast(r["r1"], r["r2"], 100, BASELINE_CONFIG, 24)
        for field in FIELDS:
            assert slow[field] == fast[field], (
                f"{r['name']} field={field}: slow={slow} fast={fast}")


# ---------------------------------------------------------------------------------- depth (EXP-11)
#
# A config segment may now carry a ``"depth": w`` key. ``compile_config`` returns a three-tuple
# ``(seg_upto, seg_w, seg_depth)`` instead of two, and when any ``seg_depth`` entry is nonzero,
# ``search_fast`` adds ``seg_depth[segment_index] * child_depth`` to a child's score before it is
# pushed -- the ``g`` term of a weighted A*, with the thirteen structural features as ``h``. Depth
# is deliberately NOT one of the thirteen: it is a property of the *path that discovered* a state,
# not of the state itself, and the visited set keeps first-discovery with no decrease-key (see
# ``search_fast``'s own docstring). ``exp11_depth.py`` is the sweep that measured this; the cases
# below are pinned from what it found on the train split.

# A phased two-segment KNOT config -- same shape as ``exp11_depth.BASES["phasedK8"]`` -- so the
# backward-compat gate below covers a phased config as well as a single-segment and a growth one.
_CFG_PHASEDK = {"segments": [{"upto": 16, "w": {"L": 1.0}},
                              {"upto": None, "w": {"L": 1.0, "K": 8.0}}]}

NO_DEPTH_CONFIGS = [
    pytest.param(BASELINE_CONFIG, id="baseline"),
    pytest.param(_CFG_PHASEDK, id="phasedK8"),
    pytest.param(_CFG_LMAX, id="Lmax-growth"),
]


@pytest.mark.parametrize("cfg", NO_DEPTH_CONFIGS)
def test_configs_with_no_depth_key_at_all_are_bit_identical_to_labsolver(structural_sample, cfg):
    """The backward-compatibility gate. The entire EXP-01..10 experiment program ran before
    ``depth`` existed as a concept, over configs that never carry the key -- a plain single-segment
    config, a phased two-segment knot config, and a growth config that lets a relator run past
    where it started. ``compile_config`` changed arity (two-tuple -> three-tuple) and
    ``search_fast`` grew a ``use_depth`` branch it did not have before; none of that may change one
    bit of what these configs already produced, or every prior EXP-01..10 result becomes
    unreproducible.
    """
    p = make_priority(cfg)
    for r in structural_sample:
        slow = run_one(r["r1"], r["r2"], MAX_BUDGET, p, MRL)
        fast = search_fast(r["r1"], r["r2"], MAX_BUDGET, cfg, MRL)
        for field in FIELDS:
            assert slow[field] == fast[field], (
                f"{r['name']} field={field}: slow={slow} fast={fast}")


def test_explicit_depth_zero_is_identical_to_omitting_the_key_entirely(structural_sample):
    """``use_depth`` in ``search_fast`` is ``any(seg_depth != 0.0)`` -- it must gate on VALUE, not
    on key presence, so a swept config that sets ``depth: 0.0`` as one point in a sweep (as
    ``exp11_depth.py``'s zero-depth incumbent rows do) is never silently different from a config
    that never mentions depth at all. Same config, with and without the key, at every field.
    """
    omitted = {"segments": [{"upto": None, "w": {"L": 1.0}}]}
    explicit_zero = {"segments": [{"upto": None, "w": {"L": 1.0}, "depth": 0.0}]}
    for r in structural_sample:
        a = search_fast(r["r1"], r["r2"], MAX_BUDGET, omitted, MRL)
        b = search_fast(r["r1"], r["r2"], MAX_BUDGET, explicit_zero, MRL)
        assert a == b, r["name"]


def test_compile_config_returns_the_depth_vector_correctly():
    """The tuple-arity change (``seg_upto, seg_w`` -> ``seg_upto, seg_w, seg_depth``) must not
    scramble the first two elements, and the new third element must be 0.0 exactly where a segment
    carries no ``depth`` key and the segment's own value everywhere it does.
    """
    cfg = {"segments": [{"upto": 16, "w": {"L": 1.0}},
                         {"upto": None, "w": {"L": 1.0, "K": 8.0}, "depth": 2.0}]}
    seg_upto, seg_w, seg_depth = compile_config(cfg)
    assert len(seg_depth) == 2
    assert seg_depth[0] == 0.0        # no "depth" key on this segment
    assert seg_depth[1] == 2.0        # exact value carried through
    # seg_upto / seg_w still line up with the segments -- the arity change didn't scramble them.
    assert seg_upto[0] == 16.0
    assert seg_upto[1] == float("inf")
    assert seg_w[0, FEATURES.index("L")] == 1.0
    assert seg_w[1, FEATURES.index("L")] == 1.0
    assert seg_w[1, FEATURES.index("K")] == 8.0


def test_a_nonzero_depth_weight_actually_changes_the_search():
    """Not vacuous by construction, which is easy to get wrong here: a depth term added to EVERY
    child of a single expansion shifts them all equally and cannot move the pop order under a
    single-segment config where nothing else competes for rank, and placing it in a segment that
    an easy presentation never reaches (e.g. an ``upto: 16`` endgame segment on a presentation that
    solves inside length 16) does nothing either. So this uses a SINGLE-segment, pure-weighted-A*
    config -- ``{"upto": None, "w": {"L": 1.0}, "depth": w}`` -- on ``ms589``, a bin-4 presentation
    (``perbin.bin_of``, difficulty measured under plain length ordering) that plain length ordering
    does NOT solve inside budget 500.

    A naive positive weight (prefer shallower/breadth-first) was tried first and is exactly the
    vacuous case the task warns about: at ``depth=1.0`` this presentation still exhausts the
    budget unsolved with identical ``nodes`` to ``depth=0`` (verified empirically, not asserted
    here). ``depth=-1.0`` (prefer DEEPER states -- dive first) is the case that actually differs:
    it flips ``solved`` False -> True and finds the trivial pair in 86 nodes instead of 500.
    """
    train = load_split("train")
    by = {r["name"]: r for r in train}
    r = by["ms589"]
    assert 4 <= bin_of("ms589") <= 7

    zero = {"segments": [{"upto": None, "w": {"L": 1.0}}]}
    weighted = {"segments": [{"upto": None, "w": {"L": 1.0}, "depth": -1.0}]}

    base = search_fast(r["r1"], r["r2"], MAX_BUDGET, zero, MRL)
    dep = search_fast(r["r1"], r["r2"], MAX_BUDGET, weighted, MRL)

    assert base["solved"] is False and base["nodes"] == MAX_BUDGET
    assert dep["solved"] is True and dep["nodes"] == 86
    assert dep["nodes"] != base["nodes"] or dep["solved"] != base["solved"]


def test_depth_named_inside_the_weight_dict_is_rejected_not_silently_ignored():
    """``depth`` is not a member of ``FEATURES``. ``compile_config`` indexes
    ``w[i, _FIDX[k]]`` for every key in a segment's ``w`` dict, so a config that puts ``"depth"``
    inside ``w`` (rather than as a sibling key next to it) must ``KeyError`` rather than silently
    scoring it as zero -- exactly the typo a config author could make.
    """
    bad_cfg = {"segments": [{"upto": None, "w": {"L": 1.0, "depth": 2.0}}]}
    with pytest.raises(KeyError):
        compile_config(bad_cfg)
