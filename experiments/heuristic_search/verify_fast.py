"""Prove the numba kernel reproduces the slow solver, on the states where they could differ.

The obvious check -- run ``BASELINE_CONFIG`` and compare against ``greedy_search`` -- is vacuous
for this particular change. Ordering by length pops the shortest state available, so a baseline
search never leaves the short regime, never generates the ten-thousand-candidate expansions the
kernel exists for, and never exercises the tie-break pressure that a structural ordering puts on
``(priority, depth, key)``. It would pass whether or not the kernel is correct.

The sensitive regime is the *runaway* configs: the ones whose stored rows show long popped
relators and high node counts. Those are already on disk, computed by the slow solver, in
``EXP02_single.jsonl``. So this replays them and demands every field match exactly -- ``solved``,
``nodes``, ``path_length``, ``min_total``, ``max_pop``. Agreement there is agreement everywhere,
because a divergence in enumeration order, key sorting or feature arithmetic shows up first, and
most violently, where the state space is widest.

    python3 -m experiments.heuristic_search.verify_fast [--configs N] [--deadline SEC]
"""
import argparse
import collections
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import LOGS, load_split       # noqa: E402
from experiments.heuristic_search.hfast import search_fast           # noqa: E402
from experiments.heuristic_search.exp02_single import (              # noqa: E402
    OUT as EXP02_OUT, BUDGET, MRL, SLICE, configs as exp02_configs,
)

FIELDS = ("solved", "nodes", "path_length", "min_total", "max_pop")


def stored():
    """{config_id: {name: row}} for every complete config in EXP-02's jsonl."""
    by = collections.defaultdict(dict)
    with open(EXP02_OUT) as f:
        for line in f:
            try:
                r = json.loads(line)
            except ValueError:
                continue
            by[r["config_id"]][r["name"]] = r
    return by


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--configs", type=int, default=14)
    ap.add_argument("--deadline", type=float, default=1800.0)
    a = ap.parse_args()

    have = stored()
    cfgs, _ = exp02_configs()
    by_id = {}
    from experiments.heuristic_search.hlab import cfg_name
    for c in cfgs:
        by_id[cfg_name(c)] = c

    rows = {r["name"]: r for r in load_split(SLICE)}
    full = {cid: v for cid, v in have.items() if len(v) == len(rows)}

    # Rank by how hard the slow solver found them: the widest expansions are where a divergence
    # in enumeration order or key sorting would surface. Longest popped relator first, then nodes.
    def cost(cid):
        v = full[cid]
        return (max(r["max_pop"] for r in v.values()),
                sum(r["nodes"] for r in v.values()))

    order = sorted(full, key=cost, reverse=True)[:a.configs]

    print(f"  {len(full)} complete configs on disk; replaying the {len(order)} widest", flush=True)
    t0 = time.perf_counter()
    checked = mism = 0
    bad = []
    for n, cid in enumerate(order, 1):
        if cid not in by_id:
            continue
        cfg = by_id[cid]
        mp, nd = cost(cid)
        for name, want in full[cid].items():
            got = search_fast(rows[name]["r1"], rows[name]["r2"], BUDGET, cfg, MRL)
            checked += 1
            diff = {k: (want[k], got[k]) for k in FIELDS if want[k] != got[k]}
            if diff:
                mism += 1
                bad.append({"config_id": cid, "name": name, "diff": diff})
        el = time.perf_counter() - t0
        print(f"    [{n}/{len(order)}] {cid[:44]:44s} maxpop={mp:>3d} nodes={nd:>6d}  "
              f"{checked} rows, {mism} mismatched, {el/60:.1f} min", flush=True)
        if el > a.deadline:
            print("    deadline reached — stopping", flush=True)
            break

    out = {"budget": BUDGET, "mrl": MRL, "slice": SLICE, "configs_checked": n,
           "rows_checked": checked, "mismatches": mism, "detail": bad[:40]}
    with open(os.path.join(LOGS, "verify_fast.json"), "w") as f:
        json.dump(out, f, indent=1)

    print(f"\n  {checked} rows replayed, {mism} mismatched", flush=True)
    if mism:
        for b in bad[:10]:
            print(f"    {b['config_id'][:50]} {b['name']}: {b['diff']}", flush=True)
        raise SystemExit("FAST KERNEL DIVERGES — do not append its rows to the slow solver's file")
    print("  IDENTICAL — the fast kernel may extend EXP-02's file", flush=True)


if __name__ == "__main__":
    main()
