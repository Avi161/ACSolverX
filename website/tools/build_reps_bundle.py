#!/usr/bin/env python3
"""Build the 261-unsolved-rep website bundle for the AC-SolverX Path Explorer.

READS (never writes) from the repo's data/ + results/ trees; WRITES only into
website/sample-data/ (the site's single flat record pool + the grid sidecar).

Emits into website/sample-data/:
  registry_reps.jsonl    261 registry rows (dataset "ms_reps_unsolved", idx 0..260)
  calibration_reps.jsonl 261 x 4 arms of the hard run (budget 500000, all unsolved)
  reps_grid.json         the (n,w) map of the whole MS(1190) family, with cell -> ms_idx / rep_idx
Also: appends the two jsonl files to manifest.json, and strips the stale 12-idx/2-arm
placeholder "ms_reps_unsolved" rows out of calibration_ms640.jsonl.

The (n,w) -> 1190MS registry idx map is a rotation+inversion-invariant signature match
(a verified perfect bijection); ms_solved_grid.csv is authoritative for trivial/label
status (it disagrees with the registry idx<640 heuristic on 12/1190 cells).

Word convention (matches scripts/build_ms_reps.py + the env): x->1, X->-1, y->2, Y->-2, z->3.
Run from anywhere:  python website/tools/build_reps_bundle.py
"""
import ast
import csv
import json
import os

L = 24
W2I = {"x": 1, "X": -1, "y": 2, "Y": -2}
I2W = {1: "x", -1: "X", 2: "y", -2: "Y", 3: "z", -3: "Z"}

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "data")
REPS = os.path.join(DATA, "ms_unsolved_reps")
STAB = os.path.join(DATA, "stabilized")
RESULTS = os.path.join(ROOT, "results", "stable_ac", "3_generators_w_choices", "solved")
OUT = os.path.join(ROOT, "website", "sample-data")


# ---- word helpers (mirror website/js/data.js canonicalisation exactly) --------
def word_to_ints(w):
    return [W2I[c] for c in w]


def ints_to_str(a):
    return "".join(I2W[v] for v in a if v != 0)


def strip_pad(a):
    return [v for v in a if v != 0]


def invert(w):
    return [-v for v in reversed(w)]


def roll(w, k):
    n = len(w)
    if n == 0:
        return []
    k %= n
    return w[n - k:] + w[:n - k] if k else list(w)


def lex_leq(a, b):
    for x, y in zip(a, b):
        if x != y:
            return x < y
    return True  # equal-length ties -> equal


def minimal_rotation(w):
    best = list(w)
    for k in range(1, len(w)):
        r = roll(w, k)
        if not lex_leq(best, r):
            best = r
    return best


def canonical_relator(w):
    if not w:
        return []
    a = minimal_rotation(w)
    b = minimal_rotation(invert(w))
    return a if lex_leq(a, b) else b


def presentation_sig(relators):
    """Rotation+inversion-invariant, relator-order-invariant signature of a 2-relator presentation."""
    return tuple(sorted(tuple(canonical_relator(r)) for r in relators))


# ---- MS(n,w) synthesis --------------------------------------------------------
def ms_relators(n, w):
    # r1 = X y^n x Y^(n+1) ; r2 = X w   (greedy_ac.py::MS)
    r1 = [-1] + [2] * n + [1] + [-2] * (n + 1)
    r2 = [-1] + word_to_ints(w)
    return [r1, r2]


# ---- load the 261 reps --------------------------------------------------------
def load_reps():
    with open(os.path.join(REPS, "ms_reps_unsolved.csv"), newline="") as f:
        rows = list(csv.reader(f))
    assert rows[0][:3] == ["r1", "r2", "name"], rows[0]
    csv_rows = rows[1:]
    txt = [ast.literal_eval(l) for l in open(os.path.join(REPS, "ms_reps_unsolved.txt")) if l.strip()]
    assert len(csv_rows) == len(txt) == 261, (len(csv_rows), len(txt))
    reps = []
    for i, (row, flat) in enumerate(zip(csv_rows, txt)):
        r1_csv, r2_csv, name = row[0], row[1], row[2]
        r1 = strip_pad(flat[:L])
        r2 = strip_pad(flat[L:2 * L])
        # alignment / integrity: txt ints must decode back to the CSV letter-words
        assert ints_to_str(r1) == r1_csv, (i, ints_to_str(r1), r1_csv)
        assert ints_to_str(r2) == r2_csv, (i, ints_to_str(r2), r2_csv)
        reps.append({"idx": i, "name": name, "r1": r1, "r2": r2})
    names = [r["name"] for r in reps]
    assert len(set(names)) == 261, "rep names not distinct"
    return reps


# ---- (n,w) -> 1190MS registry idx bijection -----------------------------------
def load_registry_1190():
    recs = []
    with open(os.path.join(OUT, "registry_1190MS.jsonl")) as f:
        for line in f:
            line = line.strip()
            if line:
                recs.append(json.loads(line))
    assert len(recs) == 1190, len(recs)
    return recs


def build_nw_to_idx(reg1190):
    sig_to_idx = {}
    for r in reg1190:
        sig = presentation_sig(r["relators"])
        assert sig not in sig_to_idx, ("dup registry sig", r["idx"])
        sig_to_idx[sig] = r["idx"]
    return sig_to_idx


# ---- grid ---------------------------------------------------------------------
def load_grid():
    with open(os.path.join(REPS, "ms_solved_grid.csv"), newline="") as f:
        rows = list(csv.reader(f))
    header = rows[0]
    nvals = [int(c) for c in header[1:8]]  # columns 1..7
    assert nvals == [1, 2, 3, 4, 5, 6, 7], nvals
    words, grid = [], {}
    for row in rows[1:]:
        w = row[0].strip()
        if not w or any(c not in W2I for c in w):
            continue  # skip the trailing count row
        words.append(w)
        for j, n in enumerate(nvals):
            grid[(w, n)] = row[1 + j].strip()
    assert len(words) == 170, len(words)
    return words, nvals, grid


# ---- calibration (the hard run) ----------------------------------------------
ARMS = ["r1", "r2", "x", "y"]
Z_FIXED = {"x": [1], "y": [2]}


def load_hard_calibration(reps):
    by_idx = {r["idx"]: r for r in reps}
    out = []
    seen = set()
    for arm in ARMS:
        path = os.path.join(RESULTS, "calibration_%s.jsonl" % arm)
        for line in open(path):
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            if rec.get("dataset") != "ms_reps_unsolved":
                continue
            if rec.get("budget_nodes") != 500000:
                continue  # drop stale 50k/200k r1 dupes
            key = (rec["idx"], arm)
            if key in seen:
                continue  # any residual dup
            seen.add(key)
            rep = by_idx[rec["idx"]]
            zword = list(rep["r1"]) if arm == "r1" else list(rep["r2"]) if arm == "r2" else list(Z_FIXED[arm])
            rec = dict(rec)
            rec["arm"] = arm
            rec["z_word"] = zword
            rec.pop("_source_file", None)
            out.append(rec)
    # exactly 261 per arm, all unsolved
    for arm in ARMS:
        n = sum(1 for r in out if r["arm"] == arm)
        assert n == 261, (arm, n)
    assert all(r["solved"] is False for r in out), "a reps calibration row is solved?!"
    return out


def verify_stabilized(reps):
    """Cross-check computed z*w^-1 third relator against data/stabilized/*.txt (defensive)."""
    def third(zword):
        # cyclic_reduce([z] + invert(w)) with z=3
        w = [3] + invert(zword)
        # free reduce
        out = []
        for a in w:
            if out and out[-1] == -a:
                out.pop()
            else:
                out.append(a)
        i, j = 0, len(out) - 1
        while i < j and out[i] == -out[j]:
            i += 1
            j -= 1
        return out[i:j + 1]
    for arm in ARMS:
        fp = os.path.join(STAB, "ms_reps_unsolved_z_%s.txt" % arm)
        if not os.path.exists(fp):
            continue
        lines = [ast.literal_eval(l) for l in open(fp) if l.strip()]
        for i, flat in enumerate(lines):
            rep = reps[i]
            zword = rep["r1"] if arm == "r1" else rep["r2"] if arm == "r2" else Z_FIXED[arm]
            got = set(map(tuple, [strip_pad(flat[2 * L:3 * L])]))
            want = tuple(third(list(zword)))
            # stabilized file stores some rotation of z*w^-1; compare canonical forms
            file_third = strip_pad(flat[2 * L:3 * L])
            assert canonical_relator(file_third) == canonical_relator(list(want)), (arm, i)
    return True


# ---- write --------------------------------------------------------------------
def write_jsonl(path, rows):
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def strip_stale_reps_from_ms640():
    fp = os.path.join(OUT, "calibration_ms640.jsonl")
    kept, dropped = [], 0
    for line in open(fp):
        s = line.strip()
        if not s:
            continue
        rec = json.loads(s)
        if rec.get("dataset") == "ms_reps_unsolved":
            dropped += 1
            continue
        kept.append(s)
    with open(fp, "w") as f:
        f.write("\n".join(kept) + "\n")
    # verify none remain
    remain = sum(1 for l in open(fp) if l.strip() and json.loads(l).get("dataset") == "ms_reps_unsolved")
    assert remain == 0, remain
    return dropped


def update_manifest():
    fp = os.path.join(OUT, "manifest.json")
    m = json.load(open(fp))
    for name in ["registry_reps.jsonl", "calibration_reps.jsonl"]:
        if name not in m["files"]:
            m["files"].append(name)
    m["label"] = ("MS(1190) original 640 + hard 550 · 261 unsolved-class reps (hard run, z ∈ {r₁,r₂,x,y}) · "
                  "z ∈ {r₁,r₂,x,y,g=xy,xY,yx,Xy}")
    with open(fp, "w") as f:
        json.dump(m, f, indent=2)
        f.write("\n")


def main():
    reps = load_reps()
    words, nvals, grid = load_grid()
    reg1190 = load_registry_1190()
    sig_to_idx = build_nw_to_idx(reg1190)

    # bijection: every (n,w) matches a unique registry idx, covering all 1190
    covered = set()
    nw_to_idx = {}
    for w in words:
        for n in nvals:
            sig = presentation_sig(ms_relators(n, w))
            assert sig in sig_to_idx, ("no registry match", n, w)
            idx = sig_to_idx[sig]
            nw_to_idx[(w, n)] = idx
            covered.add(idx)
    assert len(covered) == 1190, ("bijection not total", len(covered))

    name_to_repidx = {r["name"]: r["idx"] for r in reps}

    # registry_reps: attach nw_cells (which (n,w) grid cells point at this rep)
    cells_for_rep = {r["idx"]: [] for r in reps}
    grid_cells = []
    for w in words:
        for n in nvals:
            status = grid[(w, n)]  # "trivial" or a label
            ms_idx = nw_to_idx[(w, n)]
            cell = {"w": w, "n": n, "status": status, "ms_idx": ms_idx}
            if status != "trivial":
                rep_idx = name_to_repidx[status]
                cell["rep_idx"] = rep_idx
                cells_for_rep[rep_idx].append([w, n])
            grid_cells.append(cell)

    registry_rows = [{
        "kind": "registry", "dataset": "ms_reps_unsolved", "idx": r["idx"],
        "subset": "reps", "n_gen": 2, "relators": [r["r1"], r["r2"]],
        "name": r["name"], "nw_cells": cells_for_rep[r["idx"]],
    } for r in reps]

    calibration_rows = load_hard_calibration(reps)
    verify_stabilized(reps)

    grid_obj = {
        "dataset": "ms_reps_unsolved", "linked_dataset": "1190MS",
        "words": words, "nvals": nvals,
        "n_trivial": sum(1 for c in grid_cells if c["status"] == "trivial"),
        "n_rep_cells": sum(1 for c in grid_cells if c["status"] != "trivial"),
        "cells": grid_cells,
    }
    assert grid_obj["n_trivial"] == 640, grid_obj["n_trivial"]
    assert grid_obj["n_rep_cells"] == 550, grid_obj["n_rep_cells"]
    assert len({c["rep_idx"] for c in grid_cells if "rep_idx" in c}) == 261

    write_jsonl(os.path.join(OUT, "registry_reps.jsonl"), registry_rows)
    write_jsonl(os.path.join(OUT, "calibration_reps.jsonl"), calibration_rows)
    with open(os.path.join(OUT, "reps_grid.json"), "w") as f:
        json.dump(grid_obj, f)
        f.write("\n")
    dropped = strip_stale_reps_from_ms640()
    update_manifest()

    print("OK")
    print("  registry_reps.jsonl     : %d rows" % len(registry_rows))
    print("  calibration_reps.jsonl  : %d rows (%d per arm x 4)" % (len(calibration_rows), len(calibration_rows) // 4))
    print("  reps_grid.json          : %d cells (%d trivial, %d rep-cells, 261 distinct reps)"
          % (len(grid_cells), grid_obj["n_trivial"], grid_obj["n_rep_cells"]))
    print("  stale ms_reps rows stripped from calibration_ms640.jsonl: %d" % dropped)


if __name__ == "__main__":
    main()
