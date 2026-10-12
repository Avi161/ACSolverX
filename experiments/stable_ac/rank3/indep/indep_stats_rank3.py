#!/usr/bin/env python3
"""indep_stats_rank3.py

Independent recomputation of the published summary of the rank-3 brute-force
sweep, rank3_bf_ms640_b<B>_cap24_summary.json (B = 1000 and 10000), from the raw
result files (<stem>_control.jsonl, <stem>_L<n>.npz, <stem>_L<n>_inv.npz).

usage: python3 indep_stats_rank3.py RESULTS_DIR DATASET OUT_JSON [workers] [minutes]

Nothing is imported from the repository and the summarizer was not read. Every
number is derived from the definitions given to the tester; where a number has
no given definition the reading used is stated in the check's detail and in
indep_stats_rank3.md, and the check is named "...:inferred:...".

Exit code: 0 no mismatch, 3 at least one mismatch, 1 crash (or nothing at all
could be compared).

[unverified] This script has never been executed: the tester's rules allow only
an ast syntax check on the machine where it was written. Its first run is the
real run.
"""

import ast
import json
import math
import os
import sys
import time
import traceback

import numpy as np

SCRIPT = "indep_stats_rank3.py"
BUDGETS = (1000, 10000)
VIEWS = (100, 1000, 10000)
CAP = 24
MAX_L = 10
INV_MAX_L = 6
FLOAT_TOL = 1e-9
TIME_RTOL = 1e-5      # block_seconds is stored as float32
EX_PER_CHECK = 6
EX_TOTAL = 50
BIG = 1 << 40
I32_MAX = 2 ** 31 - 1

MEDIAN_READINGS = (
    "pooled over (presentation, word) cells where both solve",
    "per-presentation median over its solving words, then the median over presentations",
    "per-word median over the presentations where both solve, then the median over words",
)
MEDIAN_PRIMARY = 1

SKIP_RULES = (
    ("source", "a label, not a number"),
    ("views.*.subword_vs_other_within_bf",
     "relator-subword column: needs the summarizer's rule for which brute-force words count as a "
     "subword of a relator (linear or cyclic, with or without inverses), which the task does not define"),
    ("views.*.gained_presentations_priced",
     "needs the control search at control_file_budget, and the control file in RESULTS_DIR was not "
     "run at that budget"),
    ("control_at_larger_budgets", "needs a control file run at that budget, which is not in RESULTS_DIR"),
    ("relsub.vs_cov", "CoV column: needs the CoV result files"),
    ("relsub", "relator-subword column: computed from <stem>_relsub.jsonl with rules (denominators, which "
               "rows count as faster) that the task does not define; only the two row counts are checked, "
               "and only when that file is present"),
    ("inverse_pairs", "the _inv files needed to recompute it are absent or incomplete"),
)
DEFAULT_REASON = ("not recomputed: either an input was absent or the time box ran out (see the other "
                  "skipped entries of this budget), or no definition of it was available to this tester")


class _Missing(object):
    def __repr__(self):
        return "<absent>"


MISSING = _Missing()


# ----------------------------------------------------------------------------
# small helpers
# ----------------------------------------------------------------------------

def pstr(path):
    out = ""
    for k in path:
        if isinstance(k, int) and not isinstance(k, bool):
            out += "[%d]" % k
        else:
            out += ("." if out else "") + str(k)
    return out


def ppattern(path):
    out = ""
    for i, k in enumerate(path):
        if isinstance(k, int) and not isinstance(k, bool):
            out += "[*]"
        elif i == 1 and path[0] == "views":
            out += ".*"
        else:
            out += ("." if out else "") + str(k)
    return out


def jsonable(v):
    if isinstance(v, np.generic):
        v = v.item()
    if v is MISSING:
        return "<absent>"
    if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
        return None
    if isinstance(v, dict):
        return dict((str(k), jsonable(x)) for k, x in v.items())
    if isinstance(v, (list, tuple)):
        return [jsonable(x) for x in v]
    if isinstance(v, (set, frozenset)):
        return sorted(str(x) for x in v)
    if v is None or isinstance(v, (str, int, float, bool)):
        return v
    return str(v)


def is_missing_number(v):
    return v is None or (isinstance(v, float) and math.isnan(v))


def num_equal(pub, mine, tol=FLOAT_TOL, rtol=0.0):
    if isinstance(mine, np.generic):
        mine = mine.item()
    if isinstance(pub, np.generic):
        pub = pub.item()
    if is_missing_number(pub) or is_missing_number(mine):
        return is_missing_number(pub) and is_missing_number(mine)
    if isinstance(pub, bool) or isinstance(mine, bool):
        return isinstance(pub, bool) and isinstance(mine, bool) and pub == mine
    if not isinstance(pub, (int, float)) or not isinstance(mine, (int, float)):
        return False
    if isinstance(mine, int):
        return pub == mine
    return abs(float(pub) - mine) <= tol + rtol * abs(mine)


def fmean(a):
    a = np.asarray(a, dtype=np.float64)
    return float(a.mean()) if a.size else float("nan")


def fmedian(a):
    a = np.asarray(a, dtype=np.float64)
    return float(np.median(a)) if a.size else float("nan")


def inv_word(w):
    return w[::-1].swapcase()


def rotations(r):
    return set(r[i:] + r[:i] for i in range(len(r)))


def leaves(obj, path=()):
    if isinstance(obj, dict):
        for k, v in obj.items():
            for p in leaves(v, path + (k,)):
                yield p
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            for p in leaves(v, path + (i,)):
                yield p
    else:
        yield path


# ----------------------------------------------------------------------------
# report
# ----------------------------------------------------------------------------

class Summary(object):
    def __init__(self, obj, tag, budget):
        self.obj = obj
        self.tag = tag
        self.budget = budget
        self.seen = set()

    def get(self, path):
        cur = self.obj
        for k in path:
            if isinstance(cur, dict):
                if k not in cur:
                    return MISSING
                cur = cur[k]
            elif isinstance(cur, list):
                if not isinstance(k, int) or k < 0 or k >= len(cur):
                    return MISSING
                cur = cur[k]
            else:
                return MISSING
        return cur

    def mark(self, path):
        self.seen.add(tuple(path))


class Report(object):
    def __init__(self):
        self.checks = {}
        self.order = []
        self.skipped = []
        self.examples = []
        self.ex_count = {}
        self.info = {}
        self.errors = []
        self.summaries = []

    def check(self, name):
        c = self.checks.get(name)
        if c is None:
            c = {"name": name, "compared": 0, "mismatches": 0, "detail": []}
            self.checks[name] = c
            self.order.append(name)
        return c

    def note(self, name, text):
        c = self.check(name)
        if text not in c["detail"]:
            c["detail"].append(text)

    def skip(self, text):
        if text not in self.skipped:
            self.skipped.append(text)

    def record(self, name, ok, where, published, mine, budget=None):
        c = self.check(name)
        c["compared"] += 1
        if ok:
            return True
        c["mismatches"] += 1
        k = self.ex_count.get(name, 0)
        if k < EX_PER_CHECK and len(self.examples) < EX_TOTAL:
            self.ex_count[name] = k + 1
            self.examples.append({
                "check": name,
                "budget": budget,
                "where": where,
                "published": jsonable(published),
                "recomputed": jsonable(mine),
            })
        return False

    def cmp(self, summ, name, path, mine, tol=FLOAT_TOL, rtol=0.0, label=None, accept=None):
        """Compare one leaf of the summary JSON with a recomputed value."""
        pub = summ.get(path)
        if pub is MISSING:
            self.skip("%s: %s is absent from the summary JSON, so it was not compared"
                      % (summ.tag, ppattern(path)))
            return None
        summ.mark(path)
        where = pstr(path) + ((" (" + label + ")") if label else "")
        if accept is not None:
            ok = isinstance(pub, str) and pub in accept
        elif isinstance(mine, str):
            ok = (pub == mine)
        else:
            ok = num_equal(pub, mine, tol, rtol)
        return self.record(name, ok, where, pub, mine, budget=summ.budget)


# ----------------------------------------------------------------------------
# loading
# ----------------------------------------------------------------------------

class Control(object):
    pass


def load_control(path):
    rows = {}
    n_lines = 0
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            n_lines += 1
            rows[int(r["pres_id"])] = r
    c = Control()
    c.rows = rows
    c.n_lines = n_lines
    ids = sorted(rows)
    c.ids = np.array(ids, dtype=np.int64)
    c.csol = np.array([bool(rows[i]["solved"]) for i in ids], dtype=bool)
    c.cn = np.array([int(rows[i]["nodes_explored"]) for i in ids], dtype=np.int64)
    budgets = sorted(set(int(r["node_budget"]) for r in rows.values()
                         if isinstance(r.get("node_budget"), int) and not isinstance(r.get("node_budget"), bool)))
    c.budgets = budgets
    c.budget = budgets[0] if len(budgets) == 1 else None
    c.index = dict((int(i), k) for k, i in enumerate(ids))
    return c


class LenData(object):
    pass


def load_npz(path):
    d = LenData()
    with np.load(path, allow_pickle=False) as z:
        names = set(z.files)
        d.pres_ids = np.asarray(z["pres_ids"]).astype(np.int64).ravel()
        d.words = [str(w) for w in np.asarray(z["words"]).ravel().tolist()]
        d.nodes = np.asarray(z["nodes"]).astype(np.int64)
        d.path_len = np.asarray(z["path_len"])
        d.block_sum = None
        if "block_seconds" in names:
            d.block_sum = float(np.asarray(z["block_seconds"]).astype(np.float64).sum())
        d.meta = None
        if "meta" in names:
            try:
                m = np.asarray(z["meta"])
                d.meta = json.loads(str(m.item() if m.ndim == 0 else m.ravel()[0]))
            except Exception:
                d.meta = None
    if d.nodes.ndim != 2 or d.path_len.shape != d.nodes.shape:
        raise ValueError("nodes %r and path_len %r do not have the same 2-d shape"
                         % (d.nodes.shape, d.path_len.shape))
    if d.nodes.shape != (d.pres_ids.size, len(d.words)):
        raise ValueError("nodes %r does not match %d pres_ids x %d words"
                         % (d.nodes.shape, d.pres_ids.size, len(d.words)))
    if d.pres_ids.size > 1 and not bool(np.all(d.pres_ids[:-1] < d.pres_ids[1:])):
        order = np.argsort(d.pres_ids, kind="stable")
        d.pres_ids = d.pres_ids[order]
        d.nodes = d.nodes[order]
        d.path_len = d.path_len[order]
    d.solved = d.path_len >= 0
    return d


LETTERS = {1: "x", 2: "y", 3: "z", 4: "a", 5: "b", -1: "X", -2: "Y", -3: "Z", -4: "A", -5: "B"}


def load_dataset(path):
    rel = []
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                arr = json.loads(line)
            except ValueError:
                arr = ast.literal_eval(line)
            arr = [int(a) for a in arr]
            half = len(arr) // 2
            r1 = "".join(LETTERS[a] for a in arr[:half] if a != 0)
            r2 = "".join(LETTERS[a] for a in arr[half:] if a != 0)
            rel.append((r1, r2))
    return rel


# ----------------------------------------------------------------------------
# per-view state
# ----------------------------------------------------------------------------

class ViewState(object):
    def __init__(self, V, ctl):
        P = int(ctl.ids.size)
        self.V = V
        self.key = str(V)
        self.cs = ctl.csol & (ctl.cn <= V)       # control solved inside the view
        self.ncs = int(self.cs.sum())
        self.S = np.zeros(P, dtype=np.int64)     # words solved, all lengths so far
        self.F = np.zeros(P, dtype=np.int64)     # ... with fewer nodes than the control
        self.E = np.zeros(P, dtype=np.int64)     # ... with the same nodes
        self.nrot = np.zeros(P, dtype=np.int64)  # relator-rotation words
        self.Srot = np.zeros(P, dtype=np.int64)
        self.Frot = np.zeros(P, dtype=np.int64)
        self.Erot = np.zeros(P, dtype=np.int64)
        self.Ktot = 0
        self.anysol = np.zeros(P, dtype=bool)
        self.minn = np.full(P, BIG, dtype=np.int64)
        self.minn_nr = np.full(P, BIG, dtype=np.int64)
        self.cum = np.zeros(P, dtype=np.int64)   # nodes spent running the words in file order
        self.done = np.zeros(P, dtype=bool)
        self.rot = {"rows": 0, "solved": 0, "faster": 0, "equal": 0, "slower": 0, "extra_sum": 0, "both": 0}
        self.beat = 0
        self.match = 0
        self.per_word = {}
        self.bl = {}
        self.orc = {}
        self.stats = {}
        self.gp_rows = None
        self.gp_cells = {}


def median_candidates(nodes, sol, cs, cn):
    """Three readings of 'median extra nodes' on control-solved presentations."""
    nan = float("nan")
    sub = np.flatnonzero(cs)
    if sub.size == 0:
        return (nan, nan, nan)
    m = sol[sub]
    if not bool(m.any()):
        return (nan, nan, nan)
    e = (nodes[sub] - cn[sub][:, None]).astype(np.int32)
    pooled = float(np.median(e[m]))
    sent = np.int32(I32_MAX)
    a = np.where(m, e, sent)
    a.sort(axis=1)
    cnt = m.sum(axis=1)
    rows = np.flatnonzero(cnt > 0)
    lo = (cnt[rows] - 1) // 2
    hi = cnt[rows] // 2
    rmed = (a[rows, lo].astype(np.float64) + a[rows, hi].astype(np.float64)) / 2.0
    per_pres = float(np.median(rmed))
    a = np.where(m, e, sent)
    a.sort(axis=0)
    cnt = m.sum(axis=0)
    cols = np.flatnonzero(cnt > 0)
    lo = (cnt[cols] - 1) // 2
    hi = cnt[cols] // 2
    cmed = (a[lo, cols].astype(np.float64) + a[hi, cols].astype(np.float64)) / 2.0
    per_word = float(np.median(cmed))
    return (pooled, per_pres, per_word)


# ----------------------------------------------------------------------------
# one budget
# ----------------------------------------------------------------------------

def run_budget(rep, rdir, B, controls, dataset_rel, deadline, results):
    stem = "rank3_bf_ms640_b%d_cap%d" % (B, CAP)
    tag = "b%d" % B

    present = {}
    for n in range(1, MAX_L + 1):
        present[n] = os.path.isfile(os.path.join(rdir, "%s_L%d.npz" % (stem, n)))
        if not present[n]:
            rep.skip("%s_L%d.npz is absent" % (stem, n))
    inv_present = {}
    for n in range(1, INV_MAX_L + 1):
        inv_present[n] = os.path.isfile(os.path.join(rdir, "%s_L%d_inv.npz" % (stem, n)))
        if not inv_present[n]:
            rep.skip("%s_L%d_inv.npz is absent" % (stem, n))

    sum_path = os.path.join(rdir, stem + "_summary.json")
    if not os.path.isfile(sum_path):
        rep.skip("%s_summary.json is absent: nothing is under test at budget %d" % (stem, B))
        return
    ctl = controls.get(B)
    if ctl is None:
        rep.skip("%s_control.jsonl is absent, empty or unreadable: nothing at budget %d could be recomputed"
                 % (stem, B))
        return
    with open(sum_path, "r") as f:
        summ = Summary(json.load(f), tag, B)
    rep.summaries.append(summ)

    P = int(ctl.ids.size)
    cn = ctl.cn
    cncol = cn[:, None]
    even = (ctl.ids % 2) == 0

    H = tag + ":header"
    CI = tag + ":control_equals_null_start"
    FR = tag + ":oracle_some_word_faster_than_control"
    IP = tag + ":inverse_pairs"
    ME = tag + ":inferred:median_extra_nodes"
    TM = tag + ":inferred:timing"
    CL = tag + ":inferred:control_at_larger_budgets"

    def nm(vs, what, inferred=False):
        return "%s:%sview%d:%s" % (tag, "inferred:" if inferred else "", vs.V, what)

    rep.info[tag + ":control_file_node_budget"] = ctl.budgets

    # ---- header ------------------------------------------------------------
    rep.cmp(summ, H, ("node_budget",), B, label="the budget in the file name")
    rep.cmp(summ, H, ("max_relator_length_cap",), CAP, label="the cap in the file name")
    rep.cmp(summ, H, ("n_presentations",), P, label="distinct pres_id in the control file")
    rep.record(H, ctl.n_lines == P, "%s_control.jsonl has one row per pres_id" % stem,
               "one row per presentation", "%d rows, %d distinct pres_id" % (ctl.n_lines, P), budget=B)

    contig = 0
    for n in range(1, MAX_L + 1):
        if present[n]:
            contig = n
        else:
            break
    # max_len is the summarizer's choice of lengths, not a statistic: it is checked through the rows
    # and totals that depend on it. Files beyond it are reported as skipped, not as a mismatch.
    pub_max = summ.get(("max_len",))
    rep.info[tag + ":max_len"] = {"summary": jsonable(pub_max), "L_files_present_without_a_gap_to": contig}
    if isinstance(pub_max, int) and not isinstance(pub_max, bool) and 1 <= pub_max <= MAX_L:
        use_max = pub_max
        summ.mark(("max_len",))
        # Review: no pass-only record. max_len cannot fail here (a shorter summary is a choice, a longer
        # one only means absent files), so it is listed as not checked instead of counted as compared.
        rep.skip("%s summary: max_len (%d) not checked: it is the summarizer's choice of lengths, not a "
                 "statistic; RESULTS_DIR has L files without a gap for lengths 1..%d"
                 % (tag, pub_max, contig))
        if pub_max < contig:
            rep.note(H, "max_len: the summary covers lengths 1..%d but RESULTS_DIR has L files without a gap "
                        "to %d (a summary made before the later files, or on purpose over fewer lengths); it "
                        "was checked over its own lengths" % (pub_max, contig))
    else:
        if pub_max is not MISSING:
            summ.mark(("max_len",))
        rep.record(H, False, "max_len", pub_max, "an integer between 1 and %d" % MAX_L, budget=B)
        use_max = contig
        rep.note(H, "the summary's max_len is unusable; lengths 1..%d were used" % contig)
    for n in range(use_max + 1, MAX_L + 1):
        if present[n]:
            rep.skip("%s_L%d.npz is present but beyond the summary's max_len (%d): not used"
                     % (stem, n, use_max))

    pub_views = summ.get(("views",))
    pub_keys = sorted(pub_views.keys(), key=str) if isinstance(pub_views, dict) else []
    exp_keys = [str(V) for V in VIEWS if V <= B]
    rep.record(H, set(pub_keys) == set(exp_keys), "views (its keys)", pub_keys, exp_keys, budget=B)
    views = [ViewState(V, ctl) for V in VIEWS if V <= B and str(V) in pub_keys]

    for vs in views:
        rows = summ.get(("views", vs.key, "by_length"))
        if isinstance(rows, list):
            for i, r in enumerate(rows):
                if isinstance(r, dict) and isinstance(r.get("len"), int):
                    vs.bl[r["len"]] = i
                    summ.mark(("views", vs.key, "by_length", i, "len"))
        rep.record(H, sorted(vs.bl) == list(range(1, use_max + 1)),
                   "views.%s.by_length (the len of its rows)" % vs.key,
                   sorted(vs.bl), list(range(1, use_max + 1)), budget=B)
        rows = summ.get(("views", vs.key, "oracle"))
        if isinstance(rows, list):
            for i, r in enumerate(rows):
                if isinstance(r, dict) and isinstance(r.get("max_len"), int):
                    vs.orc[r["max_len"]] = i
                    summ.mark(("views", vs.key, "oracle", i, "max_len"))
        rep.record(H, sorted(vs.orc) == list(range(1, use_max + 1)),
                   "views.%s.oracle (the max_len of its rows)" % vs.key,
                   sorted(vs.orc), list(range(1, use_max + 1)), budget=B)
        rep.cmp(summ, nm(vs, "by_length"), ("views", vs.key, "control_solved"), vs.ncs,
                label="control solved and nodes <= %d" % vs.V)
        g = summ.get(("views", vs.key, "gained_presentations_priced", "rows"))
        vs.gp_rows = g if isinstance(g, list) else None

    # ---- the control against the null stabilization (claimed in the .md) ----
    trip = (("solved", "nodes_explored", "path_length"),
            ("n2_solved", "n2_nodes", "n2_path_length"),
            ("null_solved", "null_nodes", "null_path_length"))
    have = all(all(k in r for t in trip for k in t) for r in ctl.rows.values())
    if have:
        def triple(r, keys):
            # Review: an unsolved search has no path; null and -1 both mean that, so the path length is
            # only compared when the search is solved (the example CSV prints it empty for unsolved rows).
            s = r[keys[0]]
            return [s, r[keys[1]], r[keys[2]] if s else None]

        for i in ctl.ids.tolist():
            r = ctl.rows[i]
            base = triple(r, trip[0])
            for label, keys in (("n2_*", trip[1]), ("null_*", trip[2])):
                other = triple(r, keys)
                rep.record(CI, other == base,
                           "%s_control.jsonl pres_id %d: %s against (solved, nodes_explored, path_length)"
                           % (stem, i, label), base, other, budget=B)
        rep.note(CI, "the .md says the control is identical to the null stabilization: (solved, nodes, "
                     "path_length) of the 2-generator control compared with the n2_* and the null_* "
                     "columns of the same row; 'published' in an example is the control triple; the path "
                     "length is compared only when the search is solved (null and -1 both mean no path)")
    else:
        rep.skip("%s: the control file has no n2_*/null_* columns, so 'control identical to the null "
                 "stabilization' was not checked" % tag)

    # ---- relators (for the relator-rotation columns) -------------------------
    rel_ok = True
    rots = []        # per presentation: {length: set of words w with w or w^-1 a rotation of r1 or r2}
    rots_alt = []    # same without the inverses (alternative reading, counted for the detail only)
    for i in ctl.ids.tolist():
        r = ctl.rows[i]
        r1, r2 = r.get("r1"), r.get("r2")
        if not (isinstance(r1, str) and isinstance(r2, str)):
            if dataset_rel is not None and 0 <= i < len(dataset_rel):
                r1, r2 = dataset_rel[i]
            else:
                rel_ok = False
                r1, r2 = "", ""
        a = {}
        b = {}
        for rr in (r1, r2):
            if not rr:
                continue
            for s in rotations(rr):
                b.setdefault(len(s), set()).add(s)
                a.setdefault(len(s), set()).add(s)
                a.setdefault(len(s), set()).add(inv_word(s))
        rots.append(a)
        rots_alt.append(b)
    if not rel_ok:
        rep.skip("%s: r1/r2 are not available for every presentation, so the relator-rotation columns "
                 "were not checked" % tag)
    rot_alt_rows = 0

    # ---- one length file at a time -----------------------------------------
    chain_ok = True
    colmaps = {}
    block = {}
    inv_stats = {}
    inv_diffs = {}
    faster_rows = []
    nr_rows = []
    med_rows = []
    loaded = []

    # the control file with the largest budget (for the control columns of gained_presentations_priced)
    big = None
    big_cap = 0
    big_B = None
    for B2 in sorted(controls):
        c2 = controls[B2]
        if c2 is None:
            continue
        cap2 = c2.budget if c2.budget is not None else B2
        if cap2 > big_cap:
            big, big_cap, big_B = c2, cap2, B2

    for n in range(1, use_max + 1):
        fname = "%s_L%d.npz" % (stem, n)
        if not present[n]:
            chain_ok = False
            rep.skip("%s: length %d is in the summary but %s is absent: its by_length rows and every "
                     "cumulative number (oracle rows from %d on, overall, price, top_words, fixed word, "
                     "relator rotations) were not compared" % (tag, n, fname, n))
            continue
        if time.time() > deadline:
            chain_ok = False
            rep.skip("%s: the time box ran out before %s; lengths %d..%d and the cumulative numbers were "
                     "not compared" % (tag, fname, n, use_max))
            break
        try:
            d = load_npz(os.path.join(rdir, fname))
        except Exception as exc:
            chain_ok = False
            rep.errors.append("%s: could not be loaded: %r" % (fname, exc))
            continue
        if d.pres_ids.size != P or not np.array_equal(d.pres_ids, ctl.ids):
            chain_ok = False
            rep.record(H, False, "%s pres_ids" % fname, "the %d pres_id of the control file" % P,
                       "%d pres_id, not the same set" % int(d.pres_ids.size), budget=B)
            continue

        loaded.append(n)
        K = len(d.words)
        Kf = float(K)
        nodes = d.nodes
        solved = d.solved
        n_distinct = len(set(d.words))
        fam_ok = (K == 2 * 3 ** (n - 1)) and n_distinct == K and all(len(w) == n for w in d.words)
        rep.record(H, fam_ok, "%s word family" % fname,
                   "%d distinct words of length %d" % (2 * 3 ** (n - 1), n),
                   "%d words, %d distinct, %d of length %d"
                   % (K, n_distinct, sum(1 for w in d.words if len(w) == n), n), budget=B)
        if isinstance(d.meta, dict):
            if "node_budget" in d.meta:
                rep.record(H, num_equal(summ.get(("node_budget",)), d.meta["node_budget"]),
                           "node_budget against meta.node_budget of %s" % fname,
                           summ.get(("node_budget",)), d.meta["node_budget"], budget=B)
            if "max_relator_length_cap" in d.meta:
                rep.record(H, num_equal(summ.get(("max_relator_length_cap",)), d.meta["max_relator_length_cap"]),
                           "max_relator_length_cap against meta of %s" % fname,
                           summ.get(("max_relator_length_cap",)), d.meta["max_relator_length_cap"], budget=B)
        col = dict((w, k) for k, w in enumerate(d.words))
        colmaps[n] = col
        block[n] = (d.block_sum, K)

        # relator-rotation cells of this length
        pairs = set()
        if rel_ok:
            for p in range(P):
                ss = rots[p].get(n)
                if ss:
                    for s in ss:
                        k = col.get(s)
                        if k is not None:
                            pairs.add((p, k))
                ss = rots_alt[p].get(n)
                if ss:
                    rot_alt_rows += sum(1 for s in ss if s in col)
        if pairs:
            arr = np.array(sorted(pairs), dtype=np.int64)
            rp = arr[:, 0]
            rk = arr[:, 1]
        else:
            rp = np.zeros(0, dtype=np.int64)
            rk = np.zeros(0, dtype=np.int64)
        nrot_p = np.bincount(rp, minlength=P).astype(np.int64)

        lt_full = nodes < cncol
        eq_full = nodes == cncol

        for vs in views:
            V = vs.V
            cs = vs.cs
            sol = solved & (nodes <= V)
            lt = sol & lt_full
            eq = sol & eq_full
            S = sol.sum(axis=1).astype(np.int64)
            F = lt.sum(axis=1).astype(np.int64)
            E = eq.sum(axis=1).astype(np.int64)
            G = S - F - E
            W = sol.sum(axis=0).astype(np.int64)
            wmax = int(W.max())
            st = {
                "n_words": int(K),
                "solve_rate": fmean(S / Kf),
                "solve_rate_control_solved": fmean(S[cs] / Kf),
                "solve_rate_control_unsolved": fmean(S[~cs] / Kf),
                "faster": fmean(F[cs] / Kf),
                "equal": fmean(E[cs] / Kf),
                "slower": fmean(G[cs] / Kf),
                "lost": fmean((K - S[cs]) / Kf),
                "mean_presentations_per_word": float(W.mean()),
                "best_single_word_solves": wmax,
            }
            vs.stats[n] = st
            n_beat = int((W > vs.ncs).sum())
            vs.beat += n_beat
            vs.match += int((W == vs.ncs).sum())
            i = vs.bl.get(n)
            lab = "len=%d" % n
            if i is not None:
                base = ("views", vs.key, "by_length", i)
                for key in ("n_words", "solve_rate", "solve_rate_control_solved",
                            "solve_rate_control_unsolved", "faster", "equal", "slower", "lost",
                            "mean_presentations_per_word", "best_single_word_solves"):
                    rep.cmp(summ, nm(vs, "by_length"), base + (key,), st[key], label=lab)
                best = set(d.words[k] for k in np.flatnonzero(W == wmax).tolist())
                rep.cmp(summ, nm(vs, "by_length"), base + ("best_single_word",),
                        {"words_with_the_most_solves": sorted(best)[:8], "solves": wmax},
                        label=lab, accept=best)
                rep.cmp(summ, nm(vs, "words_vs_control", True), base + ("words_beating_control",),
                        n_beat, label=lab)
                if d.block_sum is not None:
                    rep.cmp(summ, TM, base + ("ms_per_search",), 1000.0 * d.block_sum / (P * Kf),
                            rtol=TIME_RTOL, label=lab)

            Wcs = sol[cs].sum(axis=0).astype(np.int64)
            Wfast = lt[cs].sum(axis=0).astype(np.int64)
            Weven = sol[even].sum(axis=0).astype(np.int64)
            vs.per_word[n] = (W, Wcs, Wfast, Weven)

            # cumulative state over lengths 1..n
            vs.S += S
            vs.F += F
            vs.E += E
            vs.Ktot += K
            vs.anysol |= (S > 0)
            tmp = np.where(sol, nodes, BIG)
            vs.minn = np.minimum(vs.minn, tmp.min(axis=1))
            if rp.size:
                tmp[rp, rk] = BIG
            vs.minn_nr = np.minimum(vs.minn_nr, tmp.min(axis=1))
            del tmp

            if rp.size:
                sol_r = sol[rp, rk]
                n_r = nodes[rp, rk]
                cn_r = cn[rp]
                cs_r = cs[rp]
                lt_r = sol_r & (n_r < cn_r)
                eq_r = sol_r & (n_r == cn_r)
                gt_r = sol_r & (n_r > cn_r)
                vs.nrot += nrot_p
                vs.Srot += np.bincount(rp[sol_r], minlength=P).astype(np.int64)
                vs.Frot += np.bincount(rp[lt_r], minlength=P).astype(np.int64)
                vs.Erot += np.bincount(rp[eq_r], minlength=P).astype(np.int64)
                both_r = sol_r & cs_r
                vs.rot["rows"] += int(rp.size)
                vs.rot["solved"] += int(sol_r.sum())
                vs.rot["faster"] += int((lt_r & cs_r).sum())
                vs.rot["equal"] += int((eq_r & cs_r).sum())
                vs.rot["slower"] += int((gt_r & cs_r).sum())
                vs.rot["extra_sum"] += int((n_r[both_r] - cn_r[both_r]).sum())
                vs.rot["both"] += int(both_r.sum())

            # the words run in file order (length by length) until the first solve
            todo = np.flatnonzero(~vs.done)
            if todo.size:
                ssol = sol[todo]
                snod = nodes[todo]
                has = ssol.any(axis=1)
                first = ssol.argmax(axis=1)
                cost = np.minimum(snod, V)
                before = np.arange(K)[None, :] < first[:, None]
                part = (cost * before).sum(axis=1) + snod[np.arange(todo.size), first]
                full = cost.sum(axis=1)
                vs.cum[todo] += np.where(has, part, full)
                vs.done[todo] = has
                del ssol, snod, cost, before

            # the cells of the best_word named in gained_presentations_priced
            if vs.gp_rows:
                for gi, r in enumerate(vs.gp_rows):
                    if not isinstance(r, dict):
                        continue
                    w = r.get("best_word")
                    pid = r.get("pres_id")
                    if isinstance(w, str) and len(w) == n and isinstance(pid, int) and pid in ctl.index:
                        k = col.get(w)
                        if k is not None:
                            p = ctl.index[pid]
                            vs.gp_cells[gi] = (bool(sol[p, k]), int(nodes[p, k]))

            # oracle row "all words of length <= n"
            if chain_ok:
                j = vs.orc.get(n)
                if j is not None:
                    base = ("views", vs.key, "oracle", j)
                    lab2 = "max_len=%d" % n
                    gained = int((vs.anysol & ~cs).sum())
                    rep.cmp(summ, nm(vs, "oracle"), base + ("words",), int(vs.Ktot), label=lab2)
                    rep.cmp(summ, nm(vs, "oracle"), base + ("solved_by_some_word",),
                            int(vs.anysol.sum()), label=lab2)
                    rep.cmp(summ, nm(vs, "oracle"), base + ("gained_over_control",), gained, label=lab2)
                    rep.cmp(summ, nm(vs, "oracle"), base + ("control_solved_lost_by_every_word",),
                            int((cs & ~vs.anysol).sum()), label=lab2)
                    strict = int((cs & (vs.minn < cn)).sum())
                    fpath = base + ("some_word_faster_than_control",)
                    pubv = summ.get(fpath)
                    if pubv is not MISSING:
                        summ.mark(fpath)
                        faster_rows.append((vs.key, n, j, pubv, strict, strict + gained))
                    if rel_ok:
                        npath = base + ("some_non_rotation_word_faster",)
                        pubn = summ.get(npath)
                        if pubn is not MISSING:
                            summ.mark(npath)
                            strict_nr = int((cs & (vs.minn_nr < cn)).sum())
                            incl_nr = strict_nr + int((~cs & (vs.minn_nr < BIG)).sum())
                            nr_rows.append((vs, n, j, pubn, strict_nr, incl_nr))

            # median extra nodes: three readings
            if i is not None:
                mpath = ("views", vs.key, "by_length", i, "median_extra_nodes")
                pubm = summ.get(mpath)
                if pubm is not MISSING and time.time() <= deadline:
                    try:
                        cands = median_candidates(nodes, sol, cs, cn)
                    except Exception as exc:
                        cands = None
                        rep.errors.append("%s view %d len %d: median_extra_nodes readings crashed: %r"
                                          % (tag, V, n, exc))
                    if cands is not None:
                        summ.mark(mpath)
                        med_rows.append((vs.key, n, i, pubm, cands))
            del sol, lt, eq

        del lt_full, eq_full

        # w against w^-1, at the file budget
        if n <= INV_MAX_L and inv_present.get(n):
            iname = "%s_L%d_inv.npz" % (stem, n)
            try:
                di = load_npz(os.path.join(rdir, iname))
            except Exception as exc:
                di = None
                rep.errors.append("%s: could not be loaded: %r" % (iname, exc))
            if di is not None:
                if di.nodes.shape != nodes.shape or not np.array_equal(di.pres_ids, ctl.ids):
                    rep.record(IP, False, "%s shape and pres_ids" % iname,
                               "the shape and pres_ids of %s" % fname,
                               "shape %r" % (di.nodes.shape,), budget=B)
                else:
                    bad = sum(1 for a, b in zip(d.words, di.words) if inv_word(a) != b)
                    rep.record(IP, bad == 0,
                               "%s words are the inverses of the %s words, in the same order" % (iname, fname),
                               "0 of %d words out of place" % K, "%d of %d words out of place" % (bad, K),
                               budget=B)
                    same_sn = (solved == di.solved) & (nodes == di.nodes)
                    both = solved & di.solved
                    inv_stats[n] = {
                        "pairs": int(P * K),
                        "identical": int(same_sn.sum()),
                        "identical_with_path_len": int((same_sn & (d.path_len == di.path_len)).sum()),
                        "differs": int((solved != di.solved).sum()),
                    }
                    inv_diffs[n] = np.abs(nodes[both] - di.nodes[both])
                del di
        del d, nodes, solved

    rep.info[tag + ":lengths_recomputed"] = loaded

    # ---- totals over the lengths ---------------------------------------------
    if len(block) == use_max and use_max >= 1:
        ktot = int(sum(block[m][1] for m in block))
        rep.cmp(summ, H, ("n_words_per_presentation",), ktot, label="sum of the word counts of L1..L%d" % use_max)
        rep.cmp(summ, H, ("n_searches",), int(ktot * P), label="presentations x words")
        if all(block[m][0] is not None for m in block):
            rep.cmp(summ, TM, ("core_seconds",), float(sum(block[m][0] for m in sorted(block))),
                    rtol=TIME_RTOL, label="sum of block_seconds over L1..L%d" % use_max)
    rep.note(TM, "inferred: ms_per_search = 1000 * sum(block_seconds of L<n>.npz) / (presentations * "
                 "words); core_seconds = that sum over the main L files (not the _inv files); relative "
                 "tolerance %g because block_seconds is float32" % TIME_RTOL)

    # ---- cumulative numbers per view -----------------------------------------
    if chain_ok and views and len(loaded) == use_max:
        for vs in views:
            cs = vs.cs
            Kt = float(vs.Ktot)

            # overall
            ob = ("views", vs.key, "overall")
            G = vs.S - vs.F - vs.E
            rep.cmp(summ, nm(vs, "overall"), ob + ("faster",), fmean(vs.F[cs] / Kt))
            rep.cmp(summ, nm(vs, "overall"), ob + ("equal",), fmean(vs.E[cs] / Kt))
            rep.cmp(summ, nm(vs, "overall"), ob + ("slower",), fmean(G[cs] / Kt))
            rep.cmp(summ, nm(vs, "overall"), ob + ("lost",), fmean((vs.Ktot - vs.S[cs]) / Kt))
            rep.cmp(summ, nm(vs, "overall"), ob + ("solve_rate",), fmean(vs.S / Kt))
            rep.cmp(summ, nm(vs, "overall"), ob + ("solve_rate_control_unsolved",), fmean(vs.S[~cs] / Kt))

            # one fixed word against the control
            WC = nm(vs, "words_vs_control", True)
            rep.cmp(summ, WC, ("views", vs.key, "words_beating_control"), int(vs.beat))
            rep.cmp(summ, WC, ("views", vs.key, "words_matching_control"), int(vs.match))
            rep.note(WC, "inferred from the .md: number of words whose solved count over all presentations "
                         "is larger than (beating) or equal to (matching) the control's solved count")

            # relator rotations
            if rel_ok:
                RR = nm(vs, "relator_rotations", True)
                rb = ("views", vs.key, "relator_rotations")
                rr = vs.rot
                rep.cmp(summ, RR, rb + ("rows",), int(rr["rows"]))
                rep.cmp(summ, RR, rb + ("solved",), int(rr["solved"]))
                rep.cmp(summ, RR, rb + ("faster",), int(rr["faster"]))
                rep.cmp(summ, RR, rb + ("equal",), int(rr["equal"]))
                rep.cmp(summ, RR, rb + ("slower",), int(rr["slower"]))
                rep.cmp(summ, RR, rb + ("mean_extra_nodes_when_both_solve",),
                        (rr["extra_sum"] / float(rr["both"])) if rr["both"] else float("nan"))
                wb = ("views", vs.key, "overall_without_relator_rotations")
                den = (vs.Ktot - vs.nrot).astype(np.float64)
                Sn = vs.S - vs.Srot
                Fn = vs.F - vs.Frot
                En = vs.E - vs.Erot
                Gn = Sn - Fn - En
                with np.errstate(divide="ignore", invalid="ignore"):
                    rep.cmp(summ, RR, wb + ("faster",), fmean((Fn / den)[cs]))
                    rep.cmp(summ, RR, wb + ("equal",), fmean((En / den)[cs]))
                    rep.cmp(summ, RR, wb + ("slower",), fmean((Gn / den)[cs]))
                    rep.cmp(summ, RR, wb + ("lost",), fmean(((den - Sn) / den)[cs]))
                rep.note(RR, "inferred: a (presentation, word) pair is a relator rotation when w or w^-1 is a "
                             "cyclic rotation of r1 or r2 (the family keeps one of w, w^-1); rows = all such "
                             "pairs, solved = those solved in the view, faster/equal/slower only where the "
                             "control solves; 'without' = per-presentation fractions over the other words, "
                             "mean over control-solved presentations. Rows under the alternative reading "
                             "(only w itself a rotation): %d" % rot_alt_rows)

            # top words
            tw = summ.get(("views", vs.key, "top_words"))
            if isinstance(tw, list) and tw:
                TW = nm(vs, "top_words", True)
                allW = np.concatenate([vs.per_word[m][0] for m in range(1, use_max + 1)])
                top = np.sort(allW)[::-1]
                for ti, r in enumerate(tw):
                    base = ("views", vs.key, "top_words", ti)
                    if not isinstance(r, dict) or not isinstance(r.get("word"), str):
                        continue
                    w = r["word"]
                    summ.mark(base + ("word",))
                    k = colmaps.get(len(w), {}).get(w)
                    lab = "word=%s" % w
                    if k is None:
                        rep.record(TW, False, pstr(base + ("word",)), w,
                                   "not a word of the family of lengths 1..%d" % use_max, budget=B)
                        continue
                    W, Wcs, Wfast, Weven = vs.per_word[len(w)]
                    rep.cmp(summ, TW, base + ("len",), len(w), label=lab)
                    rep.cmp(summ, TW, base + ("solved",), int(W[k]), label=lab)
                    rep.cmp(summ, TW, base + ("gained",), int(W[k] - Wcs[k]), label=lab)
                    rep.cmp(summ, TW, base + ("lost",), int(vs.ncs - Wcs[k]), label=lab)
                    rep.cmp(summ, TW, base + ("faster",), int(Wfast[k]), label=lab)
                    if ti < top.size:
                        rep.record(TW, num_equal(r.get("solved"), int(top[ti])),
                                   pstr(base + ("solved",)) + " (is the %d-th largest solved count of any word)"
                                   % (ti + 1), r.get("solved"), int(top[ti]), budget=B)
                rep.note(TW, "inferred: solved = presentations the word solves; gained = solved where the "
                             "control does not; lost = control-solved presentations the word does not solve; "
                             "faster = control-solved presentations it solves with fewer nodes; the list is "
                             "the words with the largest solved counts, in non-increasing order")

            # one word chosen on half of the presentations, scored on the other half
            fw = summ.get(("views", vs.key, "fixed_word_cross_validated"))
            if isinstance(fw, list) and fw:
                FW = nm(vs, "fixed_word_cross_validated", True)
                n_even = int(even.sum())
                n_odd = P - n_even
                cs_even = int((cs & even).sum())
                cs_odd = vs.ncs - cs_even
                max_even = max(int(vs.per_word[m][3].max()) for m in range(1, use_max + 1))
                max_odd = max(int((vs.per_word[m][0] - vs.per_word[m][3]).max()) for m in range(1, use_max + 1))
                for fi, r in enumerate(fw):
                    base = ("views", vs.key, "fixed_word_cross_validated", fi)
                    if not isinstance(r, dict):
                        continue
                    fold = r.get("fold")
                    w = r.get("word")
                    if fold not in ("even->odd", "odd->even") or not isinstance(w, str):
                        rep.skip("%s: %s has an unknown fold label %r: not compared"
                                 % (tag, pstr(base), fold))
                        continue
                    summ.mark(base + ("fold",))
                    summ.mark(base + ("word",))
                    k = colmaps.get(len(w), {}).get(w)
                    if k is None:
                        rep.record(FW, False, pstr(base + ("word",)), w,
                                   "not a word of the family of lengths 1..%d" % use_max, budget=B)
                        continue
                    W, Wcs, Wfast, Weven = vs.per_word[len(w)]
                    we = int(Weven[k])
                    wo = int(W[k] - Weven[k])
                    if fold == "even->odd":
                        tr, te, trc, tec, ten, best_tr = we, wo, cs_even, cs_odd, n_odd, max_even
                    else:
                        tr, te, trc, tec, ten, best_tr = wo, we, cs_odd, cs_even, n_even, max_odd
                    lab = "fold=%s word=%s" % (fold, w)
                    rep.cmp(summ, FW, base + ("train_solved",), tr, label=lab)
                    rep.cmp(summ, FW, base + ("train_control",), trc, label=lab)
                    rep.cmp(summ, FW, base + ("test_solved",), te, label=lab)
                    rep.cmp(summ, FW, base + ("test_control",), tec, label=lab)
                    rep.cmp(summ, FW, base + ("test_presentations",), ten, label=lab)
                    rep.record(FW, tr == best_tr,
                               pstr(base + ("word",)) + " (has the largest train count of any word; %s)" % lab,
                               "%s with train count %d" % (w, tr), "largest train count %d" % best_tr, budget=B)
                rep.note(FW, "inferred: even/odd is the parity of pres_id; the word is one with the largest "
                             "solved count on the train half (ties accepted); *_control is the control's "
                             "solved count on that half")

            # price of the oracle
            PR = nm(vs, "price", True)
            pb = ("views", vs.key, "price")
            rep.cmp(summ, PR, pb + ("solved_in_shortlex_order",), int(vs.done.sum()))
            rep.cmp(summ, PR, pb + ("median_nodes_to_first_solve",), fmedian(vs.cum[vs.done]))
            rep.cmp(summ, PR, pb + ("presentations_where_shortlex_beats_control",),
                    int((vs.done & (~cs | (vs.cum < cn))).sum()))
            med_all = fmedian(cn[vs.done])
            med_cs = fmedian(cn[vs.done & cs])
            # Review: the checked reading is now "presentations the run solves AND the control solves in
            # the view". The example b1000 summary rules the other one out at 100 nodes: the control's
            # nodes there have 206 values <= 7, 250 <= 8 and 295 <= 9 (example per_presentation.csv), so
            # the median over the 455 control-solved ones is 8 (published: 8.0) and over all 514 it is 9.
            rep.cmp(summ, PR, pb + ("control_nodes_median_same_presentations",), med_cs,
                    label="median of the control's nodes over the presentations both the run and the "
                          "control solve in the view")
            rep.note(PR, "inferred: words run in the order of the files (L1, L2, ... and inside a file the "
                         "column order); a search that does not solve inside the view costs min(nodes, view), "
                         "the first solving one costs its nodes; the median is over the presentations solved; "
                         "'beats' = fewer nodes than the control, or solved where the control is not. "
                         "control_nodes_median_same_presentations: checked reading = median of the control's "
                         "nodes over the presentations the run solves and the control solves in the view "
                         "(%s); alternative, over every presentation the run solves: %s"
                     % (jsonable(med_cs), jsonable(med_all)))

            gb = ("views", vs.key, "gained_presentations_priced")
            g = summ.get(gb)
            if isinstance(g, dict):
                gained_idx = np.flatnonzero(vs.anysol & ~cs)
                gained_ids = set(int(x) for x in ctl.ids[gained_idx].tolist())
                rep.cmp(summ, PR, gb + ("gained_at_this_budget",), len(gained_ids))
                grows = g.get("rows")
                if isinstance(grows, list):
                    pub_ids = [r.get("pres_id") for r in grows if isinstance(r, dict)]
                    pub_ok = all(isinstance(x, int) for x in pub_ids)
                    rep.record(PR, pub_ok and len(pub_ids) == len(set(pub_ids)) and set(pub_ids) == gained_ids,
                               pstr(gb + ("rows",)) + " (the set of pres_id)",
                               pub_ids[:40], sorted(gained_ids)[:40], budget=B)
                    full = (ctl.budget is not None and num_equal(g.get("control_file_budget"), int(ctl.budget)))
                    for gi, r in enumerate(grows):
                        if not isinstance(r, dict):
                            continue
                        pid = r.get("pres_id")
                        rbase = gb + ("rows", gi)
                        if not isinstance(pid, int) or pid not in ctl.index:
                            continue
                        summ.mark(rbase + ("pres_id",))
                        p = ctl.index[pid]
                        lab = "pres_id=%d" % pid
                        mn = int(vs.minn[p]) if int(vs.minn[p]) < BIG else None
                        rep.cmp(summ, PR, rbase + ("best_word_nodes",), mn, label=lab)
                        rep.cmp(summ, PR, rbase + ("shortlex_nodes",),
                                int(vs.cum[p]) if bool(vs.done[p]) else None, label=lab)
                        cell = vs.gp_cells.get(gi)
                        if rbase + ("best_word",) not in summ.seen and summ.get(rbase + ("best_word",)) is not MISSING:
                            summ.mark(rbase + ("best_word",))
                            okw = (cell is not None and cell[0] and mn is not None and cell[1] == mn)
                            rep.record(PR, okw,
                                       pstr(rbase + ("best_word",)) + " (solves with the fewest nodes of any word; %s)" % lab,
                                       r.get("best_word"),
                                       {"fewest_nodes_of_any_word": mn,
                                        "this_word": None if cell is None else {"solved_in_view": cell[0], "nodes": cell[1]}},
                                       budget=B)
                        if full:
                            rep.cmp(summ, PR, rbase + ("control_solved",), bool(ctl.csol[p]), label=lab)
                            rep.cmp(summ, PR, rbase + ("control_nodes",), int(cn[p]), label=lab)
                        elif big is not None and pid in big.index:
                            # prefix property of the control: a control search that solves in N nodes
                            # at a larger budget must show the same N in any control file whose
                            # budget is at least N.
                            GC = nm(vs, "gained_priced_control_columns", True)
                            q = big.index[pid]
                            pc_s = r.get("control_solved")
                            pc_n = r.get("control_nodes")
                            big_in = bool(big.csol[q]) and int(big.cn[q]) <= big_cap
                            if (pc_s is True and isinstance(pc_n, int) and not isinstance(pc_n, bool)
                                    and pc_n <= big_cap):
                                rep.cmp(summ, GC, rbase + ("control_solved",), bool(big.csol[q]), label=lab)
                                rep.cmp(summ, GC, rbase + ("control_nodes",), int(big.cn[q]), label=lab)
                            elif big is ctl and vs.V >= big_cap:
                                # Review: vacuous case removed. The row is "gained" because this same
                                # control file leaves it unsolved within the view, so "that file must not
                                # solve it" could never fail; it is listed as not checked, not counted.
                                rep.skip("%s: views.%s.gained_presentations_priced.rows[*] control_solved/"
                                         "control_nodes beyond %d nodes not checked: the only control file "
                                         "that reaches furthest is this budget's own, and it is what makes "
                                         "these rows gained" % (tag, vs.key, big_cap))
                            else:
                                rep.record(GC, not big_in,
                                           pstr(rbase) + " (published control result is beyond %d nodes, so the "
                                           "budget-%d control file must not solve it; %s)" % (big_cap, big_B, lab),
                                           {"control_solved": pc_s, "control_nodes": pc_n},
                                           {"solved": bool(big.csol[q]), "nodes": int(big.cn[q])}, budget=B)
                            rep.note(GC, "inferred: this budget's control file does not reach control_file_budget, "
                                         "so only the rows whose published control_nodes fit in the budget-%d "
                                         "control file are compared with it (solved flag and nodes); for the "
                                         "other rows that file must leave the presentation unsolved. Those other "
                                         "rows and the four totals of the block stay unchecked" % big_B)
                    if full:
                        rep.cmp(summ, PR, gb + ("control_file_budget",), int(ctl.budget))
                        rep.cmp(summ, PR, gb + ("control_solves_them_at_file_budget",),
                                int(ctl.csol[gained_idx].sum()))
                        rep.cmp(summ, PR, gb + ("best_word_cheaper_than_control",),
                                int((vs.minn[gained_idx] < cn[gained_idx]).sum()))
                        rep.cmp(summ, PR, gb + ("shortlex_to_first_solve_cheaper_than_control",),
                                int((vs.cum[gained_idx] < cn[gained_idx]).sum()))
    elif views:
        rep.skip("%s: not every length 1..%d could be recomputed, so overall, price, top_words, the fixed "
                 "word, the relator rotations and words_beating/matching_control were not compared"
                 % (tag, use_max))

    # ---- some word faster than the control: which reading ------------------
    use_incl = False
    if faster_rows:
        bad_s = sum(1 for r in faster_rows if not num_equal(r[3], r[4]))
        bad_i = sum(1 for r in faster_rows if not num_equal(r[3], r[5]))
        telling = sum(1 for r in faster_rows if r[4] != r[5])
        use_incl = (bad_s > 0 and bad_i < bad_s)
        for (vk, n, j, pubv, strict, incl) in faster_rows:
            mine = incl if use_incl else strict
            rep.record(FR, num_equal(pubv, mine),
                       "views.%s.oracle[%d].some_word_faster_than_control (max_len=%d)" % (vk, j, n),
                       pubv, {"strict_control_solves_and_a_word_uses_fewer_nodes": strict,
                              "inclusive_or_solves_where_the_control_does_not": incl}, budget=B)
        if bad_s == 0 and bad_i == 0:
            verdict = "both readings reproduce every row (they never differ here)"
        elif bad_s == 0:
            verdict = "the STRICT reading reproduces every row (the control solves and some word solves with fewer nodes)"
        elif bad_i == 0:
            verdict = "the INCLUSIVE reading reproduces every row (fewer nodes than the control, or solved where the control is not)"
        else:
            verdict = "NEITHER reading reproduces every row"
        rep.note(FR, "%s; rows: %d, rows where the two readings differ: %d, rows not reproduced: strict %d, "
                     "inclusive %d; mismatches are counted against the %s reading"
                 % (verdict, len(faster_rows), telling, bad_s, bad_i, "inclusive" if use_incl else "strict"))
    for (vs_, n, j, pubn, strict_nr, incl_nr) in nr_rows:
        rep.record(nm(vs_, "relator_rotations", True), num_equal(pubn, incl_nr if use_incl else strict_nr),
                   "views.%s.oracle[%d].some_non_rotation_word_faster (max_len=%d)" % (vs_.key, j, n),
                   pubn, {"strict": strict_nr, "inclusive": incl_nr,
                          "reading_used": "inclusive" if use_incl else "strict"}, budget=B)

    # ---- median extra nodes ------------------------------------------------
    if med_rows:
        hits = [0, 0, 0]
        for (vk, n, i, pubm, cands) in med_rows:
            for c in range(3):
                if num_equal(pubm, cands[c]):
                    hits[c] += 1
            rep.record(ME, num_equal(pubm, cands[MEDIAN_PRIMARY]),
                       "views.%s.by_length[%d].median_extra_nodes (len=%d)" % (vk, i, n), pubm,
                       {"pooled_cells": cands[0], "per_presentation_then_median": cands[1],
                        "per_word_then_median": cands[2]}, budget=B)
        rep.note(ME, "no definition was given for this field and the .md does not print it. Checked against: "
                     "%s. Rows reproduced by each reading, of %d: pooled cells %d; per-presentation %d; "
                     "per-word %d. A failure here with another reading at %d of %d is a difference of "
                     "definition, not of data"
                 % (MEDIAN_READINGS[MEDIAN_PRIMARY], len(med_rows), hits[0], hits[1], hits[2],
                    len(med_rows), len(med_rows)))
        rep.info[tag + ":median_extra_nodes_rows_reproduced"] = {
            "rows": len(med_rows), "pooled_cells": hits[0], "per_presentation_then_median": hits[1],
            "per_word_then_median": hits[2]}

    # ---- w against w^-1 --------------------------------------------------------
    ipub = summ.get(("inverse_pairs",))
    inv_contig = 0
    for n in range(1, INV_MAX_L + 1):
        if n in inv_stats:
            inv_contig = n
        else:
            break
    if isinstance(ipub, dict):
        pm = ipub.get("max_len")
        if (isinstance(pm, int) and not isinstance(pm, bool) and pm >= 1
                and all(m in inv_stats for m in range(1, pm + 1))):
            rng = list(range(1, pm + 1))
            summ.mark(("inverse_pairs", "max_len"))
            rep.skip("%s summary: inverse_pairs.max_len (%d) not checked: it is the summarizer's choice of "
                     "lengths; usable _inv files exist for lengths 1..%d" % (tag, pm, inv_contig))
            if inv_contig > pm:
                rep.note(IP, "usable _inv files exist to length %d but the summary's block stops at %d; it "
                             "was checked over its own lengths" % (inv_contig, pm))
            rep.cmp(summ, IP, ("inverse_pairs", "pairs"), int(sum(inv_stats[m]["pairs"] for m in rng)))
            rep.cmp(summ, IP, ("inverse_pairs", "identical"), int(sum(inv_stats[m]["identical"] for m in rng)),
                    label="same solved flag and same nodes")
            rep.cmp(summ, IP, ("inverse_pairs", "solved_status_differs"),
                    int(sum(inv_stats[m]["differs"] for m in rng)))
            diffs = np.concatenate([inv_diffs[m] for m in rng])
            rep.cmp(summ, IP, ("inverse_pairs", "mean_abs_node_difference_both_solved"), fmean(diffs))
            rep.cmp(summ, IP, ("inverse_pairs", "p99_abs_node_difference_both_solved"),
                    float(np.percentile(diffs, 99)) if diffs.size else float("nan"),
                    label="numpy percentile 99, linear interpolation")
            rep.note(IP, "at the file budget, not in a view; identical = same solved flag and same nodes; "
                         "pairs also identical in path_len: %d; the mean and the 99th percentile of "
                         "|nodes(w) - nodes(w^-1)| over pairs where both solve are inferred from the field names"
                     % int(sum(inv_stats[m]["identical_with_path_len"] for m in rng)))
        else:
            rep.skip("%s: inverse_pairs covers lengths 1..%s but usable _inv files exist only for 1..%d: "
                     "its totals were not compared" % (tag, jsonable(pm), inv_contig))
    elif inv_stats:
        rep.skip("%s: _inv files are present but the summary has no inverse_pairs block; nothing to compare "
                 "(recomputed per length: %s)" % (tag, json.dumps(jsonable(inv_stats), sort_keys=True)))

    # ---- relator-subword file: the two row counts only ---------------------------
    rs_path = os.path.join(rdir, stem + "_relsub.jsonl")
    if summ.get(("relsub",)) is MISSING:
        pass
    elif not os.path.isfile(rs_path):
        rep.skip("%s_relsub.jsonl is absent: relsub.rows and relsub.rows_proper were not compared" % stem)
    else:
        RS = tag + ":inferred:relsub_row_counts"
        n_rows = 0
        n_proper = 0
        try:
            with open(rs_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    n_rows += 1
                    if json.loads(line).get("is_proper") is True:
                        n_proper += 1
            rep.cmp(summ, RS, ("relsub", "rows"), n_rows, label="rows of %s_relsub.jsonl" % stem)
            rep.cmp(summ, RS, ("relsub", "rows_proper"), n_proper, label="rows with is_proper true")
            rep.note(RS, "inferred: rows = lines of the relsub file, rows_proper = lines with is_proper true; "
                         "nothing else of the relsub block is recomputed")
        except Exception as exc:
            rep.errors.append("%s_relsub.jsonl: could not be read: %r" % (stem, exc))

    # ---- control at larger budgets ---------------------------------------------
    cal = summ.get(("control_at_larger_budgets",))
    if isinstance(cal, dict):
        own_cap = ctl.budget if ctl.budget is not None else B
        for key in cal:
            try:
                kb = int(key)
            except (TypeError, ValueError):
                continue
            src = None
            if kb <= own_cap:
                src = ctl
                src_name = "this budget's control file"
            else:
                for B2 in sorted(controls):
                    c2 = controls[B2]
                    if c2 is None or B2 == B:
                        continue
                    cap2 = c2.budget if c2.budget is not None else B2
                    if kb <= cap2:
                        src = c2
                        src_name = "the budget-%d control file" % B2
                        break
            if src is None:
                continue
            rep.cmp(summ, CL, ("control_at_larger_budgets", key), int((src.csol & (src.cn <= kb)).sum()),
                    label="solved and nodes <= %d in %s" % (kb, src_name))
        rep.note(CL, "inferred: number of presentations the control solves within that many nodes; an entry "
                     "above this control file's own budget is taken from the other budget's control file "
                     "when that one reaches it, otherwise it is skipped")

    results[B] = {
        "control": dict((vs.V, vs.ncs) for vs in views),
        "views": dict((vs.V, vs.stats) for vs in views),
    }


# ----------------------------------------------------------------------------
# cross-budget check of the prefix property
# ----------------------------------------------------------------------------

def cross_budget(rep, results):
    X = "cross:prefix_property_b1000_vs_b10000"
    if 1000 not in results or 10000 not in results:
        rep.skip("cross-budget prefix check (views 100 and 1,000 recomputed from the budget-1,000 files "
                 "against the same views recomputed from the budget-10,000 files): needs both budgets")
        return
    a = results[1000]
    b = results[10000]
    for V in (100, 1000):
        if V in a["control"] and V in b["control"]:
            rep.record(X, a["control"][V] == b["control"][V],
                       "view %d: control_solved from the b1000 control file against the b10000 one" % V,
                       a["control"][V], b["control"][V])
        sa = a["views"].get(V, {})
        sb = b["views"].get(V, {})
        for n in sorted(set(sa) & set(sb)):
            for key in sorted(sa[n]):
                rep.record(X, num_equal(sa[n][key], sb[n][key]),
                           "view %d, len %d, %s: recomputed from the b1000 files against the b10000 files"
                           % (V, n, key), sa[n][key], sb[n][key])
    rep.note(X, "not a comparison with the summary: the per-length numbers of the views 100 and 1,000, "
                "recomputed here from the budget-1,000 arrays and from the budget-10,000 arrays, must agree "
                "if 'solved in the file and nodes <= V' is a true prefix of the longer search; 'published' "
                "in an example is the b1000 value, 'recomputed' the b10000 value")


def finish_skipped(rep):
    for summ in rep.summaries:
        groups = {}
        order = []
        for path in leaves(summ.obj):
            if tuple(path) in summ.seen:
                continue
            pat = ppattern(path)
            if pat not in groups:
                groups[pat] = 0
                order.append(pat)
            groups[pat] += 1
        for pat in order:
            reason = DEFAULT_REASON
            for prefix, why in SKIP_RULES:
                if pat.startswith(prefix):
                    reason = why
                    break
            rep.skip("%s summary: %s (%d value%s) not checked: %s"
                     % (summ.tag, pat, groups[pat], "" if groups[pat] == 1 else "s", reason))


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------

def write_out(rep, out_json, crashed):
    checks = []
    total = 0
    compared = 0
    for name in rep.order:
        c = rep.checks[name]
        total += c["mismatches"]
        compared += c["compared"]
        status = "not_compared" if c["compared"] == 0 else ("mismatch" if c["mismatches"] else "ok")
        checks.append({"name": name, "compared": c["compared"], "mismatches": c["mismatches"],
                       "status": status, "detail": " | ".join(c["detail"])})
    out = {
        "script": SCRIPT,
        "checks": checks,
        "mismatches": total,
        "compared": compared,
        "skipped": rep.skipped,
        "first_mismatches": rep.examples[:EX_TOTAL],
        "info": jsonable(rep.info),
        "errors": rep.errors,
        "crashed": crashed,
    }
    tmp = out_json + ".tmp"
    with open(tmp, "w") as f:
        json.dump(out, f, indent=1)
        f.write("\n")
    os.replace(tmp, out_json)
    for c in checks:
        if c["compared"] == 0:
            flag = "NOT COMPARED"
        elif c["mismatches"]:
            flag = "MISMATCH"
        else:
            flag = "ok"
        print("%-12s %s: compared %d, mismatches %d" % (flag, c["name"], c["compared"], c["mismatches"]))
    print("%s: %d checks, %d values compared, %d mismatches, %d skipped entries, %d errors"
          % (SCRIPT, len(checks), compared, total, len(rep.skipped), len(rep.errors)))
    return total, compared


def main(argv):
    if len(argv) < 4:
        sys.stderr.write("usage: python3 %s RESULTS_DIR DATASET OUT_JSON [workers] [minutes]\n" % SCRIPT)
        return 1
    rdir, dataset, out_json = argv[1], argv[2], argv[3]
    minutes = 30.0
    if len(argv) > 5:
        try:
            minutes = float(argv[5])
        except ValueError:
            minutes = 30.0
    deadline = time.time() + 60.0 * minutes   # workers (argv[4]) is not used: nothing here searches

    rep = Report()
    crashed = None
    try:
        controls = {}
        for B in BUDGETS:
            path = os.path.join(rdir, "rank3_bf_ms640_b%d_cap%d_control.jsonl" % (B, CAP))
            controls[B] = None
            if not os.path.isfile(path):
                rep.skip("%s is absent" % os.path.basename(path))
                continue
            try:
                c = load_control(path)
                controls[B] = c if c.ids.size else None
            except Exception as exc:
                rep.errors.append("%s: could not be read: %r" % (os.path.basename(path), exc))

        dataset_rel = None
        try:
            dataset_rel = load_dataset(dataset)
            info = {"lines": len(dataset_rel)}
            for B in BUDGETS:
                c = controls[B]
                if c is None:
                    continue
                same = 0
                for i in c.ids.tolist():
                    r = c.rows[i]
                    if 0 <= i < len(dataset_rel) and (r.get("r1"), r.get("r2")) == dataset_rel[i]:
                        same += 1
                info["b%d_control_rows_whose_r1_r2_equal_the_dataset_line" % B] = "%d of %d" % (same, int(c.ids.size))
            rep.info["dataset"] = info
        except Exception as exc:
            rep.info["dataset"] = "not read (%r); it is only used for information" % (exc,)

        results = {}
        for B in BUDGETS:
            try:
                run_budget(rep, rdir, B, controls, dataset_rel, deadline, results)
            except Exception:
                rep.errors.append("budget %d: crashed: %s" % (B, traceback.format_exc()))
        try:
            cross_budget(rep, results)
        except Exception:
            rep.errors.append("cross-budget check crashed: %s" % traceback.format_exc())
        finish_skipped(rep)
    except Exception:
        crashed = traceback.format_exc()

    total, compared = write_out(rep, out_json, crashed)
    for e in rep.errors:
        sys.stderr.write("ERROR: %s\n" % e)
    if crashed:
        sys.stderr.write(crashed)
        return 1
    if total:
        return 3
    if rep.errors:
        return 1
    if compared == 0:
        sys.stderr.write("nothing was compared: this is not a pass\n")
        return 1
    return 0


if __name__ == "__main__":
    try:
        code = main(sys.argv)
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        code = 1
    sys.exit(code)
