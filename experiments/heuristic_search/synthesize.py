"""Synthesis -- pick the heuristic, then spend the frozen test slice, once, to price its overfit.

Everything upstream selected on ``train``. With a dozen parameters against forty presentations,
the best of a few hundred configs is upward-biased by construction: some of its margin is signal
and some is that it happened to fit these forty rows. The only instrument that reads the split is a
slice nothing was chosen on, so this is the one place the ``test`` slice is opened, and it is
opened exactly once -- re-running this script re-reads the cached jsonl rather than re-searching,
so no amount of iteration can turn ``test`` into a selection surface.

The recommendation is not a single number. The user asked for two things that need not share a
winner: the ordering that solves the most (ranked by node budget, then path length), and the most
advantage on the second hump. EXP-07 showed the second hump has no honest ranking signal at these
budgets, so that half is reported as "what actually solved" rather than "what progressed most".

    python3 -m experiments.heuristic_search.synthesize
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import (                    # noqa: E402
    BASELINE_CONFIG, LOGS, cfg_name, load_split,
)
from experiments.heuristic_search.lab import evaluate, rank, read, score  # noqa: E402
from experiments.heuristic_search.perbin import (                  # noqa: E402
    bin_of, bin_table, decidable, decidable_line,
)

MRL = 48
TRAIN_SOURCES = ("EXP02_single.jsonl", "EXP03_segments.jsonl", "EXP04_multi.jsonl",
                 "EXP05_cap.jsonl", "EXP06_promote.jsonl")
AUT_OUT = os.path.join(LOGS, "AUT_final.jsonl")
N_CANDIDATES = 25          # proposed from the stratified sweeps, re-selected on the aut split


def all_train(budget, mrl=MRL):
    """Every config's rows at one (budget, mrl), merged across experiment files."""
    merged = {}
    for src in TRAIN_SOURCES:
        r = read(os.path.join(LOGS, src))
        for cid, v in r.items():
            for nm, row in v.items():
                if row["budget"] == budget and row["mrl"] == mrl:
                    merged.setdefault(cid, {})[nm] = row
    return {cid: v for cid, v in merged.items() if v}


def id_to_cfg(cid):
    """Recover a config dict from any experiment generator that produced it."""
    known = {}
    from experiments.heuristic_search.exp02_single import configs as c2
    known.update({cfg_name(c): c for c in c2()[0]})
    for mod in ("exp03_segments", "exp04_multi"):
        try:
            m = __import__(f"experiments.heuristic_search.{mod}", fromlist=["configs"])
            known.update({cfg_name(c): c for c in m.configs()[0]})
        except Exception:
            pass
    known[cfg_name(BASELINE_CONFIG)] = BASELINE_CONFIG
    return known.get(cid)


def main():
    ctrl = cfg_name(BASELINE_CONFIG)

    # 1) Propose candidates from the stratified sweeps -- a wide net (top 25 by decidable solves at
    #    500), used ONLY to narrow the field. The winner is chosen afterwards on the aut split.
    tr500 = all_train(500)
    if ctrl not in tr500:
        raise SystemExit("no baseline rows at 500 -- run the sweeps first")
    dec = set(decidable(tr500))
    proposed = sorted(
        (c for c in tr500 if c != ctrl),
        key=lambda cid: (-sum(1 for nm in dec if nm in tr500[cid] and tr500[cid][nm]["solved"]),
                         score(tr500[cid], tr500[ctrl])["nodes_mean"] or 1e9,
                         score(tr500[cid], tr500[ctrl])["path_mean"] or 1e9))[:N_CANDIDATES]
    cand_cfgs = [BASELINE_CONFIG] + [id_to_cfg(c) for c in proposed if id_to_cfg(c)]

    # 2) Re-evaluate every candidate on the AUTOMORPHISM-DISJOINT split, both budgets. Selection and
    #    the held-out read both live inside this partition, so no aut_class is shared across them.
    for b in (500, 1000):
        evaluate(cand_cfgs, "aut_train", b, MRL, AUT_OUT, label=f"AUT-train-{b}")
        evaluate(cand_cfgs, "aut_test", b, MRL, AUT_OUT, label=f"AUT-test-{b}")

    # Key by (config, budget): read() groups by config id alone, so the 500 and 1000 rows for one
    # (config, name) collapse to whichever is last in the file. Splitting on budget here keeps them
    # distinct -- the same trap that blanked EXP-06's Δ column.
    aut = read(AUT_OUT, by=("config_id", "budget"))
    tr_names = {r["name"] for r in load_split("aut_train")}
    te_names = {r["name"] for r in load_split("aut_test")}

    def slice_at(budget):
        tr, te = {}, {}
        for arm, v in aut.items():
            cid, b = arm.rsplit(" | ", 1)
            if int(b) != budget:
                continue
            tr[cid] = {n: r for n, r in v.items() if n in tr_names}
            te[cid] = {n: r for n, r in v.items() if n in te_names}
        return tr, te

    def dec_solved(res, cid, names):
        return sum(1 for nm in names if nm in res.get(cid, {}) and res[cid][nm]["solved"])

    def pick(a_tr):
        """Winner on aut_train's decidable subset: most solves, then fewer nodes, then shorter path."""
        d = set(decidable(a_tr))
        ranked = sorted(
            (c for c in a_tr if c != ctrl),
            key=lambda cid: (-dec_solved(a_tr, cid, d),
                             score(a_tr[cid], a_tr[ctrl])["nodes_mean"] or 1e9,
                             score(a_tr[cid], a_tr[ctrl])["path_mean"] or 1e9))
        return ranked[0], d

    # The user asked for the best heuristic *by node budget*. The 500-winner and the 1000-winner
    # need not be the same config -- EXP-06 showed the richer climb keeps converting budget into
    # solves while the leaner one plateaus -- so a winner is chosen and validated at each budget.
    per_budget = {}
    for budget in (500, 1000):
        a_tr, a_te = slice_at(budget)
        if ctrl not in a_tr or not a_tr[ctrl]:
            continue
        w, tr_dec = pick(a_tr)
        te_dec = set(decidable(a_te))
        per_budget[budget] = {
            "winner": w, "a_tr": a_tr, "a_te": a_te, "tr_dec": tr_dec, "te_dec": te_dec,
            "w_tr": dec_solved(a_tr, w, tr_dec), "b_tr": dec_solved(a_tr, ctrl, tr_dec),
            "w_te": dec_solved(a_te, w, te_dec), "b_te": dec_solved(a_te, ctrl, te_dec)}

    lines = [
        "# The heuristic — synthesis on the automorphism-disjoint split", "",
        "Selection and the held-out read both live inside `splits_aut.json`, where no automorphism "
        "class appears on both sides — so the held-out number is transfer to genuinely new problems, "
        "not memorised change-of-variables twins. **This measures decidable → decidable "
        "generalisation; the decidable → second-hump gap is not measurable at ≤1,000 nodes.**", "",
        "The winner is chosen and validated separately at each budget, because the best ordering "
        "at 500 nodes is not the best at 1,000 (EXP-06).", "",
        "## The recommendation, by node budget", "",
        "| budget | heuristic | aut_train decidable | aut_test decidable (held-out) |",
        "|---|---|---|---|",
    ]
    for budget, d in per_budget.items():
        lines.append(
            f"| **{budget}** | `{d['winner']}` | {d['w_tr']}/{len(d['tr_dec'])} "
            f"(baseline {d['b_tr']}/{len(d['tr_dec'])}) | **{d['w_te']}/{len(d['te_dec'])}** "
            f"(baseline {d['b_te']}/{len(d['te_dec'])}) |")
    lines.append("")

    for budget, d in per_budget.items():
        tr_gain, te_gain = d["w_tr"] - d["b_tr"], d["w_te"] - d["b_te"]
        verdict = (f"holds out of sample ({te_gain:+d} test vs {tr_gain:+d} train)"
                   if te_gain >= max(1, tr_gain * 0.5)
                   else f"shrinks out of sample ({te_gain:+d} test vs {tr_gain:+d} train) — "
                        "some of the training margin was selection")
        lines += [f"### Budget {budget}: `{d['winner']}`", "",
                  f"On held-out aut-classes the gain **{verdict}**. Per bin on the test slice "
                  "(floor bins shown so the gain is visibly in the hard bins, not the saturated ones):",
                  "", bin_table({ctrl: d["a_te"][ctrl], d["winner"]: d["a_te"].get(d["winner"], {})},
                                [ctrl, d["winner"]], ctrl), ""]

    with open(os.path.join(LOGS, "FINDINGS.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    with open(os.path.join(LOGS, "synthesis.json"), "w") as f:
        json.dump({"split": "aut_disjoint", "candidates": proposed,
                   "by_budget": {str(b): {"winner": d["winner"],
                                          "test_gain": d["w_te"] - d["b_te"],
                                          "train_gain": d["w_tr"] - d["b_tr"],
                                          "test_decidable": len(d["te_dec"]),
                                          "train_decidable": len(d["tr_dec"])}
                                 for b, d in per_budget.items()}}, f, indent=1)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
