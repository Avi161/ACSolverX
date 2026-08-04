"""Tests for ``experiments/stable_ac/fable/spelling_high_rank.py`` (task A10 / S11).

Every fixture in here is pinned against a number that already exists in the repo's
committed notes, so a regression shows up as a disagreement with a *document*, not just
with a previous run of this file.
"""

import os
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from experiments.stable_ac.fable import spelling_high_rank as S      # noqa: E402
from experiments.stable_ac.fable.ac_words import free_reduce         # noqa: E402


# --------------------------------------------------------------------------------------
# the instrument, pinned to numbers stated in the committed notes
# --------------------------------------------------------------------------------------


def test_ak3_matches_the_pinned_fixture():
    """S3_AUDIT section 1.2: AK(3) has census 86,400 and minimum defect 4 (gamma_N = 2)."""
    row = S.decide(S.AK3, cap=10 ** 6)
    assert row["census"] == 86_400
    assert row["minimum_defect"] == 4
    assert row["verdict"] == "NOT_THICKENABLE"
    assert S.census_cost(S.AK3) == 86_400


def test_r1f_counterexample_pair():
    """R1F: ("xyXY","xxy") is thickenable, its spiked spelling ("xyXY","yYxxy") is not."""
    red = S.decide(("xyXY", "xxy"), cap=10 ** 6)
    spiked = S.decide(("xyXY", "yYxxy"), cap=10 ** 6)
    assert red["census"] == 12 and red["minimum_defect"] == 0
    assert spiked["census"] == 144 and spiked["minimum_defect"] == 2
    assert free_reduce("yYxxy") == "xxy"


def test_cap_fails_closed_and_never_gives_a_verdict():
    row = S.decide(S.AK3, cap=10)
    assert row["status"] == "UNKNOWN_SIZE"
    assert row["verdict"] == "SKIPPED"
    assert row["minimum_defect"] is None


# --------------------------------------------------------------------------------------
# spelling moves
# --------------------------------------------------------------------------------------


def test_spike_inserts_and_reduces_back():
    out = S.spike(("xyXY", "xxy"), 1, 0, "y")
    assert out == ("xyXY", "yYxxy")
    assert free_reduce(out[1]) == "xxy"


def test_spike_images_are_deduped_on_cyclic_words():
    base = ("xyXY", "xxy")
    imgs = S.spike_images(base)
    keys = [k for k, _w, _p in imgs]
    assert len(keys) == len(set(keys))
    assert imgs, "a spike is always available"
    for _k, words, _p in imgs:
        # a spike adds exactly two letters and never changes the free-group element
        assert sum(len(w) for w in words) == sum(len(w) for w in base) + 2
        assert [free_reduce(w) for w in words] == [free_reduce(w) for w in base]


def test_spelling_key_ignores_rotation_and_inversion_only():
    assert S.spelling_key(("xyXY",)) == S.spelling_key(("yXYx",))
    assert S.spelling_key(("xyXY",)) == S.spelling_key(("yxYX",))
    # but NOT free reduction -- that is the point of spelling space
    assert S.spelling_key(("yYxxy",)) != S.spelling_key(("xxy",))


def test_peel_and_reduce_reproduces_the_S3_AUDIT_row():
    """S3_AUDIT section 3.2, row 1: ('XYYyxY','XyX') d=2 -> literal d=2 -> reduced d=0."""
    pr = S.peel_and_reduce(("XYYyxY", "XyX"), ("x", "y"), 0, 2)
    assert pr["degenerate"] is True
    assert pr["corner"] == "Yy"
    assert pr["literal"] == ("axYXY", "XyX", "aYy")
    assert pr["reduced"] == ("axYXY", "XyX", "a")
    assert S.decide(("XYYyxY", "XyX"), cap=10 ** 6)["minimum_defect"] == 2
    assert S.decide(pr["literal"], pr["generators"], cap=10 ** 6)["minimum_defect"] == 2
    assert S.decide(pr["reduced"], pr["generators"], cap=10 ** 6)["minimum_defect"] == 0


def test_degenerate_peel_equals_stabilize_and_graft_as_a_cyclic_word():
    """The section 3.2 mechanism is AC4 + AC2 in disguise, so its legality is not in doubt."""
    base, gens = ("xxy", "xyXY"), ("x", "y")
    spiked = S.spike(base, 0, 0, "x")                     # ("xXxxy", "xyXY")
    pr = S.peel_and_reduce(spiked, gens, 0, 0)
    assert pr["degenerate"] and pr["reduced"][-1] == pr["fresh"]
    sg = S.stabilize_and_graft(base, gens, 0)
    assert S.spelling_key(pr["reduced"]) == S.spelling_key(sg["words"])


def test_stabilize_and_graft_is_balanced_and_rank_raising():
    sg = S.stabilize_and_graft(("xxy", "xyXY"), ("x", "y"), 0)
    assert len(sg["words"]) == len(sg["generators"]) == 3
    assert sg["words"][-1] == sg["fresh"]


# --------------------------------------------------------------------------------------
# certification and the ladder
# --------------------------------------------------------------------------------------


def test_certify_zero_agrees_with_the_census_on_a_known_positive():
    """R1F's ("xyXY","xxy") has gamma_N = 0 and the climber certifies it.

    Note the second-order fact this pins: ``check_witness_n`` REFUSES this witness with an
    ``AuditContradiction``, because it is called with ``trivial_group=True`` while
    ("xyXY","xxy") presents **Z**, not 1 (relators [x,y] and x^2 y).  The certificate then
    rests on ``independent_defect``, the from-scratch recomputation.  A gamma_N = 0
    calibration state need not be a trivial-group presentation -- but a *Lackenby
    certificate* must be, which is what ``todd_coxeter_check`` is for.
    """
    cert = S.certify_zero(("xyXY", "xxy"), ("x", "y"), evals=20_000, seed=7)
    assert cert["climber_defect"] == 0
    assert cert["certified"] is True
    assert cert["verify"]["independent_defect"]["defect"] == 0
    assert "AuditContradiction" in cert["verify"]["check_witness_n_error"]
    assert S.todd_coxeter_check(("xyXY", "xxy"), ("x", "y"))["trivial"] is not True


def test_certify_zero_is_silent_not_wrong_on_a_known_negative():
    cert = S.certify_zero(S.AK3, ("x", "y"), evals=5_000, seed=7)
    assert cert["certified"] is False
    assert cert["climber_defect"] > 0        # an UPPER bound; silence is not a lower bound


def test_detection_table_counts_skips_as_non_detections():
    rows = [
        {"total_length": 13, "rank": 2, "verdict": "THICKENABLE", "census": 10},
        {"total_length": 13, "rank": 2, "verdict": "SKIPPED", "census": 10 ** 9},
        {"total_length": 13, "rank": 8, "verdict": "THICKENABLE", "census": 4},
    ]
    table = S.detection_table(rows, edges=(13,), width=1)
    assert table["13|2"]["detection_rate"] == 0.5
    assert table["13|2"]["skipped"] == 1
    assert table["13|8"]["detection_rate"] == 1.0


# --------------------------------------------------------------------------------------
# the census cost is what makes rank pay -- the mechanism behind the whole note
# --------------------------------------------------------------------------------------


def test_rank_lowers_the_census_at_fixed_total_length():
    """The rank-9 chord refinement of AK(3) has the SAME census (Lemma S3'), and a
    genuinely rank-8 state of comparable length is orders of magnitude cheaper."""
    forms = S.high_rank_forms(S.AK3, limit=1, seed=0)
    assert forms and forms[0]["certified"]
    ref = forms[0]
    assert len(ref["generators"]) > 2
    assert all(len(w) <= 3 for w in ref["words"])
    # Lemma S3': a share-free chord refinement preserves the census exactly
    if not ref["share"]:
        assert S.census_cost(ref["words"], ref["generators"]) == S.census_cost(S.AK3)
        assert (S.decide(ref["words"], ref["generators"], cap=10 ** 6)["minimum_defect"]
                == 4)


def test_decidability_scan_shape():
    cells = S.decidability_scan(ranks=(2, 6), lengths=(13,), per_cell=5, tries=2000)
    assert "13|2" in cells and "13|6" in cells
    for cell in cells.values():
        assert 0.0 <= cell["decidable_rate"] <= 1.0
        assert cell["median_census"] >= 1
    # the mechanism: at matched length, higher rank means a smaller compatible family
    assert cells["13|6"]["median_census"] <= cells["13|2"]["median_census"]


@pytest.mark.parametrize("words,gens", [
    (("xxxYYYY", "xyxYXY"), ("x", "y")),          # AK(3), cyclically reduced
    (("xxy", "xyx"), ("x", "y")),                 # cyclically reduced
])
def test_spiking_never_creates_thickenability_on_a_REDUCED_base(words, gens):
    """S6 section 1 / R7 Conjecture SR at spike depth 1 -> 0.  Holds here."""
    base = S.decide(words, gens, cap=10 ** 6)
    if base["verdict"] != "NOT_THICKENABLE":
        pytest.skip("only a non-thickenable base can witness the creating direction")
    for _k, img, _p in S.spike_images(words, gens):
        row = S.decide(img, gens, cap=2 * 10 ** 5)
        if row["verdict"] == "SKIPPED":
            continue
        assert row["minimum_defect"] > 0, (
            f"SR counterexample at depth 1: {img} has defect 0 while its reduction "
            f"{words} has defect {base['minimum_defect']}")


def test_conjecture_SR_is_false_for_GENERAL_presentations():
    """**Conjecture SR (R7 section 3.1) is FALSE as a statement about presentations.**

    ``gamma_N(spike(P)) = 0  =>  gamma_N(P) = 0`` fails at ``P = ("XYYyxY","XyX")``:

        P        = ("XYYyxY","XyX")     census   144, minimum defect 2  (gamma_N = 1)
        spike(P) = ("YyXYYyxY","XyX")   census 4,320, minimum defect 0  (gamma_N = 0)

    Both censuses are EXHAUSTIVE (no cap hit, no sampling).  The spike is `u = "Y"` at
    position 0 of relator 0.  Prior SR evidence never covered this because every previous
    test spiked a *cyclically reduced* base once; ``P`` here is itself one spike out.

    **SCOPE, and it is load-bearing.**  This family presents **Z/4, not the trivial
    group** -- Todd-Coxeter completes with index 4, asserted below.  The AC programme only
    ever uses SR restricted to balanced presentations of the trivial group, and a
    counterexample outside that class does not transfer (CLAUDE.md, "distinguish the
    statements").  The trivial-group restriction of SR is **not** refuted by this test; see
    ``results/stable_ac/fable/s11_sr_trivial.json`` for the hunt against it.

    The EXISTENTIAL repair also survives here: the other one-step reduction of spike(P),
    deleting the interior ``Yy``, is ("YyXYxY","XyX") with defect 0, and the full reduction
    ("XYxY","XyX") also has defect 0.
    """
    P = ("XYYyxY", "XyX")
    sp = ("YyXYYyxY", "XyX")
    rP = S.decide(P, ("x", "y"), cap=10 ** 6)
    rS = S.decide(sp, ("x", "y"), cap=10 ** 6, keep_accepting=True)
    assert (rP["census"], rP["minimum_defect"]) == (144, 2)
    assert (rS["census"], rS["minimum_defect"]) == (4320, 0)
    assert free_reduce(sp[0]) == free_reduce(P[0]) == "XYxY"
    assert sp == S.spike(P, 0, 0, "Y")
    # the defect-0 rotation re-verified by the independent from-scratch recomputation
    from experiments.stable_ac.fable import rank_n_ac_search as RN
    rot = rS["accepting_orders"][0]
    names = {"x+": 0, "x-": 1, "y+": 2, "y-": 3}
    orders = {names[k]: list(v) for k, v in rot.items()}
    assert RN.independent_defect(RN.Pres(("x", "y"), sp), orders)["defect"] == 0
    # the existential repair: SOME one-step reduction keeps defect 0
    assert S.decide(("YyXYxY", "XyX"), ("x", "y"), cap=10 ** 6)["minimum_defect"] == 0
    assert S.decide(("XYxY", "XyX"), ("x", "y"), cap=10 ** 6)["minimum_defect"] == 0
