"""EXP-18 -- re-tune the endgame threshold for the ordering that actually won.

The phase boundary has been fixed at 16 since EXP-03. That was a real measurement, but it was made
under conditions that no longer hold: EXP-03 swept the threshold at **budget 500**, for the
**simple `L + 8K`** ordering, on the stratified train slice. The recommendation has since moved to
a richer multi-feature climb, at budget 1,000, and the threshold was carried along untouched.

A knob frozen at a value chosen for a different configuration is exactly the kind of thing that
quietly costs a result, and re-checking it is cheap. So: sweep the boundary again, for each of the
orderings still in play, at both budgets, and see whether 16 is still where it belongs.

The endgame boundary is also worth understanding rather than just optimising. Below it the ordering
is pure length -- the endgame, where the remaining work is cancellation and structure has stopped
mattering. Above it the structural climb runs. Moving the boundary up hands more of the search to
pure length; moving it down keeps the climb running closer to the trivial state. A boundary of 0
would be no endgame at all (climb everywhere), and one above the starting length would be no climb
at all, so the sweep spans both degenerate ends and the answer should sit strictly inside them --
if it does not, the two-phase story is wrong.

    python3 -m experiments.heuristic_search.exp18_threshold_retune
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import LOGS, bench66        # noqa: E402
from experiments.heuristic_search.hfast import search_fast         # noqa: E402
from experiments.heuristic_search.perbin import bin_of             # noqa: E402

MRL = 48
THRESHOLDS = (0, 8, 12, 14, 16, 18, 20, 24, 28, 34)
OUT = os.path.join(LOGS, "EXP18_threshold.jsonl")

# The climb vectors still in play, each to be paired with every threshold.
CLIMBS = {
    "K8": {"L": 1.0, "K": 8.0},
    "K+xyimb": {"L": 1.0, "K": 8.936, "xyimb": -5.978},
    "richer": {"L": 1.0, "K": 2.53, "MK": 6.418, "S": 8.458, "xyimb": 3.292},
    "blocks": {"L": 1.0, "Bmax": -2.185, "S": 5.668},
}


def cfg_for(climb, T):
    """``T == 0`` means no endgame segment at all -- the climb runs everywhere."""
    if T == 0:
        return {"segments": [{"upto": None, "w": dict(CLIMBS[climb])}]}
    return {"segments": [{"upto": T, "w": {"L": 1.0}},
                         {"upto": None, "w": dict(CLIMBS[climb])}]}


def main():
    rows = [r for r in bench66() if r["source"] == "ladder" and bin_of(r["name"]) in (4, 5, 6, 7)]
    done = set()
    if os.path.exists(OUT):
        for line in open(OUT):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            done.add((r["climb"], r["T"], r["name"], r["budget"]))

    print(f"  {len(CLIMBS)} climbs x {len(THRESHOLDS)} thresholds x {len(rows)} rows x 2 budgets",
          flush=True)
    with open(OUT, "a") as f:
        for budget in (500, 1000):
            for climb in CLIMBS:
                for T in THRESHOLDS:
                    cfg = cfg_for(climb, T)
                    for row in rows:
                        if (climb, T, row["name"], budget) in done:
                            continue
                        res = search_fast(row["r1"], row["r2"], budget, cfg, MRL)
                        f.write(json.dumps({
                            "climb": climb, "T": T, "name": row["name"], "budget": budget,
                            "mrl": MRL, "solved": res["solved"], "nodes": res["nodes"],
                            "path_length": res["path_length"]}) + "\n")
                        f.flush()
                        os.fsync(f.fileno())

    data = [json.loads(l) for l in open(OUT)]
    n = len(rows)
    lines = ["# EXP-18 — is 16 still the right endgame boundary?", "",
             "The phase boundary was fixed at 16 by EXP-03, which swept it **at budget 500 for the "
             "simple `L + 8K` ordering**. The recommendation has since moved to a richer climb at "
             "budget 1,000 and the boundary was carried along untouched. This re-sweeps it for "
             f"every climb still in play, on the decidable band (bins 4–7, {n} rows).", "",
             "`T = 0` means no endgame segment at all — the climb runs everywhere — so it is the "
             "control on whether the two-phase shape is doing anything.", ""]

    best_at = {}
    for budget in (500, 1000):
        lines += [f"## Budget {budget}", "",
                  "| climb | " + " | ".join(f"T={t}" for t in THRESHOLDS) + " | best |",
                  "|---" * (len(THRESHOLDS) + 2) + "|"]
        for climb in CLIMBS:
            row_vals = []
            for T in THRESHOLDS:
                d = [r for r in data if r["climb"] == climb and r["T"] == T
                     and r["budget"] == budget]
                row_vals.append(sum(r["solved"] for r in d) if d else None)
            if any(v is None for v in row_vals):
                continue
            top = max(row_vals)
            bestT = [t for t, v in zip(THRESHOLDS, row_vals) if v == top]
            best_at[(budget, climb)] = (top, bestT)
            cells = [f"**{v}**" if v == top else str(v) for v in row_vals]
            lines.append(f"| {climb} | " + " | ".join(cells)
                         + f" | {top}/{n} at T={','.join(map(str, bestT))} |")
        lines.append("")

    lines += ["## Does 16 still hold?", ""]
    holds, moved = [], []
    for (budget, climb), (top, bestT) in sorted(best_at.items()):
        if 16 in bestT:
            holds.append(f"- budget {budget}, `{climb}`: yes — 16 is among the optima ({top}/{n}).")
        else:
            d16 = [r for r in data if r["climb"] == climb and r["T"] == 16
                   and r["budget"] == budget]
            s16 = sum(r["solved"] for r in d16)
            moved.append(f"- budget {budget}, `{climb}`: **no** — best is T={bestT[0]} at {top}/{n}, "
                         f"against {s16}/{n} at 16 (**{top - s16:+d}**).")
    lines += holds + moved + [""]

    # Is the endgame phase doing anything at all? T=0 is the control.
    lines += ["## Is the endgame phase load-bearing?", "",
              "`T = 0` removes it entirely. If that matched the best threshold, the two-phase "
              "story would be decoration.", "",
              "| budget | climb | T=0 | best T | difference |", "|---|---|---|---|---|"]
    for (budget, climb), (top, bestT) in sorted(best_at.items()):
        d0 = [r for r in data if r["climb"] == climb and r["T"] == 0 and r["budget"] == budget]
        s0 = sum(r["solved"] for r in d0)
        lines.append(f"| {budget} | {climb} | {s0}/{n} | {top}/{n} (T={bestT[0]}) | "
                     f"**{top - s0:+d}** |")

    with open(os.path.join(LOGS, "EXP18_threshold.json"), "w") as f:
        json.dump({"thresholds": list(THRESHOLDS),
                   "best": {f"{b}|{c}": {"solved": t, "T": ts}
                            for (b, c), (t, ts) in best_at.items()}}, f, indent=1)
    with open(os.path.join(LOGS, "EXP18_threshold.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
