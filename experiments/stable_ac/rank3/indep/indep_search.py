#!/usr/bin/env python3
"""indep_search.py - independent re-run of stored greedy best-first results.

Usage:
    python3 indep_search.py <RESULTS_DIR> <DATASET> <OUT_JSON> [workers] [minutes]

A second implementation of the experiment's "standard greedy" (best-first on
total relator length over seam-cancelling AC moves, any rank), written from the
prose definition in experiments/stable_ac/rank3/PLAN.md section 2, with the
details the prose leaves open pinned down from the slow reference
experiments/stable_ac/solvern.py (read, not imported, not pasted). It re-runs
randomly chosen stored cells and compares (solved, nodes, path_len).

Nothing from the repository is imported. Standard library + numpy (numpy is
used only to read the .npz files, never inside the search).

Exit code: 0 no mismatch, 3 any mismatch, 1 crash / job error / nothing compared.
"""

import heapq
import json
import multiprocessing as mp
import os
import random
import sys
import time
import traceback

import numpy as np

SCRIPT = "indep_search.py"
SEED = 12345
CAP = 24
STEM_1K = "rank3_bf_ms640_b1000_cap24"
STEM_10K = "rank3_bf_ms640_b10000_cap24"
RANKN_STEM = "rankn_bf_ms640_b1000_cap24_r%d"
LENGTHS = tuple(range(1, 11))
INV_EXPECTED = tuple(range(1, 7))

N_R3 = 150          # cells per rank-3 budget-1,000 length file
N_R3_INV = 40       # cells per rank-3 budget-1,000 _inv file
N_RN = 200          # cells per rank-4 / rank-5 file
N_RN_NULL = 30      # null starts per rank-4 / rank-5 file
N_B10K = 15         # cells per rank-3 budget-10,000 length file
N_R3_NULL = 30      # extra: rank-3 null starts against the control file

MAX_EXAMPLES = 50
MAX_EX_PER_CHECK = 6

GEN_CHARS = "xyzabcdefghijklmnopqrstuvw"
MAXG = len(GEN_CHARS)


# ---------------------------------------------------------------------------
# words as tuples of signed ints (+k = generator k, -k = its inverse)
# ---------------------------------------------------------------------------
def str_to_word(s):
    out = []
    for ch in s:
        k = GEN_CHARS.index(ch.lower()) + 1
        out.append(k if ch.islower() else -k)
    return tuple(out)


def word_to_str(w):
    return "".join(GEN_CHARS[g - 1] if g > 0 else GEN_CHARS[-g - 1].upper() for g in w)


# ---------------------------------------------------------------------------
# NAIVE search: a literal, slow transcription of the definition on signed-int
# tuples. Used only (a) in the start-up self-test against the fast search and
# (b) to re-run a few cells where the fast search disagrees with the stored
# value, so that a disagreement can be attributed.
# ---------------------------------------------------------------------------
def nv_reduce(w):
    """Free reduction, then cyclic reduction (strip cancelling end pairs)."""
    st = []
    for g in w:
        if st and st[-1] == -g:
            st.pop()
        else:
            st.append(g)
    a = 0
    b = len(st) - 1
    while a < b and st[a] == -st[b]:
        a += 1
        b -= 1
    return tuple(st[a:b + 1])


def nv_okey(w):
    """Letter order of the canonical form: higher generator first, inverse first."""
    return tuple((-abs(g), g > 0) for g in w)


def nv_canon(w):
    """Least word among all rotations of w and of w^-1."""
    n = len(w)
    if n == 0:
        return w
    best = None
    best_k = None
    for u in (w, tuple(-g for g in reversed(w))):
        dk = nv_okey(u + u)
        for k in range(n):
            rk = dk[k:k + n]
            if best_k is None or rk < best_k:
                best_k = rk
                best = u[k:] + u[:k]
    return best


def nv_sortkey(r):
    return (len(r), nv_okey(r))


def nv_tie(state):
    """Heap tie-break: inverse letters (by index) below generators (by index)."""
    return tuple(tuple((g > 0, abs(g)) for g in r) for r in state)


def naive_search(rels, budget, cap):
    st0 = tuple(sorted((nv_canon(nv_reduce(tuple(r))) for r in rels), key=nv_sortkey))
    n = len(st0)
    seen = {st0}
    heap = [(sum(len(r) for r in st0), 0, nv_tie(st0), st0)]
    nodes = 0
    while heap and nodes < budget:
        _total, depth, _tie, st = heapq.heappop(heap)
        nodes += 1
        if all(len(r) == 1 for r in st):
            return (True, nodes, depth)
        for i in range(n):
            ri = st[i]
            if not ri:
                continue
            for j in range(n):
                if j == i or not st[j]:
                    continue
                for sign in (1, -1):
                    o = st[j] if sign == 1 else tuple(-g for g in reversed(st[j]))
                    for k1 in range(len(ri)):
                        a = ri[len(ri) - k1:] + ri[:len(ri) - k1]
                        for k2 in range(len(o)):
                            b = o[len(o) - k2:] + o[:len(o) - k2]
                            if a[-1] != -b[0]:
                                continue
                            child = list(st)
                            child[i] = nv_canon(nv_reduce(a + b))
                            if any(len(r) > cap for r in child):
                                continue
                            child.sort(key=nv_sortkey)
                            ch = tuple(child)
                            if ch in seen:
                                continue
                            seen.add(ch)
                            heapq.heappush(
                                heap, (sum(len(r) for r in ch), depth + 1, nv_tie(ch), ch))
    return (False, nodes, -1)


# ---------------------------------------------------------------------------
# FAST search: the same algorithm on byte strings.
#
# A letter g is stored as the byte  2*(MAXG-|g|) + (g>0) + 1  (1..52), so that
# plain bytes comparison IS the canonical-form order (higher generator index
# first, inverse before generator: .. Z<z<Y<y<X<x). INV maps a letter byte to
# its inverse; TIE maps it to the tie-break alphabet |g| + 64*(g>0), in which
# every inverse letter sorts below every generator and indices ascend.
# ---------------------------------------------------------------------------
def _code(g):
    return 2 * (MAXG - abs(g)) + (1 if g > 0 else 0) + 1


_t_inv = bytearray(range(256))
_t_tie = bytearray(256)
for _g in range(1, MAXG + 1):
    _t_inv[_code(_g)] = _code(-_g)
    _t_inv[_code(-_g)] = _code(_g)
    _t_tie[_code(_g)] = 64 + _g
    _t_tie[_code(-_g)] = _g
INV = bytes(_t_inv)
TIE = bytes(_t_tie)
SEP = b"\x00"

PAIR = {}       # (target word, partner word) -> tuple of distinct canonical new targets
CANON = {}      # reduced word -> canonical word
INTERN = {}     # canonical word -> the one shared object
_CACHE = {"cap": None}
PAIR_LIMIT = 60000
CANON_LIMIT = 300000


def encode(w):
    return bytes([_code(g) for g in w])


def reduce_any(w):
    """Free then cyclic reduction of an arbitrary coded word (start states only)."""
    st = bytearray()
    for c in w:
        if st and st[-1] == INV[c]:
            st.pop()
        else:
            st.append(c)
    a = 0
    b = len(st) - 1
    while a < b and st[a] == INV[st[b]]:
        a += 1
        b -= 1
    return bytes(st[a:b + 1])


def canon(w):
    """Least coded word among all rotations of w and of w^-1."""
    n = len(w)
    if n == 0:
        return w
    v = w[::-1].translate(INV)
    d = w + w
    e = v + v
    return min(min([d[k:k + n] for k in range(n)]),
               min([e[k:k + n] for k in range(n)]))


def _lenlex(w):
    return (len(w), w)


def expand_pair(ri, rj, cap):
    """Distinct canonical words reduce(rot(ri) . rot(rj^s)), s = +1 then -1, over
    every pair of rotations whose seam cancels, new word no longer than cap.

    ri and rj are relators of a state, hence cyclically reduced, so every
    rotation is freely reduced and the free reduction of the concatenation is
    exactly the cancellation at the seam. First-seen order follows
    s -> k1 -> k2 with right rotations (rot_k(w) = w[-k:] + w[:-k]).
    """
    if len(CANON) > CANON_LIMIT:
        CANON.clear()
    inv = INV
    canon_get = CANON.get
    out = []
    got = set()
    la = len(ri)
    di = ri + ri
    rots = [di[la - k:2 * la - k] for k in range(la)]
    for o in (rj, rj[::-1].translate(inv)):
        lb = len(o)
        do = o + o
        by_first = {}
        for k in range(lb):
            b = do[lb - k:2 * lb - k]
            first = b[0]
            if first in by_first:
                by_first[first].append(b)
            else:
                by_first[first] = [b]
        m = la if la < lb else lb
        for a in rots:
            lst = by_first.get(inv[a[la - 1]])
            if lst is None:
                continue
            ai = a[::-1].translate(inv)
            for b in lst:
                c = 1
                while c < m and ai[c] == b[c]:
                    c += 1
                f = a[:la - c] + b[c:]
                n = la + lb - 2 * c
                if n > 1 and f[0] == inv[f[n - 1]]:
                    t = 1
                    while 2 * t < n and f[t] == inv[f[n - 1 - t]]:
                        t += 1
                    f = f[t:n - t]
                    n -= 2 * t
                if n > cap:
                    continue
                w = canon_get(f)
                if w is None:
                    w = canon(f)
                    w = INTERN.setdefault(w, w)
                    CANON[f] = w
                if w not in got:
                    got.add(w)
                    out.append(w)
    return tuple(out)


def search(rels, budget, cap):
    """Greedy best-first search. rels: relators as tuples of signed ints.

    Returns (solved, nodes popped, path length or -1).
    """
    if _CACHE["cap"] != cap or len(PAIR) > PAIR_LIMIT:
        PAIR.clear()
        CANON.clear()
        INTERN.clear()
        _CACHE["cap"] = cap
    key = tuple(sorted((canon(reduce_any(encode(r))) for r in rels), key=_lenlex))
    n = len(key)
    total = 0
    for r in key:
        total += len(r)
    seen = {key}
    heap = [(total, 0, SEP.join(key).translate(TIE), key)]
    pop = heapq.heappop
    push = heapq.heappush
    pair_get = PAIR.get
    tie = TIE
    sep_join = SEP.join
    idx = range(n)
    nodes = 0
    while heap and nodes < budget:
        total, depth, _tb, key = pop(heap)
        nodes += 1
        # key is sorted by length, so "every relator has length 1" is exactly
        # "shortest relator has length 1 and the total is n".
        if total == n and len(key[0]) == 1:
            return (True, nodes, depth)
        n_over = 0
        for r in key:
            if len(r) > cap:
                n_over += 1
        depth1 = depth + 1
        for i in idx:
            ri = key[i]
            li = len(ri)
            if li == 0:
                continue
            if n_over and n_over - (1 if li > cap else 0) > 0:
                continue        # another relator is over the cap: every child is dropped
            rest = key[:i] + key[i + 1:]
            base = total - li
            for j in idx:
                if j == i:
                    continue
                rj = key[j]
                if not rj:
                    continue
                pk = (ri, rj)
                kids = pair_get(pk)
                if kids is None:
                    kids = expand_pair(ri, rj, cap)
                    PAIR[pk] = kids
                for c in kids:
                    lc = len(c)
                    p = 0
                    for r in rest:
                        lr = len(r)
                        if lr < lc or (lr == lc and r < c):
                            p += 1
                        else:
                            break
                    ckey = rest[:p] + (c,) + rest[p:]
                    if ckey in seen:
                        continue
                    seen.add(ckey)
                    push(heap, (base + lc, depth1, sep_join(ckey).translate(tie), ckey))
    return (False, nodes, -1)


# ---------------------------------------------------------------------------
# self-test: fast search against the naive one (both written here)
# ---------------------------------------------------------------------------
def self_test(dataset, t_limit=20.0):
    t0 = time.time()
    npres = len(dataset)
    # edge cases first (they are the ones that catch a slip), then real
    # presentations by increasing relator length, so the time limit cuts the
    # slow, least informative cases
    cases = [
        ("synthetic, relator cancels to empty", ((1, 2), (1, 2), (-3, 1)), 60, CAP),
        ("synthetic AK(3)", ((1, 2, 1, -2, -1, -2), (1, 1, 1, -2, -2, -2, -2)), 60, CAP),
    ]
    if npres:
        r1, r2 = dataset[0]
        cases.append(("p0 rank 2 start over a small cap", (r1, r2), 60, 4))
        cases.append(("p0 rank 3 duplicate relator", (r1, r1, (-3, 2)), 40, CAP))
        cases.append(("p0 rank 3 unreduced start",
                      (r1 + (1, -1), (2,) + r2 + (-2,), (-3, 1, 2, -2, -1, 1)), 60, CAP))
        cases.append(("p0 rank 3 null", (r1, r2, (-3,)), 60, CAP))
        cases.append(("p0 rank 4", (r1, r2, (-3, 1), (-4, 2, -1)), 60, CAP))
        cases.append(("p0 rank 5", (r1, r2, (-3, 1), (-4, 2, -1), (-5, 2, -1)), 40, CAP))
    pids = []
    for pid in (0, 3, 7, 9, npres // 4, npres // 2, npres - 1):
        if 0 <= pid < npres and pid not in pids:
            pids.append(pid)
    pids.sort(key=lambda q: (len(dataset[q][0]) + len(dataset[q][1]), q))
    for pid in pids:
        r1, r2 = dataset[pid]
        cases.append(("p%d rank 2" % pid, (r1, r2), 40, CAP))
        cases.append(("p%d rank 3 w=xy" % pid, (r1, r2, (-3, 1, 2)), 40, CAP))
    compared = 0
    bad = []
    not_run = 0
    for name, rels, budget, cap in cases:
        if time.time() - t0 > t_limit:
            not_run += 1
            continue
        fast = search(rels, budget, cap)
        slow = naive_search(rels, budget, cap)
        compared += 1
        if tuple(fast) != tuple(slow):
            bad.append({"check": "selftest_fast_vs_naive", "what": name,
                        "start": [word_to_str(r) for r in rels],
                        "budget": budget, "cap": cap,
                        "mine": list(fast), "own_naive_rerun": list(slow)})
    detail = ("my byte-coded search against my literal tuple search on %d small starts "
              "(ranks 2-5, budgets 40-60); %d not run (self-test time limit); %.1f s"
              % (len(cases), not_run, time.time() - t0))
    return compared, bad, detail


# ---------------------------------------------------------------------------
# worker
# ---------------------------------------------------------------------------
_NAIVE_LEFT = [2]       # per worker process


def run_job(job):
    jid, rels, budget, cap, stored = job
    t0 = time.time()
    try:
        res = search(rels, budget, cap)
        naive = None
        if tuple(res) != tuple(stored) and budget <= 1000 and _NAIVE_LEFT[0] > 0:
            _NAIVE_LEFT[0] -= 1
            try:
                naive = tuple(naive_search(rels, budget, cap))
            except Exception as exc:                      # diagnosis only
                naive = "naive re-run failed: %s: %s" % (type(exc).__name__, exc)
        return (jid, tuple(res), naive, time.time() - t0, None)
    except Exception:
        return (jid, None, None, time.time() - t0, traceback.format_exc(limit=6))


# ---------------------------------------------------------------------------
# reading the inputs, planning the jobs
# ---------------------------------------------------------------------------
def load_dataset(path):
    pres = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            vals = json.loads(line)
            half = len(vals) // 2
            r1 = tuple(int(g) for g in vals[:half] if int(g) != 0)
            r2 = tuple(int(g) for g in vals[half:] if int(g) != 0)
            pres.append((r1, r2))
    return pres


def norm_triple(solved, nodes, plen):
    """(solved, nodes, path_len) with 'no path' (null or -1) written as -1."""
    return (bool(solved), int(nodes), -1 if plen is None else int(plen))


def new_group(state, name, kind, fname):
    state["groups"].append({"name": name, "kind": kind, "file": fname, "jobs": []})
    return len(state["groups"]) - 1


def add_job(state, gi, rels, budget, cap, stored, pres_id, label):
    jid = len(state["info"])
    state["info"].append((gi, pres_id, label, rels, budget, cap, stored))
    state["groups"][gi]["jobs"].append((jid, rels, budget, cap, stored))
    return jid


def read_meta(z):
    if "meta" not in z.files:
        return {}
    try:
        return json.loads(str(z["meta"].item()))
    except Exception:
        return {}


def presentation(dataset, pid):
    if not 0 <= pid < len(dataset):
        raise ValueError("pres_id %d is outside the dataset (%d lines)" % (pid, len(dataset)))
    return dataset[pid]


def plan_control(state, path, fname, dataset, rng_order, rng_null):
    rows = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    out = {"rows": len(rows), "distinct": len(set(int(r["pres_id"]) for r in rows)),
           "str_cmp": 0, "str_bad": 0, "str_ex": [], "par_cmp": 0, "par_bad": 0, "n2": {}}
    order = list(range(len(rows)))
    rng_order.shuffle(order)       # a time-out then leaves a random subset, not a prefix
    with_null = []
    pending = []
    for t in order:
        row = rows[t]
        pid = int(row["pres_id"])
        r1, r2 = presentation(dataset, pid)
        if "r1" in row and "r2" in row:
            out["str_cmp"] += 1
            if row["r1"] != word_to_str(r1) or row["r2"] != word_to_str(r2):
                out["str_bad"] += 1
                if len(out["str_ex"]) < 3:
                    out["str_ex"].append({
                        "check": "control_b1000_relators_vs_dataset", "pres_id": pid,
                        "what": "r1, r2 of the control row against the dataset line",
                        "stored": [str(row["r1"]), str(row["r2"])],
                        "mine": [word_to_str(r1), word_to_str(r2)]})
        budget = int(row.get("node_budget", 1000))
        cap = int(row.get("max_relator_length_cap", CAP))
        out["par_cmp"] += 1
        if budget != 1000 or cap != CAP:
            out["par_bad"] += 1
        stored = norm_triple(row["solved"], row["nodes_explored"], row.get("path_length"))
        n2 = None
        if "n2_solved" in row and "n2_nodes" in row:
            n2 = norm_triple(row["n2_solved"], row["n2_nodes"], row.get("n2_path_length"))
        pending.append(((r1, r2), budget, cap, stored, pid, "rank 2 control", n2))
        if "null_solved" in row and "null_nodes" in row:
            with_null.append(t)
    with_null.sort()
    pending_null = []
    for t in rng_null.sample(with_null, min(N_R3_NULL, len(with_null))):
        row = rows[t]
        pid = int(row["pres_id"])
        r1, r2 = presentation(dataset, pid)
        stored = norm_triple(row["null_solved"], row["null_nodes"],
                             row.get("null_path_length"))
        pending_null.append(((r1, r2, (-3,)), int(row.get("node_budget", 1000)),
                             int(row.get("max_relator_length_cap", CAP)), stored, pid,
                             "rank 3 null start (Z)"))
    # nothing above raised: register the jobs
    gi = new_group(state, "control_b1000", "control", fname)
    for item in pending:
        jid = add_job(state, gi, item[0], item[1], item[2], item[3], item[4], item[5])
        if item[6] is not None:
            out["n2"][jid] = item[6]
    gnull = new_group(state, "extra_rank3_null_b1000", "extra_rank3_null", fname)
    for item in pending_null:
        add_job(state, gnull, item[0], item[1], item[2], item[3], item[4], item[5])
    return out


def plan_rank3_file(state, path, fname, name, kind, budget_stem, count, rng, dataset,
                    meta_checks):
    """Pick `count` random (presentation, word) cells of one rank-3 length file."""
    with np.load(path, allow_pickle=False) as z:
        meta = read_meta(z)
        pres_ids = [int(v) for v in z["pres_ids"]]
        words = [str(v) for v in z["words"]]
        nodes = z["nodes"]
        plen = z["path_len"]
        if nodes.ndim != 2 or plen.shape != nodes.shape:
            raise ValueError("nodes %r / path_len %r shapes" % (nodes.shape, plen.shape))
        rows, cols = int(nodes.shape[0]), int(nodes.shape[1])
        if len(pres_ids) != rows or len(words) != cols:
            raise ValueError("%d pres_ids, %d words for a %dx%d array"
                             % (len(pres_ids), len(words), rows, cols))
        budget = int(meta.get("node_budget", budget_stem))
        cap = int(meta.get("max_relator_length_cap", CAP))
        pending = []
        total = rows * cols
        for flat in rng.sample(range(total), min(count, total)):
            r, c = divmod(flat, cols)
            pid = pres_ids[r]
            r1, r2 = presentation(dataset, pid)
            w = words[c]
            p = int(plen[r, c])
            stored = (p >= 0, int(nodes[r, c]), p)
            pending.append(((r1, r2, (-3,) + str_to_word(w)), budget, cap, stored, pid,
                            "rank 3, w=%s (row %d, column %d)" % (w, r, c)))
        del nodes, plen
    # nothing above raised: register the jobs. A file whose meta is missing,
    # unreadable or lacks the two values is a failed meta check (the search then
    # ran on the file name's values), never a silently skipped one.
    meta_checks.append((fname,
                        "node_budget" in meta and "max_relator_length_cap" in meta
                        and budget == budget_stem and cap == CAP,
                        "meta node_budget=%s cap=%s (None = not recorded), file name "
                        "says %d / %d"
                        % (meta.get("node_budget"), meta.get("max_relator_length_cap"),
                           budget_stem, CAP)))
    gi = new_group(state, name, kind, fname)
    for item in pending:
        add_job(state, gi, item[0], item[1], item[2], item[3], item[4], item[5])
    return words


def plan_rankn_file(state, path, fname, rank, rng_cells, rng_null, dataset, meta_checks):
    with np.load(path, allow_pickle=False) as z:
        meta = read_meta(z)
        pres_ids = [int(v) for v in z["pres_ids"]]
        combos = z["combos"]
        nodes = z["nodes"]
        plen = z["path_len"]
        null = z["null"]
        if "words" not in meta:
            raise ValueError("meta has no 'words' list")
        words = [str(w) for w in meta["words"]]
        if nodes.ndim != 2 or plen.shape != nodes.shape or combos.ndim != 2:
            raise ValueError("array shapes nodes %r path_len %r combos %r"
                             % (nodes.shape, plen.shape, combos.shape))
        rows, ncomb = int(nodes.shape[0]), int(nodes.shape[1])
        k = int(combos.shape[1])
        if len(pres_ids) != rows or int(combos.shape[0]) != ncomb:
            raise ValueError("%d pres_ids, %d combos for a %dx%d array"
                             % (len(pres_ids), int(combos.shape[0]), rows, ncomb))
        if null.ndim != 2 or int(null.shape[0]) != rows or int(null.shape[1]) < 3:
            raise ValueError("'null' has shape %r" % (null.shape,))
        budget = int(meta.get("node_budget", 1000))
        cap = int(meta.get("max_relator_length_cap", CAP))
        ok = (budget == 1000 and cap == CAP and k == rank - 2
              and all(name in meta for name in ("rank", "extra_generators", "node_budget",
                                                "max_relator_length_cap"))
              and int(meta.get("rank", rank)) == rank
              and int(meta.get("extra_generators", k)) == k)
        meta_text = ("meta rank=%s extra_generators=%s node_budget=%s cap=%s (None = not "
                     "recorded), combos have "
                     "%d columns; expected rank %d, %d extra, 1000 / %d"
                     % (meta.get("rank"), meta.get("extra_generators"),
                        meta.get("node_budget"), meta.get("max_relator_length_cap"),
                        k, rank, rank - 2, CAP))
        pending = []
        total = rows * ncomb
        for flat in rng_cells.sample(range(total), min(N_RN, total)):
            r, c = divmod(flat, ncomb)
            pid = pres_ids[r]
            r1, r2 = presentation(dataset, pid)
            # column t of the combo is the word of extra generator 3 + t
            zw = [words[int(v)] for v in combos[c]]
            extra = tuple((-(3 + t),) + str_to_word(zw[t]) for t in range(k))
            p = int(plen[r, c])
            stored = (p >= 0, int(nodes[r, c]), p)
            pending.append(((r1, r2) + extra, budget, cap, stored, pid,
                            "rank %d, words %s (row %d, combo %d)"
                            % (rank, ",".join(zw), r, c)))
        pending_null = []
        for r in rng_null.sample(range(rows), min(N_RN_NULL, rows)):
            pid = pres_ids[r]
            r1, r2 = presentation(dataset, pid)
            extra = tuple((-(3 + t),) for t in range(k))
            stored = norm_triple(int(null[r, 0]) != 0, int(null[r, 1]), int(null[r, 2]))
            pending_null.append(((r1, r2) + extra, budget, cap, stored, pid,
                                 "rank %d null start (row %d)" % (rank, r)))
        del nodes, plen, null, combos
    # nothing above raised: register the jobs
    meta_checks.append((fname, ok, meta_text))
    gi = new_group(state, "rank%d_b1000" % rank, "rank%d" % rank, fname)
    for item in pending:
        add_job(state, gi, item[0], item[1], item[2], item[3], item[4], item[5])
    gnull = new_group(state, "rank%d_b1000_null" % rank, "rank%d_null" % rank, fname)
    for item in pending_null:
        add_job(state, gnull, item[0], item[1], item[2], item[3], item[4], item[5])


def interleave(groups):
    """Job j of a group of m jobs gets position j/m: the first job of every
    group comes first, and any prefix of the run holds about the same share of
    every group."""
    order = []
    for gi, g in enumerate(groups):
        m = len(g["jobs"])
        for j, job in enumerate(g["jobs"]):
            order.append((j / m, gi, j, job))
    order.sort(key=lambda t: (t[0], t[1], t[2]))
    return [t[3] for t in order]


# ---------------------------------------------------------------------------
# reporting
# ---------------------------------------------------------------------------
def fail_check(name, fname, exc):
    return {"name": name, "compared": 0, "mismatches": 1,
            "detail": "COMPARED 0 - NOT A PASS; could not use %s: %s: %s (counted as one "
                      "mismatch)" % (fname, type(exc).__name__, exc)}


def example(check, inf, mine, naive):
    return {"check": check, "pres_id": inf[1], "what": inf[2],
            "start": [word_to_str(r) for r in inf[3]],
            "budget": inf[4], "cap": inf[5],
            "order": "(solved, nodes, path_len)",
            "stored": list(inf[6]), "mine": list(mine),
            "own_naive_rerun": list(naive) if isinstance(naive, tuple) else naive}


def summarize_group(g, info, results, stopped, examples):
    planned = len(g["jobs"])
    compared = equal = errors = 0
    d_solved = d_nodes = d_path = 0
    cpu = 0.0
    shown = 0
    first_error = None
    for job in g["jobs"]:
        jid = job[0]
        r = results.get(jid)
        if r is None:
            continue
        cpu += r[3]
        if r[4] is not None:
            errors += 1
            if first_error is None:
                first_error = r[4]
            continue
        mine = tuple(r[1])
        stored = tuple(job[4])
        compared += 1
        if mine == stored:
            equal += 1
            continue
        if mine[0] != stored[0]:
            d_solved += 1
        if mine[1] != stored[1]:
            d_nodes += 1
        if mine[2] != stored[2]:
            d_path += 1
        if shown < MAX_EX_PER_CHECK and len(examples) < MAX_EXAMPLES:
            shown += 1
            examples.append(example(g["name"], info[jid], mine, r[2]))
    not_run = planned - compared - errors
    parts = []
    if compared == 0:
        parts.append("COMPARED 0 - NOT A PASS")
    parts.append("%s: planned %d, compared %d, equal %d, not run %d%s"
                 % (g["file"], planned, compared, equal, not_run,
                    (" (%s)" % stopped) if (not_run and stopped) else ""))
    if compared != equal:
        parts.append("differing in solved / nodes / path_len: %d / %d / %d"
                     % (d_solved, d_nodes, d_path))
    if errors:
        parts.append("job errors %d, first: %s" % (errors, first_error))
    parts.append("%.0f cpu-s" % cpu)
    check = {"name": g["name"], "compared": compared, "mismatches": compared - equal,
             "detail": "; ".join(parts)}
    return check, {"planned": planned, "compared": compared, "equal": equal,
                   "errors": errors}


def main(argv):
    if len(argv) < 4:
        print("usage: python3 %s <RESULTS_DIR> <DATASET> <OUT_JSON> [workers] [minutes]"
              % SCRIPT, file=sys.stderr)
        return 1
    t_start = time.time()
    results_dir, dataset_path, out_json = argv[1], argv[2], argv[3]
    workers = max(1, int(argv[4])) if len(argv) > 4 else 1
    minutes = float(argv[5]) if len(argv) > 5 else 30.0
    deadline = t_start + 60.0 * minutes

    dataset = load_dataset(dataset_path)
    checks = []
    skipped = []
    examples = []
    meta_checks = []
    state = {"groups": [], "info": []}

    # ---- self-test of this script's two searches against each other ----
    try:
        st_compared, st_bad, st_detail = self_test(dataset)
        for ex in st_bad:
            if len(examples) < MAX_EXAMPLES:
                examples.append(ex)
        checks.append({"name": "selftest_fast_vs_naive", "compared": st_compared,
                       "mismatches": len(st_bad),
                       "detail": ("COMPARED 0 - NOT A PASS; " if st_compared == 0 else "")
                       + st_detail})
    except Exception as exc:
        checks.append({"name": "selftest_fast_vs_naive", "compared": 0, "mismatches": 1,
                       "detail": "COMPARED 0 - NOT A PASS; self-test crashed (counted as one "
                                 "mismatch): %s: %s" % (type(exc).__name__, exc)})

    # ---- one sub-generator per expected file, drawn in a fixed order whether
    # ---- or not the file exists, all from random.Random(12345)
    master = random.Random(SEED)

    def sub():
        return random.Random(master.getrandbits(64))

    rng_ctrl_order = sub()
    rng_r3 = [sub() for _ in LENGTHS]
    rng_inv = [sub() for _ in LENGTHS]
    rng_rn = [(sub(), sub()) for _ in (4, 5)]
    rng_b10k = [sub() for _ in LENGTHS]
    rng_r3null = sub()

    def present(fname):
        return os.path.isfile(os.path.join(results_dir, fname))

    # ---- control (2 generators), all rows ----
    ctrl = None
    fname = STEM_1K + "_control.jsonl"
    if present(fname):
        try:
            ctrl = plan_control(state, os.path.join(results_dir, fname), fname, dataset,
                                rng_ctrl_order, rng_r3null)
        except Exception as exc:
            checks.append(fail_check("control_b1000", fname, exc))
    else:
        skipped.append(fname)

    # ---- rank 3, budget 1,000: length files, then _inv files ----
    fwd_words = {}
    for t, n in enumerate(LENGTHS):
        fname = "%s_L%d.npz" % (STEM_1K, n)
        if not present(fname):
            skipped.append(fname)
            continue
        try:
            fwd_words[n] = plan_rank3_file(
                state, os.path.join(results_dir, fname), fname, "rank3_b1000_L%d" % n,
                "rank3_b1000", 1000, N_R3, rng_r3[t], dataset, meta_checks)
        except Exception as exc:
            checks.append(fail_check("rank3_b1000_L%d" % n, fname, exc))
    inv_word_checks = []
    for t, n in enumerate(LENGTHS):
        fname = "%s_L%d_inv.npz" % (STEM_1K, n)
        if not present(fname):
            if n in INV_EXPECTED:
                skipped.append(fname)
            continue
        try:
            inv_words = plan_rank3_file(
                state, os.path.join(results_dir, fname), fname, "rank3_b1000_L%d_inv" % n,
                "rank3_b1000_inv", 1000, N_R3_INV, rng_inv[t], dataset, meta_checks)
        except Exception as exc:
            checks.append(fail_check("rank3_b1000_L%d_inv" % n, fname, exc))
            continue
        if n in fwd_words:
            fw = fwd_words[n]
            bad = 0
            if len(fw) != len(inv_words):
                bad = max(len(fw), len(inv_words))
            else:
                for a, b in zip(fw, inv_words):
                    if b != a[::-1].swapcase():
                        bad += 1
                        if bad <= 3 and len(examples) < MAX_EXAMPLES:
                            examples.append({
                                "check": "rank3_b1000_L%d_inv_words" % n,
                                "what": "word of the _inv file in the column of forward "
                                        "word %s" % a,
                                "stored": b, "mine": a[::-1].swapcase()})
            inv_word_checks.append({
                "name": "rank3_b1000_L%d_inv_words" % n,
                "compared": max(len(fw), len(inv_words)), "mismatches": bad,
                "detail": "words[k] of %s is the inverse of words[k] of the forward file "
                          "(%d forward, %d inverse words); the search uses the word as "
                          "stored in the _inv file" % (fname, len(fw), len(inv_words))})
    fwd_words = None

    # ---- rank 4 and rank 5 ----
    for t, rank in enumerate((4, 5)):
        fname = (RANKN_STEM % rank) + ".npz"
        if not present(fname):
            skipped.append(fname)
            continue
        try:
            plan_rankn_file(state, os.path.join(results_dir, fname), fname, rank,
                            rng_rn[t][0], rng_rn[t][1], dataset, meta_checks)
        except Exception as exc:
            checks.append(fail_check("rank%d_b1000" % rank, fname, exc))

    # ---- rank 3, budget 10,000 ----
    for t, n in enumerate(LENGTHS):
        fname = "%s_L%d.npz" % (STEM_10K, n)
        if not present(fname):
            skipped.append(fname)
            continue
        try:
            plan_rank3_file(
                state, os.path.join(results_dir, fname), fname, "rank3_b10000_L%d" % n,
                "rank3_b10000", 10000, N_B10K, rng_b10k[t], dataset, meta_checks)
        except Exception as exc:
            checks.append(fail_check("rank3_b10000_L%d" % n, fname, exc))

    groups = state["groups"]
    info = state["info"]
    jobs = interleave(groups)
    print("[%s] %d jobs in %d groups, %d workers, %.1f minutes, planning took %.1f s"
          % (SCRIPT, len(jobs), len(groups), workers, minutes, time.time() - t_start),
          file=sys.stderr, flush=True)

    # ---- run ----
    results = {}
    stopped = ""
    if jobs:
        ctx = mp.get_context("fork")
        pool = ctx.Pool(processes=workers)
        try:
            it = pool.imap_unordered(run_job, jobs, chunksize=1)
            last_note = time.time()
            while True:
                left = deadline - time.time()
                if left <= 0:
                    stopped = "time-out after %.1f minutes" % minutes
                    break
                try:
                    r = it.next(timeout=min(left, 2.0))
                except StopIteration:
                    break
                except mp.TimeoutError:
                    r = None
                except KeyboardInterrupt:
                    stopped = "interrupted"
                    break
                if r is not None:
                    results[r[0]] = r
                if time.time() - last_note > 30.0:
                    last_note = time.time()
                    print("[%s] %d / %d jobs after %.0f s"
                          % (SCRIPT, len(results), len(jobs), last_note - t_start),
                          file=sys.stderr, flush=True)
        finally:
            pool.terminate()
            pool.join()

    # ---- compare ----
    kinds = {}
    job_errors = 0
    for g in groups:
        check, st = summarize_group(g, info, results, stopped, examples)
        checks.append(check)
        job_errors += st["errors"]
        k = kinds.setdefault(g["kind"], {"planned": 0, "compared": 0, "equal": 0})
        k["planned"] += st["planned"]
        k["compared"] += st["compared"]
        k["equal"] += st["equal"]

    if ctrl is not None:
        # the same rank-2 runs against the stored n2_* copy
        cmp_n2 = eq_n2 = 0
        for jid, triple in ctrl["n2"].items():
            r = results.get(jid)
            if r is None or r[4] is not None:
                continue
            cmp_n2 += 1
            if tuple(r[1]) == tuple(triple):
                eq_n2 += 1
            elif len(examples) < MAX_EXAMPLES and cmp_n2 - eq_n2 <= MAX_EX_PER_CHECK:
                ex = example("control_b1000_n2_copy", info[jid], tuple(r[1]), r[2])
                ex["stored"] = list(triple)
                examples.append(ex)
        checks.append({"name": "control_b1000_n2_copy", "compared": cmp_n2,
                       "mismatches": cmp_n2 - eq_n2,
                       "detail": ("COMPARED 0 - NOT A PASS; " if cmp_n2 == 0 else "")
                       + "extra: my rank-2 search against the n2_* columns of the control "
                         "file; equal %d of %d" % (eq_n2, cmp_n2)})
        checks.append({"name": "control_b1000_relators_vs_dataset",
                       "compared": ctrl["str_cmp"], "mismatches": ctrl["str_bad"],
                       "detail": ("COMPARED 0 - NOT A PASS; " if ctrl["str_cmp"] == 0 else "")
                       + "r1, r2 strings of each control row equal dataset line pres_id "
                         "(the search always uses the dataset line); %d rows, %d distinct "
                         "pres_id" % (ctrl["rows"], ctrl["distinct"])})
        for ex in ctrl["str_ex"]:
            if len(examples) < MAX_EXAMPLES:
                examples.append(ex)
        meta_checks.append((STEM_1K + "_control.jsonl", ctrl["par_bad"] == 0,
                            "%d of %d rows have node_budget != 1000 or cap != %d"
                            % (ctrl["par_bad"], ctrl["par_cmp"], CAP)))
        # "all rows of the control file" must mean one row per dataset line
        meta_checks.append((STEM_1K + "_control.jsonl (row count)",
                            ctrl["rows"] == ctrl["distinct"] == len(dataset),
                            "%d rows, %d distinct pres_id, dataset has %d lines"
                            % (ctrl["rows"], ctrl["distinct"], len(dataset))))
    checks.extend(inv_word_checks)
    bad_meta = [m for m in meta_checks if not m[1]]
    checks.append({"name": "meta_params", "compared": len(meta_checks),
                   "mismatches": len(bad_meta),
                   "detail": ("COMPARED 0 - NOT A PASS; " if not meta_checks else "")
                   + "budget / cap / rank recorded in each file equal the file name's "
                     "(the search uses the recorded values), and the control file has "
                     "one row per dataset line"
                   + ("; BAD: " + " | ".join("%s: %s" % (m[0], m[2]) for m in bad_meta)
                      if bad_meta else "")})

    total_mismatches = sum(c["mismatches"] for c in checks)
    total_compared = sum(st["compared"] for st in kinds.values())
    out = {
        "script": SCRIPT,
        "checks": checks,
        "mismatches": total_mismatches,
        "skipped": skipped,
        "first_mismatches": examples[:MAX_EXAMPLES],
        "kinds": kinds,
        "searches_planned": len(jobs),
        "searches_compared": total_compared,
        "job_errors": job_errors,
        "stopped_early": stopped,
        "workers": workers,
        "minutes": minutes,
        "seconds": round(time.time() - t_start, 1),
        "seed": SEED,
    }
    with open(out_json, "w") as fh:
        json.dump(out, fh, indent=1)
        fh.write("\n")

    for c in checks:
        # one line per check: a job traceback inside the detail is flattened
        print("%s: compared %d, equal %d, mismatches %d | %s"
              % (c["name"], c["compared"], c["compared"] - c["mismatches"]
                 if c["compared"] >= c["mismatches"] else 0, c["mismatches"],
                 " / ".join(str(c["detail"]).split("\n"))))
    for name in sorted(kinds):
        k = kinds[name]
        print("KIND %s: compared %d / planned %d, equal %d%s"
              % (name, k["compared"], k["planned"], k["equal"],
                 "" if k["compared"] else "  (COMPARED 0 - NOT A PASS)"))
    for s in skipped:
        print("SKIPPED (file absent): %s" % s)
    print("TOTAL: %d searches compared of %d planned, %d mismatches over all checks, "
          "%d job errors%s"
          % (total_compared, len(jobs), total_mismatches, job_errors,
             ("; stopped early: " + stopped) if stopped else ""))
    if total_mismatches:
        return 3
    if job_errors or total_compared == 0:
        return 1
    return 0


if __name__ == "__main__":
    try:
        code = main(sys.argv)
    except SystemExit:
        raise
    except BaseException:
        traceback.print_exc()
        code = 1
    sys.exit(code)
