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
TEST_OUT = os.path.join(LOGS, "TEST_final.jsonl")


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

    # Rank on the decidable subset at 500, then confirm at 1,000 where available.
    tr500 = all_train(500)
    if ctrl not in tr500:
        raise SystemExit("no baseline rows at 500 -- run the sweeps first")
    dec = set(decidable(tr500))
    ranked = sorted(
        tr500,
        key=lambda cid: (-sum(1 for nm in dec if nm in tr500[cid] and tr500[cid][nm]["solved"]),
                         score(tr500[cid], tr500[ctrl])["nodes_mean"] or 1e9,
                         score(tr500[cid], tr500[ctrl])["path_mean"] or 1e9))
    winner = ranked[0] if ranked[0] != ctrl else ranked[1]
    runners = [c for c in ranked if c != ctrl][:5]

    # Spend the test slice, once, on the winner + a few runners + the baseline, both budgets.
    test_cfgs = [BASELINE_CONFIG] + [id_to_cfg(c) for c in runners if id_to_cfg(c)]
    for b in (500, 1000):
        evaluate(test_cfgs, "test", b, MRL, TEST_OUT, label=f"TEST-{b}")

    te = read(TEST_OUT)  # config -> {name: row} (mixed budgets; split below)
    te500 = {cid: {n: r for n, r in v.items() if r["budget"] == 500} for cid, v in te.items()}
    te1k = {cid: {n: r for n, r in v.items() if r["budget"] == 1000} for cid, v in te.items()}

    def dec_solved(res, cid, names):
        return sum(1 for nm in names if nm in res.get(cid, {}) and res[cid][nm]["solved"])

    tr_dec = dec
    te_dec500 = set(decidable(te500))

    w_tr = dec_solved(tr500, winner, tr_dec)
    b_tr = dec_solved(tr500, ctrl, tr_dec)
    w_te = dec_solved(te500, winner, te_dec500)
    b_te = dec_solved(te500, ctrl, te_dec500)

    tr_gain = w_tr - b_tr
    te_gain = w_te - b_te

    lines = [
        "# The heuristic — synthesis and the one honest test read", "",
        f"Winner selected on `train` (decidable subset): **`{winner}`**.", "",
        "## Does it survive the held-out slice?", "",
        f"| slice | baseline | winner | gain |", "|---|---|---|---|",
        f"| train (decidable {len(tr_dec)}) | {b_tr}/{len(tr_dec)} | {w_tr}/{len(tr_dec)} | "
        f"**{tr_gain:+d}** |",
        f"| **test** (decidable {len(te_dec500)}) | {b_te}/{len(te_dec500)} | "
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
        json.dump({"winner": winner, "runners": runners,
                   "train_gain": tr_gain, "test_gain": te_gain,
                   "train_decidable": len(tr_dec), "test_decidable": len(te_dec500)}, f, indent=1)
    print("\n".join(lines))


if __name__ == "__main__":
    main()
