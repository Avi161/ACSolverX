"""Meet-in-the-middle: greedy substitution search with TARGET-SET termination.

Wraps the verified n=2 greedy (greedy_nrel) so a search from AK(3)/P25 terminates the
moment it generates any state whose canonical key is in a target set (the certified
stably-AC-trivial descendant catalog, symmetry-expanded), and vice versa. A hit yields
an AC path start -> target which, chained with the target's stable-triviality
certificate (and the Appendix-F bridge if the start is P25), proves AK(3) stably
AC-trivial.

Keys here are greedy_nrel.canonical_key keys (NGEN_MAX=3 byte scheme) — NOT
presentation.canonical_state_key keys. Signed-relabeling expansion happens on the
int-list states BEFORE keying, so per-node membership tests stay O(1).
"""
import heapq
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ONEGEN = os.path.join(ROOT, "experiments", "stable_ac", "one_generator")
for p in (HERE, ONEGEN):
    if p not in sys.path:
        sys.path.insert(0, p)

import greedy_nrel as gn  # noqa: E402
from presentation import relabel_variants  # noqa: E402

INT = gn.INT_DTYPE


def to_np_state(relators):
    return tuple(np.array(r, dtype=INT) for r in relators)


def gn_key(relators):
    return gn.canonical_key(to_np_state(relators))


def symmetry_keys(relators, n_gen=2):
    """gn canonical keys of all 2^k k! signed relabelings of a state."""
    return {gn_key(list(s)) for s in relabel_variants(tuple(list(r) for r in relators),
                                                      n_gen)}


def load_targets(leaves_path, max_len=gn.L, include=None):
    """Target dict: gn_key -> leaf metadata, for leaves whose relators all fit the
    search cap (unreachable otherwise). `include` = extra named states, e.g.
    {"AK3": [...], "P25": [...]}."""
    targets = {}
    n_skipped = 0
    if leaves_path and os.path.exists(leaves_path):
        with open(leaves_path) as f:
            for line in f:
                rec = json.loads(line)
                rels = rec["relators"]
                if any(len(r) >= max_len for r in rels):
                    n_skipped += 1
                    continue
                for k in symmetry_keys(rels):
                    targets.setdefault(k, {"kind": "leaf", "key": rec["key"],
                                           "total_len": rec["total_len"]})
    for name, rels in (include or {}).items():
        for k in symmetry_keys(rels):
            targets.setdefault(k, {"kind": "named", "key": name})
    return targets, n_skipped


class TargetSolver:
    """gn.NRelatorSolver's loop + a target-set membership test on every new node."""

    def __init__(self, relators, n_gen=2, max_nodes=100_000, max_len=gn.L,
                 targets=None):
        self.n_gen = n_gen
        self.max_nodes = max_nodes
        self.max_len = max_len
        self.targets = targets or {}
        self.ball = None           # optional frozen key set; membership == hit
        self.initial_key = gn.canonical_key(to_np_state(relators))
        self.visited = {}
        self.min_total_len = None
        self.hit = None            # (key, meta) on target hit

    def solve(self):
        if self.initial_key in self.targets:
            self.hit = (self.initial_key, self.targets[self.initial_key])
            self.visited[self.initial_key] = None
            return 0
        pq = []
        init_key = self.initial_key
        init_len = sum(len(p) for p in init_key.split(b"\x00"))
        self.min_total_len = init_len
        heapq.heappush(pq, (init_len, 0, init_key))
        self.visited[init_key] = None
        visited, targets, n_gen, max_len = self.visited, self.targets, self.n_gen, self.max_len
        nodes = 0
        while pq and nodes < self.max_nodes:
            _, depth, key = heapq.heappop(pq)
            nodes += 1
            state = gn.key_to_state(key)
            byte_parts = key.split(b"\x00")
            for nbr_state, move in gn.get_neighbors(state, n_gen):
                ci = move[0]
                new_r = nbr_state[ci]
                if len(new_r) >= max_len:
                    continue
                parts = list(byte_parts)
                parts[ci] = gn._relator_bytes(gn.canonical_relator(new_r))
                parts.sort(key=gn._bskey)
                nkey = b"\x00".join(parts)
                if nkey in visited:
                    continue
                visited[nkey] = key
                if nkey in targets:
                    self.hit = (nkey, targets[nkey])
                    return nodes
                if self.ball is not None and nkey in self.ball:
                    self.hit = (nkey, {"kind": "ball"})
                    return nodes
                tl = sum(len(p) for p in parts)
                if tl < self.min_total_len:
                    self.min_total_len = tl
                heapq.heappush(pq, (tl, depth + 1, nkey))
        return nodes

    def retrace(self):
        """Path of canonical states from the initial state to the hit."""
        assert self.hit is not None
        keys = []
        k = self.hit[0]
        while k is not None:
            keys.append(k)
            k = self.visited[k]
        keys.reverse()
        return [gn.key_to_state(k) for k in keys], keys


def run_search(start_relators, targets, max_nodes=200_000, max_len=gn.L, tag="",
               ball=None, dump_visited_to=None):
    """`ball`: an extra frozen set of keys (e.g. the dumped visited set of a prior
    AK3/P25 run) — membership there also counts as a hit. `dump_visited_to`: write
    this run's visited keys (hex lines, gz) for later ball-intersection searches."""
    import gzip
    import time
    s = TargetSolver(start_relators, 2, max_nodes=max_nodes, max_len=max_len,
                     targets=targets)
    if ball:
        s.ball = ball
    t0 = time.time()
    nodes = s.solve()
    dt = time.time() - t0
    out = {"tag": tag, "nodes": nodes, "wall_s": round(dt, 2),
           "min_total_len": s.min_total_len, "hit": None}
    if s.hit:
        states, keys = s.retrace()
        out["hit"] = {"meta": s.hit[1], "path_len": len(states) - 1,
                      "path_states": [[[int(a) for a in r] for r in st] for st in states]}
    if dump_visited_to:
        os.makedirs(os.path.dirname(dump_visited_to), exist_ok=True)
        with gzip.open(dump_visited_to, "wt") as f:
            for k in s.visited:
                f.write(k.hex() + "\n")
        out["dumped_keys"] = len(s.visited)
    return out


def load_ball(path):
    """Load a dumped visited-key set (hex lines, gz)."""
    import gzip
    with gzip.open(path, "rt") as f:
        return frozenset(bytes.fromhex(line.strip()) for line in f if line.strip())


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", choices=["AK3", "P25"], default="AK3")
    ap.add_argument("--max_nodes", type=int, default=200_000)
    ap.add_argument("--max_len", type=int, default=gn.L)
    ap.add_argument("--leaves", default=os.path.join(ROOT, "results", "stable_ac",
                                                     "ak3_stable_proof", "catalog",
                                                     "catalog_leaves.jsonl"))
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    from hmoves import AK3, P25
    starts = {"AK3": AK3, "P25": P25}
    targets, n_skip = load_targets(args.leaves, max_len=args.max_len)
    print(f"targets: {len(targets)} keys ({n_skip} leaves skipped as over-cap)")
    res = run_search(list(starts[args.start]), targets, max_nodes=args.max_nodes,
                     max_len=args.max_len, tag=args.start)
    print(json.dumps({k: v for k, v in res.items() if k != "hit"} |
                     {"hit": None if res["hit"] is None else res["hit"]["meta"]}, indent=1))
    if args.out and res["hit"]:
        os.makedirs(os.path.dirname(args.out), exist_ok=True)
        with open(args.out, "a") as f:
            f.write(json.dumps(res) + "\n")
    return 0 if res["hit"] else 1


if __name__ == "__main__":
    sys.exit(main())
