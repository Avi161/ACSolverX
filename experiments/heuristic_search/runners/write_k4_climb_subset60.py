"""Regenerate K=4 nonsym-beam climb jsonl with full hop provenance.

Committed writer for ``covbeam_nonsym_beam_k4_climb_subset60.jsonl``
(ac-advisor must-address #5). Carries ``best_chain_hops`` so
``verify_nonsym_chains`` can replay. Uses the same knobs as the K-sweep
winner: beam_k=4, rungs=32, max_aut_canon=1000, stop_mu=12.

``stopped_reason == "closed"`` is rewritten to ``beam_no_new_orbits`` in
the output (not μ-ball closure).

    PYTHONPATH=. python3 -m experiments.heuristic_search.runners.write_k4_climb_subset60
"""
from __future__ import annotations

import json
import os
import sys
import time

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.heuristic_search.runners.run_bench60_covbeam_b1k import (  # noqa: E402
    search_cap, ORIG_CAP,
)
from experiments.heuristic_search.runners.run_sweep import (  # noqa: E402
    load, subset_ids,
)
from experiments.stable_ac.cov.ladder.autcanon_fast import warm  # noqa: E402
from experiments.stable_ac.cov.ladder.mu_ladder_nonsym_beam import (  # noqa: E402
    climb_beam,
)

ROOT = _d
OUT = os.path.join(
    ROOT, "results", "comparison", "covbeam_nonsym_beam_k4_climb_subset60.jsonl")
BEAM_K = 4
RUNGS = 32
MAX_AUT = 1000
STOP_MU = 12


def main():
    warm()
    rows = load(subset_ids(60))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    t0 = time.perf_counter()
    with open(OUT, "w") as f:
        for i, (pres_id, r1, r2) in enumerate(rows):
            climb = climb_beam(
                r1, r2, beam_k=BEAM_K, rungs=RUNGS, cap=ORIG_CAP,
                stop_mu=STOP_MU, max_aut_canon=MAX_AUT)
            reason = climb["stopped_reason"]
            if reason == "closed":
                reason = "beam_no_new_orbits"
            br = climb["best_rep"]
            row = {
                "pres_id": str(pres_id),
                "r1": r1, "r2": r2,
                "mu_in": climb["mu_in"],
                "best_mu": climb["best_mu"],
                "hits_stop": climb["hits_stop"],
                "descended": climb["descended"],
                "best_rep": br,
                "best_chain": climb["best_chain"],
                "best_nsubs": climb["best_nsubs"],
                "best_chain_hops": climb["best_chain_hops"],
                "n_orbits_seen": climb["n_orbits_seen"],
                "stopped_reason": reason,
                "n_aut_canon": climb["cost"]["n_aut_canon"],
                "n_expanded": climb["cost"]["n_expanded"],
                "n_rungs": climb["cost"]["n_rungs"],
                "treat_cap": search_cap(br[0], br[1]),
                "beam_k": BEAM_K,
                "rungs_cap": RUNGS,
                "max_aut_canon": MAX_AUT,
                "stop_mu": STOP_MU,
                "writer": "write_k4_climb_subset60",
            }
            f.write(json.dumps(row) + "\n")
            print(
                f"  [{i+1:02d}/60] ms{pres_id}: μ {climb['mu_in']}→"
                f"{climb['best_mu']} hit={climb['hits_stop']} "
                f"reason={reason} n_ac={climb['cost']['n_aut_canon']}",
                flush=True)
    print(f"wrote {OUT} in {time.perf_counter()-t0:.1f}s")


if __name__ == "__main__":
    main()
