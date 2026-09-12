"""Identity check for Family A (MS_TEMPLATE_PROPOSITION sibling).

P(n) = ⟨ y^{-1}x^{-2}y^{-1}xy^{-1}x^3, y^{-n}x^{-1}y^n x^{-2} y x^2 ⟩
claimed hops z1 = y x^{-2}, z2 = y x^2 y^{-1}
claimed Q(n) = ⟨ y^{-2} x^{-n} y x^2, y^{-2} x y x y x^{-1} y^{-1} x y x^{-1} ⟩

aca_43 is n=2 and aca_95 is n=3 on the archival initial table.
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.autcanon import aut_canon, aut_min_len  # noqa: E402
from experiments.equivalence_classes.lib.words import canon_pair, free_reduce  # noqa: E402
from experiments.greedy_tests.spec.words import str_to_word, word_to_str  # noqa: E402
from experiments.stable_ac.cov.cov import cov_branches  # noqa: E402

OUT = ROOT / "research" / "u124_stable_20260912" / "tables"


def parametric_p(n: int) -> tuple[str, str]:
    r1 = "YXXYxYxxx"
    r2 = "Y" * n + "X" + "y" * n + "XXyxx"
    return r1, r2


def claimed_q(n: int) -> tuple[str, str]:
    q1 = "YY" + "X" * n + "yxx"
    q2 = "YYxyxyXYxyX"
    return free_reduce(q1), free_reduce(q2)


def apply_cov(pair: tuple[str, str], z: str, iso_gen: str = "x"):
    branches = cov_branches(
        str_to_word(pair[0]),
        str_to_word(pair[1]),
        str_to_word(z),
        iso_gen=iso_gen,
    )
    return [
        {
            "iso_index": b.iso_index,
            "iso_gen": b.iso_gen,
            "n_subs": b.n_subs,
            "pair": (word_to_str(b.r1), word_to_str(b.r2)),
            "z": word_to_str(b.z_word),
        }
        for b in branches
    ]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    n_ok = 0
    n_fail = 0
    for n in range(2, 8):
        p = parametric_p(n)
        q = claimed_q(n)
        q_rep = aut_canon(q)[1]
        matched = None
        exact = False
        aut_match = False
        path = None
        for h1 in apply_cov(p, "yXX", iso_gen="x"):
            if h1["n_subs"] < 3:
                continue
            for h2 in apply_cov(h1["pair"], "yxxY", iso_gen="y"):
                if h2["n_subs"] < 2:
                    continue
                got = h2["pair"]
                if got == q or got == (q[1], q[0]):
                    matched, exact, aut_match, path = h2, True, True, (h1, h2)
                    break
                if aut_canon(got)[1] == q_rep:
                    matched, exact, aut_match, path = h2, False, True, (h1, h2)
                    break
            if matched:
                break
        rec = {
            "n": n,
            "P": list(p),
            "Q_claim": list(q),
            "matched": matched is not None,
            "exact_spelling": exact,
            "aut_min_match": aut_match,
            "mu_P": aut_min_len(p),
            "mu_Q": aut_min_len(q),
            "claimed_mu_P_2n_plus_15": 2 * n + 15,
            "claimed_mu_Q_n_plus_16": n + 16,
            "path": path,
        }
        rec["identities_ok"] = (
            aut_match
            and rec["mu_P"] == 2 * n + 15
            and rec["mu_Q"] == n + 16
        )
        records.append(rec)
        n_ok += int(rec["identities_ok"])
        n_fail += int(not rec["identities_ok"])
        print(
            f"n={n} aut_match={aut_match} exact={exact} "
            f"muP={rec['mu_P']} muQ={rec['mu_Q']}"
        )

    initial_path = ROOT / "data" / "ms_unsolved_reps" / "aca_124_initial.csv"
    with initial_path.open(newline="", encoding="utf-8") as handle:
        initial_rows = list(csv.DictReader(handle))
    hits = []
    for rec in records:
        target = canon_pair(*rec["P"])
        for row in initial_rows:
            if canon_pair(row["r1"], row["r2"]) == target:
                hits.append({"name": row["name"], "n": rec["n"], "initial": [row["r1"], row["r2"]]})
    summary = {
        "n_checked": len(records),
        "n_ok": n_ok,
        "n_fail": n_fail,
        "status": "PASS" if n_fail == 0 else "FAIL",
        "u124_initial_hits": hits,
        "caveat": "CoV identities, not elementary certificates or solves.",
    }
    path = OUT / "family_a_identities.json"
    path.write_text(json.dumps({"summary": summary, "rows": records}, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    if n_fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
