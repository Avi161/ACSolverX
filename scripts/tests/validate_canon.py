"""Phase 1 gate G2: confirm scripts/canon.py reproduces the validated P2-11 result.

Re-derives every on-path state from the greedy CSV (the eda.ipynb PREP-B
construction), canonicalizes each unique stored state via canon.canon_key, and
asserts:

  (1) the stored state strings are 1:1 with canonical_pair_nj classes
      (#unique stored == #unique canonical), and
  (2) within greedy data, every canonical class has a single greedy remaining-dot
      value (zero label disagreement) -- the eda.ipynb P0-3 finding.

Also round-trips a sample of initial pairs through the env-int8 bridge
(strs -> presentation literal -> strs) used in Phase 3.

Run from the repository root:
    python scripts/validate_canon.py
"""

import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))  # repo root
from scripts.lib import canon  # noqa: E402

CSV = "data/all_presentations_len_8_to_19_GS_solved_copy2.csv"


def main():
    if not os.path.exists(CSV):
        raise SystemExit(f"CSV not found: {CSV} (run from repo root?)")

    # stored_key "r1|r2" -> set of greedy remaining_dot values observed for it
    stored_to_dots = {}
    n_onpath = 0
    n_solved_rows = 0

    with open(CSV, "r", newline="") as f:
        reader = csv.reader(f)
        next(reader)  # header
        for tok in reader:
            if not tok or all(c.strip() == "" for c in tok):
                continue
            path_len = int(tok[3])
            if path_len < 0:
                continue  # greedy-unsolved: no path
            n_solved_rows += 1
            path = [t.strip() for t in tok[4:]]
            expected = 2 * (path_len + 1)
            if len(path) != expected:
                raise SystemExit(
                    f"path token count {len(path)} != 2*(PathLength+1)={expected}")
            for t in range(path_len + 1):
                r1, r2 = path[2 * t], path[2 * t + 1]
                key = r1 + "|" + r2
                rem = path_len - t
                stored_to_dots.setdefault(key, set()).add(rem)
                n_onpath += 1

    n_unique_stored = len(stored_to_dots)

    # Canonicalize each UNIQUE stored state once (memoized).
    stored_to_canon = {}
    canon_to_dots = {}
    for key, dots in stored_to_dots.items():
        r1, r2 = key.split("|")
        ckey, _tot = canon.canon_key(r1, r2)
        stored_to_canon[key] = ckey
        canon_to_dots.setdefault(ckey, set()).update(dots)

    n_unique_canon = len(set(stored_to_canon.values()))
    n_disagree = sum(1 for d in canon_to_dots.values() if len(d) > 1)

    print(f"on-path states (rows)      : {n_onpath}")
    print(f"solved presentations       : {n_solved_rows}")
    print(f"unique stored states       : {n_unique_stored}")
    print(f"unique canonical classes   : {n_unique_canon}")
    print(f"canonical classes w/ >1 dot: {n_disagree}")
    print(f"numba available for canon  : {canon.HAVE_NUMBA}")

    fail = []
    if n_unique_canon != n_unique_stored:
        fail.append(
            f"NOT 1:1: {n_unique_stored} stored vs {n_unique_canon} canonical")
    if n_disagree != 0:
        fail.append(f"{n_disagree} canonical classes have disagreeing greedy d-o-t")

    # Env-int8 bridge round-trip on a sample of initial pairs.
    sample = list(stored_to_dots.keys())[:2000]
    for key in sample:
        r1, r2 = key.split("|")
        if len(r1) > 24 or len(r2) > 24:
            continue  # only initial-scale words fit the env literal
        lit = canon.strs_to_presentation_literal(r1, r2, max_length=24)
        b1, b2 = canon.env_state_to_strs(lit, max_length=24)
        if (b1, b2) != (r1, r2):
            fail.append(f"env bridge round-trip failed on ({r1!r},{r2!r})")
            break

    if fail:
        for m in fail:
            print("  G2 FAIL:", m)
        raise SystemExit("G2 validation FAILED")
    print("G2 PASS: stored states 1:1 with canonical classes, zero d-o-t "
          "disagreement, env bridge round-trips")


if __name__ == "__main__":
    main()
