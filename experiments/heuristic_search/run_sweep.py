"""Does any block/knot heap ordering beat ordering by length, at the same node budget?

Protocol, and why each piece is there:

  * **Benchmark**: the frozen difficulty-stratified subsets in ``results/benchmark/subsets/`` --
    10 log-width bins of search difficulty, minimally automorphic, so the set is not 20 copies of
    the same easy problem. Tuning happens on ``subset_20``; the reported held-out check is the
    **22 presentations in subset_40 that are not in subset_20** (the two overlap by 18, so
    subset_40 as a whole is NOT a clean validation set and is never used as one here).
  * **Control**: ``length`` is the baseline's own ordering. It is asserted to reproduce
    ``greedy_search`` presentation by presentation -- identical solved flag AND identical
    ``nodes_explored`` -- before any comparison is read. A control that merely scores the same is
    not the same search.
  * **Budgets**: 100 / 200 / 500 pops per presentation. 500 is the ceiling for any search run
    locally (``experiments/lessons/local-run-budget-cap.md``); a search at budget B is the first B
    pops of any longer one, so this measures the opening, which is exactly where an ordering
    differs.
  * **Two metrics**: solve count at the budget, and -- on the presentations *both* arms solve --
    total nodes spent. An ordering can be better without solving more, by getting there sooner.

    python3 -m experiments.heuristic_search.run_sweep
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hsearch import PRIORITIES, ROOT, hsearch   # noqa: E402
from experiments.run_baseline import load_dataset                           # noqa: E402
from experiments.search.greedy_baseline import greedy_search                # noqa: E402

SUBSETS = os.path.join(ROOT, "results", "benchmark", "subsets")
OUT = os.path.join(ROOT, "results", "heuristic_search")
BUDGETS = (100, 200, 500)          # 500 is the hard local ceiling -- never raise it here
MRL = 24


def subset_ids(k):
    with open(os.path.join(SUBSETS, f"benchmark_subset_{k}.json")) as f:
        return [r["pres_id"] for r in json.load(f)["subset"]]


def load(ids):
    by = {p: (r1, r2) for p, r1, r2 in load_dataset(os.path.join(ROOT, "data/ms640_solved.txt"))}
    return [(p, *by[p]) for p in ids]


def control_gate(pres, budget):
    """``length`` must BE the baseline, not merely tie it. Nothing below is readable otherwise."""
    for pid, r1, r2 in pres:
        a = greedy_search(r1, r2, budget, max_relator_length=MRL)
        b = hsearch(r1, r2, budget, PRIORITIES["length"], max_relator_length=MRL)
        if bool(a["solved"]) != bool(b["solved"]) or a["nodes_explored"] != b["nodes_explored"]:
            raise RuntimeError(
                f"control diverges on pres {pid} @{budget}: baseline "
                f"{a['solved']}/{a['nodes_explored']} vs length-priority "
                f"{b['solved']}/{b['nodes_explored']} -- the subclass changed more than the order")
    return True


def run(pres, budget, name):
    p = PRIORITIES[name]
    out = {}
    for pid, r1, r2 in pres:
        r = hsearch(r1, r2, budget, p, max_relator_length=MRL)
        out[pid] = (bool(r["solved"]), r["nodes_explored"], r["path_length"])
    return out


def _sign_test(w, l):
    """Two-sided exact sign test on the discordant pairs -- solve counts here are PAIRED.

    Reporting a net gain without this invites reading '+3 of 22' as an effect; with 4 wins against
    1 loss it is p = 0.375, which is the honest reading of a benchmark this small.
    """
    n = w + l
    if n == 0:
        return 1.0
    from math import comb
    k = max(w, l)
    tail = sum(comb(n, i) for i in range(k, n + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def compare(res, ctrl):
    """Solved count, plus nodes on the presentations BOTH arms solved (a like-for-like subset).

    ``nodes_both_mean`` exists because the raw SUM is not comparable between two arms: each arm's
    both-solved set has its own size, so an arm that solves one presentation fewer can post a
    smaller total while being slower on every single search. Ranking on the sum picked the wrong
    winner here once already -- 537 over 8 beat 582 over 9, when the means are 67.1 against 64.7.
    """
    both = [k for k in res if res[k][0] and ctrl[k][0]]
    won = sorted(k for k in res if res[k][0] and not ctrl[k][0])
    lost = sorted(k for k in res if ctrl[k][0] and not res[k][0])
    n = len(both)
    return {
        "solved": sum(v[0] for v in res.values()),
        "won": won, "lost": lost, "net": len(won) - len(lost),
        "sign_p": _sign_test(len(won), len(lost)),
        "nodes_both": sum(res[k][1] for k in both),
        "nodes_both_ctrl": sum(ctrl[k][1] for k in both),
        "nodes_both_mean": (sum(res[k][1] for k in both) / n) if n else None,
        "nodes_both_ctrl_mean": (sum(ctrl[k][1] for k in both) / n) if n else None,
        "n_both": n,
    }


def table(pres, tag, names, verbose=True):
    rows = {}
    for budget in BUDGETS:
        control_gate(pres, budget)
        ctrl = run(pres, budget, "length")
        rows[budget] = {n: compare(run(pres, budget, n), ctrl) for n in names}
        rows[budget]["length"] = compare(ctrl, ctrl)
    if verbose:
        n = len(pres)
        print(f"\n{'=' * 92}\n{tag}  ({n} presentations)   control gate passed at every budget"
              f"\n{'=' * 92}")
        print(f"  {'priority':26s}" + "".join(f"{'@' + str(b):>18}" for b in BUDGETS))
        base = {b: rows[b]["length"]["solved"] for b in BUDGETS}
        for name in ["length"] + [x for x in names if x != "length"]:
            cells = ""
            for b in BUDGETS:
                r = rows[b][name]
                d = r["solved"] - base[b]
                mark = "" if name == "length" else (f" {d:+d}" if d else "  =")
                cells += f"{r['solved']:>3d}/{n}{mark:>5}".rjust(18)
            print(f"  {name:26s}{cells}")
    return rows


def detail(rows, names, tag):
    print(f"\n  paired detail @500 ({tag}) -- net solves and nodes per commonly-solved search:")
    for n in names:
        r = rows[500][n]
        if n == "length":
            continue
        nm = "" if r["nodes_both_mean"] is None else (
            f"{r['nodes_both_mean']:.0f} vs {r['nodes_both_ctrl_mean']:.0f} ctrl "
            f"(n={r['n_both']})")
        print(f"    {n:26s} won {len(r['won'])} lost {len(r['lost'])}  net {r['net']:+d}  "
              f"sign p={r['sign_p']:.3f}   nodes {nm}")


def main():
    ids20 = subset_ids(20)
    s20, s40 = set(ids20), set(subset_ids(40))
    burned = [p for p in subset_ids(40) if p not in s20]
    fresh = [p for p in subset_ids(60) if p not in s20 and p not in s40]
    names = list(PRIORITIES)

    tune = table(load(ids20), "TUNE  ·  benchmark subset 20", names)
    # The winner is chosen on the TUNING set only, ranked by solves and then by nodes per
    # commonly-solved search. See compare(): ranking on the node SUM is what picked wrong before.
    ranked = sorted((r for r in PRIORITIES if r != "length"),
                    key=lambda n: (-tune[500][n]["solved"],
                                   tune[500][n]["nodes_both_mean"] or 1e9))
    best, runners = ranked[0], ranked[1:3]
    detail(tune, ranked[:4], "tuning set")
    print(f"\n  pre-registered winner on the tuning set @500: {best}")

    # The 22 of subset-40 were already looked at under a BUGGY tie-break, so they cannot serve as
    # a clean confirmation any more -- they are reported, and labelled, as exploratory.
    expl = table(load(burned),
                 f"EXPLORATORY (already seen)  ·  the {len(burned)} of subset-40 not in subset-20",
                 ["length", best] + runners)
    detail(expl, [best] + runners, "exploratory")

    conf = table(load(fresh),
                 f"CONFIRM (untouched)  ·  the {len(fresh)} of subset-60 in neither set above",
                 ["length", best] + runners)
    detail(conf, [best] + runners, "confirmation")

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "sweep.json"), "w") as f:
        json.dump({"tune_ids": ids20, "exploratory_ids": burned, "confirm_ids": fresh,
                   "budgets": list(BUDGETS), "best_on_tune": best, "runners_up": runners,
                   "tune": {str(k): v for k, v in tune.items()},
                   "exploratory": {str(k): v for k, v in expl.items()},
                   "confirm": {str(k): v for k, v in conf.items()}}, f, indent=1)
    print(f"\nwrote -> {os.path.relpath(OUT, ROOT)}/sweep.json")


if __name__ == "__main__":
    main()
