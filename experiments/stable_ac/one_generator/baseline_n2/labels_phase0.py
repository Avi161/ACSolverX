"""Phase 0 — per-presentation reference labels over MS(1190), index-derived (no compute).

Writes ``results/labels_1190.json``: one object per idx carrying the PAPER's claim
(solved = idx < 640; in the AC19_extended prefix = idx < 634 — the cross-verified
solved-first ordering) plus cheap structural fields. The empirical `greedy` field and
the JAX-gated `rl_610model`/`beam_610model` are left null here; they are filled later
by merging the Phase 0.5 streams / running the RL stack where JAX exists.

Run once (no compute):  python labels_phase0.py
"""
import argparse
import ast
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
DEFAULT_DATA = os.path.join(ROOT, "data", "1190MS.txt")
DEFAULT_OUT = os.path.join(ROOT, "results", "labels_1190.json")

INT_TO_CHAR = {1: "x", -1: "X", 2: "y", -2: "Y"}
L = 24
N_SOLVED = 640        # idx < 640 = paper's greedy-trivializable set
N_AC19_PREFIX = 634   # idx < 634 = the 100K-node solves seeding AC19_extended
PAPER_SOURCE = "GS-Sub greedy (paper Table 1: 634@100K, 640@1M/10M)"

_MS_R1 = re.compile(r"^Xy(y*)x(Y+)$")  # MS r1 = 'X'+'y'*n+'x'+'Y'*(n+1)


def flat_to_strs(flat):
    r1 = "".join(INT_TO_CHAR[i] for i in flat[:L] if i != 0)
    r2 = "".join(INT_TO_CHAR[i] for i in flat[L:] if i != 0)
    return r1, r2


def try_parse_ms(r1, r2):
    """Best-effort MS(n, w) recovery from the RAW stored strings. Most stored forms are
    canonicalised/rotated and won't match, so this returns (None, None) for those."""
    m = _MS_R1.match(r1)
    if m and r2.startswith("X"):
        n = 1 + len(m.group(1))            # 'y'*n  -> one 'y' + the captured extra y's
        if len(m.group(2)) == n + 1:       # 'Y'*(n+1)
            return n, r2[1:]
    return None, None


def build_labels(data_path):
    labels = []
    with open(data_path) as f:
        for idx, line in enumerate(f):
            line = line.strip()
            if not line:
                continue
            flat = ast.literal_eval(line)
            r1_len = sum(1 for v in flat[:L] if v != 0)
            r2_len = sum(1 for v in flat[L:] if v != 0)
            r1, r2 = flat_to_strs(flat)
            ms_n, ms_w = try_parse_ms(r1, r2)
            labels.append({
                "idx": idx,
                "presentation": flat,
                "r1_len": r1_len,
                "r2_len": r2_len,
                "ms_n": ms_n,
                "ms_w": ms_w,
                "paper_reference": {
                    "solved": idx < N_SOLVED,
                    "source": PAPER_SOURCE,
                    "in_ac19_extended_prefix": idx < N_AC19_PREFIX,
                },
                "greedy": None,        # filled at report time from the Phase 0.5 streams
                "rl_610model": None,   # filled where JAX + checkpoint exist
                "beam_610model": None,
            })
    return labels


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=DEFAULT_DATA)
    ap.add_argument("--out", default=DEFAULT_OUT)
    args = ap.parse_args()

    labels = build_labels(args.data)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(labels, f)

    n_solved = sum(1 for r in labels if r["paper_reference"]["solved"])
    n_ms = sum(1 for r in labels if r["ms_n"] is not None)
    print(f"OK: {len(labels)} labels -> {os.path.relpath(args.out, ROOT)}")
    print(f"    paper_reference.solved (idx<640): {n_solved}; ms_n recovered: {n_ms}")


if __name__ == "__main__":
    main()
