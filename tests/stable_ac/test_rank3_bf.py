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
from experiments.stable_ac.solvern import Pres, search_n, word_to_str
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


def _run(tmp_path, max_len, inv_max_len, pres):
    import argparse
    rows = [r for r in MS640 if r[0] in pres]
    a = argparse.Namespace(source="ms640", budget=300, cap=R.CAP,
                           path_sample_target=10 ** 9, log_every=1e9)
    out = str(tmp_path)
    log = []
    ctrl = R.run_control(_SerialPool(), rows, a, out, log.append)
    R.run_sub(_SerialPool(), rows, a, out, log.append)
    meta = {"node_budget": a.budget, "max_relator_length_cap": a.cap}
    for n in range(1, max_len + 1):
        R.run_bf(_SerialPool(), rows, ctrl, n, "fwd", a, out, meta, log.append)
        if n <= inv_max_len:
            R.run_bf(_SerialPool(), rows, ctrl, n, "inv", a, out, meta, log.append)
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
        assert nodes.shape == (2, W.n_words(n))
        for i, (_, r1, r2) in enumerate(rows):
            for k, w in enumerate(W.words_of_length(n)):
                ref = search_n(R.rank3(r1, r2, w), 300, cap=R.CAP)
                assert int(nodes[i, k]) == ref["nodes_explored"]
                assert int(plen[i, k]) == (ref["path_length"] if ref["solved"]
                                           else -1)
                assert int(mint[i, k]) == ref["min_relator_length"]
    with np.load(f"{stem}_L2_inv.npz") as z:
        assert list(z["words"]) == [word_to_str(W.inverse(w))
                                    for w in W.words_of_length(2)]
    assert not os.path.exists(os.path.join(out, "shards", "L3"))
    # every solved row of the sample and of the subword arm is a certificate
    # the independent verifier accepts
    n_rows, n_solved, failures = verify_results.verify_file(f"{stem}_L3_sample.jsonl")
    assert n_rows == n_solved > 0 and not failures
    n_rows, n_solved, failures = verify_results.verify_file(f"{stem}_relsub.jsonl")
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
    shard_dir = os.path.join(out, "shards", "L2")
    os.makedirs(shard_dir)
    np.savez(os.path.join(shard_dir, "p0000_b000.npz"),
             nodes=np.full(W.n_words(2), 7, dtype=np.uint16),
             path_len=np.full(W.n_words(2), -1, dtype=np.int16),
             min_total=np.full(W.n_words(2), 9, dtype=np.uint8),
             seconds=np.float32(0), paths=np.array("[]"))
    _run(tmp_path, 2, 0, {0})
    with np.load(f"{stem}_L2.npz") as z:
        assert (z["nodes"] == 7).all() and not (first == 7).all()


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
