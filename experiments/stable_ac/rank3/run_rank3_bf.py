"""Rank-3 brute-force baseline: the greedy on ``<x,y,z | r1, r2, Z.w>`` for every w.

Per presentation of the dataset, three arms, all with the SAME search
(``solvern_fast.search_n_fast``, the n-generator port of the baseline greedy),
the same per-relator cap as the 2-generator control (24) and the same budget:

* ``control``  the 2-generator pair itself, and the null stabilization
  ``<x,y,z | r1, r2, Z>``. No S-move can touch ``Z`` (it shares no letter with
  r1, r2), so the two must agree node for node; the runner refuses to continue
  if they do not.
* ``bf``       every freely reduced w of length n (``words.words_of_length``),
  for n = 1..L. Stored as arrays indexed ``[presentation, word]``.
  ``--side inv`` runs w^-1 for the same index (the tie-break check).
* ``sub``      every cyclic subword of r1/r2 (``words.relator_subwords``), all
  lengths: the word set of the CoV sweep, searched in rank 3.

A task is one (presentation, length, block of ``words.BLOCK`` words). Workers
write one shard per task (tmp file + rename), so a killed run loses at most the
tasks in flight and resumes from the shards on disk; when a length is complete
its shards are merged into one compressed npz and removed.

Paths are kept for a deterministic sample of the solved rows (md5 of the row
key), written in the nocov row format so ``verify_results`` replays them
through the pure-Python spec. Every solved control row carries its own path
(``path_moves``, the moves of the rank-n code on the 2-generator search).

Every search also stores the three cap counters of ``search_n`` (``CAP_DOC``):
as fields of the json rows (control ``n2_*`` / ``null_*``, relator subwords,
path samples) and, for the word arrays, in ``<stem>_L<n>_capcount.npz`` beside
each ``<stem>_L<n>.npz`` (same ``[presentation, word]`` index).

CLI (from the repo root, ``PYTHONPATH=.``):
    python3 -m experiments.stable_ac.rank3.run_rank3_bf --budget 1000 --max-len 8
"""

import argparse
import hashlib
import json
import os
import platform
import subprocess
import time
from multiprocessing import get_context

import numpy as np

from experiments import run_baseline
from experiments.stable_ac.rank3 import words as W
from experiments.stable_ac.solvern import Pres, word_to_str
from experiments.stable_ac.solvern_fast import search_n_fast

OUT_DIR = "results/stable_ac/rank3_bf"
CAP = 24                    # the 2-generator control's per-relator cap
FAMILY_TAG = "allred_foldinv"
SOLVER = "solvern_fast.search_n_fast"
CAP_FIELDS = ("cap_dropped", "cap_dropped_min_total", "cap_first_bind")
CAP_DOC = (
    "cap_dropped: children not pushed because one of their relators is longer "
    "than the cap (one per move). cap_dropped_min_total: smallest total length "
    "among them (none: null in json, -1 in arrays). cap_first_bind: number of "
    "the first pop (1 = the start) at which a child dropped earlier had a heap "
    "key (total length, depth) no larger than the popped state's (never: null "
    "in json, -1 in arrays); never means the search is the same at every "
    "larger cap.")


def cap_counters(res, prefix=""):
    """The cap counters of a search result as json fields (None stays None)."""
    return {prefix + k: None if res[k] is None else int(res[k])
            for k in CAP_FIELDS}


def find_repo_root(start):
    """Walk up until a dir holds both experiments/ and data/ (repo rule)."""
    d = os.path.abspath(start)
    while True:
        if (os.path.isdir(os.path.join(d, "experiments"))
                and os.path.isdir(os.path.join(d, "data"))):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            raise RuntimeError(f"no repo root (experiments/ + data/) above {start}")
        d = parent


def load_ms640(path):
    """``[(pres_id, r1, r2)]`` int tuples; pres_id is the 0-based line index."""
    import ast
    out = []
    with open(path) as f:
        for i, line in enumerate(f):
            if not line.strip():
                continue
            v = ast.literal_eval(line)
            half = len(v) // 2
            out.append((i, tuple(g for g in v[:half] if g),
                        tuple(g for g in v[half:] if g)))
    return out


def sampled(pres_id, wstr, frac):
    if frac <= 0:
        return False
    if frac >= 1:
        return True
    h = hashlib.md5(f"{pres_id}|{wstr}".encode()).digest()
    return int.from_bytes(h[:8], "big") / 2**64 < frac


def rank3(r1, r2, w):
    return Pres(3, (tuple(r1), tuple(r2), (-3,) + tuple(w)))


def stem(source, budget, cap):
    return f"rank3_bf_{source}_b{budget}_cap{cap}"


def abs_det(r1, r2):
    """|det| of the exponent-sum matrix; 1 for a presentation of the trivial group."""
    e = [[sum((g > 0) - (g < 0) for g in r if abs(g) == k) for k in (1, 2)]
         for r in (r1, r2)]
    return abs(e[0][0] * e[1][1] - e[0][1] * e[1][0])


def shard_dir_for(out_dir, source, budget, cap, n, side):
    return os.path.join(out_dir, "shards", stem(source, budget, cap),
                        f"L{n}" + ("_inv" if side == "inv" else ""))


def shard_ident(source, budget, cap, n, side, block, pres_id, r1, r2):
    """What a shard holds. Stored in it and compared on reuse, so a shard left
    by a run with another budget, cap or dataset is refused, never merged."""
    return json.dumps({"source": source, "node_budget": budget,
                       "max_relator_length_cap": cap, "z_len": n, "side": side,
                       "block": block, "pres_id": pres_id,
                       "r1": word_to_str(r1), "r2": word_to_str(r2)},
                      sort_keys=True, separators=(",", ":"))


def check_shard(path, ident):
    with np.load(path) as z:
        got = str(z["ident"]) if "ident" in z.files else None
    if got != ident:
        raise SystemExit(f"shard {path} is not from this run: has {got}, "
                         f"expected {ident}")


# ---------------------------------------------------------------------------
# workers
# ---------------------------------------------------------------------------
def control_task(args):
    pres_id, r1, r2, budget, cap = args
    r1s, r2s = word_to_str(r1), word_to_str(r2)
    two = run_baseline.greedy_search(r1s, r2s, budget, max_relator_length=cap,
                                     cyclic_reduce=True, high_speedup=True)
    n2 = search_n_fast(Pres(2, (r1, r2)), budget, cap=cap, cyclic=True)
    n3 = search_n_fast(Pres(3, (r1, r2, (-3,))), budget, cap=cap, cyclic=True)

    def pl(res):
        return res["path_length"] if res["solved"] else None

    row = {
        "pres_id": pres_id, "r1": r1s, "r2": r2s, "node_budget": budget,
        "max_relator_length_cap": cap, "cyclic_reduce": True,
        "solved": bool(two["solved"]), "nodes_explored": int(two["nodes_explored"]),
        "path_length": pl(two),
        "n2_solved": bool(n2["solved"]), "n2_nodes": int(n2["nodes_explored"]),
        "n2_path_length": pl(n2),
        "null_solved": bool(n3["solved"]), "null_nodes": int(n3["nodes_explored"]),
        "null_path_length": pl(n3),
        **cap_counters(n2, "n2_"), **cap_counters(n3, "null_"),
    }
    if n2["solved"]:
        # the 2-generator greedy keeps no path at high speed; the rank-n code
        # ran the same search, and verify_results replays its moves
        row["path_moves"] = list(n2["path_moves"])
    return row


def _paths_json(paths):
    return np.array(json.dumps(paths, separators=(",", ":")))


def block_task(args):
    """One (presentation, length, block): search every word of the block."""
    (pres_id, r1, r2, n, block, side, budget, cap, frac, shard, ident) = args
    if os.path.exists(shard):
        check_shard(shard, ident)
        return pres_id, n, block, 0, 0, 0.0
    lo, hi = W.block_slice(n, block)
    ws = W.words_of_length(n)[lo:hi]
    nodes = np.zeros(len(ws), dtype=np.uint16)
    plen = np.full(len(ws), -1, dtype=np.int16)
    mint = np.zeros(len(ws), dtype=np.uint8)
    dropped = np.zeros(len(ws), dtype=np.uint32)
    dmin = np.full(len(ws), -1, dtype=np.int16)
    bind = np.full(len(ws), -1, dtype=np.int32)
    paths = []
    t0 = time.time()
    for k, w in enumerate(ws):
        if side == "inv":
            w = W.inverse(w)
        res = search_n_fast(rank3(r1, r2, w), budget, cap=cap, cyclic=True)
        nodes[k] = res["nodes_explored"]
        mint[k] = min(res["min_relator_length"], 255)
        dropped[k] = min(res["cap_dropped"], 2 ** 32 - 1)
        if res["cap_dropped_min_total"] is not None:
            dmin[k] = min(res["cap_dropped_min_total"], 32767)
        if res["cap_first_bind"] is not None:
            bind[k] = res["cap_first_bind"]
        if res["solved"]:
            plen[k] = res["path_length"]
            ws_ = word_to_str(w)
            if sampled(pres_id, ws_, frac):
                paths.append({"pres_id": pres_id, "z_word": ws_, "index": lo + k,
                              "nodes_explored": int(nodes[k]),
                              "path_moves": list(res["path_moves"]),
                              **cap_counters(res)})
    secs = time.time() - t0
    tmp = shard + f".tmp{os.getpid()}.npz"
    np.savez(tmp, nodes=nodes, path_len=plen, min_total=mint,
             cap_dropped=dropped, cap_dropped_min_total=dmin,
             cap_first_bind=bind,
             seconds=np.float32(secs), paths=_paths_json(paths),
             ident=np.array(ident))
    os.replace(tmp, shard)
    return pres_id, n, block, len(ws), int((plen >= 0).sum()), secs


def sub_task(args):
    """Every relator subword of one presentation: (rows, path rows)."""
    pres_id, r1, r2, budget, cap, source = args
    r1s, r2s = word_to_str(r1), word_to_str(r2)
    rows, paths = [], []
    for w, proper in W.relator_subwords(r1, r2):
        assert 1 + len(w) <= cap, "start relator Z.w is over the cap"
        t0 = time.time()
        res = search_n_fast(rank3(r1, r2, w), budget, cap=cap, cyclic=True)
        ws_ = word_to_str(w)
        ident = {"name": f"{source}_{pres_id}", "z_word": ws_, "r1": r1s,
                 "r2": r2s, "z_relator": "Z" + ws_}
        rows.append(dict(
            ident, mode="nocov", pres_id=pres_id, source=source,
            family_tag="relsub", z_len=len(w), is_proper=bool(proper),
            node_budget=budget, max_relator_length_cap=cap, cyclic_reduce=True,
            solved=bool(res["solved"]),
            nodes_explored=int(res["nodes_explored"]),
            path_length=res["path_length"] if res["solved"] else None,
            min_total_length=int(res["min_relator_length"]),
            **cap_counters(res),
            time_seconds=round(time.time() - t0, 4)))
        if res["solved"]:
            paths.append(dict(ident, path_moves=list(res["path_moves"])))
    return pres_id, rows, paths


# ---------------------------------------------------------------------------
# parent
# ---------------------------------------------------------------------------
def _git_commit():
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"],
                                       text=True).strip()
    except Exception:
        return None


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def _read_jsonl(path):
    """Rows of a jsonl, dropping (and truncating away) a torn final line."""
    if not os.path.exists(path):
        return []
    with open(path, "rb") as f:
        data = f.read()
    good = data.rfind(b"\n") + 1
    if good != len(data):
        with open(path, "r+b") as f:
            f.truncate(good)
    return [json.loads(ln) for ln in data[:good].splitlines() if ln.strip()]


def run_control(pool, rows, a, out_dir, say):
    path = os.path.join(out_dir, f"{stem(a.source, a.budget, a.cap)}_control.jsonl")
    have = {r["pres_id"]: r for r in _read_jsonl(path)}
    todo = [(p, r1, r2, a.budget, a.cap) for p, r1, r2 in rows if p not in have]
    if todo:
        with open(path, "a") as f:
            for row in pool.imap_unordered(control_task, todo, chunksize=2):
                f.write(json.dumps(row, separators=(",", ":")) + "\n")
                have[row["pres_id"]] = row
            f.flush()
            os.fsync(f.fileno())
    bad = [r["pres_id"] for r in have.values()
           if not ((r["solved"], r["nodes_explored"], r["path_length"])
                   == (r["n2_solved"], r["n2_nodes"], r["n2_path_length"])
                   == (r["null_solved"], r["null_nodes"], r["null_path_length"]))]
    if bad:
        raise SystemExit(f"control mismatch (2-gen vs rank-n port vs null "
                         f"stabilization) on pres_ids {sorted(bad)[:20]}")
    solved = sum(have[p]["solved"] for p, _, _ in rows)
    say(f"control: {solved}/{len(rows)} solved at budget {a.budget}; "
        f"2-gen == rank-n port == null stabilization on all {len(rows)}")
    return have


def merge_length(n, side, rows, a, out_dir, shard_dir, meta, say):
    """Shards of one length -> one compressed npz + the path-sample jsonl pair."""
    suffix = "_inv" if side == "inv" else ""
    base = os.path.join(out_dir, f"{stem(a.source, a.budget, a.cap)}_L{n}{suffix}")
    nw, nb = W.n_words(n), W.n_blocks(n)
    nodes = np.zeros((len(rows), nw), dtype=np.uint16)
    plen = np.full((len(rows), nw), -1, dtype=np.int16)
    mint = np.zeros((len(rows), nw), dtype=np.uint8)
    dropped = np.zeros((len(rows), nw), dtype=np.uint32)
    dmin = np.full((len(rows), nw), -1, dtype=np.int16)
    bind = np.full((len(rows), nw), -1, dtype=np.int32)
    secs = np.zeros((len(rows), nb), dtype=np.float32)
    sample, used = [], []
    ws = W.words_of_length(n)
    for i, (pres_id, r1, r2) in enumerate(rows):
        r1s, r2s = word_to_str(r1), word_to_str(r2)
        for b in range(nb):
            shard = os.path.join(shard_dir, f"p{pres_id:04d}_b{b:03d}.npz")
            lo, hi = W.block_slice(n, b)
            check_shard(shard, shard_ident(a.source, a.budget, a.cap, n, side,
                                           b, pres_id, r1, r2))
            with np.load(shard) as z:
                nodes[i, lo:hi] = z["nodes"]
                plen[i, lo:hi] = z["path_len"]
                mint[i, lo:hi] = z["min_total"]
                dropped[i, lo:hi] = z["cap_dropped"]
                dmin[i, lo:hi] = z["cap_dropped_min_total"]
                bind[i, lo:hi] = z["cap_first_bind"]
                secs[i, b] = float(z["seconds"])
                paths = json.loads(str(z["paths"]))
            used.append(shard)
            for p in paths:
                sample.append((pres_id, r1s, r2s, p))
    if int((nodes == 0).sum()):
        raise SystemExit(f"L{n}{suffix}: {int((nodes == 0).sum())} rows missing")
    with open(base + "_sample.jsonl", "w") as f, \
            open(base + "_sample_paths.jsonl", "w") as g:
        for pres_id, r1s, r2s, p in sorted(sample, key=lambda t: (t[0], t[3]["index"])):
            ident = {"name": f"{a.source}_{pres_id}", "z_word": p["z_word"],
                     "r1": r1s, "r2": r2s, "z_relator": "Z" + p["z_word"]}
            f.write(json.dumps(dict(
                ident, mode="nocov", pres_id=pres_id, source=a.source,
                family_tag=FAMILY_TAG, side=side, z_len=n, word_index=p["index"],
                node_budget=a.budget, max_relator_length_cap=a.cap,
                cyclic_reduce=True, solved=True,
                nodes_explored=p["nodes_explored"],
                path_length=len(p["path_moves"]),
                **{k: p[k] for k in CAP_FIELDS}), separators=(",", ":")) + "\n")
            g.write(json.dumps(dict(ident, path_moves=p["path_moves"]),
                               separators=(",", ":")) + "\n")
    pres_ids = np.array([p for p, _, _ in rows], dtype=np.int32)
    words = np.array([word_to_str(W.inverse(w) if side == "inv" else w)
                      for w in ws])
    # the counters first: a merged length always has both files
    tmp = base + "_capcount.tmp.npz"
    np.savez_compressed(
        tmp, cap_dropped=dropped, cap_dropped_min_total=dmin,
        cap_first_bind=bind, pres_ids=pres_ids, words=words,
        meta=np.array(json.dumps(dict(meta, z_len=n, side=side, n_words=nw,
                                      fields=CAP_DOC))))
    os.replace(tmp, base + "_capcount.npz")
    tmp = base + ".tmp.npz"
    np.savez_compressed(
        tmp, nodes=nodes, path_len=plen, min_total=mint, block_seconds=secs,
        pres_ids=pres_ids, words=words,
        meta=np.array(json.dumps(dict(meta, z_len=n, side=side,
                                      n_words=nw, n_sample=len(sample)))))
    os.replace(tmp, base + ".npz")
    for s in used:
        os.remove(s)
    for d in (shard_dir, os.path.dirname(shard_dir)):
        try:
            os.rmdir(d)
        except OSError:
            pass
    n_solved = int((plen >= 0).sum())
    say(f"merged L{n}{suffix}: {nodes.size} searches, {n_solved} solved "
        f"({100 * n_solved / nodes.size:.2f}%), {len(sample)} sampled paths, "
        f"cap dropped a child in {int((dropped > 0).sum())}, "
        f"could bind in {int((bind >= 0).sum())}, "
        f"core-seconds {float(secs.sum()):.0f} -> {base}.npz")


def run_bf(pool, rows, ctrl, n, side, a, out_dir, meta, say):
    suffix = "_inv" if side == "inv" else ""
    base = os.path.join(out_dir, f"{stem(a.source, a.budget, a.cap)}_L{n}{suffix}")
    if os.path.exists(base + ".npz"):
        say(f"L{n}{suffix}: already merged, skipping")
        return
    shard_dir = shard_dir_for(out_dir, a.source, a.budget, a.cap, n, side)
    os.makedirs(shard_dir, exist_ok=True)
    frac = min(1.0, a.path_sample_target / (W.n_words(n) * len(rows)))
    for f in os.listdir(shard_dir):
        if ".tmp" in f:
            os.remove(os.path.join(shard_dir, f))
    tasks = []
    for pres_id, r1, r2 in rows:
        for b in range(W.n_blocks(n)):
            shard = os.path.join(shard_dir, f"p{pres_id:04d}_b{b:03d}.npz")
            ident = shard_ident(a.source, a.budget, a.cap, n, side, b,
                                pres_id, r1, r2)
            if os.path.exists(shard):
                check_shard(shard, ident)
            else:
                tasks.append((pres_id, r1, r2, n, b, side, a.budget, a.cap,
                              frac, shard, ident))
    total = len(rows) * W.n_blocks(n)
    say(f"L{n}{suffix}: {W.n_words(n)} words x {len(rows)} presentations = "
        f"{W.n_words(n) * len(rows)} searches in {total} tasks, {len(tasks)} to run")
    # the slow presentations (control unsolved, then most control nodes) first
    tasks.sort(key=lambda t: (ctrl[t[0]]["solved"], -ctrl[t[0]]["nodes_explored"]))
    t0, done, searched, solved, core = time.time(), 0, 0, 0, 0.0
    last = t0
    for _, _, _, k, s, secs in pool.imap_unordered(block_task, tasks, chunksize=1):
        done += 1
        searched += k
        solved += s
        core += secs
        if time.time() - last >= a.log_every or done == len(tasks):
            last = time.time()
            say(f"L{n}{suffix} progress {done}/{len(tasks)} tasks, "
                f"{searched} searches, solved={solved}, "
                f"elapsed={time.time() - t0:.0f}s, core-seconds={core:.0f}")
    merge_length(n, side, rows, a, out_dir, shard_dir, meta, say)


def _dump(rows):
    return "".join(json.dumps(r, separators=(",", ":")) + "\n" for r in rows)


def run_sub(pool, rows, a, out_dir, say):
    base = os.path.join(out_dir, f"{stem(a.source, a.budget, a.cap)}_relsub")
    path, ppath = base + ".jsonl", base + "_paths.jsonl"
    done = {r["pres_id"] for r in _read_jsonl(path)}
    _read_jsonl(ppath)          # drops a torn final line
    todo = [(p, r1, r2, a.budget, a.cap, a.source)
            for p, r1, r2 in rows if p not in done]
    todo.sort(key=lambda t: -(len(t[1]) + len(t[2])))
    n, solved, t0 = 0, 0, time.time()
    # paths first, then the rows in ONE write: a presentation is in `done` only
    # when its certificates are already on disk
    with open(path, "a") as f, open(ppath, "a") as g:
        for _, out, paths in pool.imap_unordered(sub_task, todo, chunksize=1):
            g.write(_dump(paths))
            g.flush()
            os.fsync(g.fileno())
            f.write(_dump(out))
            f.flush()
            os.fsync(f.fileno())
            n += len(out)
            solved += len(paths)
    say(f"relsub: {n} new rows ({solved} solved) for {len(todo)} presentations "
        f"in {time.time() - t0:.0f}s -> {path}")


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="data/ms640_solved.txt")
    ap.add_argument("--source", default="ms640")
    ap.add_argument("--budget", type=int, required=True)
    ap.add_argument("--cap", type=int, default=CAP)
    ap.add_argument("--min-len", type=int, default=1)
    ap.add_argument("--max-len", type=int, required=True,
                    help="brute-force every w with min-len <= |w| <= max-len "
                         "(0: skip the brute-force arm)")
    ap.add_argument("--inv-max-len", type=int, default=0,
                    help="also run w^-1 for every w up to this length")
    ap.add_argument("--no-sub", action="store_true",
                    help="skip the relator-subword arm")
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    ap.add_argument("--path-sample-target", type=int, default=2000,
                    help="rows per length whose path is kept if solved "
                         "(the fraction is target / searches, at most 1)")
    ap.add_argument("--pres", default=None,
                    help="comma list of pres_ids (default: all)")
    ap.add_argument("--out-dir", default=OUT_DIR)
    ap.add_argument("--log-every", type=float, default=60.0)
    a = ap.parse_args(argv)
    os.chdir(find_repo_root(os.path.dirname(os.path.abspath(__file__))))

    assert 0 < a.budget <= 65535, "node counts are stored as uint16"
    assert 1 + max(a.max_len, a.inv_max_len) <= a.cap, \
        "start relator Z.w is over the cap"
    rows = load_ms640(a.dataset)
    bad = [p for p, r1, r2 in rows if abs_det(r1, r2) != 1]
    assert not bad, f"not presentations of the trivial group: pres_ids {bad[:10]}"
    if a.pres:
        keep = {int(x) for x in a.pres.split(",")}
        rows = [r for r in rows if r[0] in keep]
    out_dir = a.out_dir
    os.makedirs(out_dir, exist_ok=True)
    log = os.path.join(out_dir, f"{stem(a.source, a.budget, a.cap)}.log")

    def say(msg):
        line = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {msg}"
        print(line, flush=True)
        with open(log, "a") as f:
            f.write(line + "\n")

    import numba
    meta = {
        "source": a.source, "dataset": a.dataset,
        "dataset_sha256": _sha256(a.dataset), "node_budget": a.budget,
        "max_relator_length_cap": a.cap, "cyclic_reduce": True,
        "solver": SOLVER, "family_tag": FAMILY_TAG, "block": W.BLOCK,
        "path_sample_target": a.path_sample_target, "commit": _git_commit(),
        "python": platform.python_version(), "numpy": np.__version__,
        "numba": numba.__version__, "n_presentations": len(rows),
    }
    say(f"start budget={a.budget} cap={a.cap} lengths={a.min_len}..{a.max_len} "
        f"inv<= {a.inv_max_len} workers={a.workers} pres={len(rows)} "
        f"commit={meta['commit']}")
    # compile once before forking, and build the word lists the workers share
    search_n_fast(rank3((1, 2), (1, -2), (1,)), 10, cap=a.cap, cyclic=True)
    run_baseline.greedy_search("xy", "xY", 10, max_relator_length=a.cap,
                               cyclic_reduce=True, high_speedup=True)
    for n in range(1, max(a.max_len, a.inv_max_len) + 1):
        assert len(W.words_of_length(n)) == W.n_words(n)
    t0 = time.time()
    with get_context("fork").Pool(a.workers) as pool:
        ctrl = run_control(pool, rows, a, out_dir, say)
        if not a.no_sub:
            run_sub(pool, rows, a, out_dir, say)
        for n in range(a.min_len, a.max_len + 1):
            run_bf(pool, rows, ctrl, n, "fwd", a, out_dir, meta, say)
            if n <= a.inv_max_len:
                run_bf(pool, rows, ctrl, n, "inv", a, out_dir, meta, say)
    say(f"done total_wall={time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
