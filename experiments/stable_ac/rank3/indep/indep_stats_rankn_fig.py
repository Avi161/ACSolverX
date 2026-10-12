#!/usr/bin/env python3
"""indep_stats_rankn_fig.py -- independent recomputation, from the raw arrays only, of

  (a) every field of rankn_bf_ms640_b1000_cap24_r{4,5}_summary.json, and
  (b) every table row of every *_control_vs_start*.md present in RESULTS_DIR
      (rank 3 at both budgets, any _L<a>-<b> range, and the rank 4/5 files).

CLI:  python3 indep_stats_rankn_fig.py <RESULTS_DIR> <DATASET> <OUT_JSON> [workers] [minutes]
Exit: 0 no mismatch, 3 any mismatch, 1 crash.

Nothing is imported from the repository.  numpy + standard library only.
See indep_stats_rankn_fig.md for the definitions used and the assumptions made.
"""

import json
import math
import os
import re
import sys
import time
import traceback

import numpy as np

SCRIPT = "indep_stats_rankn_fig.py"
SHARE_KEYS = ("fewer", "same", "more", "notsolved", "fewer17", "more17")
MAX_FIRST = 50
CHUNK_ROWS = 32

R3_MD = re.compile(r"^(rank3_bf_ms640_b(\d+)_cap(\d+))_control_vs_start(?:_L(\d+)-(\d+))?\.md$")
RN_FILE = re.compile(r"^(rankn_bf_ms640_b(\d+)_cap(\d+)_r(\d+))_(summary\.json|control_vs_start\.md)$")
SEP_RE = re.compile(r"^:?-+:?$")
PCT_RE = re.compile(r"^(-?\d+(?:\.(\d+))?)\s*%$")
INT_RE = re.compile(r"^-?\d+$")


# --------------------------------------------------------------------------- report

def is_num(v):
    return isinstance(v, (int, float, np.integer, np.floating)) and not isinstance(v, (bool, np.bool_))


def clean(o):
    """Make a value strictly JSON-serialisable (no numpy scalars, no NaN)."""
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
    if isinstance(o, float) and not math.isfinite(o):
        return repr(o)
    if o is None or isinstance(o, (str, int, float, bool)):
        return o
    return repr(o)


class Report:
    def __init__(self):
        self.checks = []
        self.skipped = []
        self.first = []

    def new(self, name):
        c = Check(self, name)
        self.checks.append(c)
        return c

    def skip(self, what, why):
        self.skipped.append("%s: %s" % (what, why))


class Check:
    def __init__(self, rep, name):
        self.rep = rep
        self.name = name
        self.compared = 0
        self.mismatches = 0
        self.detail = {}

    def note(self, key, value):
        self.detail[key] = value

    def bad(self, what, file_value, recomputed, note=None):
        self.mismatches += 1
        if len(self.rep.first) < MAX_FIRST:
            e = {"check": self.name, "what": what, "file_value": file_value, "recomputed": recomputed}
            if note is not None:
                e["note"] = note
            self.rep.first.append(e)

    def fail(self, what, file_value=None, recomputed=None, note=None):
        """A structural failure (missing row, unparsable cell ...): one item compared, one mismatch."""
        self.compared += 1
        self.bad(what, file_value, recomputed, note)

    def eq(self, what, file_value, recomputed, note=None):
        self.compared += 1
        if not (file_value == recomputed):
            self.bad(what, file_value, recomputed, note)

    def eq_int(self, what, file_value, recomputed, note=None):
        self.compared += 1
        ok = is_num(file_value) and is_num(recomputed) and float(file_value) == float(recomputed)
        if not ok:
            self.bad(what, file_value, recomputed, note)

    def close(self, what, file_value, recomputed, tol, note=None):
        self.compared += 1
        ok = (is_num(file_value) and math.isfinite(float(file_value))
              and abs(float(file_value) - float(recomputed)) <= tol)
        if not ok:
            self.bad(what, file_value, round(float(recomputed), 8), note or ("tolerance %g" % tol))


# --------------------------------------------------------------------------- small helpers

def fam(n):
    """Size of the word family of length n: reduced words, one per pair {w, w^-1}."""
    return 2 * 3 ** (n - 1)


def load_meta(z):
    raw = np.asarray(z["meta"]).reshape(-1)[0]
    if isinstance(raw, (bytes, np.bytes_)):
        raw = raw.decode("utf-8")
    return json.loads(str(raw))


def read_control_rows(path):
    """control.jsonl -> ({pres_id: row}, number of duplicated pres_id rows)."""
    rows = {}
    dup = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            o = json.loads(line)
            pid = int(o["pres_id"])
            if pid in rows:
                dup += 1
            rows[pid] = o
    return rows, dup


def to_int(text):
    return int(text.replace(",", ""))


def parse_int(cell):
    t = cell.replace(",", "").strip()
    return int(t) if INT_RE.match(t) else None


def parse_pct(cell):
    """'65.7%' -> (65.7, 1); None when the cell is not a percentage."""
    m = PCT_RE.match(cell.replace(",", "").strip())
    if not m:
        return None
    return float(m.group(1)), len(m.group(2) or "")


def norm_label(cell):
    return re.sub(r"\s+", " ", cell.replace(",", "").strip().lower())


def parse_tables(text):
    """Every markdown pipe table of the text, as a list of rows of stripped cells."""
    tables = []
    cur = None
    for line in text.splitlines():
        s = line.strip()
        if len(s) >= 2 and s.startswith("|") and s.endswith("|"):
            cells = [x.strip() for x in s[1:-1].split("|")]
            if cur is None:
                cur = []
                tables.append(cur)
            cur.append(cells)
        else:
            cur = None
    return tables


def data_rows(table):
    return [r for r in table[1:] if not all(SEP_RE.match(x) for x in r)]


def is_group_header(header):
    t = header[0].lower() if header else ""
    return "control" in t and "node" in t


def is_length_header(header):
    t = header[0].lower() if header else ""
    return "length" in t


def header_columns(header):
    """Positions of the six share columns of a table header, or None."""
    pos = {}
    for j, h in enumerate(header):
        if j < 2:
            continue
        t = h.lower()
        if "17" in t and "fewer" in t:
            key = "fewer17"
        elif "17" in t and "more" in t:
            key = "more17"
        elif "not solved" in t or "unsolved" in t:
            key = "notsolved"
        elif "same" in t:
            key = "same"
        elif "fewer" in t:
            key = "fewer"
        elif "more" in t:
            key = "more"
        else:
            return None
        if key in pos:
            return None
        pos[key] = j
    return pos if len(pos) == len(SHARE_KEYS) else None


# --------------------------------------------------------------------------- the statistics

def cell_counts(nodes, path_len, cs, cn):
    """Per presentation (row), the number of starts (columns) in each class.

    nodes [P, K] (any integer dtype), path_len [P, K] (>= 0 <=> the start solves),
    cs [P] bool = control solved, cn [P] int64 = control nodes (used only where cs).

    Column order of the result: fewer, same, more, not solved, fewer by >17%, more by >17%.
      fewer     : start solves and (control unsolved or nodes <  cn)
      same      : both solve and nodes == cn
      more      : both solve and nodes >  cn
      not solved: start does not solve
      fewer17   : start solves and (control unsolved or nodes < cn * 0.83)
      more17    : both solve and nodes > cn * 1.17
    The 17% thresholds are the float64 products of the stated definition
    (nodes < cn*0.83, nodes > cn*1.17).  Also returns how many cells the exact
    integer reading (100*nodes vs 83*cn, 117*cn in int64) classifies differently,
    for the record: the two can differ only where 100*nodes == 117*cn exactly.
    """
    p, k = nodes.shape
    out = np.zeros((p, 6), dtype=np.int64)
    fdiff = [0, 0]
    for i0 in range(0, p, CHUNK_ROWS):
        i1 = min(p, i0 + CHUNK_ROWS)
        n = nodes[i0:i1].astype(np.int64)
        s = path_len[i0:i1].astype(np.int64) >= 0
        c_s = cs[i0:i1].astype(bool)[:, None]
        c_n = cn[i0:i1].astype(np.int64)[:, None]
        both = s & c_s
        gain = s & ~c_s
        fewer = gain | (both & (n < c_n))
        same = both & (n == c_n)
        more = both & (n > c_n)
        c_f = c_n.astype(np.float64)
        f17 = gain | (both & (n < c_f * 0.83))
        m17 = both & (n > c_f * 1.17)
        out[i0:i1, 0] = fewer.sum(axis=1)
        out[i0:i1, 1] = same.sum(axis=1)
        out[i0:i1, 2] = more.sum(axis=1)
        out[i0:i1, 3] = (~s).sum(axis=1)
        out[i0:i1, 4] = f17.sum(axis=1)
        out[i0:i1, 5] = m17.sum(axis=1)
        f17_exact = gain | (both & (100 * n < 83 * c_n))
        m17_exact = both & (100 * n > 117 * c_n)
        fdiff[0] += int((f17 != f17_exact).sum())
        fdiff[1] += int((m17 != m17_exact).sum())
    if not bool((out[:, :4].sum(axis=1) == k).all()):
        raise RuntimeError("internal: fewer + same + more + not solved != number of starts")
    return out, fdiff


def expected_group_rows(counts, k_starts, cs, cn, budget):
    """Rows of the 'control's nodes' table.

    counts [P, 6] per presentation over its k_starts starts.  Every presentation has
    the same number of starts, so the mean over a group of the per-presentation shares
    is sum(counts) / (n_group * k_starts).

    Returns ({normalised label: (presentations, [6 percentages] or None when empty)},
             number of solved controls whose node count is outside 1..budget).
    """
    p = counts.shape[0]
    last_d = len(str(budget - 1)) - 1        # 1000 -> 2 (100 to 999); 10000 -> 3
    dec = np.full(p, -1, dtype=np.int64)
    out_of_range = 0
    for i in range(p):
        if cs[i]:
            v = int(cn[i])
            if v < 1 or v > budget:
                out_of_range += 1
            dec[i] = min(len(str(max(v, 1))) - 1, last_d)   # nodes == budget -> last decade

    def make(mask):
        n = int(mask.sum())
        if n == 0:
            return (0, None)
        tot = counts[mask].sum(axis=0)
        return (n, [100.0 * float(t) / float(n * k_starts) for t in tot])

    rows = {}
    for d in range(last_d + 1):
        rows["%d to %d" % (10 ** d, 10 ** (d + 1) - 1)] = make(dec == d)
    rows["unsolved"] = make(~cs)
    rows["all"] = make(np.ones(p, dtype=bool))
    return rows, out_of_range


# --------------------------------------------------------------------------- table comparison

def compare_row(c, where, cells, colpos, count_want, pcts_want):
    count_cell = cells[1] if len(cells) > 1 else ""
    c.eq_int("%s | count" % where, parse_int(count_cell), count_want, note="cell %r" % count_cell)
    if pcts_want is None:
        return                                   # empty group: shares are undefined
    for i, key in enumerate(SHARE_KEYS):
        j = colpos[key]
        cell = cells[j] if j < len(cells) else ""
        got = parse_pct(cell)
        if got is None:
            c.fail("%s | %s" % (where, key), cell, round(pcts_want[i], 6), "cell is not a percentage")
        else:
            val, ndec = got
            # printed precision: half a unit of the last printed decimal, + 0.001 (0.051 for one decimal)
            c.close("%s | %s" % (where, key), val, pcts_want[i], 0.5 * 10.0 ** (-ndec) + 0.001)


def compare_group_table(c, where, table, exp):
    colpos = header_columns(table[0])
    if colpos is None:
        c.fail("%s header" % where, table[0], None, "cannot identify the six share columns")
        return
    seen = set()
    for cells in data_rows(table):
        lab = norm_label(cells[0]) if cells else ""
        if lab in seen:
            c.fail("%s row '%s'" % (where, lab), cells, None, "duplicated row")
            continue
        seen.add(lab)
        if lab not in exp:
            c.fail("%s row '%s'" % (where, lab), cells, None, "row label not expected for this budget")
            continue
        n, pcts = exp[lab]
        compare_row(c, "%s row '%s'" % (where, lab), cells, colpos, n, pcts)
    for lab, (n, pcts) in exp.items():
        if lab not in seen and n > 0:
            c.fail("%s row '%s'" % (where, lab), None,
                   {"presentations": n, "pct": [round(x, 4) for x in pcts]}, "row missing from the file")


def compare_length_table(c, rep, fname, table, exp_len, wanted, unavailable):
    """exp_len: {n: (starts, [6 pct])} for the lengths whose raw file was usable."""
    where = "per-word-length table"
    colpos = header_columns(table[0])
    if colpos is None:
        c.fail("%s header" % where, table[0], None, "cannot identify the six share columns")
        return
    seen = set()
    for cells in data_rows(table):
        n = parse_int(cells[0]) if cells else None
        if n is None:
            c.fail("%s row %r" % (where, cells[0] if cells else ""), cells, None, "row label is not a word length")
            continue
        if n in seen:
            c.fail("%s row %d" % (where, n), cells, None, "duplicated row")
            continue
        seen.add(n)
        if n in exp_len:
            k, pcts = exp_len[n]
            compare_row(c, "%s row %d" % (where, n), cells, colpos, k, pcts)
        elif n in unavailable:
            rep.skip("%s %s row %d" % (fname, where, n), "raw L%d.npz absent or unusable" % n)
        else:
            c.fail("%s row %d" % (where, n), cells, None, "length outside the range of the file name")
    for n in wanted:
        if n in exp_len and n not in seen:
            k, pcts = exp_len[n]
            c.fail("%s row %d" % (where, n), None,
                   {"starts": k, "pct": [round(x, 4) for x in pcts]}, "row missing from the file")


def prose_common(c, text, fname, budget, p, k_total, control_solved):
    """Numbers quoted in the title and the paragraph above the table (an extra, beyond the rows)."""
    lines = text.splitlines()
    first = lines[0] if lines else ""
    not_found = []
    m = re.search(r"`([^`]+)`", first)
    if m:
        c.eq("title: stem in backticks", m.group(1), fname[:-3])
    else:
        not_found.append("title stem")
    m = re.search(r"Budget (\d[\d,]*)", text)
    if m:
        c.eq_int("prose: budget", to_int(m.group(1)), budget)
    else:
        not_found.append("budget")
    m = re.search(r"(\d[\d,]*) presentations", text)
    if m:
        c.eq_int("prose: presentations", to_int(m.group(1)), p)
    else:
        not_found.append("presentations")
    if k_total is not None:
        m = re.search(r"(\d[\d,]*) starts each", text)
        if m:
            c.eq_int("prose: starts each", to_int(m.group(1)), k_total)
        else:
            not_found.append("starts each")
        m = re.search(r"(\d[\d,]*) searches", text)
        if m:
            c.eq_int("prose: searches", to_int(m.group(1)), p * k_total)
        else:
            not_found.append("searches")
    m = re.search(r"Control solved: (\d[\d,]*) of (\d[\d,]*)", text)
    if m:
        c.eq_int("prose: control solved", to_int(m.group(1)), control_solved)
        c.eq_int("prose: control solved, 'of' count", to_int(m.group(2)), p)
    else:
        not_found.append("control solved")
    return first, not_found


# --------------------------------------------------------------------------- rank 4 / 5

def load_rankn(rep, results_dir, stem, budget, cap, rank, deadline):
    fname = stem + ".npz"
    path = os.path.join(results_dir, fname)
    if not os.path.isfile(path):
        rep.skip(fname, "absent")
        return None
    if time.time() > deadline:
        rep.skip(fname, "time box reached before this file was loaded")
        return None
    c = rep.new("%s: structure of the raw arrays" % fname)
    try:
        with np.load(path, allow_pickle=False) as z:
            pres_ids = np.asarray(z["pres_ids"]).astype(np.int64).reshape(-1)
            nodes = np.asarray(z["nodes"]).astype(np.int64)        # uint16 -> int64 before arithmetic
            path_len = np.asarray(z["path_len"]).astype(np.int64)
            base = np.asarray(z["base"]).astype(np.int64)
            null = np.asarray(z["null"]).astype(np.int64)
            combos = np.asarray(z["combos"]).astype(np.int64)
            meta = load_meta(z)
    except Exception as e:                                         # noqa: BLE001
        c.fail("load", None, None, repr(e))
        rep.skip(fname, "could not be loaded")
        return None

    p = int(len(pres_ids))
    n_combo = int(nodes.shape[1]) if nodes.ndim == 2 else -1
    words = [str(w) for w in meta.get("words", [])]
    k = meta.get("extra_generators")
    m = meta.get("max_word_len")
    c.eq("nodes.shape", list(nodes.shape), [p, n_combo])
    c.eq("path_len.shape", list(path_len.shape), list(nodes.shape))
    c.eq("base.shape", list(base.shape), [p, 3])
    c.eq("null.shape", list(null.shape), [p, 3])
    c.eq_int("distinct pres_ids", len(set(pres_ids.tolist())), p)
    c.eq_int("meta.rank vs the file name", meta.get("rank"), rank)
    c.eq_int("meta.node_budget vs the file name", meta.get("node_budget"), budget)
    if "max_relator_length_cap" in meta:
        c.eq_int("meta.max_relator_length_cap vs the file name", meta.get("max_relator_length_cap"), cap)
    c.eq_int("distinct words in meta.words", len(set(words)), len(words))
    if is_num(m):
        c.eq("lengths of meta.words (families of lengths 1..max_word_len concatenated)",
             [len(w) for w in words], [n for n in range(1, int(m) + 1) for _ in range(fam(n))])
    if is_num(k) and int(k) >= 1:
        c.eq_int("meta.rank == 2 + extra_generators", meta.get("rank"), 2 + int(k))
        c.eq("combos.shape", list(combos.shape), [n_combo, int(k)])
        c.eq_int("number of combos == number of multisets of k words",
                 n_combo, math.comb(len(words) + int(k) - 1, int(k)))
    if combos.ndim == 2 and combos.shape[0] > 0 and combos.shape[1] > 0:
        srt = np.sort(combos, axis=1)
        c.eq_int("distinct multisets among the combos rows", len({tuple(r) for r in srt.tolist()}),
                 int(combos.shape[0]))
        c.eq("combo indices inside range(len(words))",
             bool(combos.min() >= 0 and combos.max() < len(words)), True)
    if base.ndim == 2 and base.shape[1] == 3:
        c.eq("base[:, 0] is 0/1", bool(np.isin(base[:, 0], [0, 1]).all()), True)

    usable = (nodes.ndim == 2 and n_combo > 0 and nodes.shape == path_len.shape and nodes.shape[0] == p
              and base.shape == (p, 3) and null.shape == (p, 3)
              and combos.ndim == 2 and combos.shape[0] == n_combo
              and combos.size > 0 and combos.min() >= 0 and combos.max() < len(words))
    if not usable:
        rep.skip(fname, "unusable (see the structure check); summary and table not recomputed")
        return None

    cs = base[:, 0] != 0
    cn = base[:, 1]
    counts, fdiff = cell_counts(nodes, path_len, cs, cn)
    d = {"fname": fname, "check": c, "pres_ids": pres_ids, "nodes": nodes, "solved": path_len >= 0,
         "base": base, "null": null, "combos": combos, "meta": meta, "words": words,
         "p": p, "n_combo": n_combo, "cs": cs, "cn": cn, "counts": counts, "fdiff": fdiff}

    # the control inside the rank-n file against the rank-3 control file of the same budget
    ctrl_name = "rank3_bf_ms640_b%d_cap%d_control.jsonl" % (budget, cap)
    ctrl_path = os.path.join(results_dir, ctrl_name)
    if os.path.isfile(ctrl_path):
        c2 = rep.new("%s: base (2-generator control) vs %s" % (fname, ctrl_name))
        rows, _dup = read_control_rows(ctrl_path)
        for i in range(p):
            pid = int(pres_ids[i])
            row = rows.get(pid)
            if row is None:
                c2.fail("pres_id %d" % pid, None, [int(x) for x in base[i]], "no control.jsonl row")
                continue
            c2.compared += 1
            r_solved = bool(row.get("solved"))
            r_nodes = row.get("nodes_explored")
            ok = (r_solved == bool(cs[i])) and (not r_solved or (is_num(r_nodes) and int(r_nodes) == int(cn[i])))
            if not ok:
                c2.bad("pres_id %d (solved, nodes)" % pid, [int(x) for x in base[i][:2]],
                       [int(r_solved), r_nodes], "file_value = npz base, recomputed = control.jsonl")
        c2.note("rule", "solved flags equal; node counts equal where solved")
    else:
        rep.skip("%s base vs %s" % (fname, ctrl_name), "control.jsonl absent")
    return d


def check_rankn_summary(rep, path, fname, d):
    c = rep.new("%s: every field" % fname)
    try:
        with open(path, encoding="utf-8") as f:
            summ = json.load(f)
    except Exception as e:                                         # noqa: BLE001
        c.fail("parse", None, None, repr(e))
        return
    if not isinstance(summ, dict):
        c.fail("parse", type(summ).__name__, "object", "top level is not a JSON object")
        return

    p, n_combo = d["p"], d["n_combo"]
    solved, nodes, cs, cn = d["solved"], d["nodes"], d["cs"], d["cn"]
    pres_ids, base, null, combos, meta, words = d["pres_ids"], d["base"], d["null"], d["combos"], d["meta"], d["words"]

    rate = solved.sum(axis=1).astype(np.float64) / float(n_combo)   # per presentation
    any_solved = solved.any(axis=1)
    both = solved & cs[:, None]                                     # cells: combo solved, control solved
    faster = both & (nodes < cn[:, None])
    n_both = int(both.sum())
    per_combo = solved.sum(axis=0)
    best = int(per_combo.max())
    best_rows = [int(j) for j in np.nonzero(per_combo == best)[0]]
    searches = p * n_combo
    core = meta.get("core_seconds")
    null_mis = sorted(int(x) for x in pres_ids[(null != base).any(axis=1)])
    gained = sorted(int(x) for x in pres_ids[any_solved & ~cs])
    lost = sorted(int(x) for x in pres_ids[cs & ~any_solved])

    exp = [
        ("rank", "int", meta.get("rank")),
        ("combos_per_presentation", "int", n_combo),
        ("searches", "int", searches),
        ("core_seconds", "round0", float(core) if is_num(core) else None),
        ("ms_per_search", "round1", 1000.0 * float(core) / float(searches) if is_num(core) else None),
        ("null_mismatch_pres_ids", "ids", null_mis),
        ("control_solved", "int", int(cs.sum())),
        ("mean_solve_rate_per_presentation", "round4", float(rate.mean())),
        ("mean_solve_rate_on_control_solved", "round4", float(rate[cs].mean()) if cs.any() else None),
        ("mean_solve_rate_on_control_unsolved", "round4", float(rate[~cs].mean()) if (~cs).any() else None),
        ("solved_by_some_combo", "int", int(any_solved.sum())),
        ("gained_presentations", "ids", gained),
        ("lost_by_every_combo", "ids", lost),
        ("share_of_solved_combos_faster_than_control", "round4",
         float(faster.sum()) / float(n_both) if n_both else None),
        ("presentations_where_some_combo_is_faster", "int", int(faster.any(axis=1).sum())),
        ("best_single_combo_solved", "int", best),
    ]
    tol = {"round0": 0.5 + 1e-9, "round1": 0.05 + 1e-9, "round4": 0.00005 + 1e-9}
    known = {"best_single_combo"}
    recomputed = {}
    for key, kind, want in exp:
        known.add(key)
        recomputed[key] = len(want) if key == "lost_by_every_combo" else want
        what = "field %s" % key
        if key in ("core_seconds", "ms_per_search") and want is None:
            rep.skip("%s field %s" % (fname, key), "meta.core_seconds absent from the npz; not recomputed")
            continue
        if key not in summ:
            c.fail(what, None, recomputed[key], "field absent from the file")
            continue
        fv = summ[key]
        if kind == "int":
            c.eq_int(what, fv, want)
        elif kind == "ids":
            if isinstance(fv, list):
                try:
                    got = sorted(int(x) for x in fv)
                except (TypeError, ValueError):
                    got = fv
                c.eq(what, got, want, "pres_ids, compared as sorted lists")
            elif is_num(fv):
                c.eq_int(what, fv, len(want), "the file gives a count; compared with the number of pres_ids")
            else:
                c.fail(what, fv, want, "neither a list of pres_ids nor a count")
        else:
            if want is None:
                c.compared += 1
                if not (fv is None or (isinstance(fv, float) and math.isnan(fv))):
                    c.bad(what, fv, None, "undefined here (empty group); null or NaN expected")
            else:
                if key == "ms_per_search" and is_num(fv):
                    # the file may have divided the integer-rounded core_seconds: take the reading nearer to it
                    alt = 1000.0 * float(round(float(core))) / float(searches)
                    if abs(float(fv) - alt) < abs(float(fv) - want):
                        want = alt
                c.close(what, fv, want, tol[kind])

    # best_single_combo: any combo reaching the maximum satisfies the definition (ties)
    what = "field best_single_combo"
    k = int(combos.shape[1])
    first_best = [words[int(i)] for i in combos[best_rows[0]]]
    recomputed["best_single_combo"] = first_best
    widx = {w: i for i, w in enumerate(words)}
    if "best_single_combo" not in summ:
        c.fail(what, None, first_best, "field absent from the file")
    else:
        fv = summ["best_single_combo"]
        if not (isinstance(fv, list) and len(fv) == k and all(isinstance(w, str) and w in widx for w in fv)):
            c.fail(what, fv, first_best, "not a list of k words of meta.words")
        else:
            target = np.array(sorted(widx[w] for w in fv), dtype=np.int64)
            hit = np.nonzero((np.sort(combos, axis=1) == target[None, :]).all(axis=1))[0]
            if len(hit) != 1:
                c.fail(what, fv, first_best, "the words match %d rows of combos" % len(hit))
            else:
                j = int(hit[0])
                c.eq_int("%s: presentations solved by the named combo vs the maximum over combos" % what,
                         int(per_combo[j]), best,
                         "file names %r (combos row %d); first maximiser is %r" % (fv, j, first_best))
                c.note("best_single_combo", {
                    "named_row": j, "named_solved": int(per_combo[j]), "max_solved": best,
                    "number_of_combos_at_the_maximum": len(best_rows),
                    "named_is_first_maximiser": j == best_rows[0],
                    "same_word_order_as_combos_row": [words[int(i)] for i in combos[j]] == fv})

    for key in summ:
        if key not in known:
            rep.skip("%s field %s" % (fname, key), "field not known to this script; not recomputed")

    # other readings, for whoever adjudicates a mismatch (not compared)
    n_cs_cells = int(cs.sum()) * n_combo
    n_solved_cells = int(solved.sum())
    fewer_any = solved & (~cs[:, None] | (nodes < cn[:, None]))
    c.note("recomputed", recomputed)
    c.note("other_readings_not_compared", {
        "share_faster / all cells with a solved control": (float(faster.sum()) / n_cs_cells) if n_cs_cells else None,
        "share_faster incl. gained / all solved cells":
            (float(fewer_any.sum()) / n_solved_cells) if n_solved_cells else None,
        "presentations with some combo 'fewer' (counting an unsolved control as fewer)":
            int(fewer_any.any(axis=1).sum()),
        "null mismatch on (solved, nodes) only":
            sorted(int(x) for x in pres_ids[(null[:, :2] != base[:, :2]).any(axis=1)]),
        "faster cells": int(faster.sum()), "solved cells with a solved control": n_both})


def check_rankn_md(rep, path, fname, d, budget, rank):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    c = rep.new("%s: table rows" % fname)
    exp, out_of_range = expected_group_rows(d["counts"], d["n_combo"], d["cs"], d["cn"], budget)
    c.eq_int("solved controls with a node count outside 1..budget", out_of_range, 0)
    tables = parse_tables(text)
    groups = [t for t in tables if is_group_header(t[0])]
    if len(groups) != 1:
        c.fail("control's-nodes table", len(groups), 1, "number of such tables in the file")
    else:
        compare_group_table(c, "control's-nodes table", groups[0], exp)
    if len(tables) > len(groups):
        rep.skip(fname, "%d table(s) of another kind in the file were not compared" % (len(tables) - len(groups)))
    c.note("exact_integer_17pct_cells_classified_differently [fewer17, more17]", d["fdiff"])
    c.note("recomputed_rows", {lab: {"presentations": n, "pct": None if pc is None else [round(x, 4) for x in pc]}
                               for lab, (n, pc) in exp.items()})

    cp = rep.new("%s: numbers in the title and the prose" % fname)
    first, not_found = prose_common(cp, text, fname, budget, d["p"], d["n_combo"], int(d["cs"].sum()))
    m = re.search(r"random (\d+)-generator start", first)
    if m:
        cp.eq_int("title: rank", int(m.group(1)), rank)
    else:
        not_found.append("rank in the title")
    k = int(d["combos"].shape[1])
    m = re.search(r"(\d+) new generators", text)
    if m:
        cp.eq_int("prose: new generators", int(m.group(1)), k)
    else:
        not_found.append("new generators")
    m = re.search(r"every (\d+) words of length at most (\d+)", text)
    if m:
        cp.eq_int("prose: words per start", int(m.group(1)), k)
        cp.eq_int("prose: maximum word length", int(m.group(2)), max(len(w) for w in d["words"]))
    else:
        not_found.append("words per start / maximum word length")
    if not_found:
        cp.note("not_found_in_the_text", not_found)


# --------------------------------------------------------------------------- rank 3

class Rank3:
    def __init__(self, rep, results_dir, n_dataset, deadline):
        self.rep = rep
        self.results_dir = results_dir
        self.n_dataset = n_dataset
        self.deadline = deadline
        self.controls = {}
        self.lens = {}
        self.in_checks = {}

    def in_check(self, stem):
        if stem not in self.in_checks:
            self.in_checks[stem] = self.rep.new("%s: raw inputs of the tables (control.jsonl, L<n>.npz)" % stem)
        return self.in_checks[stem]

    def control(self, stem, budget):
        if stem in self.controls:
            return self.controls[stem]
        fname = stem + "_control.jsonl"
        path = os.path.join(self.results_dir, fname)
        res = None
        if not os.path.isfile(path):
            self.rep.skip(fname, "absent; every rank-3 table of this budget is skipped")
        else:
            c = self.in_check(stem)
            rows, dup = read_control_rows(path)
            pids = sorted(rows)
            solved = np.array([bool(rows[q].get("solved")) for q in pids], dtype=bool)
            nodes = np.array([int(rows[q]["nodes_explored"]) if is_num(rows[q].get("nodes_explored")) else -1
                              for q in pids], dtype=np.int64)
            bad_budget = 0
            n2_diff = 0
            null_diff = 0
            for q in pids:
                o = rows[q]
                if is_num(o.get("node_budget")) and int(o["node_budget"]) != budget:
                    bad_budget += 1
                prim = (bool(o.get("solved")), o.get("nodes_explored"))
                if "n2_solved" in o and (bool(o.get("n2_solved")), o.get("n2_nodes")) != prim:
                    n2_diff += 1
                if "null_solved" in o and (bool(o.get("null_solved")), o.get("null_nodes")) != prim:
                    null_diff += 1
            c.eq_int("%s: duplicated pres_id rows" % fname, dup, 0)
            c.eq_int("%s: rows whose node_budget differs from the file name" % fname, bad_budget, 0)
            if self.n_dataset is not None:
                c.eq_int("%s: presentations vs lines of DATASET" % fname, len(pids), self.n_dataset)
            c.eq_int("%s: solved rows with nodes_explored outside 1..budget" % fname,
                     int((solved & ((nodes < 1) | (nodes > budget))).sum()), 0)
            c.note("%s" % fname, {
                "presentations": len(pids), "control_solved": int(solved.sum()),
                "rows where n2_(solved, nodes) differ from the control (not compared)": n2_diff,
                "rows where null_(solved, nodes) differ from the control (not compared)": null_diff})
            res = {"pids": pids, "pos": {q: i for i, q in enumerate(pids)}, "solved": solved, "nodes": nodes}
        self.controls[stem] = res
        return res

    def length(self, stem, budget, n):
        key = (stem, n)
        if key in self.lens:
            return self.lens[key]
        ctrl = self.controls[stem]
        fname = "%s_L%d.npz" % (stem, n)
        path = os.path.join(self.results_dir, fname)
        res = None
        if not os.path.isfile(path):
            self.rep.skip(fname, "absent")
        elif time.time() > self.deadline:
            self.rep.skip(fname, "time box reached before this file was loaded")
        else:
            c = self.in_check(stem)
            loaded = None
            try:
                with np.load(path, allow_pickle=False) as z:
                    pres_ids = np.asarray(z["pres_ids"]).astype(np.int64).reshape(-1)
                    words = [str(w) for w in np.asarray(z["words"]).reshape(-1)]
                    nodes = np.asarray(z["nodes"])
                    path_len = np.asarray(z["path_len"])
                    meta = load_meta(z) if "meta" in z.files else {}
                loaded = True
            except Exception as e:                                 # noqa: BLE001
                c.fail("%s: load" % fname, None, None, repr(e))
                self.rep.skip(fname, "could not be loaded")
            if loaded:
                p = len(ctrl["pids"])
                k = len(words)
                pos = ctrl["pos"]
                c.eq("%s: nodes.shape" % fname, list(nodes.shape), [p, k])
                c.eq("%s: path_len.shape" % fname, list(path_len.shape), [p, k])
                c.eq_int("%s: number of words vs 2*3^(n-1)" % fname, k, fam(n))
                c.eq_int("%s: words whose length is not %d" % (fname, n), sum(1 for w in words if len(w) != n), 0)
                c.eq_int("%s: distinct words" % fname, len(set(words)), k)
                if is_num(meta.get("node_budget")):
                    c.eq_int("%s: meta.node_budget vs the file name" % fname, meta.get("node_budget"), budget)
                id_list = [int(q) for q in pres_ids]
                perm_ok = len(id_list) == p and len(set(id_list)) == p and all(q in pos for q in id_list)
                c.eq("%s: pres_ids is a permutation of the control's pres_ids" % fname, perm_ok, True)
                if perm_ok and k > 0 and nodes.shape == (p, k) and path_len.shape == (p, k):
                    idx = np.array([pos[q] for q in id_list], dtype=np.int64)
                    rows_counts, fdiff = cell_counts(nodes, path_len, ctrl["solved"][idx], ctrl["nodes"][idx])
                    counts = np.zeros((p, 6), dtype=np.int64)
                    counts[idx] = rows_counts                      # aligned to the control's sorted pres_ids
                    res = {"k": k, "counts": counts, "fdiff": fdiff}
                else:
                    self.rep.skip(fname, "unusable (see the raw-inputs check)")
                del nodes, path_len
        self.lens[key] = res
        return res

    def check_md(self, fname, stem, budget, a, b):
        rep = self.rep
        with open(os.path.join(self.results_dir, fname), encoding="utf-8") as f:
            text = f.read()
        if a is None:
            m = re.search(r"lengths (\d+) to (\d+)", text)
            if not m:
                rep.skip(fname, "no length range in the file name or in the prose; not compared")
                return
            a, b = int(m.group(1)), int(m.group(2))
        if a < 1 or b < a:
            rep.skip(fname, "length range %d-%d is not usable; not compared" % (a, b))
            return
        ctrl = self.control(stem, budget)
        if ctrl is None:
            rep.skip(fname, "control.jsonl absent; not compared")
            return
        wanted = list(range(a, b + 1))
        per_len = {n: self.length(stem, budget, n) for n in wanted}
        unavailable = [n for n in wanted if per_len[n] is None]
        p = len(ctrl["pids"])
        cs, cn = ctrl["solved"], ctrl["nodes"]

        c = rep.new("%s: table rows" % fname)
        tables = parse_tables(text)
        groups = [t for t in tables if is_group_header(t[0])]
        lengths = [t for t in tables if is_length_header(t[0]) and not is_group_header(t[0])]
        k_total = None
        if unavailable:
            rep.skip("%s control's-nodes table" % fname,
                     "needs L<n>.npz for every length; absent or unusable: %s" % unavailable)
        else:
            k_total = sum(per_len[n]["k"] for n in wanted)
            total = np.zeros((p, 6), dtype=np.int64)
            fdiff = [0, 0]
            for n in wanted:
                total += per_len[n]["counts"]
                fdiff[0] += per_len[n]["fdiff"][0]
                fdiff[1] += per_len[n]["fdiff"][1]
            exp, _oor = expected_group_rows(total, k_total, cs, cn, budget)
            if len(groups) != 1:
                c.fail("control's-nodes table", len(groups), 1, "number of such tables in the file")
            else:
                compare_group_table(c, "control's-nodes table", groups[0], exp)
            c.note("exact_integer_17pct_cells_classified_differently [fewer17, more17]", fdiff)
            c.note("recomputed_rows", {lab: {"presentations": n_, "pct": None if pc is None else
                                             [round(x, 4) for x in pc]} for lab, (n_, pc) in exp.items()})
        exp_len = {}
        for n in wanted:
            if per_len[n] is not None:
                k = per_len[n]["k"]
                tot = per_len[n]["counts"].sum(axis=0)
                exp_len[n] = (k, [100.0 * float(t) / float(p * k) for t in tot])
        if len(lengths) == 0:
            rep.skip("%s per-word-length table" % fname, "no such table in the file; nothing compared for it")
        elif len(lengths) > 1:
            c.fail("per-word-length table", len(lengths), 1, "number of such tables in the file")
        else:
            compare_length_table(c, rep, fname, lengths[0], exp_len, wanted, set(unavailable))
        c.note("recomputed_length_rows", {str(n): {"starts": k, "pct": [round(x, 4) for x in pc]}
                                          for n, (k, pc) in exp_len.items()})
        other = len(tables) - len(groups) - len(lengths)
        if other > 0:
            rep.skip(fname, "%d table(s) of another kind in the file were not compared" % other)

        cp = rep.new("%s: numbers in the title and the prose" % fname)
        first, not_found = prose_common(cp, text, fname, budget, p, k_total, int(cs.sum()))
        m = re.search(r"random (\d+)-generator start", first)
        if m:
            cp.eq_int("title: rank", int(m.group(1)), 3)
        else:
            not_found.append("rank in the title")
        m = re.search(r"lengths (\d+) to (\d+)", text)
        if m:
            cp.eq("prose: length range", [int(m.group(1)), int(m.group(2))], [a, b])
        else:
            not_found.append("length range")
        if not_found:
            cp.note("not_found_in_the_text", not_found)


# --------------------------------------------------------------------------- driver

def run(argv, rep):
    results_dir, dataset = argv[1], argv[2]
    minutes = float(argv[5]) if len(argv) > 5 else 30.0     # argv[4] (workers) is accepted and unused
    deadline = time.time() + minutes * 60.0

    n_dataset = None
    if os.path.isfile(dataset):
        with open(dataset, encoding="utf-8") as f:
            n_dataset = sum(1 for line in f if line.strip())
    else:
        rep.skip(dataset, "DATASET absent; the number of presentations is not cross-checked")

    names = sorted(os.listdir(results_dir))
    present = set(names)

    # ---- rank 4 / 5 (small files first)
    rn = {}
    for r in (4, 5):
        rn["rankn_bf_ms640_b1000_cap24_r%d" % r] = (1000, 24, r)
    for name in names:
        m = RN_FILE.match(name)
        if m:
            rn[m.group(1)] = (int(m.group(2)), int(m.group(3)), int(m.group(4)))
    for stem in sorted(rn):
        budget, cap, rank = rn[stem]
        s_name = stem + "_summary.json"
        m_name = stem + "_control_vs_start.md"
        d = load_rankn(rep, results_dir, stem, budget, cap, rank, deadline)
        if n_dataset is not None and d is not None:
            d["check"].eq_int("presentations vs lines of DATASET", d["p"], n_dataset)
        for name, fn in ((s_name, "summary"), (m_name, "md")):
            if name not in present:
                rep.skip(name, "absent")
            elif d is None:
                rep.skip(name, "raw %s.npz absent or unusable; not compared" % stem)
            elif fn == "summary":
                check_rankn_summary(rep, os.path.join(results_dir, name), name, d)
            else:
                check_rankn_md(rep, os.path.join(results_dir, name), name, d, budget, rank)

    # ---- rank 3
    r3 = []
    for name in names:
        if "_control_vs_start" not in name or not name.endswith(".md"):
            continue
        m = R3_MD.match(name)
        if m:
            a = int(m.group(4)) if m.group(4) is not None else None
            b = int(m.group(5)) if m.group(5) is not None else None
            r3.append((int(m.group(2)), b if b is not None else 0, a if a is not None else 0, name, m.group(1), a, b))
        elif not RN_FILE.match(name):
            rep.skip(name, "file name not recognised; not compared")
    for budget in (1000, 10000):
        if not any(t[0] == budget for t in r3):
            rep.skip("rank3_bf_ms640_b%d_cap24_control_vs_start_L<a>-<b>.md" % budget, "none present")
    worker = Rank3(rep, results_dir, n_dataset, deadline)
    for budget, _b, _a, name, stem, a, b in sorted(r3):     # short ranges first, so the time box cuts the big files
        worker.check_md(name, stem, budget, a, b)


def main():
    if len(sys.argv) < 4:
        sys.stderr.write("usage: python3 %s <RESULTS_DIR> <DATASET> <OUT_JSON> [workers] [minutes]\n" % SCRIPT)
        return 1
    out_json = sys.argv[3]
    rep = Report()
    crash = None
    try:
        run(sys.argv, rep)
    except Exception:                                              # noqa: BLE001
        crash = traceback.format_exc()
        sys.stderr.write(crash)

    total = sum(c.mismatches for c in rep.checks)
    compared = sum(c.compared for c in rep.checks)
    out = {
        "script": SCRIPT,
        "checks": [{"name": c.name, "compared": c.compared, "mismatches": c.mismatches, "detail": c.detail}
                   for c in rep.checks],
        "mismatches": total,
        "compared": compared,
        "skipped": rep.skipped,
        "first_mismatches": rep.first[:MAX_FIRST],
    }
    if crash is not None:
        out["crash"] = crash
    try:
        with open(out_json, "w", encoding="utf-8") as f:
            json.dump(clean(out), f, indent=1, allow_nan=False)
            f.write("\n")
    except Exception:                                              # noqa: BLE001
        sys.stderr.write(traceback.format_exc())
        crash = crash or "could not write OUT_JSON"

    for c in rep.checks:
        if c.mismatches:
            status = "MISMATCH"
        elif c.compared == 0:
            status = "NOTHING COMPARED"
        else:
            status = "ok"
        print("[%s] %s: compared=%d mismatches=%d" % (status, c.name, c.compared, c.mismatches))
    for s in rep.skipped:
        print("[skipped] %s" % s)
    print("TOTAL %s: checks=%d compared=%d mismatches=%d skipped=%d%s" % (
        SCRIPT, len(rep.checks), compared, total, len(rep.skipped),
        " CRASH" if crash is not None else (" (NOTHING COMPARED)" if compared == 0 else "")))
    if crash is not None:
        return 1
    return 3 if total else 0


if __name__ == "__main__":
    sys.exit(main())
