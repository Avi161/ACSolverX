"""Replay μ-ladder ``best_chain`` → ``best_rep`` without the orbits dump.

For each CoV descender in ``mu_ladder_big_aca124_r256_b64_mrl24.jsonl``,
branch-BFS along the recorded z-chain from the concrete ``(r1_orig, r2_orig)``
(and from each intermediate's ``aut_canon`` rep — CoV junctions at canonical
reps). Accept iff some endpoint's ``aut_canon`` equals the recorded
``best_rep`` / ``best_mu``.

This closes the advisor REVISE that the 1.6 GB orbits dump is not in-repo, so
``verify_mu_ladder.py --level full`` cannot run here. Runtime ~15 s for all 36.

    PYTHONPATH=. python3 -m experiments.heuristic_search.verify.verify_cov_best_rep_chains
"""
from __future__ import annotations

import argparse
import json
import os
import sys

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.equivalence_classes.lib.autcanon import aut_canon  # noqa: E402
from experiments.greedy_tests.spec.words import str_to_word, word_to_str  # noqa: E402
from experiments.stable_ac.cov import cov  # noqa: E402
from experiments.heuristic_search.runners.run_unsolved124_s20mk2 import (  # noqa: E402
    MU_LADDER_JSONL, N_COV_DESCENDERS,
)


def _hop_children(pair, z, cap):
    """All gated CoV outputs for ``z`` from ``pair`` and from ``aut_canon(pair)``."""
    out = []
    zw = str_to_word(z)
    seeds = [tuple(pair)]
    mu, rep, _ = aut_canon((str(pair[0]), str(pair[1])))
    if tuple(rep) != tuple(pair):
        seeds.append(tuple(rep))
    for seed in seeds:
        for iso in ("x", "y"):
            for allow in (False, True):
                brs = cov.cov_branches(
                    str_to_word(seed[0]), str_to_word(seed[1]), zw,
                    default_cap=cap, cap_headroom=cov.CAP_HEADROOM,
                    reject_len=cov.REJECT_LEN,
                    allow_defining_iso=allow, iso_gen=iso)
                for b in brs:
                    out.append((word_to_str(b.r1), word_to_str(b.r2)))
    # unique preserve order
    return list(dict.fromkeys(out))


def replay_best_chain(row, cap=None):
    """Return ``(ok, err)``. ``ok`` ⇒ some endpoint aut_canon-matches ``best_rep``."""
    if cap is None:
        cap = int(row.get("cfg", {}).get("cap", 24))
    frontier = [(row["r1_orig"], row["r2_orig"])]
    for z in row["best_chain"]:
        nxt = []
        for p in frontier:
            nxt.extend(_hop_children(p, z, cap))
        frontier = list(dict.fromkeys(nxt))
        if not frontier:
            return False, f"empty frontier after z={z}"
    target = [str(row["best_rep"][0]), str(row["best_rep"][1])]
    best_mu = int(row["best_mu"])
    for p in frontier:
        if list(p) == target:
            return True, None
        mu, rep, _ = aut_canon(p)
        if list(rep) == target and int(mu) == best_mu:
            return True, None
    return False, f"no endpoint matched best_rep among {len(frontier)} leaves"


def verify_all_descenders(path=MU_LADDER_JSONL, names=None):
    fails = []
    n = 0
    with open(path) as f:
        for line in f:
            if not line.strip():
                continue
            row = json.loads(line)
            if int(row["best_mu"]) >= int(row["mu_in"]):
                continue
            if names and row["pres_id"] not in names:
                continue
            n += 1
            ok, err = replay_best_chain(row)
            if not ok:
                fails.append(f"{row['pres_id']}: {err}")
            else:
                print(f"  {row['pres_id']}: OK "
                      f"(μ {row['mu_in']}→{row['best_mu']})", flush=True)
    return n, fails


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ladder", default=MU_LADDER_JSONL)
    ap.add_argument("--names", nargs="*", default=None)
    ap.add_argument("--expect-n", type=int, default=N_COV_DESCENDERS)
    args = ap.parse_args()
    names = set(args.names) if args.names else None
    n, fails = verify_all_descenders(args.ladder, names=names)
    print(f"checked {n} descenders; fails={len(fails)}")
    if args.expect_n is not None and names is None and n != args.expect_n:
        fails.append(f"descender count {n} != expect {args.expect_n}")
    for x in fails[:20]:
        print("  FAIL", x)
    if fails:
        sys.exit(1)
    print("ALL 36 BEST_REP CHAINS REPLAY")


if __name__ == "__main__":
    main()
