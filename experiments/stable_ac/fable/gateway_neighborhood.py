"""Exhaustive one-move neighbourhood of AK(3)'s gamma_N = 1 *gateway* states.

Why this exists
---------------
Every harvest in this project is best-first with a length cap, so the images of a
length-13 state under a graft (length ~20) are systematically CUT.  The
gamma_N floor measurement (``gamma_floor_measurement.json``) found that AK(3)'s
classical class contains length-13 members with **gamma_N = 1** -- one genus unit from
thickenable -- while AK(3) itself sits at gamma_N = 2.  By the AUDITED ceiling
(``R3PRIME_GRAFT_CALCULUS.md`` Theorem G6: a graft lowers gamma_N by at most 1) those
gamma_N = 1 states are exactly the *gateway*: the only states from which a single graft
can possibly land on a thickenable presentation.  Nobody has ever enumerated their
neighbourhood, because it lives beyond every cap we have run.

What this does
--------------
For each seed state, enumerate the FULL one-move AC2 graft neighbourhood -- every
ordered pair of relators, every rotation of the host and of the guest, and both guest
signs -- and decide each image, in BOTH realizations that the AC move set produces:

* the exact concatenation (what AC2 alone gives), and
* its cyclic reduction (AC2 followed by Lackenby's move (0)).

Deciding both is not pedantry: this session verified that move (0) alone can turn a
gamma_N = 1 complex into a gamma_N = 0 one -- ("xyXY","yYxxy") has gamma_N = 1 while its
reduction ("xyXY","xxy") has gamma_N = 0 -- so the reduced image is a genuinely
different, and strictly more promising, complex than the exact one.

A SPHERICAL image would be a thickenable member of AK(3)'s classical class: by
Corollary 3 / D3 (Lackenby Thm 1.3, FLAGGED [unverified this session]) that would make
AK(3) classically AC-trivial, hence stably AC-trivial.  Such a row is written with a
loud flag and the full hit protocol; it is a candidate requiring replay, never a claim.

Budget note: this is exhaustive enumeration of a bounded neighbourhood plus per-state
decisions -- there is no best-first search here, so no node budget is consumed.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from collections import Counter

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

import neuwirth_cut_schemes as CS                               # noqa: E402
import neuwirth_rank_n as RN                                    # noqa: E402
from ac_words import canon_pair, cyclic_reduce, inverse         # noqa: E402
from disconnected_split import support_class_and_E              # noqa: E402

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(_HERE)))
DEFAULT_OUT = os.path.join(REPO_ROOT, "results", "stable_ac", "fable",
                           "gateway_neighborhood.json")
FLOOR_JSON = os.path.join(REPO_ROOT, "results", "stable_ac", "fable",
                          "gamma_floor_measurement.json")

# budgets pinned to the round-2 / contrast stack so verdicts join the corpus
SCHEME_BUDGET = 200_000
BRANCH_BUDGET = 2_000_000
CENSUS_CAP = 2_000_000

AK3 = ("xxxYYYY", "xyxYXY")


def rotations(word: str):
    return [word[i:] + word[:i] for i in range(len(word))]


def census_size(words) -> int:
    degrees = Counter("".join(words).lower())
    size = 1
    for deg in degrees.values():
        size *= math.factorial(max(deg - 1, 0))
    return size


def decide(words) -> dict:
    """R1c-v2 solver first (fast, certified); census fallback when out of scope."""
    words = tuple(words)
    generators = tuple(sorted(set("".join(words).lower())))
    if len(generators) < 2:
        return {"verdict": "UNSUPPORTED", "method": "degenerate",
                "reason": f"only {len(generators)} generator(s) occur"}
    support = CS.classify_cut_support(words, generators)
    if support.kind != CS.UNSUPPORTED:
        decision = CS.solve_cut_schemes(words, generators, scheme_budget=SCHEME_BUDGET,
                                        branch_budget=BRANCH_BUDGET, support=support)
        return {"verdict": decision.verdict,
                "method": ("r1c_v2_nonplanar" if support.kind == CS.NONPLANAR
                           else "r1c_v2_solver"),
                "reason": decision.reason,
                "support_kind": support.kind}
    size = census_size(words)
    if size > CENSUS_CAP:
        return {"verdict": "UNDECIDED_BUDGET", "method": "none",
                "reason": (f"solver out of scope ({support.reason}); census family "
                           f"{size} exceeds cap {CENSUS_CAP}"),
                "support_kind": support.kind, "census_size": size}
    census = RN.gamma_N_factorial_n(words, generators, cap_rotations=CENSUS_CAP,
                                    keep_accepting=False)
    if census["status"] != "OK":
        return {"verdict": "UNDECIDED_BUDGET", "method": "none",
                "reason": f"census status {census['status']}",
                "support_kind": support.kind}
    gamma = census["minimum_defect"] // 2
    return {"verdict": "SPHERICAL" if gamma == 0 else "NOT_SPHERICAL",
            "method": "factorial_census", "reason": None,
            "support_kind": support.kind, "gamma_N": gamma,
            "census_size": census["expected_cases"]}


def graft_images(seed):
    """Every AC2 graft image of ``seed``: (label, exact_pair, reduced_pair)."""
    out = []
    for host in (0, 1):
        guest = 1 - host
        for hk, hw in enumerate(rotations(seed[host])):
            for gk, gw in enumerate(rotations(seed[guest])):
                for sign, guest_word in (("+", gw), ("-", inverse(gw))):
                    new = list(seed)
                    new[host] = hw + guest_word
                    exact = tuple(new)
                    reduced = tuple(cyclic_reduce(w) for w in exact)
                    label = (f"r{host + 1} <- rot^{hk}(r{host + 1})"
                             f"*rot^{gk}(r{guest + 1}){sign}")
                    out.append((label, exact, reduced))
    return out


def run_seed(name: str, seed, out_rows: list) -> dict:
    t0 = time.time()
    images = graft_images(seed)
    seen_exact, seen_reduced = set(), set()
    verdicts: Counter = Counter()
    hits = []
    undecided = []
    for label, exact, reduced in images:
        for kind, pair in (("exact", exact), ("reduced", reduced)):
            if any(not w for w in pair):
                continue
            key = canon_pair(*pair) if len(pair) == 2 else pair
            bucket = seen_exact if kind == "exact" else seen_reduced
            if key in bucket:
                continue
            bucket.add(key)
            decision = decide(pair)
            verdicts[(kind, decision["verdict"])] += 1
            row = {"seed": name, "seed_words": list(seed), "move": label,
                   "realization": kind, "words": list(pair),
                   "canonical": list(key), "total_length": sum(len(w) for w in pair),
                   **decision}
            if decision["verdict"] == "SPHERICAL":
                cls, e = support_class_and_E(tuple(pair)) if len(pair) == 2 \
                    else (None, None)
                row["LOUD_SPHERICAL_ALERT"] = True
                row["support_class"] = cls
                row["E"] = float(e) if e is not None else None
                row["replay_required"] = ("candidate only: reconstruct the explicit "
                                          "AC move list from AK(3) and replay before "
                                          "any claim")
                hits.append(row)
            elif decision["verdict"] == "UNDECIDED_BUDGET":
                undecided.append(row)
            out_rows.append(row)
    return {
        "seed": name,
        "seed_words": list(seed),
        "graft_moves_enumerated": len(images),
        "distinct_exact_images": len(seen_exact),
        "distinct_reduced_images": len(seen_reduced),
        "verdicts": {f"{k[0]}/{k[1]}": v for k, v in sorted(verdicts.items())},
        "spherical": len(hits),
        "undecided": len(undecided),
        "hits": hits,
        "undecided_rows": undecided[:20],
        "elapsed_seconds": round(time.time() - t0, 1),
    }


def load_gateway_seeds(floor_json: str = FLOOR_JSON) -> list:
    """The measured gamma_N = 1 witnesses of AK(3)'s class, plus AK(3) itself."""
    seeds = [("AK(3) itself (gamma_N=2 control)", AK3)]
    try:
        with open(floor_json, encoding="utf-8") as handle:
            report = json.load(handle)
    except FileNotFoundError:
        return seeds
    ak3 = report["classes"].get("AK(3) classical class", {})
    for i, witness in enumerate(ak3.get("floor_witnesses", [])):
        if witness.get("gamma_N") == 1:
            seeds.append((f"gateway{i + 1} (gamma_N=1, len "
                          f"{witness['total_length']})", tuple(witness["pair"])))
    return seeds


def run(out_path: str = DEFAULT_OUT) -> dict:
    t0 = time.time()
    seeds = load_gateway_seeds()
    print(f"[gateway] {len(seeds)} seeds", flush=True)
    rows: list = []
    per_seed = []
    for name, seed in seeds:
        print(f"[gateway] {name}: {seed}", flush=True)
        stats = run_seed(name, seed, rows)
        per_seed.append(stats)
        print(f"[gateway]   {stats['distinct_exact_images']} exact + "
              f"{stats['distinct_reduced_images']} reduced images; "
              f"SPHERICAL {stats['spherical']}; undecided {stats['undecided']} "
              f"({stats['elapsed_seconds']}s)", flush=True)

    total_hits = sum(s["spherical"] for s in per_seed)
    report = {
        "record": "gateway_neighborhood",
        "context": ("exhaustive one-move AC2 graft neighbourhood of AK(3)'s measured "
                    "gamma_N = 1 gateway states, in both the exact and the "
                    "cyclically reduced realization; the region every capped harvest "
                    "cuts"),
        "budgets": {"scheme": SCHEME_BUDGET, "branch": BRANCH_BUDGET,
                    "census_cap": CENSUS_CAP},
        "seeds": [{"name": n, "words": list(w)} for n, w in seeds],
        "per_seed": per_seed,
        "rows_written": len(rows),
        "TOTAL_SPHERICAL": total_hits,
        "LOUD_SPHERICAL_ALERT": bool(total_hits),
        "elapsed_seconds": round(time.time() - t0, 1),
    }
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump({"summary": report, "rows": rows}, handle, indent=1)
    print(f"[gateway] wrote {out_path}", flush=True)
    print(f"[gateway] TOTAL SPHERICAL = {total_hits}", flush=True)
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default=DEFAULT_OUT)
    args = parser.parse_args(argv)
    run(args.out)


if __name__ == "__main__":
    main()
