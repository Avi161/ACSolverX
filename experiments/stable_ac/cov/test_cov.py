"""Tests for the one-shot CoV transform (case i).

Collected by a bare ``pytest`` (pytest.ini's testpaths includes
``experiments/stable_ac``); run just this pipeline's tests with:

    .venv/bin/python3 -m pytest experiments/stable_ac -q
"""

import json
import os

import pytest

from experiments.greedy_tests.spec.invariants import abs_det
from experiments.greedy_tests.spec.presentation import Presentation
from experiments.greedy_tests.spec.words import inverse, str_to_word, word_to_str
from experiments.stable_ac.cov import cov, run_cov

AK3_R1, AK3_R2 = str_to_word("xyxYXY"), str_to_word("xxxYYYY")


# --- the paper's §4 worked example, pinned exactly --------------------------

def test_golden_paper_example_z_xyx():
    r1s, n1 = cov.substitute_word(AK3_R1, str_to_word("xyx"))
    r2s, n2 = cov.substitute_word(AK3_R2, str_to_word("xyx"))
    assert (r1s, n1) == (str_to_word("zYXY"), 1)
    assert (r2s, n2) == (AK3_R2, 0)

    ok, expr = cov.isolate(r1s)
    assert ok and expr == str_to_word("YzY")

    res = cov.apply_cov_once(AK3_R1, AK3_R2, str_to_word("xyx"))
    assert res.applicable and res.n_cov == 1 and res.iso_index == 0
    assert word_to_str(res.r1) == "XyXXyXXyXXXXX"      # (y⁻¹zy⁻¹)³y⁻⁴ relabeled
    assert word_to_str(res.r2) == "YXyXyX"             # z⁻¹y⁻¹zy⁻¹zy⁻¹ relabeled
    assert res.cap == max(24, 13 + cov.CAP_HEADROOM) == 29


def test_golden_family_path_picks_xy():
    # The plan assumed every length-2 word fails on AK(3); it does not: both
    # xy and its inverse YX occur in r1 = xyxYXY, so substitution removes two
    # x letters at once and leaves zxZY with a single x. First success wins.
    res = cov.change_of_variables(AK3_R1, AK3_R2)
    assert res.z_word == str_to_word("xy")
    assert res.iso_index == 0 and res.n_subs == 2
    assert word_to_str(res.expr) == "Zyz"
    assert word_to_str(res.r1) == "YxxxyXXXX"
    assert word_to_str(res.r2) == "YYxyx"
    assert res.cap == max(24, 9 + cov.CAP_HEADROOM) == 25


# --- abelianization invariant, including a non-|det|=1 case -----------------

def _three_stage_dets(r1, r2, res):
    return (abs_det(Presentation(2, (r1, r2))),
            abs_det(Presentation(3, res.meta["intermediate"])),
            abs_det(Presentation(2, (res.r1, res.r2))))


def test_abs_det_preserved_on_goldens():
    paper = cov.apply_cov_once(AK3_R1, AK3_R2, str_to_word("xyx"))
    family = cov.change_of_variables(AK3_R1, AK3_R2)
    assert _three_stage_dets(AK3_R1, AK3_R2, paper) == (1, 1, 1)
    assert _three_stage_dets(AK3_R1, AK3_R2, family) == (1, 1, 1)


def test_abs_det_preserved_nontrivial_group():
    # ⟨x,y | xyxY, xxyy⟩ has |det| = 4, so this equality is not vacuous 1==1.
    r1, r2 = str_to_word("xyxY"), str_to_word("xxyy")
    res = cov.change_of_variables(r1, r2)
    assert res.z_word == str_to_word("xy") and res.iso_index == 0
    assert word_to_str(res.r1) == "Yxyx" and word_to_str(res.r2) == "YYxx"
    assert _three_stage_dets(r1, r2, res) == (4, 4, 4)


def test_abs_det_preserved_for_every_z_on_benchmark_rows():
    root = run_cov.find_repo_root(os.path.dirname(__file__))
    rows = run_cov.load_rows(run_cov.COV_DEFAULTS["datasets"], root)
    assert len(rows) == 11        # subset_10 + reach_1 (AK(3))

    n_applicable = 0
    for rid, r1s_, r2s_, _src in rows:
        r1, r2 = str_to_word(r1s_), str_to_word(r2s_)
        before = abs_det(Presentation(2, (r1, r2)))
        for z in cov.NAIVE_Z_FAMILY:
            w = z
            a, _ = cov.substitute_word(r1, w)
            b, _ = cov.substitute_word(r2, w)
            inter = Presentation(3, (a, b, cov.defining_relator(w)))
            assert abs_det(inter) == before, (rid, word_to_str(w))
            res = cov.apply_cov_once(r1, r2, w)
            if res is not None:
                after = abs_det(Presentation(2, (res.r1, res.r2)))
                assert after == before, (rid, word_to_str(w))
        if cov.change_of_variables(r1, r2).applicable:
            n_applicable += 1
    assert n_applicable > 0       # the invariant loop above must not be vacuous


# --- edge cases --------------------------------------------------------------

def test_no_occurrence_falls_back_to_original():
    res = cov.change_of_variables((1,), (2,))
    assert not res.applicable and res.n_cov == 0
    assert res.r1 == (1,) and res.r2 == (2,)
    assert res.cap == cov.DEFAULT_CAP


def test_w_equal_to_whole_relator_is_rejected_by_isolation():
    word, n = cov.substitute_word(str_to_word("xyx"), str_to_word("xyx"))
    assert (word, n) == ((3,), 1)
    assert cov.isolate((3,)) == (False, ())     # no x letter left to isolate


def test_zfree_isolator_is_rejected():
    # relator with one x but no z must not isolate (z would be redundant)
    assert cov.isolate(str_to_word("xyy")) == (False, ())


def test_blowup_rejected():
    # x -> YzY triples r2 = x^17 to 51 > REJECT_LEN; r2s keeps 17 x letters so
    # the other isolator fails too -> the z is rejected outright
    assert cov.apply_cov_once(AK3_R1, (1,) * 17, str_to_word("xyx")) is None


def test_empty_relator_rejected():
    # z=xy on ⟨x,y | xyxY, xYxy⟩: either isolation choice free-reduces the
    # other relator to the empty word -> the z must be rejected
    assert cov.apply_cov_once(str_to_word("xyxY"), str_to_word("xYxy"),
                              str_to_word("xy")) is None


def test_degenerate_z_words_rejected():
    assert cov.apply_cov_once(AK3_R1, AK3_R2, (1,)) is None          # too short
    assert cov.apply_cov_once(AK3_R1, AK3_R2, (1, -1)) is None       # reduces to ()


def test_pure_power_z_is_a_candidate():
    # z=xx on AK(3): r2 = xxxYYYY -> zxYYYY, one x left -> isolatable. Pure
    # powers are deliberately IN the family — which words win is the sweep's
    # empirical question, not a rule.
    res = cov.apply_cov_once(AK3_R1, AK3_R2, (1, 1))
    assert res is not None and res.applicable and res.n_subs >= 1


def test_relabel_preserves_signs():
    assert cov.relabel(str_to_word("yYzZ")) == str_to_word("xXyY")
    with pytest.raises(KeyError):
        cov.relabel((1,))       # x must be gone before relabeling


# --- adapters & runner seams --------------------------------------------------

def test_cov_for_greedy_strings():
    r1t, r2t, cap, n_cov, meta = cov.cov_for_greedy("xyxYXY", "xxxYYYY")
    assert (r1t, r2t, cap, n_cov) == ("YxxxyXXXX", "YYxyx", 25, 1)
    assert meta["cov_applicable"] and meta["z_word"] == "xy"
    assert meta["start_total_length_orig"] == 13
    assert meta["start_total_length_cov"] == 14


def test_transformed_flat_repads_to_cap():
    paper = cov.apply_cov_once(AK3_R1, AK3_R2, str_to_word("xyx"))
    flat = cov.transformed_flat(paper)
    assert len(flat) == 2 * paper.cap
    assert flat[:13] == list(paper.r1) and flat[13:paper.cap] == [0] * 16
    assert flat[paper.cap:paper.cap + 6] == list(paper.r2)


def test_run_prefix_identity():
    c = dict(run_cov.COV_DEFAULTS)
    assert run_cov._run_prefix(c, 1000, 11) == "cov_1000_11_zf1_mrl24_cyc_s10r1_"
    c["mode"] = "baseline"
    assert run_cov._run_prefix(c, 100, 11) == "covbase_100_11_mrl24_cyc_s10r1_"


def test_baseline_mode_is_identity():
    c = run_cov.load_config(mode="baseline")
    r1t, r2t, cap, n_cov, extra = run_cov._transform(c, "xyxYXY", "xxxYYYY")
    assert (r1t, r2t, cap, n_cov) == ("xyxYXY", "xxxYYYY", 24, 0)
    assert extra["cov_applicable"] is None and extra["z_word"] is None


# --- subword family & the length-sweep experiment ----------------------------

def test_subword_candidates_ak3():
    fam = cov.subword_candidates(AK3_R1, AK3_R2)
    # the zf1 winner xy and the paper's xyx are both subwords of r1 = xyxYXY
    assert str_to_word("xy") in fam
    assert str_to_word("xyx") in fam
    # pure powers are candidates too (from r2 = xxxYYYY; YY canonicalises to yy)
    assert str_to_word("xx") in fam
    assert str_to_word("yy") in fam
    assert str_to_word("xxx") in fam
    assert str_to_word("yyyy") in fam
    # the cyclic seam is included: Yx wraps r1's boundary (…Y|x…); its
    # canonical member max(Yx, Xy) = Xy is what the family stores
    assert str_to_word("Xy") in fam
    # w and w⁻¹ never both present (same CoV up to inverting z)
    as_set = set(fam)
    assert not any(inverse(w) in as_set and inverse(w) != w for w in fam)
    # deterministic canonical order — sweep row identity depends on it
    assert list(fam) == sorted(fam, key=lambda w: (len(w), w))


def test_enumerate_cov_ak3_valid_and_deduped():
    results = cov.enumerate_cov(AK3_R1, AK3_R2)
    assert results                       # AK(3) admits at least one CoV (z=xy)
    assert any(r.z_word == str_to_word("xy") for r in results)
    pairs = [(r.r1, r.r2) for r in results]
    assert len(pairs) == len(set(pairs))            # no duplicate searches
    assert all(r.applicable and r.n_cov == 1 and r.n_subs >= 1 for r in results)


def test_enumerate_cov_explicit_family_dedup():
    fam = (str_to_word("xy"), str_to_word("xy"))
    assert len(cov.enumerate_cov(AK3_R1, AK3_R2, family=fam)) == 1


def test_enumerate_cov_abs_det_on_benchmark_rows():
    root = run_cov.find_repo_root(os.path.dirname(__file__))
    rows = run_cov.load_rows(run_cov.COV_DEFAULTS["datasets"], root)
    total = 0
    for rid, r1s_, r2s_, _src in rows:
        r1, r2 = str_to_word(r1s_), str_to_word(r2s_)
        before = abs_det(Presentation(2, (r1, r2)))
        for res in cov.enumerate_cov(r1, r2):
            assert abs_det(Presentation(3, res.meta["intermediate"])) == before
            assert abs_det(Presentation(2, (res.r1, res.r2))) == before
            total += 1
    assert total > 0                     # the sweep family must not be vacuous


def test_run_prefix_sweep_identity():
    c = dict(run_cov.COV_DEFAULTS)
    c["experiment_length"] = True
    assert (run_cov._run_prefix(c, 1000, 11)
            == "covsweep_1000_11_sub4p_mrl24_cyc_s10r1_")
    with pytest.raises(ValueError):
        run_cov.load_config(mode="baseline", experiment_length=True)


def _stub_stats():
    return {
        "solved": False, "nodes_explored": 7, "path_length": None,
        "min_relator_length": 5, "min_relator": "xyxYX",
        "max_relator_length": 9, "max_relator": "xyxYXYxxx",
        "max_relator_length_expanded": 9, "max_relator_expanded": "xyxYXYxxx",
    }


def test_sweep_runner_rows_and_resume(tmp_path, monkeypatch):
    csv_p = tmp_path / "reach_tier_9.csv"
    csv_p.write_text("name,r1,r2\nAK(3),xyxYXY,xxxYYYY\n")
    calls = []

    def fake_search(*args, **kwargs):
        calls.append(args)
        return _stub_stats()

    monkeypatch.setattr(run_cov.run_baseline, "greedy_search", fake_search)
    common = dict(datasets=[str(csv_p)], budgets=[100], mode="cov",
                  experiment_length=True, out_dir=str(tmp_path / "out"))
    out = run_cov.run(**common)

    assert os.path.basename(out[0]).startswith("covsweep_100_1_sub4p_mrl24_cyc_r9_")
    rows = [json.loads(ln) for ln in open(out[0])]
    controls = [r for r in rows if r["z_word"] is None]
    variants = [r for r in rows if r["z_word"] is not None]
    assert len(controls) == 1 and controls[0]["n_cov"] == 0
    assert controls[0]["r1"] == "xyxYXY" and controls[0]["max_relator_length_cap"] == 24
    assert variants and all(v["n_cov"] == 1 and v["cov_applicable"] for v in variants)
    assert len(rows) == len(calls)       # one search per (pres, z) row
    keys = {(r["pres_id"], r["z_word"]) for r in rows}
    assert len(keys) == len(rows)        # pair key is unique

    # resume: a second run finds every (pres_id, z_word) done and re-searches nothing
    n_calls = len(calls)
    out2 = run_cov.run(**common)
    assert out2 == out and len(calls) == n_calls
