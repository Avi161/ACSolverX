"""Phase 1 gate A: the move sets behave as claimed. No search yet.

  1. ``seam`` reproduces ``expand_node_nj`` exactly (same child set).
  2. ``full`` is a strict superset of ``seam``.
  3. ``full`` is inverse-closed on samples: P in children(children(P)).  ``seam`` is not.
  4. The trivial pair (x, y) is a SINK under ``seam`` and is not under ``full``.
"""
import csv
import os
import random
import sys

# The repo root, found by walking up rather than by counting directory levels. A
# dirname chain encodes this file's depth, so it silently repoints at the wrong
# directory the moment the file moves -- and every path below is then wrong.
def _repo_root():
    d = os.path.dirname(os.path.abspath(__file__))
    while d != os.path.dirname(d):
        if (os.path.isdir(os.path.join(d, "experiments"))
                and os.path.isdir(os.path.join(d, "data"))):
            return d
        d = os.path.dirname(d)
    raise RuntimeError("repo root (holding experiments/ and data/) not found")


ROOT = _repo_root()
sys.path.insert(0, ROOT)

from experiments.equivalence_classes.lib.acmoves import canon, children  # noqa: E402
from experiments.search.greedy_baseline import (  # noqa: E402
    canonical_pair_nj, expand_node_nj, reduce_relator_nj, str_to_arr,
)

CAP = 48
_CHR = {1: "X", 2: "Y", 3: "x", 4: "y"}


def baseline_children(r1s, r2s, cap=CAP):
    a1 = reduce_relator_nj(str_to_arr(r1s), True)
    a2 = reduce_relator_nj(str_to_arr(r2s), True)
    c1, c2 = canonical_pair_nj(a1, a2)
    codes, lens, moves, n = expand_node_nj(c1, c2, cap, True)
    out = set()
    for i in range(n):
        la, lb = int(lens[i, 0]), int(lens[i, 1])
        out.add(("".join(_CHR[c] for c in codes[i, :la]),
                 "".join(_CHR[c] for c in codes[i, la:la + lb])))
    return out


def main():
    with open(os.path.join(ROOT, "data", "ms_unsolved_reps", "ms_reps_unsolved.csv")) as f:
        reps = [(r["r1"], r["r2"], r["name"]) for r in csv.DictReader(f)]
    rng = random.Random(0)
    sample = rng.sample(reps, 30)

    # 1 + 2
    bad_eq = bad_sup = 0
    seam_sizes, full_sizes = [], []
    for (r1, r2, _) in sample:
        base = baseline_children(r1, r2)
        seam = set(children(r1, r2, cap=CAP, seam_only=True))
        full = set(children(r1, r2, cap=CAP, seam_only=False))
        if seam != base:
            bad_eq += 1
        if not (seam < full):
            bad_sup += 1
        seam_sizes.append(len(seam))
        full_sizes.append(len(full))
    print(f"[1] seam == expand_node_nj on 30 reps : {bad_eq == 0} ({bad_eq} mismatches)")
    print(f"[2] seam STRICT subset of full        : {bad_sup == 0} ({bad_sup} failures)")
    print(f"    mean children/node  seam={sum(seam_sizes)/30:.1f}  full={sum(full_sizes)/30:.1f}"
          f"  (cap={CAP})")

    # 3 -- inverse closure
    for label, seam_only in (("seam", True), ("full", False)):
        closed = total = 0
        for (r1, r2, _) in sample[:10]:
            P = canon(r1, r2)
            kids = list(children(*P, cap=CAP, seam_only=seam_only))
            for c in kids[:12]:
                total += 1
                if P in children(*c, cap=CAP, seam_only=seam_only):
                    closed += 1
        pct = 100.0 * closed / max(total, 1)
        print(f"[3] {label}: P recoverable from its child in one move: {closed}/{total} ({pct:.0f}%)")

    # 4 -- the trivial pair
    for label, seam_only in (("seam", True), ("full", False)):
        k = children("x", "y", cap=CAP, seam_only=seam_only)
        print(f"[4] trivial (x, y) children under {label}: {len(k)}"
              f"{'   <-- SINK' if not k else '   e.g. ' + str(sorted(k)[:3])}")


if __name__ == "__main__":
    main()
