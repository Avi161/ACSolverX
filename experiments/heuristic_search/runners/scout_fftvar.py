"""Scout: which spectral transform, if any, belongs in the heap — ``L + 4 * F_i``.

The shipped Fourier work fixed one transform (exponent-sign channel, autocorrelation lags 3..5)
and swept only its weight. This sweeps the *transform* at a fixed weight instead: every arm is
``L + 4 * F_i`` for one variant of ``fftvar_feats``, against the ``length`` control, so the
comparison is between spectral functionals rather than between scales. Every variant is
normalised to a per-relator [0, 1] range precisely so that one weight is portable.

Three reads, cheapest first:

1. **Preflight** — rotation invariance (mandatory: states are stored Booth-rotated) and the
   x <-> X relabel invariance table. A variant that fails rotation is not a ring feature at all.
2. **Redundancy** — R^2 of each variant against the 17 heap features on start states. This is
   free (no search) and it is what killed the generator channel last time; a variant with R^2
   near 1 cannot help no matter how the search goes.
3. **Search** — solved / nodes at budget 1,000 on a small deterministic slice of the
   ac1m_hard_aut *train* split. Train only: a 14-arm sweep against either holdout would spend it.

Local scope is deliberately small (repo rule: Claude-launched searches are capped at budget 1,000
and ~10-20 presentations). This ranks transforms; it does not settle one. The winner is what
earns a Colab run on the full train 120 and then a holdout read.

    PYTHONPATH=. .venv/bin/python3 -m experiments.heuristic_search.runners.scout_fftvar
"""
from __future__ import annotations

import json
import os
import sys
import time
from datetime import datetime, timezone

import numpy as np

_d = os.path.dirname(os.path.abspath(__file__))
while _d != os.path.dirname(_d) and not all(
        os.path.isdir(os.path.join(_d, _s)) for _s in ("experiments", "data")):
    _d = os.path.dirname(_d)
sys.path.insert(0, _d)

from experiments.heuristic_search.core.search_fftvar import search_fftvar  # noqa: E402
from experiments.heuristic_search.core.fftvar_feats import (  # noqa: E402
    VARIANTS, RELABEL_INVARIANT, fvar_pair_words,
)
from experiments.heuristic_search.core.hlab import phi  # noqa: E402

ROOT = _d
SPLIT = os.path.join(ROOT, "results", "heuristic_search", "splits",
                     "splits_ac1m_hard_aut.json")
OUT_DIR = os.path.join(ROOT, "results", "heuristic_search", "fftvar_scout")
JSONL = os.path.join(OUT_DIR, "runs.jsonl")
RESULTS = os.path.join(OUT_DIR, "RESULTS.md")

BUDGET = 1000          # repo hard cap for a Claude-launched search
CAP = 48
N_PRES = 20            # repo hard cap: ~10-20 presentations locally
WF = 4.0               # the fixed weight the whole sweep is run at

_ALPHA = "XYxy"
_RELABEL = {"X": "x", "x": "X", "Y": "Y", "y": "y"}


def _cfg_L():
    """Pure length base — the arm is exactly ``L + WF * F_i``."""
    return {"segments": [{"upto": None, "w": {"L": 1.0}}]}


def _arms():
    """Control + one arm per variant + the sum-vs-max aggregation probe."""
    out = [("length", "lag345", False, 0.0)]
    for v in VARIANTS:
        out.append((f"F4_{v}", v, False, WF))
    out.append(("F4_lag345_max", "lag345", True, WF))
    return out


# ---------------------------------------------------------------- 1. preflight

def preflight(seed=0):
    """Assert rotation invariance; report and verify the relabel-invariance table."""
    rng = np.random.default_rng(seed)

    def rand_pair(lo=5, hi=24):
        n1 = int(rng.integers(lo, hi))
        n2 = int(rng.integers(lo, hi))
        return ("".join(_ALPHA[i] for i in rng.integers(0, 4, n1)),
                "".join(_ALPHA[i] for i in rng.integers(0, 4, n2)))

    rows = []
    for v in VARIANTS:
        rot_worst = 0.0
        rel_worst = 0.0
        for _ in range(60):
            r1, r2 = rand_pair()
            base = fvar_pair_words(r1, r2, v)
            for k in (1, 3, 7):
                kk1, kk2 = k % len(r1), k % len(r2)
                rot_worst = max(rot_worst, abs(base - fvar_pair_words(
                    r1[kk1:] + r1[:kk1], r2[kk2:] + r2[:kk2], v)))
            rel_worst = max(rel_worst, abs(base - fvar_pair_words(
                "".join(_RELABEL[c] for c in r1),
                "".join(_RELABEL[c] for c in r2), v)))
        rows.append({"variant": v, "rot_dev": rot_worst, "relabel_dev": rel_worst,
                     "relabel_invariant": rel_worst < 1e-9,
                     "claimed_invariant": v in RELABEL_INVARIANT})

    bad_rot = [r["variant"] for r in rows if r["rot_dev"] > 1e-9]
    if bad_rot:
        raise AssertionError(
            f"not rotation-invariant, cannot be a ring feature: {bad_rot}")
    bad_claim = [r["variant"] for r in rows
                 if r["relabel_invariant"] != r["claimed_invariant"]]
    if bad_claim:
        raise AssertionError(
            f"RELABEL_INVARIANT disagrees with measurement for: {bad_claim}")
    return rows


# ---------------------------------------------------------------- 2. redundancy

def redundancy(rows):
    """R^2 of each variant against the 17 heap features, on start states.

    The generator channel died here last time (its low-order DFT content *is* K / xyimb by
    Parseval). Anything with R^2 near 1 is re-deriving a feature the heap already has.
    """
    X = np.asarray([list(phi(r["r1"], r["r2"])) for r in rows], dtype=float)
    X1 = np.concatenate([X, np.ones((len(X), 1))], axis=1)
    out = []
    for v in VARIANTS:
        y = np.asarray([fvar_pair_words(r["r1"], r["r2"], v) for r in rows], float)
        ss_tot = float(np.sum((y - y.mean()) ** 2))
        if ss_tot <= 0:
            out.append({"variant": v, "R2_vs_17": 1.0, "mean": float(y.mean()),
                        "std": 0.0, "degenerate": True})
            continue
        coef, _, _, _ = np.linalg.lstsq(X1, y, rcond=None)
        ss_res = float(np.sum((y - X1 @ coef) ** 2))
        out.append({"variant": v, "R2_vs_17": 1.0 - ss_res / ss_tot,
                    "mean": float(y.mean()), "std": float(y.std()),
                    "degenerate": False})
    return out


# ---------------------------------------------------------------- 3. search

def _append(row):
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(JSONL, "a") as f:
        f.write(json.dumps(row) + "\n")
        f.flush()
        os.fsync(f.fileno())


def _done():
    s = set()
    if not os.path.exists(JSONL):
        return s
    for line in open(JSONL):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        s.add((r.get("arm"), r.get("idx")))
    return s


def run_search(pres, arms):
    done = _done()
    t0 = time.perf_counter()
    n_new = 0
    for arm, variant, agg_max, wF in arms:
        for rec in pres:
            if (arm, rec["idx"]) in done:
                continue
            res = search_fftvar(rec["r1"], rec["r2"], BUDGET, _cfg_L(), CAP,
                                wF=wF, variant=variant, agg_max=agg_max)
            _append({
                "arm": arm, "variant": variant, "agg_max": agg_max, "wF": wF,
                "idx": rec["idx"], "L": rec.get("L"),
                "budget": BUDGET, "cap": CAP,
                "solved": bool(res["solved"]),
                "nodes": int(res["nodes_explored"]),
                "path_length": res["path_length"],
                "min_relator_length": int(res["min_relator_length"]),
                "ts": datetime.now(timezone.utc).isoformat(),
            })
            n_new += 1
        el = time.perf_counter() - t0
        print(f"  {arm:16s} done  ({el/60:.1f} min elapsed)", flush=True)
    return n_new


def rank():
    by = {}
    for line in open(JSONL):
        r = json.loads(line)
        by.setdefault(r["arm"], []).append(r)
    out = []
    for arm, rs in by.items():
        solved = [r for r in rs if r["solved"]]
        nodes = [r["nodes"] for r in solved]
        out.append({
            "arm": arm, "n": len(rs), "solved": len(solved),
            # mean, never sum: each arm's solved set has its own size
            "mean_nodes": (sum(nodes) / len(nodes)) if nodes else None,
            # graded progress signal, defined on unsolved presentations too
            "mean_min_relator": sum(r["min_relator_length"] for r in rs) / len(rs),
            "variant": rs[0]["variant"], "agg_max": rs[0]["agg_max"],
        })
    out.sort(key=lambda r: (-r["solved"],
                            r["mean_nodes"] if r["mean_nodes"] is not None else 1e18))
    return out


# ---------------------------------------------------------------- report

def write_report(pre, red, ranked, pres, wall_min):
    red_by = {r["variant"]: r for r in red}
    pre_by = {r["variant"]: r for r in pre}
    ctrl = next((r for r in ranked if r["arm"] == "length"), None)
    L = []
    L.append("# Spectral-transform scout — `L + 4*F_i` @ budget 1,000")
    L.append("")
    L.append(f"Updated `{datetime.now(timezone.utc).isoformat()}`")
    L.append("")
    L.append("Sweeps the **transform** at a fixed weight, where the shipped work swept the ")
    L.append("weight at a fixed transform. Every variant is normalised to a per-relator [0,1] ")
    L.append("range, so one weight is portable across arms.")
    L.append("")
    L.append(f"**selected_on** = ac1m_hard_aut **train**, first {len(pres)} by index "
             f"(holdouts untouched — a 15-arm sweep would spend one).")
    L.append(f"Budget {BUDGET}, cap {CAP}, weight {WF:g}. Engine: `search_fftvar` "
             f"(`search_signlag` twin). Wall {wall_min:.1f} min.")
    L.append("")
    L.append("> **Scope.** 20 presentations is a *ranking* scout, not a decision: "
             "at this n a one-arm gap is noise. It says which transforms are worth a "
             "Colab run on the full train 120, and which are already dead.")
    L.append("")
    L.append("## Invariance + redundancy (no search — the cheap screen)")
    L.append("")
    L.append("| variant | rot-inv | x<->X inv | R² vs 17 feats | mean | std |")
    L.append("|---|:--:|:--:|---:|---:|---:|")
    for v in VARIANTS:
        p, r = pre_by[v], red_by[v]
        L.append(f"| `{v}` | {'yes' if p['rot_dev'] < 1e-9 else '**NO**'} | "
                 f"{'**yes**' if p['relabel_invariant'] else 'no'} | "
                 f"{r['R2_vs_17']:.3f} | {r['mean']:.3f} | {r['std']:.3f} |")
    L.append("")
    L.append("All thirteen are rotation-invariant (asserted — a variant that failed would not "
             "be a ring feature). `R²` is against the 17 heap features on start states: high "
             "means the heap already knows it.")
    L.append("")
    L.append(f"## Search — `L + {WF:g}*F_i`, budget {BUDGET}")
    L.append("")
    L.append("| rank | arm | solved | mean nodes (own solves) | mean min-relator |")
    L.append("|---:|---|---:|---:|---:|")
    for i, r in enumerate(ranked, 1):
        mn = f"{r['mean_nodes']:.0f}" if r["mean_nodes"] is not None else "—"
        bold = "**" if r["arm"] == "length" else ""
        L.append(f"| {i} | {bold}`{r['arm']}`{bold} | {bold}{r['solved']}/{r['n']}{bold} | "
                 f"{mn} | {r['mean_min_relator']:.1f} |")
    L.append("")
    L.append("## Notes")
    L.append("")
    if ctrl:
        L.append(f"- Control `length` = {ctrl['solved']}/{ctrl['n']} on this slice.")
    L.append("- `mean nodes` is over each arm's **own** solved set, so arms that solve "
             "different presentations are not directly comparable on it — it is a cost "
             "sanity check, not a ranking key.")
    L.append("- `mean min-relator` is the shortest total relator length reached, averaged over "
             "**all** presentations including unsolved ones — a graded progress signal that "
             "does not need a solve, which is what makes n=20 readable at all.")
    L.append("- `F4_lag345_max` swaps the house sum for `2*max` over the two relators "
             "(the move that made MK beat K); same transform, different aggregation.")
    L.append("- Unsolved = unsolved within budget 1,000.")
    L.append("")
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(RESULTS, "w") as f:
        f.write("\n".join(L))
    return "\n".join(L)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    t0 = time.perf_counter()

    print("preflight: invariances…", flush=True)
    pre = preflight()
    for r in pre:
        print(f"   {r['variant']:9s} rot={r['rot_dev']:.1e} "
              f"relabel={'INV' if r['relabel_invariant'] else 'no '}", flush=True)

    sp = json.load(open(SPLIT))
    train = sp["train_rows"]
    all_rows = train + sp["holdout_rows"]

    print(f"redundancy vs 17 feats on {len(all_rows)} start states…", flush=True)
    red = redundancy(all_rows)
    for r in sorted(red, key=lambda r: r["R2_vs_17"]):
        print(f"   {r['variant']:9s} R2={r['R2_vs_17']:.3f} "
              f"mean={r['mean']:.3f} std={r['std']:.3f}", flush=True)
    with open(os.path.join(OUT_DIR, "screen.json"), "w") as f:
        json.dump({"preflight": pre, "redundancy": red}, f, indent=2)
        f.write("\n")

    pres = sorted(train, key=lambda r: r["idx"])[:N_PRES]
    arms = _arms()
    print(f"search: {len(arms)} arms x {len(pres)} pres @ budget {BUDGET}", flush=True)
    search_fftvar("X", "Y", 20, _cfg_L(), 32, wF=0.0)  # warm the jit
    run_search(pres, arms)

    ranked = rank()
    wall = (time.perf_counter() - t0) / 60.0
    print(write_report(pre, red, ranked, pres, wall))
    print(f"\nwrote {RESULTS}")


if __name__ == "__main__":
    main()
