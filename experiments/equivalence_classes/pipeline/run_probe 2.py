"""The ACA probe: re-seed the **class reps** and push the knobs the production sweep left alone.

`run_sweep.py` seeds the 261 raw reps and settles the partition. This runner seeds the *classes*
that sweep produced (plus TRIVIAL, as a 127th source, so a merge with it would be an actual SOLVE)
and turns on one lever at a time. Fewer sources means a deeper search per source for the same
wall clock -- which is the point, because the levers that matter are the ones that need depth.

Production was  `moves=seam  max_total=28  budget=250`  ->  126 classes.

The lever that mattered was **`max_total`**. The convergence study varied the move set
(`seam`/`full`) and the seed sources (`+ms`/`+jsonl`) but never raised the ceiling past 28, and on
that basis the search was reported converged. It was not: at `max_total=34` this runner found

    21_3  ==  21_29        (both singletons in the 126)  ->  125 classes

The two roots meet at Aut-minimal total length **30**. At cap 28 that merge was not out of budget,
it was **outside the search space** -- no budget could ever have reached it. See
`results/equivalence_classes/EQUIVALENCE_FINDING.md` section 3b.

Two negatives from the same sweep of arms, worth as much as the positive:
  * `--levelset` closes the one incompleteness `aut_search` documents in its own docstring
    (it expands ONE representative per Aut-class) and returns the SAME partition.
  * A higher ceiling is not monotonically better: cap 40 *contains* the length-30 meeting point
    and still missed the merge, because a wider cap lets far more children past the phase-1
    prefilter and buys fewer pops per second. Tune the ceiling; do not maximise it.

Usage:
    run_probe.py --tag seam34 --moves seam --max-total 34 --budget 1000 --time 1680
    run_probe.py --tag ls28   --moves full --max-total 28 --budget 1000 --levelset

Writes: results/equivalence_classes/probe/probe_<tag>.json
"""
import argparse
import csv
import json
import os
import sys
import time


# The repo root, found by walking up rather than by counting directory levels. A dirname chain
# encodes this file's depth and silently repoints at the wrong directory the moment it moves.
def _repo_root():
    d = os.path.dirname(os.path.abspath(__file__))
    while d != os.path.dirname(d):
        if (os.path.isdir(os.path.join(d, "experiments"))
                and os.path.isdir(os.path.join(d, "data"))):
            return d
        d = os.path.dirname(d)
    raise RuntimeError("repo root (holding experiments/ and data/) not found")


ROOT = _repo_root()
sys.path.insert(0, ROOT)

import experiments.equivalence_classes.search.aut_search as aut_search  # noqa: E402
from experiments.equivalence_classes.search.aut_search import aut_key, aut_multi_search  # noqa: E402
from experiments.equivalence_classes.search.levelset import levelset_children  # noqa: E402
from experiments.equivalence_classes.search import levelset as levelset_mod  # noqa: E402

MANIFEST = os.path.join(ROOT, "results", "equivalence_classes", "sweep",
                        "classes_126_from_greedy_1000000_261_mrl48.jsonl")
JSONL_1M = os.path.join(ROOT, "results", "greedy_baseline",
                        "greedy_1000000_261_mrl48_cyc_all_07_09_26.jsonl")
REPS_CSV = os.path.join(ROOT, "data", "ms_unsolved_reps", "ms_reps_unsolved.csv")
OUT = os.path.join(ROOT, "results", "equivalence_classes", "probe")
TRIVIAL = "TRIVIAL"

# Searches launched from this repo are capped at 1,000 nodes/source (see CLAUDE.md). A search at
# budget B is exactly the first B pops of any longer one, so a bigger budget buys a slower repro,
# never different behaviour -- and this runner's whole point is that the CEILING, not the budget,
# is what changes the answer.
MAX_BUDGET = 1_000


def load_sources(use_jsonl):
    """The 126 class reps + TRIVIAL, optionally + the 783 recorded 1M-node states as pre-unions."""
    classes = [json.loads(line) for line in open(MANIFEST)]
    sources = [(f"C{c['class_id']}", c["r1"], c["r2"]) for c in classes]
    sources.append((TRIVIAL, "x", "y"))
    idx = {n: i for i, (n, _, _) in enumerate(sources)}
    pre_union = []

    if use_jsonl:
        # Each recorded state was emitted by that row's own search, so it is AC-reachable from its
        # root by construction: pre-unioning it is free reach, not an assumption.
        names = [r["name"] for r in csv.DictReader(open(REPS_CSV))]
        cls_of = {m: c["class_id"] for c in classes for m in c["members"]}
        for line in open(JSONL_1M):
            row = json.loads(line)
            if row["pres_id"] >= len(names):
                continue
            name = names[row["pres_id"]]
            if name not in cls_of:
                continue
            root = idx[f"C{cls_of[name]}"]
            for field in ("min_relator", "max_relator", "max_relator_expanded"):
                v = row.get(field)
                if not v or len(v) != 2 or not v[0] or not v[1]:
                    continue
                pre_union.append((root, len(sources)))
                sources.append((f"J/{name}/{field}", v[0], v[1]))

    return classes, sources, pre_union


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--moves", choices=("seam", "full"), default="seam")
    ap.add_argument("--max-total", type=int, default=34)
    ap.add_argument("--budget", type=int, default=1000)
    ap.add_argument("--time", type=float, default=1680)
    ap.add_argument("--max-states", type=int, default=500_000)
    ap.add_argument("--levelset", action="store_true",
                    help="expand EVERY member of each Aut-class's minimal level set")
    ap.add_argument("--jsonl", action="store_true",
                    help="seed the 783 states the 1M-node sweep recorded, as pre-unions")
    args = ap.parse_args()

    assert args.budget <= MAX_BUDGET, f"budget cap is {MAX_BUDGET} nodes/source"

    if args.levelset:
        # aut_search calls `children` at module scope; swapping it here is what turns on the
        # level-set expansion without modifying aut_search itself.
        aut_search.children = levelset_children

    classes, sources, pre_union = load_sources(args.jsonl)
    n_reps = len(classes)
    rep_names = {f"C{c['class_id']}" for c in classes}

    lens = sorted(aut_key((r1, r2))[0] for (_, r1, r2) in sources[:n_reps])
    print(f"[{args.tag}] sources={len(sources)} ({n_reps} class reps + TRIVIAL"
          f"{f' + {len(pre_union)} recorded states' if pre_union else ''})")
    print(f"[{args.tag}] Aut-min totals: min={lens[0]} med={lens[len(lens)//2]} max={lens[-1]}")
    print(f"[{args.tag}] moves={args.moves} max_total={args.max_total} budget={args.budget} "
          f"levelset={args.levelset} time={args.time}s", flush=True)

    t0 = time.time()

    def progress(pops, states, comps):
        el = time.time() - t0
        print(f"[{args.tag}] {pops:>8} pops {states:>8} states {comps:>4} comps "
              f"{el:>6.0f}s ({pops / max(el, 1e-9):.0f}/s)", flush=True)

    dsu, merges, stats, _roots = aut_multi_search(
        sources, nodes_per_source=args.budget, max_total=args.max_total,
        seam_only=(args.moves == "seam"), max_states=args.max_states,
        progress=progress, time_limit=args.time, pre_union=pre_union)

    elapsed = time.time() - t0
    comps = {}
    for i in range(len(sources)):
        comps.setdefault(dsu.find(i), []).append(sources[i][0])

    rep_classes = [sorted(n for n in v if n in rep_names) for v in comps.values()]
    rep_classes = [c for c in rep_classes if c]
    # NOT dsu.find(len(sources) - 1): TRIVIAL is the last source only when nothing was appended
    # after it, which is false as soon as --jsonl adds bridges. That bug once produced a false
    # SOLVED report; see EQUIVALENCE_FINDING.md.
    triv = dsu.find(next(i for i, (n, _, _) in enumerate(sources) if n == TRIVIAL))
    solved = [n for n in comps[triv] if n in rep_names]
    new = [c for c in rep_classes if len(c) > 1]

    print(f"\n{'=' * 66}")
    print(f"[{args.tag}] pops={stats['popped']} states={stats['states']} {elapsed:.0f}s"
          f"{'  [STATE CAP]' if stats['capped'] else ''}"
          f"{'  [TIME LIMIT]' if stats.get('timed_out') else ''}")
    print(f"[{args.tag}] CLASSES over the {n_reps} : {len(rep_classes)}   (baseline {n_reps})")
    print(f"[{args.tag}] *** NEW MERGES *** : {len(new)}  {new}")
    print(f"[{args.tag}] SOLVED (hit trivial): {len(solved)}  {solved}")
    if args.levelset:
        print(f"[{args.tag}] levelset: {levelset_mod.stats}")

    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, f"probe_{args.tag}.json")
    with open(path, "w") as f:
        json.dump({
            "tag": args.tag,
            "config": {"moves": args.moves, "max_total": args.max_total,
                       "budget": args.budget, "levelset": args.levelset,
                       "jsonl": args.jsonl, "sources": len(sources)},
            "stats": {**stats, "seconds": round(elapsed, 1)},
            "n_classes": len(rep_classes),
            "new_merges": new,
            "solved": solved,
            "merges": [{"kind": m["kind"], "a": m["a"], "b": m["b"], "at": list(m["at"]),
                        "len_a": len(m["path_a"]), "len_b": len(m["path_b"]),
                        "path_a": [[list(s[0]), s[1], list(s[2])] for s in m["path_a"]],
                        "path_b": [[list(s[0]), s[1], list(s[2])] for s in m["path_b"]]}
                       for m in merges],
        }, f, indent=1)
    print(f"[{args.tag}] wrote {path}", flush=True)


if __name__ == "__main__":
    main()
