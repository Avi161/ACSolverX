"""Check that cov_gates_cpu.py is Ryan's algorithm: compare with the JAX original, child by child and search by search.

Needs Ryan's repo (default /home/user/ryanzang04/Stable-ACSolver) and jax 0.6.0 importable (JAX is used only here).

  JAX_PLATFORMS=cpu python benchmark/ryan/check_port.py --children 300 --searches 0:12 --nodes 3000
"""
from __future__ import annotations

import argparse
import ast
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import cov_gates_cpu as C  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ryan", default="/home/user/ryanzang04/Stable-ACSolver")
    ap.add_argument("--input", default=str(ROOT / "data/ms640_solved.txt"))
    ap.add_argument("--children", type=int, default=300, help="random popped states whose children are compared")
    ap.add_argument("--searches", default="0:12", help="row range for whole-search comparison, all six gates")
    ap.add_argument("--nodes", type=int, default=3000)
    a = ap.parse_args()
    sys.path.insert(0, a.ryan)
    sys.path.insert(0, a.ryan + "/scripts")
    import greedy_search_n as g
    import ms640_cov_gates as R

    params = g.MoveParams(n_gen=2, max_n_gen=2, max_length=24, max_steps_in_episode=10**6)
    apply_batch = g.build_apply_batch(params, True, False)
    lines = [l for l in Path(a.input).read_text().splitlines() if l.strip()]

    # 1. children: collect popped states from short CPU searches over many rows, compare every child
    rng = random.Random(0)
    pool = []
    for idx in rng.sample(range(len(lines)), 120):
        key = C.start_key_from_row(ast.literal_eval(lines[idx]))
        res_states = []
        parents = {key: None}
        frontier = [key]
        for _ in range(40):  # a few BFS-ish steps to get varied states
            if not frontier:
                break
            k = frontier.pop(rng.randrange(len(frontier)))
            res_states.append(k)
            for act in C.substitution_actions(k) + C.cov_actions(k):
                n = C.apply(k, act)
                if n is not None and n not in parents and C.total_length(n) <= 48:
                    parents[n] = k
                    frontier.append(n)
        pool += res_states
    states = rng.sample(pool, min(a.children, len(pool)))
    n_child = mism = 0
    for key in states:
        flat = g.key_to_flat(key, 2, 24)
        actions = C.substitution_actions(key) + C.cov_actions(key)
        assert [tuple(x) for x in g.iter_substitution_actions(key, 2)] == C.substitution_actions(key)
        assert [tuple(x) for x in g.iter_change_of_variables_actions(key, 2, 1, None, 1)] == C.cov_actions(key)
        for action, nf, nn in g.apply_actions_chunked(apply_batch, flat, 2, actions, 256):
            jk, _ = g.canonicalize_flat(nf, nn, 2, 24)
            mine = C.apply(key, tuple(action))
            mine = key if mine is None else mine
            n_child += 1
            if jk != mine:
                mism += 1
                if mism <= 5:
                    print("MISMATCH", key, action, jk, mine)
    print(f"children: {len(states)} states, {n_child} children, mismatches {mism}")

    # 2. whole searches: Ryan's search() against ours, every gate
    s, e = map(int, a.searches.split(":"))

    class Args:
        max_nodes = a.nodes
        chunk_size = 256
        progress_seconds = 1e9

    bad = 0
    total = 0
    for idx in range(s, e):
        raw = ast.literal_eval(lines[idx])
        flat, _, _ = g.normalize_dataset_flat(raw, 2, 2, 24)
        key = C.start_key_from_row(raw)
        for gate in C.GATES:
            r = R.search(flat, gate, Args, apply_batch)
            m = C.search(key, gate, a.nodes, 1e9)
            fields = ["solved", "termination", "nodes_visited", "states_seen", "path_length", "gate_openings",
                      "cov_actions_enumerated", "cov_changed_in_cap_actions", "cov_shortening_actions",
                      "best_popped_length"]
            diff = {f: (r[f], m[f]) for f in fields if r[f] != m[f]}
            same_path = [p["relators"] for p in r["path"]] == [p["relators"] for p in m["path"]]
            total += 1
            if diff or not same_path:
                bad += 1
                print("SEARCH DIFF", idx, gate, diff, "path same:", same_path)
    print(f"searches: {total} (rows {s}:{e} x 6 gates, {a.nodes} nodes), differing {bad}")


if __name__ == "__main__":
    main()
