"""Freeze the train / test / reach slices of the 66-row benchmark. Run ONCE, then never again.

Every number this research program reports is either selected on ``train`` or read on ``test``,
and the split has to exist before the first evaluation or "held out" means nothing. The file it
writes is committed; regenerating it after seeing results would silently reshuffle which
presentations were held out, so the script refuses to overwrite.

The 60 ladder rows are stratified 4/2 within each of the 10 difficulty bins. Unstratified would
be worse than useless here: only a fraction of the 60 solve at these budgets, so a split that
happened to take four easy bins would move the achievable score by more than any heuristic does.

The 6 reach rows are held apart entirely. They are open problems -- none will solve at 1,000
nodes -- so they cannot join a solve-count split; they get scored on ``min_total`` against their
``bar_to_beat`` as a progress measure, once, at the end.

    python3 -m experiments.heuristic_search.freeze_splits
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from experiments.heuristic_search.hlab import LOGS, bench66      # noqa: E402

SEED = 20260723
OUT = os.path.join(LOGS, "splits.json")


def main():
    if os.path.exists(OUT):
        print(f"{OUT} already exists -- refusing to overwrite a frozen split.")
        return
    import numpy as np
    rng = np.random.default_rng(SEED)

    rows = bench66()
    ladder = [r for r in rows if r["source"] == "ladder"]
    reach = [r for r in rows if r["source"] == "reach"]

    bins = {}
    for r in ladder:
        bins.setdefault(r["bin"], []).append(r["name"])

    train, test = [], []
    for b in sorted(bins):
        names = sorted(bins[b])
        rng.shuffle(names)
        k = len(names) // 3                       # 2 of every 6 -> a 40/20 split overall
        test += names[:k]
        train += names[k:]

    out = {
        "seed": SEED,
        "source": "results/benchmark/combined/benchmark_combined_66.json",
        "policy": ("train is the ONLY slice any configuration may be selected on; test is read "
                   "once, at the end, and never used to choose anything; reach rows are open "
                   "problems scored on min_total vs bar_to_beat, not on solves"),
        "stratification": "4 train / 2 test within each of the 10 difficulty bins",
        "train": sorted(train),
        "test": sorted(test),
        "reach": sorted(r["name"] for r in reach),
    }
    os.makedirs(LOGS, exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(out, f, indent=1)
    print(f"train {len(train)}  test {len(test)}  reach {len(reach)}  -> {OUT}")


if __name__ == "__main__":
    main()
