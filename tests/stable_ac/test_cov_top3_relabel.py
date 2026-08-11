"""The relabel-dedup gate: no two of a presentation's top-3 picks are the same start renamed.

Three properties carry this suite.

**The relabel class is the repo's, not a new one.** ``words.relabel_key`` (the
definition shared with the equivalence-class work) and
``autcanon_fast.relabel_min`` (its numba twin) must partition the shipped picks
identically. A private third notion of "the same up to renaming" is how a dedup
starts discarding candidates that are not duplicates.

**Registration is scoped.** ``cov_top3_manifest.RULES`` is read at module scope
by other code — five tests in ``test_cov_top3.py`` parametrize on
``sorted(M.RULES)`` at collection time, and the base module's no-argument CLI
builds ``sorted(RULES)``. So importing this arm must not add anything to that
dict; only an actual stage-B run may, and only for its duration. The import-purity
test is what keeps the two suites independent of collection order.

**The dedup is the only change.** The ranking is ``cov_top3_manifest.rank``
verbatim, so a deduped manifest's picks must be a subsequence of the base arm's
full ranking, in order, with rank 1 always identical — anything else means the
key changed too, and the arms would differ in two variables instead of one.

Zero searches run here: stage A never calls the solver, so the 1,000-node local
cap is not in play.
"""

import json
import os

import pytest

from experiments.equivalence_classes.lib import words
from experiments.stable_ac.cov.run import cov_top3_manifest as M
from experiments.stable_ac.cov.run import cov_top3_relabel as RD
from experiments.stable_ac.cov.run import cov_top3_relabel_run as RDRUN
from experiments.stable_ac.cov.run import cov_top3_run as R

MAX_BUDGET = 1_000

# what the shipped (undeduped) manifests contain, measured. These files are
# frozen, so a change here is a change to a published number.
SHIPPED_REPEATS = {"abel": (500, 723), "len": (343, 424)}


def _rows(path):
    with open(os.path.join(RD.ROOT, path)) as fh:
        return [json.loads(l) for l in fh if l.strip()]


@pytest.fixture(scope="module")
def shipped_abel():
    return _rows(M.manifest_path("abel"))


# ------------------------------------------------------- the relabel class

def test_relabel_key_and_the_numba_twin_partition_identically(shipped_abel):
    """One definition of "the same start renamed", two implementations.

    ``relabel_min`` is the numba twin the ladder uses; ``relabel_key`` is the
    pure-Python original this module ranks with. If they ever disagree, one arm
    of the repo is deduping on a different equivalence than the other.
    """
    from experiments.stable_ac.cov.ladder import autcanon_fast as AF
    AF.warm()
    slow, fast = {}, {}
    for d in shipped_abel:
        tag = (d["pres_id"], d["r1"], d["r2"])
        slow.setdefault(words.relabel_key((d["r1"], d["r2"])), set()).add(tag)
        fast.setdefault(AF.relabel_min((d["r1"], d["r2"])), set()).add(tag)
    part = lambda g: frozenset(frozenset(v) for v in g.values())
    assert part(slow) == part(fast)


def test_equal_relabel_class_means_an_actual_signed_permutation(shipped_abel):
    """The class is not just a hash: two picks that share it are genuinely one
    presentation under one of the 8 signed permutations."""
    by_cls = {}
    for d in shipped_abel:
        by_cls.setdefault((d["pres_id"], RD.relabel_class(d)), []).append(d)
    checked = 0
    for (_, _), group in by_cls.items():
        if len(group) < 2:
            continue
        a, rest = group[0], group[1:]
        pa = words.canon_pair(a["r1"], a["r2"])
        for b in rest:
            imgs = [words.apply_pair((b["r1"], b["r2"]), img)
                    for _, img in words.SIGNED_PERMS]
            assert pa in imgs, f"pres {a['pres_id']}: same class, no relabel maps them"
            checked += 1
    assert checked > 0, "no duplicate groups to check — fixture is not exercising this"


def test_relabel_class_is_length_preserving(shipped_abel):
    """The 8 signed permutations never change a relator's length, so a dedup on
    them cannot be smuggling a length preference into the ranking.

    Stated on the *cyclically reduced* pair, which is the form both
    ``relabel_key`` and the solver work in (``canon_pair`` cyclically reduces;
    the run's ``cyclic_reduce`` is True). A signed permutation is a
    length-preserving bijection on letters and so commutes with reduction —
    which is exactly why all 8 images share one length profile.
    """
    for d in shipped_abel[:400]:
        base = words.canon_pair(d["r1"], d["r2"])
        lens = {tuple(sorted(map(len, words.apply_pair((d["r1"], d["r2"]), img))))
                for _, img in words.SIGNED_PERMS}
        assert len(lens) == 1, f"relabels changed lengths: {lens}"
        assert lens.pop() == tuple(sorted(map(len, base)))
        assert sorted(map(len, RD.relabel_class(d))) == sorted(map(len, base))


# ------------------------------------------------------ scoped registration

def test_importing_this_module_does_not_touch_the_shared_whitelist():
    """The whole reason ``registered`` is a context manager.

    A permanent entry would make ``test_cov_top3.py``'s five
    ``sorted(M.RULES)`` parametrizations depend on collection order, and would
    let the base module's no-argument CLI overwrite the deduped manifests with
    undeduped ones.
    """
    assert sorted(M.RULES) == ["abel", "len"]
    assert sorted(RD.RULES) == ["abel_rd", "len_rd"]
    assert set(RD.RULES) & set(M.RULES) == set()


def test_registered_scopes_the_rule_and_restores_on_error():
    before = dict(M.RULES)
    with RD.registered("abel_rd"):
        assert "abel_rd" in M.RULES
        assert M.check_rule("abel_rd") == "abel_rd"
        assert R.load_config(budget=MAX_BUDGET, rule="abel_rd")["rule"] == "abel_rd"
    assert M.RULES == before
    with pytest.raises(RuntimeError):
        with RD.registered("len_rd"):
            raise RuntimeError("boom")
    assert M.RULES == before


def test_unknown_deduped_rule_is_refused():
    for call in (lambda: RD.check_rule("abel"),
                 lambda: RD.manifest_path("abel_dedup"),
                 lambda: RD.build("len", verbose=False),
                 lambda: RDRUN.preflight("abel")):
        with pytest.raises(ValueError):
            call()


def test_the_deduped_rules_reuse_the_base_keys_not_copies():
    """The dedup is the only difference between an arm and its base — the
    ranking key must be the same object, not a re-implementation."""
    for new, base in RD.BASE_OF.items():
        assert RD.RULES[new] is M.RULES[base]


# ------------------------------------------------------------ run identity

def test_manifest_paths_and_resume_prefixes_are_distinct_from_the_shipped_arms():
    """A deduped arm that could resume into ``abeltop3_*`` would silently merge
    two experiments into one file."""
    for new, base in RD.BASE_OF.items():
        assert RD.manifest_path(new) != M.manifest_path(base)
        assert RD.manifest_path(new).endswith(f"manifest_ms640_{new}_top3.jsonl")
        with RD.registered(new):
            assert RD.manifest_path(new) == M.manifest_path(new)
            c_new = R.load_config(budget=MAX_BUDGET, rule=new)
        c_base = R.load_config(budget=MAX_BUDGET, rule=base)
        assert R._run_prefix(c_new, 640) != R._run_prefix(c_base, 640)
        assert R._run_prefix(c_new, 640).startswith(f"{new}top3_")


# ------------------------------------------------------------------- dedup

def _cand(r1, r2):
    return {"r1": r1, "r2": r2}


def test_dedup_keeps_the_first_of_each_class_and_pulls_deeper():
    ranked = [_cand("xy", "xxY"),          # 1  kept -> rank 1
              _cand("XY", "XXy"),          # 2  relabel of #1 -> dropped
              _cand("xyx", "yy"),          # 3  kept -> rank 2
              _cand("xy", "xxY"),          # 4  relabel of #1 -> dropped
              _cand("xxyy", "xy")]         # 5  kept -> rank 3
    picks, dropped = RD.dedup_ranked(ranked, k=3)
    assert [p for p, _, _ in picks] == [1, 3, 5]
    assert [d["rank_raw"] for d in dropped] == [2, 4]
    assert [d["collides_with_rank"] for d in dropped] == [1, 1]


def test_dedup_emits_fewer_than_k_when_the_family_is_one_class():
    """A presentation whose whole candidate list is one relabel class is a real
    property of that family — counted, never asserted."""
    ranked = [_cand("xy", "xxY"), _cand("XY", "XXy"), _cand("yx", "yyX")]
    picks, dropped = RD.dedup_ranked(ranked, k=3)
    assert len(picks) == 1 and len(dropped) == 2


def test_dedup_is_a_filter_not_a_reordering():
    """Picks must be a strictly increasing subsequence of the base ranking."""
    for pres_id in (0, 7, 123, 400, 639):
        r1, r2 = None, None
        for p, a, b in __import__("experiments.run_baseline", fromlist=["x"]
                                  ).load_dataset(
                os.path.join(RD.ROOT, M.DATASET), subset=[pres_id]):
            r1, r2 = a, b
        cands = M.candidates(r1, r2)
        ranked = M.rank(cands, "abel")
        picks, _ = RD.top_k(cands, 3, "abel_rd")
        pos = [p for p, _, _ in picks]
        assert pos == sorted(pos) and len(set(pos)) == len(pos)
        assert pos[0] == 1, "rank 1 can never collide, so it must never move"
        for p, _, d in picks:
            assert ranked[p - 1]["r1"] == d["r1"] and ranked[p - 1]["r2"] == d["r2"]


# ---------------------------------------------------------------- manifests

@pytest.mark.parametrize("rule", sorted(SHIPPED_REPEATS))
def test_the_shipped_manifests_carry_the_measured_repeats(rule):
    """The numbers the module docstring and RESULTS.md cite. These files are
    frozen, so a move here is a published number changing."""
    a = RD.audit(M.manifest_path(rule))
    assert (a["presentations_with_a_repeat"], a["repeat_slots"]) == \
        SHIPPED_REPEATS[rule]
    assert a["n_pres"] == 640


@pytest.mark.parametrize("rule", sorted(RD.RULES))
def test_the_deduped_manifests_have_no_repeats_and_full_k(rule):
    a = RD.verify(RD.manifest_path(rule), rule=rule)
    assert a["repeat_slots"] == 0 and a["n_pres"] == 640
    rows = _rows(RD.manifest_path(rule))
    assert len(rows) == 640 * RD.K
    by_pres = {}
    for r in rows:
        by_pres.setdefault(r["pres_id"], []).append(r)
    for p, picks in by_pres.items():
        picks.sort(key=lambda r: r["rank"])
        assert [r["rank"] for r in picks] == [1, 2, 3]
        assert all(r["dedup"] == RD.DEDUP_TAG for r in picks)
        assert all(r["rule"] == rule for r in picks)
        assert [r["rank_raw"] for r in picks] == sorted(r["rank_raw"] for r in picks)
        assert picks[0]["rank_raw"] == 1


@pytest.mark.parametrize("rule", sorted(RD.RULES))
def test_deduped_rows_are_a_superset_of_the_base_schema(rule, tmp_path):
    """Stage B reads the manifest by field name; a missing field is a crash
    mid-run, an extra one is free."""
    base = M.build(rule=RD.base_rule(rule), subset=list(range(6)),
                   out_path=str(tmp_path / "base.jsonl"), verbose=False)
    new = RD.build(rule=rule, subset=list(range(6)),
                   out_path=str(tmp_path / "new.jsonl"), verbose=False)
    bk = set(json.loads(open(base).readline()))
    nk = set(json.loads(open(new).readline()))
    assert bk <= nk
    assert nk - bk == {"dedup", "rank_raw", "relabel_class", "n_dropped"}


@pytest.mark.parametrize("rule", sorted(RD.RULES))
def test_build_is_deterministic_and_matches_the_shipped_file(rule, tmp_path):
    kw = dict(rule=rule, subset=list(range(12)), verbose=False)
    a = RD.build(out_path=str(tmp_path / f"a_{rule}.jsonl"), **kw)
    b = RD.build(out_path=str(tmp_path / f"b_{rule}.jsonl"), **kw)
    assert open(a).read() == open(b).read()
    shipped = {(r["pres_id"], r["rank"]): r for r in _rows(RD.manifest_path(rule))}
    for r in (json.loads(l) for l in open(a) if l.strip()):
        s = shipped[(r["pres_id"], r["rank"])]
        assert (s["r1"], s["r2"], s["cap"], s["rank_raw"]) == \
            (r["r1"], r["r2"], r["cap"], r["rank_raw"])


# ------------------------------------------------------------------- gates

def test_verify_rejects_a_manifest_with_a_relabel_repeat(tmp_path):
    rows = _rows(RD.manifest_path("abel_rd"))[:9]
    # make rank 2 of the first presentation a relabel of its rank 1
    p1 = [r for r in rows if r["pres_id"] == rows[0]["pres_id"]]
    img = dict(words.SIGNED_PERMS[3][1])
    p1[1]["r1"] = words.apply_hom(p1[0]["r1"], img)
    p1[1]["r2"] = words.apply_hom(p1[0]["r2"], img)
    path = tmp_path / "collide.jsonl"
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    with pytest.raises(ValueError, match="relabel class"):
        RD.verify(str(path))


def test_verify_rejects_an_undeduped_build_at_a_deduped_path(tmp_path):
    """Scoped registration narrows this footgun; the tag closes it."""
    path = tmp_path / "manifest_ms640_abel_rd_top3.jsonl"
    with RD.registered("abel_rd"):
        M.build(rule="abel_rd", subset=list(range(30)),
                out_path=str(path), verbose=False)
    with pytest.raises(ValueError, match="dedup"):
        RD.verify(str(path))


def test_verify_rejects_the_other_rules_manifest():
    with pytest.raises(ValueError, match="ranked by"):
        RD.verify(RD.manifest_path("abel_rd"), rule="len_rd")


def test_load_manifest_runs_the_gate(tmp_path):
    groups = RD.load_manifest(rule="abel_rd")
    assert len(groups) == 640 and [p for p, _ in groups] == list(range(640))
    bad = tmp_path / "bad.jsonl"
    bad.write_text("".join(
        json.dumps({**r, "dedup": None}) + "\n"
        for r in _rows(RD.manifest_path("abel_rd"))[:6]))
    with pytest.raises(ValueError):
        RD.load_manifest(str(bad))


def test_preflight_refuses_a_missing_manifest(tmp_path):
    with pytest.raises((FileNotFoundError, ValueError)):
        RDRUN.preflight("abel_rd", out_dir=str(tmp_path))


def test_stage_b_requires_an_explicit_rule():
    with pytest.raises(SystemExit):
        RDRUN.main([])
