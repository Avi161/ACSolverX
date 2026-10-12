#!/usr/bin/env python3
"""indep_relsub_cov.py -- independent recomputation, from the raw result files,
of three parts of rank3_bf_ms640_b<B>_cap24_summary.json (B = 1000 and 10000):

  * the whole `relsub` block (relator subwords searched in rank 3, and their
    join with the change-of-variables (CoV) sweep),
  * `control_at_larger_budgets`,
  * the control columns of views["<B>"].gained_presentations_priced.

Run from the repo root:

    python3 -I -u indep_relsub_cov.py <RESULTS_DIR> <DATASET> <OUT_JSON> [workers] [minutes]

Only the standard library and numpy are imported; nothing comes from the
repository.  Exit code 0 = no mismatch, 3 = at least one mismatch (a check
that compared 0 items counts as one), 1 = crash.

`workers` is accepted and ignored (nothing here searches).  `minutes` is a
wall-clock box: stages that have not started when it runs out are listed as
skipped.
"""

import gzip
import json
import math
import os
import re
import statistics
import sys
import time
import traceback

import numpy as np

SCRIPT = "indep_relsub_cov.py"
BUDGETS = (1000, 10000)
CAP = 24
MAX_LEN = 10
COV_DEFAULT = "results/stable_ac/cov_all/cov_all_suballpxyb8_ms640_b100000.jsonl.gz"
COV_BUDGET = 100000
LARGER_BUDGETS = (100, 1000, 10000, 100000)
EXPECTED_PRESENTATIONS = 640
TOL = 1e-9
PER_CHECK_EXAMPLES = 8
MAX_FIRST = 50

LETTER_TO_INT = {"x": 1, "y": 2, "z": 3, "a": 4, "b": 5,
                 "X": -1, "Y": -2, "Z": -3, "A": -4, "B": -5}
INT_TO_LETTER = dict((v, k) for k, v in LETTER_TO_INT.items())


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------

def is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def word_to_tuple(s):
    """'xY' -> (1, -2).  Raises KeyError on a letter outside x,y,z,a,b / capitals."""
    return tuple(LETTER_TO_INT[c] for c in s)


def tuple_to_word(t):
    return "".join(INT_TO_LETTER[v] for v in t)


def inverse(t):
    return tuple(-v for v in reversed(t))


def fold(t):
    """The larger of the integer tuples w and w^-1 (ordinary tuple comparison)."""
    inv = inverse(t)
    if t >= inv:
        return t
    return inv


def free_reduce(t):
    out = []
    for v in t:
        if out and out[-1] == -v:
            out.pop()
        else:
            out.append(v)
    return out


def cyclic_reduce(t):
    w = free_reduce(t)
    i = 0
    j = len(w) - 1
    while i < j and w[i] == -w[j]:
        i += 1
        j -= 1
    return tuple(w[i:j + 1])


def relator_subwords(relators):
    """Relator-subword word set of a presentation.

    relators: cyclically reduced relators (tuples of ints).
    Returns {folded word (tuple): whole (bool)}.  For each relator r and each
    length 2 <= l <= |r|: every window of length l of r written twice in a row,
    starting at positions 0..|r|-1, folded.  whole = arises with l = |r| from
    either relator.
    """
    words = {}
    for r in relators:
        n = len(r)
        if n < 2:
            continue
        rr = tuple(r) + tuple(r)
        for length in range(2, n + 1):
            whole = (length == n)
            for start in range(n):
                w = fold(rr[start:start + length])
                if whole:
                    words[w] = True
                elif w not in words:
                    words[w] = False
    return words


def open_text(path):
    """Open a text file that may or may not be gzip-compressed (magic bytes)."""
    with open(path, "rb") as fh:
        magic = fh.read(2)
    if magic == b"\x1f\x8b":
        return gzip.open(path, "rt", encoding="utf-8")
    return open(path, "r", encoding="utf-8")


def json_lines(path):
    """Yield (line number, object) for every non-blank line, one line at a time.

    A line that is not valid JSON is yielded as a string (not a dict), so every
    loader counts it as one bad row instead of the whole run crashing.
    """
    with open_text(path) as fh:
        lineno = 0
        for line in fh:
            lineno += 1
            if not line or line.isspace():
                continue
            try:
                obj = json.loads(line)
            except ValueError as exc:
                obj = "unparsable JSON line: %s" % exc
            yield lineno, obj


def same_value(got, want):
    """got = value in the file under test, want = recomputed value.

    Booleans and None must match exactly, integer counts exactly, floats
    within 1e-9.
    """
    if isinstance(want, bool) or isinstance(got, bool):
        return isinstance(want, bool) and isinstance(got, bool) and got == want
    if want is None or got is None:
        return want is None and got is None
    if is_int(want):
        if not is_num(got):
            return False
        return float(got) == float(want)
    if isinstance(want, float):
        if not is_num(got):
            return False
        g = float(got)
        if math.isnan(want) or math.isnan(g):
            return math.isnan(want) and math.isnan(g)
        return abs(g - want) <= TOL
    return got == want


def jsonable(obj):
    if isinstance(obj, dict):
        return dict((str(k), jsonable(v)) for k, v in obj.items())
    if isinstance(obj, (list, tuple)):
        return [jsonable(v) for v in obj]
    if isinstance(obj, (set, frozenset)):
        return [jsonable(v) for v in sorted(obj, key=repr)]
    if isinstance(obj, np.ndarray):
        return jsonable(obj.tolist())
    if isinstance(obj, np.generic):
        return jsonable(obj.item())
    if isinstance(obj, bool) or obj is None or isinstance(obj, (int, str)):
        return obj
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return repr(obj)
        return obj
    return repr(obj)


def bump(counter, key):
    counter[key] = counter.get(key, 0) + 1


# --------------------------------------------------------------------------
# report
# --------------------------------------------------------------------------

class Check(object):
    def __init__(self, name):
        self.name = name
        self.compared = 0
        self.mismatches = 0
        self.detail = {}
        self.examples = []
        # other readings of the same numbers: written out, never compared
        self.report_only = {}

    def add(self, ok, example=None):
        self.compared += 1
        if not ok:
            self.mismatches += 1
            if len(self.examples) < PER_CHECK_EXAMPLES:
                ex = {"check": self.name}
                if example:
                    ex.update(example)
                self.examples.append(ex)
        return bool(ok)


class Report(object):
    def __init__(self):
        self.checks = []
        self.skipped = []
        self.info = {}

    def new(self, name):
        chk = Check(name)
        self.checks.append(chk)
        return chk

    def skip(self, what, why):
        self.skipped.append("%s: %s" % (what, why))

    def build(self, crash=None):
        out_checks = []
        per_check_examples = []
        total = 0
        for chk in self.checks:
            mism = chk.mismatches
            detail = dict(chk.detail)
            examples = list(chk.examples)
            if chk.compared == 0:
                status = "ZERO_COMPARED"
                mism = 1
                detail["zero_compared"] = ("0 items compared: counted as 1 mismatch, "
                                           "never as a pass")
                examples = [{"check": chk.name, "why": "0 items compared"}]
            elif mism:
                status = "MISMATCH"
            else:
                status = "ok"
            total += mism
            entry = {"name": chk.name, "compared": chk.compared,
                     "mismatches": mism, "status": status, "detail": detail}
            if chk.report_only:
                entry["report_only"] = chk.report_only
            out_checks.append(entry)
            per_check_examples.append(examples)
        first = []
        depth = 0
        while len(first) < MAX_FIRST:
            took = False
            for examples in per_check_examples:
                if depth < len(examples) and len(first) < MAX_FIRST:
                    first.append(examples[depth])
                    took = True
            if not took:
                break
            depth += 1
        doc = {"script": SCRIPT, "checks": out_checks, "mismatches": total,
               "skipped": list(self.skipped), "first_mismatches": first,
               "info": dict(self.info)}
        if crash is not None:
            doc["crash"] = crash
        return jsonable(doc), total


def compare_leaves(chk, prefix, got_block, want_block, unverified, ignore=()):
    """Compare every leaf of want_block (recomputed) with got_block (summary)."""
    if not isinstance(got_block, dict):
        chk.add(False, {"key": prefix, "why": "missing or not an object in the summary",
                        "summary": got_block})
        return
    for key in want_block:
        want = want_block[key]
        path = "%s.%s" % (prefix, key)
        if isinstance(want, dict):
            compare_leaves(chk, path, got_block.get(key), want, unverified)
        elif key not in got_block:
            chk.add(False, {"key": path, "why": "missing in the summary", "recomputed": want})
        else:
            chk.add(same_value(got_block[key], want),
                    {"key": path, "summary": got_block[key], "recomputed": want})
    for key in got_block:
        if key not in want_block and key not in ignore:
            unverified.append("%s.%s" % (prefix, key))


# --------------------------------------------------------------------------
# loaders
# --------------------------------------------------------------------------

def load_dataset(path, rep):
    """List of presentations: raw relators, their strings, the cyclically
    reduced forms and the relator-subword word set.

    The check is structural only (640 lines; zeros only as trailing padding;
    letters in x,y,X,Y; no empty relator).  How many relators are not already
    cyclically reduced is reported in the detail, not counted as a mismatch:
    the word set is always built from the cyclic reduction.
    """
    chk = rep.new("dataset:lines_and_relators_well_formed")
    with open(path, "r", encoding="utf-8") as fh:
        lines = fh.read().split("\n")
    while lines and not lines[-1].strip():
        lines.pop()
    dataset = []
    not_reduced = 0
    not_free = 0
    for index, line in enumerate(lines):
        vals = json.loads(line)
        if not isinstance(vals, list) or len(vals) % 2 != 0:
            raise ValueError("dataset line %d is not a list of even length" % index)
        for v in vals:
            if not is_int(v):
                raise ValueError("dataset line %d has a non-integer entry" % index)
        half = len(vals) // 2
        entry = {}
        for name, part in (("r1", vals[:half]), ("r2", vals[half:])):
            letters = tuple(v for v in part if v != 0)
            zeros_trailing = (tuple(part[:len(letters)]) == letters)
            in_xy = all(v in (1, 2, -1, -2) for v in letters)
            cyc = cyclic_reduce(letters)
            reduced = (cyc == letters)
            if not reduced:
                not_reduced += 1
            if tuple(free_reduce(letters)) != letters:
                not_free += 1
            chk.add(zeros_trailing and in_xy and len(letters) >= 1,
                    {"pres_id": index, "relator": name, "letters": list(letters),
                     "zeros_only_trailing": zeros_trailing, "letters_in_xy": in_xy,
                     "cyclically_reduced": reduced})
            entry[name] = letters
            entry[name + "s"] = tuple_to_word(letters)
            entry[name + "c"] = cyc
        entry["subwords"] = relator_subwords([entry["r1c"], entry["r2c"]])
        dataset.append(entry)
    chk.add(len(dataset) == EXPECTED_PRESENTATIONS,
            {"why": "number of dataset lines", "lines": len(dataset),
             "expected": EXPECTED_PRESENTATIONS})
    chk.detail = {"presentations": len(dataset),
                  "relators_not_cyclically_reduced": not_reduced,
                  "relators_not_freely_reduced": not_free,
                  "expected_relsub_words": sum(len(e["subwords"]) for e in dataset),
                  "expected_relsub_words_proper": sum(
                      1 for e in dataset for w in e["subwords"] if not e["subwords"][w])}
    return dataset


def load_control(path, budget, dataset, chk):
    """{pres_id: (solved, nodes)} from <stem>_control.jsonl, with row checks."""
    n_pres = len(dataset)
    ctrl = {}
    problems = {}
    n_rows = 0
    for lineno, row in json_lines(path):
        n_rows += 1
        bad = []
        if not isinstance(row, dict):
            chk.add(False, {"line": lineno, "why": "row is not an object"})
            continue
        p = row.get("pres_id")
        if not is_int(p) or not (0 <= p < n_pres):
            bad.append("pres_id_invalid")
            p = None
        elif p in ctrl:
            bad.append("pres_id_duplicate")
        solved = row.get("solved")
        nodes = row.get("nodes_explored")
        plen = row.get("path_length")
        if not isinstance(solved, bool):
            bad.append("solved_not_bool")
        if not is_int(nodes):
            bad.append("nodes_explored_not_int")
            nodes = None
        if row.get("node_budget") != budget:
            bad.append("node_budget_differs")
        if solved is True and not (is_int(plen) and plen >= 0):
            bad.append("solved_without_path_length")
        if solved is False and not (plen is None or (is_int(plen) and plen < 0)):
            bad.append("unsolved_with_path_length")
        if p is not None:
            if row.get("r1") != dataset[p]["r1s"]:
                bad.append("r1_differs_from_dataset")
            if row.get("r2") != dataset[p]["r2s"]:
                bad.append("r2_differs_from_dataset")
            if p not in ctrl:
                ctrl[p] = (solved is True, nodes)
        for b in bad:
            bump(problems, b)
        chk.add(not bad, {"line": lineno, "pres_id": row.get("pres_id"), "problems": bad})
    missing = 0
    for p in range(n_pres):
        if p not in ctrl:
            missing += 1
        chk.add(p in ctrl, {"pres_id": p, "why": "no control row for this presentation"})
    chk.detail = {"rows": n_rows, "presentations_with_a_row": len(ctrl),
                  "presentations_without_a_row": missing, "problems": problems,
                  "solved": sum(1 for v in ctrl.values() if v[0])}
    return ctrl


def load_relsub(path, budget, dataset, chk):
    """Relsub rows grouped by presentation, with per-row field checks.

    Stored per row: (z_word string, z_word tuple or None, is_proper as written,
    solved (bool), nodes or None).
    """
    n_pres = len(dataset)
    by_pres = {}
    problems = {}
    n_rows = 0
    n_proper = 0
    for lineno, row in json_lines(path):
        n_rows += 1
        if not isinstance(row, dict):
            chk.add(False, {"line": lineno, "why": "row is not an object"})
            continue
        bad = []
        p = row.get("pres_id")
        if not is_int(p) or not (0 <= p < n_pres):
            bad.append("pres_id_invalid")
            p = None
        zs = row.get("z_word")
        zt = None
        if isinstance(zs, str) and zs:
            try:
                zt = word_to_tuple(zs)
            except KeyError:
                bad.append("z_word_unknown_letter")
            else:
                if any(abs(v) > 2 for v in zt):
                    bad.append("z_word_not_in_x_y")
        else:
            bad.append("z_word_missing_or_empty")
        is_proper = row.get("is_proper")
        if not isinstance(is_proper, bool):
            bad.append("is_proper_not_bool")
        if is_proper is True:
            n_proper += 1
        solved = row.get("solved")
        if not isinstance(solved, bool):
            bad.append("solved_not_bool")
        nodes = row.get("nodes_explored")
        if not is_int(nodes):
            bad.append("nodes_explored_not_int")
            nodes = None
        plen = row.get("path_length")
        if solved is True and not (is_int(plen) and plen >= 0):
            bad.append("solved_without_path_length")
        if solved is False and not (plen is None or (is_int(plen) and plen < 0)):
            bad.append("unsolved_with_path_length")
        if row.get("family_tag") != "relsub":
            bad.append("family_tag_not_relsub")
        if "node_budget" in row and row.get("node_budget") != budget:
            bad.append("node_budget_differs")
        if "max_relator_length_cap" in row and row.get("max_relator_length_cap") != CAP:
            bad.append("cap_differs")
        if isinstance(zs, str):
            if "z_relator" in row and row.get("z_relator") != "Z" + zs:
                bad.append("z_relator_not_Z_plus_word")
            if "z_len" in row and row.get("z_len") != len(zs):
                bad.append("z_len_differs")
        if p is not None:
            if row.get("r1") != dataset[p]["r1s"]:
                bad.append("r1_differs_from_dataset")
            if row.get("r2") != dataset[p]["r2s"]:
                bad.append("r2_differs_from_dataset")
            if "name" in row and row.get("name") != "ms640_%d" % p:
                bad.append("name_differs")
            by_pres.setdefault(p, []).append((zs, zt, is_proper, solved is True, nodes))
        for b in bad:
            bump(problems, b)
        chk.add(not bad, {"line": lineno, "pres_id": row.get("pres_id"),
                          "z_word": zs, "problems": bad})
    chk.detail = {"file": os.path.basename(path), "rows": n_rows, "rows_is_proper": n_proper,
                  "presentations_with_rows": len(by_pres), "problems": problems}
    return {"by_pres": by_pres, "n_rows": n_rows, "n_proper": n_proper}


def find_cov_file(results_dir):
    env = os.environ.get("COV_FILE")
    base = env if env else COV_DEFAULT
    candidates = [base]
    if base.endswith(".gz"):
        candidates.append(base[:-3])
    else:
        candidates.append(base + ".gz")
    if not env:
        name = os.path.basename(COV_DEFAULT)
        candidates.append(os.path.join(results_dir, name))
        candidates.append(os.path.join(results_dir, name[:-3]))
    for cand in candidates:
        if os.path.isfile(cand):
            return cand, candidates
    return None, candidates


def load_cov(path, dataset, rep, deadline):
    """One streaming pass over the CoV sweep file.  Keeps only:
    ctrl[p] = (solved, nodes) of the control row at 100,000;
    by_word[p][fold(z_word)] = fewest nodes over the solved non-control rows
    with that word (None if no such row solves); every non-control cap.
    Returns None if the time box ran out before the end of the file.
    """
    n_pres = len(dataset)
    chk_f = rep.new("cov:rows_fields")
    chk_r = rep.new("cov:orig_relators_match_dataset")
    ctrl = {}
    ctrl_rows = {}
    ctrl_conflict = set()
    by_word = {}
    raw_words = {}
    caps = []
    budgets = {}
    problems = {}
    n_rows = 0
    n_ctrl = 0
    n_non = 0
    n_not_folded = 0
    timed_out = False
    for lineno, row in json_lines(path):
        n_rows += 1
        if n_rows % 20000 == 0 and time.time() > deadline:
            timed_out = True
            break
        if not isinstance(row, dict):
            chk_f.add(False, {"line": lineno, "why": "row is not an object"})
            continue
        bad = []
        p = row.get("pres_id")
        if not is_int(p) or not (0 <= p < n_pres):
            bad.append("pres_id_invalid")
            p = None
        is_control = row.get("is_control")
        if not isinstance(is_control, bool):
            bad.append("is_control_not_bool")
        solved = row.get("solved")
        if not isinstance(solved, bool):
            bad.append("solved_not_bool")
        nodes = row.get("nodes_explored")
        if not is_int(nodes):
            bad.append("nodes_explored_not_int")
            nodes = None
        nb = row.get("node_budget")
        bump(budgets, str(nb))
        if nb != COV_BUDGET:
            bad.append("node_budget_not_100000")
        zs = row.get("z_word")
        if is_control is True:
            n_ctrl += 1
            if zs is not None:
                bad.append("control_row_with_z_word")
            if p is not None:
                val = (solved is True, nodes)
                if p in ctrl:
                    ctrl_rows[p] += 1
                    if ctrl[p] != val:
                        ctrl_conflict.add(p)
                else:
                    ctrl[p] = val
                    ctrl_rows[p] = 1
        elif is_control is False:
            n_non += 1
            cap = row.get("max_relator_length_cap")
            if is_num(cap):
                caps.append(cap)
            else:
                bad.append("cap_not_a_number")
            w = None
            if isinstance(zs, str) and zs:
                try:
                    zt = word_to_tuple(zs)
                except KeyError:
                    bad.append("z_word_unknown_letter")
                else:
                    w = fold(zt)
                    if w != zt:
                        n_not_folded += 1
                    if p is not None:
                        # words as written, for a report-only reading of the join
                        raw_words.setdefault(p, set()).add(zt)
            else:
                bad.append("z_word_missing_or_empty")
            if p is not None and w is not None:
                d = by_word.get(p)
                if d is None:
                    d = {}
                    by_word[p] = d
                if w not in d:
                    d[w] = None
                if solved is True and nodes is not None:
                    if d[w] is None or nodes < d[w]:
                        d[w] = nodes
        if p is not None and ("r1_orig" in row or "r2_orig" in row):
            chk_r.add(row.get("r1_orig") == dataset[p]["r1s"]
                      and row.get("r2_orig") == dataset[p]["r2s"],
                      {"line": lineno, "pres_id": p, "r1_orig": row.get("r1_orig"),
                       "r2_orig": row.get("r2_orig"), "dataset_r1": dataset[p]["r1s"],
                       "dataset_r2": dataset[p]["r2s"]})
        for b in bad:
            bump(problems, b)
        chk_f.add(not bad, {"line": lineno, "pres_id": row.get("pres_id"), "problems": bad})
    chk_f.detail = {"file": path, "rows": n_rows, "control_rows": n_ctrl,
                    "non_control_rows": n_non, "node_budget_values": budgets,
                    "problems": problems,
                    "non_control_z_words_not_their_own_fold": n_not_folded,
                    "distinct_presentation_word_pairs": sum(len(d) for d in by_word.values()),
                    "presentations_with_non_control_rows": len(by_word),
                    "readme_says": "114,682 rows = 640 controls + 114,042 CoV rows"}
    if timed_out:
        note = "time box: stopped after %d rows (partial); the other CoV checks are skipped" % n_rows
        chk_f.detail["time_box"] = note
        chk_r.detail["time_box"] = note
        return None
    chk_c = rep.new("cov:one_control_row_per_presentation")
    for p in range(n_pres):
        chk_c.add(ctrl_rows.get(p, 0) == 1 and p not in ctrl_conflict,
                  {"pres_id": p, "control_rows": ctrl_rows.get(p, 0),
                   "conflicting_copies": p in ctrl_conflict})
    chk_c.detail = {"presentations_with_a_control_row": len(ctrl),
                    "presentations_with_conflicting_control_rows": sorted(ctrl_conflict)}
    best = {}
    for p, d in by_word.items():
        vals = [v for v in d.values() if v is not None]
        if vals:
            best[p] = min(vals)
    median_cap = None
    median_low = None
    median_high = None
    if caps:
        median_cap = float(statistics.median(caps))
        median_low = statistics.median_low(caps)
        median_high = statistics.median_high(caps)
    return {"path": path, "ctrl": ctrl, "by_word": by_word, "best": best,
            "median_cap": median_cap, "n_rows": n_rows, "n_ctrl": n_ctrl, "n_non": n_non,
            "raw_words": raw_words, "n_not_folded": n_not_folded,
            "median_cap_low": median_low, "median_cap_high": median_high}


# --------------------------------------------------------------------------
# relsub checks and statistics
# --------------------------------------------------------------------------

def check_relsub_words(tag, dataset, relsub, rep):
    by_pres = relsub["by_pres"]
    chk_fold = rep.new(tag + ":relsub_zword_is_own_fold")
    chk_dup = rep.new(tag + ":relsub_one_row_per_word")
    chk_set = rep.new(tag + ":relsub_wordset_per_presentation")
    chk_prop = rep.new(tag + ":relsub_is_proper_flag")
    n_missing = 0
    n_extra = 0
    n_whole_rows = 0
    for p in range(len(dataset)):
        expected = dataset[p]["subwords"]
        rows = by_pres.get(p, [])
        seen = set()
        got = set()
        unparsed = []
        for (zs, zt, is_proper, solved, nodes) in rows:
            if zt is None:
                chk_fold.add(False, {"pres_id": p, "z_word": zs, "why": "word cannot be parsed"})
                unparsed.append(zs)
            else:
                chk_fold.add(fold(zt) == zt,
                             {"pres_id": p, "z_word": zs, "fold": tuple_to_word(fold(zt))})
                got.add(zt)
            key = repr(zs)
            chk_dup.add(key not in seen, {"pres_id": p, "z_word": zs,
                                          "why": "more than one row for this word"})
            seen.add(key)
            if zt is not None and zt in expected:
                whole = expected[zt]
                if whole:
                    n_whole_rows += 1
                chk_prop.add(is_proper is (not whole),
                             {"pres_id": p, "z_word": zs, "is_proper_in_row": is_proper,
                              "whole_rotation_of_a_relator": whole})
        missing = sorted(w for w in expected if w not in got)
        extra = sorted(w for w in got if w not in expected)
        n_missing += len(missing)
        n_extra += len(extra) + len(unparsed)
        chk_set.add(not missing and not extra and not unparsed,
                    {"pres_id": p, "expected_words": len(expected), "rows": len(rows),
                     "missing": [tuple_to_word(w) for w in missing[:5]],
                     "n_missing": len(missing),
                     "extra": [tuple_to_word(w) for w in extra[:5]] + unparsed[:5],
                     "n_extra": len(extra) + len(unparsed)})
    chk_set.detail = {"what": "set of row z_words == relator-subword word set, per presentation",
                      "words_missing_in_rows": n_missing, "rows_with_unexpected_word": n_extra,
                      "expected_words_total": sum(len(e["subwords"]) for e in dataset)}
    chk_fold.detail = {"z_words_not_their_own_fold": chk_fold.mismatches, "expected": 0}
    chk_prop.detail = {"rows_whose_word_is_a_whole_rotation": n_whole_rows}


def relsub_stats(by_pres, ctrl, proper_only, n_pres=None):
    """Returns (stats compared with the summary, denominators, report_only).

    report_only holds other readings of the same statistics (other
    denominators); they are written out so a mismatch can be diagnosed from
    one run, and never compared.
    """
    some = 0
    gained = 0
    rates = []
    faster_some = 0
    fracs = []
    no_control = 0
    tot_rows = 0
    tot_solved = 0
    gain_rates = []
    fracs_of_solved = []
    for p in sorted(by_pres):
        rows = [r for r in by_pres[p] if (r[2] is True or not proper_only)]
        if not rows:
            continue
        c = ctrl.get(p)
        if c is None:
            no_control += 1
        c_solved = bool(c is not None and c[0])
        c_nodes = c[1] if c is not None else None
        n_solved = sum(1 for r in rows if r[3])
        rates.append(n_solved / float(len(rows)))
        tot_rows += len(rows)
        tot_solved += n_solved
        if n_solved > 0:
            some += 1
            if not c_solved:
                gained += 1
        if not c_solved:
            gain_rates.append(n_solved / float(len(rows)))
        if c_solved and c_nodes is not None:
            n_faster = sum(1 for r in rows if r[3] and r[4] is not None and r[4] < c_nodes)
            fracs.append(n_faster / float(len(rows)))
            if n_solved > 0:
                fracs_of_solved.append(n_faster / float(n_solved))
            if n_faster > 0:
                faster_some += 1
    stats = {"solved_by_some_subword": some,
             "gained_over_control": gained,
             "mean_solve_rate": (math.fsum(rates) / len(rates)) if rates else None,
             "some_subword_faster_than_control": faster_some,
             "mean_fraction_faster_than_control": (math.fsum(fracs) / len(fracs)) if fracs else None}
    extra = {"presentations_with_such_rows": len(rates),
             "control_solved_presentations_with_such_rows": len(fracs),
             "presentations_without_control_row": no_control}
    try:
        def ratio(a, b):
            return (a / float(b)) if b else None
        n_ctrl_solved = sum(1 for v in ctrl.values() if v[0])
        report_only = {
            "what": "other readings of the same statistics; written out, never compared",
            "solve_rate_pooled_over_rows": ratio(tot_solved, tot_rows),
            "mean_solve_rate_over_all_presentations": ratio(math.fsum(rates), n_pres),
            "mean_fraction_faster_over_all_control_solved_presentations":
                ratio(math.fsum(fracs), n_ctrl_solved),
            "mean_fraction_faster_over_presentations_with_such_rows_control_unsolved_as_0":
                ratio(math.fsum(fracs), len(rates)),
            "mean_fraction_faster_or_gained_over_presentations_with_such_rows":
                ratio(math.fsum(fracs) + math.fsum(gain_rates), len(rates)),
            "mean_over_control_solved_of_faster_rows_over_solved_rows":
                ratio(math.fsum(fracs_of_solved), len(fracs_of_solved)),
            "some_subword_faster_or_gained": faster_some + gained,
            "control_solved_presentations": n_ctrl_solved,
            "all_presentations": n_pres}
    except Exception:
        report_only = {"error": traceback.format_exc()}
    return stats, extra, report_only


def vs_cov_block(by_pres, ctrl, cov, budget):
    control_set = set(p for p, v in ctrl.items() if v[0])
    rank3_set = set()
    for p, rows in by_pres.items():
        for r in rows:
            if r[2] is True and r[3]:
                rank3_set.add(p)
                break
    cov_set = set(p for p, m in cov["best"].items() if m <= budget)
    joined = 0
    neither = 0
    only_rank3 = 0
    only_cov = 0
    rank3_fewer = 0
    tie = 0
    cov_fewer = 0
    for p, rows in by_pres.items():
        words = cov["by_word"].get(p)
        if not words:
            continue
        for (zs, zt, is_proper, solved, nodes) in rows:
            if is_proper is not True or zt is None or zt not in words:
                continue
            joined += 1
            a = nodes if (solved and nodes is not None) else None
            m = words[zt]
            c = m if (m is not None and m <= budget) else None
            if a is None and c is None:
                neither += 1
            elif c is None:
                only_rank3 += 1
            elif a is None:
                only_cov += 1
            elif a < c:
                rank3_fewer += 1
            elif a == c:
                tie += 1
            else:
                cov_fewer += 1
    want = {"cov_file_budget": COV_BUDGET,
            "cov_median_cap": cov["median_cap"],
            "same_word_pairs_joined": joined,
            "same_word_neither": neither,
            "control": len(control_set),
            "rank3_subword_oracle": len(rank3_set),
            "cov_oracle": len(cov_set),
            "control_or_rank3": len(control_set | rank3_set),
            "control_or_cov": len(control_set | cov_set),
            "rank3_not_cov": len(rank3_set - cov_set),
            "cov_not_rank3": len(cov_set - rank3_set),
            "same_word_rank3_fewer_nodes": rank3_fewer,
            "same_word_tie": tie,
            "same_word_cov_fewer_nodes": cov_fewer,
            "same_word_only_rank3_solves": only_rank3,
            "same_word_only_cov_solves": only_cov}
    extra = {"control_source": "<stem>_control.jsonl (rank-3 run's control at budget B)",
             "rank3_not_cov_presentations": sorted(rank3_set - cov_set)[:50],
             "cov_not_rank3_presentations": sorted(cov_set - rank3_set)[:100]}
    # Other readings of the same block: written out, never compared.
    try:
        cov_control_at_b = set(p for p, v in cov["ctrl"].items()
                               if v[0] and v[1] is not None and v[1] <= budget)
        raw_words = cov.get("raw_words") or {}
        joined_folded = 0
        joined_raw = 0
        joined_any_row = 0
        for p, rows in by_pres.items():
            words = cov["by_word"].get(p) or {}
            raws = raw_words.get(p) or ()
            for (zs, zt, is_proper, solved, nodes) in rows:
                if zt is None:
                    continue
                if zt in words:
                    joined_any_row += 1
                if is_proper is True:
                    if fold(zt) in words:
                        joined_folded += 1
                    if zt in raws:
                        joined_raw += 1
        union_rank3 = control_set | rank3_set
        union_cov = control_set | cov_set
        report_only = {
            "what": "other readings of relsub.vs_cov; written out, never compared",
            "control_from_cov_file_cut_to_B": len(cov_control_at_b),
            "control_or_rank3_with_that_control": len(cov_control_at_b | rank3_set),
            "control_or_cov_with_that_control": len(cov_control_at_b | cov_set),
            "cov_oracle_including_control_rows": len(cov_set | cov_control_at_b),
            "rank3_not_cov_between_the_unions_with_control": len(union_rank3 - union_cov),
            "cov_not_rank3_between_the_unions_with_control": len(union_cov - union_rank3),
            "same_word_pairs_joined_relsub_word_folded_before_lookup": joined_folded,
            "same_word_pairs_joined_cov_word_as_written_not_folded": joined_raw,
            "same_word_pairs_joined_whole_rows_included": joined_any_row,
            "cov_non_control_z_words_not_their_own_fold": cov.get("n_not_folded"),
            "cov_median_cap_low": cov.get("median_cap_low"),
            "cov_median_cap_high": cov.get("median_cap_high")}
    except Exception:
        report_only = {"error": traceback.format_exc()}
    return want, extra, report_only


# --------------------------------------------------------------------------
# brute-force arrays (only to find the presentations some word solves)
# --------------------------------------------------------------------------

def scan_bruteforce(results_dir, stem, tag, budget, n_pres, wanted, rep, deadline):
    """Reads <stem>_L<n>.npz one at a time (the `_inv` files are not used).

    Returns None if no such file is present, else
    {"lengths": [...], "any_solved": [bool]*n_pres, "best": [int or None]*n_pres,
     "hits": {(pres_id, word): {...}}, "words_error": str or None,
     "incomplete": [present files that could not be used], "notes": [...]}.
    solved <=> path_len >= 0; nodes are cast from uint16 before use.
    """
    chk = None
    lengths = []
    any_solved = [False] * n_pres
    best = [None] * n_pres
    first_len = [None] * n_pres
    hits = {}
    words_error = None
    notes = []
    incomplete = []
    # Lengths 1..MAX_LEN, plus any longer <stem>_L<n>.npz that is in the
    # directory (the summary is built from every length file present).
    lens = set(range(1, MAX_LEN + 1))
    try:
        pat = re.compile(r"^%s_L([0-9]+)\.npz$" % re.escape(stem))
        for fn in os.listdir(results_dir):
            found = pat.match(fn)
            if found:
                lens.add(int(found.group(1)))
    except OSError:
        pass
    for n in sorted(lens):
        fname = "%s_L%d.npz" % (stem, n)
        path = os.path.join(results_dir, fname)
        if not os.path.isfile(path):
            rep.skip(fname, "file absent")
            continue
        if time.time() > deadline:
            rep.skip(fname, "time box reached before this file was read")
            incomplete.append("L%d not read (time box)" % n)
            continue
        if chk is None:
            chk = rep.new(tag + ":bruteforce_npz_files")
        with np.load(path, allow_pickle=False) as z:
            pres_ids = np.asarray(z["pres_ids"]).astype(np.int64).ravel()
            nodes = np.asarray(z["nodes"])
            path_len = np.asarray(z["path_len"])
            shape_ok = (nodes.ndim == 2 and path_len.shape == nodes.shape
                        and nodes.shape[0] == pres_ids.shape[0])
            chk.add(shape_ok, {"file": fname, "why": "array shapes disagree",
                               "nodes": list(nodes.shape), "path_len": list(path_len.shape),
                               "pres_ids": list(pres_ids.shape)})
            signed_ok = (path_len.dtype.kind == "i")
            chk.add(signed_ok, {"file": fname, "why": "path_len is not a signed integer array "
                                "(-1 = not solved cannot be read)",
                                "dtype": str(path_len.dtype)})
            if not shape_ok or not signed_ok:
                incomplete.append("L%d not used (shapes or dtype)" % n)
                continue
            n_words = int(nodes.shape[1])
            chk.add(n_words == 2 * 3 ** (n - 1),
                    {"file": fname, "why": "number of words is not 2*3^(n-1)",
                     "words": n_words, "expected": 2 * 3 ** (n - 1)})
            ids = [int(v) for v in pres_ids.tolist()]
            chk.add(sorted(ids) == list(range(n_pres)),
                    {"file": fname, "why": "pres_ids is not a permutation of 0..n-1",
                     "n_ids": len(ids)})
            meta = None
            try:
                m = np.asarray(z["meta"])
                mraw = m.item() if m.ndim == 0 else m.ravel()[0]
                if isinstance(mraw, bytes):
                    mraw = mraw.decode("utf-8")
                meta = json.loads(str(mraw))
            except Exception as exc:
                notes.append("L%d meta not readable: %r" % (n, exc))
            if isinstance(meta, dict):
                chk.add(meta.get("node_budget") == budget,
                        {"file": fname, "why": "meta.node_budget differs",
                         "meta": meta.get("node_budget"), "expected": budget})
                chk.add(meta.get("max_relator_length_cap") == CAP,
                        {"file": fname, "why": "meta.max_relator_length_cap differs",
                         "meta": meta.get("max_relator_length_cap"), "expected": CAP})
            solved = path_len >= 0
            row_any = solved.any(axis=1)
            pos = {}
            for i, p in enumerate(ids):
                if not (0 <= p < n_pres):
                    continue
                pos.setdefault(p, i)
                if not bool(row_any[i]):
                    continue
                row = nodes[i].astype(np.int64)
                least = int(row[solved[i]].min())
                any_solved[p] = True
                if first_len[p] is None:
                    first_len[p] = n
                if best[p] is None or least < best[p]:
                    best[p] = least
            want_here = [pw for pw in wanted if len(pw[1]) == n]
            if want_here and words_error is None:
                try:
                    raw = np.asarray(z["words"]).ravel().tolist()
                    index = {}
                    for j, w in enumerate(raw):
                        if isinstance(w, bytes):
                            w = w.decode("ascii")
                        index[str(w)] = j
                    chk.add(len(raw) == n_words,
                            {"file": fname, "why": "len(words) differs from the number of columns",
                             "words": len(raw), "columns": n_words})
                    for (p, w) in want_here:
                        j = index.get(w)
                        i = pos.get(p)
                        if j is None or i is None or j >= n_words:
                            hits[(p, w)] = {"found": False}
                        else:
                            hits[(p, w)] = {"found": True,
                                            "path_len": int(path_len[i, j]),
                                            "nodes": int(nodes[i, j])}
                except Exception as exc:
                    words_error = "%s: %r" % (fname, exc)
            lengths.append(n)
    if chk is not None:
        chk.detail = {"lengths_used": list(lengths), "notes": notes,
                      "present_but_not_used": list(incomplete),
                      "inverse_files": "not used (<stem>_L<n>_inv.npz)"}
    if not lengths and not incomplete:
        return None
    return {"lengths": lengths, "any_solved": any_solved, "best": best,
            "first_len": first_len, "hits": hits, "words_error": words_error,
            "notes": notes, "incomplete": incomplete}


def index_priced_rows(block):
    srows = {}
    problems = []
    if not isinstance(block, dict):
        return srows, problems
    rows = block.get("rows")
    if not isinstance(rows, list):
        problems.append({"why": "gained_presentations_priced.rows is not a list"})
        return srows, problems
    for i, r in enumerate(rows):
        pid = r.get("pres_id") if isinstance(r, dict) else None
        if not is_int(pid):
            problems.append({"row": i, "why": "row without an integer pres_id"})
        elif pid in srows:
            problems.append({"row": i, "pres_id": pid, "why": "second row for this pres_id"})
        else:
            srows[pid] = r
    return srows, problems


# --------------------------------------------------------------------------
# one budget
# --------------------------------------------------------------------------

def run_budget(budget, results_dir, dataset, cov, cov_why, rep, deadline):
    tag = "b%d" % budget
    stem = "rank3_bf_ms640_b%d_cap%d" % (budget, CAP)
    n_pres = len(dataset)
    if time.time() > deadline:
        rep.skip(tag, "time box reached before this budget was started; nothing compared")
        return

    # ---- the summary under test
    summary = None
    spath = os.path.join(results_dir, stem + "_summary.json")
    if os.path.isfile(spath):
        with open(spath, "r", encoding="utf-8") as fh:
            summary = json.load(fh)
        if not isinstance(summary, dict):
            summary = {}
    else:
        rep.skip(stem + "_summary.json", "file absent; nothing to compare with at this budget")

    # ---- the control at budget B
    ctrl = None
    cpath = os.path.join(results_dir, stem + "_control.jsonl")
    if os.path.isfile(cpath):
        ctrl = load_control(cpath, budget, dataset, rep.new(tag + ":control_rows"))
    else:
        rep.skip(stem + "_control.jsonl", "file absent")

    # ---- the relsub rows
    relsub = None
    rpath = None
    for name in (stem + "_relsub.jsonl", stem + "_relsub.jsonl.gz"):
        cand = os.path.join(results_dir, name)
        if os.path.isfile(cand):
            rpath = cand
            break
    if rpath is None:
        rep.skip(stem + "_relsub.jsonl[.gz]", "file absent")
    else:
        relsub = load_relsub(rpath, budget, dataset, rep.new(tag + ":relsub_rows_fields"))
        check_relsub_words(tag, dataset, relsub, rep)

    def needs(pairs):
        return ", ".join(label for label, value in pairs if value is None)

    unverified = []

    # ---- relsub block: rows, rows_proper, proper, all
    name = tag + ":summary_relsub_counts_and_stats"
    lacking = needs((("relsub rows", relsub), ("control file", ctrl), ("summary", summary)))
    if lacking:
        rep.skip(name, "needs " + lacking)
    else:
        proper_stats, proper_extra, proper_ro = relsub_stats(relsub["by_pres"], ctrl, True,
                                                             n_pres)
        all_stats, all_extra, all_ro = relsub_stats(relsub["by_pres"], ctrl, False, n_pres)
        want = {"rows": relsub["n_rows"], "rows_proper": relsub["n_proper"],
                "proper": proper_stats, "all": all_stats}
        chk = rep.new(name)
        compare_leaves(chk, "relsub", summary.get("relsub"), want, unverified,
                       ignore=("vs_cov",))
        chk.detail = {"recomputed": want, "proper_denominators": proper_extra,
                      "all_denominators": all_extra}
        chk.report_only = {"proper": proper_ro, "all": all_ro}

    # ---- relsub.vs_cov
    name = tag + ":summary_relsub_vs_cov"
    lacking = needs((("relsub rows", relsub), ("control file", ctrl), ("summary", summary)))
    if cov is None:
        rep.skip(name, cov_why)
    elif lacking:
        rep.skip(name, "needs " + lacking)
    else:
        want, extra, vs_ro = vs_cov_block(relsub["by_pres"], ctrl, cov, budget)
        chk = rep.new(name)
        block = summary.get("relsub")
        got = block.get("vs_cov") if isinstance(block, dict) else None
        compare_leaves(chk, "relsub.vs_cov", got, want, unverified)
        chk.detail = {"recomputed": want, "notes": extra}
        chk.report_only = vs_ro
        if isinstance(got, dict):
            parts = [got.get(k) for k in ("same_word_neither", "same_word_only_rank3_solves",
                                          "same_word_only_cov_solves",
                                          "same_word_rank3_fewer_nodes", "same_word_tie",
                                          "same_word_cov_fewer_nodes")]
            if all(is_int(v) for v in parts):
                chk.detail["summary_six_buckets_sum"] = sum(parts)
                chk.detail["summary_same_word_pairs_joined"] = got.get("same_word_pairs_joined")

    # ---- control_at_larger_budgets
    name = tag + ":summary_control_at_larger_budgets"
    if cov is None:
        rep.skip(name, cov_why)
    elif summary is None:
        rep.skip(name, "needs summary")
    else:
        want = {}
        for b in LARGER_BUDGETS:
            want[str(b)] = sum(1 for p in range(n_pres)
                               if p in cov["ctrl"] and cov["ctrl"][p][0]
                               and cov["ctrl"][p][1] is not None and cov["ctrl"][p][1] <= b)
        chk = rep.new(name)
        compare_leaves(chk, "control_at_larger_budgets",
                       summary.get("control_at_larger_budgets"), want, unverified)
        chk.detail = {"recomputed": want}

    # ---- cross-run check: CoV control rows cut back to B against <stem>_control.jsonl
    name_s = tag + ":crossrun_control_solved"
    name_n = tag + ":crossrun_control_nodes"
    if cov is None:
        rep.skip(name_s, cov_why)
        rep.skip(name_n, cov_why)
    elif ctrl is None:
        rep.skip(name_s, "needs control file")
        rep.skip(name_n, "needs control file")
    else:
        chk_s = rep.new(name_s)
        chk_n = rep.new(name_n)
        for p in range(n_pres):
            a = ctrl.get(p)
            c = cov["ctrl"].get(p)
            if a is None or c is None:
                chk_s.add(False, {"pres_id": p, "why": "no control row",
                                  "in_control_jsonl": a is not None,
                                  "in_cov_file": c is not None})
                continue
            cov_solved = bool(c[0] and c[1] is not None and c[1] <= budget)
            chk_s.add(a[0] == cov_solved,
                      {"pres_id": p, "control_jsonl_solved": a[0], "control_jsonl_nodes": a[1],
                       "cov_file_solved_at_100000": c[0], "cov_file_nodes": c[1],
                       "cov_file_solved_cut_to_B": cov_solved})
            if a[0] and cov_solved:
                chk_n.add(a[1] == c[1], {"pres_id": p, "control_jsonl_nodes": a[1],
                                          "cov_file_nodes": c[1]})
        chk_s.detail = {"what": "CoV control row (solved and nodes <= B) == control.jsonl solved"}
        chk_n.detail = {"what": "nodes equal wherever both are solved at B"}

    # ---- views["<B>"].gained_presentations_priced
    name_a = tag + ":summary_priced_gained_set_and_best_word_nodes"
    name_b = tag + ":summary_priced_control_columns"
    name_c = tag + ":summary_priced_best_word_attains_best_nodes"
    block = None
    if summary is not None:
        views = summary.get("views")
        view = views.get(str(budget)) if isinstance(views, dict) else None
        block = view.get("gained_presentations_priced") if isinstance(view, dict) else None
    srows, row_problems = index_priced_rows(block)
    wanted = set()
    for p, r in srows.items():
        if isinstance(r.get("best_word"), str):
            wanted.add((p, r.get("best_word")))
    bf = scan_bruteforce(results_dir, stem, tag, budget, n_pres, wanted, rep, deadline)
    lacking = needs((("<stem>_L<n>.npz files", bf), ("control file", ctrl), ("summary", summary)))
    if bf is not None and bf["incomplete"]:
        if lacking:
            lacking += ", "
        lacking += "every present <stem>_L<n>.npz (%s)" % "; ".join(bf["incomplete"])
    if lacking:
        rep.skip(name_a, "needs " + lacking)
        rep.skip(name_b, "needs " + lacking)
        rep.skip(name_c, "needs " + lacking)
    else:
        gained = [p for p in range(n_pres)
                  if bf["any_solved"][p] and not (p in ctrl and ctrl[p][0])]
        gset = set(gained)
        block_key = "views[\"%d\"].gained_presentations_priced" % budget

        chk = rep.new(name_a)
        chk.detail = {"lengths_used": bf["lengths"], "summary_max_len": summary.get("max_len"),
                      "notes": bf["notes"], "gained_recomputed": gained,
                      "presentations_solved_by_some_word": sum(1 for v in bf["any_solved"] if v),
                      "best_word_nodes_recomputed": dict((p, bf["best"][p]) for p in gained)}
        # Other readings of the gained set: written out, never compared.
        try:
            by_max = {}
            for m in bf["lengths"]:
                by_max[str(m)] = sum(1 for p in range(n_pres)
                                     if bf["first_len"][p] is not None
                                     and bf["first_len"][p] <= m
                                     and not (p in ctrl and ctrl[p][0]))
            ro = {"what": "other readings of the gained set; written out, never compared",
                  "gained_if_only_lengths_up_to": by_max}
            if cov is not None:
                ro["gained_if_control_is_the_cov_file_row_cut_to_B"] = sum(
                    1 for p in range(n_pres)
                    if bf["any_solved"][p]
                    and not (p in cov["ctrl"] and cov["ctrl"][p][0]
                             and cov["ctrl"][p][1] is not None
                             and cov["ctrl"][p][1] <= budget))
            chk.report_only = ro
        except Exception:
            chk.report_only = {"error": traceback.format_exc()}
        if not isinstance(block, dict):
            chk.add(False, {"key": block_key, "why": "missing or not an object in the summary",
                            "recomputed_gained": len(gained)})
        else:
            chk.add(same_value(block.get("gained_at_this_budget"), len(gained)),
                    {"key": block_key + ".gained_at_this_budget",
                     "summary": block.get("gained_at_this_budget"), "recomputed": len(gained)})
            for prob in row_problems:
                chk.add(False, prob)
            for p in sorted(gset | set(srows)):
                if p in gset and p in srows:
                    chk.add(True)
                elif p in gset:
                    chk.add(False, {"pres_id": p,
                                    "why": "gained (recomputed) but no row in the summary"})
                else:
                    chk.add(False, {"pres_id": p,
                                    "why": "row in the summary but not gained (recomputed)",
                                    "some_word_solves": bf["any_solved"][p]
                                    if 0 <= p < n_pres else None,
                                    "control_solved_at_B": bool(p in ctrl and ctrl[p][0])})
            for p in gained:
                if p in srows:
                    chk.add(same_value(srows[p].get("best_word_nodes"), bf["best"][p]),
                            {"pres_id": p, "key": "best_word_nodes",
                             "summary": srows[p].get("best_word_nodes"),
                             "recomputed": bf["best"][p]})

        if cov is None:
            rep.skip(name_b, cov_why)
        else:
            chk_b = rep.new(name_b)
            n_solved = 0
            n_cheaper = 0
            per = {}
            for p in gained:
                c = cov["ctrl"].get(p)
                cs = bool(c is not None and c[0])
                cn = c[1] if c is not None else None
                if cs:
                    n_solved += 1
                if (not cs) or (cn is not None and bf["best"][p] < cn):
                    n_cheaper += 1
                per[p] = (c is not None, cs, cn)
            chk_b.detail = {"recomputed": {"control_file_budget": COV_BUDGET,
                                           "control_solves_them_at_file_budget": n_solved,
                                           "best_word_cheaper_than_control": n_cheaper},
                            "control_rows_recomputed": dict(
                                (p, {"control_solved": per[p][1], "control_nodes": per[p][2]})
                                for p in gained)}
            # Other readings of the control columns: written out, never compared.
            # The task does not say what control_nodes holds when the control is
            # unsolved at 100,000; the compared reading is the CoV row's
            # nodes_explored as written, the other one is null.
            try:
                unsolved_rows = []
                n_null_reading_mismatches = 0
                n_cheaper_solved_only = 0
                for p in gained:
                    has_row, cs, cn = per[p]
                    if cs and cn is not None and bf["best"][p] < cn:
                        n_cheaper_solved_only += 1
                    srow = srows.get(p)
                    if srow is not None and has_row and not same_value(
                            srow.get("control_nodes"), cn if cs else None):
                        n_null_reading_mismatches += 1
                    if not cs:
                        unsolved_rows.append({
                            "pres_id": p, "cov_file_has_control_row": has_row,
                            "cov_file_control_nodes": cn,
                            "summary_control_solved":
                                srow.get("control_solved") if srow is not None else None,
                            "summary_control_nodes":
                                srow.get("control_nodes") if srow is not None else None})
                chk_b.report_only = {
                    "what": "other readings of the control columns; written out, never compared",
                    "gained_rows_control_unsolved_at_file_budget": unsolved_rows,
                    "control_nodes_mismatches_if_null_when_control_unsolved":
                        n_null_reading_mismatches,
                    "best_word_cheaper_counting_only_solved_controls": n_cheaper_solved_only}
            except Exception:
                chk_b.report_only = {"error": traceback.format_exc()}
            if not isinstance(block, dict):
                chk_b.add(False, {"key": block_key,
                                  "why": "missing or not an object in the summary"})
            else:
                for key, want in (("control_file_budget", COV_BUDGET),
                                  ("control_solves_them_at_file_budget", n_solved),
                                  ("best_word_cheaper_than_control", n_cheaper)):
                    chk_b.add(same_value(block.get(key), want),
                              {"key": block_key + "." + key, "summary": block.get(key),
                               "recomputed": want})
                for p in gained:
                    if p not in srows:
                        continue
                    has_row, cs, cn = per[p]
                    if not has_row:
                        chk_b.add(False, {"pres_id": p,
                                          "why": "no control row for it in the CoV file"})
                        continue
                    chk_b.add(same_value(srows[p].get("control_solved"), cs),
                              {"pres_id": p, "key": "control_solved",
                               "summary": srows[p].get("control_solved"), "recomputed": cs})
                    chk_b.add(same_value(srows[p].get("control_nodes"), cn),
                              {"pres_id": p, "key": "control_nodes",
                               "summary": srows[p].get("control_nodes"), "recomputed": cn,
                               "control_solved_at_100000": cs})

        candidates = [(p, srows[p].get("best_word")) for p in sorted(srows)
                      if p in gset and isinstance(srows[p].get("best_word"), str)]
        if bf["words_error"] is not None:
            rep.skip(name_c, "the words array could not be read: " + bf["words_error"])
        elif not candidates:
            rep.skip(name_c, "no gained row with a best_word to look up")
        else:
            chk_c = rep.new(name_c)
            chk_c.detail = {"what": "extra to the task: the summary's best_word is a word of the "
                                    "L<len> file that solves the presentation with exactly the "
                                    "recomputed fewest nodes (tie-break not checked)"}
            for (p, w) in candidates:
                hit = bf["hits"].get((p, w))
                ok = bool(hit is not None and hit.get("found")
                          and hit["path_len"] >= 0 and hit["nodes"] == bf["best"][p])
                chk_c.add(ok, {"pres_id": p, "best_word": w, "lookup": hit,
                               "recomputed_fewest_nodes": bf["best"][p]})

        if isinstance(block, dict):
            for key in block:
                if key not in ("gained_at_this_budget", "control_file_budget",
                               "control_solves_them_at_file_budget",
                               "best_word_cheaper_than_control", "rows"):
                    unverified.append("%s.%s" % (block_key, key))
            row_keys = set()
            for r in srows.values():
                for key in r:
                    if key not in ("pres_id", "best_word", "best_word_nodes",
                                   "control_solved", "control_nodes"):
                        row_keys.add(key)
            for key in sorted(row_keys):
                unverified.append("%s.rows[].%s" % (block_key, key))

    for key in unverified:
        rep.skip("%s summary key %s" % (tag, key),
                 "present in the summary, not defined in this task, not verified")


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------

def run(results_dir, dataset_path, rep, deadline):
    dataset = load_dataset(dataset_path, rep)
    rep.info["presentations"] = len(dataset)

    cov = None
    cov_why = ""
    cov_path, tried = find_cov_file(results_dir)
    rep.info["cov_file"] = cov_path
    if cov_path is None:
        cov_why = "CoV file absent (tried: %s)" % ", ".join(tried)
        rep.skip("cov:rows_fields", cov_why)
        rep.skip("cov:orig_relators_match_dataset", cov_why)
        rep.skip("cov:one_control_row_per_presentation", cov_why)
    elif time.time() > deadline:
        cov_why = "time box reached before the CoV file was read"
        rep.skip("cov:*", cov_why)
    else:
        cov = load_cov(cov_path, dataset, rep, deadline)
        if cov is None:
            cov_why = "time box reached while reading the CoV file"
            rep.skip("cov:one_control_row_per_presentation", cov_why)
        else:
            rep.info["cov_rows"] = cov["n_rows"]
            rep.info["cov_median_cap"] = cov["median_cap"]

    for budget in BUDGETS:
        run_budget(budget, results_dir, dataset, cov, cov_why, rep, deadline)

    # The dataset and CoV checks compare items even when RESULTS_DIR is wrong or
    # empty.  If not one summary value was compared, say so with a check that
    # compared 0 items (counted as a mismatch), so the exit code is not 0.
    if not any(":summary_" in c.name and c.compared > 0 for c in rep.checks):
        chk = rep.new("summary:no_summary_value_compared")
        chk.detail = {"why": "every summary check was skipped (see `skipped`): no value of "
                             "any <stem>_summary.json was compared",
                      "results_dir": results_dir}


def write_out(out_json, doc):
    folder = os.path.dirname(out_json)
    if folder and not os.path.isdir(folder):
        os.makedirs(folder)
    with open(out_json, "w", encoding="utf-8") as fh:
        json.dump(doc, fh, indent=1, sort_keys=False)
        fh.write("\n")


def print_lines(doc):
    for c in doc["checks"]:
        print("[%s] %s: compared=%d mismatches=%d"
              % (c["status"], c["name"], c["compared"], c["mismatches"]))
    for s in doc["skipped"]:
        print("[skipped] %s" % s)
    print("TOTAL %s: checks=%d mismatches=%d skipped=%d"
          % (doc["script"], len(doc["checks"]), doc["mismatches"], len(doc["skipped"])))


def main(argv):
    t0 = time.time()
    if len(argv) < 4:
        print("usage: python3 -I -u %s <RESULTS_DIR> <DATASET> <OUT_JSON> [workers] [minutes]"
              % SCRIPT)
        return 1
    out_json = argv[3]
    rep = Report()
    try:
        results_dir = argv[1]
        dataset_path = argv[2]
        workers = int(argv[4]) if len(argv) > 4 else 1
        minutes = float(argv[5]) if len(argv) > 5 else 30.0
        rep.info["results_dir"] = results_dir
        rep.info["dataset"] = dataset_path
        rep.info["workers_ignored"] = workers
        rep.info["minutes"] = minutes
        rep.info["numpy"] = np.__version__
        run(results_dir, dataset_path, rep, t0 + 60.0 * minutes)
        rep.info["seconds"] = round(time.time() - t0, 1)
        doc, total = rep.build()
        write_out(out_json, doc)
        print_lines(doc)
    except Exception:
        tb = traceback.format_exc()
        sys.stderr.write(tb)
        try:
            doc, total = rep.build(crash=tb)
            write_out(out_json, doc)
            print_lines(doc)
        except Exception:
            sys.stderr.write(traceback.format_exc())
        print("CRASH %s: see the traceback above; exit code 1" % SCRIPT)
        return 1
    return 3 if total else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
