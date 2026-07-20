"""Tests for the one-shot CoV transform (case i).

Collected by a bare ``pytest`` (pytest.ini's testpaths is ``tests``); run just
this pipeline's tests with:

    .venv/bin/python3 -m pytest tests/stable_ac -q
"""

import glob
import json
import os
import shutil

import pytest
import yaml

from experiments.greedy_tests.spec.invariants import abs_det
from experiments.greedy_tests.spec.presentation import Presentation
from experiments.greedy_tests.spec.words import (
    inverse, reduce_word, rotate, str_to_word, word_to_str)
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


def test_zf2_family_is_every_canonical_cyclically_reduced_word():
    fam = cov.NAIVE_Z_FAMILY
    assert len(fam) == 62                # 6 + 14 + 42 canonical words, len 2..4
    assert {L: sum(1 for w in fam if len(w) == L) for L in (2, 3, 4)} \
        == {2: 6, 3: 14, 4: 42}
    # nothing excluded: pure powers are candidates like any other word
    for s in ("xx", "yy", "xxx", "yyy", "xxxx", "yyyy"):
        assert str_to_word(s) in fam, s
    # every member survives free AND cyclic reduction
    assert all(w[0] != -w[-1] and
               all(a != -b for a, b in zip(w, w[1:])) for w in fam)
    # one member per w ~ w⁻¹ pair, deterministic first-win order
    as_set = set(fam)
    assert not any(inverse(w) in as_set and inverse(w) != w for w in fam)
    assert list(fam) == sorted(fam, key=lambda w: (len(w), w))


def test_golden_family_path_zf3_picks_xx():
    # zf3 first-win on AK(3): Xy now matches via the cyclic seam on both
    # relators, but the full CoV fails end-to-end; xx then fires on
    # r2 = xxxYYYY (-> zxYYYY, one x) and is valid. The old zf1 ordering
    # artifact (xy pinned early) is gone with the hand-picked family.
    res = cov.change_of_variables(AK3_R1, AK3_R2)
    assert res.z_word == str_to_word("xx")
    assert res.iso_index == 1 and res.iso_gen == "x" and res.n_subs == 1
    assert word_to_str(res.expr) == "Zyyyy"
    assert word_to_str(res.r1) == "YxxxxxYXyX"
    assert word_to_str(res.r2) == "YYxxxxYxxxx"
    assert res.cap == max(24, 11 + cov.CAP_HEADROOM) == 27


def test_substitute_word_matches_cyclic_seam():
    # r1 = xyxYXY stores seam …Y|x…; canonical z = Xy (= max(Yx, Xy)).
    # Linear scan misses it; seam pass must replace once → ZyxYX.
    out, n = cov.substitute_word(AK3_R1, str_to_word("Xy"))
    assert n == 1 and word_to_str(out) == "ZyxYX"
    # r2 = xxxYYYY has the same wrap Y|x → a second independent seam hit.
    out2, n2 = cov.substitute_word(AK3_R2, str_to_word("Xy"))
    assert n2 == 1 and word_to_str(out2) == "ZxxYYY"
    # Contiguous hits are unchanged (paper example).
    out3, n3 = cov.substitute_word(AK3_R1, str_to_word("xyx"))
    assert (out3, n3) == (str_to_word("zYXY"), 1)


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
    # Under zf3, seam-capable Xy wins first (was unreachable under linear-only
    # substitution); xx still fails end-to-end (zyy / xyxY, no isolatable x).
    r1, r2 = str_to_word("xyxY"), str_to_word("xxyy")
    res = cov.change_of_variables(r1, r2)
    assert res.z_word == str_to_word("Xy") and res.iso_index == 0
    assert word_to_str(res.r1) == "XyXyxx" and word_to_str(res.r2) == "YYxx"
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


def test_blowup_gate_is_structural_only():
    # x -> YzY triples r2 = x^17 to 51 — above the OLD empirical gate of 48,
    # and rejecting it was a length prior (some presentations solve only from
    # long starts: 629, 539). Under the structural-only default (239 = fast
    # solver's 255-cap minus headroom) it is admitted:
    res = cov.apply_cov_once(AK3_R1, (1,) * 17, str_to_word("xyx"))
    assert res is not None and max(len(res.r1), len(res.r2)) == 51
    assert res.cap == 51 + cov.CAP_HEADROOM == 67
    # the gate itself still works when set explicitly...
    assert cov.apply_cov_once(AK3_R1, (1,) * 17, str_to_word("xyx"),
                              reject_len=48) is None
    # ...and the structural ceiling fires on a true monster: x^81 -> 243 > 239
    assert cov.apply_cov_once(AK3_R1, (1,) * 81, str_to_word("xyx")) is None


def test_cov_branches_returns_every_isolating_branch():
    """521 z=yy/iso=y isolates from BOTH r1' and r2' — two different CoVs.

    first-wins would return only iso_index 0 (total 30) and silently discard
    iso_index 1 (total 16), picking the worse start purely because r1' is tried
    first. Candidate order is an implementation detail, not a principle.
    """
    r1, r2 = str_to_word("YYYYYYYYXyyyyyyyx"), str_to_word("YYYX")
    br = cov.cov_branches(r1, r2, str_to_word("yy"), iso_gen="y")
    assert [b.iso_index for b in br] == [0, 1]
    pairs = [(word_to_str(b.r1), word_to_str(b.r2)) for b in br]
    assert pairs[0] != pairs[1]                       # genuinely different CoVs
    assert [len(b.r1) + len(b.r2) for b in br] == [30, 16]
    # apply_cov_once keeps first-wins for single-transform callers...
    first = cov.apply_cov_once(r1, r2, str_to_word("yy"), iso_gen="y")
    assert first.iso_index == 0
    # ...and can address a specific branch
    assert cov.apply_cov_once(r1, r2, str_to_word("yy"), iso_gen="y",
                              iso_index=1).iso_index == 1
    assert cov.apply_cov_once(r1, r2, str_to_word("yy"), iso_gen="y",
                              iso_index=2) is None
    # the sweep must see both
    keys = {(word_to_str(r.z_word), r.iso_gen, r.iso_index)
            for r in cov.enumerate_cov(r1, r2)}
    assert ("yy", "y", 0) in keys and ("yy", "y", 1) in keys


def test_sweep_row_key_includes_iso_index():
    """Without iso_index the two branches of one (z, iso_gen) collide and
    resume drops the second while reporting the work as finished."""
    rows = [{"pres_id": "521", "z_word": "yy", "iso_gen": "y", "iso_index": 0,
             "solved": False},
            {"pres_id": "521", "z_word": "yy", "iso_gen": "y", "iso_index": 1,
             "solved": False}]
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
        path = f.name
    try:
        done, n_seen, _ = run_cov._read_done_pairs(path)
        assert n_seen == 2
        assert len(done) == 2, "iso_index missing from the key -> rows collide"
        assert ("521", "yy", "y", 0) in done and ("521", "yy", "y", 1) in done
    finally:
        os.unlink(path)


def test_family_tag_stamped_in_every_sweep_row():
    """The rule that made each row, recorded IN the row.

    The tag-bump discipline rests on the filename; nothing else enforces that
    a file's rows all came from one rule. Stamping it per row makes a
    rule-change-without-a-bump detectable afterwards, and survives the jsonl
    being renamed or moved. It must agree with the filename's tag, or the file
    name is lying about its contents.
    """
    c = run_cov.load_config(experiment_length=True)
    entries = _sweep_entries_for(c)
    assert entries, "sweep must produce rows"
    tags = {extra["family_tag"] for _z, _a, _b, _cap, _n, extra in entries}
    assert tags == {cov.SUBWORD_FAMILY_TAG}      # control row included
    assert cov.SUBWORD_FAMILY_TAG in run_cov._run_prefix(c, 100, 1)


def _sweep_entries_for(c):
    return run_cov._sweep_entries(c, "xyxYXY", "xxxYYYY")


def test_aut_canon_reps_stamped_and_detect_a_pure_relabel():
    """The reps are the only sound test of whether a CoV changed coordinates.

    n_subs, iso_index and a shorter total can ALL look like real work on a row
    that is just the input relabeled — so the row carries the two orbit reps
    and `same orbit` is their equality. Stored as reps rather than a bool so
    analysis can also count/group distinct orbits.
    """
    c = run_cov.load_config(experiment_length=True)
    entries = _sweep_entries_for(c)
    ctrl = entries[0][5]
    # the control is the input, so it is trivially in its own orbit
    assert ctrl["aut_canon_orig"] == ctrl["aut_canon_cov"]
    covs = [e[5] for e in entries[1:]]
    assert covs and all(e["aut_canon_orig"] == ctrl["aut_canon_orig"] for e in covs)
    # the sweep must contain BOTH kinds, or the field is decoration
    same = [e for e in covs if e["aut_canon_cov"] == e["aut_canon_orig"]]
    moved = [e for e in covs if e["aut_canon_cov"] != e["aut_canon_orig"]]
    assert same and moved, "AK(3) must show relabels AND real coordinate changes"
    # Every n_subs == 1 row is a relabel. Do NOT attribute this to PROOFS.tex's
    # "Only-occurrence degeneracy" corollary: that corollary rides on the
    # relator-minus-one theorem's two-letter isolator (|w| = |R|-1), and the
    # no-collapse gate rejects exactly those w — so NO shipped row is inside
    # its scope. The reason is the stronger argument pinned in
    # test_n_subs_one_is_an_automorphism_for_any_w_length.
    # NOTE the converse is NOT pinned: n_subs >= 2 does real substitution work
    # and may still land back in the input's orbit, which is exactly why the
    # rep is stored and n_subs is not a proxy for it. On AK(3) the split
    # happens to be clean (1 -> relabel, 2 -> moved); do not read that as a
    # general rule.
    assert all(e["n_subs"] == 1 for e in same)


def _canon_cyc(w):
    """Canonical form under cyclic rotation + whole-word inversion."""
    w = reduce_word(tuple(w), cyclic=True)
    if not w:
        return ()
    return min(rotate(u, -k) for u in (w, inverse(w)) for k in range(len(u)))


def _canon_pair(a, b):
    return tuple(sorted((_canon_cyc(a), _canon_cyc(b))))


def test_n_subs_one_is_an_automorphism_for_any_w_length():
    """n_subs == 1 => the output is the input renamed, for ANY |w|.

    This is STRONGER than PROOFS.tex's "Only-occurrence degeneracy" corollary,
    which rides on the relator-minus-one theorem's two-letter isolator
    (|w| = |R|-1) — a case the no-collapse gate rejects outright, so the
    corollary covers NO shipped row. The general argument: the lone occurrence
    sits in R, so S_z = S and R_z is forced to be the isolator (S has no z, and
    defining-relator isolation is off here). Isolation needs exactly one a in
    R_z = z^eta t, so t is pure b-powers around it: t = b^m a^eps b^n. Rotating
    gives a = (b^n z^eta b^m)^-eps =: alpha, and psi: a -> alpha, b -> b is an
    ISOMORPHISM F(a,b) -> F(b,z) (inverse z -> (b^-n a^-eps b^-m)^eta) for any
    |w|. The kept relators are then psi(S) and z^-1 psi(w), and
    psi(R) = psi(w)^eta z^-eta — a rotation of the latter when eta=+1, its
    inverse when eta=-1. So output == {psi(R), psi(S)} up to order/rotation/
    inversion, with psi an automorphism after the relabel.

    Pinned as the IDENTITY, not merely the orbit conclusion: aut_canon agreeing
    would also pass if the transform silently changed to some other rename, and
    the identity is what the proof actually claims. Verified offline on
    544326/544326 rows over relator words of length 2..5 (441606 at |R|-1-|w|=1,
    102720 at gap 2, none at the corollary's gap 0); this tier pins the AK(3)
    rows plus a pure-power z (the z=xx case the corollary cannot speak to).
    """
    cases = [(AK3_R1, AK3_R2), (str_to_word("xx"), str_to_word("xyyy")),
             (str_to_word("xxyxy"), str_to_word("xyXY"))]
    n_checked = n_purepow = 0
    for r1, r2 in cases:
        for res in cov.enumerate_cov(r1, r2):
            if res.n_subs != 1:
                continue
            # which original relator carries the single selected occurrence?
            in_r1 = cov.substitute_word(reduce_word(r1, cyclic=True),
                                        res.z_word)[1] == 1
            src, oth = (r1, r2) if in_r1 else (r2, r1)
            a = cov.X_GEN if res.iso_gen == "x" else cov.Y_GEN
            psi = lambda w: cov.substitute_generator(w, a, res.expr)
            pred = _canon_pair(
                cov.relabel(psi(reduce_word(src, cyclic=True)), res.iso_gen),
                cov.relabel(psi(reduce_word(oth, cyclic=True)), res.iso_gen))
            assert pred == _canon_pair(res.r1, res.r2), (
                word_to_str(res.z_word), res.iso_gen, res.iso_index)
            # the shipped family never produces the corollary's gap-0 isolator
            assert len(reduce_word(src, cyclic=True)) - 1 - len(res.z_word) >= 1
            n_checked += 1
            if len({abs(g) for g in res.z_word}) == 1:
                n_purepow += 1
    assert n_checked, "no n_subs==1 rows — the test proves nothing"
    assert n_purepow, "no pure-power z (the z=xx case) exercised"


def test_aut_canon_cap_does_not_truncate_on_this_data():
    """aut_canon(pair, level_cap=50000) BREAKS out when the orbit level is
    bigger than the cap, returning the min of a partial exploration — a
    truncated rep would make the stored fields cap-dependent approximations
    rather than facts. Measured 0/150 on the longest benchmark outputs; this
    pins it for the rows the test suite can afford. If this ever fails, the
    aut_canon_* fields must move to an analysis pass where the cap is visible.
    """
    from experiments.equivalence_classes.lib.autcanon import aut_canon
    entries = _sweep_entries_for(run_cov.load_config(experiment_length=True))
    pairs = sorted(((e[1], e[2]) for e in entries),
                   key=lambda p: -(len(p[0]) + len(p[1])))[:12]
    for a, b in pairs:
        assert aut_canon((a, b), level_cap=50_000)[1] \
            == aut_canon((a, b), level_cap=400_000)[1], (a, b)


def test_family_tag_tracks_the_universe_family():
    """A different family must stamp a different tag — otherwise the field is
    decoration rather than a tripwire."""
    c = run_cov.load_config(experiment_length=True, z_source="universe")
    tags = {extra["family_tag"] for _z, _a, _b, _cap, _n, extra
            in _sweep_entries_for(c)}
    assert tags == {f"uni{c['universe_max_len']}xys"}
    assert cov.SUBWORD_FAMILY_TAG not in tags


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


# --- universe family (z need not occur; defining-relator isolation) -----------

def test_universe_candidates_canonical():
    fam2 = cov.universe_candidates(2, 2)
    assert set(fam2) == {str_to_word(s) for s in ("xx", "yy", "xy", "yx", "yX", "Xy")}
    fam4 = cov.universe_candidates(2, 4)
    # 12 + 36 + 108 reduced words, exactly halved by w ~ w⁻¹ (no fixed points)
    assert len(fam4) == 78
    assert list(fam4) == sorted(fam4, key=lambda w: (len(w), w))
    as_set = set(fam4)
    assert not any(inverse(w) in as_set and inverse(w) != w for w in fam4)


def test_universe_cov_nonoccurring_word():
    # z=xyy occurs nowhere in AK(3) -> default mode rejects it, universe mode
    # isolates from the defining relator Zxyy (one x): x = zYY, a pure Nielsen
    # re-coordinatisation of BOTH relators, no substitution at all.
    w = str_to_word("xyy")
    assert cov.apply_cov_once(AK3_R1, AK3_R2, w) is None
    res = cov.apply_cov_once(AK3_R1, AK3_R2, w, allow_defining_iso=True)
    assert res.applicable and res.iso_index == 2 and res.n_subs == 0
    assert word_to_str(res.expr) == "zYY"
    assert word_to_str(res.r1) == "yXyXYX"
    assert word_to_str(res.r2) == "yXXyXXyXXXXXX"
    assert res.cap == max(24, 13 + cov.CAP_HEADROOM) == 29
    assert _three_stage_dets(AK3_R1, AK3_R2, res) == (1, 1, 1)


def test_universe_two_x_nonoccurring_rejected():
    # w=xxyy neither occurs nor has a single x OR a single y: no isolation
    # path for either target
    assert cov.apply_cov_once(AK3_R1, AK3_R2, str_to_word("xxyy"),
                              allow_defining_iso=True) is None
    assert cov.apply_cov_once(AK3_R1, AK3_R2, str_to_word("xxyy"),
                              allow_defining_iso=True, iso_gen="y") is None


def test_universe_output_pairs_superset_of_subwords():
    """Every subword z is a reduced word, so the universe family contains the
    subword family and its outputs are a superset.

    The universe bound is DERIVED from the subword family, never pinned: the
    subword family has no |w| knob (no-collapse is its only length rule), so a
    universe capped at some fixed K is simply a different family and the
    containment would not hold. Pinning 4 here passed only while the subword
    family was itself capped at 4.
    """
    fam = cov.subword_candidates(AK3_R1, AK3_R2)
    max_len = max(len(w) for w in fam)
    assert max_len > 4, "AK(3) must exercise z longer than the old global K"
    sub = cov.enumerate_cov(AK3_R1, AK3_R2)
    uni = cov.enumerate_cov(AK3_R1, AK3_R2,
                            family=cov.universe_candidates(2, max_len),
                            allow_defining_iso=True)
    sub_pairs = {(r.r1, r.r2) for r in sub}
    uni_pairs = {(r.r1, r.r2) for r in uni}
    assert sub_pairs <= uni_pairs and len(uni_pairs) > len(sub_pairs)


def test_universe_abs_det_on_benchmark_rows():
    root = run_cov.find_repo_root(os.path.dirname(__file__))
    rows = run_cov.load_rows(run_cov.COV_DEFAULTS["datasets"], root)
    fam = cov.universe_candidates(2, 3)
    by_gen = {"x": 0, "y": 0}
    for rid, r1s_, r2s_, _src in rows:
        r1, r2 = str_to_word(r1s_), str_to_word(r2s_)
        before = abs_det(Presentation(2, (r1, r2)))
        for res in cov.enumerate_cov(r1, r2, family=fam, allow_defining_iso=True):
            assert _three_stage_dets(r1, r2, res) == (before,) * 3, \
                (rid, word_to_str(res.z_word))
            by_gen[res.iso_gen] += 1
    assert by_gen["x"] > 0 and by_gen["y"] > 0


def test_subword_relator_minus_one_boundary():
    """w = a relator minus its last letter shortens that relator to z·g, so
    isolation from it yields g = z^±1 — a pure re-lettering of coordinates.
    If that was w's only occurrence, the output is the ORIGINAL pair up to
    relator order / rotation / letter names (a redundant ~control start).
    But when w also fires elsewhere, the same boundary word does real work:
    it substitutes the relation g = rest⁻¹ into the other relator. Both
    kinds live in sub4pxy today (short-relator benchmark rows); per the
    empiricism rule neither is filtered out (PIPELINE.md §5)."""
    # only occurrence -> trivial: output == (r2, rotation of r1)
    res = cov.apply_cov_once(AK3_R1, AK3_R2, AK3_R1[:-1], iso_gen="y")
    assert word_to_str(res.expr) == "z" and res.n_subs == 1
    assert (word_to_str(res.r1), word_to_str(res.r2)) == ("xxxYYYY", "YxyxYX")
    assert word_to_str(AK3_R1) in word_to_str(res.r2) * 2   # a rotation of r1
    # multi-occurrence -> real compression (pres 496: 18 letters -> 10)
    r1, r2 = str_to_word("YYYYYYYXyyyyyyx"), str_to_word("YYX")
    res2 = cov.apply_cov_once(r1, r2, str_to_word("YY"), iso_gen="x")
    assert word_to_str(res2.expr) == "z" and res2.n_subs == 7
    assert (word_to_str(res2.r1), word_to_str(res2.r2)) == ("yyyXYYY", "YXX")
    assert len(res2.r1) + len(res2.r2) < len(r1) + len(r2)


def test_universe_iso2_expr_is_nielsen_shaped():
    """One-shot defining-relator isolation (iso_index 2) realizes exactly the
    elementary Nielsen re-coordinatisations: a freely reduced w with one
    letter of the eliminated generator is forced into kept^a·elim^±1·kept^b
    (a, b in Z), so expr is a power of the kept generator on each side of
    exactly one ±z. This is the classical basis condition — (y, w) is a free
    basis of F2 iff w = y^a x^±1 y^b — so the "exactly one ±g" gate IS the
    set of valid generator-keeping CoVs, not a filter over it (PIPELINE.md
    §5). iso 0/1 exprs are relator-mediated and escape this shape (zxZ, two
    z-letters, in the z=xy golden)."""
    root = run_cov.find_repo_root(os.path.dirname(__file__))
    rows = run_cov.load_rows(run_cov.COV_DEFAULTS["datasets"], root)
    fam = cov.universe_candidates(2, 4)
    kept = {"x": cov.Y_GEN, "y": cov.X_GEN}
    seen = {"x": 0, "y": 0}
    for rid, r1s_, r2s_, _src in rows:
        r1, r2 = str_to_word(r1s_), str_to_word(r2s_)
        for res in cov.enumerate_cov(r1, r2, family=fam, allow_defining_iso=True):
            if res.iso_index != 2:
                continue
            seen[res.iso_gen] += 1
            z_at = [i for i, g in enumerate(res.expr) if abs(g) == cov.Z_GEN]
            assert len(z_at) == 1, (rid, word_to_str(res.z_word), res.expr)
            for block in (res.expr[:z_at[0]], res.expr[z_at[0] + 1:]):
                assert len(set(block)) <= 1, (rid, res.expr)   # one power g^a
                assert all(abs(g) == kept[res.iso_gen] for g in block)
    assert seen["x"] > 0 and seen["y"] > 0


def test_xy_family_output_pairs_superset_of_x_only():
    # the xy rule strictly extends the retired x-only rule on AK(3)
    x_only = cov.enumerate_cov(AK3_R1, AK3_R2, iso_targets=("x",))
    both = cov.enumerate_cov(AK3_R1, AK3_R2)
    x_pairs = {(r.r1, r.r2) for r in x_only}
    both_pairs = {(r.r1, r.r2) for r in both}
    assert x_pairs <= both_pairs and len(both_pairs) > len(x_pairs)
    assert all(r.iso_gen == "x" for r in x_only)


# --- y-isolation (either generator may be eliminated at destabilization) ------

def test_golden_y_isolation_universe_z_yxx():
    # z=yxx occurs nowhere in AK(3) and carries TWO x -> no x-isolation even in
    # universe mode. But it has exactly ONE y, so the defining relator Zyxx
    # isolates y: y = zXX (the y-Nielsen move y -> zx⁻²). Survivors mention
    # (x,z); relabel z -> y. Hand-verified twice.
    w = str_to_word("yxx")
    assert cov.apply_cov_once(AK3_R1, AK3_R2, w,
                              allow_defining_iso=True, iso_gen="x") is None
    res = cov.apply_cov_once(AK3_R1, AK3_R2, w,
                             allow_defining_iso=True, iso_gen="y")
    assert res.applicable and res.iso_index == 2 and res.iso_gen == "y"
    assert res.n_subs == 0
    assert word_to_str(res.expr) == "zXX"
    assert word_to_str(res.r1) == "xyxYxY"
    assert word_to_str(res.r2) == "xxxxxYxxYxxYxxY"
    assert res.cap == max(24, 15 + cov.CAP_HEADROOM) == 31
    assert _three_stage_dets(AK3_R1, AK3_R2, res) == (1, 1, 1)


def test_golden_y_isolation_subword_z_xy():
    # The same z=xy that drives worked example B, eliminating y instead:
    # r1 -> zxZY has exactly one Y (and one x), so BOTH targets isolate from
    # it — two genuinely different coordinate systems from one z word.
    # y = zxZ; hand-verified twice.
    res = cov.apply_cov_once(AK3_R1, AK3_R2, str_to_word("xy"), iso_gen="y")
    assert res.applicable and res.iso_index == 0 and res.iso_gen == "y"
    assert res.n_subs == 2
    assert word_to_str(res.expr) == "zxZ"
    assert word_to_str(res.r1) == "xxxyXXXXY"
    assert word_to_str(res.r2) == "YxyxY"
    assert res.cap == max(24, 9 + cov.CAP_HEADROOM) == 25
    assert _three_stage_dets(AK3_R1, AK3_R2, res) == (1, 1, 1)
    # and the x-eliminating sibling is a DIFFERENT pair (worked example B)
    res_x = cov.apply_cov_once(AK3_R1, AK3_R2, str_to_word("xy"), iso_gen="x")
    assert (word_to_str(res_x.r1), word_to_str(res_x.r2)) == ("YxxxyXXXX", "YYxyx")
    assert (res.r1, res.r2) != (res_x.r1, res_x.r2)


def test_zfree_y_isolator_is_rejected():
    # one y, no z: y-isolation must refuse exactly like the x gate does
    assert cov.isolate(str_to_word("yxx"), x=cov.Y_GEN) == (False, ())


def test_xy_symmetry_oracle():
    # Swapping the generators sigma = (x <-> y) commutes with every stage of
    # the transform, and relabel_x . sigma == relabel_y, so eliminating y on P
    # with z=w must EQUAL eliminating x on sigma(P) with z=sigma(w) — same
    # output pair, cap, iso_index, n_subs. Run over every benchmark row and
    # both family kinds; this is an independent oracle for the y path.
    sigma_map = {1: 2, -1: -2, 2: 1, -2: -1, 3: 3, -3: -3}

    def sigma(word):
        return tuple(sigma_map[g] for g in word)

    root = run_cov.find_repo_root(os.path.dirname(__file__))
    rows = run_cov.load_rows(run_cov.COV_DEFAULTS["datasets"], root)
    n_compared = 0
    for _rid, r1s_, r2s_, _src in rows:
        r1, r2 = str_to_word(r1s_), str_to_word(r2s_)
        fams = ((cov.subword_candidates(r1, r2), False),
                (cov.universe_candidates(2, 3), True))
        for fam, def_iso in fams:
            for w in fam:
                res_y = cov.apply_cov_once(r1, r2, w, iso_gen="y",
                                           allow_defining_iso=def_iso)
                res_x = cov.apply_cov_once(sigma(r1), sigma(r2), sigma(w),
                                           iso_gen="x",
                                           allow_defining_iso=def_iso)
                assert (res_y is None) == (res_x is None), word_to_str(w)
                if res_y is not None:
                    assert (res_y.r1, res_y.r2, res_y.cap, res_y.iso_index,
                            res_y.n_subs) \
                        == (res_x.r1, res_x.r2, res_x.cap, res_x.iso_index,
                            res_x.n_subs), word_to_str(w)
                    n_compared += 1
    assert n_compared > 0


def test_relabel_preserves_signs():
    assert cov.relabel(str_to_word("yYzZ")) == str_to_word("xXyY")
    with pytest.raises(KeyError):
        cov.relabel((1,))       # x must be gone before relabeling
    # y-elimination: x stays x, z -> y
    assert cov.relabel(str_to_word("xXzZ"), "y") == str_to_word("xXyY")
    with pytest.raises(KeyError):
        cov.relabel((2,), "y")  # y must be gone before relabeling


# --- adapters & runner seams --------------------------------------------------

def test_cov_for_greedy_strings():
    r1t, r2t, cap, n_cov, meta = cov.cov_for_greedy("xyxYXY", "xxxYYYY")
    assert (r1t, r2t, cap, n_cov) == ("YxxxxxYXyX", "YYxxxxYxxxx", 27, 1)
    assert meta["cov_applicable"] and meta["z_word"] == "xx"
    assert meta["iso_gen"] == "x"
    assert meta["start_total_length_orig"] == 13
    assert meta["start_total_length_cov"] == 21


def test_transformed_flat_repads_to_cap():
    paper = cov.apply_cov_once(AK3_R1, AK3_R2, str_to_word("xyx"))
    flat = cov.transformed_flat(paper)
    assert len(flat) == 2 * paper.cap
    assert flat[:13] == list(paper.r1) and flat[13:paper.cap] == [0] * 16
    assert flat[paper.cap:paper.cap + 6] == list(paper.r2)


def test_run_prefix_identity():
    c = dict(run_cov.COV_DEFAULTS)
    assert run_cov._run_prefix(c, 1000, 11) == "cov_1000_11_zf3_mrl24_cyc_s10r1_"
    c["mode"] = "baseline"
    assert run_cov._run_prefix(c, 100, 11) == "covbase_100_11_mrl24_cyc_s10r1_"


def test_shipped_yaml_cannot_shadow_the_family_tag():
    """config_cov.yaml once carried z_family: zf1 after the code moved to zf2
    (now zf3) — load_config applies the yaml OVER COV_DEFAULTS, so a yaml
    copy of an identity tag silently mislabels files (and resumes the wrong
    family's rows). The tag's only source of truth is cov.Z_FAMILY_TAG."""
    path = os.path.join(os.path.dirname(cov.__file__), "config_cov.yaml")
    c = run_cov.load_config(path)
    assert c["z_family"] == cov.Z_FAMILY_TAG


def test_subword_family_has_no_length_knob():
    """The subword family's length rule is no-collapse and nothing else.

    `subword_max_len` was a fixed global K that bounded |w| for every
    presentation; it is GONE, not renamed. A yaml that resurrects the key
    would read as if it still bounds the sweep while changing nothing — the
    same shadowing failure as an identity tag mirrored in yaml — so pin its
    absence from BOTH the defaults and the shipped yaml.
    """
    assert "subword_max_len" not in run_cov.COV_DEFAULTS
    path = os.path.join(os.path.dirname(cov.__file__), "config_cov.yaml")
    with open(path) as f:
        raw = yaml.safe_load(f)
    assert "subword_max_len" not in raw
    assert cov.SUBWORD_FAMILY_TAG in run_cov._run_prefix(
        dict(run_cov.load_config(path), experiment_length=True), 100, 1)


def test_baseline_mode_is_identity():
    c = run_cov.load_config(mode="baseline")
    r1t, r2t, cap, n_cov, extra = run_cov._transform(c, "xyxYXY", "xxxYYYY")
    assert (r1t, r2t, cap, n_cov) == ("xyxYXY", "xxxYYYY", 24, 0)
    assert extra["cov_applicable"] is None and extra["z_word"] is None


# --- subword family & the length-sweep experiment ----------------------------

def test_subword_no_collapse_gate_is_cross_relator():
    """A z is judged by what it does to EVERY relator, not by where it was read.

    r1 = xyxxy, r2 = yxxy, w = yxx: |w| = 3 = |r1| - 2, so w is a legitimate
    interior subword of r1 (-> xzy) and any per-relator |w| <= |r| - 2 rule
    keeps it. But w also occurs in r2 and takes it to zy — the two-letter
    isolator z^eta a^eps, which the relator-minus-one factorization theorem
    proves is ordinary rank-two substitution plus a signed rename. Its outputs
    are (yx, YYXY) and (X, YYx): primitive relators, i.e. starts that solve in
    ~1 node and measure nothing.
    """
    r1, r2 = str_to_word("xyxxy"), str_to_word("yxxy")
    w = str_to_word("yxx")
    # the gate's premise: w IS interior to r1 and DOES collapse r2
    assert len(w) <= len(reduce_word(r1, cyclic=True)) - 2
    assert len(cov.substitute_word(r1, w)[0]) >= cov.MIN_TRANSFORMED_LEN
    assert len(cov.substitute_word(r2, w)[0]) < cov.MIN_TRANSFORMED_LEN
    # ... so the family drops it, under either canonical spelling
    fam = cov.subword_candidates(r1, r2)
    assert w not in fam and inverse(w) not in fam
    # and it would otherwise have been a valid CoV — the gate is what kills it
    assert cov.apply_cov_once(r1, r2, w, iso_gen="x") is not None
    assert all(r.z_word != w for r in cov.enumerate_cov(r1, r2))


def test_subword_no_collapse_subsumes_relator_minus_one():
    """|w| = |r| - 1 collapses that relator to 2 and |w| = |r| collapses it to
    1, so the no-collapse gate needs no separate |w| bound. 496 is the proofs'
    worked example: w = YY takes r2 = YYX to zX."""
    r1, r2 = str_to_word("YYYYYYYXyyyyyyx"), str_to_word("YYX")
    fam = cov.subword_candidates(r1, r2)
    assert str_to_word("YY") not in fam and str_to_word("yy") not in fam
    for w in fam:
        for rel in (r1, r2):
            sub, n_subs = cov.substitute_word(rel, w)
            assert not (n_subs and len(sub) < cov.MIN_TRANSFORMED_LEN)


def test_subword_family_is_unbounded_in_length():
    """No global K: a z longer than the old cap of 4 must survive when it
    collapses nothing. AK(3)'s r2 = xxxYYYY (len 7) admits |w| = 5."""
    fam = cov.subword_candidates(AK3_R1, AK3_R2)
    assert max(len(w) for w in fam) == 5
    assert str_to_word("Xyyyy") in fam


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
    # a duplicated z contributes nothing new: one row per (z, iso target)
    fam = (str_to_word("xy"), str_to_word("xy"))
    res = cov.enumerate_cov(AK3_R1, AK3_R2, family=fam)
    assert [r.iso_gen for r in res] == ["x", "y"]
    assert len(cov.enumerate_cov(AK3_R1, AK3_R2, family=fam,
                                 iso_targets=("x",))) == 1


def test_enumerate_cov_abs_det_on_benchmark_rows():
    root = run_cov.find_repo_root(os.path.dirname(__file__))
    rows = run_cov.load_rows(run_cov.COV_DEFAULTS["datasets"], root)
    by_gen = {"x": 0, "y": 0}
    for rid, r1s_, r2s_, _src in rows:
        r1, r2 = str_to_word(r1s_), str_to_word(r2s_)
        before = abs_det(Presentation(2, (r1, r2)))
        for res in cov.enumerate_cov(r1, r2):
            assert abs_det(Presentation(3, res.meta["intermediate"])) == before
            assert abs_det(Presentation(2, (res.r1, res.r2))) == before
            by_gen[res.iso_gen] += 1
    # neither half of the xy family rule may be vacuous on the invariant check
    assert by_gen["x"] > 0 and by_gen["y"] > 0


def test_run_prefix_sweep_identity():
    c = dict(run_cov.COV_DEFAULTS)
    c["experiment_length"] = True
    # literal on purpose: this is the tripwire for an ACCIDENTAL family-tag
    # change. Bumping the tag is deliberate and must edit this line too.
    assert (run_cov._run_prefix(c, 1000, 11)
            == "covsweep_1000_11_subnc2pxysb_mrl24_cyc_s10r1_")
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

    assert os.path.basename(out[0]).startswith("covsweep_100_1_subnc2pxysb_mrl24_cyc_r9_")
    rows = [json.loads(ln) for ln in open(out[0])]
    controls = [r for r in rows if r["z_word"] is None]
    variants = [r for r in rows if r["z_word"] is not None]
    assert len(controls) == 1 and controls[0]["n_cov"] == 0
    assert controls[0]["r1"] == "xyxYXY" and controls[0]["max_relator_length_cap"] == 24
    assert controls[0]["iso_gen"] is None
    assert variants and all(v["n_cov"] == 1 and v["cov_applicable"] for v in variants)
    assert len(rows) == len(calls)       # one search per (pres, z, iso_gen) row
    keys = {(r["pres_id"], r["z_word"], r["iso_gen"]) for r in rows}
    assert len(keys) == len(rows)        # triple key is unique...
    z_only = {(r["pres_id"], r["z_word"]) for r in rows}
    assert len(z_only) < len(rows)       # ...and NOT reducible to (pres, z):
    assert {v["iso_gen"] for v in variants} == {"x", "y"}   # some z go both ways

    # resume: a second run finds every (pres_id, z_word, iso_gen) done and
    # re-searches nothing
    n_calls = len(calls)
    out2 = run_cov.run(**common)
    assert out2 == out and len(calls) == n_calls


# --- HIGH_SPEEDUP (result-neutral fast solver + path recovery) -----------------

def _spy_searches(monkeypatch, solved):
    """Replace the greedy seam with a spy; returns the list of call kwargs."""
    calls = []

    def spy(r1, r2, budget, **kw):
        calls.append(dict(kw))
        s = dict(_stub_stats())
        if solved:
            s.update(solved=True, path_length=3,
                     path_moves=["r1 <- r1 . r2"] * 3)
        return s

    monkeypatch.setattr(run_cov.run_baseline, "greedy_search", spy)
    return calls


def _sweep_common(tmp_path):
    csv_p = tmp_path / "reach_tier_9.csv"
    csv_p.write_text("name,r1,r2\nAK(3),xyxYXY,xxxYYYY\n")
    return dict(datasets=[str(csv_p)], budgets=[100], mode="cov",
                experiment_length=True, out_dir=str(tmp_path / "out"))


def test_high_speedup_dispatch_and_path_recovery(tmp_path, monkeypatch):
    # unsolved rows: exactly one fast call each
    calls = _spy_searches(monkeypatch, solved=False)
    out = run_cov.run(**_sweep_common(tmp_path), high_speedup=True)
    rows = [json.loads(ln) for ln in open(out[0])]
    assert len(calls) == len(rows)
    assert all(kw["high_speedup"] is True for kw in calls)


def test_high_speedup_resolves_solved_rows_for_the_path(tmp_path, monkeypatch):
    # solved rows: fast call, then the normal-solver recovery re-solve
    calls = _spy_searches(monkeypatch, solved=True)
    out = run_cov.run(**_sweep_common(tmp_path), high_speedup=True)
    rows = [json.loads(ln) for ln in open(out[0])]
    assert len(calls) == 2 * len(rows)
    assert [kw["high_speedup"] for kw in calls] == [True, False] * len(rows)


def test_high_speedup_off_stays_on_the_normal_solver(tmp_path, monkeypatch):
    calls = _spy_searches(monkeypatch, solved=True)
    out = run_cov.run(**_sweep_common(tmp_path))          # default: off
    rows = [json.loads(ln) for ln in open(out[0])]
    assert len(calls) == len(rows)                        # no recovery pass
    assert all(kw["high_speedup"] is False for kw in calls)


def test_run_prefix_neutral_to_high_speedup():
    # result-neutral -> outside the filename identity; files resume across modes
    for sweep in (False, True):
        c = dict(run_cov.COV_DEFAULTS)
        c["experiment_length"] = sweep
        p = run_cov._run_prefix(c, 1000, 11)
        assert run_cov._run_prefix({**c, "high_speedup": True}, 1000, 11) == p


def test_resume_interoperates_across_modes(tmp_path, monkeypatch):
    calls = _spy_searches(monkeypatch, solved=False)
    common = _sweep_common(tmp_path)
    out1 = run_cov.run(**common)
    n_slow = len(calls)
    assert n_slow > 0 and all(kw["high_speedup"] is False for kw in calls)
    out2 = run_cov.run(**common, high_speedup=True)
    assert out2 == out1 and len(calls) == n_slow, \
        "the fast rerun must resume the slow run's file, not re-search"


def test_fast_and_slow_micro_runs_write_identical_rows(tmp_path):
    """No monkeypatch: real searches both ways on benchmark presentation 491
    (4 of its 17 sweep starts solve at budget 100, so the recovery re-solve
    runs for real). Rows must match on every field except ``time_seconds``
    and the three min/max relator STRINGS — those are tie-broken over a set
    in the normal solver (PYTHONHASHSEED, documented repo-wide) while the
    compact solver pins first-seen, so only their lengths are contractual.
    Paths ARE compared exactly: a solved fast row's path comes from the
    normal-solver recovery, so it must be bit-identical."""
    csv_p = tmp_path / "benchmark_subset_1.csv"
    csv_p.write_text("pres_id,r1,r2\n491,YYYYYYXyyyyyx,YYXyyxyx\n")
    noncontractual = {"time_seconds", "min_relator", "max_relator",
                      "max_relator_expanded"}
    got = {}
    for high, sub in ((False, "slow"), (True, "fast")):
        out = run_cov.run(datasets=[str(csv_p)], budgets=[100], mode="cov",
                          experiment_length=True,
                          out_dir=str(tmp_path / sub), high_speedup=high)
        rows = [json.loads(ln) for ln in open(out[0])]
        got[sub] = [{k: v for k, v in r.items() if k not in noncontractual}
                    for r in rows]
    assert got["slow"] == got["fast"]
    solved = [r for r in got["fast"] if r["solved"]]
    assert solved, "the fixture must exercise the recovery path"
    assert all(r["path_moves"] for r in solved)


def test_run_prefix_universe_identity_and_validation():
    c = dict(run_cov.COV_DEFAULTS)
    c["experiment_length"], c["z_source"] = True, "universe"
    assert (run_cov._run_prefix(c, 1000, 11)
            == "covsweep_1000_11_uni4xys_mrl24_cyc_s10r1_")
    with pytest.raises(ValueError):
        run_cov.load_config(z_source="universe")            # needs the sweep
    with pytest.raises(ValueError):
        run_cov.load_config(z_source="anything-else")


# --- CHUNKED SWEEPS (stride partition, chunk-file identity, merge) -------------

def test_chunk_rows_stride_partition():
    rows = [(f"p{j}", "r1", "r2", "src") for j in range(7)]
    parts = [run_cov._chunk_rows(rows, 3, i) for i in (1, 2, 3)]
    # covers everything, disjoint, stride (not blocks), near-equal sizes
    assert sorted(sum(parts, [])) == sorted(rows)
    assert parts[0] == [rows[0], rows[3], rows[6]]
    assert parts[1] == [rows[1], rows[4]]
    assert parts[2] == [rows[2], rows[5]]


def test_run_prefix_chunk_identity():
    c = dict(run_cov.COV_DEFAULTS)
    c["experiment_length"] = True
    base = run_cov._run_prefix(c, 1000, 66)
    ch = dict(c, use_chunks=True, chunks=3, chunk_index=2)
    # the chunk is a different row subset -> in the identity; n_rows stays the
    # FULL dataset size so the merged file's name is exactly the base prefix
    assert run_cov._run_prefix(ch, 1000, 66) == base + "c2of3_"
    # use_chunks without a chunk_index (the parallel parent) resolves nothing
    assert run_cov._run_prefix(dict(ch, chunk_index=None), 1000, 66) == base
    with pytest.raises(ValueError):
        run_cov.load_config(use_chunks=True, chunks=1)
    with pytest.raises(ValueError):
        run_cov.load_config(use_chunks=True, chunks=3, chunk_index=4)


def test_unchunked_resume_never_globs_a_chunk_file(tmp_path, monkeypatch):
    calls = _spy_searches(monkeypatch, solved=False)
    common = _sweep_common(tmp_path)
    ch1 = run_cov.run(**common, use_chunks=True, chunks=2, chunk_index=1,
                      chunk_procs=1)
    assert "_c1of2_" in os.path.basename(ch1[0])
    n_chunk_rows = sum(1 for _ in open(ch1[0]))
    # an unchunked run in the same out_dir must open a FRESH file, not resume
    # into the chunk file (a different row subset with the same name prefix)
    out = run_cov.run(**common)
    assert "_c1of2_" not in os.path.basename(out[0]) and out[0] != ch1[0]
    assert sum(1 for _ in open(ch1[0])) == n_chunk_rows


def test_chunked_sweep_merges_to_the_unchunked_rows(tmp_path, monkeypatch):
    _spy_searches(monkeypatch, solved=False)
    csv_p = tmp_path / "reach_tier_9.csv"
    csv_p.write_text("name,r1,r2\nAK(3),xyxYXY,xxxYYYY\nW4,xyyxY,yxxxY\n")
    common = dict(datasets=[str(csv_p)], budgets=[100], mode="cov",
                  experiment_length=True, out_dir=str(tmp_path / "out"))
    ref = run_cov.run(**dict(common, out_dir=str(tmp_path / "ref")))
    volatile = {"time_seconds"}

    def keyed(path):
        rows = [json.loads(ln) for ln in open(path) if ln.strip()]
        return {(r["pres_id"], r["z_word"], r["iso_gen"], r["iso_index"]):
                {k: v for k, v in r.items() if k not in volatile} for r in rows}

    chunked = dict(common, use_chunks=True, chunks=2, chunk_procs=1)
    # merging before both chunks exist must refuse
    run_cov.run(**chunked, chunk_index=1)
    with pytest.raises(RuntimeError, match="expected exactly one"):
        run_cov.merge_chunks(**chunked)
    run_cov.run(**chunked, chunk_index=2)
    merged = run_cov.merge_chunks(**chunked)
    assert len(merged) == 1
    assert "_c" not in os.path.basename(merged[0]).replace("_cyc", "")
    assert keyed(merged[0]) == keyed(ref[0])
    # a second merge must refuse to overwrite the target
    with pytest.raises(RuntimeError, match="already exists"):
        run_cov.merge_chunks(**chunked)
    # and the merged file IS the unchunked resume target: rerunning the
    # unchunked sweep finds every row done and re-searches nothing
    out2 = run_cov.run(**common)
    assert out2[0] == merged[0]
    assert keyed(out2[0]) == keyed(ref[0])


def test_merge_refuses_an_incomplete_chunk(tmp_path, monkeypatch):
    _spy_searches(monkeypatch, solved=False)
    common = _sweep_common(tmp_path)
    chunked = dict(common, use_chunks=True, chunks=2, chunk_procs=1)
    run_cov.run(**chunked, chunk_index=1)
    run_cov.run(**chunked, chunk_index=2)
    # single-presentation fixture: chunk 2 is legitimately empty of rows only
    # if it has no presentations — so instead truncate chunk 1 to fake a crash
    files = sorted(glob.glob(str(tmp_path / "out" / "*_c1of2_*.jsonl")))
    assert len(files) == 1
    lines = open(files[0]).read().splitlines()
    with open(files[0], "w") as f:
        f.write("\n".join(lines[:-1]) + "\n")
    with pytest.raises(RuntimeError, match="INCOMPLETE"):
        run_cov.merge_chunks(**chunked)


# --- SWEEP HEARTBEAT (nodes/s + ETA, printed between rows) ---------------------

def test_sweep_heartbeat_phases_and_stats():
    hb = run_cov._SweepHeartbeat(total_rows=100, done_rows=10, period=60.0,
                                 now=1000.0)
    assert hb.maybe_beat(1059.9) is None      # first emission waits a FULL period
    hb.note_row({"solved": True, "nodes_explored": 500})
    hb.note_row({"solved": False, "nodes_explored": 10000})
    line = hb.maybe_beat(1060.0)
    assert line is not None
    assert "12/100 rows" in line and "1 solved" in line
    assert "10,500 nodes" in line and "175 nodes/s" in line     # 10500 / 60s
    # 2 rows in 60s -> 30 s/row x 88 remaining = 44 min
    assert "~44m left" in line
    assert hb.maybe_beat(1061.0) is None      # cadence phase: no spam after a beat
    assert hb.maybe_beat(1121.0) is not None


def test_sweep_heartbeat_no_rows_yet():
    hb = run_cov._SweepHeartbeat(total_rows=10, done_rows=0, period=60.0, now=0.0)
    line = hb.maybe_beat(60.0)
    assert line is not None and "eta n/a" in line


def test_sweep_emits_heartbeat_lines(tmp_path, monkeypatch, capsys):
    _spy_searches(monkeypatch, solved=False)
    monkeypatch.setattr(run_cov, "_HB_PERIOD", 0.0)   # every row beats
    run_cov.run(**_sweep_common(tmp_path))
    out = capsys.readouterr().out
    assert "[hb]" in out and "nodes/s" in out and "rows total" in out


# --- RECHUNK (finer partition migration) + list-mode chunk_index ---------------

def test_chunk_index_list_validation():
    ok = run_cov.load_config(use_chunks=True, chunks=8, chunk_index=[1, 5])
    assert ok["chunk_index"] == [1, 5]
    for bad in ([], [0], [9], [1, 1], [1, "2"]):
        with pytest.raises(ValueError):
            run_cov.load_config(use_chunks=True, chunks=8, chunk_index=bad)


def test_rechunk_rebins_without_rerunning(tmp_path, monkeypatch):
    calls = _spy_searches(monkeypatch, solved=False)
    csv_p = tmp_path / "reach_tier_9.csv"
    csv_p.write_text("name,r1,r2\nAK(3),xyxYXY,xxxYYYY\nW4,xyyxY,yxxxY\n")
    common = dict(datasets=[str(csv_p)], budgets=[100], mode="cov",
                  experiment_length=True, out_dir=str(tmp_path / "out"),
                  chunk_procs=1)
    # the "old" 2-way partition, both chunks complete (serial: spies must apply)
    run_cov.run(**common, use_chunks=True, chunks=2, chunk_index=1)
    run_cov.run(**common, use_chunks=True, chunks=2, chunk_index=2)
    n_searched = len(calls)

    # migrate 2 -> 4: pres0 -> c1of4, pres1 -> c2of4; c3/c4 own no presentations
    run_cov.rechunk(**common, use_chunks=True, chunks=4, old_chunks=2)
    files = sorted(os.path.basename(p)
                   for p in glob.glob(str(tmp_path / "out" / "*_c?of4_*.jsonl")))
    assert [f.split("_")[7] for f in files] == ["c1of4", "c2of4"]

    # resuming the new partition re-searches NOTHING
    run_cov.run(**common, use_chunks=True, chunks=4, chunk_index=1)
    run_cov.run(**common, use_chunks=True, chunks=4, chunk_index=2)
    assert len(calls) == n_searched
    # rechunk again: idempotent, everything already present
    run_cov.rechunk(**common, use_chunks=True, chunks=4, old_chunks=2)
    run_cov.run(**common, use_chunks=True, chunks=4, chunk_index=1)
    assert len(calls) == n_searched

    # merge of the NEW partition succeeds (empty chunks owe no file) and
    # matches the old partition's rows exactly
    merged = run_cov.merge_chunks(**common, use_chunks=True, chunks=4)
    rows = [json.loads(ln) for ln in open(merged[0]) if ln.strip()]
    keys = {(r["pres_id"], r["z_word"], r["iso_gen"], r["iso_index"])
            for r in rows}
    old_rows = []
    for p in glob.glob(str(tmp_path / "out" / "*_c?of2_*.jsonl")):
        old_rows += [json.loads(ln) for ln in open(p) if ln.strip()]
    assert keys == {(r["pres_id"], r["z_word"], r["iso_gen"], r["iso_index"])
                    for r in old_rows}
    assert len(rows) == len(old_rows) == n_searched


# --- CHUNK WORKERS (one chunk fanned over chunk_procs processes) ---------------

def test_chunk_procs_validation_auto_and_fine_indices(monkeypatch):
    assert run_cov._fine_indices(2, 4, 8) == [2, 6, 10, 14, 18, 22, 26, 30]
    assert run_cov._fine_indices(1, 2, 2) == [1, 3]
    monkeypatch.setattr(run_cov.os, "cpu_count", lambda: 8)
    assert run_cov._resolved_chunk_procs({"chunk_procs": 0}) == 8
    assert run_cov._resolved_chunk_procs({"chunk_procs": 3}) == 3
    assert run_cov.load_config(use_chunks=True, chunks=4,
                               chunk_index=1)["chunk_procs"] == 0
    for bad in (True, -1, 2.5):
        with pytest.raises(ValueError):
            run_cov.load_config(use_chunks=True, chunks=4, chunk_procs=bad)


def test_chunk_workers_dispatch_wiring(tmp_path, monkeypatch):
    """chunk_index=int + chunk_procs>1 must re-bin ONLY its own coarse chunk,
    fan out over the NESTED fine indices with chunks scaled to N*P, and
    return the fold-back's coarse paths (real spawn covered end-to-end
    below)."""
    seen = {}
    monkeypatch.setattr(run_cov, "_rechunk_impl",
                        lambda c, old_chunks, old_index=None:
                        seen.update(rebin=(c["chunks"], old_chunks,
                                           old_index)))
    monkeypatch.setattr(run_cov, "_run_chunks_parallel",
                        lambda c, indices, label="":
                        seen.update(chunks=c["chunks"], indices=indices,
                                    label=label))
    monkeypatch.setattr(run_cov, "_backfill_coarse",
                        lambda c, fine, indices: ["coarse.jsonl"])
    out = run_cov.run(**_sweep_common(tmp_path), use_chunks=True, chunks=4,
                      chunk_index=2, chunk_procs=8)
    assert out == ["coarse.jsonl"]
    assert seen["rebin"] == (32, 4, 2)
    assert seen["chunks"] == 32
    assert seen["indices"] == [2, 6, 10, 14, 18, 22, 26, 30]
    assert seen["label"] == "c2of4"


def test_chunk_files_heartbeat_scans_and_tolerates_torn_tail(tmp_path):
    f = tmp_path / "c1.jsonl"
    f.write_text('{"solved": true, "nodes_explored": 100}\n'
                 '{"solved": false, "nodes_explored": 900}\n'
                 '{"solved": fal')                       # in-flight tail
    hb = run_cov._ChunkFilesHeartbeat([str(tmp_path / "*.jsonl")],
                                      total_rows=10, period=60.0, now=0.0)
    assert (hb.done0, hb.solved0, hb.nodes0) == (2, 1, 1000)
    # the scanner reads a file another process owns: skip, NEVER repair
    assert f.read_text().endswith('{"solved": fal')
    assert hb.maybe_beat(59.0) is None                # full first period
    f.write_text('{"solved": true, "nodes_explored": 100}\n'
                 '{"solved": false, "nodes_explored": 900}\n'
                 '{"solved": true, "nodes_explored": 500}\n'
                 '{"solved": false, "nodes_explored": 1500}\n')
    line = hb.maybe_beat(60.0)
    assert "4/10 rows" in line and "1 solved this session" in line
    assert "2,000 nodes" in line
    # 2 rows in 60 s -> 30 s/row x 6 remaining = 3 min
    assert "~3m left" in line
    assert hb.maybe_beat(61.0) is None                # cadence: no spam


def test_notebook_mirror_patch_is_monotonic(tmp_path, monkeypatch):
    """run()'s .py-side retrofit of the notebook's Drive mirror: rebinds a
    __main__._sync_to_drive to bigger-wins — pushes a grown local file, never
    clobbers a bigger Drive copy with a stale seeded one (the multi-session
    flip-flop) — and patches exactly once."""
    import __main__
    local, drive = tmp_path / "local", tmp_path / "drive"
    local.mkdir(), drive.mkdir()
    monkeypatch.setattr(__main__, "_sync_to_drive", lambda: None,
                        raising=False)
    monkeypatch.setattr(__main__, "LOCAL_OUT", str(local), raising=False)
    monkeypatch.setattr(__main__, "DRIVE_DIR", str(drive), raising=False)
    assert run_cov._patch_notebook_mirror() is True
    assert run_cov._patch_notebook_mirror() is False      # idempotent
    (local / "a_c1of4_x.jsonl").write_text('{"r": 1}\n{"r": 2}\n')   # fresh own
    (drive / "a_c1of4_x.jsonl").write_text('{"r": 1}\n')
    (local / "b_c2of4_x.jsonl").write_text('{"r": 1}\n')             # stale seed
    (drive / "b_c2of4_x.jsonl").write_text('{"r": 1}\n{"r": 2}\n')   # owner fresh
    __main__._sync_to_drive()
    assert (drive / "a_c1of4_x.jsonl").read_text().count("\n") == 2  # pushed
    assert (drive / "b_c2of4_x.jsonl").read_text().count("\n") == 2  # kept


def test_chunk_workers_end_to_end(tmp_path):
    """REAL spawn path (no spies — monkeypatches don't survive spawn). Coarse
    chunk 1 of 2 holds presentations j=0 and j=2; chunk_procs=2 splits them
    over fine chunks c1of4 and c3of4, one worker each. The fold-back coarse
    file must hold exactly the serial chunk run's rows, a rerun must append
    nothing, and a pre-seeded COMPLETE coarse file (the user's restart after
    a serial session) must migrate without re-searching."""
    csv_p = tmp_path / "reach_tier_9.csv"
    csv_p.write_text("name,r1,r2\nAK(3),xyxYXY,xxxYYYY\nW4,xyyxY,yxxxY\n"
                     "W4b,xyyxY,yxxxY\n")
    base = dict(datasets=[str(csv_p)], budgets=[100], mode="cov",
                experiment_length=True, use_chunks=True, chunks=2,
                chunk_index=1)
    volatile = {"time_seconds", "min_relator", "max_relator",
                "max_relator_expanded"}      # set-tie-broken -> PYTHONHASHSEED

    def keyed(path):
        rows = [json.loads(ln) for ln in open(path) if ln.strip()]
        return {(r["pres_id"], r["z_word"], r["iso_gen"], r["iso_index"]):
                {k: v for k, v in r.items() if k not in volatile}
                for r in rows}

    ref = run_cov.run(**base, out_dir=str(tmp_path / "ref"), chunk_procs=1)
    par = run_cov.run(**base, out_dir=str(tmp_path / "out"), chunk_procs=2)
    assert os.path.basename(par[0]) == os.path.basename(ref[0])
    assert "_c1of2_" in os.path.basename(par[0])
    assert keyed(par[0]) == keyed(ref[0])
    fine = sorted(os.path.basename(p) for p in
                  glob.glob(str(tmp_path / "out" / "*of4_*.jsonl")))
    assert [f.split("_")[7] for f in fine] == ["c1of4", "c3of4"]

    # rerun: fine files are complete, so nothing is searched or appended
    before = open(par[0]).read()
    par2 = run_cov.run(**base, out_dir=str(tmp_path / "out"), chunk_procs=2)
    assert par2[0] == par[0] and open(par[0]).read() == before

    # a serial session's coarse file alone migrates: re-bin fills the fine
    # files, workers re-search nothing, fold-back adds nothing new
    os.makedirs(tmp_path / "mig")
    shutil.copyfile(ref[0], tmp_path / "mig" / os.path.basename(ref[0]))
    mig = run_cov.run(**base, out_dir=str(tmp_path / "mig"), chunk_procs=2)
    assert keyed(mig[0]) == keyed(ref[0])
    assert open(mig[0]).read() == open(ref[0]).read()
