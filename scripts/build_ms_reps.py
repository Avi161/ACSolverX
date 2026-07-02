"""Build the loadable unsolved-representatives dataset from the mentor's CSV.

Input : data/ms_unsolved_reps/ms_reps_unsolved.csv  (columns: r1, r2, name) — one AC-equivalence
        -class representative per row for each of the 261 unsolved Miller--Schupp classes.
Output: data/ms_unsolved_reps/ms_reps_unsolved.txt  — env-format flat presentations, one Python-literal
        list per line, length 2*L = 48, zero-padded. Line i corresponds to CSV row i, so the row
        order IS the idx and the CSV doubles as the idx -> class-name label.

Word convention (matches greedy_search.ipynb's char_to_array and the env's signed ints):
    x -> 1, X -> -1, y -> 2, Y -> -2.

Run from anywhere:  python scripts/build_ms_reps.py
"""
import ast
import csv
import os

L = 24
WORD2INT = {"x": 1, "X": -1, "y": 2, "Y": -2}
INT2WORD = {v: k for k, v in WORD2INT.items()}

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data", "ms_unsolved_reps")
CSV_IN = os.path.join(DATA, "ms_reps_unsolved.csv")
TXT_OUT = os.path.join(DATA, "ms_reps_unsolved.txt")


def word_to_ints(w):
    return [WORD2INT[c] for c in w]


def pad(rel):
    assert len(rel) <= L, f"relator length {len(rel)} exceeds L={L}"
    return rel + [0] * (L - len(rel))


def main():
    rows = []
    with open(CSV_IN, newline="") as f:
        for r1, r2, name in csv.reader(f):
            if (r1, r2, name) == ("r1", "r2", "name"):
                continue  # header
            rows.append((r1, r2, name))

    lines = []
    for r1, r2, name in rows:
        flat = pad(word_to_ints(r1)) + pad(word_to_ints(r2))
        lines.append(flat)

    with open(TXT_OUT, "w") as f:
        for flat in lines:
            f.write(repr(flat) + "\n")

    # ---- self-verification ----
    with open(TXT_OUT) as f:
        parsed = [ast.literal_eval(ln) for ln in f if ln.strip()]
    assert len(parsed) == len(rows) == 261, f"row count {len(parsed)} != 261"
    for (r1, r2, name), flat in zip(rows, parsed):
        assert len(flat) == 2 * L == 48, f"{name}: len {len(flat)} != 48"
        assert all(v in (-2, -1, 0, 1, 2) for v in flat), f"{name}: bad symbol"
        back1 = "".join(INT2WORD[v] for v in flat[:L] if v != 0)
        back2 = "".join(INT2WORD[v] for v in flat[L:] if v != 0)
        assert back1 == r1, f"{name}: r1 round-trip {back1!r} != {r1!r}"
        assert back2 == r2, f"{name}: r2 round-trip {back2!r} != {r2!r}"
    print(f"OK: wrote {len(parsed)} presentations -> {os.path.relpath(TXT_OUT, ROOT)}")
    print(f"     round-trip verified against {os.path.relpath(CSV_IN, ROOT)}")


if __name__ == "__main__":
    main()
