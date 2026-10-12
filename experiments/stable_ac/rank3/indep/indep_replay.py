#!/usr/bin/env python3
"""indep_replay.py - independent replay of the stored AC-move paths.

usage: python3 indep_replay.py <RESULTS_DIR> <DATASET> <OUT_JSON> [workers] [minutes]

Every stored path (rank-3 samples, plain and _inv, both budgets; relsub; rank 4
and 5 samples) is replayed from the dataset relators with a move implementation
written for this script, and the number of moves is compared with every stored
path length. Nothing is imported from the repository.

Exit code: 3 at least one mismatch; else 1 on a crash or an internal error in
one file group; else 0. A run that compared nothing also exits 0: read the
per-check lines, a check with compared=0 is printed as NO DATA.
"""

import ast
import json
import multiprocessing
import os
import re
import sys
import time
import traceback

import numpy as np

SCRIPT = "indep_replay.py"
CAP = 24                     # no relator may be longer than this, at any state
N_PRES = 640
GEN_CHARS = "xyzab"          # generators 1..5; the capital letter is the inverse
MAX_EXAMPLES = 50
BATCH_ROWS = 2000            # path rows read before they are replayed
CHUNK_ROWS = 100             # path rows per replay job
POOL_WAIT_SECONDS = 300.0    # longest wait for one replay job of a process pool
NAME_RE = re.compile(r"ms640_(\d+)")
KIND_ORDER = {"rank3": 0, "relsub": 1, "rankn": 2}


# --------------------------------------------------------------------------
# words
# --------------------------------------------------------------------------
def word_from_str(s):
    if not isinstance(s, str):
        raise ValueError("word %r is not a string" % (s,))
    out = []
    for c in s:
        g = GEN_CHARS.find(c.lower()) + 1
        if g == 0:
            raise ValueError("letter %r is not one of %s" % (c, GEN_CHARS))
        out.append(g if c == c.lower() else -g)
    return tuple(out)


def word_to_str(w):
    return "".join(GEN_CHARS[g - 1] if g > 0 else GEN_CHARS[-g - 1].upper() for g in w)


def inverse(w):
    return tuple(-g for g in reversed(w))


def reduce_word(w):
    """Free reduction, then cyclic reduction (strip inverse letters at the two ends)."""
    st = []
    for g in w:
        if st and st[-1] == -g:
            st.pop()
        else:
            st.append(g)
    lo, hi = 0, len(st) - 1
    while lo < hi and st[lo] == -st[hi]:
        lo += 1
        hi -= 1
    return tuple(st[lo:hi + 1])


def roll(w, k):
    """Right rotation by k: out[t] = w[(t - k) mod n] (the last k letters come first)."""
    n = len(w)
    if n == 0:
        return w
    return tuple(w[(t - k) % n] for t in range(n))


# Letter order used for the canonical form: larger generator index first, and
# for one generator the inverse before the generator: B<b<A<a<Z<z<Y<y<X<x.
# One byte per letter with that order, so bytes compare like the words do.
_CODE = {}
for _g in range(1, len(GEN_CHARS) + 1):
    _CODE[-_g] = 2 * (len(GEN_CHARS) - _g)
    _CODE[_g] = 2 * (len(GEN_CHARS) - _g) + 1
_LETTER = {c: g for g, c in _CODE.items()}


def order_bytes(w):
    return bytes([_CODE[g] for g in w])


def canon_word(w):
    """Least word, in the order above, among all rotations of w and of w^-1."""
    n = len(w)
    if n == 0:
        return w
    best = None
    for cand in (order_bytes(w), order_bytes(inverse(w))):
        dbl = cand + cand
        for t in range(n):
            rot = dbl[t:t + n]
            if best is None or rot < best:
                best = rot
    return tuple(_LETTER[c] for c in best)


def state_key(r):
    return (len(r), order_bytes(r))


def canon_state(relators):
    st = [canon_word(reduce_word(r)) for r in relators]
    st.sort(key=state_key)
    return st


def is_trivial(state):
    """Every relator one letter, and the letters are the n generators up to inverse."""
    if any(len(r) != 1 for r in state):
        return False
    return sorted(abs(r[0]) for r in state) == list(range(1, len(state) + 1))


# --------------------------------------------------------------------------
# replay
# --------------------------------------------------------------------------
def parse_move(mv):
    if not isinstance(mv, str):
        raise TypeError("move is not a string")
    parts = mv.split("_")
    if len(parts) != 5:
        raise ValueError("move does not have five fields")
    return int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])


def replay_one(start, moves):
    """Apply the moves to the canonical form of `start`. Returns a plain dict.

    Move 'i_j_s_k1_k2' on the canonical sorted state: relator i becomes
    roll(r_i, k1) . roll(r_j^s, k2), reduced, made canonical; the list is then
    sorted again. i and j are positions in the sorted parent state.
    """
    n_rel = len(start)
    state = canon_state(start)
    res = {
        "start": [word_to_str(r) for r in state],
        "error": None, "error_step": None,
        "illformed": None, "illformed_step": None,
        "over_cap_step": None, "max_len": 0,
        "final": None, "trivial": False, "applied": 0,
    }
    longest = max(len(r) for r in state) if state else 0
    res["max_len"] = longest
    if longest > CAP:
        res["over_cap_step"] = 0
    for step, mv in enumerate(moves, 1):
        try:
            i, j, s, k1, k2 = parse_move(mv)
        except (ValueError, TypeError):
            res["error"] = "move %r is not 'i_j_s_k1_k2' with five integers" % (mv,)
            res["error_step"] = step
            break
        if not (0 <= i < n_rel and 0 <= j < n_rel) or i == j or s not in (1, -1):
            res["error"] = ("move %r is not a move of this presentation "
                            "(needs 0 <= i != j < %d and s = 1 or -1)" % (mv, n_rel))
            res["error_step"] = step
            break
        a = roll(state[i], k1)
        b = roll(state[j] if s == 1 else inverse(state[j]), k2)
        if res["illformed"] is None:
            why = None
            if not a or not b:
                why = "uses an empty relator"
            elif not (0 <= k1 < len(a) and 0 <= k2 < len(b)):
                why = "rotation outside 0..len-1"
            elif a[-1] != -b[0]:
                why = "seam does not cancel"
            if why is not None:
                res["illformed"] = "move %d %r: %s" % (step, mv, why)
                res["illformed_step"] = step
        state[i] = canon_word(reduce_word(a + b))
        state.sort(key=state_key)
        res["applied"] = step
        longest = max(len(r) for r in state)
        if longest > res["max_len"]:
            res["max_len"] = longest
        if longest > CAP and res["over_cap_step"] is None:
            res["over_cap_step"] = step
    res["final"] = [word_to_str(r) for r in state]
    res["trivial"] = res["error"] is None and is_trivial(state)
    return res


def replay_chunk(tasks):
    """tasks: list of (start or None, moves). Top level so a process pool can run it."""
    return [None if start is None else replay_one(start, moves) for start, moves in tasks]


def run_replays(tasks, ctx):
    """Replay results in task order; None where there was no start or no time left.

    A pool job is waited for at most POOL_WAIT_SECONDS (and never past the time
    box): a pool whose worker was killed never delivers that worker's job, and a
    plain loop over imap() would then block for ever. When that happens the rest
    is replayed in this process, so no row is lost to it.
    """
    out = []
    if tasks and not ctx["timed_out"]:
        chunks = [tasks[a:a + CHUNK_ROWS] for a in range(0, len(tasks), CHUNK_ROWS)]
        done = 0
        if ctx["pool"] is not None:
            it = ctx["pool"].imap(replay_chunk, chunks)
            while done < len(chunks):
                wait = max(5.0, min(POOL_WAIT_SECONDS, ctx["deadline"] - time.time() + 5.0))
                try:
                    part = it.next(wait)
                except multiprocessing.TimeoutError:
                    if time.time() > ctx["deadline"]:
                        ctx["timed_out"] = True
                    else:
                        ctx["pool"] = None
                        ctx["pool_note"] = ("a replay job did not come back from the process pool "
                                            "within %g s; replayed in one process from there on" % wait)
                    break
                out.extend(part)
                done += 1
                if time.time() > ctx["deadline"]:
                    ctx["timed_out"] = True
                    break
        if ctx["pool"] is None and not ctx["timed_out"]:
            for chunk in chunks[done:]:
                out.extend(replay_chunk(chunk))
                if time.time() > ctx["deadline"]:
                    ctx["timed_out"] = True
                    break
    out.extend([None] * (len(tasks) - len(out)))
    return out


# --------------------------------------------------------------------------
# report
# --------------------------------------------------------------------------
class Report:
    def __init__(self):
        self.names = []
        self.checks = {}
        self.examples = {}
        self.skipped = []
        self.files = {}
        self.internal_errors = []

    def declare(self, name, what, cap=5):
        self.names.append(name)
        self.checks[name] = {"what": what, "compared": 0, "mismatches": 0,
                             "per_file": {}, "cap": cap}
        self.examples[name] = []

    def _count(self, name, fname, bad):
        c = self.checks[name]
        c["compared"] += 1
        c["mismatches"] += bad
        pf = c["per_file"].get(fname)
        if pf is None:
            pf = c["per_file"][fname] = [0, 0]
        pf[0] += 1
        pf[1] += bad
        return c

    def good(self, name, fname):
        self._count(name, fname, 0)

    def bad(self, name, fname, example):
        c = self._count(name, fname, 1)
        if len(self.examples[name]) < c["cap"]:
            ex = {"check": name, "file": fname}
            ex.update(example)
            self.examples[name].append(ex)

    def file_info(self, fname, kind):
        fi = self.files.get(fname)
        if fi is None:
            fi = self.files[fname] = {
                "kind": kind, "path_rows": 0, "rows_replayed": 0,
                "rows_start_not_built": 0,
                "rows_not_replayed_time_budget": 0, "failures": 0,
                "replay_failures": 0, "duplicate_path_rows": 0,
                "jsonl_rows": 0, "jsonl_rows_solved": 0, "jsonl_row_failures": 0,
                "identical_duplicate_jsonl_rows": 0,
            }
        return fi


def judge(rep, name, fname, ok, example):
    """Count one comparison; returns 1 when it failed."""
    if ok:
        rep.good(name, fname)
        return 0
    rep.bad(name, fname, example)
    return 1


def declare_checks(rep):
    rep.declare("replay_ends_trivial",
                "path row: the moves, applied to the start built from the dataset relators and "
                "the row's z word(s), end with every relator one letter and the letters the n "
                "generators up to inverse", cap=20)
    rep.declare("no_relator_over_24_on_path",
                "path row: no relator longer than 24 at any state of the replay, start included")
    rep.declare("row_r1_r2_equal_dataset",
                "row of a rank-3 / relsub jsonl (path rows and sample / relsub rows): r1 and r2 "
                "equal the dataset relators of its pres_id")
    rep.declare("n_moves_eq_jsonl_path_length",
                "path row: len(path_moves) == path_length of the sample / relsub row with the "
                "same pres_id + z_word, and that row is solved")
    rep.declare("n_moves_eq_npz_path_len",
                "path row: len(path_moves) == npz path_len[row of pres_id, word_index] "
                "(rank n: [row of pres_id, index])")
    rep.declare("jsonl_nodes_eq_npz_nodes",
                "nodes_explored of the jsonl row == npz nodes cell (rank 3: every sample row; "
                "rank n: every path row)")
    rep.declare("solved_rows_have_path_row",
                "every sample / relsub row with solved true has a path row")
    rep.declare("moves_wellformed_for_search",
                "extra. path row: every move is one the search can emit: 0 <= k1 < len(r_i), "
                "0 <= k2 < len(r_j), both relators non-empty, the seam cancels")
    rep.declare("sample_path_length_eq_npz_path_len",
                "extra. rank-3 sample row: path_length (null -> -1) == npz path_len cell, and "
                "solved <=> cell >= 0")
    rep.declare("sample_word_index_eq_npz_word",
                "extra. rank-3 sample row: npz words[word_index] == z_word")
    rep.declare("rankn_row_matches_npz_combo",
                "extra. rank-n path row: rank == 2 + len(z_words) == r<R> of the file name == "
                "npz meta rank, and z_words == [words[c] for c in combos[index]]")
    rep.declare("row_name_zword_zrelator_consistent",
                "extra. rank-3 / relsub row: name is ms640_<pres_id>, z_word is a word in x,y "
                "(of length L and freely reduced in an L file), z_relator == 'Z' + z_word")
    rep.declare("jsonl_rows_parse_unique",
                "every jsonl line is a JSON object; no two sample / relsub rows share "
                "pres_id + z_word with different solved / nodes / path_length")
    rep.declare("path_file_has_rows",
                "a path file that is present has at least one row")
    rep.declare("companion_files_present",
                "when one file of a (paths, rows, npz) group is present, the others are too")


# --------------------------------------------------------------------------
# input
# --------------------------------------------------------------------------
def load_dataset(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
    while lines and not lines[-1].strip():
        lines.pop()
    if len(lines) != N_PRES:
        raise ValueError("dataset %s has %d lines, expected %d" % (path, len(lines), N_PRES))
    out = []
    for p, line in enumerate(lines):
        try:
            vals = json.loads(line)
        except ValueError:
            vals = ast.literal_eval(line.strip())
        if not isinstance(vals, list) or len(vals) % 2 or not vals:
            raise ValueError("dataset line %d is not a list of 2*L integers" % p)
        half = len(vals) // 2
        rels = []
        for part in (vals[:half], vals[half:]):
            letters = [int(v) for v in part if v != 0]
            if any(v != 0 for v in part[len(letters):]) or any(abs(v) not in (1, 2) for v in letters):
                raise ValueError("dataset line %d: zeros inside a relator or a letter outside +-1, +-2" % p)
            rels.append(tuple(letters))
        out.append((rels[0], rels[1]))
    return out


def iter_jsonl(path):
    """Yield (line number, dict or None); None for a line that is not a JSON object."""
    with open(path, "r", encoding="utf-8") as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                row = None
            yield ln, (row if isinstance(row, dict) else None)


def batches(path):
    batch = []
    for item in iter_jsonl(path):
        batch.append(item)
        if len(batch) >= BATCH_ROWS:
            yield batch
            batch = []
    if batch:
        yield batch


def as_int(v):
    return v if type(v) is int else None


def pid_from_name(name):
    if isinstance(name, str):
        m = NAME_RE.fullmatch(name)
        if m:
            return int(m.group(1))
    return None


def text_key(v):
    return v if isinstance(v, str) else json.dumps(v, sort_keys=True, default=str)


def load_rank3_npz(path):
    with np.load(path, allow_pickle=False) as z:
        pres_ids = z["pres_ids"]
        words = [str(w) for w in z["words"]]
        nodes = z["nodes"]
        path_len = z["path_len"]
    return {
        "row_of": {int(p): i for i, p in enumerate(pres_ids)},
        "words": words,
        "word_pos": {w: k for k, w in enumerate(words)},
        "nodes": nodes, "path_len": path_len,
        "nrow": min(nodes.shape[0], path_len.shape[0]),
        "ncol": min(len(words), nodes.shape[1], path_len.shape[1]),
    }


def load_rankn_npz(path):
    with np.load(path, allow_pickle=False) as z:
        pres_ids = z["pres_ids"]
        nodes = z["nodes"]
        path_len = z["path_len"]
        combos = [[int(c) for c in row] for row in z["combos"]]
        meta_raw = z["meta"].item()
    if isinstance(meta_raw, bytes):
        meta_raw = meta_raw.decode("utf-8")
    meta = json.loads(meta_raw)
    return {
        "row_of": {int(p): i for i, p in enumerate(pres_ids)},
        "words": [str(w) for w in meta.get("words", [])],
        "rank": meta.get("rank"), "k": meta.get("extra_generators"),
        "combos": combos,
        "nodes": nodes, "path_len": path_len,
        "nrow": min(nodes.shape[0], path_len.shape[0]),
        "ncol": min(len(combos), nodes.shape[1], path_len.shape[1]),
    }


def npz_cell(npz, pid, col):
    """(nodes, path_len) of the cell, or None when pres_id / column does not exist."""
    ri = npz["row_of"].get(pid)
    if ri is None or col is None:
        return None
    if not (0 <= ri < npz["nrow"] and 0 <= col < npz["ncol"]):
        return None
    return int(npz["nodes"][ri, col]), int(npz["path_len"][ri, col])


# --------------------------------------------------------------------------
# checks shared by the unit kinds
# --------------------------------------------------------------------------
def judge_replay(rep, fname, ln, row, res, fi):
    nbad = 0
    ok = res["error"] is None and res["trivial"]
    if not ok:
        fi["replay_failures"] += 1
    nbad += judge(rep, "replay_ends_trivial", fname, ok, {
        "line": ln,
        "why": res["error"] or "the final state is not the trivial presentation",
        "error_at_move": res["error_step"], "moves_applied": res["applied"],
        "start_state": res["start"], "final_state": res["final"], "row": row})
    nbad += judge(rep, "no_relator_over_24_on_path", fname, res["over_cap_step"] is None, {
        "line": ln, "name": row.get("name", row.get("pres_id")),
        "z": row.get("z_word", row.get("z_words")),
        "first_state_over_24": res["over_cap_step"], "longest_relator": res["max_len"],
        "note": "state 0 is the start, state t follows move t"})
    nbad += judge(rep, "moves_wellformed_for_search", fname,
                  res["error"] is None and res["illformed"] is None, {
                      "line": ln, "name": row.get("name", row.get("pres_id")),
                      "z": row.get("z_word", row.get("z_words")),
                      "why": res["illformed"] or res["error"],
                      "path_moves": row.get("path_moves")})
    return nbad


def check_row_strings(rep, fname, ln, row, pid, zw, ds_str, zlen):
    nbad = 0
    in_ds = pid is not None and 0 <= pid < len(ds_str)
    got = [row.get("r1"), row.get("r2")]
    nbad += judge(rep, "row_r1_r2_equal_dataset", fname, in_ds and got == list(ds_str[pid]), {
        "line": ln, "name": row.get("name"), "pres_id": pid, "row_r1_r2": got,
        "dataset_r1_r2": list(ds_str[pid]) if in_ds else None})
    why = []
    name_pid = pid_from_name(row.get("name"))
    if name_pid is None:
        why.append("name is not 'ms640_<pres_id>'")
    if "pres_id" in row and as_int(row.get("pres_id")) != name_pid:
        why.append("pres_id field differs from the name")
    if not isinstance(zw, str) or any(c not in "xyXY" for c in zw):
        why.append("z_word is not a word in x,y,X,Y")
    else:
        if row.get("z_relator") != "Z" + zw:
            why.append("z_relator is not 'Z' + z_word")
        if zlen is not None:
            if len(zw) != zlen:
                why.append("z_word length is not the L of the file name")
            if any(a != b and a.lower() == b.lower() for a, b in zip(zw, zw[1:])):
                why.append("z_word is not freely reduced")
    nbad += judge(rep, "row_name_zword_zrelator_consistent", fname, not why, {
        "line": ln, "name": row.get("name"), "pres_id": row.get("pres_id"),
        "z_word": zw, "z_relator": row.get("z_relator"), "why": why})
    return nbad


# --------------------------------------------------------------------------
# rank-3 sample files (L<n>, L<n>_inv) and relsub files
# --------------------------------------------------------------------------
def process_word_unit(unit, ds, ds_str, rep, ctx):
    kind = unit["kind"]
    names, d = ctx["names"], ctx["dir"]
    pname, rname, zname = unit["paths"], unit["rows"], unit["npz"]
    have_p, have_r = pname in names, rname in names
    have_z = zname is not None and zname in names
    zlen = unit["zlen"]
    fi = rep.file_info(pname, kind)
    fi["paths_file_present"] = have_p

    npz = load_rank3_npz(os.path.join(d, zname)) if have_z else None

    # --- the sample / relsub rows: (pres_id, z_word) -> (solved, nodes, path_length, word_index)
    info = {}
    if have_r:
        for ln, row in iter_jsonl(os.path.join(d, rname)):
            if row is None:
                rep.bad("jsonl_rows_parse_unique", rname, {"line": ln, "why": "not a JSON object"})
                continue
            fi["jsonl_rows"] += 1
            nbad = 0
            zw = row.get("z_word")
            # rank-3 samples are matched on pres_id + z_word, relsub rows on name + z_word
            pid = as_int(row.get("pres_id")) if kind == "rank3" else pid_from_name(row.get("name"))
            nbad += check_row_strings(rep, rname, ln, row, pid, zw, ds_str, zlen)
            rec = (row.get("solved") is True, as_int(row.get("nodes_explored")),
                   row.get("path_length"), as_int(row.get("word_index")))
            key = (pid, text_key(zw))
            old = info.get(key)
            if old is not None and old != rec:
                nbad += judge(rep, "jsonl_rows_parse_unique", rname, False, {
                    "line": ln, "pres_id": pid, "z_word": zw,
                    "why": "two rows with this pres_id + z_word disagree",
                    "first": list(old), "this": list(rec)})
            else:
                rep.good("jsonl_rows_parse_unique", rname)
                if old is not None:
                    fi["identical_duplicate_jsonl_rows"] += 1
                else:
                    info[key] = rec
                    if rec[0]:
                        fi["jsonl_rows_solved"] += 1
            if kind == "rank3" and npz is not None:
                cell = npz_cell(npz, pid, rec[3])
                nbad += judge(rep, "jsonl_nodes_eq_npz_nodes", rname,
                              cell is not None and rec[1] == cell[0], {
                                  "line": ln, "pres_id": pid, "z_word": zw, "word_index": rec[3],
                                  "jsonl_nodes_explored": row.get("nodes_explored"),
                                  "npz_nodes": None if cell is None else cell[0], "npz": zname})
                pl = rec[2]
                jl = -1 if pl is None else (pl if type(pl) is int else None)
                nbad += judge(rep, "sample_path_length_eq_npz_path_len", rname,
                              cell is not None and jl is not None and jl == cell[1]
                              and rec[0] == (cell[1] >= 0), {
                                  "line": ln, "pres_id": pid, "z_word": zw, "word_index": rec[3],
                                  "jsonl_solved": row.get("solved"), "jsonl_path_length": pl,
                                  "npz_path_len": None if cell is None else cell[1], "npz": zname})
                wi = rec[3]
                nw = npz["words"][wi] if wi is not None and 0 <= wi < len(npz["words"]) else None
                note = None
                if nw is not None and isinstance(zw, str) and nw != zw and nw == zw[::-1].swapcase():
                    note = "the npz word is the inverse of z_word"
                nbad += judge(rep, "sample_word_index_eq_npz_word", rname, nw is not None and nw == zw, {
                    "line": ln, "pres_id": pid, "z_word": zw, "word_index": wi,
                    "npz_word": nw, "note": note, "npz": zname})
            if nbad:
                fi["jsonl_row_failures"] += 1

    # --- the path rows
    path_keys = set()
    if have_p:
        for batch in batches(os.path.join(d, pname)):
            metas, tasks = [], []
            for ln, row in batch:
                if row is None:
                    rep.bad("jsonl_rows_parse_unique", pname, {"line": ln, "why": "not a JSON object"})
                    continue
                rep.good("jsonl_rows_parse_unique", pname)
                pid = pid_from_name(row.get("name"))
                zw = row.get("z_word")
                moves = row.get("path_moves")
                start, err = None, None
                if pid is None or not (0 <= pid < len(ds)):
                    err = "name is not 'ms640_<pres_id>' with a pres_id of the dataset"
                elif not isinstance(moves, list):
                    err = "path_moves is not a list"
                else:
                    try:
                        start = [ds[pid][0], ds[pid][1], (-3,) + word_from_str(zw)]
                    except ValueError as e:
                        err = "z_word: %s" % e
                n_moves = len(moves) if isinstance(moves, list) else None
                metas.append((ln, row, pid, zw, err, n_moves))
                tasks.append((start, moves if start is not None else []))
            results = run_replays(tasks, ctx)
            for (ln, row, pid, zw, err, n_moves), res in zip(metas, results):
                fi["path_rows"] += 1
                nbad = 0
                if err is not None:
                    fi["rows_start_not_built"] += 1
                    fi["replay_failures"] += 1
                    nbad += judge(rep, "replay_ends_trivial", pname, False, {
                        "line": ln, "why": "cannot build the start: " + err, "row": row})
                elif res is None:
                    fi["rows_not_replayed_time_budget"] += 1
                else:
                    fi["rows_replayed"] += 1
                    nbad += judge_replay(rep, pname, ln, row, res, fi)
                nbad += check_row_strings(rep, pname, ln, row, pid, zw, ds_str, zlen)
                key = (pid, text_key(zw))
                if key in path_keys:
                    fi["duplicate_path_rows"] += 1
                path_keys.add(key)
                rec = info.get(key)
                if have_r:
                    ok = (rec is not None and rec[0] and n_moves is not None
                          and type(rec[2]) is int and rec[2] == n_moves)
                    nbad += judge(rep, "n_moves_eq_jsonl_path_length", pname, ok, {
                        "line": ln, "name": row.get("name"), "z_word": zw, "n_moves": n_moves,
                        "jsonl_row": None if rec is None else {
                            "solved": rec[0], "nodes_explored": rec[1],
                            "path_length": rec[2], "word_index": rec[3]},
                        "why": ("no row with this pres_id + z_word in %s" % rname) if rec is None
                        else "path_length differs from the number of moves, or the row is not solved"})
                if kind == "rank3" and npz is not None:
                    col = rec[3] if rec is not None and rec[3] is not None else None
                    src = "word_index of the sample row"
                    if col is None:
                        col = npz["word_pos"].get(text_key(zw))
                        src = "position of z_word in npz words (no sample row)"
                    cell = npz_cell(npz, pid, col)
                    ok = cell is not None and n_moves is not None and cell[1] == n_moves
                    nbad += judge(rep, "n_moves_eq_npz_path_len", pname, ok, {
                        "line": ln, "name": row.get("name"), "z_word": zw, "n_moves": n_moves,
                        "word_index": col, "word_index_from": src,
                        "npz_path_len": None if cell is None else cell[1], "npz": zname})
                if nbad:
                    fi["failures"] += 1
        judge(rep, "path_file_has_rows", pname, fi["path_rows"] > 0,
              {"why": "the file is present and has no row"})

    # --- every solved row has a path row
    if have_r:
        for key, rec in info.items():
            if rec[0]:
                judge(rep, "solved_rows_have_path_row", rname, key in path_keys, {
                    "pres_id": key[0], "z_word": key[1],
                    "why": ("no path row in %s" % pname) if have_p else ("%s is absent" % pname)})


# --------------------------------------------------------------------------
# rank-n sample path files
# --------------------------------------------------------------------------
def process_rankn_unit(unit, ds, rep, ctx):
    names, d = ctx["names"], ctx["dir"]
    pname, zname = unit["paths"], unit["npz"]
    have_p, have_z = pname in names, zname in names
    fi = rep.file_info(pname, "rankn")
    fi["paths_file_present"] = have_p
    m = re.search(r"_r(\d+)$", unit["base"])
    file_rank = int(m.group(1)) if m else None
    npz = load_rankn_npz(os.path.join(d, zname)) if have_z else None
    if not have_p:
        return
    seen = set()
    for batch in batches(os.path.join(d, pname)):
        metas, tasks = [], []
        for ln, row in batch:
            if row is None:
                rep.bad("jsonl_rows_parse_unique", pname, {"line": ln, "why": "not a JSON object"})
                continue
            rep.good("jsonl_rows_parse_unique", pname)
            pid = as_int(row.get("pres_id"))
            zws = row.get("z_words")
            moves = row.get("path_moves")
            start, err = None, None
            if pid is None or not (0 <= pid < len(ds)):
                err = "pres_id is missing or not in the dataset"
            elif not isinstance(moves, list):
                err = "path_moves is not a list"
            elif not isinstance(zws, list):
                err = "z_words is not a list"
            elif 2 + len(zws) > len(GEN_CHARS):
                err = "more than %d generators" % len(GEN_CHARS)
            else:
                try:
                    start = [ds[pid][0], ds[pid][1]]
                    start += [(-(3 + t),) + word_from_str(w) for t, w in enumerate(zws)]
                except ValueError as e:
                    start, err = None, "z_words: %s" % e
            n_moves = len(moves) if isinstance(moves, list) else None
            metas.append((ln, row, pid, zws, err, n_moves))
            tasks.append((start, moves if start is not None else []))
        results = run_replays(tasks, ctx)
        for (ln, row, pid, zws, err, n_moves), res in zip(metas, results):
            fi["path_rows"] += 1
            nbad = 0
            if err is not None:
                fi["rows_start_not_built"] += 1
                fi["replay_failures"] += 1
                nbad += judge(rep, "replay_ends_trivial", pname, False, {
                    "line": ln, "why": "cannot build the start: " + err, "row": row})
            elif res is None:
                fi["rows_not_replayed_time_budget"] += 1
            else:
                fi["rows_replayed"] += 1
                nbad += judge_replay(rep, pname, ln, row, res, fi)
            idx = as_int(row.get("index"))
            if (pid, idx) in seen:
                fi["duplicate_path_rows"] += 1
            seen.add((pid, idx))

            why = []
            k = len(zws) if isinstance(zws, list) else None
            rrank = as_int(row.get("rank"))
            if k is None or rrank != 2 + k:
                why.append("rank != 2 + len(z_words)")
            if file_rank is not None and rrank != file_rank:
                why.append("rank differs from r<R> of the file name")
            if isinstance(zws, list) and any(
                    not isinstance(w, str) or any(c not in "xyXY" for c in w) for w in zws):
                why.append("a z word is not a word in x,y,X,Y")
            expected = None
            if npz is not None:
                if npz["rank"] != rrank:
                    why.append("npz meta rank differs from the row's rank")
                if npz["k"] != k:
                    why.append("npz meta extra_generators != len(z_words)")
                combo = npz["combos"][idx] if idx is not None and 0 <= idx < len(npz["combos"]) else None
                if combo is None:
                    why.append("index is not a row of combos")
                elif any(not (0 <= c < len(npz["words"])) for c in combo):
                    why.append("combos[index] points outside meta words")
                else:
                    expected = [npz["words"][c] for c in combo]
                    if expected != zws:
                        why.append("z_words != [words[c] for c in combos[index]]")
            nbad += judge(rep, "rankn_row_matches_npz_combo", pname, not why, {
                "line": ln, "pres_id": pid, "index": idx, "rank": row.get("rank"),
                "z_words": zws, "npz_words_of_combo": expected, "why": why,
                "npz": zname if npz is not None else None})

            if npz is not None:
                cell = npz_cell(npz, pid, idx)
                nbad += judge(rep, "n_moves_eq_npz_path_len", pname,
                              cell is not None and n_moves is not None and cell[1] == n_moves, {
                                  "line": ln, "pres_id": pid, "index": idx, "z_words": zws,
                                  "n_moves": n_moves,
                                  "npz_path_len": None if cell is None else cell[1], "npz": zname})
                nbad += judge(rep, "jsonl_nodes_eq_npz_nodes", pname,
                              cell is not None and as_int(row.get("nodes_explored")) == cell[0], {
                                  "line": ln, "pres_id": pid, "index": idx, "z_words": zws,
                                  "jsonl_nodes_explored": row.get("nodes_explored"),
                                  "npz_nodes": None if cell is None else cell[0], "npz": zname})
            if nbad:
                fi["failures"] += 1
    judge(rep, "path_file_has_rows", pname, fi["path_rows"] > 0,
          {"why": "the file is present and has no row"})


# --------------------------------------------------------------------------
# which files
# --------------------------------------------------------------------------
def make_unit(kind, base, expected):
    if kind == "rank3":
        m = re.search(r"_L(\d+)(?:_inv)?$", base)
        return {"kind": kind, "base": base, "expected": expected,
                "paths": base + "_sample_paths.jsonl", "rows": base + "_sample.jsonl",
                "npz": base + ".npz", "zlen": int(m.group(1)) if m else None}
    if kind == "relsub":
        return {"kind": kind, "base": base, "expected": expected,
                "paths": base + "_paths.jsonl", "rows": base + ".jsonl",
                "npz": None, "zlen": None}
    return {"kind": kind, "base": base, "expected": expected,
            "paths": base + "_sample_paths.jsonl", "rows": None,
            "npz": base + ".npz", "zlen": None}


def build_units(names):
    units = {}
    for budget in (1000, 10000):
        stem = "rank3_bf_ms640_b%d_cap24" % budget
        for n in range(1, 11):
            units[stem + "_L%d" % n] = make_unit("rank3", stem + "_L%d" % n, True)
        for n in range(1, 7):
            units[stem + "_L%d_inv" % n] = make_unit("rank3", stem + "_L%d_inv" % n, True)
        units[stem + "_relsub"] = make_unit("relsub", stem + "_relsub", True)
    for rank in (4, 5):
        base = "rankn_bf_ms640_b1000_cap24_r%d" % rank
        units[base] = make_unit("rankn", base, True)

    unrecognized = []
    for n in sorted(names):
        if n.endswith("_sample_paths.jsonl"):
            base = n[:-len("_sample_paths.jsonl")]
            kind = "rankn" if base.startswith("rankn_") else "rank3"
        elif n.endswith("_relsub_paths.jsonl"):
            base, kind = n[:-len("_paths.jsonl")], "relsub"
        elif n.endswith("_sample.jsonl"):
            base = n[:-len("_sample.jsonl")]
            kind = "rankn" if base.startswith("rankn_") else "rank3"
        elif n.endswith("_relsub.jsonl"):
            base, kind = n[:-len(".jsonl")], "relsub"
        else:
            if n.endswith("paths.jsonl"):
                unrecognized.append(n)
            continue
        if base not in units:
            units[base] = make_unit(kind, base, False)

    def order(u):
        return (KIND_ORDER[u["kind"]], [int(x) for x in re.findall(r"\d+", u["base"])], u["base"])

    return sorted(units.values(), key=order), unrecognized


# --------------------------------------------------------------------------
# main
# --------------------------------------------------------------------------
def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, default=str)
        f.write("\n")


def main(argv):
    if len(argv) < 4:
        sys.stderr.write(__doc__)
        return 1
    results_dir, dataset, out_json = argv[1], argv[2], argv[3]
    workers = max(1, int(argv[4])) if len(argv) > 4 else 1
    minutes = float(argv[5]) if len(argv) > 5 else 30.0
    t0 = time.time()

    ds = load_dataset(dataset)
    ds_str = [(word_to_str(a), word_to_str(b)) for a, b in ds]
    names = set(os.listdir(results_dir))
    rep = Report()
    declare_checks(rep)
    units, unrecognized = build_units(names)
    for n in unrecognized:
        rep.skipped.append("%s: a *paths.jsonl file this script does not know; not replayed" % n)

    pool, pool_note = None, None
    if workers > 1:
        try:
            pool = multiprocessing.Pool(workers)
        except Exception as e:           # no pool: replay in this process
            pool, pool_note = None, "no process pool (%s); replayed in one process" % (e,)
    ctx = {"dir": results_dir, "names": names, "deadline": t0 + 60.0 * minutes,
           "timed_out": False, "pool": pool, "pool_note": pool_note}

    try:
        for unit in units:
            files = [f for f in (unit["paths"], unit["rows"], unit["npz"]) if f]
            present = [f for f in files if f in names]
            if not present:
                for f in files:
                    rep.skipped.append("%s: absent" % f)
                continue
            for f in files:
                if f in names:
                    rep.good("companion_files_present", f)
                else:
                    rep.bad("companion_files_present", f, {
                        "why": "absent, but present: %s" % ", ".join(present)})
                    rep.skipped.append("%s: absent although %s is present; the checks that "
                                       "need it were not made" % (f, present[0]))
            if ctx["timed_out"] or time.time() > ctx["deadline"]:
                ctx["timed_out"] = True
                for f in present:
                    rep.skipped.append("%s: not processed, the %g minutes were used up" % (f, minutes))
                continue
            try:
                if unit["kind"] == "rankn":
                    process_rankn_unit(unit, ds, rep, ctx)
                else:
                    process_word_unit(unit, ds, ds_str, rep, ctx)
            except Exception:
                rep.internal_errors.append({"unit": unit["base"],
                                            "traceback": traceback.format_exc()})
                rep.skipped.append("%s: internal error of this script, group not fully "
                                   "processed (see internal_errors)" % unit["base"])
    finally:
        if pool is not None:
            pool.terminate()

    for fname, fi in sorted(rep.files.items()):
        if fi["rows_not_replayed_time_budget"]:
            rep.skipped.append("%s: %d of %d path rows not replayed, the %g minutes were used up "
                               "(their length checks were still made)"
                               % (fname, fi["rows_not_replayed_time_budget"], fi["path_rows"], minutes))

    checks_out, total = [], 0
    for name in rep.names:
        c = rep.checks[name]
        total += c["mismatches"]
        if c["compared"] == 0:
            status = "NO DATA (compared 0, not a pass)"
        else:
            status = "FAIL" if c["mismatches"] else "pass"
        checks_out.append({
            "name": name, "compared": c["compared"], "mismatches": c["mismatches"],
            "status": status,
            "detail": {"what": c["what"],
                       "per_file": {f: {"compared": v[0], "mismatches": v[1]}
                                    for f, v in sorted(c["per_file"].items())}}})
        print("%s: compared=%d mismatches=%d -> %s" % (name, c["compared"], c["mismatches"], status))

    first = []
    for name in rep.names:
        first.extend(rep.examples[name])
    first = first[:MAX_EXAMPLES]

    for fname, fi in sorted(rep.files.items()):
        print("FILE %s: path rows=%d replayed=%d start not built=%d not replayed (time)=%d "
              "replay failures=%d rows with any failure=%d"
              % (fname, fi["path_rows"], fi["rows_replayed"], fi["rows_start_not_built"],
                 fi["rows_not_replayed_time_budget"], fi["replay_failures"], fi["failures"]))
    if ctx["timed_out"]:
        print("TIME: the %g minutes were used up; see 'skipped'" % minutes)
    if ctx["pool_note"]:
        print("POOL: %s" % ctx["pool_note"])
    for err in rep.internal_errors:
        print("INTERNAL ERROR in %s:\n%s" % (err["unit"], err["traceback"]))
    no_data = [c["name"] for c in checks_out if c["compared"] == 0]
    if no_data:
        print("NO DATA (compared 0, not a pass) in %d of %d checks: %s"
              % (len(no_data), len(checks_out), ", ".join(no_data)))

    write_json(out_json, {
        "script": SCRIPT,
        "checks": checks_out,
        "mismatches": total,
        "skipped": rep.skipped,
        "first_mismatches": first,
        "checks_with_no_data": no_data,
        "per_file": {f: rep.files[f] for f in sorted(rep.files)},
        "internal_errors": rep.internal_errors,
        "timed_out": ctx["timed_out"],
        "workers": workers if pool is not None else 1,
        "pool_note": ctx["pool_note"],
        "minutes": minutes,
        "seconds": round(time.time() - t0, 1),
    })
    print("TOTAL mismatches=%d checks_with_no_data=%d skipped=%d internal_errors=%d seconds=%.0f"
          % (total, len(no_data), len(rep.skipped), len(rep.internal_errors), time.time() - t0))
    if total:
        return 3
    return 1 if rep.internal_errors else 0


if __name__ == "__main__":
    try:
        code = main(sys.argv)
    except Exception:
        tb = traceback.format_exc()
        sys.stderr.write(tb)
        try:
            if len(sys.argv) > 3:
                write_json(sys.argv[3], {"script": SCRIPT, "checks": [], "mismatches": 0,
                                         "skipped": [], "first_mismatches": [], "crash": tb})
        except Exception:
            pass
        code = 1
    sys.exit(code)
