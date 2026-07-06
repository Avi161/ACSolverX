"""AK(3) word-choice probe worker — importable (pickles under fork AND spawn; macOS default is
spawn, see the Lessons-Learned "worker must live in an importable module" trap).

A task is ``(form, dataset, word_name, family, w_ints, base_flat, budget, max_len)``. The worker
stabilizes ``base_flat`` (a 2-gen AK(3) form) with the explicit word ``w_ints`` to a 3-gen
``z=w`` presentation, runs the greedy solver to ``budget`` nodes with the null-revert block, and
returns a fully-formed JSONL record (same core schema as ``calibrate_probe.probe`` plus the
word-choice fields ``form/word_name/family/w_ints/w_str/z_relator/min_total_len``). On a solve it
attaches ``rec["path_record"]`` for the main process to write to the paths sidecar."""
import platform
import resource

import greedy_nrel as gn
import ak3_words as aw


def peak_rss_mb():
    rr = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return rr / 1024.0 if platform.system() == "Linux" else rr / (1024.0 * 1024.0)  # Linux KB, macOS bytes


def probe(task):
    form, dataset, word_name, family, w_ints, base_flat, budget, max_len = task
    sflat = aw.stabilize_with_word(base_flat, w_ints)
    blocked = [gn.null_revert_state(sflat, 3)]
    res, path = gn.solve_one(sflat, n_gen=3, max_len=max_len, max_nodes=budget,
                             blocked_states=blocked)
    nps = res["nodes_explored"] / res["wall_time_s"] if res["wall_time_s"] > 0 else 0
    rec = {"kind": "ak3_wormhole", "form": form, "dataset": dataset,
           "word_name": word_name, "family": family,
           "w_ints": list(w_ints), "w_str": aw.to_str(w_ints),
           "z_relator": list(aw.z_relator_for(w_ints)),
           "n_gen": 3, "budget_nodes": budget,
           "nodes_explored": res["nodes_explored"], "solved": res["solved"],
           "path_verified": res["path_verified"], "path_len": res["path_len"],
           "max_len_along_path": res["max_len_along_path"],
           "min_total_len": res["min_total_len"], "revert_hits": res["revert_hits"],
           "wall_time_s": res["wall_time_s"], "nodes_per_sec": round(nps),
           "peak_rss_mb": round(peak_rss_mb(), 1),
           "exhausted_budget": (not res["solved"])}
    if res["solved"] and path is not None:
        prec = gn.serialize_path(path, idx=word_name, name=f"AK3_{form}:z={word_name}")
        prec.update({"kind": "ak3_wormhole", "form": form, "dataset": dataset,
                     "word_name": word_name, "family": family, "w_str": aw.to_str(w_ints),
                     "n_gen": 3, "budget_nodes": budget, "path_verified": res["path_verified"]})
        rec["path_record"] = prec
    return rec
