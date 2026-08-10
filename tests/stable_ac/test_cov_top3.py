"""The ms640 CoV-top-3 pipeline: selection, the two rules, early exit, resume.

The load-bearing test is ``test_manifest_reproduces_validated_b1k_selection``,
run for BOTH rules: Stage A builds its candidate families from
``data/ms640_solved.txt`` and ranks them itself, while the validated budget-1,000
result ranked rows read out of a frozen sweep jsonl. Those are two independent
paths to the same 60 selections per rule, and if they ever disagree the ms640 run
is measuring a different rule than the one the deck reports.

The second load-bearing property is the rule↔manifest binding. With two manifests
on disk, searching one rule's picks while calling the run by the other rule's name
is a wrong experiment that nothing in the results could reveal — so the rule is in
the filename, in every manifest row, in every result row, and asserted before the
first search.

Every search here runs at budget <= 1,000 (`MAX_BUDGET`): a search at budget B is
exactly the first B pops of any longer one, so a bigger budget buys a slower
test, never different behaviour.
"""

import csv
import json
import os
import subprocess
import sys

import pytest

from experiments import run_baseline
from experiments.heuristic_search.runners import abel_topk_cov_b1k as B1K
from experiments.stable_ac.cov import cov
from experiments.stable_ac.cov.run import cov_top3_manifest as M
from experiments.stable_ac.cov.run import cov_top3_run as R

MAX_BUDGET = 1_000
SUBSET60 = "benchmark/subsets/benchmark_subset_60.csv"
BASE_100K = "results/greedy_baseline/greedy_100000_640_mrl24_cyc_all_07_10_26.jsonl"

# rule -> the b1k KEYS name it must reproduce
RULE_KEYS = {"abel": "abel", "len": "len_only"}


def _ms640(subset=None):
    return {p: (r1, r2) for p, r1, r2 in run_baseline.load_dataset(
        os.path.join(M.ROOT, M.DATASET), subset=subset)}


def _key3(d):
    return (d["z_word"], d["iso_gen"], d["iso_index"])


@pytest.fixture(scope="module")
def ids60():
    with open(os.path.join(M.ROOT, SUBSET60)) as fh:
        return [int(r["pres_id"]) for r in csv.DictReader(fh)]


@pytest.fixture(scope="module")
def sweep60(ids60):
    """{pres_id: [cov rows]} from the frozen budget-1,000 sweep."""
    keep, out = set(ids60), {}
    with open(os.path.join(B1K.ROOT, B1K.SWEEP)) as fh:
        for line in fh:
            d = json.loads(line)
            if d["pres_id"] in keep and d.get("n_cov", 0) != 0:
                out.setdefault(d["pres_id"], []).append(d)
    return out


# ------------------------------------------------------------------ selection

@pytest.mark.parametrize("rule", sorted(M.RULES))
def test_manifest_reproduces_validated_b1k_selection(rule, ids60, sweep60):
    """Two independent paths, one selection — the tie to the validated result.

    If this fails, the ms640 run is not the experiment the subset-60 deck
    reports, whatever the number it produces. The tie-break is part of the
    claim: at the length minimum especially, many candidates tie, so a
    reproduction that ignored ``_ident`` would be reproducing a set, not a rank.
    """
    ms = _ms640(ids60)
    for p in ids60:
        want = [_key3(d) for d in
                B1K.rank(sweep60[p], B1K.KEYS[RULE_KEYS[rule]], "ident")[:M.K]]
        got = [_key3(d) for d in M.top_k(M.candidates(*ms[p]), rule=rule)]
        assert got == want, f"{rule} pres {p}: {got} != {want}"


def test_the_two_rules_select_different_starts(ids60):
    """The comparison must have something to compare: if both rules picked the
    same three candidates everywhere, the second Colab session would be a
    re-run of the first under another name."""
    ms = _ms640(ids60)
    differ = 0
    for p in ids60:
        cands = M.candidates(*ms[p])
        a = {(d["r1"], d["r2"]) for d in M.top_k(cands, rule="abel")}
        n = {(d["r1"], d["r2"]) for d in M.top_k(cands, rule="len")}
        differ += a != n
    assert differ >= len(ids60) // 2, (
        f"the rules agree on {len(ids60) - differ}/{len(ids60)} subset-60 rows")


def test_manifest_family_matches_the_sweeps_family(ids60, sweep60):
    """Same enumeration, not merely the same top 3 — a family that differed
    only below rank 3 would pass the selection test today and diverge the
    moment a key or K moved."""
    ms = _ms640(ids60)
    for p in ids60:
        got = sorted(_key3(d) for d in M.candidates(*ms[p]))
        want = sorted(_key3(d) for d in sweep60[p])
        assert got == want, f"pres {p}: family differs ({len(got)} vs {len(want)})"


def test_manifest_cap_is_the_cov_cap_not_the_base_cap(ids60, sweep60):
    """A CoV lengthens relators. Searching a lengthened start under the
    untransformed 24-cap would cripple it, so the cap travels with the pick."""
    ms = _ms640(ids60)
    by_key = {(p, _key3(d)): d for p in ids60 for d in sweep60[p]}
    raised = 0
    for p in ids60:
        for d in M.candidates(*ms[p]):
            want = by_key[(p, _key3(d))]["max_relator_length_cap"]
            assert d["cap"] == want, f"pres {p} {_key3(d)}: cap {d['cap']} != {want}"
            assert d["cap"] == max(M.DEFAULT_CAP,
                                   max(len(d["r1"]), len(d["r2"]))
                                   + M.CAP_HEADROOM)
            raised += d["cap"] > M.DEFAULT_CAP
    assert raised, "no candidate needed a raised cap — the guard is vacuous here"


def test_keys_are_imported_not_reimplemented():
    """One key, one implementation. A second copy is a silent fork waiting to
    happen, and the b1k runner is the one the published numbers came from."""
    assert M.abel_magnitude is B1K.abel_magnitude
    assert M._ident is B1K._ident
    for rule, name in RULE_KEYS.items():
        assert M.RULES[rule] is B1K.KEYS[name]


def test_unknown_rule_is_refused_everywhere():
    """The whitelist is the point: an unrecognised rule must fail at config
    time, never fall back to a default and mislabel the run."""
    for call in (lambda: M.check_rule("abelian"),
                 lambda: M.manifest_path("shortest"),
                 lambda: M.rank([], "ABEL"),
                 lambda: R.load_config(budget=MAX_BUDGET, rule="len_only")):
        with pytest.raises(ValueError):
            call()


# ------------------------------------------------------------------- manifest

@pytest.mark.parametrize("rule", sorted(M.RULES))
def test_shipped_manifest_covers_ms640_and_aligns_with_the_baseline(rule):
    """`pres_id` is a line index in three files at once (ms640, the manifest,
    the plain-greedy baseline). A silent off-by-one would mis-key every
    comparison downstream while every count still looked right."""
    groups = M.load_manifest(rule=rule)
    assert len(groups) == 640
    assert [p for p, _ in groups] == list(range(640))
    ms = _ms640()
    base = {}
    with open(os.path.join(M.ROOT, BASE_100K)) as fh:
        for line in fh:
            d = json.loads(line)
            base[d["pres_id"]] = (d["r1"], d["r2"])
    for p, picks in groups:
        assert len(picks) == M.K
        assert [q["rank"] for q in picks] == [1, 2, 3]
        assert all(q["rule"] == rule for q in picks)
        orig = (picks[0]["r1_orig"], picks[0]["r2_orig"])
        assert orig == ms[p], f"pres {p}: manifest start != ms640 line"
        assert orig == base[p], f"pres {p}: manifest start != baseline row"
        assert picks[0]["family_tag"] == cov.SUBWORD_FAMILY_TAG


def test_manifest_path_derives_from_the_rule():
    """Never a path passed alongside a rule name — that is the pair that drifts."""
    a, n = M.manifest_path("abel"), M.manifest_path("len")
    assert a != n and a.endswith("manifest_ms640_abel_top3.jsonl")
    assert n.endswith("manifest_ms640_len_top3.jsonl")
    assert R.load_config(budget=MAX_BUDGET, rule="len")["manifest"] == n


def test_load_manifest_rejects_the_other_rules_manifest():
    """The guard that makes a stale path loud instead of silently wrong."""
    with pytest.raises(ValueError, match="ranked by"):
        M.load_manifest(M.manifest_path("abel"), rule="len")
    assert M.load_manifest(M.manifest_path("abel"), rule="abel")


@pytest.mark.parametrize("rule", sorted(M.RULES))
def test_manifest_build_is_deterministic(rule, tmp_path):
    kw = dict(rule=rule, subset=list(range(12)), verbose=False)
    a = M.build(out_path=str(tmp_path / f"a_{rule}.jsonl"), **kw)
    b = M.build(out_path=str(tmp_path / f"b_{rule}.jsonl"), **kw)
    assert open(a).read() == open(b).read()
    shipped = {(r["pres_id"], r["rank"]): r
               for _, picks in M.load_manifest(rule=rule) for r in picks}
    for line in open(a):
        row = json.loads(line)
        assert row == shipped[(row["pres_id"], row["rank"])], (
            "a fresh build disagrees with the shipped manifest — the frozen "
            "artifact and the code that makes it have drifted apart")


# ------------------------------------------------------------------- sharding

@pytest.mark.parametrize("chunks", [2, 3, 5])
def test_shard_partition_is_disjoint_and_covering(chunks):
    items = [(p, None) for p in range(640)]
    parts = [R.shard(items, chunks, i) for i in range(1, chunks + 1)]
    flat = [p for part in parts for p, _ in part]
    assert sorted(flat) == list(range(640))
    assert len(flat) == len(set(flat))
    assert max(len(p) for p in parts) - min(len(p) for p in parts) <= 1
    # stride, not blocks: ms640 is difficulty-ordered, and a block split hands
    # one shard every hard row and finishes hours after the other
    assert [p for p, _ in parts[0]][:3] == [0, chunks, 2 * chunks]
    assert R.shard(items, chunks, None) == items


def test_run_prefix_is_the_resume_identity():
    base = dict(R.DEFAULTS, chunks=2, chunk_index=1)
    stem = R._run_prefix(base, 640)
    assert stem.startswith("abeltop3_")
    assert "c1of2_" in stem and "100000" in stem
    assert cov.SUBWORD_FAMILY_TAG in stem
    # result-neutral knobs must NOT move the file, or a mode switch orphans a
    # half-finished run
    for neutral in ({"high_speedup": False}, {"resume": False},
                    {"manifest": "elsewhere.jsonl"}):
        assert R._run_prefix(dict(base, **neutral), 640) == stem
    # …and every knob that changes the result must
    for knob in ({"rule": "len"}, {"budget": 50}, {"k": 2},
                 {"cyclic_reduce": False}, {"chunk_index": 2},
                 {"max_relator_length": 30}):
        assert R._run_prefix(dict(base, **knob), 640) != stem
    # the two arms can never resume into each other
    assert R._run_prefix(dict(base, rule="len"), 640).startswith("lentop3_")
    assert R._run_prefix(dict(base, chunk_index=None), 640).endswith("ms640_")


def test_budget_above_the_local_cap_refuses_without_the_env(monkeypatch):
    monkeypatch.delenv(R._ALLOW_BIG_ENV, raising=False)
    with pytest.raises(RuntimeError, match="local cap"):
        R.load_config(budget=100_000)
    monkeypatch.setenv(R._ALLOW_BIG_ENV, "1")
    assert R.load_config(budget=100_000)["budget"] == 100_000
    assert R.load_config(budget=MAX_BUDGET)["budget"] == MAX_BUDGET


@pytest.mark.parametrize("bad", [{"chunks": 0}, {"chunk_index": 0},
                                 {"chunk_index": 3, "chunks": 2},
                                 {"chunk_index": True}])
def test_load_config_rejects_bad_sharding(bad):
    with pytest.raises(ValueError):
        R.load_config(budget=MAX_BUDGET, **bad)


# -------------------------------------------------------- end-to-end (budget 1k)

@pytest.fixture(params=sorted(M.RULES))
def mini(request, tmp_path):
    """A 6-presentation manifest per rule: 4 that solve at rank 1 and the two
    hardest ms640 rows, which no CoV solves at budget 1,000 — so the early-exit
    test sees both branches and the "all 3 ranks ran" branch is not vacuous."""
    rule = request.param
    path = str(tmp_path / f"mini_{rule}.jsonl")
    M.build(rule=rule, out_path=path, subset=[0, 1, 2, 3, 638, 639],
            verbose=False)
    return rule, path


def _run(mini, out_dir, **kw):
    rule, path = mini
    return R.run(rule=rule, budget=MAX_BUDGET, manifest=path,
                 out_dir=str(out_dir), **kw)


def test_run_refuses_a_manifest_built_for_the_other_rule(mini, tmp_path):
    """The wrong-experiment guard, end to end: no search may start against
    picks somebody else ranked."""
    rule, path = mini
    other = "len" if rule == "abel" else "abel"
    with pytest.raises(ValueError, match="ranked by"):
        R.run(rule=other, budget=MAX_BUDGET, manifest=path,
              out_dir=str(tmp_path))


def test_early_exit_and_resume(mini, tmp_path):
    out = _run(mini, tmp_path, chunks=1, chunk_index=None)
    rows = [json.loads(ln) for ln in open(out)]
    by_pres = {}
    for r in rows:
        by_pres.setdefault(r["pres_id"], []).append(r)

    for p, rs in by_pres.items():
        rs.sort(key=lambda r: r["rank"])
        assert [r["rank"] for r in rs] == list(range(1, len(rs) + 1))
        # a solve is always the LAST row for its presentation: ranks after the
        # first solve are the searches the early exit exists to never run
        solved = [i for i, r in enumerate(rs) if r["solved"]]
        assert solved in ([], [len(rs) - 1])
        if not solved:
            assert len(rs) == M.K, f"pres {p} stopped early without solving"
        assert [r["cum_nodes"] for r in rs] == [
            sum(x["nodes_explored"] for x in rs[:i + 1]) for i in range(len(rs))]
        assert all(r["node_budget"] == MAX_BUDGET for r in rs)
        assert all(r["nodes_explored"] <= MAX_BUDGET for r in rs)
        assert all(r["rule"] == mini[0] for r in rs)

    assert any(len(rs) == 1 for rs in by_pres.values()), "no row exited early"
    assert any(len(rs) == M.K for rs in by_pres.values()), "no row ran all K"

    before = open(out).read()
    assert _run(mini, tmp_path, chunks=1, chunk_index=None) == out
    assert open(out).read() == before, "resume re-searched finished work"


def test_rows_carry_the_path_and_the_plain_greedy_reference(mini, tmp_path):
    """"Everything in the jsonl": a solved row must carry its move path, and
    every row the untransformed route's own numbers for the same presentation —
    so the comparison this run exists to make needs no join, and
    ``verify_results`` can replay the certificate."""
    out = _run(mini, tmp_path, chunks=1, chunk_index=None)
    base = R.baseline_rows()
    assert base, "the frozen plain-greedy baseline is missing"
    solved_seen = 0
    for ln in open(out):
        r = json.loads(ln)
        ref = base[r["pres_id"]]
        assert r["base_solved"] == ref["solved"]
        assert r["base_nodes_explored"] == ref["nodes_explored"]
        assert r["base_path_length"] == ref["path_length"]
        assert r["r1_orig"], "the untransformed start must travel with the row"
        if r["solved"]:
            solved_seen += 1
            moves = r.get("path_moves")
            assert moves, "a solved row carries no move path"
            assert len(moves) == r["path_length"]
            # Definition 2.1 tuples — replayable by ``verify_results``, which
            # is what makes the row a certificate rather than a claim
            assert all(len(m.split("_")) == 4 for m in moves), moves[:3]
    assert solved_seen, "no solved row — the path assertion was vacuous"


def test_resume_after_a_torn_trailing_line(mini, tmp_path):
    out = _run(mini, tmp_path, chunks=1, chunk_index=None)
    good = open(out).read()
    n_rows = len(good.splitlines())
    with open(out, "a") as fh:                      # a crash mid-append
        fh.write('{"pres_id": 3, "rank": 2, "solv')
    assert _run(mini, tmp_path, chunks=1, chunk_index=None) == out
    after = open(out).read()
    assert len(after.splitlines()) == n_rows
    assert after == good, "the torn line was not repaired before the first append"


def test_merge_refuses_before_every_shard_has_finished(mini, tmp_path):
    """The merged file claims the canonical name that later unchunked runs
    resume from, so an early merge would report unfinished presentations as
    done for the rest of the experiment's life."""
    _run(mini, tmp_path, chunks=2, chunk_index=1)
    kw = dict(rule=mini[0], budget=MAX_BUDGET, manifest=mini[1],
              out_dir=str(tmp_path), chunks=2)
    with pytest.raises(RuntimeError, match="refusing to merge"):
        R.merge_chunks(**kw)
    forced = R.merge_chunks(force=True, **kw)
    assert os.path.exists(forced)


def test_chunks_partition_the_work_and_merge_back(mini, tmp_path):
    a = _run(mini, tmp_path, chunks=2, chunk_index=1)
    b = _run(mini, tmp_path, chunks=2, chunk_index=2)
    assert a != b, "two shards must not share a resume file"
    ids_a = {json.loads(ln)["pres_id"] for ln in open(a)}
    ids_b = {json.loads(ln)["pres_id"] for ln in open(b)}
    assert ids_a & ids_b == set()
    assert ids_a | ids_b == {0, 1, 2, 3, 638, 639}

    merged = R.merge_chunks(rule=mini[0], budget=MAX_BUDGET, manifest=mini[1],
                            out_dir=str(tmp_path), chunks=2)
    assert not R._CHUNK_MARK.search(os.path.basename(merged))
    rows = [json.loads(ln) for ln in open(merged)]
    keys = [(r["pres_id"], r["rank"]) for r in rows]
    assert len(keys) == len(set(keys))
    assert sorted(keys) == sorted(
        [(json.loads(ln)["pres_id"], json.loads(ln)["rank"])
         for p in (a, b) for ln in open(p)])
    # the merged file is a normal resumable run of the same experiment
    assert _run(mini, tmp_path, chunks=2, chunk_index=None) == merged
    assert len(open(merged).read().splitlines()) == len(rows)


def test_the_two_arms_never_share_a_results_file(tmp_path):
    """One rule per session, one file per rule — a shared file would interleave
    two experiments' rows under one identity and neither could be scored."""
    minis = {}
    for rule in sorted(M.RULES):
        p = str(tmp_path / f"m_{rule}.jsonl")
        M.build(rule=rule, out_path=p, subset=[0, 1], verbose=False)
        minis[rule] = R.run(rule=rule, budget=MAX_BUDGET, manifest=p,
                            out_dir=str(tmp_path))
    assert minis["abel"] != minis["len"]
    for rule, path in minis.items():
        assert all(json.loads(ln)["rule"] == rule for ln in open(path))


# ------------------------------------------------------------------ summarize

def test_summary_scores_both_arms_on_the_searched_rows_only(mini, tmp_path):
    out = _run(mini, tmp_path, chunks=2, chunk_index=1)
    s = R.summarize(out, rule=mini[0], budget=MAX_BUDGET, manifest=mini[1],
                    out_dir=str(tmp_path), chunks=2, chunk_index=1)
    assert s["searched"] == {0, 2, 638}
    assert s["missing"] == [1, 3, 639]
    for arm in ("solved", "greedy_matched", "greedy_one"):
        assert s[arm] <= s["searched"], f"{arm} scored outside the searched set"


def test_summary_separates_unfinished_rows_from_failed_ones(mini, tmp_path):
    """A presentation with ranks left to try is an unsolved row in every
    statistic while the arm has not given up on it — mid-run that reads as a
    loss it never took, so the summary must say so out loud."""
    out = _run(mini, tmp_path, chunks=1, chunk_index=None)
    kw = dict(rule=mini[0], budget=MAX_BUDGET, manifest=mini[1],
              out_dir=str(tmp_path))
    assert R.summarize(out, **kw)["partial"] == [], (
        "a completed run reported unfinished presentations")

    rows = [json.loads(ln) for ln in open(out)]
    victim = max(r["pres_id"] for r in rows if not r["solved"])
    keep = [r for r in rows
            if not (r["pres_id"] == victim and r["rank"] == M.K)]
    assert len(keep) == len(rows) - 1
    with open(out, "w") as fh:
        for r in keep:
            fh.write(json.dumps(r) + "\n")
    s = R.summarize(out, **kw)
    assert s["partial"] == [victim]
    assert victim in s["searched"] and victim not in s["solved"]


def test_paired_comparison_uses_only_rows_both_arms_solved(mini, tmp_path,
                                                           monkeypatch):
    """A mean over rows one arm never finished is a mean over two different
    questions. Both filters must bite: the unsolved-here rows (638, 639 solve
    from no CoV at budget 1,000) and an unsolved-there row."""
    out = _run(mini, tmp_path, chunks=1, chunk_index=None)
    kw = dict(rule=mini[0], budget=MAX_BUDGET, manifest=mini[1],
              out_dir=str(tmp_path))
    s = R.summarize(out, **kw)
    assert 638 in s["searched"] and 638 not in s["paired"], (
        "a presentation this arm never solved entered the paired statistics")
    assert set(s["paired"]) <= s["solved"]
    assert s["paired"], "the paired set is empty — the comparison is vacuous"

    victim = s["paired"][0]
    faked = dict(R.baseline_rows())
    faked[victim] = dict(faked[victim], solved=False)
    monkeypatch.setattr(R, "baseline_rows", lambda *a, **k: faked)
    s2 = R.summarize(out, **kw)
    assert victim in s2["solved"] and victim not in s2["paired"], (
        "a presentation plain greedy never solved entered the paired statistics")


def test_per_presentation_reports_the_rules_own_cost(mini, tmp_path):
    """``cum_nodes`` is what the rule actually spent — every rank it ran, not
    just the winning one — and the reported path is the winning rank's."""
    out = _run(mini, tmp_path, chunks=1, chunk_index=None)
    rows = [json.loads(ln) for ln in open(out)]
    per = R.per_presentation(out, M.K)
    for p, d in per.items():
        mine = sorted((r for r in rows if r["pres_id"] == p),
                      key=lambda r: r["rank"])
        assert d["cum_nodes"] == sum(r["nodes_explored"] for r in mine)
        assert d["n_searches"] == len(mine)
        if d["solved"]:
            win = next(r for r in mine if r["solved"])
            assert d["rank"] == win["rank"] == mine[-1]["rank"]
            assert d["path_length"] == win["path_length"]
        else:
            assert d["rank"] is None and d["path_length"] is None


def test_compare_rules_scores_on_the_common_set(tmp_path):
    """Two sessions finish at different times; the intersection is the only
    denominator both arms have earned."""
    paths = {}
    for rule, subset in (("abel", [0, 1, 2]), ("len", [0, 1])):
        m = str(tmp_path / f"m_{rule}.jsonl")
        M.build(rule=rule, out_path=m, subset=subset, verbose=False)
        paths[rule] = R.run(rule=rule, budget=MAX_BUDGET, manifest=m,
                            out_dir=str(tmp_path))
    c = R.compare_rules(paths["abel"], paths["len"], k=M.K)
    assert c["common"] == [0, 1], "compare scored a row only one arm searched"
    assert c["abel"] <= set(c["common"]) and c["len"] <= set(c["common"])


# ------------------------------------------------------------------- controls

def test_node_matched_control_is_a_truncation_read():
    """The control costs zero new search. Truncating the frozen 1,000,000-node
    ms640 run at 100,000 must reproduce the independently-run 100,000 file
    exactly — the identity that makes any k x budget control free."""
    want = {}
    with open(os.path.join(M.ROOT, BASE_100K)) as fh:
        for line in fh:
            d = json.loads(line)
            want[d["pres_id"]] = bool(d["solved"])
    got = R.baseline_at(100_000)
    assert got == want
    matched = R.baseline_at(300_000)
    assert sum(want.values()) <= sum(matched.values()), "truncation is monotone"


def test_overlap_gate_agrees_with_the_frozen_sweep(mini, tmp_path):
    """Presentations 0, 638 and 639 are in subset-60, whose whole CoV families
    the frozen 10,000-node sweep already searched — so these searches have a
    known answer for BOTH rules, and reproducing it is the budget-agnostic
    proof."""
    out = _run(mini, tmp_path, chunks=1, chunk_index=None)
    n, bad = R.verify_overlap(out, budget=MAX_BUDGET)
    assert not bad, bad
    assert n >= 3, f"only {n} overlapping searches — the gate is near-vacuous"
    rows = [json.loads(ln) for ln in open(out)]
    assert any(r["pres_id"] == 0 and r["solved"] for r in rows), (
        "no overlapping row SOLVED — the nodes/path identity is untested")


def test_overlap_gate_catches_a_tampered_row(mini, tmp_path):
    """A gate that never fires proves nothing: move one node count and it must
    say so."""
    out = _run(mini, tmp_path, chunks=1, chunk_index=None)
    rows = [json.loads(ln) for ln in open(out)]
    for r in rows:
        if r["pres_id"] == 0 and r["solved"]:
            r["nodes_explored"] += 1
    with open(out, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    _, bad = R.verify_overlap(out, budget=MAX_BUDGET)
    assert bad and "!=" in bad[0]


def test_module_finds_the_repo_root_from_its_real_depth():
    """The root walk-up, executed at this file's real depth with PYTHONPATH
    unset and cwd=/ — the only way to catch a dirname-counting regression,
    since pytest already has the root on sys.path and would stay green."""
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    env["ACSOLVERX_ALLOW_BIG"] = "1"
    code = ("import sys; sys.path.insert(0, %r);"
            "from experiments.stable_ac.cov.run import cov_top3_run as R;"
            "print(R.ROOT)" % M.ROOT)
    out = subprocess.run([sys.executable, "-c", code], cwd="/", env=env,
                         capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert out.stdout.strip() == M.ROOT
