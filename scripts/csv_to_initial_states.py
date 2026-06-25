"""Phase 1: convert the greedy-solved CSV into env initial states + a join index.

Reads `data/all_presentations_len_8_to_19_GS_solved_copy2.csv` (one presentation
per row: r1, r2, Nodes Visited, Path Length, <flat path tokens...>) and writes:

  data/<stem>.txt          one Python-literal presentation per line (2*max_length
                           ints, x->1 X->-1 y->2 Y->-2, zero-padded) consumed by ACS
  data/<stem>_index.csv    line_idx, r1, r2, greedy_solved, greedy_path_length
                           so beam results join back to the original rows + labels

ALL rows are emitted (solved and greedy-unsolved alike): the greedy-unsolved
presentations are the highest-value new-solve targets for the beam search.

Self-validates gate G1 (line count, alphabet, round-trip) before declaring done.

Run from the repository root:
    python scripts/csv_to_initial_states.py
"""

import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import canon  # noqa: E402

VALID_CHARS = set("xXyY")


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument(
        "--csv", type=str,
        default="data/all_presentations_len_8_to_19_GS_solved_copy2.csv",
        help="source greedy CSV (read-only)")
    p.add_argument("--out_stem", type=str, default="greedy_all",
                   help="writes data/<stem>.txt and data/<stem>_index.csv")
    p.add_argument("--max_length", type=int, default=24,
                   help="per-relator padded length (env operating value)")
    return p.parse_args()


def main():
    args = parse_args()
    L = args.max_length

    if not os.path.exists(args.csv):
        raise SystemExit(f"CSV not found: {args.csv} (run from repo root?)")

    txt_path = os.path.join("data", f"{args.out_stem}.txt")
    idx_path = os.path.join("data", f"{args.out_stem}_index.csv")

    rows = []  # (line_idx, r1, r2, greedy_solved, greedy_path_length)
    literals = []

    with open(args.csv, "r", newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        if header[:4] != ["r1", "r2", "Nodes Visited", "Path Length"]:
            raise SystemExit(f"unexpected header: {header[:5]}")
        for i, tok in enumerate(reader):
            if not tok or all(c.strip() == "" for c in tok):
                continue  # skip blank trailing line
            r1, r2 = tok[0].strip(), tok[1].strip()
            path_len = int(tok[3])

            # G1 alphabet check
            if not r1 or not r2:
                raise SystemExit(f"row {i}: empty relator")
            bad = (set(r1) | set(r2)) - VALID_CHARS
            if bad:
                raise SystemExit(f"row {i}: bad chars {bad} in ({r1!r},{r2!r})")

            literal = canon.strs_to_presentation_literal(r1, r2, max_length=L)
            literals.append(literal)
            rows.append((len(rows), r1, r2, path_len >= 0, path_len))

    # ---- Write outputs ----
    with open(txt_path, "w") as f:
        for literal in literals:
            f.write(repr(literal) + "\n")

    with open(idx_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["line_idx", "r1", "r2", "greedy_solved", "greedy_path_length"])
        w.writerows(rows)

    n = len(rows)

    # ---- G1 validation gate ----
    failures = []
    # (a) line count matches the source data rows
    with open(txt_path) as f:
        n_txt = sum(1 for _ in f)
    if n_txt != n:
        failures.append(f"txt line count {n_txt} != rows {n}")

    # (b) every literal: correct length, no interior zeros within a relator's word,
    #     and round-trips back to the original (r1, r2)
    n_unsolved = 0
    for (li, r1, r2, solved, _pl), literal in zip(rows, literals):
        if not solved:
            n_unsolved += 1
        if len(literal) != 2 * L:
            failures.append(f"row {li}: literal len {len(literal)} != {2*L}")
            break
        back1, back2 = canon.env_state_to_strs(literal, max_length=L)
        if (back1, back2) != (r1, r2):
            failures.append(
                f"row {li}: round-trip ({back1!r},{back2!r}) != ({r1!r},{r2!r})")
            break
        a = canon.str_to_env_ints(r1)
        b = canon.str_to_env_ints(r2)
        if 0 in a or 0 in b:
            failures.append(f"row {li}: zero inside a relator word")
            break

    print(f"wrote {txt_path} and {idx_path}")
    print(f"rows: {n}  (greedy-solved {n - n_unsolved}, greedy-unsolved {n_unsolved})")
    print(f"numba available for canon: {canon.HAVE_NUMBA}")
    if failures:
        for msg in failures:
            print("  G1 FAIL:", msg)
        raise SystemExit("G1 validation FAILED")
    print("G1 PASS: line count, alphabet, length, and (r1,r2) round-trip all OK")


if __name__ == "__main__":
    main()
