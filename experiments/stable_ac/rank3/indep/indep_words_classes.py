#!/usr/bin/env python3
"""Independent tester: word families, value sanity, control files, rank-4/5
combos, cross-budget prefix property and signed relabelings of MS640.

Usage:
    python3 indep_words_classes.py <RESULTS_DIR> <DATASET> <OUT_JSON> [workers] [minutes]

Self-contained (standard library + numpy). Imports nothing from the repo.
Exit code 0 = no mismatch, 3 = at least one mismatch, 1 = crash.
`workers` is accepted and ignored (nothing here searches); `minutes` is a
wall-clock box checked before every result file is opened.
"""

import ast
import collections
import hashlib
import itertools
import json
import math
import os
import sys
import time
import traceback

import numpy as np

SCRIPT = "indep_words_classes.py"
N_PRES = 640
BUDGETS = (1000, 10000)
LOW, HIGH = BUDGETS
CAP = 24
MAX_LEN = 10
MAX_INV_LEN = 6
RANKS = (4, 5)
ALPHABET = "xyXY"
LETTER = {1: "x", 2: "y", -1: "X", -2: "Y"}
EX_PER_CHECK = 20
EX_GLOBAL = 50
MISSING = "<missing key>"

CHECK_NAMES = (
    "0_dataset_format",
    "1_word_family",
    "2_value_sanity",
    "3_control_files",
    "4_rank45_npz",
    "5_cross_budget_prefix",
    "6_signed_relabelings_ms640",
    "7_duplicate_starts_in_row",
)


# --------------------------------------------------------------------------
# bookkeeping
# --------------------------------------------------------------------------

class Check:
    def __init__(self, name):
        self.name = name
        self.compared = 0
        self.mismatches = 0
        self.detail = {}
        self.examples = []
        self.errors = []
        self.summary = ""

    def bulk(self, compared, mismatches=0, examples=()):
        self.compared += int(compared)
        self.mismatches += int(mismatches)
        if mismatches:
            for ex in examples:
                if len(self.examples) >= EX_PER_CHECK:
                    break
                row = {"check": self.name}
                row.update(ex)
                self.examples.append(row)

    def item(self, ok, **example):
        good = bool(ok)
        self.bulk(1, 0 if good else 1, (example,))
        return good


class Report:
    def __init__(self):
        self.ck = collections.OrderedDict(
            (i, Check(nm)) for i, nm in enumerate(CHECK_NAMES))
        self.skipped = []
        self.crash = None
        self.timed_out = False
        self.dataset_sha = None

    def guard(self, cid, label, fn, *args):
        try:
            return fn(*args)
        except Exception:
            self.ck[cid].errors.append(
                {"where": label, "traceback": traceback.format_exc(limit=8)})
            return None


def clean(o):
    """Make an object strictly JSON-serialisable."""
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (set, frozenset)):
        return [clean(v) for v in sorted(o)]
    if isinstance(o, np.ndarray):
        return clean(o.tolist())
    if isinstance(o, np.generic):
        return clean(o.item())
    if isinstance(o, float) and (math.isnan(o) or math.isinf(o)):
        return None
    return o


def stem(budget):
    return "rank3_bf_ms640_b%d_cap%d" % (budget, CAP)


def rankn_name(rank):
    return "rankn_bf_ms640_b%d_cap%d_r%d.npz" % (LOW, CAP, rank)


# --------------------------------------------------------------------------
# words in the free group on x, y (own enumeration, nothing borrowed)
# --------------------------------------------------------------------------

def inv_word(w):
    return w[::-1].swapcase()


def is_reduced(w):
    return all(a != b.swapcase() for a, b in zip(w, w[1:]))


def valid_word(w, n):
    return len(w) == n and all(c in ALPHABET for c in w) and is_reduced(w)


def pair_key(w):
    """Canonical name of the unordered pair {w, w^-1}."""
    v = inv_word(w)
    return w if w <= v else v


def reduced_words(n):
    words = list(ALPHABET)
    for _ in range(n - 1):
        words = [w + c for w in words for c in ALPHABET if c != w[-1].swapcase()]
    return words


_PAIR_CACHE = {}


def expected_pair_keys(n):
    if n not in _PAIR_CACHE:
        allw = reduced_words(n)
        if len(allw) != 4 * 3 ** (n - 1) or len(set(allw)) != len(allw):
            raise RuntimeError("own enumeration of reduced words is wrong at n=%d" % n)
        keys = {pair_key(w) for w in allw}
        if len(keys) != 2 * 3 ** (n - 1):
            raise RuntimeError("own enumeration of pair classes is wrong at n=%d" % n)
        _PAIR_CACHE[n] = keys
    return _PAIR_CACHE[n]


def family_check(ck, words, n, where):
    """`words` (list of str) is claimed to be the word family of length n."""
    k_exp = 2 * 3 ** (n - 1)

    bad = [(i, w) for i, w in enumerate(words) if not valid_word(w, n)]
    ck.bulk(len(words), len(bad), [
        {"file": where,
         "what": "entry is not a freely reduced word of length %d over x,y,X,Y" % n,
         "index": i, "got": w} for i, w in bad[:3]])

    ck.item(len(words) == k_exp, file=where, what="number of words K = 2*3^(n-1)",
            expected=k_exp, got=len(words))

    first = {}
    dups = []
    for i, w in enumerate(words):
        if w in first:
            dups.append((first[w], i, w))
        else:
            first[w] = i
    muts = []
    for w, i in first.items():
        v = inv_word(w)
        if w < v and v in first:
            muts.append((i, first[v], w, v))
    ex = [{"file": where, "what": "two entries are equal",
           "index": [a, b], "got": w} for a, b, w in dups[:2]]
    ex += [{"file": where, "what": "two entries are mutually inverse",
            "index": [a, b], "got": [w, v]} for a, b, w, v in muts[:2]]
    ck.bulk(len(words), len(dups) + len(muts), ex)

    exp = expected_pair_keys(n)
    got = {pair_key(w) for w in words}
    missing = sorted(exp - got)
    extra = sorted(got - exp)
    ex = [{"file": where, "what": "pair {w, w^-1} missing from the file",
           "expected": w} for w in missing[:2]]
    ex += [{"file": where, "what": "pair {w, w^-1} not in the enumerated family",
            "got": w} for w in extra[:2]]
    ck.bulk(len(exp | got), len(missing) + len(extra), ex)

    return {"K": len(words), "K_expected": k_exp, "invalid_words": len(bad),
            "duplicate_entries": len(dups), "mutually_inverse_pairs": len(muts),
            "pairs_missing": len(missing), "pairs_extra": len(extra)}


# --------------------------------------------------------------------------
# file helpers
# --------------------------------------------------------------------------

def load_npz(path, names):
    out = {}
    with np.load(path, allow_pickle=False) as z:
        present = set(z.files)
        for nm in names:
            out[nm] = z[nm] if nm in present else None
        out["_members"] = sorted(present)
    return out


def as_str_list(arr):
    out = []
    for w in np.asarray(arr).ravel().tolist():
        out.append(w.decode("ascii", "replace") if isinstance(w, bytes) else str(w))
    return out


def parse_meta(arr):
    a = np.asarray(arr)
    s = a.item() if a.ndim == 0 else a.ravel()[0].item()
    if isinstance(s, bytes):
        s = s.decode("utf-8", "replace")
    return json.loads(str(s))


def load_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                rows.append(json.loads(ln))
    return rows


def parse_dataset(path):
    """Return (rows, problems, sha256, n_lines); rows[p] = (r1, r2) as strings."""
    with open(path, "rb") as f:
        raw = f.read()
    sha = hashlib.sha256(raw).hexdigest()
    lines = raw.decode("utf-8").splitlines()
    while lines and not lines[-1].strip():
        lines.pop()
    rows = []
    problems = []
    for p, ln in enumerate(lines):
        try:
            try:
                vals = json.loads(ln)
            except ValueError:
                vals = ast.literal_eval(ln.strip())
            vals = [int(v) for v in vals]
        except Exception as e:
            problems.append({"line": p, "what": "unparsable dataset line", "got": repr(e)})
            rows.append(("?", "?"))
            continue
        if len(vals) % 2:
            problems.append({"line": p, "what": "odd number of integers", "got": len(vals)})
        half = len(vals) // 2
        rel = []
        for which, part in (("r1", vals[:half]), ("r2", vals[half:])):
            m = len(part)
            while m and part[m - 1] == 0:
                m -= 1
            body = part[:m]
            if not body:
                problems.append({"line": p, "what": "%s is empty" % which})
            if any(v not in LETTER for v in body):
                problems.append({"line": p, "got": body,
                                 "what": "%s has a zero before its end or an unknown letter" % which})
            rel.append("".join(LETTER.get(v, "?") for v in body))
        rows.append((rel[0], rel[1]))
    return rows, problems, sha, len(lines)


# --------------------------------------------------------------------------
# check 2: value sanity of one nodes / path_len pair
# --------------------------------------------------------------------------

def value_sanity(c2, fname, nodes, path_len, budget, row_ids, col_labels):
    if nodes is None or path_len is None:
        c2.item(False, file=fname, what="'nodes' or 'path_len' missing")
        return
    if nodes.ndim != 2 or nodes.shape != path_len.shape:
        c2.item(False, file=fname, what="'nodes' and 'path_len' are not two equal 2-D shapes",
                got=[list(nodes.shape), list(path_len.shape)])
        return
    # native dtypes on purpose: no widened copy of a 640 x 39,366 matrix
    nd = nodes
    pl = path_len
    solved = pl >= 0
    unsolved = ~solved
    bad = solved & ((nd < 1) | (nd > budget) | (pl < 1))
    n_cells = int(solved.size)
    n_solved = int(np.count_nonzero(solved))
    n_bad = int(np.count_nonzero(bad))
    examples = []
    if n_bad:
        for i, k in np.argwhere(bad)[:3]:
            examples.append({
                "file": fname,
                "what": "solved cell violates 1 <= nodes <= budget and path_len >= 1",
                "pres_id": row_ids[i] if row_ids is not None and i < len(row_ids) else int(i),
                "word_or_index": col_labels[k] if col_labels is not None and k < len(col_labels) else int(k),
                "expected": "1 <= nodes <= %d, path_len >= 1" % budget,
                "got": {"nodes": int(nd[i, k]), "path_len": int(pl[i, k])}})
    # compared = solved cells: the implication says nothing about the others
    c2.bulk(n_solved, n_bad, examples)

    info = {"budget": budget, "cells": n_cells, "solved_cells": n_solved,
            "unsolved_cells": n_cells - n_solved, "violations": n_bad,
            "max_nodes_minus_path_len_solved": None,
            "min_nodes_minus_path_len_solved": None}
    if n_solved:
        diff = nd[solved].astype(np.int32) - pl[solved].astype(np.int32)
        info["max_nodes_minus_path_len_solved"] = int(diff.max())
        info["min_nodes_minus_path_len_solved"] = int(diff.min())
        info["max_path_len_solved"] = int(pl[solved].max())
    info["unsolved_with_nodes_lt_budget"] = int(np.count_nonzero(unsolved & (nd < budget)))
    info["unsolved_with_nodes_gt_budget"] = int(np.count_nonzero(unsolved & (nd > budget)))
    info["solved_with_nodes_eq_budget"] = int(np.count_nonzero(solved & (nd == budget)))
    info["solved_with_path_len_0"] = int(np.count_nonzero(pl == 0))
    info["path_len_below_minus_1"] = int(np.count_nonzero(pl < -1))
    if n_cells - n_solved:
        un = nd[unsolved]
        info["unsolved_nodes_min"] = int(un.min())
        info["unsolved_nodes_max"] = int(un.max())
    c2.detail.setdefault("files", {})[fname] = info

    ov = c2.detail.setdefault("overall", {
        "files": 0, "cells": 0, "solved_cells": 0, "violations": 0,
        "max_nodes_minus_path_len_solved": None,
        "min_nodes_minus_path_len_solved": None,
        "unsolved_with_nodes_lt_budget": 0, "unsolved_with_nodes_gt_budget": 0,
        "solved_with_nodes_eq_budget": 0, "path_len_below_minus_1": 0})
    ov["files"] += 1
    ov["cells"] += n_cells
    ov["solved_cells"] += n_solved
    ov["violations"] += n_bad
    for key in ("unsolved_with_nodes_lt_budget", "unsolved_with_nodes_gt_budget",
                "solved_with_nodes_eq_budget", "path_len_below_minus_1"):
        ov[key] += info[key]
    if n_solved:
        hi = info["max_nodes_minus_path_len_solved"]
        lo = info["min_nodes_minus_path_len_solved"]
        cur = ov["max_nodes_minus_path_len_solved"]
        ov["max_nodes_minus_path_len_solved"] = hi if cur is None else max(cur, hi)
        cur = ov["min_nodes_minus_path_len_solved"]
        ov["min_nodes_minus_path_len_solved"] = lo if cur is None else min(cur, lo)


# --------------------------------------------------------------------------
# checks 1 + 2 on one rank-3 npz
# --------------------------------------------------------------------------

def check_rank3_file(rep, path, fname, budget, n, side, plain_words):
    c1, c2 = rep.ck[1], rep.ck[2]
    d = load_npz(path, ("pres_ids", "words", "nodes", "path_len", "min_total", "meta"))
    info = {"members": d["_members"]}
    k_exp = 2 * 3 ** (n - 1)

    words = None
    if c1.item(d["words"] is not None, file=fname, what="array 'words' present"):
        words = as_str_list(d["words"])
        info.update(family_check(c1, words, n, fname))
        info["first_words"] = words[:6]
        if side == "inv":
            plain = plain_words.get((budget, n))
            if plain is None:
                rep.skipped.append(fname + ": words vs plain file (plain file absent or unreadable)")
            else:
                m = min(len(words), len(plain))
                badk = [k for k in range(m) if words[k] != inv_word(plain[k])]
                ex = [{"file": fname,
                       "what": "words[k] is not the inverse of words[k] of the plain file",
                       "index": k, "expected": inv_word(plain[k]), "got": words[k]}
                      for k in badk[:3]]
                if len(words) != len(plain):
                    ex.append({"file": fname, "what": "word count differs from the plain file",
                               "expected": len(plain), "got": len(words)})
                c1.bulk(max(len(words), len(plain)),
                        len(badk) + abs(len(words) - len(plain)), ex)
                info["inverse_of_plain_mismatches"] = len(badk) + abs(len(words) - len(plain))

    pres_list = None
    pres = d["pres_ids"]
    if c1.item(pres is not None, file=fname, what="array 'pres_ids' present"):
        pres = np.asarray(pres)
        info["pres_ids_dtype"] = str(pres.dtype)
        pres_list = [int(v) for v in pres.ravel().tolist()]
        if pres.shape == (N_PRES,):
            wrong = np.flatnonzero(pres.astype(np.int64) != np.arange(N_PRES))
            c1.bulk(N_PRES, wrong.size, [
                {"file": fname, "what": "pres_ids[i] != i", "index": int(i),
                 "expected": int(i), "got": int(pres[i])} for i in wrong[:3]])
        else:
            c1.bulk(N_PRES, N_PRES, [
                {"file": fname, "what": "shape of 'pres_ids'",
                 "expected": [N_PRES], "got": list(pres.shape)}])

    for nm in ("nodes", "path_len", "min_total"):
        a = d[nm]
        if a is None:
            if nm == "min_total":
                info["min_total"] = "absent (not counted)"
            else:
                c1.item(False, file=fname, what="array '%s' present" % nm)
            continue
        info[nm + "_dtype"] = str(a.dtype)
        c1.item(a.shape == (N_PRES, k_exp), file=fname, what="shape of '%s' is [640, K]" % nm,
                expected=[N_PRES, k_exp], got=list(a.shape))

    meta = None
    if c1.item(d["meta"] is not None, file=fname, what="array 'meta' present"):
        try:
            meta = parse_meta(d["meta"])
        except Exception as e:
            c1.item(False, file=fname, what="meta is not a JSON string", got=repr(e))
    if meta is not None:
        if c1.item(isinstance(meta, dict), file=fname, what="meta is a JSON object"):
            c1.item(meta.get("node_budget", MISSING) == budget, file=fname,
                    what="meta.node_budget equals the budget in the file name",
                    expected=budget, got=meta.get("node_budget", MISSING))
            for key, want in (("max_relator_length_cap", CAP), ("z_len", n),
                              ("n_words", k_exp), ("n_presentations", N_PRES)):
                if key in meta:
                    c1.item(meta[key] == want, file=fname,
                            what="meta.%s agrees with the file name / layout" % key,
                            expected=want, got=meta[key])
            info["meta_side"] = meta.get("side")
            info["meta_commit"] = meta.get("commit")
            if "dataset_sha256" in meta:
                info["meta_dataset_sha256_equals_given_dataset"] = (
                    meta["dataset_sha256"] == rep.dataset_sha)

    c1.detail.setdefault("files", {})[fname] = info
    value_sanity(c2, fname, d["nodes"], d["path_len"], budget, pres_list, words)
    return {"pres": pres_list, "words": words,
            "nodes": d["nodes"], "path_len": d["path_len"]}


# --------------------------------------------------------------------------
# check 5: prefix property between the two budgets
# --------------------------------------------------------------------------

def align(keys_lo, keys_hi):
    pos_lo = {}
    for i, k in enumerate(keys_lo):
        pos_lo.setdefault(k, i)
    pos_hi = {}
    for i, k in enumerate(keys_hi):
        pos_hi.setdefault(k, i)
    common = [k for k in pos_lo if k in pos_hi]
    only_lo = [k for k in pos_lo if k not in pos_hi]
    only_hi = [k for k in pos_hi if k not in pos_lo]
    idx_lo = np.array([pos_lo[k] for k in common], dtype=np.int64)
    idx_hi = np.array([pos_hi[k] for k in common], dtype=np.int64)
    return common, idx_lo, idx_hi, only_lo, only_hi


def _is_identity(idx, n):
    return idx.size == n and bool(np.array_equal(idx, np.arange(n)))


def _take(a, ri, ci):
    if not _is_identity(ri, a.shape[0]):
        a = a[ri, :]
    if not _is_identity(ci, a.shape[1]):
        a = a[:, ci]
    return a


def prefix_check(c5, label, lo, hi):
    for tag, part in (("b%d" % LOW, lo), ("b%d" % HIGH, hi)):
        for nm in ("nodes", "path_len", "words"):
            if part.get(nm) is None:
                c5.item(False, file=label,
                        what="cannot compare: '%s' missing in the %s file" % (nm, tag))
                return
        if part["nodes"].ndim != 2 or part["nodes"].shape != part["path_len"].shape:
            c5.item(False, file=label,
                    what="cannot compare: nodes / path_len shapes of the %s file" % tag)
            return
        if len(part["words"]) != part["nodes"].shape[1]:
            c5.item(False, file=label,
                    what="cannot compare: len(words) != number of columns in the %s file" % tag)
            return

    def row_keys(part):
        nrow = part["nodes"].shape[0]
        if part.get("pres") is not None and len(part["pres"]) == nrow:
            return list(part["pres"])
        return list(range(nrow))

    rows, ri_lo, ri_hi, rows_only_lo, rows_only_hi = align(row_keys(lo), row_keys(hi))
    cols, ci_lo, ci_hi, cols_only_lo, cols_only_hi = align(lo["words"], hi["words"])

    n_row_miss = len(rows_only_lo) + len(rows_only_hi)
    c5.bulk(len(rows) + n_row_miss, n_row_miss, [
        {"file": label, "what": "pres_id present in only one budget",
         "got": {"only_b%d" % LOW: rows_only_lo[:5], "only_b%d" % HIGH: rows_only_hi[:5]}}])
    n_col_miss = len(cols_only_lo) + len(cols_only_hi)
    c5.bulk(len(cols) + n_col_miss, n_col_miss, [
        {"file": label, "what": "word present in only one budget",
         "got": {"only_b%d" % LOW: cols_only_lo[:5], "only_b%d" % HIGH: cols_only_hi[:5]}}])

    info = {"rows_compared": len(rows), "words_compared": len(cols),
            "rows_only_in_one_budget": n_row_miss, "words_only_in_one_budget": n_col_miss,
            "same_word_order_in_both_files": list(lo["words"]) == list(hi["words"])}
    if not rows or not cols:
        info["cells"] = 0
        c5.detail.setdefault("pairs", {})[label] = info
        return

    n1 = _take(lo["nodes"], ri_lo, ci_lo)
    p1 = _take(lo["path_len"], ri_lo, ci_lo)
    n2 = _take(hi["nodes"], ri_hi, ci_hi)
    p2 = _take(hi["path_len"], ri_hi, ci_hi)
    s1 = p1 >= 0
    s2 = p2 >= 0
    want = s2 & (n2 <= LOW)
    bad_solved = s1 != want
    bad_vals = s1 & ((n1 != n2) | (p1 != p2))
    bad = bad_solved | bad_vals
    n_bad = int(np.count_nonzero(bad))
    examples = []
    if n_bad:
        for i, k in np.argwhere(bad)[:3]:
            examples.append({
                "file": label, "pres_id": rows[i], "word_or_index": cols[k],
                "what": "[solved at 1000] == [solved at 10000 and nodes <= 1000], "
                        "and equal nodes / path_len when solved at 1000",
                "expected": {"b%d (solved, nodes, path_len)" % HIGH:
                             [bool(s2[i, k]), int(n2[i, k]), int(p2[i, k])]},
                "got": {"b%d (solved, nodes, path_len)" % LOW:
                        [bool(s1[i, k]), int(n1[i, k]), int(p1[i, k])]}})
    c5.bulk(int(bad.size), n_bad, examples)

    boundary = s2 & (n2 == LOW)
    info.update({
        "cells": int(bad.size),
        "solved_at_%d" % LOW: int(np.count_nonzero(s1)),
        "solved_at_%d" % HIGH: int(np.count_nonzero(s2)),
        "solved_at_%d_within_%d_nodes" % (HIGH, LOW): int(np.count_nonzero(want)),
        "mismatch_cells": n_bad,
        "solved_flag_mismatch": int(np.count_nonzero(bad_solved)),
        "solved_low_but_not_predicted_by_high": int(np.count_nonzero(s1 & ~want)),
        "predicted_by_high_but_unsolved_low": int(np.count_nonzero(~s1 & want)),
        "values_differ_when_solved_low": int(np.count_nonzero(bad_vals)),
        "cells_solved_high_with_nodes_exactly_%d" % LOW: int(np.count_nonzero(boundary)),
        "solved_flag_mismatch_on_that_boundary": int(np.count_nonzero(bad_solved & boundary)),
    })
    c5.detail.setdefault("pairs", {})[label] = info


TRIPLES = (
    ("main", "solved", "nodes_explored", "path_length"),
    ("n2", "n2_solved", "n2_nodes", "n2_path_length"),
    ("null", "null_solved", "null_nodes", "null_path_length"),
)


def control_prefix(c5, ctrl_lo, ctrl_hi):
    info = {"pres_ids_compared": 0, "triples_compared": 0, "mismatches": 0,
            "boundary_rows_solved_high_with_nodes_exactly_%d" % LOW: 0}
    before = c5.mismatches
    for pid in range(N_PRES):
        a = ctrl_lo.get(pid)
        b = ctrl_hi.get(pid)
        if a is None or b is None:
            c5.item(False, file="control", pres_id=pid,
                    what="pres_id present in only one control file")
            continue
        info["pres_ids_compared"] += 1
        c5.item((a.get("r1"), a.get("r2")) == (b.get("r1"), b.get("r2")),
                file="control", pres_id=pid, what="r1/r2 identical in both control files",
                expected=[b.get("r1"), b.get("r2")], got=[a.get("r1"), a.get("r2")])
        for tag, ks, kn, kp in TRIPLES:
            if any(k not in a for k in (ks, kn, kp)) or any(k not in b for k in (ks, kn, kp)):
                c5.item(False, file="control", pres_id=pid,
                        what="%s triple: a key is missing" % tag)
                continue
            s1 = bool(a[ks])
            s2 = bool(b[ks])
            nb = b[kn]
            within = isinstance(nb, (int, float)) and nb <= LOW
            want = s2 and within
            if tag == "main" and s2 and nb == LOW:
                info["boundary_rows_solved_high_with_nodes_exactly_%d" % LOW] += 1
            ok = (s1 == want) and ((not s1) or (a[kn] == b[kn] and a[kp] == b[kp]))
            info["triples_compared"] += 1
            c5.item(ok, file="control", pres_id=pid, word_or_index=tag,
                    what="[solved at 1000] == [solved at 10000 and nodes <= 1000], "
                         "and equal nodes / path_length when solved at 1000",
                    expected={"b%d" % HIGH: [b[ks], b[kn], b[kp]]},
                    got={"b%d" % LOW: [a[ks], a[kn], a[kp]]})
    info["mismatches"] = c5.mismatches - before
    c5.detail["control"] = info


# --------------------------------------------------------------------------
# check 3: control file
# --------------------------------------------------------------------------

def _is_id(pid):
    return isinstance(pid, int) and not isinstance(pid, bool) and 0 <= pid < N_PRES


def check_control(c3, path, fname, budget, dataset_rows):
    rows = load_jsonl(path)
    c3.item(len(rows) == N_PRES, file=fname, what="number of rows",
            expected=N_PRES, got=len(rows))

    counts = collections.Counter()
    for r in rows:
        pid = r.get("pres_id", MISSING)
        counts[pid if _is_id(pid) else "stray:" + repr(pid)] += 1
    bad_ids = [p for p in range(N_PRES) if counts.get(p, 0) != 1]
    stray = [k for k in counts if not _is_id(k)]
    ex = [{"file": fname, "what": "pres_id must appear exactly once",
           "pres_id": p, "expected": 1, "got": counts.get(p, 0)} for p in bad_ids[:3]]
    ex += [{"file": fname, "what": "pres_id outside 0..639", "got": k} for k in stray[:2]]
    c3.bulk(N_PRES + len(stray), len(bad_ids) + len(stray), ex)

    by_id = {}
    n_solved = 0
    n_null_path = 0
    unsolved_nodes = []
    sane = 0
    for r in rows:
        pid = r.get("pres_id", MISSING)
        if _is_id(pid):
            by_id.setdefault(pid, r)
        c3.item(r.get("node_budget", MISSING) == budget, file=fname, pres_id=pid,
                what="node_budget equals the budget in the file name",
                expected=budget, got=r.get("node_budget", MISSING))
        if _is_id(pid) and pid < len(dataset_rows):
            e1, e2 = dataset_rows[pid]
            c3.item(r.get("r1", MISSING) == e1, file=fname, pres_id=pid,
                    what="r1 equals the dataset line", expected=e1, got=r.get("r1", MISSING))
            c3.item(r.get("r2", MISSING) == e2, file=fname, pres_id=pid,
                    what="r2 equals the dataset line", expected=e2, got=r.get("r2", MISSING))
        else:
            c3.bulk(2, 2, [{"file": fname, "pres_id": pid,
                            "what": "r1/r2 cannot be compared: no dataset line for this pres_id"}])
        main = tuple(r.get(k, MISSING) for k in TRIPLES[0][1:])
        n2 = tuple(r.get(k, MISSING) for k in TRIPLES[1][1:])
        nul = tuple(r.get(k, MISSING) for k in TRIPLES[2][1:])
        ok = (MISSING not in main + n2 + nul) and main == n2 and main == nul
        c3.item(ok, file=fname, pres_id=pid,
                what="(solved, nodes_explored, path_length) == n2_* == null_*",
                expected=list(main), got={"n2": list(n2), "null": list(nul)})
        if r.get("solved") is True:
            n_solved += 1
            nd, pl = r.get("nodes_explored"), r.get("path_length")
            if isinstance(nd, int) and isinstance(pl, int) and 1 <= nd <= budget and pl >= 0:
                sane += 1
        else:
            unsolved_nodes.append(r.get("nodes_explored"))
        if r.get("path_length", MISSING) is None:
            n_null_path += 1
    un = [v for v in unsolved_nodes if isinstance(v, int)]
    c3.detail.setdefault("files", {})[fname] = {
        "rows": len(rows), "solved": n_solved, "not_solved": len(rows) - n_solved,
        "rows_with_path_length_null": n_null_path,
        "solved_rows_with_1<=nodes<=budget_and_path_length>=0 (reported, not judged)": sane,
        "unsolved_nodes_min": min(un) if un else None,
        "unsolved_nodes_max": max(un) if un else None,
        "rows_in_pres_id_order": [r.get("pres_id") for r in rows] == list(range(len(rows))),
    }
    return by_id


# --------------------------------------------------------------------------
# check 4: rank 4 / 5 npz
# --------------------------------------------------------------------------

def check_rankn_file(rep, path, fname, rank, ctrl_low):
    c4, c2 = rep.ck[4], rep.ck[2]
    d = load_npz(path, ("pres_ids", "meta", "combos", "nodes", "path_len", "base", "null"))
    info = {"members": d["_members"]}
    k = rank - 2

    meta = None
    if c4.item(d["meta"] is not None, file=fname, what="array 'meta' present"):
        try:
            meta = parse_meta(d["meta"])
        except Exception as e:
            c4.item(False, file=fname, what="meta is not a JSON string", got=repr(e))
    words = None
    if meta is not None and c4.item(isinstance(meta, dict), file=fname,
                                    what="meta is a JSON object"):
        c4.item(meta.get("rank", MISSING) == rank, file=fname, what="meta.rank",
                expected=rank, got=meta.get("rank", MISSING))
        c4.item(meta.get("extra_generators", MISSING) == k, file=fname,
                what="meta.extra_generators == rank - 2",
                expected=k, got=meta.get("extra_generators", MISSING))
        c4.item(meta.get("node_budget", MISSING) == LOW, file=fname, what="meta.node_budget",
                expected=LOW, got=meta.get("node_budget", MISSING))
        if "max_relator_length_cap" in meta:
            c4.item(meta["max_relator_length_cap"] == CAP, file=fname,
                    what="meta.max_relator_length_cap", expected=CAP,
                    got=meta["max_relator_length_cap"])
        m = meta.get("max_word_len")
        mw = meta.get("words")
        usable = (isinstance(m, int) and not isinstance(m, bool) and 1 <= m <= 12
                  and isinstance(mw, list))
        if c4.item(usable, file=fname,
                   what="meta.max_word_len is an int in 1..12 and meta.words is a list",
                   got=[repr(m), type(mw).__name__]):
            words = [str(w) for w in mw]
            w_exp = 3 ** m - 1
            c4.item(len(words) == w_exp, file=fname,
                    what="len(meta.words) == sum of 2*3^(n-1) for n = 1..max_word_len",
                    expected=w_exp, got=len(words))
            off = 0
            fam = {}
            for n in range(1, m + 1):
                kn = 2 * 3 ** (n - 1)
                fam[str(n)] = family_check(
                    c4, words[off:off + kn], n,
                    "%s:meta.words[%d:%d] (length %d)" % (fname, off, off + kn, n))
                off += kn
            info["max_word_len"] = m
            info["words_total"] = len(words)
            info["families"] = fam
            info["word_lengths_in_file_order"] = [len(w) for w in words][:40]

    combos = d["combos"]
    c_actual = None
    if c4.item(combos is not None and combos.ndim == 2, file=fname,
               what="'combos' present and 2-D"):
        c_actual = int(combos.shape[0])
        info["combos_shape"] = list(combos.shape)
        k_ok = c4.item(combos.shape[1] == k, file=fname, what="combos.shape[1] == rank - 2",
                       expected=k, got=int(combos.shape[1]))
        if words is not None:
            n_words = len(words)
            c_exp = math.comb(n_words + k - 1, k)
            c4.item(c_actual == c_exp, file=fname, what="number of combos C = comb(W+k-1, k)",
                    expected=c_exp, got=c_actual)
            cb = combos.astype(np.int64)
            outside = (cb < 0) | (cb >= n_words)
            n_out = int(np.count_nonzero(outside))
            c4.bulk(int(cb.size), n_out, [
                {"file": fname, "what": "combo entry outside [0, W)", "index": int(i),
                 "got": cb[i].tolist()} for i in np.flatnonzero(outside.any(axis=1))[:3]])
            srt = np.sort(cb, axis=1)
            rows_sorted = [tuple(r) for r in srt.tolist()]
            got = collections.Counter(rows_sorted)
            dup_rows = [t for t, v in got.items() if v > 1]
            c4.bulk(c_actual, sum(v - 1 for v in got.values()), [
                {"file": fname, "what": "multiset appears more than once in combos",
                 "got": list(t), "expected": 1} for t in dup_rows[:3]])
            if k_ok and c_exp <= 3000000:
                exp = set(itertools.combinations_with_replacement(range(n_words), k))
                gset = set(got)
                missing = sorted(exp - gset)
                extra = sorted(gset - exp)
                ex = [{"file": fname, "what": "multiset missing from combos",
                       "expected": list(t)} for t in missing[:2]]
                ex += [{"file": fname, "what": "combos row is not a multiset of word indices",
                        "got": list(t)} for t in extra[:2]]
                c4.bulk(len(exp | gset), len(missing) + len(extra), ex)
                info["combos_missing"] = len(missing)
                info["combos_extra"] = len(extra)
            else:
                info["combos_set_enumeration"] = "not enumerated (wrong k or too many)"
            raw_rows = [tuple(r) for r in cb.tolist()]
            info["combo_rows_each_sorted"] = raw_rows == rows_sorted
            info["combo_rows_in_lexicographic_order"] = raw_rows == sorted(raw_rows)
            info["combos_duplicate_multisets"] = sum(v - 1 for v in got.values())

    for nm in ("nodes", "path_len"):
        a = d[nm]
        if c4.item(a is not None, file=fname, what="array '%s' present" % nm) and c_actual is not None:
            c4.item(a.shape == (N_PRES, c_actual), file=fname,
                    what="shape of '%s' is [640, C]" % nm,
                    expected=[N_PRES, c_actual], got=list(a.shape))

    pres_list = None
    if c4.item(d["pres_ids"] is not None, file=fname, what="array 'pres_ids' present"):
        pres_list = [int(v) for v in np.asarray(d["pres_ids"]).ravel().tolist()]
        info["pres_ids_dtype"] = str(d["pres_ids"].dtype)
        info["pres_ids_in_order"] = pres_list == list(range(N_PRES))
        c4.item(sorted(pres_list) == list(range(N_PRES)), file=fname,
                what="pres_ids holds 0..639 once each", got=pres_list[:8])

    base, null = d["base"], d["null"]
    ok_base = c4.item(base is not None and base.shape == (N_PRES, 3), file=fname,
                      what="'base' present with shape [640, 3]",
                      got=None if base is None else list(base.shape))
    ok_null = c4.item(null is not None and null.shape == (N_PRES, 3), file=fname,
                      what="'null' present with shape [640, 3]",
                      got=None if null is None else list(null.shape))
    have_ids = pres_list is not None and len(pres_list) == N_PRES
    if ok_base and ok_null:
        differ = np.flatnonzero(np.any(base.astype(np.int64) != null.astype(np.int64), axis=1))
        c4.bulk(N_PRES, differ.size, [
            {"file": fname, "what": "null[i] != base[i]", "index": int(i),
             "pres_id": pres_list[i] if have_ids else int(i),
             "expected": base[i].tolist(), "got": null[i].tolist()} for i in differ[:3]])
        info["null_rows_differing_from_base"] = int(differ.size)
    if ok_base and have_ids:
        if ctrl_low is None:
            rep.skipped.append(fname + ": base vs budget-%d control (control file absent or unreadable)" % LOW)
        else:
            bad = []
            n_norm = 0
            for i in range(N_PRES):
                row = ctrl_low.get(pres_list[i])
                got_row = [int(v) for v in base[i].tolist()]
                if row is None:
                    exp_row = None
                else:
                    pl = row.get("path_length", MISSING)
                    if pl is None:
                        pl = -1
                        n_norm += 1
                    exp_row = [int(bool(row.get("solved"))), row.get("nodes_explored", MISSING), pl]
                if exp_row != got_row:
                    bad.append((i, exp_row, got_row))
            c4.bulk(N_PRES, len(bad), [
                {"file": fname, "what": "base[i] != budget-%d control row of pres_ids[i]" % LOW,
                 "index": i, "pres_id": pres_list[i], "expected": e, "got": g}
                for i, e, g in bad[:3]])
            info["base_rows_differing_from_control"] = len(bad)
            info["control_rows_with_path_length_null_read_as_-1"] = n_norm
        info["base_solved"] = int(np.count_nonzero(base[:, 0] != 0))

    c4.detail.setdefault("files", {})[fname] = info
    value_sanity(c2, fname, d["nodes"], d["path_len"], LOW, pres_list, None)


# --------------------------------------------------------------------------
# checks 6 + 7: signed relabelings of MS640
# --------------------------------------------------------------------------

def make_relabelings():
    out = []
    for a, b in (("x", "y"), ("y", "x")):
        for flip_a in (False, True):
            for flip_b in (False, True):
                ia = a.upper() if flip_a else a
                ib = b.upper() if flip_b else b
                table = {"x": ia, "X": ia.swapcase(), "y": ib, "Y": ib.swapcase()}
                out.append(("x->%s,y->%s" % (ia, ib), str.maketrans(table)))
    if "xyXY".translate(out[0][1]) != "xyXY":
        raise RuntimeError("first relabeling is not the identity")
    if len({"xyXY".translate(t) for _, t in out}) != 8:
        raise RuntimeError("the 8 relabelings are not distinct")
    return out


def canon_relator(r):
    """Least of all cyclic rotations of r and of r^-1 (no free reduction)."""
    if not r:
        return r
    n = len(r)
    best = None
    for s in (r, inv_word(r)):
        dbl = s + s
        for i in range(n):
            c = dbl[i:i + n]
            if best is None or c < best:
                best = c
    return best


def pres_key(r1, r2):
    a, b = canon_relator(r1), canon_relator(r2)
    return (a, b) if a <= b else (b, a)


def stage_relabel(rep, rows):
    c6 = rep.ck[6]
    relab = make_relabelings()
    names = [nm for nm, _ in relab]
    nrel = len(relab)
    keys = [[pres_key(r1.translate(t), r2.translate(t)) for _, t in relab]
            for r1, r2 in rows]

    classes = collections.OrderedDict()
    for p, ks in enumerate(keys):
        classes.setdefault(min(ks), []).append(p)
    same = collections.OrderedDict()
    for p, ks in enumerate(keys):
        same.setdefault(ks[0], []).append(p)
    raw = collections.OrderedDict()
    for p, r in enumerate(rows):
        raw.setdefault(r, []).append(p)
    stab = [[j for j in range(1, nrel) if keys[p][j] == keys[p][0]]
            for p in range(len(rows))]

    partition = []
    complete = 0
    for members in classes.values():
        p0 = members[0]
        maps = {}
        for q in members:
            maps[str(q)] = [names[j] for j in range(nrel) if keys[p0][j] == keys[q][0]]
        present = len({keys[q][0] for q in members})
        abstract = len(set(keys[p0]))
        if present == abstract:
            complete += 1
        partition.append({"rows": members, "size": len(members),
                          "distinct_presentations_present": present,
                          "orbit_size_under_the_8_relabelings": abstract,
                          "relabelings_taking_first_row_to_row": maps})

    size_hist = collections.Counter(len(v) for v in classes.values())
    stab_hist = collections.Counter(1 + len(s) for s in stab)
    dup_groups = [v for v in same.values() if len(v) > 1]
    raw_groups = [v for v in raw.values() if len(v) > 1]
    fixed = {str(p): [names[j] for j in stab[p]] for p in range(len(rows)) if stab[p]}
    fixed_by = collections.Counter()
    for s in stab:
        for j in s:
            fixed_by[names[j]] += 1

    c6.bulk(len(rows), 0)
    c6.detail.update({
        "note": "report only, no expected value",
        "relabelings": names,
        "rows": len(rows),
        "number_of_classes": len(classes),
        "class_size_histogram (rows per class, duplicates included)":
            {str(k): size_hist[k] for k in sorted(size_hist)},
        "classes_holding_their_whole_orbit": complete,
        "distinct_presentations_up_to_order_rotation_inversion": len(same),
        "duplicate_groups (same presentation, identity relabeling)": dup_groups,
        "rows_that_duplicate_another_row": sorted(p for g in dup_groups for p in g),
        "groups_of_identical_dataset_lines": raw_groups,
        "stabiliser_order_histogram": {str(k): stab_hist[k] for k in sorted(stab_hist)},
        "rows_fixed_by_a_non_identity_relabeling": len(fixed),
        "fixed_rows": fixed,
        "rows_fixed_per_relabeling": {nm: fixed_by.get(nm, 0) for nm in names[1:]},
        "partition": partition,
    })
    c6.summary = "classes=%d sizes=%s duplicate_rows=%d fixed_rows=%d" % (
        len(classes), {k: size_hist[k] for k in sorted(size_hist)},
        sum(len(g) for g in dup_groups), len(fixed))
    return {"relab": relab, "names": names, "stab": stab,
            "classes": list(classes.values())}


def start_duplicates(tables):
    """`tables` = the non-identity relabelings fixing a row (with the identity
    they form a group). Per length: words of the family moved to another pair
    class by at least one of them, and the number of orbits of pair classes."""
    per_len = []
    for n in range(1, MAX_LEN + 1):
        keys = expected_pair_keys(n)
        moved_any = 0
        moved_by = [0] * len(tables)
        orbits = 0
        for w in keys:
            lowest = True
            moved = False
            for j, t in enumerate(tables):
                v = pair_key(w.translate(t))
                if v != w:
                    moved_by[j] += 1
                    moved = True
                    if v < w:
                        lowest = False
            if moved:
                moved_any += 1
            if lowest:
                orbits += 1
        per_len.append({"n": n, "words": len(keys), "duplicate_words": moved_any,
                        "moved_by": moved_by, "distinct_starts": orbits})
    return per_len


def stage_dup_starts(rep, rows, rl):
    c7 = rep.ck[7]
    relab, names, stab = rl["relab"], rl["names"], rl["stab"]
    words_per_row = sum(2 * 3 ** (n - 1) for n in range(1, MAX_LEN + 1))
    cache = {}
    rows_of = collections.OrderedDict()
    per_row = {}
    total_dup = 0
    total_redundant = 0
    for p in range(len(rows)):
        if not stab[p]:
            continue
        h = tuple(stab[p])
        if h not in cache:
            cache[h] = start_duplicates([relab[j][1] for j in h])
        rows_of.setdefault(h, []).append(p)
        per_len = cache[h]
        dup = sum(e["duplicate_words"] for e in per_len)
        distinct = sum(e["distinct_starts"] for e in per_len)
        per_row[str(p)] = {
            "fixed_by": [names[j] for j in h],
            "duplicate_words": dup,
            "distinct_starts": distinct,
            "redundant_starts": words_per_row - distinct,
            "moved_by_relabeling": {names[j]: sum(e["moved_by"][i] for e in per_len)
                                    for i, j in enumerate(h)},
        }
        total_dup += dup
        total_redundant += words_per_row - distinct

    by_stab = []
    for h, members in rows_of.items():
        by_stab.append({
            "fixed_by": [names[j] for j in h], "rows": members,
            "per_length": [{"n": e["n"], "words": e["words"],
                            "duplicate_words": e["duplicate_words"],
                            "distinct_starts": e["distinct_starts"],
                            "moved_by_relabeling": {names[j]: e["moved_by"][i]
                                                    for i, j in enumerate(h)}}
                           for e in cache[h]]})

    distinct_dataset = 0
    for members in rl["classes"]:
        h = tuple(stab[members[0]])
        distinct_dataset += (sum(e["distinct_starts"] for e in cache[h])
                             if h else words_per_row)

    total_starts = len(rows) * words_per_row
    c7.bulk(len(rows), 0)
    c7.detail.update({
        "note": "report only, no expected value",
        "lengths": [1, MAX_LEN],
        "words_per_row (sum over n of 2*3^(n-1))": words_per_row,
        "total_starts (rows * words_per_row)": total_starts,
        "rows_fixed_by_a_non_identity_relabeling": len(per_row),
        "duplicate_starts_total (words whose image under a fixing relabeling is in another pair class)": total_dup,
        "redundant_starts_total (duplicate words minus one representative per orbit)": total_redundant,
        "per_row": per_row,
        "by_stabiliser": by_stab,
        "extra_distinct_starts_whole_dataset_up_to_relabeling (one row per class, one word per orbit)": distinct_dataset,
    })
    c7.summary = "fixed_rows=%d duplicate_starts=%d of total_starts=%d" % (
        len(per_row), total_dup, total_starts)


# --------------------------------------------------------------------------
# stages
# --------------------------------------------------------------------------

def stage_controls(rep, results_dir, dataset_rows):
    ctrl = {}
    for budget in BUDGETS:
        fname = stem(budget) + "_control.jsonl"
        path = os.path.join(results_dir, fname)
        if not os.path.isfile(path):
            rep.skipped.append(fname + " (absent)")
            continue
        res = rep.guard(3, fname, check_control, rep.ck[3], path, fname, budget, dataset_rows)
        if res is not None:
            ctrl[budget] = res
    if LOW in ctrl and HIGH in ctrl:
        rep.guard(5, "control", control_prefix, rep.ck[5], ctrl[LOW], ctrl[HIGH])
    else:
        rep.ck[5].detail["control"] = "not compared: a control file is absent or unreadable"
    return ctrl


def stage_rank3(rep, results_dir, deadline):
    plain_words = {}
    for n in range(1, MAX_LEN + 1):
        for side in ("fwd", "inv"):
            suffix = "_inv" if side == "inv" else ""
            loaded = {}
            for budget in BUDGETS:
                fname = "%s_L%d%s.npz" % (stem(budget), n, suffix)
                path = os.path.join(results_dir, fname)
                if not os.path.isfile(path):
                    if side == "fwd" or n <= MAX_INV_LEN:
                        rep.skipped.append(fname + " (absent)")
                    continue
                if time.time() > deadline:
                    rep.timed_out = True
                    rep.skipped.append(fname + " (time limit reached before this file)")
                    continue
                res = rep.guard(1, fname, check_rank3_file, rep, path, fname,
                                budget, n, side, plain_words)
                if res is not None:
                    loaded[budget] = res
                    if side == "fwd" and res["words"] is not None:
                        plain_words[(budget, n)] = res["words"]
            if LOW in loaded and HIGH in loaded:
                label = "L%d%s" % (n, suffix)
                rep.guard(5, label, prefix_check, rep.ck[5], label, loaded[LOW], loaded[HIGH])
            loaded = None
            res = None


def stage_rankn(rep, results_dir, ctrl_low, deadline):
    for rank in RANKS:
        fname = rankn_name(rank)
        path = os.path.join(results_dir, fname)
        if not os.path.isfile(path):
            rep.skipped.append(fname + " (absent)")
            continue
        if time.time() > deadline:
            rep.timed_out = True
            rep.skipped.append(fname + " (time limit reached before this file)")
            continue
        rep.guard(4, fname, check_rankn_file, rep, path, fname, rank, ctrl_low)


def run_all(rep, results_dir, dataset_path, deadline):
    if not os.path.isdir(results_dir):
        raise FileNotFoundError("RESULTS_DIR is not a directory: %s" % results_dir)
    rows, problems, sha, n_lines = parse_dataset(dataset_path)
    rep.dataset_sha = sha

    c0 = rep.ck[0]
    dname = os.path.basename(dataset_path)
    c0.item(n_lines == N_PRES, file=dname, what="number of dataset lines",
            expected=N_PRES, got=n_lines)
    bad_lines = sorted({pr["line"] for pr in problems})
    c0.bulk(n_lines, len(bad_lines), [dict(pr, file=dname) for pr in problems[:5]])
    rels = [r for pair in rows for r in pair]
    not_reduced = [p for p, pair in enumerate(rows) if not all(is_reduced(r) for r in pair)]
    not_cyc = [p for p, pair in enumerate(rows)
               if any(len(r) >= 2 and r[0] == r[-1].swapcase() for r in pair)]
    c0.detail.update({
        "sha256": sha, "lines": n_lines, "lines_with_a_format_problem": bad_lines[:50],
        "max_relator_length": max((len(r) for r in rels), default=0),
        "min_relator_length": min((len(r) for r in rels), default=0),
        "rows_with_a_relator_not_freely_reduced (reported)": not_reduced,
        "rows_with_a_relator_not_cyclically_reduced (reported)": not_cyc,
    })

    rl = rep.guard(6, "signed relabelings", stage_relabel, rep, rows)
    if rl is not None:
        rep.guard(7, "duplicate starts", stage_dup_starts, rep, rows, rl)
    ctrl = stage_controls(rep, results_dir, rows)
    stage_rank3(rep, results_dir, deadline)
    stage_rankn(rep, results_dir, ctrl.get(LOW), deadline)

    ov = rep.ck[2].detail.get("overall")
    if ov:
        rep.ck[2].summary = "nodes-path_len over solved: max=%s min=%s; unsolved with nodes<budget=%d" % (
            ov["max_nodes_minus_path_len_solved"], ov["min_nodes_minus_path_len_solved"],
            ov["unsolved_with_nodes_lt_budget"])
    pairs = rep.ck[5].detail.get("pairs", {})
    rep.ck[5].summary = "npz pairs compared: %s; control: %s" % (
        ",".join(pairs) if pairs else "none",
        "yes" if isinstance(rep.ck[5].detail.get("control"), dict) else "no")
    files1 = rep.ck[1].detail.get("files", {})
    rep.ck[1].summary = "files checked: %d" % len(files1)


def finish(rep, out_json, t0, args):
    checks = []
    total = 0
    lines = []
    crashed = rep.crash is not None
    for ck in rep.ck.values():
        det = dict(ck.detail)
        det["examples"] = ck.examples
        if ck.errors:
            det["errors"] = ck.errors
            crashed = True
        if ck.errors:
            status = "ERROR (exception inside this check, see detail.errors)"
        elif ck.mismatches:
            status = "MISMATCH"
        elif ck.compared == 0:
            status = "NOTHING COMPARED (not a pass)"
        else:
            status = "ok"
        det["status"] = status
        checks.append({"name": ck.name, "compared": ck.compared,
                       "mismatches": ck.mismatches, "detail": det})
        total += ck.mismatches
        lines.append("%-28s compared=%d mismatches=%d  %s%s" % (
            ck.name, ck.compared, ck.mismatches, status,
            ("  [" + ck.summary + "]") if ck.summary else ""))

    first = []
    for group in itertools.zip_longest(*[ck.examples for ck in rep.ck.values()]):
        for ex in group:
            if ex is not None and len(first) < EX_GLOBAL:
                first.append(ex)

    doc = {
        "script": SCRIPT,
        "checks": checks,
        "mismatches": total,
        "skipped": rep.skipped,
        "first_mismatches": first,
        "crash": rep.crash,
        "timed_out": rep.timed_out,
        "seconds": round(time.time() - t0, 2),
        "args": args,
    }
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(clean(doc), f, indent=1)
        f.write("\n")

    for ln in lines:
        print(ln)
    print("total mismatches=%d skipped=%d%s%s" % (
        total, len(rep.skipped),
        " TIME LIMIT REACHED" if rep.timed_out else "",
        " CRASH" if crashed else ""))
    if rep.crash:
        print(rep.crash, file=sys.stderr)
    for ck in rep.ck.values():
        for err in ck.errors:
            print("%s: %s\n%s" % (ck.name, err["where"], err["traceback"]), file=sys.stderr)
    if crashed:
        return 1
    return 3 if total else 0


def main(argv):
    if len(argv) < 4:
        print("usage: python3 %s <RESULTS_DIR> <DATASET> <OUT_JSON> [workers] [minutes]" % SCRIPT,
              file=sys.stderr)
        return 1
    t0 = time.time()
    try:
        results_dir, dataset_path, out_json = argv[1], argv[2], argv[3]
        workers = int(argv[4]) if len(argv) > 4 else 1
        minutes = float(argv[5]) if len(argv) > 5 else 30.0
    except Exception:
        traceback.print_exc()
        return 1
    rep = Report()
    try:
        run_all(rep, results_dir, dataset_path, t0 + 60.0 * minutes)
    except Exception:
        rep.crash = traceback.format_exc()
    try:
        return finish(rep, out_json, t0, {
            "results_dir": results_dir, "dataset": dataset_path,
            "workers (ignored)": workers, "minutes": minutes})
    except Exception:
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
