"""EXP-05 -- the relator cap, re-asked as an interaction instead of in isolation.

EXP-01 swept ``max_relator_length`` at 24/32/48/64 and found it completely inert: bit-identical
solves, nodes, paths and progress at both budgets. That result is correct and it is also nearly
uninformative, because it was measured under the *baseline* ordering. A length-greedy pops the
shortest state available, so inside 1,000 pops it never reaches a 24-letter relator at all -- the
cap cannot bind on a search that never approaches it, at any cap above where it sits.

EXP-02 changed the premise. Its winner (``L + 8K``) pops a **28-letter** relator, and 78 of its
193 configs exceed 24. So the cap is a live parameter exactly where the ordering climbs, and the
honest form of the question is not "does the cap matter" but "does the cap matter *for an ordering
that uses it*".

Two things this must not do. It must not sweep caps for the baseline again -- that is EXP-01 and
it is already answered. And it must not read the winners off a hand-typed list: the configs come
from the EXP-02/03/04 jsonl files, so if an earlier experiment is re-run this one follows it
rather than silently testing a superseded ordering.

``max_pop`` is the diagnostic that makes a null result readable. If an arm's longest popped
relator sits strictly below its cap, the cap provably did not bind for that arm and its equality
with a lower cap is a tautology rather than evidence.

    python3 -m experiments.heuristic_search.exp05_cap
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import (                    # noqa: E402
    BASELINE_CONFIG, LOGS, cfg_name,
)
from experiments.heuristic_search.lab import evaluate, rank, read  # noqa: E402

BUDGET = 500
SLICE = "train"
CAPS = (24, 32, 48, 64, 96)
N_TOP = 6
OUT = os.path.join(LOGS, "EXP05_cap.jsonl")

SOURCES = ("EXP02_single.jsonl", "EXP03_segments.jsonl", "EXP04_multi.jsonl")


def top_configs(n=N_TOP):
    """The best orderings found so far, read from the experiment files rather than retyped.

    Configs are recovered from each experiment's own generator so the dict shape is exact; a
    config id parsed back into a dict would be a second, drifting definition of the same thing.
    """
    pool, seen = [], set()
    ctrl = cfg_name(BASELINE_CONFIG)

    known = {}
    from experiments.heuristic_search.exp02_single import configs as c2
    known.update({cfg_name(c): c for c in c2()[0]})
    try:
        from experiments.heuristic_search.exp03_segments import configs as c3
        known.update({cfg_name(c): c for c in c3()[0]})
    except Exception:
        pass                                   # EXP-03 has not run yet; its arms simply are not offered
    try:
        from experiments.heuristic_search.exp04_multi import configs as c4
        known.update({cfg_name(c): c for c in c4()[0]})
    except Exception:
        pass

    for src in SOURCES:
        path = os.path.join(LOGS, src)
        res = read(path)
        if ctrl not in res:
            continue
        for r in rank(res, ctrl):
            cid = r["config_id"]
            if cid == ctrl or cid in seen or cid not in known:
                continue
            seen.add(cid)
            pool.append((r["solved"], r["nodes_mean"] or 1e9, cid))
    pool.sort(key=lambda t: (-t[0], t[1]))
    return [known[cid] for _, _, cid in pool[:n]]


def main():
    tops = top_configs()
    if not tops:
        raise SystemExit("no completed experiment to draw winners from -- run EXP-02 first")
    # The baseline rides along at every cap so each arm has a same-cap control. An ordering
    # compared against a control at a different cap is not a comparison.
    cfgs = [BASELINE_CONFIG] + tops
    print("  sweeping caps for: " + ", ".join(cfg_name(c) for c in tops), flush=True)

    for cap in CAPS:
        evaluate(cfgs, SLICE, BUDGET, cap, OUT, label=f"EXP05-cap{cap}")

    res = read(OUT, by=("config_id", "mrl"))
    lines = [f"# EXP-05 — does the cap bind once the ordering climbs?", "",
             f"Slice: `{SLICE}` (40). Budget {BUDGET}. Caps {', '.join(map(str, CAPS))}. Each cap "
             "carries its own baseline control, because an ordering compared against a control at "
             "a different cap is not a comparison.", "",
             "`max pop` is the longest single relator any search under that arm actually popped. "
             "Where it sits strictly below the cap, the cap **provably did not bind** and equality "
             "with a lower cap is a tautology, not evidence.", "",
             "| config | " + " | ".join(f"cap {c}" for c in CAPS) + " |",
             "|---" * (len(CAPS) + 1) + "|"]

    for cfg in cfgs:
        cid = cfg_name(cfg)
        cells = []
        for cap in CAPS:
            arm = f"{cid} | {cap}"
            if arm not in res:
                cells.append("—")
                continue
            ctrl_arm = f"{cfg_name(BASELINE_CONFIG)} | {cap}"
            sc = rank({arm: res[arm], ctrl_arm: res[ctrl_arm]}, ctrl_arm)
            r = next(x for x in sc if x["config_id"] == arm)
            mp = max(x["max_pop"] for x in res[arm].values())
            cells.append(f"{r['solved']}/{r['n']} (maxpop {mp})")
        tag = " ← control" if cid == cfg_name(BASELINE_CONFIG) else ""
        lines.append(f"| `{cid[:44]}`{tag} | " + " | ".join(cells) + " |")

    with open(os.path.join(LOGS, "EXP05_cap.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
