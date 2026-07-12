"""Phase 2: the 262-source ACA sweep (261 reps + the trivial presentation).

Feeding all 261 reps -- not the 168 Aut-minimal ones -- is deliberate: the search collapses the
Aut-duplicates itself at seed time (``kind: "aut"``), which reproduces the known 261 -> 168 as a
by-product and is a free consistency check on the rest of the machinery.

The trivial presentation is source 262. If any rep's ball reaches it, that rep is **SOLVED**.

Optionally (``+ms``) the 550 raw unsolved Miller-Schupp presentations are seeded too, as extra
**bridge** sources. Each MS(n, w) is AC-equivalent to the rep the grid names (verified 12/12 by
this same search), so a component containing MS cells whose reps differ merges those reps. The
bridges cost nothing in rigour -- they are ordinary sources -- and they route through the
*unreduced* presentations, which the reps, being local minima of the upstream reduction, cannot
reach on their own.

Usage:  run_sweep.py <max_total> <budget_per_source> [seam|full] [time_limit_s] [+ms]
Writes: results/equivalence_classes/sweep_<moves>_<max_total>_<budget>[_ms].json
"""
import csv
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.equivalence_classes.aut_search import aut_key, aut_multi_search  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, "results", "equivalence_classes")
TRIVIAL = "TRIVIAL"


def load_reps():
    p = os.path.join(ROOT, "data", "ms_unsolved_reps", "ms_reps_unsolved.csv")
    return [(r["name"], r["r1"], r["r2"]) for r in csv.DictReader(open(p))]


def load_jsonl_states():
    """The states the 1M-node sweep recorded, as (source_name, r1, r2, pre_union_with).

    Each row of the jsonl carries `min_relator`, `max_relator` and `max_relator_expanded` -- the
    shortest / longest state that row's search *discovered*. Being emitted by ``expand_node_nj``
    from that row's root, each is AC-reachable from it **by construction**, so it can be
    pre-unioned with its root: no search needed, and no soundness given up.

    This is the cheapest possible upgrade. Those 783 states cost a million nodes each to find,
    and they sit deep in regions the reps -- which are local minima of the upstream reduction --
    cannot get to on their own. Seeding them hands the ACA search that reach for free.
    """
    import json as _json
    reps = load_reps()
    by_id = {i: n for i, (n, _, _) in enumerate(reps)}
    p = os.path.join(ROOT, "results", "greedy_baseline",
                     "greedy_1000000_261_mrl48_cyc_all_07_09_26.jsonl")
    out = []
    for line in open(p):
        row = _json.loads(line)
        name = by_id.get(row["pres_id"])
        if name is None:
            continue
        for fld in ("min_relator", "max_relator", "max_relator_expanded"):
            v = row.get(fld)
            if not v or len(v) != 2 or not v[0] or not v[1]:
                continue
            out.append((f"J/{name}/{fld}", v[0], v[1], name))
    return out


def load_ms_cells():
    """The 550 unsolved Miller-Schupp cells, as (source_name, r1, r2)."""
    from experiments.equivalence_classes.words import ms_presentation
    p = os.path.join(ROOT, "data", "ms_unsolved_reps", "ms_solved_grid.csv")
    rows = list(csv.reader(open(p)))
    ns = [c for c in rows[0][1:] if c.strip()]
    out = []
    for row in rows[1:]:
        w = row[0]
        if not w:
            continue
        for j, n in enumerate(ns):
            v = row[1 + j].strip()
            if v and v != "trivial":
                r1, r2 = ms_presentation(int(n), w)
                out.append((f"MS/{n}/{w}", r1, r2))
    return out


def main():
    max_total = int(sys.argv[1]) if len(sys.argv) > 1 else 26
    budget = int(sys.argv[2]) if len(sys.argv) > 2 else 2000
    moves = sys.argv[3] if len(sys.argv) > 3 else "seam"
    seam_only = (moves == "seam")
    time_limit = float(sys.argv[4]) if len(sys.argv) > 4 else None
    use_ms = "+ms" in sys.argv
    use_j = "+jsonl" in sys.argv

    reps = load_reps()
    sources = reps + [(TRIVIAL, "x", "y")]
    idx = {n: i for i, (n, _, _) in enumerate(sources)}
    pre_union = []
    if use_ms:
        sources += load_ms_cells()
    if use_j:
        for (name, r1, r2, root) in load_jsonl_states():
            pre_union.append((idx[root], len(sources)))
            sources.append((name, r1, r2))

    lens = sorted(aut_key((r1, r2))[0] for (_, r1, r2) in reps)
    extra = (" + 550 MS bridges" if use_ms else "") + \
            (f" + {len(pre_union)} recorded 1M-node states" if use_j else "")
    print(f"sources        : {len(sources)} (261 reps + trivial{extra})")
    print(f"Aut-min totals : min={lens[0]} median={lens[len(lens)//2]} max={lens[-1]}")
    print(f"config         : moves={moves} max_total={max_total} budget={budget}/source\n")

    t0 = time.time()

    def prog(pops, states, comps):
        el = time.time() - t0
        print(f"  {pops:>7} pops  {states:>7} states  {comps:>4} components  "
              f"{el:>6.0f}s  ({pops/max(el,1e-9):.0f} pops/s)", flush=True)

    dsu, merges, stats, roots_of = aut_multi_search(
        sources, nodes_per_source=budget, max_total=max_total,
        seam_only=seam_only, max_states=1_500_000, progress=prog, time_limit=time_limit,
        pre_union=pre_union)

    el = time.time() - t0
    S = len(sources)
    comps = {}
    for i in range(S):
        comps.setdefault(dsu.find(i), []).append(sources[i][0])

    # NOT dsu.find(S - 1): TRIVIAL is the last source only when no bridges are appended after
    # it. With +ms / +jsonl, S-1 is a bridge, and this reported that bridge's component as
    # "solved" -- which briefly looked like four of the 261 had been trivialised. They had not.
    triv_root = dsu.find(idx[TRIVIAL])
    solved = [n for n in comps[triv_root]
              if n != TRIVIAL and not n.startswith("MS/") and not n.startswith("J/")]

    # the headline number counts the 261 REPS only: MS bridges and trivial are scaffolding
    rep_names = {n for (n, _, _) in reps}
    rep_classes = [sorted(n for n in v if n in rep_names) for v in comps.values()]
    rep_classes = [c for c in rep_classes if c]

    aut_merges = [m for m in merges if m["kind"] == "aut"]
    aca_merges = [m for m in merges if m["kind"] == "aca"]

    print(f"\n{'='*70}")
    print(f"pops {stats['popped']}  states {stats['states']}  {el:.0f}s"
          f"{'  [STATE CAP]' if stats['capped'] else ''}"
          f"{'  [TIME LIMIT]' if stats.get('timed_out') else ''}")
    print(f"root-level Aut merges                 : {len(aut_merges)}")
    print(f"ACA merges found by search            : {len(aca_merges)}")
    print(f"CLASSES over the 261 reps             : {len(rep_classes)}")
    print(f"SOLVED (merged with trivial)          : {len(solved)} {solved[:8]}")

    big = sorted((c for c in rep_classes if len(c) > 1), key=len, reverse=True)
    print(f"\nmulti-member classes: {len(big)}  "
          f"(singletons: {len(rep_classes) - len(big)})")
    for c in big[:14]:
        print(f"   {len(c):>2}  {c}")

    os.makedirs(OUT, exist_ok=True)
    suffix = ("_ms" if use_ms else "") + ("_j" if use_j else "")
    path = os.path.join(OUT, f"sweep_{moves}_{max_total}_{budget}{suffix}.json")
    with open(path, "w") as f:
        json.dump({
            "config": {"moves": moves, "max_total": max_total, "budget": budget,
                       "sources": S, "ms_bridges": use_ms, "jsonl_states": use_j},
            "pre_union": [{"state": sources[b][0], "root": sources[a][0],
                           "r1": sources[b][1], "r2": sources[b][2]}
                          for (a, b) in pre_union],
            "stats": {**stats, "seconds": round(el, 1)},
            "n_classes": len(rep_classes),
            "solved": solved,
            "rep_classes": rep_classes,
            "classes": [sorted(v) for v in comps.values()],
            "merges": [{"kind": m["kind"], "a": m["a"], "b": m["b"], "at": list(m["at"]),
                        "path_a": [[list(s[0]), s[1], list(s[2])] for s in m["path_a"]],
                        "path_b": [[list(s[0]), s[1], list(s[2])] for s in m["path_b"]]}
                       for m in merges],
            "roots": {sources[i][0]: {"raw": list(roots_of[i][0]),
                                      "aut_rep": list(roots_of[i][1]),
                                      "phi": roots_of[i][2]}
                      for i in roots_of},
        }, f, indent=1)
    print(f"\nwrote {path}")


if __name__ == "__main__":
    main()
