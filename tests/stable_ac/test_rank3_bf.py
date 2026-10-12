"""Rank-3 brute-force baseline: word family, control invariants, runner, verifier."""

import json
import os

import numpy as np
import pytest

from experiments import run_baseline
from experiments.stable_ac import verify_results
from experiments.stable_ac.cov import cov_all
from experiments.stable_ac.rank3 import run_rank3_bf as R
from experiments.stable_ac.rank3 import verify_rank3_bf as V
from experiments.stable_ac.rank3 import words as W
from experiments.stable_ac.solvern import Pres, search_n, str_to_word, word_to_str
from experiments.stable_ac.solvern_fast import search_n_fast

MS640 = R.load_ms640("data/ms640_solved.txt")
SAMPLE = MS640[::40]


def _reduced(w):
    return all(a != -b for a, b in zip(w, w[1:]))


def _all_reduced(n):
    out = [()]
    for _ in range(n):
        out = [w + (g,) for w in out for g in W.LETTERS if not w or w[-1] != -g]
    return out


@pytest.mark.parametrize("n", range(1, 8))
def test_words_of_length_is_every_reduced_word_once_up_to_inverse(n):
    ws = W.words_of_length(n)
    assert len(ws) == W.n_words(n) == 2 * 3 ** (n - 1)
    assert len(set(ws)) == len(ws)
    assert all(len(w) == n and _reduced(w) and W.fold(w) == w for w in ws)
    assert set(ws) | {W.inverse(w) for w in ws} == set(_all_reduced(n))
    assert not set(ws) & {W.inverse(w) for w in ws}


def test_cumulative_count_is_3_to_the_L_minus_1():
    assert [sum(W.n_words(n) for n in range(1, L + 1)) for L in (1, 2, 8, 10)] \
        == [2, 8, 3 ** 8 - 1, 3 ** 10 - 1]


@pytest.mark.parametrize("n", (1, 7, 8, 9, 10))
def test_blocks_partition_the_word_list(n):
    cuts = [W.block_slice(n, b) for b in range(W.n_blocks(n))]
    assert cuts[0][0] == 0 and cuts[-1][1] == W.n_words(n)
    assert all(a[1] == b[0] for a, b in zip(cuts, cuts[1:]))
    assert all(0 < hi - lo <= W.BLOCK for lo, hi in cuts)


def test_relator_subwords_extend_the_cov_family_with_the_same_representative():
    for _, r1, r2 in SAMPLE:
        subs = W.relator_subwords(r1, r2)
        ws = [w for w, _ in subs]
        assert len(set(ws)) == len(ws)
        assert all(W.fold(w) == w and _reduced(w) for w in ws)
        assert {w for w, proper in subs if proper} == set(cov_all.subwords(r1, r2))
        # the brute-force family contains every subword it is long enough for
        for w in ws:
            if len(w) <= 7:
                assert w in set(W.words_of_length(len(w)))


def test_null_stabilization_is_the_two_generator_control():
    for pres_id, r1, r2 in SAMPLE:
        row = R.control_task((pres_id, r1, r2, 1000, R.CAP))
        two = (row["solved"], row["nodes_explored"], row["path_length"])
        assert two == (row["n2_solved"], row["n2_nodes"], row["n2_path_length"])
        assert two == (row["null_solved"], row["null_nodes"],
                       row["null_path_length"])
        base = run_baseline.greedy_search(
            row["r1"], row["r2"], 1000, max_relator_length=R.CAP,
            cyclic_reduce=True)
        assert (bool(base["solved"]), int(base["nodes_explored"])) == two[:2]


def test_budget_prefix_property_in_rank_3():
    for _, r1, r2 in SAMPLE[:6]:
        for w in ((1,), (1, 2), (2, -1, 2)):
            big = search_n_fast(R.rank3(r1, r2, w), 1000, cap=R.CAP)
            small = search_n_fast(R.rank3(r1, r2, w), 100, cap=R.CAP)
            in100 = big["solved"] and big["nodes_explored"] <= 100
            assert small["solved"] == in100
            if in100:
                assert small["nodes_explored"] == big["nodes_explored"]
                assert small["path_moves"] == big["path_moves"]


def test_a_rank_3_solve_ends_at_three_single_letters():
    _, r1, r2 = MS640[0]
    res = search_n_fast(R.rank3(r1, r2, (1, 2)), 1000, cap=R.CAP)
    assert res["solved"]
    assert sorted(s.lower() for s in res["path"][-1]) == ["x", "y", "z"]


class _SerialPool:
    def imap_unordered(self, fn, tasks, chunksize=1):
        return map(fn, tasks)


def _run(tmp_path, max_len, inv_max_len, pres, budget=300, cap=R.CAP,
         reverse=False, pool=None):
    import argparse
    rows = [r for r in MS640 if r[0] in pres]
    a = argparse.Namespace(source="ms640", budget=budget, cap=cap,
                           path_sample_target=10 ** 9, log_every=1e9,
                           reverse=reverse)
    out = str(tmp_path)
    log = []
    pool = pool or _SerialPool()
    ctrl = R.run_control(pool, rows, a, out, log.append)
    R.run_sub(pool, rows, a, out, log.append)
    meta = {"source": a.source, "node_budget": a.budget,
            "max_relator_length_cap": a.cap}
    for n in range(1, max_len + 1):
        R.run_bf(pool, rows, ctrl, n, "fwd", a, out, meta, log.append)
        if n <= inv_max_len:
            R.run_bf(pool, rows, ctrl, n, "inv", a, out, meta, log.append)
    return rows, out, log


def test_runner_end_to_end_matches_the_reference_search_and_verifies(tmp_path):
    rows, out, _ = _run(tmp_path, 3, 2, {0, 320})
    stem = os.path.join(out, R.stem("ms640", 300, R.CAP))
    for n in (1, 2, 3):
        with np.load(f"{stem}_L{n}.npz") as z:
            nodes, plen, mint = z["nodes"], z["path_len"], z["min_total"]
            assert list(z["pres_ids"]) == [0, 320]
            assert list(z["words"]) == [word_to_str(w)
                                        for w in W.words_of_length(n)]
        with np.load(f"{stem}_L{n}_capcount.npz") as c:
            caps = [c[f] for f in R.CAP_FIELDS]
            assert list(c["pres_ids"]) == [0, 320]
            assert all(a.shape == nodes.shape for a in caps)
        assert nodes.shape == (2, W.n_words(n))
        for i, (_, r1, r2) in enumerate(rows):
            for k, w in enumerate(W.words_of_length(n)):
                ref = search_n(R.rank3(r1, r2, w), 300, cap=R.CAP)
                assert int(nodes[i, k]) == ref["nodes_explored"]
                assert int(plen[i, k]) == (ref["path_length"] if ref["solved"]
                                           else -1)
                assert int(mint[i, k]) == ref["min_relator_length"]
                assert tuple(int(a[i, k]) for a in caps) == V._cap_tuple(ref)
    with np.load(f"{stem}_L2_inv.npz") as z:
        assert list(z["words"]) == [word_to_str(W.inverse(w))
                                    for w in W.words_of_length(2)]
    assert not os.listdir(os.path.join(out, "shards"))
    # the json rows carry the reference search's cap counters
    with open(f"{stem}_control.jsonl") as f:
        ctrl = {r["pres_id"]: r for r in map(json.loads, f)}
    for p, r1, r2 in rows:
        ref = search_n(Pres(2, (r1, r2)), 300, cap=R.CAP)
        assert R.cap_counters(ref, "n2_").items() <= ctrl[p].items()
        ref = search_n(Pres(3, (r1, r2, (-3,))), 300, cap=R.CAP)
        assert R.cap_counters(ref, "null_").items() <= ctrl[p].items()
    with open(f"{stem}_relsub.jsonl") as f:
        sub = [json.loads(line) for line in f]
    for r in sub[::5]:
        ref = search_n(R.rank3(str_to_word(r["r1"]), str_to_word(r["r2"]),
                               str_to_word(r["z_word"])), 300, cap=R.CAP)
        assert R.cap_counters(ref).items() <= r.items()
    with open(f"{stem}_L3_sample.jsonl") as f:
        assert all(set(R.CAP_FIELDS) <= set(json.loads(line)) for line in f)
    # every solved row of the sample and of the subword arm is a certificate
    # the independent verifier accepts
    n_rows, n_solved, failures = verify_results.verify_file(f"{stem}_L3_sample.jsonl")
    assert n_rows == n_solved > 0 and not failures
    n_rows, n_solved, failures = verify_results.verify_file(f"{stem}_relsub.jsonl")
    assert n_solved > 0 and not failures
    n_rows, n_solved, failures = verify_results.verify_file(f"{stem}_control.jsonl")
    assert n_solved > 0 and not failures
    assert V.main(["--dir", out, "--recheck", "3"]) == 0


def test_runner_resumes_from_shards_and_skips_merged_lengths(tmp_path):
    rows, out, _ = _run(tmp_path, 2, 0, {0})
    stem = os.path.join(out, R.stem("ms640", 300, R.CAP))
    before = {f: os.path.getmtime(os.path.join(out, f)) for f in os.listdir(out)
              if f.endswith(".npz")}
    with np.load(f"{stem}_L2.npz") as z:
        first = z["nodes"].copy()
    _, _, log = _run(tmp_path, 2, 0, {0})
    assert sum("already merged" in m for m in log) == 2
    assert before == {f: os.path.getmtime(os.path.join(out, f))
                      for f in os.listdir(out) if f.endswith(".npz")}
    with open(f"{stem}_relsub.jsonl") as f:
        keys = [(r["pres_id"], r["z_word"]) for r in map(json.loads, f)]
    assert len(keys) == len(set(keys))
    # a half-finished length: a leftover shard is reused, not recomputed
    os.remove(f"{stem}_L2.npz")
    _fake_shard(out, rows[0], 300)
    _run(tmp_path, 2, 0, {0})
    with np.load(f"{stem}_L2.npz") as z:
        assert (z["nodes"] == 7).all() and not (first == 7).all()


def test_reverse_runs_the_same_tasks_in_the_opposite_order(tmp_path):
    """--reverse is for a second machine that works towards the first one from
    the fast end: the same tasks, last one first, and the same merged arrays."""
    order, arrays = {}, {}
    for rev in (False, True):
        seen = []

        class Pool(_SerialPool):
            def imap_unordered(self, fn, tasks, chunksize=1):
                if fn is R.block_task:
                    seen.extend((t[3], t[0], t[4]) for t in tasks)
                return map(fn, tasks)

        os.makedirs(tmp_path / str(rev))
        _, out, _ = _run(tmp_path / str(rev), 2, 0, {0, 320, 639}, reverse=rev,
                         pool=Pool())
        order[rev] = seen
        with np.load(os.path.join(out, R.stem("ms640", 300, R.CAP) + "_L2.npz")) as z:
            arrays[rev] = {k: z[k].copy() for k in
                           ("nodes", "path_len", "min_total", "pres_ids", "words")}
    for n in (1, 2):
        fwd = [t for t in order[False] if t[0] == n]
        assert len(fwd) == 3 and len({p for _, p, _ in fwd}) == 3
        assert [t for t in order[True] if t[0] == n] == fwd[::-1]
    for k in arrays[False]:
        assert (arrays[False][k] == arrays[True][k]).all(), k


def _fake_shard(out, row, budget, ident_budget=None):
    pres_id, r1, r2 = row
    shard_dir = R.shard_dir_for(out, "ms640", budget, R.CAP, 2, "fwd")
    os.makedirs(shard_dir)
    np.savez(os.path.join(shard_dir, f"p{pres_id:04d}_b000.npz"),
             nodes=np.full(W.n_words(2), 7, dtype=np.uint16),
             path_len=np.full(W.n_words(2), -1, dtype=np.int16),
             min_total=np.full(W.n_words(2), 9, dtype=np.uint8),
             cap_dropped=np.zeros(W.n_words(2), dtype=np.uint32),
             cap_dropped_min_total=np.full(W.n_words(2), -1, dtype=np.int16),
             cap_first_bind=np.full(W.n_words(2), -1, dtype=np.int32),
             seconds=np.float32(0), paths=np.array("[]"),
             ident=np.array(R.shard_ident("ms640", ident_budget or budget, R.CAP,
                                          2, "fwd", 0, pres_id, r1, r2)))


def test_a_task_whose_shard_arrived_after_the_list_was_built_is_skipped(tmp_path):
    """Two machines on one length: a shard the other one wrote, copied here
    after this one built its task list, is checked and kept, not searched."""
    row = MS640[0]
    out = str(tmp_path)
    _fake_shard(out, row, 300)
    shard = os.path.join(R.shard_dir_for(out, "ms640", 300, R.CAP, 2, "fwd"),
                         f"p{row[0]:04d}_b000.npz")
    ident = R.shard_ident("ms640", 300, R.CAP, 2, "fwd", 0, *row)
    task = (*row, 2, 0, "fwd", 300, R.CAP, 0.0, shard, ident)
    assert R.block_task(task) == (row[0], 2, 0, 0, 0, 0.0)
    with np.load(shard) as z:
        assert (z["nodes"] == 7).all()
    with pytest.raises(SystemExit):
        R.block_task(task[:-1] + (ident.replace('"z_len":2', '"z_len":3'),))


def test_a_shard_from_another_run_is_refused_not_merged(tmp_path):
    # another budget in the same out-dir uses its own shard directory
    _run(tmp_path, 1, 0, {320}, budget=5)
    _run(tmp_path, 1, 0, {320}, budget=300)
    out = str(tmp_path)
    a, b = (np.load(os.path.join(out, R.stem("ms640", bud, R.CAP) + "_L1.npz"))
            for bud in (5, 300))
    assert a["nodes"].max() <= 5 < b["nodes"].max()
    # a shard whose stored identity is another budget, cap or dataset row
    _fake_shard(out, MS640[0], 300, ident_budget=50)
    with pytest.raises(SystemExit, match="not from this run"):
        _run(tmp_path, 2, 0, {0})
    os.remove(os.path.join(R.shard_dir_for(out, "ms640", 300, R.CAP, 2, "fwd"),
                           "p0000_b000.npz"))
    _fake_shard_dir = R.shard_dir_for(out, "ms640", 300, R.CAP, 2, "fwd")
    os.rmdir(_fake_shard_dir)
    _fake_shard(out, MS640[1], 300)          # row 1's relators under row 0's name
    os.rename(os.path.join(_fake_shard_dir, "p0001_b000.npz"),
              os.path.join(_fake_shard_dir, "p0000_b000.npz"))
    with pytest.raises(SystemExit, match="not from this run"):
        _run(tmp_path, 2, 0, {0})


def test_every_job_starts_from_a_trivial_group_presentation_under_the_cap():
    assert all(R.abs_det(r1, r2) == 1 for _, r1, r2 in MS640)
    assert R.abs_det((1, 1), (2,)) == 2
    longest = max(len(r) for _, r1, r2 in MS640 for r in (r1, r2))
    assert 1 + longest <= R.CAP
    for _, r1, r2 in SAMPLE:
        for w, _ in W.relator_subwords(r1, r2):
            assert _reduced(w) and set(map(abs, w)) <= {1, 2}
            assert 1 + len(w) <= R.CAP


def test_inverse_word_is_the_same_start_up_to_renaming_z():
    # z <-> Z maps Z.w to a rotation of (Z.w^-1)^-1: same canonical start
    from experiments.stable_ac.solvern import canonical_presentation
    _, r1, r2 = MS640[100]
    for w in W.words_of_length(4)[:20]:
        flipped = [tuple(-g if abs(g) == 3 else g for g in r)
                   for r in R.rank3(r1, r2, w).relators]
        assert canonical_presentation(flipped) == canonical_presentation(
            R.rank3(r1, r2, W.inverse(w)).relators)


def test_verifier_rejects_a_renamed_budget(tmp_path):
    _, out, _ = _run(tmp_path, 1, 0, {0}, budget=50)
    for f in os.listdir(out):
        os.rename(os.path.join(out, f), os.path.join(out, f.replace("_b50_", "_b300_")))
    assert V.main(["--dir", out]) == 1


def test_verifier_rejects_a_tampered_array(tmp_path):
    _, out, _ = _run(tmp_path, 2, 0, {0})
    path = os.path.join(out, R.stem("ms640", 300, R.CAP) + "_L2.npz")
    with np.load(path) as z:
        d = {k: z[k] for k in z.files}
    solved = np.argwhere(d["path_len"] >= 0)
    assert len(solved)
    i, k = solved[0]
    d["nodes"] = d["nodes"].copy()
    d["nodes"][i, k] += 1
    np.savez_compressed(path, **d)
    assert V.main(["--dir", out]) == 1


def test_verifier_reads_the_gzipped_subword_arm(tmp_path, capsys):
    import gzip
    import shutil
    _, out, _ = _run(tmp_path, 1, 0, {0, 320})
    base = os.path.join(out, R.stem("ms640", 300, R.CAP) + "_relsub")
    for f in (base + ".jsonl", base + "_paths.jsonl"):
        with open(f, "rb") as src, gzip.open(f + ".gz", "wb") as dst:
            shutil.copyfileobj(src, dst)
        os.remove(f)
    assert V.main(["--dir", out]) == 0
    assert "_relsub.jsonl.gz:" in capsys.readouterr().out
    # a solved row whose certificate is gone must fail, gzipped or not
    os.remove(base + "_paths.jsonl.gz")
    assert V.main(["--dir", out]) == 1



def test_cap_compare_counts_exactly_the_searches_that_differ(tmp_path):
    from experiments.stable_ac.rank3 import cap_compare as C
    dirs = []
    for name in ("base", "other"):
        (tmp_path / name).mkdir()
        dirs.append(_run(tmp_path / name, 2, 0, {0, 320})[1])
    base, other = dirs
    out = str(tmp_path / "cmp.json")
    args = ["--base", base, "--other", other, "--budget", "300", "--out", out]
    diff = ("solved_only_base", "solved_only_other", "nodes_differ",
            "path_length_differs", "both_solved_fewer_nodes_other",
            "both_solved_more_nodes_other", "largest_node_difference")

    assert C.main(args + ["--must-match"]) == 0
    with open(out) as f:
        rows = json.load(f)["comparisons"][0]["rows"]
    assert [r["kind"] for r in rows] == [
        "control, 2 generators", "control, rank-n code on 2 generators",
        "control, third relator Z", "relator subwords", "words of length 1",
        "words of length 2", "all word lengths compared"]
    for r in rows:
        assert r["searches"] > 0 and r["solved_base"] == r["solved_other"]
        assert not any(r[k] for k in diff)

    # change three searches on one side: each is counted once, where it is
    stem = os.path.join(other, R.stem("ms640", 300, R.CAP))
    with np.load(stem + "_L2.npz") as z:
        d = {k: z[k] for k in z.files}
    solved = np.argwhere(d["path_len"] >= 0)
    assert len(solved) >= 2
    d["nodes"], d["path_len"] = d["nodes"].copy(), d["path_len"].copy()
    d["nodes"][tuple(solved[0])] += 1
    d["path_len"][tuple(solved[1])] = -1
    np.savez_compressed(stem + "_L2.npz", **d)
    with open(stem + "_relsub.jsonl") as f:
        sub = [json.loads(line) for line in f]
    i = next(i for i, r in enumerate(sub) if r["solved"])
    sub[i].update(solved=False, path_length=None)
    with open(stem + "_relsub.jsonl", "w") as f:
        f.write("".join(json.dumps(r) + "\n" for r in sub))

    assert C.main(args) == 0 and C.main(args + ["--must-match"]) == 1
    with open(out) as f:
        rows = {r["kind"]: r for r in json.load(f)["comparisons"][0]["rows"]}
    for kind in ("words of length 2", "all word lengths compared"):
        assert [rows[kind][k] for k in diff] == [1, 0, 1, 1, 0, 1, 1]
        assert rows[kind]["solved_base"] == rows[kind]["solved_other"] + 1
    assert [rows["relator subwords"][k] for k in diff] == [1, 0, 0, 1, 0, 0, 0]
    for kind in ("control, 2 generators", "control, third relator Z", "words of length 1"):
        assert not any(rows[kind][k] for k in diff)

    # a search present on one side only is an error, not a silent skip
    with open(stem + "_relsub.jsonl", "w") as f:
        f.write("".join(json.dumps(r) + "\n" for r in sub[1:]))
    with pytest.raises(SystemExit):
        C.main(args)


def _resave(path, **change):
    """Rewrite one npz with ``array[index] = value`` for each ``array=(index, value)``."""
    with np.load(path) as z:
        d = {k: z[k] for k in z.files}
    for name, (index, value) in change.items():
        d[name] = d[name].copy()
        d[name][index] = value
    np.savez_compressed(path, **d)


def test_verifier_rejects_cap_counters_that_cannot_be_right(tmp_path):
    _, out, _ = _run(tmp_path, 2, 0, {0})
    assert V.main(["--dir", out]) == 0
    path = os.path.join(out, R.stem("ms640", 300, R.CAP) + "_L2_capcount.npz")
    # the start is popped before anything is dropped: pop 1 is never a bind
    _resave(path, cap_first_bind=((0, 0), 1))
    assert V.main(["--dir", out]) == 1


def test_a_search_with_no_bind_is_the_same_search_at_a_larger_cap(tmp_path):
    from experiments.stable_ac.rank3 import cap_compare as C
    from experiments.stable_ac.rank3 import cap_exhaustion as E
    pres = {0, 320}
    small = 1 + max(len(r) for p, r1, r2 in MS640 if p in pres for r in (r1, r2))
    dirs = {}
    for cap in (small, 64):
        (tmp_path / f"cap{cap}").mkdir()
        dirs[cap] = _run(tmp_path / f"cap{cap}", 3, 0, pres, cap=cap)[1]
        assert V.main(["--dir", dirs[cap]]) == 0
    out = str(tmp_path / "cmp.json")

    def compare(base, other):
        code = C.main(["--base", dirs[base], "--other", dirs[other],
                       "--budget", "300", "--out", out])
        with open(out) as f:
            return code, json.load(f)["comparisons"][0]["rows"]

    for base, other in ((small, 64), (64, small)):
        code, rows = compare(base, other)
        assert code == 0
        for r in rows:
            assert r["differ_without_bind"] == 0
            assert r["differ"] <= r["bind_at_smaller_cap"] <= r["searches"]

    E.main(["--dir", dirs[small], "--out", str(tmp_path / "exh.json")])
    with open(tmp_path / "exh.json") as f:
        exh = json.load(f)
    assert len(exh["files"]) == 5
    for f in exh["files"]:
        assert (f["cap_could_bind"] == f["cap_could_bind_solved"]
                + f["cap_could_bind_unsolved"] <= f["cap_dropped_a_child"]
                <= f["searches"])
    assert exh["total"]["searches_with_cap_counters"] == exh["total"]["searches"]

    # a search that claims "no bind" and differs breaks the certificate
    _resave(os.path.join(dirs[small], R.stem("ms640", 300, small) + "_L2_capcount.npz"),
            cap_first_bind=((0, 0), -1))
    path = os.path.join(dirs[64], R.stem("ms640", 300, 64) + "_L2.npz")
    with np.load(path) as z:
        n = int(z["nodes"][0, 0])
    _resave(path, nodes=((0, 0), n + 1))
    code, rows = compare(small, 64)
    assert code == 1
    assert {r["kind"]: r["differ_without_bind"] for r in rows}["words of length 2"] == 1


def test_verifier_replays_the_path_of_every_solved_control_row(tmp_path):
    _, out, _ = _run(tmp_path, 1, 0, {0})
    assert V.main(["--dir", out]) == 0
    path = os.path.join(out, R.stem("ms640", 300, R.CAP) + "_control.jsonl")
    with open(path) as f:
        rows = [json.loads(line) for line in f]
    assert rows[0]["solved"] and len(rows[0]["path_moves"]) == rows[0]["path_length"]
    rows[0]["path_moves"] = rows[0]["path_moves"][:-1]
    with open(path, "w") as f:
        f.writelines(json.dumps(r) + "\n" for r in rows)
    assert V.main(["--dir", out]) == 1
