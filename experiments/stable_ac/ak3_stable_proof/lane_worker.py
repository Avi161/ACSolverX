"""Importable multiprocessing workers for the Colab lane notebooks (pickle-safe under
fork AND spawn — same pattern as calibrate_probe.py). Each worker takes one plain
tuple task and returns one JSONL-ready dict including its own peak RSS.

Task shapes:
  ("mitm_out",  start_name, budget, max_len, leaves_path, dump_path|None)
  ("mitm_leaf", leaf_key, budget, max_len, leaves_path, ball_path|None)
  ("laneB",     start_name, budget, max_len, max_gen, bank_name, gen_penalty)
  ("laneC",     form, n_gen_total, budget)
"""
import json
import os
import resource
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ONEGEN = os.path.join(ROOT, "experiments", "stable_ac", "one_generator")
for p in (HERE, ONEGEN):
    if p not in sys.path:
        sys.path.insert(0, p)


def _peak_rss_mb():
    ru = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return round(ru / (1024 * 1024 if sys.platform == "darwin" else 1024), 1)


def _starts():
    from hmoves import AK3, P25
    from wirtinger import eliminate_final_via_w, paper_family
    starts = {"AK3": ([list(r) for r in AK3], 2),
              "P25": ([list(r) for r in P25], 2)}
    c = paper_family()
    starts["M3corr"] = ([list(r) for r in c._state()], 3)
    eliminate_final_via_w(c)
    starts["P25corr"] = ([list(r) for r in c._state()], 2)
    return starts


def _banks():
    hero = [[1, 2, 1], [2, 1, 2], [1, 1, 1], [2, 2, 2, 2],
            [-1, 2, 1, 2], [-2, 1, 2, -1], [1], [2]]
    banks = {"hero8": hero, "none": []}
    import ak3_words
    banks["full"] = [w["w_ints"] for w in ak3_words.build_word_bank()]
    return banks


def probe(task):
    kind = task[0]
    try:
        if kind == "mitm_out":
            _, start_name, budget, max_len, leaves_path, dump_path = task
            from mitm import load_targets, run_search
            starts = _starts()
            targets, n_skip = load_targets(leaves_path, max_len=max_len)
            rels, ng = starts[start_name]
            res = run_search(rels, targets, max_nodes=budget, max_len=max_len,
                             tag=start_name, dump_visited_to=dump_path)
            rec = {"kind": kind, "id": f"{start_name}@{budget}", "targets": len(targets),
                   **{k: res[k] for k in ("nodes", "wall_s", "min_total_len")},
                   "hit": res["hit"] and res["hit"]["meta"],
                   "hit_detail": res["hit"], "dumped": res.get("dumped_keys")}
        elif kind == "mitm_leaf":
            _, leaf_key, budget, max_len, leaves_path, ball_path = task
            from hmoves import AK3, P25
            from mitm import load_ball, load_targets, run_search
            rec_leaf = None
            with open(leaves_path) as f:
                for line in f:
                    r = json.loads(line)
                    if r["key"] == leaf_key:
                        rec_leaf = r
                        break
            targets, _ = load_targets(None, include={"AK3": AK3, "P25": P25})
            ball = load_ball(ball_path) if ball_path and os.path.exists(ball_path) else None
            res = run_search(rec_leaf["relators"], targets, max_nodes=budget,
                             max_len=max_len, tag=f"leaf:{leaf_key[:16]}", ball=ball)
            rec = {"kind": kind, "id": f"{leaf_key}@{budget}",
                   "leaf_total_len": rec_leaf["total_len"], "ball": bool(ball),
                   **{k: res[k] for k in ("nodes", "wall_s", "min_total_len")},
                   "hit": res["hit"] and res["hit"]["meta"], "hit_detail": res["hit"]}
        elif kind == "laneB":
            _, start_name, budget, max_len, max_gen, bank_name, gen_penalty = task
            from stable_solver import solve_one
            starts = _starts()
            rels, ng = starts[start_name]
            cert_path = os.path.join(ROOT, "results", "stable_ac", "ak3_stable_proof",
                                     "certs", f"laneB_{start_name}_{bank_name}_{budget}.json")
            rec = solve_one(rels, ng, bank=_banks()[bank_name], max_gen=max_gen,
                            max_nodes=budget, max_len=max_len, gen_penalty=gen_penalty,
                            name=f"{start_name}_{bank_name}", emit_cert_path=cert_path)
            rec = {"kind": kind, "id": f"{start_name}_{bank_name}_g{max_gen}@{budget}", **rec}
        elif kind == "laneC":
            _, form, n_total, budget = task
            import numpy as np
            import greedy_nrel as gn
            # bump the byte tables for n_gen > 3 (order property of the formula holds)
            if n_total > gn.NGEN_MAX:
                gn.NGEN_MAX = n_total
                gn._INT_TO_RANK_BYTE = {
                    v: (gn.NGEN_MAX - abs(v)) * 2 + (1 if v > 0 else 0) + 1
                    for g in range(1, gn.NGEN_MAX + 1) for v in (-g, g)}
                gn._RANK_BYTE_TO_INT = {b: v for v, b in gn._INT_TO_RANK_BYTE.items()}
            FORMS = {"textbook": ([1, 2, 1, -2, -1, -2], [1, 1, 1, -2, -2, -2, -2]),
                     "rep": ([-2, -1, 2, -1, -2, 1], [-2, -2, -2, -1, -1, -1, -1])}
            r1, r2 = FORMS[form]
            rels = [np.array(r1, dtype=gn.INT_DTYPE), np.array(r2, dtype=gn.INT_DTYPE)]
            for g in range(3, n_total + 1):
                rels.append(np.array([g], dtype=gn.INT_DTYPE))
            import time
            solver = gn.NRelatorSolver(rels, n_total, max_nodes=budget, max_len=gn.L)
            t0 = time.time()
            path, nodes, _ = solver.solve()
            rec = {"kind": kind, "id": f"{form}_n{n_total}@{budget}",
                   "solved": path is not None, "nodes": int(nodes),
                   "min_total_len": int(solver.min_total_len),
                   "wall_s": round(time.time() - t0, 1)}
            if path is not None:
                rec["path_verified"] = bool(gn.verify_path(path["states"], n_total))
                rec["path_len"] = len(path["states"]) - 1
        else:
            rec = {"kind": kind, "id": "?", "error": f"unknown task kind {kind}"}
    except Exception as e:
        import traceback
        rec = {"kind": kind, "id": str(task[1:3]), "error": repr(e),
               "traceback": traceback.format_exc()[-2000:]}
    rec["peak_rss_mb"] = _peak_rss_mb()
    return rec
