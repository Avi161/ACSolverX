"""EXP-06 -- promote the survivors from budget 500 to budget 1,000.

Everything so far was selected at 500 nodes because that is where a hundred-config sweep is
affordable. Nothing guarantees the ranking survives a doubled budget, and the failure mode has a
direction: an ordering that wins at 500 by reaching easy solutions fast can be overtaken at 1,000
by one that spends its early pops climbing and cashes in later. That is precisely the ordering
this program is looking for, so the promotion step is not a formality.

The budget is the *only* thing that changes. Same frozen slice, same cap, same control, so a
config's movement between the two tables is attributable to the budget and to nothing else.

1,000 is the hard local ceiling and it is asserted in ``lab.evaluate``. A search at budget B is
exactly the first B pops of any longer search, so the shape of the 500 -> 1,000 movement is what
predicts behaviour at the budgets the user runs on Colab; a bigger local budget would buy a slower
repro, never a different behaviour.

    python3 -m experiments.heuristic_search.exp06_promote
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import (                    # noqa: E402
    BASELINE_CONFIG, LOGS, cfg_name,
)
from experiments.heuristic_search.lab import evaluate, rank, read  # noqa: E402
from experiments.heuristic_search.exp05_cap import top_configs     # noqa: E402

BUDGET = 1_000
MRL = 48
SLICE = "train"
N_TOP = 10
OUT = os.path.join(LOGS, "EXP06_promote.jsonl")


def main():
    tops = top_configs(N_TOP)
    if not tops:
        raise SystemExit("no completed experiment to draw winners from")
    cfgs = [BASELINE_CONFIG] + tops
    evaluate(cfgs, SLICE, BUDGET, MRL, OUT, label="EXP06")

    hi = read(OUT)
    ctrl = cfg_name(BASELINE_CONFIG)
    rows_hi = {r["config_id"]: r for r in rank(hi, ctrl)}

    # The same configs at 500, so the two columns are the same arms and the movement is readable.
    # Filter each row to (500, mrl) BEFORE merging: EXP-05 carries five caps per name, and read()
    # groups by config id alone, so a blind merge lets a non-48 cap overwrite the 48 row and the
    # filter then drops it -- which blanked this column the first time.
    lo_all = {}
    for src in ("EXP02_single.jsonl", "EXP03_segments.jsonl", "EXP04_multi.jsonl",
                "EXP05_cap.jsonl"):
        r = read(os.path.join(LOGS, src), by=("config_id", "budget", "mrl"))
        for arm, v in r.items():
            cid, budget, mrl = arm.rsplit(" | ", 2)
            if int(budget) == 500 and int(mrl) == MRL:
                lo_all.setdefault(cid, {}).update(v)
    lo = {}
    if ctrl in lo_all and lo_all[ctrl]:
        lo = {r["config_id"]: r for r in rank({k: v for k, v in lo_all.items() if v}, ctrl)}

    base_hi = rows_hi[ctrl]
    lines = [f"# EXP-06 — the same orderings at budget 1,000", "",
             f"Slice: `{SLICE}` (40). Cap {MRL}. Only the budget changed. Control = baseline, "
             f"**{base_hi['solved']}/{base_hi['n']}** at 1,000"
             + (f" (was {lo[ctrl]['solved']}/{lo[ctrl]['n']} at 500)." if ctrl in lo else "."), "",
             "An ordering that gains going 500 → 1,000 is spending early pops on structure and "
             "cashing in later — the behaviour this program is looking for. One that loses ground "
             "was winning at 500 by reaching the easy solutions first.", "",
             "| config | 500 | 1,000 | Δ | net@1k | p | mean nodes | mean path | Δmin |",
             "|---|---|---|---|---|---|---|---|---|"]

    order = sorted(rows_hi.values(), key=lambda r: (-r["solved"], r["nodes_mean"] or 1e9))
    for r in order:
        cid = r["config_id"]
        lo_s = f"{lo[cid]['solved']}/{lo[cid]['n']}" if cid in lo else "—"
        d = (f"{r['solved'] - lo[cid]['solved']:+d}" if cid in lo else "—")
        nm = f"{r['nodes_mean']:.0f}" if r["nodes_mean"] is not None else "—"
        pm = f"{r['path_mean']:.1f}" if r["path_mean"] is not None else "—"
        tag = " ← control" if cid == ctrl else ""
        lines.append(f"| `{cid[:46]}`{tag} | {lo_s} | {r['solved']}/{r['n']} | {d} | "
                     f"{r['net']:+d} | {r['sign_p']:.3f} | {nm} | {pm} | "
                     f"{r['min_total_gain']:+.2f} |")

    with open(os.path.join(LOGS, "EXP06_promote.json"), "w") as f:
        json.dump({"budget": BUDGET, "mrl": MRL, "top": order}, f, indent=1)
    with open(os.path.join(LOGS, "EXP06_promote.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
