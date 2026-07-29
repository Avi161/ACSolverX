"""Certified gamma_N = 1 *gateway* detection at any word length, by sampling.

The exact census decides gamma_N but costs prod (deg-1)! rotations, which is already
out of reach at total length 14.  Yet the one number the search needs -- "is this
member one genus unit from thickenable?" -- can be certified far more cheaply, because
each side of it comes from a different tool:

* the R1c-v2 solver has ALREADY certified every harvest member NOT_SPHERICAL, i.e.
  ``gamma_N >= 1`` (exhaustive over schemes x phases x seeds, not a sample);
* a single sampled compatible rotation with defect 2 is a WITNESS that
  ``gamma_N <= 1`` -- one explicit rotation system, verifiable in isolation.

Together: ``gamma_N = 1`` exactly, certified, with no census.  Sampling can only ever
under-report gateways (a member with no witness found may still be a gateway), so the
counts here are honest lower bounds; nothing is inferred from the absence of a witness.

Gateways matter because of the AUDITED ceiling (``R3PRIME_GRAFT_CALCULUS.md`` Thm G6):
a graft lowers gamma_N by at most 1, so a thickenable member can only ever be reached
from a gamma_N = 1 state.  Feeding the gateways found here into
``gateway_neighborhood.py`` searches exactly the region every capped harvest cuts.
"""

from __future__ import annotations

import argparse
import gzip
import json
import math
import os
import random
import sys
import time
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import neuwirth_rank_n as RN                                    # noqa: E402
from disconnected_split import support_class_and_E              # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
AK3_MEMBERS = os.path.join(REPO_ROOT, "results", "stable_ac", "fable",
                           "ak3_matched_members.jsonl.gz")
DEFAULT_OUT = os.path.join(REPO_ROOT, "results", "stable_ac", "fable",
                           "gateway_scan.json")

SAMPLES_PER_MEMBER = 3_000
MEMBERS_SAMPLED = 4_000
SEED = 20260729


def sampled_min_defect(words, samples: int, rng: random.Random,
                       local_search: bool = True, plateau_steps: int = 60):
    """(min defect found, witness rotation) over the compatible family.

    Uniform sampling alone is hopeless here: the minimising rotations are vanishingly
    rare (the length-13 gateway ("YYXXyx","YYxyXXX") has exactly 2 defect-2 systems out
    of 86,400 -- probability 2.3e-5).  So each draw seeds a hill-climb that swaps two
    darts in one positive germ's order and keeps the move when the defect does not
    increase, walking plateaus for a bounded number of steps.  The search is a
    heuristic; the WITNESS it returns is not -- it is one explicit rotation system whose
    defect is recomputed exactly by :func:`verify_witness`.

    The compatible family is a product over positive germs of the orderings of that
    germ's darts with one dart pinned as head (``compatible_orders_n``'s convention);
    permuting each tail explores it, and the negative germs stay forced by B-reversal.
    """
    generators = tuple(sorted(set("".join(words).lower())))
    data = RN.build_link_n(tuple(words), generators)
    B, A = data.B, data.A
    n_darts = data.n_darts
    nA = data.n_occurrences
    nC = len(data.present_germs)
    L = data.link_components
    positive = [2 * k for k in range(len(generators)) if data.vertex_darts[2 * k]]
    tails = [list(data.vertex_darts[g][1:]) for g in positive]
    heads = [data.vertex_darts[g][0] for g in positive]

    C = [0] * n_darts
    base = nA - nC + 2 * L

    def defect_of(state):
        for idx, germ in enumerate(positive):
            order = (heads[idx],) + tuple(state[idx])
            m = len(order)
            for k in range(m):
                C[order[k]] = order[(k + 1) % m]
            rev = tuple(B[d] for d in reversed(order))
            m = len(rev)
            for k in range(m):
                C[rev[k]] = rev[(k + 1) % m]
        seen = bytearray(n_darts)
        nAC = 0
        for start in range(n_darts):
            if seen[start]:
                continue
            nAC += 1
            cur = start
            while not seen[cur]:
                seen[cur] = 1
                cur = A[C[cur]]
        return base - nAC

    def orders_of(state):
        out = {}
        for idx, germ in enumerate(positive):
            order = (heads[idx],) + tuple(state[idx])
            out[int(germ)] = [int(d) for d in order]
            out[int(germ ^ 1)] = [int(B[d]) for d in reversed(order)]
        return out

    swappable = [idx for idx, tail in enumerate(tails) if len(tail) >= 2]
    best = None
    best_state = None
    budget = samples
    while budget > 0:
        state = [rng.sample(tail, len(tail)) for tail in tails]
        cur = defect_of(state)
        budget -= 1
        if best is None or cur < best:
            best, best_state = cur, [t[:] for t in state]
        if not local_search or not swappable:
            continue
        stale = 0
        while budget > 0 and stale < plateau_steps:
            idx = rng.choice(swappable)
            tail = state[idx]
            i, j = rng.randrange(len(tail)), rng.randrange(len(tail))
            if i == j:
                continue
            tail[i], tail[j] = tail[j], tail[i]
            trial = defect_of(state)
            budget -= 1
            if trial <= cur:                       # accept improvements and plateaus
                stale = 0 if trial < cur else stale + 1
                cur = trial
                if cur < best:
                    best, best_state = cur, [t[:] for t in state]
                    if best <= 0:
                        return best, orders_of(best_state)
            else:
                tail[i], tail[j] = tail[j], tail[i]
                stale += 1
    return best, (orders_of(best_state) if best_state is not None else None)


def verify_witness(words, orders: dict) -> int:
    """Recompute a witness rotation's defect independently of the sampler."""
    generators = tuple(sorted(set("".join(words).lower())))
    data = RN.build_link_n(tuple(words), generators)
    C = [0] * data.n_darts
    for _germ, seq in orders.items():
        m = len(seq)
        for k in range(m):
            C[seq[k]] = seq[(k + 1) % m]
    # compatibility: every negative germ cycle is the B-reversal of its positive one
    for k in range(len(generators)):
        pos, neg = 2 * k, 2 * k + 1
        if pos not in orders and str(pos) not in orders:
            continue
        p = orders.get(pos, orders.get(str(pos)))
        n = orders.get(neg, orders.get(str(neg)))
        if p is None or n is None:
            continue
        if tuple(n) != tuple(data.B[d] for d in reversed(p)):
            raise AssertionError("witness violates the B-reversal compatibility law")
    seen = bytearray(data.n_darts)
    nAC = 0
    for start in range(data.n_darts):
        if seen[start]:
            continue
        nAC += 1
        cur = start
        while not seen[cur]:
            seen[cur] = 1
            cur = data.A[C[cur]]
    return data.n_occurrences - len(data.present_germs) + 2 * data.link_components - nAC


def scan(members_path: str = AK3_MEMBERS, out_path: str = DEFAULT_OUT,
         members_sampled: int = MEMBERS_SAMPLED,
         samples_per_member: int = SAMPLES_PER_MEMBER, seed: int = SEED) -> dict:
    t0 = time.time()
    rows = []
    with (gzip.open(members_path, "rt", encoding="utf-8") if members_path.endswith(".gz")
          else open(members_path, encoding="utf-8")) as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            pair = row.get("canonical") or row.get("pair")
            if isinstance(pair, list) and len(pair) == 2:
                rows.append((tuple(pair), row.get("verdict")))
    rng = random.Random(seed)
    population = rows if len(rows) <= members_sampled else rng.sample(rows,
                                                                     members_sampled)
    print(f"[scan] {len(rows)} members, scanning {len(population)} "
          f"({samples_per_member} rotations each)", flush=True)

    gateways = []
    hat_hist: Counter = Counter()
    by_length: Counter = Counter()
    gateway_by_length: Counter = Counter()
    anomalies = []
    for i, (pair, verdict) in enumerate(population, 1):
        length = sum(len(w) for w in pair)
        by_length[length] += 1
        best, orders = sampled_min_defect(pair, samples_per_member, rng)
        hat = best // 2
        hat_hist[hat] += 1
        if best <= 0:
            # a sampled defect-0 rotation would CONTRADICT the solver's NOT_SPHERICAL
            anomalies.append({"pair": list(pair), "recorded_verdict": verdict,
                              "sampled_defect": best})
            continue
        if hat == 1:
            check = verify_witness(pair, orders)
            entry = {"pair": list(pair), "total_length": length,
                     "gamma_N": 1, "certificate": {
                         "upper_bound": "sampled compatible rotation with defect 2",
                         "lower_bound": f"solver verdict {verdict} => gamma_N >= 1",
                         "witness_defect_recomputed": check},
                     "witness_rotation": orders}
            if check != best:
                entry["WITNESS_RECHECK_MISMATCH"] = True
                anomalies.append(entry)
            else:
                gateways.append(entry)
                gateway_by_length[length] += 1
        if i % 250 == 0:
            print(f"[scan]   {i}/{len(population)} scanned, "
                  f"{len(gateways)} gateways", flush=True)

    report = {
        "record": "gateway_scan",
        "source": os.path.relpath(members_path, REPO_ROOT),
        "members_total": len(rows),
        "members_scanned": len(population),
        "samples_per_member": samples_per_member,
        "seed": seed,
        "gamma_hat_histogram": {str(k): v for k, v in sorted(hat_hist.items())},
        "gateways_found": len(gateways),
        "gateway_by_length": {str(k): v for k, v in sorted(gateway_by_length.items())},
        "scanned_by_length": {str(k): v for k, v in sorted(by_length.items())},
        "anomalies": anomalies,
        "note": ("gamma_hat is an UPPER bound from sampling; gamma_hat = 1 combined "
                 "with the solver's certified NOT_SPHERICAL pins gamma_N = 1 exactly. "
                 "Absence of a witness proves nothing -- gateway counts are lower "
                 "bounds."),
        "elapsed_seconds": round(time.time() - t0, 1),
    }
    payload = {"summary": report, "gateways": gateways}
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=1)
    print(f"[scan] wrote {out_path}", flush=True)
    print(f"[scan] gateways found: {len(gateways)}  "
          f"gamma_hat hist: {report['gamma_hat_histogram']}", flush=True)
    if anomalies:
        print(f"[scan] ANOMALIES: {len(anomalies)} (see report)", flush=True)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default=DEFAULT_OUT)
    parser.add_argument("--members", default=AK3_MEMBERS)
    parser.add_argument("--members-sampled", type=int, default=MEMBERS_SAMPLED)
    parser.add_argument("--samples-per-member", type=int, default=SAMPLES_PER_MEMBER)
    args = parser.parse_args(argv)
    scan(args.members, args.out, args.members_sampled, args.samples_per_member)


if __name__ == "__main__":
    main()
