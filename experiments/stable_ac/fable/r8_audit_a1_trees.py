"""ADVERSARIAL AUDIT of R8 Theorem A1 (the SHARP PROFILE).  NEW FILE, read-only w.r.t.
everything else in the repo.

Independent re-implementation.  Nothing here imports `r8_complexity_profile.py`; the
census is re-parsed from the upstream CSV with a fresh tokenizer, the singular graph is
reconstructed INTRINSICALLY from the disk attaching maps (no reliance on the upstream
labelling-convention PDF), and the tree-collapse presentation is recomputed for EVERY
spanning tree of every surface, not just the one the project's builder happened to pick.

Checks performed per (surface, spanning tree):
  1  #disks = V+1, total attaching length = 6V, every edge label occurs exactly 3x
  2  the reconstructed singular graph has exactly V vertices, all of degree 4, connected
  3  RAW collapse (delete tree letters, no reduction): V+1 generators, V+1 relators,
     total length 3V+3, every generator exactly 3 occurrences
  4  FREELY REDUCED collapse: same four conditions -- this is the version that matters,
     because a presentation is a set of free-group ELEMENTS and every downstream filter
     (R8 section 6) is applied to reduced words
  5  CYCLICALLY reduced collapse: same again
  6  empty relators after collapse (would break balancedness)

Usage: python3 experiments/stable_ac/fable/r8_audit_a1_trees.py [--csv PATH] [--max-rows N]
"""

from __future__ import annotations

import argparse
import csv
import itertools
import json
import os
from collections import Counter, defaultdict

ALPHABET = "abcdefghijklmnopqrstuvwxyz"


# ------------------------------------------------------------------ census parsing

def tokenize(field: str, max_label: int) -> list[int]:
    """Parse an attaching map like '42-1-1-2431-3' into [4,2,-1,-1,-2,4,3,1,-3].

    Greedy longest digit run whose value is a legal edge label (1..max_label).  For
    max_label <= 10 this is the unique legal parse (label 0 does not exist and no label
    exceeds 10), and the per-row invariants in check 1 independently confirm it.
    """
    out: list[int] = []
    i = 0
    n = len(field)
    while i < n:
        sign = 1
        if field[i] == "-":
            sign = -1
            i += 1
        j = i
        while j < n and field[j].isdigit():
            j += 1
        if j == i:
            raise ValueError(f"bad field {field!r} at {i}")
        best = None
        for k in range(j, i, -1):                    # longest first
            val = int(field[i:k])
            if 1 <= val <= max_label:
                best = (val, k)
                break
        if best is None:
            raise ValueError(f"no legal label in {field!r} at {i}")
        out.append(sign * best[0])
        i = best[1]
    return out


def load_census(path: str):
    rows = []
    with open(path, newline="", encoding="utf-8") as fh:
        for lineno, fields in enumerate(csv.reader(fh), start=1):
            if not fields or not fields[0].strip():
                continue
            V = int(fields[0])
            skeleton = int(fields[1])
            disks = []
            i = 2
            while i < len(fields) and fields[i].strip():
                disks.append(tokenize(fields[i].strip(), 2 * V))
                i += 3                                # disk, embedded?, trivial T-bundle?
            rows.append({"line": lineno, "V": V, "skeleton": skeleton, "disks": disks})
    return rows


# ------------------------------------------------------------------ singular graph

class DSU:
    def __init__(self, items):
        self.p = {x: x for x in items}

    def find(self, x):
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[ra] = rb


def start_end(letter: int):
    """Ends of a directed traversal: end 0 = tail, end 1 = head."""
    e = abs(letter)
    return ((e, 0), (e, 1)) if letter > 0 else ((e, 1), (e, 0))


def reconstruct_skeleton(V: int, disks):
    """Recover the vertex set of the singular graph from the disk boundary walks alone.

    Consecutive edges in a disk's boundary walk meet at a vertex, so identifying
    end(x_i) with start(x_{i+1}) cyclically over every disk glues the 4V edge-ends into
    the true vertex classes (each vertex's four germs are pairwise joined by its six
    K4-link corners, so the identification is complete).  Returns (endpoints, nverts).
    """
    ends = [(e, s) for e in range(1, 2 * V + 1) for s in (0, 1)]
    dsu = DSU(ends)
    for disk in disks:
        m = len(disk)
        for i in range(m):
            _, e_i = start_end(disk[i])
            s_next, _ = start_end(disk[(i + 1) % m])
            dsu.union(e_i, s_next)
    classes = defaultdict(list)
    for x in ends:
        classes[dsu.find(x)].append(x)
    names = {root: idx for idx, root in enumerate(sorted(classes))}
    endpoints = {e: (names[dsu.find((e, 0))], names[dsu.find((e, 1))])
                 for e in range(1, 2 * V + 1)}
    degrees = Counter(len(v) for v in classes.values())
    return endpoints, len(classes), degrees


def spanning_trees(V: int, endpoints):
    """Every spanning tree, as a frozenset of edge labels (V-1 of them)."""
    edges = sorted(endpoints)
    out = []
    for subset in itertools.combinations(edges, max(V - 1, 0)):
        parent = {v: v for v in range(V)}

        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x

        ok = True
        for e in subset:
            u, v = endpoints[e]
            ru, rv = find(u), find(v)
            if ru == rv:                              # loop or cycle
                ok = False
                break
            parent[ru] = rv
        if ok and len({find(v) for v in range(V)}) == 1:
            out.append(frozenset(subset))
    return out


# ------------------------------------------------------------------ collapse

def collapse(disks, tree: frozenset, nedges: int):
    """Delete tree letters and relabel the survivors to a,b,c,... (no reduction)."""
    survivors = [e for e in range(1, nedges + 1) if e not in tree]
    letter = {e: ALPHABET[i] for i, e in enumerate(survivors)}
    words = []
    for disk in disks:
        w = []
        for x in disk:
            e = abs(x)
            if e in tree:
                continue
            w.append(letter[e] if x > 0 else letter[e].upper())
        words.append("".join(w))
    return words


def free_reduce(word: str) -> str:
    out: list[str] = []
    for ch in word:
        if out and out[-1] == ch.swapcase():
            out.pop()
        else:
            out.append(ch)
    return "".join(out)


def cyclic_reduce(word: str) -> str:
    w = free_reduce(word)
    while len(w) > 1 and w[0] == w[-1].swapcase():
        w = w[1:-1]
        w = free_reduce(w)
    return w


def occ(words) -> Counter:
    return Counter(c.lower() for w in words for c in w)


def profile_ok(words, V: int):
    gens = sorted({c.lower() for w in words for c in w})
    o = occ(words)
    return {
        "n_relators_V+1": len(words) == V + 1,
        "n_generators_V+1": len(gens) == V + 1,
        "every_gen_3x": bool(gens) and all(o[g] == 3 for g in gens),
        "length_3V+3": sum(len(w) for w in words) == 3 * V + 3,
        "no_empty_relator": all(len(w) > 0 for w in words),
        "occvec": tuple(o[g] for g in gens),
        "length": sum(len(w) for w in words),
        "ngens": len(gens),
    }


# ------------------------------------------------------------------ main

def main(argv=None):
    here = os.path.dirname(os.path.abspath(__file__))
    repo = os.path.dirname(os.path.dirname(os.path.dirname(here)))
    default_csv = ("/tmp/claude-0/-home-user-ACSolverX/"
                   "3b1e6f55-9c29-53f6-95b5-fd7ded7bcafc/scratchpad/"
                   "Fake-Surfaces/fakesurfaces.csv")
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=default_csv)
    ap.add_argument("--max-rows", type=int, default=0)
    ap.add_argument("--out", default=os.path.join(
        repo, "results", "stable_ac", "fable", "r8_audit_a1_trees.json"))
    args = ap.parse_args(argv)

    rows = load_census(args.csv)
    if args.max_rows:
        rows = rows[:args.max_rows]
    print(f"[census] rows parsed: {len(rows)}")
    print(f"[census] by complexity: "
          f"{dict(sorted(Counter(r['V'] for r in rows).items()))}")

    fail1 = fail2 = 0
    tree_counts = Counter()
    raw_fail, red_fail, cyc_fail, empty_fail = [], [], [], []
    backtrack_rows, k4_fail = [], []
    pairs = 0
    shrink_examples = []
    per_V_trees = defaultdict(Counter)
    for r in rows:
        V, disks = r["V"], r["disks"]
        # ---- check 1: census-level invariants
        lengths = sum(len(d) for d in disks)
        labels = Counter(abs(x) for d in disks for x in d)
        c1 = (len(disks) == V + 1 and lengths == 6 * V
              and set(labels) == set(range(1, 2 * V + 1))
              and all(labels[e] == 3 for e in labels))
        if not c1:
            fail1 += 1
            if len(raw_fail) < 5:
                print(f"[1] FAIL line {r['line']} V={V} disks={len(disks)} "
                      f"len={lengths} labels={dict(labels)}")
            continue
        # ---- check 2: intrinsic skeleton
        endpoints, nverts, degrees = reconstruct_skeleton(V, disks)
        c2 = (nverts == V and set(degrees) == {4})
        if not c2:
            fail2 += 1
            if fail2 <= 5:
                print(f"[2] FAIL line {r['line']} V={V} nverts={nverts} "
                      f"degrees={dict(degrees)}")
            continue
        # ---- check 7: every raw attaching walk is CYCLICALLY REDUCED (no backtrack).
        # This is the hypothesis of the repair lemma for A1: a cancellation under
        # tree-collapse needs a closed walk in the tree between two mutually inverse
        # non-tree letters, and a closed walk in a tree contains a backtrack, so
        # backtrack-free attaching maps make free reduction a no-op after collapse.
        for disk in disks:
            m = len(disk)
            if m > 1 and any(disk[(i + 1) % m] == -disk[i] for i in range(m)):
                backtrack_rows.append((r["line"], V, disk))
                break
        # ---- check 8: the K4-link condition -- at each vertex the 6 corners realize
        # the 6 distinct unordered pairs of its 4 germs, each exactly once (so no corner
        # repeats a germ, which is what forbids backtracks).
        corners = defaultdict(Counter)
        germs_at = defaultdict(set)
        for e, (u, v) in endpoints.items():
            germs_at[u].add((e, 0))
            germs_at[v].add((e, 1))
        for disk in disks:
            m = len(disk)
            for i in range(m):
                _, g_in = start_end(disk[i])
                g_out, _ = start_end(disk[(i + 1) % m])
                vtx = endpoints[g_in[0]][g_in[1]]
                corners[vtx][frozenset((g_in, g_out)) if g_in != g_out
                             else ("SELF", g_in)] += 1
        for vtx in range(V):
            want = {frozenset(p) for p in itertools.combinations(sorted(germs_at[vtx]), 2)}
            got = corners[vtx]
            if len(germs_at[vtx]) != 4 or set(got) != want or set(got.values()) != {1}:
                k4_fail.append((r["line"], V, vtx, dict(got)))
                break
        trees = spanning_trees(V, endpoints)
        tree_counts[len(trees)] += 1
        per_V_trees[V][len(trees)] += 1
        for T in trees:
            pairs += 1
            raw = collapse(disks, T, 2 * V)
            pr = profile_ok(raw, V)
            if not (pr["n_relators_V+1"] and pr["n_generators_V+1"]
                    and pr["every_gen_3x"] and pr["length_3V+3"]):
                raw_fail.append((r["line"], V, sorted(T), raw, pr))
            if not pr["no_empty_relator"]:
                empty_fail.append((r["line"], V, sorted(T), raw))
            red = [free_reduce(w) for w in raw]
            pf = profile_ok(red, V)
            if not (pf["every_gen_3x"] and pf["length_3V+3"]
                    and pf["n_generators_V+1"]):
                red_fail.append((r["line"], V, sorted(T), raw, red, pf))
                if len(shrink_examples) < 12:
                    shrink_examples.append({
                        "csv_line": r["line"], "V": V, "skeleton": r["skeleton"],
                        "tree": sorted(T), "raw": raw, "reduced": red,
                        "raw_occ": dict(occ(raw)), "reduced_occ": dict(occ(red)),
                        "raw_len": sum(map(len, raw)),
                        "reduced_len": sum(map(len, red))})
            cyc = [cyclic_reduce(w) for w in raw]
            pc = profile_ok(cyc, V)
            if not (pc["every_gen_3x"] and pc["length_3V+3"]
                    and pc["n_generators_V+1"]):
                cyc_fail.append((r["line"], V, sorted(T), raw, cyc, pc))

    print("-" * 78)
    print(f"[1] census invariant failures (disks/length/3-germs) : {fail1}")
    print(f"[2] skeleton reconstruction failures (V verts, 4-reg): {fail2}")
    print(f"[T] spanning trees per surface, distribution         : "
          f"{dict(sorted(tree_counts.items()))}")
    for V in sorted(per_V_trees):
        print(f"[T]   V={V}: {dict(sorted(per_V_trees[V].items()))}")
    print(f"[T] (surface, spanning tree) pairs tested            : {pairs}")
    print(f"[3] RAW-collapse profile failures                    : {len(raw_fail)}")
    print(f"[6] collapses producing an EMPTY relator             : {len(empty_fail)}")
    print(f"[4] FREELY-REDUCED profile failures                  : {len(red_fail)}")
    print(f"[5] CYCLICALLY-REDUCED profile failures              : {len(cyc_fail)}")
    print(f"[7] surfaces with a BACKTRACK in some attaching walk  : {len(backtrack_rows)}")
    print(f"[8] surfaces failing the K4-link corner condition     : {len(k4_fail)}")
    for row in backtrack_rows[:5]:
        print(f"[7] example: csv line {row[0]} V={row[1]} disk={row[2]}")
    for row in k4_fail[:5]:
        print(f"[8] example: csv line {row[0]} V={row[1]} vertex={row[2]}")
    for ex in shrink_examples[:6]:
        print(f"[4] example: csv line {ex['csv_line']} V={ex['V']} tree={ex['tree']}")
        print(f"[4]   raw      {ex['raw']}  occ={ex['raw_occ']} len={ex['raw_len']}")
        print(f"[4]   reduced  {ex['reduced']}  occ={ex['reduced_occ']} "
              f"len={ex['reduced_len']}")

    verdict = (fail1 == 0 and fail2 == 0 and not raw_fail and not empty_fail
               and not red_fail and not cyc_fail and not backtrack_rows
               and not k4_fail)
    print("-" * 78)
    print(f"A1 over EVERY spanning tree: {'CONFIRMED' if verdict else 'BROKEN'}")

    payload = {
        "record": "r8_audit_a1_trees",
        "census_rows": len(rows),
        "census_invariant_failures": fail1,
        "skeleton_reconstruction_failures": fail2,
        "spanning_tree_distribution": {str(k): v for k, v in sorted(tree_counts.items())},
        "trees_by_complexity": {str(V): {str(k): v for k, v in sorted(c.items())}
                                for V, c in sorted(per_V_trees.items())},
        "surface_tree_pairs": pairs,
        "raw_profile_failures": len(raw_fail),
        "empty_relator_collapses": len(empty_fail),
        "freely_reduced_profile_failures": len(red_fail),
        "cyclically_reduced_profile_failures": len(cyc_fail),
        "reduced_failure_examples": shrink_examples,
        "attaching_walk_backtracks": len(backtrack_rows),
        "k4_link_condition_failures": len(k4_fail),
        "verdict_A1_all_trees": "CONFIRMED" if verdict else "BROKEN",
    }
    with open(args.out, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1)
    print(f"[out] {args.out}")
    return payload


if __name__ == "__main__":
    main()
