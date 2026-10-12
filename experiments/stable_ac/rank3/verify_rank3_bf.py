"""Verifier for the rank-3 brute-force sweep (``run_rank3_bf``).

Checks, on a results directory:

1. control: the 2-generator greedy, the rank-n port at n = 2 and the null
   stabilization ``<x,y,z | r1,r2,Z>`` agree on (solved, nodes, path length)
   for every presentation; with ``--cov-control`` also against the control rows
   of a ``cov_all`` file at a budget >= this one (budget prefix property).
2. every merged npz: the word list is exactly ``words.words_of_length(n)`` (or
   its inverses for the ``inv`` side), every (presentation, word) has a row,
   and solved rows used at most ``budget`` nodes.
3. certificates: every sampled path and every solved relator-subword row is
   replayed by ``verify_results`` through the pure-Python spec (legal moves,
   cancelling seams, cap respected, trivial endpoint), and its nodes / path
   length equal the stored arrays.
4. ``--recheck N``: N stored entries per file re-run with the reference
   ``solvern.search_n`` (not the fast twin the sweep used) and compared on
   every stored field, the cap counters included.
5. cap counters, where a run stored them (``run_rank3_bf.CAP_DOC``): the
   ``_capcount.npz`` of a length indexes the same searches as its npz, the
   counters are consistent with each other and with the node counts, the
   sampled rows repeat them, and the null stabilization drops exactly the
   children the 2-generator control drops.

CLI (repo root, ``PYTHONPATH=.``):
    python3 -m experiments.stable_ac.rank3.verify_rank3_bf --dir results/stable_ac/rank3_bf
"""

import argparse
import glob
import gzip
import json
import os
import random
import re
import shutil
import sys
import tempfile

import numpy as np

from experiments.stable_ac import verify_results
from experiments.stable_ac.rank3 import words as W
from experiments.stable_ac.rank3.run_rank3_bf import (
    CAP_FIELDS, find_repo_root, load_ms640, rank3)
from experiments.stable_ac.solvern import search_n, str_to_word, word_to_str


def _rows(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as f:
        return [json.loads(ln) for ln in f if ln.strip()]


def plain_copy(path, tmp):
    """``verify_results`` reads a plain .jsonl with its _paths.jsonl sibling;
    unpack a committed ``.jsonl.gz`` pair into ``tmp`` and return the copy."""
    out = os.path.join(tmp, os.path.basename(path)[:-len(".gz")])
    for src, dst in ((path, out),
                     (path[:-len(".jsonl.gz")] + "_paths.jsonl.gz",
                      out[:-len(".jsonl")] + "_paths.jsonl")):
        if os.path.exists(src):
            with gzip.open(src, "rb") as f, open(dst, "wb") as g:
                shutil.copyfileobj(f, g)
    return out


def capcount_path(path):
    return path[:-len(".npz")] + "_capcount.npz"


def _cap_tuple(res):
    return tuple(-1 if res[k] is None else int(res[k]) for k in CAP_FIELDS)


def cap_violations(dropped, dmin, bind, nodes, solved, budget, cap):
    """Boolean array: searches whose cap counters (-1 = none) cannot be right."""
    return (((dmin < 0) != (dropped == 0))       # a smallest total iff a drop
            | ((dropped > 0) & (dmin <= cap))    # a dropped child holds a relator > cap
            | ((bind >= 0) & ((dropped == 0) | (bind < 2) | (bind > nodes + 1)))
            # "the pop that never came" only when the frontier ran out
            | ((bind == nodes + 1) & (solved | (nodes >= budget)))
            | (~solved & (nodes < budget) & (dropped > 0) & (bind < 0)))


def check_cap_rows(label, rows, prefix, fail):
    """The cap counters stored as json fields ``<prefix>cap_*``, if any."""
    if not rows or prefix + "cap_dropped" not in rows[0]:
        return
    dropped, dmin, bind = (
        np.array([-1 if r[prefix + k] is None else r[prefix + k] for r in rows],
                 dtype=np.int64) for k in CAP_FIELDS)
    nodes = np.array([r[prefix + "nodes" if prefix else "nodes_explored"]
                      for r in rows], dtype=np.int64)
    solved = np.array([bool(r[prefix + "solved"]) for r in rows])
    bad = cap_violations(dropped, dmin, bind, nodes, solved,
                         rows[0]["node_budget"], rows[0]["max_relator_length_cap"])
    if bad.any():
        fail(f"{label}: {int(bad.sum())} rows with inconsistent cap counters")
    print(f"  {label}: the cap dropped a child in {int((dropped > 0).sum())} of "
          f"{len(rows)} searches, could bind in {int((bind >= 0).sum())}")


def check_control(path, cov_control, dataset, fail):
    rows = _rows(path)
    ms = {p: (word_to_str(r1), word_to_str(r2)) for p, r1, r2 in load_ms640(dataset)}
    if len({r["pres_id"] for r in rows}) != len(rows):
        fail(f"{path}: duplicate presentations")
    for r in rows:
        if ms.get(r["pres_id"]) != (r["r1"], r["r2"]):
            fail(f"control pres {r['pres_id']}: relators are not the dataset row")
        if not 0 < r["nodes_explored"] <= r["node_budget"]:
            fail(f"control pres {r['pres_id']}: nodes outside (0, budget]")
        a = (r["solved"], r["nodes_explored"], r["path_length"])
        if not (a == (r["n2_solved"], r["n2_nodes"], r["n2_path_length"])
                == (r["null_solved"], r["null_nodes"], r["null_path_length"])):
            fail(f"control pres {r['pres_id']}: 2-gen/port/null disagree")
    print(f"{path}: {len(rows)} presentations, "
          f"{sum(r['solved'] for r in rows)} solved; 3-way agreement checked")
    if rows and "n2_cap_dropped" in rows[0]:
        for r in rows:
            # Z shares no letter with r1, r2: the same children are dropped,
            # each one letter longer in total
            two = _cap_tuple({k: r["n2_" + k] for k in CAP_FIELDS})
            nul = _cap_tuple({k: r["null_" + k] for k in CAP_FIELDS})
            if nul != (two[0], two[1] + (two[1] >= 0), two[2]):
                fail(f"control pres {r['pres_id']}: cap counters of the null "
                     f"stabilization {nul} do not follow the control's {two}")
        check_cap_rows("rank-n code on 2 generators", rows, "n2_", fail)
        check_cap_rows("third relator Z", rows, "null_", fail)
    if cov_control:
        mine = {r["pres_id"]: r for r in rows}
        n = 0
        for c in _rows(cov_control):
            if not c.get("is_control") or c["pres_id"] not in mine:
                continue
            m, b = mine[c["pres_id"]], mine[c["pres_id"]]["node_budget"]
            if c["node_budget"] < b:
                fail(f"{cov_control} budget {c['node_budget']} < {b}")
                return rows
            if c["max_relator_length_cap"] != m["max_relator_length_cap"] \
                    or (c["r1"], c["r2"]) != (m["r1"], m["r2"]):
                fail(f"pres {c['pres_id']}: control job differs from {cov_control}")
            c_in = c["solved"] and c["nodes_explored"] <= b
            if c_in != m["solved"] or (c_in and (
                    c["nodes_explored"], c["path_length"])
                    != (m["nodes_explored"], m["path_length"])):
                fail(f"pres {c['pres_id']}: control differs from {cov_control}")
            n += 1
        print(f"  matches the cov_all control on {n} presentations")
    return rows


def check_npz(path, fail):
    with np.load(path) as z:
        meta = json.loads(str(z["meta"]))
        nodes, plen, words = z["nodes"], z["path_len"], z["words"]
        pres_ids = z["pres_ids"]
    n, side = meta["z_len"], meta["side"]
    m = re.fullmatch(r"rank3_bf_(.+)_b(\d+)_cap(\d+)_L(\d+)(_inv)?\.npz",
                     os.path.basename(path))
    named = m and (m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4)),
                   "inv" if m.group(5) else "fwd")
    if named != (meta["source"], meta["node_budget"],
                 meta["max_relator_length_cap"], n, side):
        fail(f"{path}: file name does not match its meta {named}")
    if len(set(pres_ids.tolist())) != len(pres_ids):
        fail(f"{path}: duplicate presentations")
    if ((plen >= 0) & (plen > nodes.astype(np.int64))).any():
        fail(f"{path}: a path longer than the nodes popped")
    want = [word_to_str(W.inverse(w) if side == "inv" else w)
            for w in W.words_of_length(n)]
    if list(words) != want:
        fail(f"{path}: word list is not words_of_length({n}) [{side}]")
    if nodes.shape != (len(pres_ids), W.n_words(n)) or plen.shape != nodes.shape:
        fail(f"{path}: shape {nodes.shape}")
    if (nodes == 0).any():
        fail(f"{path}: {int((nodes == 0).sum())} missing rows")
    if (nodes > meta["node_budget"]).any():
        fail(f"{path}: nodes above the budget")
    print(f"{path}: {nodes.size} searches, {int((plen >= 0).sum())} solved")
    return meta, nodes, plen, pres_ids


def check_sample(base, meta, nodes, plen, pres_ids, fail):
    spath = base + "_sample.jsonl"
    if not os.path.exists(spath):
        fail(f"{spath}: missing")
        return 0
    rows = _rows(spath)
    if rows:
        _, n_solved, failures = verify_results.verify_file(spath)
        for f in failures:
            fail(f"{f[0]} {f[1]}: {f[2]}")
    at = {int(p): i for i, p in enumerate(pres_ids)}
    for r in rows:
        i, k = at[r["pres_id"]], r["word_index"]
        if (int(nodes[i, k]), int(plen[i, k])) != (r["nodes_explored"],
                                                   r["path_length"]):
            fail(f"{spath}: pres {r['pres_id']} word {r['z_word']} "
                 f"disagrees with the npz")
    print(f"  {len(rows)} sampled certificates replayed through the spec")
    return len(rows)


def check_capcount(path, meta, nodes, plen, pres_ids, fail):
    """The cap counters of one length: same searches as the npz, consistent."""
    cpath = capcount_path(path)
    if not os.path.exists(cpath):
        return
    with np.load(path) as z, np.load(cpath) as c:
        same = all(z[k].shape == c[k].shape and bool((z[k] == c[k]).all())
                   for k in ("pres_ids", "words"))
        dropped, dmin, bind = (c[k].astype(np.int64) for k in CAP_FIELDS)
        cmeta = json.loads(str(c["meta"]))
    if (not same or dropped.shape != nodes.shape or dmin.shape != nodes.shape
            or bind.shape != nodes.shape
            or any(cmeta.get(k) != meta.get(k) for k in (
                "source", "node_budget", "max_relator_length_cap", "z_len",
                "side", "commit"))):
        fail(f"{cpath}: not the counters of {path}")
        return
    bad = cap_violations(dropped, dmin, bind, nodes.astype(np.int64), plen >= 0,
                         meta["node_budget"], meta["max_relator_length_cap"])
    if bad.any():
        fail(f"{cpath}: {int(bad.sum())} searches with inconsistent cap counters")
    spath = path[:-len(".npz")] + "_sample.jsonl"
    at = {int(p): i for i, p in enumerate(pres_ids)}
    for r in _rows(spath) if os.path.exists(spath) else []:
        i, k = at[r["pres_id"]], r["word_index"]
        if "cap_dropped" not in r or _cap_tuple(r) != (
                int(dropped[i, k]), int(dmin[i, k]), int(bind[i, k])):
            fail(f"{spath}: pres {r['pres_id']} word {r['z_word']}: cap "
                 f"counters disagree with {cpath}")
    print(f"  cap counters: a child dropped in {int((dropped > 0).sum())} of "
          f"{dropped.size} searches, could bind in {int((bind >= 0).sum())}")


def recheck_rows(paths, k, seed, fail):
    """k rows of each relator-subword file against the reference search."""
    rng = random.Random(seed)
    n = 0
    for path in paths:
        rows = _rows(path)
        for r in rng.sample(rows, min(k, len(rows))):
            res = search_n(rank3(str_to_word(r["r1"]), str_to_word(r["r2"]),
                                 str_to_word(r["z_word"])), r["node_budget"],
                           cap=r["max_relator_length_cap"], cyclic=True)
            got = (bool(res["solved"]), res["nodes_explored"],
                   res["path_length"] if res["solved"] else None)
            want = (r["solved"], r["nodes_explored"], r["path_length"])
            if "cap_dropped" in r:
                got += _cap_tuple(res)
                want += _cap_tuple(r)
            if got != want:
                fail(f"{path}: pres {r['pres_id']} word {r['z_word']}: "
                     f"reference search gives {got}, stored {want}")
            n += 1
    print(f"recheck: {n} relator-subword rows re-run with the reference "
          f"solvern.search_n")


def recheck(npz_paths, dataset, k, seed, fail):
    pres = {p: (r1, r2) for p, r1, r2 in load_ms640(dataset)}
    rng = random.Random(seed)
    n = 0
    for path in npz_paths:
        with np.load(path) as z:
            meta = json.loads(str(z["meta"]))
            nodes, plen, mint = z["nodes"], z["path_len"], z["min_total"]
            words, pres_ids = z["words"], z["pres_ids"]
        caps = None
        if os.path.exists(capcount_path(path)):
            with np.load(capcount_path(path)) as c:
                caps = [c[f] for f in CAP_FIELDS]
        for _ in range(k):
            i, j = rng.randrange(nodes.shape[0]), rng.randrange(nodes.shape[1])
            r1, r2 = pres[int(pres_ids[i])]
            res = search_n(rank3(r1, r2, str_to_word(str(words[j]))),
                           meta["node_budget"],
                           cap=meta["max_relator_length_cap"], cyclic=True)
            got = (res["nodes_explored"],
                   res["path_length"] if res["solved"] else -1,
                   min(res["min_relator_length"], 255))
            want = (int(nodes[i, j]), int(plen[i, j]), int(mint[i, j]))
            if caps is not None:
                got += _cap_tuple(res)
                want += tuple(int(a[i, j]) for a in caps)
            if got != want:
                fail(f"{path}: pres {int(pres_ids[i])} word {words[j]}: "
                     f"reference search gives {got}, stored {want}")
            n += 1
    print(f"recheck: {n} entries re-run with the reference solvern.search_n")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="results/stable_ac/rank3_bf")
    ap.add_argument("--dataset", default="data/ms640_solved.txt")
    ap.add_argument("--cov-control", default=None)
    ap.add_argument("--recheck", type=int, default=0,
                    help="entries per npz to re-run with the reference search")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args(argv)
    d = os.path.abspath(a.dir)
    cov_control = os.path.abspath(a.cov_control) if a.cov_control else None
    os.chdir(find_repo_root(os.path.dirname(os.path.abspath(__file__))))

    failures = []

    def fail(msg):
        failures.append(msg)
        print("FAIL:", msg)

    n_cert = 0
    for path in sorted(glob.glob(os.path.join(d, "*_control.jsonl"))):
        check_control(path, cov_control, a.dataset, fail)
        if any("path_moves" in r for r in _rows(path)):
            _, n_solved, fs = verify_results.verify_file(path)
            for f in fs:
                fail(f"{f[0]} {f[1]}: {f[2]}")
            n_cert += n_solved
            print(f"{path}: {n_solved} solved, {len(fs)} failed to replay")
        else:
            print(f"{path}: rows carry no path_moves, nothing replayed")
    npzs = sorted(p for p in glob.glob(os.path.join(d, "*_L*.npz"))
                  if not p.endswith("_capcount.npz"))
    subs = []
    for path in npzs:
        meta, nodes, plen, pres_ids = check_npz(path, fail)
        n_cert += check_sample(path[:-len(".npz")], meta, nodes, plen,
                               pres_ids, fail)
        check_capcount(path, meta, nodes, plen, pres_ids, fail)
    with tempfile.TemporaryDirectory(dir=d) as tmp:
        for path in sorted(glob.glob(os.path.join(d, "*_relsub.jsonl*"))):
            if path.endswith(".gz"):
                if os.path.exists(path[:-len(".gz")]):
                    continue
                plain = plain_copy(path, tmp)
            else:
                plain = path
            n_rows, n_solved, fs = verify_results.verify_file(plain)
            for f in fs:
                fail(f"{f[0]} {f[1]}: {f[2]}")
            n_cert += n_solved
            print(f"{path}: {n_rows} rows, {n_solved} solved, "
                  f"{len(fs)} failed to replay")
            check_cap_rows("relator subwords", _rows(path), "", fail)
            subs.append(path)
    if a.recheck:
        recheck(npzs, a.dataset, a.recheck, a.seed, fail)
        recheck_rows(subs, a.recheck, a.seed, fail)
    if failures:
        print(f"\n{len(failures)} FAILURES")
        return 1
    print(f"\nOK: {len(npzs)} npz files, {n_cert} certificates replayed, 0 failures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
