"""Calibration probe worker (Phase 2.5) — kept in an importable module so ``multiprocessing`` can
pickle it under BOTH fork (Colab/Linux) and spawn (macOS default), and so it is unit-testable.
``calibrate.ipynb`` imports ``probe`` and maps it over a task list across ``PROBE_WORKERS`` cores.

A task is the tuple ``(kind, dataset, idx, arm, budget, flat, n_gen, max_len, use_block)``. Each worker
runs one presentation to ``budget`` nodes and returns a fully-formed JSONL record including this
worker's peak RSS (so the notebook can size RAM-bounded parallelism).

``n_gen`` selects the arm type: ``3`` = a ``z=w`` stabilized arm (``flat`` is stabilized via
``stabilize_flat(flat, arm)`` and the null-revert block applies); ``2`` = the plain 2-gen GS-Sub
baseline (``flat`` used as-is, no stabilization, no block, ``arm`` is a free label e.g. ``"baseline"``).
Both emit the identical record schema, so ``run_baseline_greedy.py`` (n=2) and ``calibrate.ipynb`` (n=3)
produce streams the website viewer can merge/compare directly."""
import platform
import resource

import greedy_nrel as gn
import stabilize as stab


def peak_rss_mb():
    rr = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return rr / 1024.0 if platform.system() == "Linux" else rr / (1024.0 * 1024.0)  # Linux KB, macOS bytes


def probe(task):
    kind, dataset, idx, arm, budget, flat, n_gen, max_len, use_block = task
    if n_gen == 2:                                            # 2-gen GS-Sub baseline: no z, no null-revert block
        sflat = list(flat)
        blocked = None
        path_name = f"{dataset}:idx{idx}:baseline"
    else:                                                     # z=w stabilized arm (n=2 -> n=3)
        sflat = stab.stabilize_flat(flat, arm)
        blocked = [gn.null_revert_state(sflat, n_gen)] if use_block else None
        path_name = f"{dataset}:idx{idx}:z={arm}"
    res, path = gn.solve_one(sflat, n_gen=n_gen, max_len=max_len, max_nodes=budget, blocked_states=blocked)
    nps = res["nodes_explored"] / res["wall_time_s"] if res["wall_time_s"] > 0 else 0
    rec = {"kind": kind, "dataset": dataset, "idx": idx, "arm": arm, "n_gen": n_gen,
           "budget_nodes": budget, "nodes_explored": res["nodes_explored"], "solved": res["solved"],
           "path_verified": res["path_verified"], "path_len": res["path_len"],
           "revert_hits": res["revert_hits"], "wall_time_s": res["wall_time_s"],
           "nodes_per_sec": round(nps), "peak_rss_mb": round(peak_rss_mb(), 1),
           "exhausted_budget": (not res["solved"])}
    if res["solved"] and path is not None:                    # persist the exact move+state path (n>=3 rule)
        prec = gn.serialize_path(path, idx, name=path_name)
        prec.update({"kind": kind, "dataset": dataset, "arm": arm, "n_gen": n_gen,
                     "budget_nodes": budget, "path_verified": res["path_verified"]})
        rec["path_record"] = prec                              # main process writes this to paths.jsonl
    return rec
