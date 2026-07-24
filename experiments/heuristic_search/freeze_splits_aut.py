"""Freeze an automorphism-disjoint train/test split -- no aut_class on both sides.

The first split (``splits.json``) stratified by difficulty bin but let automorphism classes leak:
six classes (87, 93, 97, 99, 106, 108) had members in both train and test, and they cluster in
the hard ladder rows -- exactly where generalisation is being measured. Two presentations in the
same class are the same problem up to a change of variables (``Aut(F2)``, exact), so a config that
solves the train member can solve the test twin for free, and the held-out number is inflated by
whatever share of it is memorised twins rather than transfer.

This split assigns **whole classes** to one side. Difficulty is still stratified -- within each
bin the classes are shuffled (seeded) and split ~2:1 -- so both sides span the range, but no class
is ever divided. A class that spans two bins is placed by its lowest bin, and classes with a lone
member in a sparse bin still go entirely to one side.

The result measures **decidable -> decidable** generalisation across genuinely distinct problems.
It does *not* measure the decidable -> second-hump gap, which is unmeasurable at these budgets;
that distinction is stated wherever a number from this split is reported.

Write-once, like the original: a seed is fixed and the file refuses to overwrite, so the split
cannot drift under re-runs.

    python3 -m experiments.heuristic_search.freeze_splits_aut
"""
import collections
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import numpy as np                                                 # noqa: E402
from experiments.heuristic_search.hlab import LOGS, bench66        # noqa: E402

SEED = 20260723
OUT = os.path.join(LOGS, "splits_aut.json")
TEST_FRACTION = 1 / 3


def build():
    rows = bench66()
    ladder = [r for r in rows if r["source"] == "ladder"]
    reach = [r["name"] for r in rows if r["source"] == "reach"]

    by_class = collections.defaultdict(list)
    class_bin = {}
    for r in ladder:
        c = int(r["aut_class"])
        by_class[c].append(r["name"])
        b = int(r["bin"])
        class_bin[c] = min(class_bin.get(c, b), b)   # a multi-bin class sits at its easiest bin

    bins = collections.defaultdict(list)
    for c in by_class:
        bins[class_bin[c]].append(c)

    rng = np.random.default_rng(SEED)
    train, test = [], []
    for b in sorted(bins):
        classes = sorted(bins[b])                    # deterministic before the seeded shuffle
        rng.shuffle(classes)
        n_test = int(round(len(classes) * TEST_FRACTION))
        # Every bin with >=2 classes contributes to both sides; a lone-class bin goes to train.
        n_test = min(max(n_test, 1 if len(classes) > 1 else 0), len(classes) - 1) if len(classes) > 1 else 0
        for i, c in enumerate(classes):
            (test if i < n_test else train).extend(sorted(by_class[c]))

    return sorted(train), sorted(test), sorted(reach), by_class, class_bin


def main():
    if os.path.exists(OUT):
        raise SystemExit(f"{OUT} exists -- the split is frozen and must not be regenerated")

    train, test, reach, by_class, class_bin = build()

    # Assert the property the whole point rests on: no class on both sides.
    def classes_of(names):
        s = set()
        for r in bench66():
            if r["name"] in names and r["source"] == "ladder":
                s.add(int(r["aut_class"]))
        return s
    leak = classes_of(train) & classes_of(test)
    assert not leak, f"aut_class leak: {sorted(leak)}"

    payload = {
        "seed": SEED, "kind": "aut_disjoint",
        "train": train, "test": test, "reach": reach,
        "note": ("whole automorphism classes on one side only; decidable->decidable "
                 "generalisation, NOT decidable->second-hump"),
        "n_train": len(train), "n_test": len(test), "n_reach": len(reach),
        "train_classes": sorted(classes_of(train)), "test_classes": sorted(classes_of(test)),
    }
    with open(OUT, "w") as f:
        json.dump(payload, f, indent=1)

    print(f"train {len(train)}  test {len(test)}  reach {len(reach)}")
    print(f"train classes {len(payload['train_classes'])}  "
          f"test classes {len(payload['test_classes'])}  leak none")
    print("test:", test)


if __name__ == "__main__":
    main()
