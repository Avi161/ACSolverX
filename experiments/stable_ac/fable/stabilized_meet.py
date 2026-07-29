"""Forward harvest from STABILISED AK(3) at ranks 4-6, meeting the certified targets.

`target_meet.py` established that the rank of a presentation is the binding constraint:
AC1/AC2/AC3 preserve it, and no census target is destabilisable (0 of 5,389 admit an
AC5), so a rank-r target can only ever be met by a rank-r forward state.  Our corpora
were rank 2 and 3, which made only 19 of the 5,389 certified targets eligible.

This module searches where the other 5,370 live.  Starting from AK(3) plus k plain
stabilisations (rank 2+k), it runs the same rotation-expanded operator the contrast
harvests use, and tests every popped state against the certified target set of its own
rank.  Rank 6 is the interesting one: stabilised AK(3) has 6 generators and total
length 17, while the 514 complexity-5 targets have 6 generators and total length 18.

A match means AK(3) is stable-AC-equivalent to a presentation that is certified stably
AC-trivial, i.e. **AK(3) is stably AC-trivial** — the headline sub-goal. It is written
out as a CANDIDATE with a loud flag and never treated as a claim: the hit protocol
(explicit AC1-AC5 move list, full replay, Todd-Coxeter certificate) comes first.

Budget: the harvest is best-first and capped at :data:`POPS` = 1,000 pops per rank, the
hard session limit. Production scale is the user's Colab tier (Run E in
`R1_COLAB_RUNNER_SPEC.md`).
"""

from __future__ import annotations

import argparse
import heapq
import json
import os
import sys
import time
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from ac_words import cyclic_reduce, inverse                     # noqa: E402
from certified_targets import (REPO_ROOT, TARGETS_JSON, canon_multi,  # noqa: E402
                               load_targets, match)

DEFAULT_OUT = os.path.join(REPO_ROOT, "results", "stable_ac", "fable",
                           "stabilized_meet.json")
AK3 = ("xxxYYYY", "xyxYXY")
STABILISERS = "zwvu"          # fresh generators, in the order they are adjoined
POPS = 1_000                  # hard session limit, per rank
SLACK = 4                     # length cap = starting total length + SLACK


def stabilise(base, k: int):
    """AK(3) plus k plain stabilisations: rank 2+k, one fresh relator each."""
    if k > len(STABILISERS):
        raise ValueError(f"only {len(STABILISERS)} stabilisers available")
    return tuple(base) + tuple(STABILISERS[:k])


def rotations(word: str):
    return [word[i:] + word[:i] for i in range(len(word))]


def children(state, cap: int):
    """Rotation-expanded AC2 grafts, cyclically reduced, within the length cap.

    Identical in shape to the operator used by `ak2_battery` / the contrast harvests,
    generalised to arbitrary rank: every ordered pair of relators, every rotation of
    host and guest, both guest signs.
    """
    out = set()
    n = len(state)
    for host in range(n):
        for guest in range(n):
            if host == guest:
                continue
            for hw in rotations(state[host]):
                for gw in rotations(state[guest]):
                    for word in (gw, inverse(gw)):
                        merged = cyclic_reduce(hw + word)
                        if not merged:
                            continue
                        image = list(state)
                        image[host] = merged
                        if sum(len(w) for w in image) <= cap:
                            out.add(tuple(image))
    return out


def harvest(root, targets: dict, pops: int = POPS, slack: int = SLACK) -> dict:
    cap = sum(len(w) for w in root) + slack
    start_key = canon_multi(root)
    seen = {start_key: tuple(root)}
    heap = [(sum(len(w) for w in root), 0, tuple(root))]
    tie = 0
    hits = []
    popped = 0
    length_hist: Counter = Counter()
    t0 = time.time()

    found = match(root, targets)
    if found is not None:
        hits.append({"state": list(root), "match": found, "popped_at": 0})

    while heap and popped < pops:
        _priority, _t, state = heapq.heappop(heap)
        popped += 1
        for child in children(state, cap):
            key = canon_multi(child)
            if key in seen:
                continue
            seen[key] = child
            length_hist[sum(len(w) for w in child)] += 1
            found = match(child, targets)
            if found is not None:
                hits.append({"state": list(child), "match": found,
                             "popped_at": popped,
                             "replay_required": ("CANDIDATE: reconstruct the explicit "
                                                 "AC1-AC5 move list and replay before "
                                                 "any claim")})
            tie += 1
            heap.append((sum(len(w) for w in child), tie, child))
        heapq.heapify(heap)

    return {
        "root": list(root),
        "rank": len({c.lower() for w in root for c in w}),
        "length_cap": cap,
        "pops": popped,
        "distinct_states": len(seen),
        "queue_remaining": len(heap),
        "length_histogram": {str(k): v for k, v in sorted(length_hist.items())},
        "hits": hits,
        "elapsed_seconds": round(time.time() - t0, 1),
    }


def run(out_path: str = DEFAULT_OUT, ranks=(4, 5, 6), pops: int = POPS) -> dict:
    targets = load_targets(TARGETS_JSON)
    by_rank: Counter = Counter()
    for entry in targets["entries"]:
        by_rank[len({c.lower() for w in entry["relators"] for c in w})] += 1
    print(f"[stab] certified targets by rank: {dict(sorted(by_rank.items()))}",
          flush=True)

    report = {"record": "stabilized_meet", "pops_per_rank": pops,
              "targets_by_rank": {str(k): v for k, v in sorted(by_rank.items())},
              "targets_meta": targets["meta"], "runs": []}
    for rank in ranks:
        k = rank - 2
        root = stabilise(AK3, k)
        print(f"[stab] rank {rank}: root {root} (AK(3) + {k} stabilisations), "
              f"{by_rank.get(rank, 0)} targets at this rank", flush=True)
        stats = harvest(root, targets, pops=pops)
        stats["stabilisations"] = k
        stats["targets_at_rank"] = by_rank.get(rank, 0)
        report["runs"].append(stats)
        print(f"[stab]   {stats['distinct_states']} states, "
              f"{len(stats['hits'])} MATCHES ({stats['elapsed_seconds']}s)", flush=True)

    report["TOTAL_MATCHES"] = sum(len(r["hits"]) for r in report["runs"])
    report["LOUD_HIT_ALERT"] = bool(report["TOTAL_MATCHES"])
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=1)
    print(f"[stab] wrote {out_path}; TOTAL MATCHES {report['TOTAL_MATCHES']}",
          flush=True)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--pops", type=int, default=POPS)
    parser.add_argument("--ranks", default="4,5,6")
    args = parser.parse_args(argv)
    if args.pops > POPS:
        raise SystemExit(f"budget rule: at most {POPS} pops per rank in-session")
    run(args.out, tuple(int(r) for r in args.ranks.split(",")), args.pops)


if __name__ == "__main__":
    main()
