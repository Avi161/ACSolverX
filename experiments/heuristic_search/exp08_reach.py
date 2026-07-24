"""EXP-08 -- the second hump, reported on real solves only.

EXP-07 established that no checkpoint proxy (knots reached, length reached) predicts a solve, so
there is nothing honest to *rank* the never-solving rows by. What remains worth doing is the
literal question the user posed: run the best orderings found on the hardest rows and see whether
any of them actually cracks one at a budget this program can run. Unlikely -- these need 60k to
10M+ nodes under the baseline -- but a knot ordering reorders difficulty, so it is not impossible
that some row falls far below its baseline cost, and that would be a genuine find rather than a
proxy.

The hard set is the train rows in bins 8-9 (baseline needs ~60k-270k nodes) plus the six reach
rows (open; unsolved past ten million). Budget 1,000, the local ceiling. Every field is a real
outcome: ``solved`` is a solve, ``min_total``/``min_K`` are recorded but explicitly NOT used to
rank anything -- they are context for a human, carrying the caveat EXP-07 attached to them.

    python3 -m experiments.heuristic_search.exp08_reach
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import (                    # noqa: E402
    BASELINE_CONFIG, LOGS, bench66, cfg_name, load_split,
)
from experiments.heuristic_search.lab import evaluate, read        # noqa: E402
from experiments.heuristic_search.exp05_cap import top_configs     # noqa: E402
from experiments.heuristic_search.perbin import bin_of             # noqa: E402

BUDGET = 1_000
MRL = 64            # let relators grow: the climb orderings pop past 24, EXP-02 showed 28+
OUT = os.path.join(LOGS, "EXP08_reach.jsonl")


def hard_rows():
    """Train bins 8-9 + the reach slice. Names only; evaluate() re-reads them from the split."""
    hard = [r["name"] for r in load_split("train") if bin_of(r["name"]) in (8, 9)]
    reach = [r["name"] for r in load_split("reach")]
    return hard, reach


class _Slice:
    """A throwaway slice object: evaluate() calls load_split(name), so register these names."""


def main():
    hard, reach = hard_rows()
    # evaluate() loads by split name, so build an ad-hoc split file entry via a monkeypatch-free
    # route: run the two real splits and filter. Simpler: score directly with search_fast here,
    # since this is a fixed small set and needs no resume sharing with the sweeps.
    from experiments.heuristic_search.hfast import search_fast
    by = {r["name"]: r for r in bench66()}
    cfgs = [BASELINE_CONFIG] + top_configs(8)

    done = set()
    if os.path.exists(OUT):
        for line in open(OUT):
            try:
                r = json.loads(line)
            except ValueError:
                continue
            done.add((r["config_id"], r["name"]))

    names = hard + reach
    with open(OUT, "a") as f:
        for cfg in cfgs:
            cid = cfg_name(cfg)
            for nm in names:
                if (cid, nm) in done:
                    continue
                row = by[nm]
                res = search_fast(row["r1"], row["r2"], BUDGET, cfg, MRL)
                f.write(json.dumps({
                    "config_id": cid, "name": nm, "budget": BUDGET, "mrl": MRL,
                    "bin": bin_of(nm), "solved": res["solved"], "nodes": res["nodes"],
                    "path_length": res["path_length"], "min_total": res["min_total"],
                    "start_K": res["start_K"], "min_K": res["min_K"],
                    "source": row["source"]}) + "\n")
                f.flush()
                os.fsync(f.fileno())

    res = read(OUT)
    ctrl = cfg_name(BASELINE_CONFIG)
    any_solve = [(cid, nm) for cid, v in res.items() for nm, r in v.items() if r["solved"]]

    lines = [
        "# EXP-08 — the second hump, on real solves only", "",
        f"Train bins 8-9 ({len(hard)} rows) + the reach slice ({len(reach)} open rows). "
        f"Budget {BUDGET}, cap {MRL} (relators allowed to grow). Best {len(cfgs) - 1} orderings "
        "from the sweeps, plus the baseline.", "",
        "Ranked on nothing but solves: EXP-07 showed knot- and length-progress do not predict a "
        "solve at the boundary, so `min_total`/`min_K` below are context, not a score.", "",
    ]
    if any_solve:
        lines += [f"## A hard row actually solved at {BUDGET} nodes", ""]
        for cid, nm in any_solve:
            r = res[cid][nm]
            lines.append(f"- **{nm}** (bin {r['bin']}, {r['source']}) by `{cid}` in "
                         f"{r['nodes']} nodes, path {r['path_length']}")
        lines.append("")
    else:
        lines += [f"**No hard row solved at {BUDGET} nodes** by any ordering — expected: these need "
                  "tens of thousands to millions of nodes under the baseline, and a 1,000-node "
                  "local ceiling cannot reach that. The finding is that the knot ordering does not "
                  "collapse any second-hump row to a small search, not that it fails to help on the "
                  "decidable rows (it does — see EXP-02/03).", ""]

    # Descriptive only, with the caveat stated in the header.
    lines += ["## Best knot count reached (descriptive — NOT a ranking)", "",
              "| config | rows where min_K < start_K | mean min_K reached |", "|---|---|---|"]
    for cid in [ctrl] + [cfg_name(c) for c in cfgs[1:]]:
        if cid not in res:
            continue
        v = res[cid]
        red = sum(1 for r in v.values() if "min_K" in r and r["min_K"] < r["start_K"])
        mk = sum(r["min_K"] for r in v.values() if "min_K" in r) / max(1, len(v))
        tag = " ← ctrl" if cid == ctrl else ""
        lines.append(f"| `{cid[:40]}`{tag} | {red}/{len(v)} | {mk:.2f} |")

    with open(os.path.join(LOGS, "EXP08_reach.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
