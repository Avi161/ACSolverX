#!/usr/bin/env python3
"""Independent recomputation of the relabeling-class view.

Recomputes, from the raw result arrays and the dataset only, every number in

    rank3_bf_ms640_b<B>_cap24_class_view.json          (B = 1000, 10000)
    rankn_bf_ms640_b1000_cap24_r<R>_class_view.json    (R = 4, 5)

and compares (integers equal, floats within 1e-9).

Usage (from anywhere, nothing is imported from the repository):

    python3 -I -u indep_class_view.py <RESULTS_DIR> <DATASET> <OUT_JSON> [workers] [minutes]

Exit code: 0 no mismatch, 3 some mismatch (or a comparison check that
compared nothing), 1 crash.  Standard library and numpy only.
"""

import ast
import json
import math
import os
import re
import sys
import time
import traceback
from collections import Counter

import numpy as np

SCRIPT = "indep_class_view.py"
TOL = 1e-9
NOISE_THRESHOLD = 0.17
N_PRES = 640
MAX_EXAMPLES = 50
BUDGETS = (1000, 10000)
RANKS = (4, 5)
DEFAULT_LENGTHS = tuple(range(1, 11))
BIG = int(np.iinfo(np.int64).max)
CHUNK = 4096

# letters: 1 = x, 2 = y, -1 = X = x^-1, -2 = Y = y^-1
LETTER = {1: "x", 2: "y", -1: "X", -2: "Y"}

# The eight signed relabelings (image of x, image of y), in the order of the task.
RELABELINGS = (
    (1, 2),    # x->x,y->y
    (1, -2),   # x->x,y->Y
    (-1, 2),   # x->X,y->y
    (-1, -2),  # x->X,y->Y
    (2, 1),    # x->y,y->x
    (2, -1),   # x->y,y->X
    (-2, 1),   # x->Y,y->x
    (-2, -1),  # x->Y,y->X
)

ROW_RE = re.compile(r"words up to length ([1-9][0-9]*)")
INT_KEY_RE = re.compile(r"0|[1-9][0-9]*")


def relabeling_name(f):
    return "x->%s,y->%s" % (LETTER[f[0]], LETTER[f[1]])


def _translate_table(f):
    fx, fy = f
    return str.maketrans({"x": LETTER[fx], "X": LETTER[-fx], "y": LETTER[fy], "Y": LETTER[-fy]})


TRANSLATE = [_translate_table(f) for f in RELABELINGS]


# --------------------------------------------------------------------------
# bookkeeping
# --------------------------------------------------------------------------

def _json_default(o):
    if isinstance(o, np.bool_):
        return bool(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (set, frozenset)):
        return sorted(o)
    return str(o)


def brief(v, limit=240):
    """A JSON-safe, short rendering of a value for the mismatch examples."""
    try:
        s = json.dumps(v, default=_json_default, sort_keys=True)
    except (TypeError, ValueError):
        return repr(v)[:limit]
    if len(s) <= limit:
        try:
            return json.loads(s)
        except ValueError:
            return s
    return s[:limit] + "...(truncated)"


class Run:
    def __init__(self):
        self.checks = []
        self.skipped = []
        self.first = []
        self.errors = []
        self.info = {}
        self.recomputed = {}
        self.report_only = {}  # other readings of the definitions: never compared

    def skip(self, what, why):
        self.skipped.append("%s: %s" % (what, why))


class Check:
    def __init__(self, run, name, report_only=False, prerequisite=False):
        self.run = run
        self.name = name
        self.compared = 0
        self.mismatches = 0
        self.detail = {}
        self.report_only = report_only
        self.prerequisite = prerequisite
        run.checks.append(self)

    def ok(self, count=1):
        self.compared += int(count)

    def bad(self, path, recomputed, committed, why):
        self.compared += 1
        self.mismatches += 1
        if len(self.run.first) < MAX_EXAMPLES:
            self.run.first.append({
                "check": self.name,
                "path": str(path),
                "recomputed": brief(recomputed),
                "committed": brief(committed),
                "why": why,
            })

    def as_dict(self):
        return {
            "name": self.name,
            "compared": int(self.compared),
            "mismatches": int(self.mismatches),
            "detail": self.detail,
        }


def is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def cmp_leaf(check, path, mine, ref):
    """mine is an int (must be equal), a float (within TOL) or a str (equal)."""
    if isinstance(mine, np.integer):
        mine = int(mine)
    elif isinstance(mine, np.floating):
        mine = float(mine)
    if isinstance(mine, (bool, np.bool_)):
        raise TypeError("no boolean is expected in a class view: %s" % path)
    if isinstance(mine, int):
        good = is_number(ref) and math.isfinite(float(ref)) and ref == mine
        if good:
            check.ok()
        else:
            check.bad(path, mine, ref, "integer missing or not equal")
    elif isinstance(mine, float):
        good = (is_number(ref) and math.isfinite(float(ref)) and math.isfinite(mine)
                and abs(float(ref) - mine) <= TOL)
        if good:
            check.ok()
        else:
            check.bad(path, mine, ref, "float missing or further than 1e-9")
    elif isinstance(mine, str):
        if isinstance(ref, str) and ref == mine:
            check.ok()
        else:
            check.bad(path, mine, ref, "string missing or not equal")
    else:
        raise TypeError("unexpected recomputed value at %s: %r" % (path, type(mine)))


def cmp_tree(check, path, mine, ref):
    """Two-sided comparison of a recomputed dict tree with the committed one."""
    if isinstance(mine, dict):
        if not isinstance(ref, dict):
            check.bad(path, mine, ref, "committed value missing or not an object")
            return
        for k in mine:
            if k not in ref:
                check.bad("%s.%s" % (path, k), mine[k], None, "key missing in the committed JSON")
            else:
                cmp_tree(check, "%s.%s" % (path, k), mine[k], ref[k])
        for k in ref:
            if k not in mine:
                check.bad("%s.%s" % (path, k), None, ref[k],
                          "key in the committed JSON that the definitions do not produce")
    else:
        cmp_leaf(check, path, mine, ref)


def cmp_counts(check, path, mine, ref):
    """name -> count maps; a name that is absent counts 0 on either side."""
    if not isinstance(ref, dict):
        check.bad(path, mine, ref, "committed value missing or not an object")
        return
    for k in sorted(set(mine) | set(ref)):
        cmp_leaf(check, "%s.%s" % (path, k), int(mine.get(k, 0)), ref.get(k, 0))


def get_path(obj, *keys):
    cur = obj
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            return None
        cur = cur[k]
    return cur


# --------------------------------------------------------------------------
# dataset and classes of copies
# --------------------------------------------------------------------------

def load_dataset(path):
    """Returns (list of (r1, r2) as tuples of signed letters, notes)."""
    with open(path, "r") as fh:
        lines = fh.read().splitlines()
    while lines and not lines[-1].strip():
        lines.pop()
    pres = []
    zeros_not_trailing = 0
    for ln, line in enumerate(lines):
        text = line.strip()
        if not text:
            raise ValueError("dataset line %d is empty" % ln)
        try:
            vals = json.loads(text)
        except ValueError:
            vals = ast.literal_eval(text)
        if not isinstance(vals, (list, tuple)) or len(vals) == 0 or len(vals) % 2 != 0:
            raise ValueError("dataset line %d is not a list of 2*L integers" % ln)
        half = len(vals) // 2
        rel = []
        for part in (vals[:half], vals[half:]):
            word = tuple(int(v) for v in part if v != 0)
            for v in word:
                if v not in LETTER:
                    raise ValueError("dataset line %d: letter %r is not one of 1, 2, -1, -2" % (ln, v))
            if any(v != 0 for v in part[len(word):]):
                zeros_not_trailing += 1
            rel.append(word)
        pres.append((rel[0], rel[1]))
    return pres, {"lines": len(pres), "relators_with_a_zero_before_a_letter": zeros_not_trailing}


def word_string(word):
    return "".join(LETTER[v] for v in word)


def apply_relabeling(f, word):
    fx, fy = f
    out = []
    for v in word:
        if v == 1:
            out.append(fx)
        elif v == -1:
            out.append(-fx)
        elif v == 2:
            out.append(fy)
        elif v == -2:
            out.append(-fy)
        else:
            raise ValueError("letter %r" % (v,))
    return tuple(out)


def inverse_word(word):
    return tuple(-v for v in reversed(word))


def canon_cyclic(word):
    """Smallest of all rotations of the word and of its inverse (no reduction)."""
    if not word:
        return ()
    best = None
    for u in (word, inverse_word(word)):
        for i in range(len(u)):
            r = u[i:] + u[:i]
            if best is None or r < best:
                best = r
    return best


def pair_key(f, pres):
    a = canon_cyclic(apply_relabeling(f, pres[0]))
    b = canon_cyclic(apply_relabeling(f, pres[1]))
    return (a, b) if a <= b else (b, a)


def cyclically_reduce(word):
    st = []
    for v in word:
        if st and st[-1] == -v:
            st.pop()
        else:
            st.append(v)
    i, j = 0, len(st) - 1
    while i < j and st[i] == -st[j]:
        i += 1
        j -= 1
    return tuple(st[i:j + 1])


def same_partition(a, b):
    return len(set(zip(a, b))) == len(set(a)) == len(set(b))


def build_classes(pres):
    n = len(pres)
    # keys[p][j] = the unordered pair of relators of f_j(p), each up to rotation and inversion
    keys = [[pair_key(f, p) for f in RELABELINGS] for p in pres]

    # method A: union-find on "some relabeling maps a onto b"
    by_identity = {}
    for p in range(n):
        by_identity.setdefault(keys[p][0], []).append(p)
    parent = list(range(n))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    for a in range(n):
        for j in range(len(RELABELINGS)):
            for b in by_identity.get(keys[a][j], ()):
                ra, rb = find(a), find(b)
                if ra != rb:
                    parent[max(ra, rb)] = min(ra, rb)

    label = {}
    class_of = []
    for p in range(n):
        r = find(p)
        if r not in label:
            label[r] = len(label)
        class_of.append(label[r])
    ncls = len(label)

    # method B: the orbit minimum.  The eight relabelings are a group, so this
    # must give the same partition; a difference is a bug in this script.
    orbit = [min(keys[p]) for p in range(n)]
    if not same_partition(class_of, orbit):
        raise RuntimeError("internal: union-find classes and orbit-minimum classes differ")

    members = [[] for _ in range(ncls)]
    for p in range(n):
        members[class_of[p]].append(p)  # pres_id ascending by construction

    twins = []
    twins_back = []     # report only: (a, b, first relabeling that maps b onto a)
    n_maps = Counter()  # report only: how many of the eight relabelings map a onto b
    for c in range(ncls):
        m = members[c]
        for i in range(len(m)):
            for k in range(i + 1, len(m)):
                a, b = m[i], m[k]
                first = None
                for j in range(len(RELABELINGS)):
                    if keys[a][j] == keys[b][0]:  # f_j applied to a gives b
                        first = j
                        break
                if first is None:
                    raise RuntimeError("internal: no relabeling maps %d onto %d" % (a, b))
                twins.append((a, b, first))
                n_maps[sum(1 for j in range(len(RELABELINGS)) if keys[a][j] == keys[b][0])] += 1
                for j in range(len(RELABELINGS)):
                    if keys[b][j] == keys[a][0]:  # f_j applied to b gives a
                        twins_back.append((a, b, j))
                        break

    sizes = Counter(len(m) for m in members)
    relab = Counter(relabeling_name(RELABELINGS[j]) for (_, _, j) in twins)
    relab_back = Counter(relabeling_name(RELABELINGS[j]) for (_, _, j) in twins_back)
    not_involution = [[int(a), int(b), relabeling_name(RELABELINGS[j])] for (a, b, j) in twins
                      if apply_relabeling(RELABELINGS[j], RELABELINGS[j]) != (1, 2)]

    # report only: would cyclically reducing the relators first change the classes?
    not_free = 0
    not_cyc = 0
    red = []
    for (r1, r2) in pres:
        rr = []
        for r in (r1, r2):
            st = []
            for v in r:
                if st and st[-1] == -v:
                    st.pop()
                else:
                    st.append(v)
            if len(st) != len(r):
                not_free += 1
            cr = cyclically_reduce(r)
            if len(cr) != len(r):
                not_cyc += 1
            rr.append(cr)
        red.append((rr[0], rr[1]))
    orbit_red = [min(pair_key(f, p) for f in RELABELINGS) for p in red]

    return {
        "n": ncls,
        "class_of": class_of,
        "members": members,
        "twins": twins,
        "twins_back": twins_back,
        "sizes": {str(int(s)): int(c) for s, c in sorted(sizes.items())},
        "twin_relabelings": {str(k): int(v) for k, v in relab.items()},
        "report_only": {
            "twin_pairs_by_number_of_relabelings_that_map_a_onto_b":
                {str(int(k)): int(v) for k, v in sorted(n_maps.items())},
            "twin_pairs_whose_relabeling_is_not_its_own_inverse": not_involution,
            "twin_relabelings_if_the_relabeling_is_the_first_that_maps_b_onto_a":
                {str(k): int(v) for k, v in relab_back.items()},
        },
        "notes": {
            "relators_not_freely_reduced": not_free,
            "relators_not_cyclically_reduced": not_cyc,
            "same_classes_if_relators_are_cyclically_reduced_first": bool(same_partition(class_of, orbit_red)),
        },
    }


# --------------------------------------------------------------------------
# statistics
# --------------------------------------------------------------------------

class GapAcc:
    """Gap statistics of two aligned lists of searches, fed in pieces."""

    def __init__(self):
        self.pairs = 0
        self.differs = 0
        self.both = 0
        self.gaps = []
        self.zero_max = 0

    def add(self, sa, sb, na, nb):
        sa = np.asarray(sa, dtype=bool)
        sb = np.asarray(sb, dtype=bool)
        na = np.asarray(na).astype(np.int64)
        nb = np.asarray(nb).astype(np.int64)
        if not (sa.shape == sb.shape == na.shape == nb.shape) or sa.ndim != 1:
            raise RuntimeError("internal: unaligned search lists")
        self.pairs += int(sa.shape[0])
        self.differs += int(np.count_nonzero(sa != sb))
        both = sa & sb
        nboth = int(np.count_nonzero(both))
        self.both += nboth
        if nboth:
            a = na[both]
            b = nb[both]
            num = np.abs(a - b).astype(np.float64)
            den = np.maximum(a, b).astype(np.float64)
            zero = den == 0.0
            nzero = int(np.count_nonzero(zero))
            if nzero:
                # 0 nodes on both sides: |0 - 0| / max(0, 0) is read as gap 0
                self.zero_max += nzero
                den = np.where(zero, 1.0, den)
            self.gaps.append(num / den)

    def stats(self):
        out = {
            "pairs": int(self.pairs),
            "solved_flag_differs": int(self.differs),
            "both_solved": int(self.both),
        }
        if self.both > 0:
            g = np.concatenate(self.gaps)
            if int(g.shape[0]) != self.both:
                raise RuntimeError("internal: gap count")
            out["same_nodes"] = float(np.mean(g == 0.0))
            out["gap_median"] = float(np.median(g))
            out["gap_p90"] = float(np.quantile(g, 0.9))
            out["gap_p99"] = float(np.quantile(g, 0.99))
        return out


def control_noise(twins, c_solved, c_nodes):
    a = np.array([t[0] for t in twins], dtype=np.int64)
    b = np.array([t[1] for t in twins], dtype=np.int64)
    acc = GapAcc()
    acc.add(c_solved[a], c_solved[b], c_nodes[a], c_nodes[b])
    return acc


def start_noise(twins, words, nodes, solved, row_of):
    """Pairs the search (a, w) with (b, f(w)) for every twin pair and every
    word w whose letter-by-letter image f(w) is itself an entry of words."""
    index = {}
    for k, w in enumerate(words):
        index.setdefault(w, k)
    count = len(words)
    acc = GapAcc()
    cache = {}
    for (a, b, j) in twins:
        if j not in cache:
            table = TRANSLATE[j]
            img = np.fromiter((index.get(w.translate(table), -1) for w in words),
                              dtype=np.int64, count=count)
            cols = np.flatnonzero(img >= 0)
            cache[j] = (cols, img[cols])
        cols, tgt = cache[j]
        ra = int(row_of[a])
        rb = int(row_of[b])
        acc.add(solved[ra, cols], solved[rb, tgt], nodes[ra, cols], nodes[rb, tgt])
    return acc


def best_per_row(nodes, solved):
    """has[i] = some column of row i is solved; best[i] = fewest nodes over the
    solved columns of row i (BIG when none).  Column chunks keep memory small."""
    n, count = nodes.shape
    best = np.full(n, BIG, dtype=np.int64)
    has = np.zeros(n, dtype=bool)
    for c0 in range(0, count, CHUNK):
        blk = nodes[:, c0:c0 + CHUNK].astype(np.int64)
        s = solved[:, c0:c0 + CHUNK]
        masked = np.where(s, blk, BIG)
        best = np.minimum(best, masked.min(axis=1))
        has |= s.any(axis=1)
    return has, best


def row_stats(has, best, c_solved, c_nodes, class_of, ncls):
    """All arrays are indexed by pres_id.  Returns (presentations, classes, boundary)."""
    n = len(class_of)
    k_control = [False] * ncls
    k_start = [False] * ncls
    kc = [None] * ncls
    ks = [None] * ncls
    for p in range(n):
        c = class_of[p]
        if bool(c_solved[p]):
            k_control[c] = True
            v = int(c_nodes[p])
            if kc[c] is None or v < kc[c]:
                kc[c] = v
        if bool(has[p]):
            k_start[c] = True
            v = int(best[p])
            if ks[c] is None or v < ks[c]:
                ks[c] = v

    pres = {
        "n": n,
        "control": 0,
        "some_start": 0,
        "gained": 0,
        "gained_but_control_solves_a_copy": 0,
        "lost": 0,
        "cheaper": 0,
        "cheaper_beyond_noise": 0,
        "cheaper_than_every_copy_of_control": 0,
    }
    examined = 0
    on_boundary = 0
    on_boundary_counted = 0
    disagree = 0
    beyond_exact = 0  # report only: cheaper_beyond_noise with the exact test 100*best < 83*c_nodes
    for p in range(n):
        c = class_of[p]
        cs = bool(c_solved[p])
        hs = bool(has[p])
        cn = int(c_nodes[p])
        bp = int(best[p]) if hs else None
        if cs:
            pres["control"] += 1
        if hs:
            pres["some_start"] += 1
        gained = hs and not cs
        if gained:
            pres["gained"] += 1
            if k_control[c]:
                pres["gained_but_control_solves_a_copy"] += 1
        if cs and not hs:
            pres["lost"] += 1
        if hs and (not cs or bp < cn):
            pres["cheaper"] += 1
        by_float = bool(cs and hs and (float(bp) < float(cn) * (1 - NOISE_THRESHOLD)))
        if gained or by_float:
            pres["cheaper_beyond_noise"] += 1
        if gained or (cs and hs and 100 * bp < 83 * cn):
            beyond_exact += 1
        if hs and ((not k_control[c]) or bp < kc[c]):
            pres["cheaper_than_every_copy_of_control"] += 1
        if cs and hs:
            examined += 1
            if 100 * bp == 83 * cn:
                on_boundary += 1
                if by_float:
                    on_boundary_counted += 1
            if (100 * bp < 83 * cn) != by_float:
                disagree += 1

    classes = {"n": int(ncls), "control": 0, "some_start": 0, "gained": 0, "lost": 0, "cheaper": 0}
    for c in range(ncls):
        if k_control[c]:
            classes["control"] += 1
        if k_start[c]:
            classes["some_start"] += 1
        if k_start[c] and not k_control[c]:
            classes["gained"] += 1
        if k_control[c] and not k_start[c]:
            classes["lost"] += 1
        if k_start[c] and ((not k_control[c]) or ks[c] < kc[c]):
            classes["cheaper"] += 1

    boundary = {
        "examined_control_and_some_start_solve": examined,
        "on_boundary_100best_eq_83control": on_boundary,
        "on_boundary_counted_as_beyond_noise_by_the_float_test": on_boundary_counted,
        "float_test_differs_from_exact_100best_lt_83control": disagree,
        "cheaper_beyond_noise_by_the_float_test_of_the_task": pres["cheaper_beyond_noise"],
        "cheaper_beyond_noise_by_the_exact_test_100best_lt_83control": beyond_exact,
    }
    return pres, classes, boundary


# --------------------------------------------------------------------------
# reading the result files
# --------------------------------------------------------------------------

def read_json(path):
    with open(path, "r") as fh:
        return json.load(fh)


def _fetch(z, path, key):
    try:
        return z[key]
    except ValueError:
        if key not in ("words", "meta"):
            raise
        # a string array stored as objects; these are the experiment's own files
        with np.load(path, allow_pickle=True) as z2:
            return z2[key]


def load_npz(path, required, optional=()):
    out = {}
    with np.load(path, allow_pickle=False) as z:
        names = set(z.files)
        for k in required:
            if k not in names:
                raise KeyError("array %r is not in %s" % (k, os.path.basename(path)))
            out[k] = _fetch(z, path, k)
        for k in optional:
            if k in names:
                try:
                    out[k] = _fetch(z, path, k)
                except Exception:  # optional arrays are only used for notes
                    pass
    return out


def as_str_list(arr):
    out = []
    for w in np.asarray(arr).ravel().tolist():
        out.append(w.decode("ascii") if isinstance(w, bytes) else str(w))
    return out


def parse_meta(arr):
    try:
        v = np.asarray(arr)
        v = v.item() if v.ndim == 0 else v.ravel().tolist()[0]
        if isinstance(v, bytes):
            v = v.decode("utf-8")
        meta = json.loads(v)
        return meta if isinstance(meta, dict) else None
    except Exception:
        return None


def row_index(pres_ids):
    """row_of[pres_id] = row of that presentation; None when pres_ids is not a
    permutation of 0..639."""
    ids = np.asarray(pres_ids).astype(np.int64).ravel()
    if ids.shape[0] != N_PRES:
        return None
    if not np.array_equal(np.sort(ids), np.arange(N_PRES, dtype=np.int64)):
        return None
    row_of = np.empty(N_PRES, dtype=np.int64)
    row_of[ids] = np.arange(N_PRES, dtype=np.int64)
    return row_of


def load_control(path, pres_strings, check):
    """Returns (c_solved bool[640], c_nodes int64[640]) indexed by pres_id, or
    None when some presentation has no usable control row."""
    rows = {}
    with open(path, "r") as fh:
        for line in fh:
            text = line.strip()
            if not text:
                continue
            row = json.loads(text)
            pid = row.get("pres_id") if isinstance(row, dict) else None
            if (isinstance(pid, bool) or not isinstance(pid, int)
                    or not (0 <= pid < N_PRES) or pid in rows):
                check.bad("control.pres_id", "each of 0..639 once", pid,
                          "pres_id is not an int in 0..639 or is repeated")
                continue
            rows[pid] = row
    usable = True
    c_solved = np.zeros(N_PRES, dtype=bool)
    c_nodes = np.zeros(N_PRES, dtype=np.int64)
    for p in range(N_PRES):
        row = rows.get(p)
        if row is None:
            check.bad("control[pres_id=%d]" % p, "one row", None, "no control row for this presentation")
            usable = False
            continue
        for key, want in (("r1", pres_strings[p][0]), ("r2", pres_strings[p][1])):
            if row.get(key) == want:
                check.ok()
            else:
                check.bad("control[pres_id=%d].%s" % (p, key), want, row.get(key),
                          "control relator differs from the dataset line")
        s = row.get("solved")
        nd = row.get("nodes_explored")
        nd_is_int = isinstance(nd, int) and not isinstance(nd, bool)
        if not isinstance(s, bool) or (s and not nd_is_int):
            check.bad("control[pres_id=%d].solved/nodes_explored" % p, "bool and int", [s, nd],
                      "solved is not a boolean, or a solved row has no integer node count")
            usable = False
            continue
        check.ok()
        c_solved[p] = s
        c_nodes[p] = int(nd) if nd_is_int else 0
    return (c_solved, c_nodes) if usable else None


# --------------------------------------------------------------------------
# comparisons shared by the two kinds of file
# --------------------------------------------------------------------------

def compare_class_of(check, cls, ref_map):
    if not isinstance(ref_map, dict):
        check.bad("classes.class_of", "an object with 640 keys", ref_map, "missing or not an object")
        return
    ref_label = {}
    for k, v in ref_map.items():
        if not (isinstance(k, str) and INT_KEY_RE.fullmatch(k) and int(k) < N_PRES):
            check.bad("classes.class_of[%s]" % (k,), None, v, "key is not a pres_id in 0..639")
            continue
        ref_label[int(k)] = json.dumps(v, sort_keys=True)
    ref_members = {}
    for p, lab in ref_label.items():
        ref_members.setdefault(lab, set()).add(p)
    members = cls["members"]
    class_of = cls["class_of"]
    for p in range(N_PRES):
        if p not in ref_label:
            check.bad("classes.class_of[%d]" % p, "a class label", None,
                      "presentation missing from the committed class_of")
            continue
        mine = set(members[class_of[p]])
        theirs = ref_members[ref_label[p]]
        if mine == theirs:
            check.ok()
        else:
            check.bad("classes.class_of[%d]" % p, sorted(mine), sorted(theirs),
                      "the set of copies of this presentation differs (compared as a partition)")
    check.detail["committed_distinct_labels"] = len(ref_members)
    check.detail["recomputed_classes"] = int(cls["n"])


def compare_classes(c_cls, c_cof, c_thr, cls, ref):
    rc = ref.get("classes")
    if not isinstance(rc, dict):
        c_cls.bad("classes", "an object", rc, "missing or not an object")
        c_cof.bad("classes.class_of", "an object with 640 keys", None, "classes block missing")
    else:
        cmp_leaf(c_cls, "classes.presentations", N_PRES, rc.get("presentations"))
        cmp_leaf(c_cls, "classes.n", int(cls["n"]), rc.get("n"))
        cmp_counts(c_cls, "classes.sizes", cls["sizes"], rc.get("sizes"))
        cmp_leaf(c_cls, "classes.twin_pairs", len(cls["twins"]), rc.get("twin_pairs"))
        cmp_counts(c_cls, "classes.twin_relabelings", cls["twin_relabelings"], rc.get("twin_relabelings"))
        known = ("presentations", "n", "sizes", "twin_pairs", "twin_relabelings", "class_of")
        for k in rc:
            if k not in known:
                c_cls.bad("classes.%s" % (k,), None, rc[k],
                          "key in the committed JSON that the definitions do not produce")
        compare_class_of(c_cof, cls, rc.get("class_of"))
    for k in ref:
        if k not in ("classes", "noise", "noise_threshold", "rows"):
            c_cls.bad(str(k), None, ref[k], "top-level key that the definitions do not produce")
    cmp_leaf(c_thr, "noise_threshold", float(NOISE_THRESHOLD), ref.get("noise_threshold"))


def load_reference(run, results_dir, stem, c_cls):
    """Returns (ref dict, have_ref)."""
    name = stem + "_class_view.json"
    path = os.path.join(results_dir, name)
    if not os.path.isfile(path):
        run.skip(name, "absent: nothing can be compared for this file")
        return {}, False
    ref = read_json(path)
    if not isinstance(ref, dict):
        c_cls.bad("(top level)", "an object", ref, "the committed JSON is not an object")
        return {}, True
    return ref, True


def mark_no_reference(checks, stem):
    for c in checks:
        c.detail["reason_nothing_compared"] = "%s_class_view.json is absent" % stem


def noise_extra_keys(check, ref):
    noise = ref.get("noise")
    if isinstance(noise, dict):
        for k in noise:
            if k not in ("control", "starts"):
                check.bad("noise.%s" % (k,), None, noise[k],
                          "key in the committed JSON that the definitions do not produce")


def record_boundary(c_bnd, boundary):
    """Report only: never a mismatch."""
    c_bnd.detail["by_row"] = boundary
    total = 0
    for name in boundary:
        total += int(boundary[name]["examined_control_and_some_start_solve"])
    c_bnd.compared = int(total)
    c_bnd.detail["note"] = ("report only, not a comparison: presentations with 100*best == 83*control_nodes "
                            "among those where the control and some start both solve")
    if boundary:
        last = list(boundary.keys())[-1]
        c_bnd.detail["file_value_last_row"] = {"row": last,
                                               "on_boundary": boundary[last]["on_boundary_100best_eq_83control"]}


# --------------------------------------------------------------------------
# rank 3
# --------------------------------------------------------------------------

def process_rank3(run, budget, results_dir, cls, pres_strings, deadline):
    stem = "rank3_bf_ms640_b%d_cap24" % budget
    c_in = Check(run, stem + ":inputs", prerequisite=True)
    c_cls = Check(run, stem + ":classes")
    c_cof = Check(run, stem + ":classes.class_of")
    c_thr = Check(run, stem + ":noise_threshold")
    c_nc = Check(run, stem + ":noise.control")
    c_ns = Check(run, stem + ":noise.starts")
    c_rows = Check(run, stem + ":rows")
    c_bnd = Check(run, stem + ":boundary_17pct(report only)", report_only=True)

    ref, have_ref = load_reference(run, results_dir, stem, c_cls)
    if not have_ref:
        mark_no_reference((c_cls, c_cof, c_thr, c_nc, c_ns, c_rows), stem)

    # control
    control = None
    ctl_name = stem + "_control.jsonl"
    ctl_path = os.path.join(results_dir, ctl_name)
    if os.path.isfile(ctl_path):
        control = load_control(ctl_path, pres_strings, c_in)
        if control is None:
            run.skip(ctl_name, "unusable (see the inputs check): noise.control and rows not recomputed")
    else:
        run.skip(ctl_name, "absent: noise.control and rows not recomputed")

    # lengths to look for: 1..10 and any length the committed JSON mentions
    lengths = set(DEFAULT_LENGTHS)
    ref_starts = get_path(ref, "noise", "starts")
    if isinstance(ref_starts, dict):
        for k in ref_starts:
            if isinstance(k, str) and INT_KEY_RE.fullmatch(k) and int(k) >= 1:
                lengths.add(int(k))
    ref_rows = ref.get("rows")
    if isinstance(ref_rows, list):
        for r in ref_rows:
            nm = r.get("name") if isinstance(r, dict) else None
            m = ROW_RE.fullmatch(nm) if isinstance(nm, str) else None
            if m:
                lengths.add(int(m.group(1)))
    lengths = sorted(lengths)

    cum_has = np.zeros(N_PRES, dtype=bool)
    cum_best = np.full(N_PRES, BIG, dtype=np.int64)
    cum_starts = 0
    my_rows = {}
    my_starts = {}
    boundary = {}
    unavailable = {}
    used = []
    zero_max = {}
    length_gaps = []
    incomplete = {}  # length n -> why its cumulative row is not compared
    ro_starts = {}   # report only
    ro_rows = {}     # report only

    for n in lengths:
        fname = "%s_L%d.npz" % (stem, n)
        path = os.path.join(results_dir, fname)
        if not os.path.isfile(path):
            unavailable[n] = "absent"
            run.skip(fname, "absent")
            continue
        if time.time() > deadline:
            unavailable[n] = "time box reached"
            run.skip(fname, "time box reached before this file was read")
            continue
        try:
            d = load_npz(path, ("pres_ids", "words", "nodes", "path_len"))
            words = as_str_list(d["words"])
            nodes = d["nodes"]
            path_len = d["path_len"]
            row_of = row_index(d["pres_ids"])
            problem = None
            if row_of is None:
                problem = "pres_ids is not a permutation of 0..639"
            elif nodes.ndim != 2 or nodes.shape != path_len.shape or nodes.shape != (N_PRES, len(words)):
                problem = "shapes: nodes %r, path_len %r, words %d" % (nodes.shape, path_len.shape, len(words))
            elif len(set(words)) != len(words):
                problem = "words has repeated entries"
        except Exception as exc:  # unreadable result file: a finding, not a crash
            problem = "could not be read: %r" % (exc,)
        if problem is not None:
            c_in.bad(fname, "a usable length file", problem, "length file unusable")
            unavailable[n] = "unusable: " + problem
            run.skip(fname, "unusable: " + problem)
            continue
        c_in.ok(3)  # pres_ids permutation, shapes, words distinct

        missing_below = [k for k in range(1, n) if k not in used]
        if missing_below:
            length_gaps.append(n)
        used.append(n)

        solved = path_len >= 0
        has_f, best_f = best_per_row(nodes, solved)
        cum_has = cum_has | has_f[row_of]
        cum_best = np.minimum(cum_best, best_f[row_of])
        cum_starts += len(words)

        acc = start_noise(cls["twins"], words, nodes, solved, row_of)
        my_starts[str(n)] = acc.stats()
        if acc.zero_max:
            zero_max[str(n)] = int(acc.zero_max)
        try:  # report only: the twin relabeling read as the first that maps b onto a
            alt = start_noise(cls["twins_back"], words, nodes, solved, row_of).stats()
            same = bool(alt == my_starts[str(n)])
            alt["identical_to_the_compared_reading"] = same
            ro_starts[str(n)] = alt
        except Exception as exc:
            ro_starts[str(n)] = {"error": repr(exc)}

        if control is not None:
            name = "words up to length %d" % n
            pres_block, class_block, bnd = row_stats(cum_has, cum_best, control[0], control[1],
                                                     cls["class_of"], cls["n"])
            row = {"name": name, "starts": int(cum_starts),
                   "presentations": pres_block, "classes": class_block}
            if missing_below:
                # the row of the task is all words of lengths 1..n: without every one of
                # those files it is not defined, so it is reported but not compared
                incomplete[n] = "length file(s) %s below it are not available" % (missing_below,)
                run.skip("%s:rows[%s]" % (stem, name), "not compared, " + incomplete[n])
                ro_rows[name] = row
            else:
                my_rows[name] = row
                boundary[name] = bnd
        del d, nodes, path_len, solved, has_f, best_f

    c_in.detail["length_files_used"] = used
    c_ns.detail["lengths_recomputed"] = used
    c_rows.detail["rows_recomputed"] = list(my_rows.keys())
    if length_gaps:
        c_rows.detail["length_gap_before"] = length_gaps
        c_rows.detail["length_gap_note"] = ("a length below these is not available: their rows are not compared "
                                            "(listed as skipped); the union of the length files available up to "
                                            "each is under report_only")
    if zero_max:
        c_ns.detail["both_solved_pairs_with_0_nodes_on_both_sides_read_as_gap_0"] = zero_max

    mine_nc = None
    if control is not None:
        acc = control_noise(cls["twins"], control[0], control[1])
        mine_nc = acc.stats()
        if acc.zero_max:
            c_nc.detail["both_solved_pairs_with_0_nodes_on_both_sides_read_as_gap_0"] = int(acc.zero_max)

    run.recomputed[stem] = {
        "noise": {"control": mine_nc, "starts": my_starts},
        "noise_threshold": NOISE_THRESHOLD,
        "rows": list(my_rows.values()),
    }
    record_boundary(c_bnd, boundary)
    run.info[stem] = {"boundary_17pct": boundary}
    run.report_only[stem] = {
        "noise.starts_if_the_twin_relabeling_is_the_first_that_maps_b_onto_a": ro_starts,
        "rows_from_the_available_lengths_when_a_lower_length_is_missing": ro_rows,
    }

    if not have_ref:
        return

    compare_classes(c_cls, c_cof, c_thr, cls, ref)
    noise_extra_keys(c_nc, ref)

    # noise.control
    if mine_nc is not None:
        cmp_tree(c_nc, "noise.control", mine_nc, get_path(ref, "noise", "control"))
    else:
        c_nc.detail["reason_nothing_compared"] = "%s is absent or unusable" % ctl_name

    # noise.starts
    if not isinstance(ref_starts, dict):
        c_ns.bad("noise.starts", my_starts, ref_starts, "missing or not an object")
    else:
        for key in my_starts:
            if key not in ref_starts:
                c_ns.bad("noise.starts.%s" % key, my_starts[key], None,
                         "the length file is present but the committed JSON has no entry")
                c_ns.detail.setdefault("length_files_present_without_a_committed_entry", []).append(key)
            else:
                cmp_tree(c_ns, "noise.starts.%s" % key, my_starts[key], ref_starts[key])
        for key in ref_starts:
            if key in my_starts:
                continue
            is_len = isinstance(key, str) and INT_KEY_RE.fullmatch(key) and int(key) in unavailable
            if is_len:
                run.skip("%s:noise.starts[%s]" % (stem, key),
                         "not recomputed, length file %s" % unavailable[int(key)])
            else:
                c_ns.bad("noise.starts.%s" % (key,), None, ref_starts[key],
                         "committed entry that is not a word length")

    # rows
    if not isinstance(ref_rows, list):
        c_rows.bad("rows", list(my_rows.keys()), ref_rows, "missing or not a list")
    else:
        by_name = {}
        for i, r in enumerate(ref_rows):
            nm = r.get("name") if isinstance(r, dict) else None
            if not isinstance(nm, str) or nm in by_name:
                c_rows.bad("rows[%d].name" % i, None, nm, "row without a string name, or a repeated name")
                continue
            by_name[nm] = r
        for nm in my_rows:
            if nm not in by_name:
                c_rows.bad("rows[%s]" % nm, my_rows[nm], None,
                           "the length file is present but the committed JSON has no row")
                c_rows.detail.setdefault("rows_recomputed_without_a_committed_row", []).append(nm)
            else:
                cmp_tree(c_rows, "rows[%s]" % nm, my_rows[nm], by_name[nm])
        for nm in by_name:
            if nm in my_rows:
                continue
            m = ROW_RE.fullmatch(nm)
            if m and control is None:
                run.skip("%s:rows[%s]" % (stem, nm), "not recomputed, %s absent or unusable" % ctl_name)
            elif m and int(m.group(1)) in unavailable:
                run.skip("%s:rows[%s]" % (stem, nm),
                         "not recomputed, length file %s" % unavailable[int(m.group(1))])
            elif m and int(m.group(1)) in incomplete:
                pass  # already listed as skipped: a lower length file is missing
            else:
                c_rows.bad("rows[%s]" % nm, None, by_name[nm],
                           "committed row that the definitions do not produce")
        if control is None:
            c_rows.detail["reason_nothing_compared"] = "%s is absent or unusable" % ctl_name


# --------------------------------------------------------------------------
# rank n
# --------------------------------------------------------------------------

def process_rankn(run, rank, results_dir, cls, deadline):
    stem = "rankn_bf_ms640_b1000_cap24_r%d" % rank
    c_in = Check(run, stem + ":inputs", prerequisite=True)
    c_cls = Check(run, stem + ":classes")
    c_cof = Check(run, stem + ":classes.class_of")
    c_thr = Check(run, stem + ":noise_threshold")
    c_nc = Check(run, stem + ":noise.control")
    c_ns = Check(run, stem + ":noise.starts")
    c_rows = Check(run, stem + ":rows")
    c_bnd = Check(run, stem + ":boundary_17pct(report only)", report_only=True)

    ref, have_ref = load_reference(run, results_dir, stem, c_cls)
    if not have_ref:
        mark_no_reference((c_cls, c_cof, c_thr, c_nc, c_ns, c_rows), stem)

    fname = stem + ".npz"
    path = os.path.join(results_dir, fname)
    mine_nc = None
    mine_row = None
    meta = None
    available = False
    boundary = {}
    ro = {}  # report only
    if not os.path.isfile(path):
        run.skip(fname, "absent: noise.control and rows not recomputed")
    elif time.time() > deadline:
        run.skip(fname, "time box reached before this file was read")
    else:
        try:
            d = load_npz(path, ("pres_ids", "nodes", "path_len", "base"), optional=("meta", "combos"))
            nodes = d["nodes"]
            path_len = d["path_len"]
            base = np.asarray(d["base"]).astype(np.int64)
            row_of = row_index(d["pres_ids"])
            problem = None
            if row_of is None:
                problem = "pres_ids is not a permutation of 0..639"
            elif nodes.ndim != 2 or nodes.shape != path_len.shape or nodes.shape[0] != N_PRES:
                problem = "shapes: nodes %r, path_len %r" % (nodes.shape, path_len.shape)
            elif base.ndim != 2 or base.shape[0] != N_PRES or base.shape[1] < 2:
                problem = "shape of base: %r" % (base.shape,)
            elif not bool(np.all((base[:, 0] == 0) | (base[:, 0] == 1))):
                problem = "base column 0 is not 0/1"
        except Exception as exc:  # unreadable result file: a finding, not a crash
            problem = "could not be read: %r" % (exc,)
        if problem is not None:
            c_in.bad(fname, "a usable rank-n file", problem, "rank-n file unusable")
            run.skip(fname, "unusable: " + problem)
        else:
            c_in.ok(4)  # pres_ids permutation, shapes of nodes/path_len, shape of base, base flags 0/1
            available = True
            columns = int(nodes.shape[1])
            if "combos" in d:
                combos = np.asarray(d["combos"])
                if combos.ndim == 2 and int(combos.shape[0]) == columns:
                    c_in.ok()
                else:
                    c_in.bad(fname + ":combos", "%d rows" % columns, list(combos.shape),
                             "combos does not have one row per column of nodes")
            if "meta" in d:
                meta = parse_meta(d["meta"])
            if isinstance(meta, dict) and "rank" in meta:
                if meta.get("rank") == rank:
                    c_in.ok()
                else:
                    c_in.bad(fname + ":meta.rank", rank, meta.get("rank"), "rank in meta differs from the file name")

            c_solved = (base[:, 0] != 0)[row_of]
            c_nodes = base[:, 1][row_of]
            solved = path_len >= 0
            has_f, best_f = best_per_row(nodes, solved)
            has = has_f[row_of]
            best = best_f[row_of]
            pres_block, class_block, bnd = row_stats(has, best, c_solved, c_nodes, cls["class_of"], cls["n"])
            mine_row = {"starts": columns, "presentations": pres_block, "classes": class_block}
            boundary["all columns"] = bnd
            acc = control_noise(cls["twins"], c_solved, c_nodes)
            mine_nc = acc.stats()
            if acc.zero_max:
                c_nc.detail["both_solved_pairs_with_0_nodes_on_both_sides_read_as_gap_0"] = int(acc.zero_max)
            # The task does not say how the rows of base are ordered.  Compared reading:
            # row i is pres_ids[i], like nodes.  When pres_ids is 0..639 in order the other
            # reading (row i is presentation i) is the same; otherwise it is reported.
            in_order = bool(np.array_equal(row_of, np.arange(N_PRES)))
            c_in.detail["pres_ids_is_0_to_639_in_order"] = in_order
            if not in_order:
                try:
                    alt_solved = base[:, 0] != 0
                    alt_pres, alt_cls, _ = row_stats(has, best, alt_solved, base[:, 1],
                                                     cls["class_of"], cls["n"])
                    ro["if_row_i_of_base_is_presentation_i"] = {
                        "noise.control": control_noise(cls["twins"], alt_solved, base[:, 1]).stats(),
                        "row": {"starts": columns, "presentations": alt_pres, "classes": alt_cls},
                    }
                except Exception as exc:
                    ro["if_row_i_of_base_is_presentation_i"] = {"error": repr(exc)}
            del d, nodes, path_len, solved, has_f, best_f

    run.recomputed[stem] = {
        "noise": {"control": mine_nc, "starts": {}},
        "noise_threshold": NOISE_THRESHOLD,
        "rows": [mine_row] if mine_row is not None else [],
    }
    record_boundary(c_bnd, boundary)
    run.info[stem] = {"boundary_17pct": boundary}
    run.report_only[stem] = ro

    if not have_ref:
        return

    compare_classes(c_cls, c_cof, c_thr, cls, ref)
    noise_extra_keys(c_nc, ref)

    # a rank-n file has no start noise: the block must be an empty object
    ref_starts = get_path(ref, "noise", "starts")
    if isinstance(ref_starts, dict) and len(ref_starts) == 0:
        c_ns.ok()
    else:
        c_ns.bad("noise.starts", {}, ref_starts, "a rank-n class view has no start noise entries")

    if not available:
        c_nc.detail["reason_nothing_compared"] = "%s is absent or unusable" % fname
        c_rows.detail["reason_nothing_compared"] = "%s is absent or unusable" % fname
        return

    cmp_tree(c_nc, "noise.control", mine_nc, get_path(ref, "noise", "control"))

    ref_rows = ref.get("rows")
    if not isinstance(ref_rows, list):
        c_rows.bad("rows", "a list with one row", ref_rows, "missing or not a list")
        return
    cmp_leaf(c_rows, "len(rows)", 1, len(ref_rows))
    if len(ref_rows) == 0:
        return
    r0 = ref_rows[0]
    if not isinstance(r0, dict):
        c_rows.bad("rows[0]", mine_row, r0, "not an object")
        return
    cmp_tree(c_rows, "rows[0]", mine_row, {k: v for k, v in r0.items() if k != "name"})
    # the numbers inside the name: "every <k> words up to length <m> (rank <R>)"
    name = r0.get("name")
    want = None
    if isinstance(meta, dict):
        k_extra = meta.get("extra_generators")
        m_len = meta.get("max_word_len")
        if all(isinstance(v, int) and not isinstance(v, bool) for v in (k_extra, m_len)):
            want = [int(k_extra), int(m_len), int(rank)]
    if not isinstance(name, str):
        c_rows.bad("rows[0].name", want, name, "row without a string name")
    elif want is None:
        c_rows.detail["name_not_checked"] = "meta has no extra_generators / max_word_len"
    else:
        got = [int(t) for t in re.findall(r"[0-9]+", name)]
        if got == want:
            c_rows.ok()
        else:
            c_rows.bad("rows[0].name (numbers k, m, rank)", want, name,
                       "the numbers in the row name are not (extra_generators, max_word_len, rank)")
    c_rows.detail["committed_name"] = brief(name)


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def write_report(run, out_json, args, t0, crash=None):
    total = int(sum(c.mismatches for c in run.checks))
    compared_total = int(sum(c.compared for c in run.checks if not c.report_only and not c.prerequisite))
    input_items = int(sum(c.compared for c in run.checks if c.prerequisite))
    zero = [c.name for c in run.checks if c.compared == 0 and not c.report_only]
    doc = {
        "script": SCRIPT,
        "checks": [c.as_dict() for c in run.checks],
        "mismatches": total,
        "skipped": run.skipped,
        "first_mismatches": run.first,
        "compared_total": compared_total,
        "input_items_checked": input_items,
        "nothing_compared": bool(compared_total == 0),
        "checks_that_compared_0": zero,
        "comparison_checks_that_compared_0_(exit_3)": [c.name for c in run.checks
                                                       if c.compared == 0 and not c.report_only
                                                       and not c.prerequisite],
        "errors": run.errors,
        "info": run.info,
        "report_only": run.report_only,
        "recomputed": run.recomputed,
        "args": args,
        "seconds": round(time.time() - t0, 3),
    }
    if crash is not None:
        doc["crash"] = crash
    out_dir = os.path.dirname(os.path.abspath(out_json))
    if out_dir and not os.path.isdir(out_dir):
        os.makedirs(out_dir, exist_ok=True)
    with open(out_json, "w") as fh:
        json.dump(doc, fh, indent=1, default=_json_default)
        fh.write("\n")
    return total, compared_total, zero


def print_summary(run, total, compared_total, zero):
    for c in run.checks:
        if c.report_only:
            status = "REPORT ONLY"
        elif c.mismatches:
            status = "MISMATCH"
        elif c.compared == 0:
            status = "COMPARED 0 (not a pass)"
        else:
            status = "ok"
        extra = ""
        if c.report_only and "file_value_last_row" in c.detail:
            extra = " on_boundary(last row)=%d" % c.detail["file_value_last_row"]["on_boundary"]
        if c.compared == 0 and "reason_nothing_compared" in c.detail:
            extra = " [%s]" % c.detail["reason_nothing_compared"]
        print("%-66s compared=%d mismatches=%d %s%s" % (c.name, c.compared, c.mismatches, status, extra))
    print("skipped: %d item(s)" % len(run.skipped))
    for s in run.skipped:
        print("  skipped %s" % s)
    for e in run.errors:
        print("ERROR in %s: %s" % (e.get("where"), e.get("error")))
    print("TOTAL compared=%d mismatches=%d checks_that_compared_0=%d errors=%d"
          % (compared_total, total, len(zero), len(run.errors)))


def main(argv):
    t0 = time.time()
    if len(argv) < 4:
        print("usage: python3 -I -u %s <RESULTS_DIR> <DATASET> <OUT_JSON> [workers] [minutes]" % SCRIPT)
        return 1
    results_dir, dataset, out_json = argv[1], argv[2], argv[3]
    workers = int(argv[4]) if len(argv) > 4 else 1
    minutes = float(argv[5]) if len(argv) > 5 else 30.0
    deadline = t0 + 60.0 * minutes
    args = {"results_dir": results_dir, "dataset": dataset, "out_json": out_json,
            "workers": workers, "minutes": minutes, "numpy": np.__version__}
    run = Run()
    try:
        pres, ds_notes = load_dataset(dataset)
        if len(pres) != N_PRES:
            raise ValueError("the dataset has %d presentations, expected %d" % (len(pres), N_PRES))
        pres_strings = [(word_string(r1), word_string(r2)) for (r1, r2) in pres]
        cls = build_classes(pres)
        run.info["dataset"] = ds_notes
        run.info["classes"] = cls["notes"]
        run.report_only["classes"] = cls["report_only"]
        run.recomputed["classes"] = {
            "presentations": N_PRES,
            "n": int(cls["n"]),
            "sizes": cls["sizes"],
            "twin_pairs": len(cls["twins"]),
            "twin_relabelings": cls["twin_relabelings"],
            "class_of": {str(p): int(c) for p, c in enumerate(cls["class_of"])},
        }
        print("dataset: %d presentations, %d classes, sizes %s, %d twin pairs %s"
              % (len(pres), cls["n"], json.dumps(cls["sizes"]), len(cls["twins"]),
                 json.dumps(cls["twin_relabelings"])))

        for budget in BUDGETS:
            try:
                process_rank3(run, budget, results_dir, cls, pres_strings, deadline)
            except Exception as exc:
                run.errors.append({"where": "rank3 b%d" % budget, "error": repr(exc),
                                   "traceback": traceback.format_exc()})
                traceback.print_exc()
        for rank in RANKS:
            try:
                process_rankn(run, rank, results_dir, cls, deadline)
            except Exception as exc:
                run.errors.append({"where": "rankn r%d" % rank, "error": repr(exc),
                                   "traceback": traceback.format_exc()})
                traceback.print_exc()
    except Exception as exc:
        tb = traceback.format_exc()
        traceback.print_exc()
        run.errors.append({"where": "main", "error": repr(exc), "traceback": tb})
        try:
            total, compared_total, zero = write_report(run, out_json, args, t0, crash=tb)
            print_summary(run, total, compared_total, zero)
        except Exception:
            traceback.print_exc()
        print("RESULT crash (exit 1)")
        return 1

    total, compared_total, zero = write_report(run, out_json, args, t0)
    print_summary(run, total, compared_total, zero)
    if run.errors:
        print("RESULT crash in part of the run (exit 1)")
        return 1
    if total > 0:
        print("RESULT %d mismatch(es) (exit 3)" % total)
        return 3
    if compared_total == 0:
        print("RESULT nothing was compared with a committed class view: not a pass (exit 3)")
        return 3
    zero_cmp = [c.name for c in run.checks
                if c.compared == 0 and not c.report_only and not c.prerequisite]
    if zero_cmp:
        # no mismatch where something was compared, but a whole comparison compared
        # nothing (reference or input absent, unusable or past the time box)
        print("RESULT no mismatch in the %d items compared, but %d check(s) compared nothing: "
              "not a pass (exit 3): %s" % (compared_total, len(zero_cmp), ", ".join(zero_cmp)))
        return 3
    print("RESULT no mismatch in %d items compared with the committed class views (exit 0)" % compared_total)
    return 0


if __name__ == "__main__":
    try:
        code = main(sys.argv)
    except BaseException:
        traceback.print_exc()
        code = 1
    sys.exit(code)
