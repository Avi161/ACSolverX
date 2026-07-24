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

    aut = read(AUT_OUT)
    tr_names = {r["name"] for r in load_split("aut_train")}
    te_names = {r["name"] for r in load_split("aut_test")}
    a_tr500 = {cid: {n: r for n, r in v.items() if n in tr_names and r["budget"] == 500}
               for cid, v in aut.items()}
    a_te500 = {cid: {n: r for n, r in v.items() if n in te_names and r["budget"] == 500}
               for cid, v in aut.items()}

    # 3) Choose the winner on aut_train's decidable subset.
    tr_dec = set(decidable(a_tr500))
    ranked = sorted(
        (c for c in a_tr500 if c != ctrl),
        key=lambda cid: (-sum(1 for nm in tr_dec if a_tr500[cid].get(nm, {}).get("solved")),
                         score(a_tr500[cid], a_tr500[ctrl])["nodes_mean"] or 1e9,
                         score(a_tr500[cid], a_tr500[ctrl])["path_mean"] or 1e9))
    winner = ranked[0]

    def dec_solved(res, cid, names):
        return sum(1 for nm in names if nm in res.get(cid, {}) and res[cid][nm]["solved"])

    te_dec500 = set(decidable(a_te500))
    w_tr = dec_solved(a_tr500, winner, tr_dec)
    b_tr = dec_solved(a_tr500, ctrl, tr_dec)
    w_te = dec_solved(a_te500, winner, te_dec500)
    b_te = dec_solved(a_te500, ctrl, te_dec500)
    tr_gain = w_tr - b_tr
    te_gain = w_te - b_te
    te500 = a_te500

    lines = [
        "# The heuristic — synthesis on the automorphism-disjoint split", "",
        "Selection and the held-out read both live inside `splits_aut.json`, where no automorphism "
        "class appears on both sides — so the held-out number is transfer to genuinely new problems, "
        "not memorised change-of-variables twins. **This measures decidable → decidable "
        "generalisation; the decidable → second-hump gap is not measurable at ≤1,000 nodes.**", "",
        f"Winner, chosen on `aut_train` (decidable subset): **`{winner}`**.", "",
        "## Does it survive the held-out aut-classes?", "",
        f"| slice | baseline | winner | gain |", "|---|---|---|---|",
        f"| aut_train (decidable {len(tr_dec)}) | {b_tr}/{len(tr_dec)} | {w_tr}/{len(tr_dec)} | "
        f"**{tr_gain:+d}** |",
        f"| **aut_test** (decidable {len(te_dec500)}) | {b_te}/{len(te_dec500)} | "
        f"{w_te}/{len(te_dec500)} | **{te_gain:+d}** |", "",
    ]
    if te_gain >= max(1, tr_gain * 0.5):
        lines += [f"The gain holds out of sample ({te_gain:+d} on test vs {tr_gain:+d} on train): "
                  "the ordering is picking up a real property of these presentations, not fitting "
                  "the training forty.", ""]
    else:
        lines += [f"**The gain shrinks out of sample** ({te_gain:+d} on test vs {tr_gain:+d} on "
                  "train): some of the training margin was selection. Trust the test number as the "
                  "estimate of what this heuristic buys on unseen presentations.", ""]

    # Per-bin on test at 500, winner + baseline, so the headline is never the saturated 40-denom.
    lines += ["## Where the test-slice solves land (per bin)", "",
              bin_table({ctrl: te500[ctrl], winner: te500.get(winner, {})},
                        [ctrl, winner], ctrl), ""]

    with open(os.path.join(LOGS, "FINDINGS.md"), "w") as f:
        f.write("\n".join(lines) + "\n")
    with open(os.path.join(LOGS, "synthesis.json"), "w") as f:
        json.dump({"winner": winner, "candidates": proposed,
                   "train_gain": tr_gain, "test_gain": te_gain,
                   "train_decidable": len(tr_dec), "test_decidable": len(te_dec500),
                   "split": "aut_disjoint"}, f, indent=1)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
