"""The ms640 abel-top-3 pipeline: selection, sharding, early exit, resume.

The load-bearing test is ``test_manifest_reproduces_validated_b1k_selection``:
Stage A builds its candidate families from ``data/ms640_solved.txt`` and ranks
them itself, while the validated budget-1,000 result ranked rows read out of a
frozen sweep jsonl. Those are two independent paths to the same 60 selections,
and if they ever disagree the ms640 run is measuring a different rule than the
one the deck reports.

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
from experiments.stable_ac.cov.run import abel_top3_manifest as M
from experiments.stable_ac.cov.run import abel_top3_run as R

MAX_BUDGET = 1_000
SUBSET60 = "benchmark/subsets/benchmark_subset_60.csv"
BASE_100K = "results/greedy_baseline/greedy_100000_640_mrl24_cyc_all_07_10_26.jsonl"


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

def test_manifest_reproduces_validated_b1k_selection(ids60, sweep60):
    """Two independent paths, one selection — the tie to the validated result.

    If this fails, the ms640 run is not the experiment the subset-60 deck
    reports, whatever the number it produces.
    """
    ms = _ms640(ids60)
    for p in ids60:
        want = [_key3(d) for d in
                B1K.rank(sweep60[p], B1K.KEYS["abel"], "ident")[:M.K]]
        got = [_key3(d) for d in M.top_k(M.candidates(*ms[p]))]
        assert got == want, f"pres {p}: {got} != {want}"


def test_manifest_family_matches_the_sweeps_family(ids60, sweep60):
    """Same enumeration, not merely the same top 3 — a family that differed
    only below rank 3 would pass the selection test today and diverge the
    moment the key or K moved."""
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


def test_abel_key_is_imported_not_reimplemented():
    """One key, one implementation. A second copy is a silent fork waiting to
    happen, and the b1k runner is the one the published numbers came from."""
    assert M.abel_magnitude is B1K.abel_magnitude
    assert M._ident is B1K._ident


# ------------------------------------------------------------------- manifest

def test_shipped_manifest_covers_ms640_and_aligns_with_the_baseline():
    """`pres_id` is a line index in three files at once (ms640, the manifest,
    the plain-greedy baseline). A silent off-by-one would mis-key every
    comparison downstream while every count still looked right."""
    groups = M.load_manifest()
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
        orig = (picks[0]["r1_orig"], picks[0]["r2_orig"])
        assert orig == ms[p], f"pres {p}: manifest start != ms640 line"
        assert orig == base[p], f"pres {p}: manifest start != baseline row"
        assert picks[0]["family_tag"] == cov.SUBWORD_FAMILY_TAG


def test_manifest_build_is_deterministic(tmp_path):
    a = M.build(out_path=str(tmp_path / "a.jsonl"), subset=list(range(12)),
                verbose=False)
    b = M.build(out_path=str(tmp_path / "b.jsonl"), subset=list(range(12)),
                verbose=False)
    assert open(a).read() == open(b).read()
    shipped = {(r["pres_id"], r["rank"]): r
               for _, picks in M.load_manifest() for r in picks}
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
    base = dict(R.DEFAULTS, chunk_index=1)
    stem = R._run_prefix(base, 640)
    assert "c1of2_" in stem and "100000" in stem and "k3" in stem
    assert cov.SUBWORD_FAMILY_TAG in stem
    # result-neutral knobs must NOT move the file, or a mode switch orphans a
    # half-finished run
    for neutral in ({"high_speedup": False}, {"resume": False}):
        assert R._run_prefix(dict(base, **neutral), 640) == stem
    # …and every knob that changes the result must
    for knob in ({"budget": 50}, {"k": 2}, {"cyclic_reduce": False},
                 {"chunk_index": 2}, {"max_relator_length": 30}):
        assert R._run_prefix(dict(base, **knob), 640) != stem
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

@pytest.fixture
def mini(tmp_path):
    """A 6-presentation manifest: 4 that solve at rank 1 and the two hardest
    ms640 rows, which no CoV solves at budget 1,000 — so the early-exit test
    sees both branches and the "all 3 ranks ran" branch is not vacuous."""
    path = str(tmp_path / "mini.jsonl")
    M.build(out_path=path, subset=[0, 1, 2, 3, 638, 639], verbose=False)
    return path


def _run(mini, out_dir, **kw):
    return R.run(budget=MAX_BUDGET, manifest=mini, out_dir=str(out_dir), **kw)


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

    assert any(len(rs) == 1 for rs in by_pres.values()), "no row exited early"
    assert any(len(rs) == M.K for rs in by_pres.values()), "no row ran all K"

    before = open(out).read()
    assert _run(mini, tmp_path, chunks=1, chunk_index=None) == out
    assert open(out).read() == before, "resume re-searched finished work"


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
    kw = dict(budget=MAX_BUDGET, manifest=mini, out_dir=str(tmp_path), chunks=2)
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

    merged = R.merge_chunks(budget=MAX_BUDGET, manifest=mini,
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


def test_summary_scores_both_arms_on_the_searched_rows_only(mini, tmp_path):
    out = _run(mini, tmp_path, chunks=2, chunk_index=1)
    s = R.summarize(out, budget=MAX_BUDGET, manifest=mini,
                    out_dir=str(tmp_path), chunks=2, chunk_index=1)
    assert s["searched"] == {0, 2, 638}
    assert s["missing"] == [1, 3, 639]
    for arm in ("solved", "greedy_matched", "greedy_one"):
        assert s[arm] <= s["searched"], f"{arm} scored outside the searched set"


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
    known answer, and reproducing it is the budget-agnostic proof."""
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
            "from experiments.stable_ac.cov.run import abel_top3_run as R;"
            "print(R.ROOT)" % M.ROOT)
    out = subprocess.run([sys.executable, "-c", code], cwd="/", env=env,
                         capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert out.stdout.strip() == M.ROOT
