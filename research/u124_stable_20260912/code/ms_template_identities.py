"""Independent free-group check of the MS two-hop template.

Re-derives hop z=xy then z=x^n through ``cov.cov_branches`` for both signs and
n in a finite range, compares the output to the claimed normal form Q_{n,δ},
and applies the claimed automorphism y ↦ x^{-2} y.

This is an identity check, not an AC-move expansion and not a U124 solve.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.autcanon import aut_min_len  # noqa: E402
from experiments.equivalence_classes.lib.words import (  # noqa: E402
    apply_hom,
    canon_pair,
    cyc_reduce,
    free_reduce,
)
from experiments.greedy_tests.spec.words import str_to_word, word_to_str  # noqa: E402
from experiments.stable_ac.cov.cov import cov_branches  # noqa: E402

OUT = ROOT / "research" / "u124_stable_20260912" / "tables"


def parametric_p(n: int, delta: int) -> tuple[str, str]:
    r1 = "Y" + "X" * 3 + ("y" if delta == 1 else "Y") + "x" * 2
    r2 = "Y" * (n + 1) + "X" + "y" * n + "x"
    return r1, r2


def claimed_q(n: int, delta: int) -> tuple[str, str]:
    """Literal Q_{n,δ} from MS_TEMPLATE_PROPOSITION.md.

    R1 = x^{-1} y^{-1} x y x^2 y x^δ y^{-1} x^{-2}
    R2 = y^{-1} x^2 y x^{nδ} y^{-1} x^{-2}
    """
    xd = "x" if delta == 1 else "X"
    q1 = "XYxyxxy" + xd + "YXX"
    q2 = "Yxxy" + xd * n + "YXX"
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


def same_orbit_pair(a: tuple[str, str], b: tuple[str, str]) -> bool:
    return canon_pair(a[0], a[1]) == canon_pair(b[0], b[1])


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    records = []
    n_ok = 0
    n_fail = 0
    for delta in (-1, 1):
        for n in range(2, 9):
            p = parametric_p(n, delta)
            hop1 = apply_cov(p, "xy", iso_gen="x")
            hop1_keep = [h for h in hop1 if h["n_subs"] >= 2]
            q_claim = claimed_q(n, delta)
            matched = None
            path = None
            exact = False
            for h1 in hop1_keep:
                hop2 = apply_cov(h1["pair"], "x" * n, iso_gen="x")
                hop2_keep = [h for h in hop2 if h["n_subs"] >= 2]
                for h2 in hop2_keep:
                    got = h2["pair"]
                    if got == q_claim or got == (q_claim[1], q_claim[0]):
                        matched = h2
                        path = (h1, h2)
                        exact = True
                        break
                    if same_orbit_pair(got, q_claim):
                        matched = h2
                        path = (h1, h2)
                        exact = False
                        break
                if matched:
                    break
            # automorphism y -> x^{-2} y
            img = {"x": "x", "y": "XXy"}
            q_auto = (
                apply_hom(q_claim[0], img),
                apply_hom(q_claim[1], img),
            )
            auto_len = len(cyc_reduce(q_auto[0])) + len(cyc_reduce(q_auto[1]))
            mu_auto = aut_min_len(q_auto)
            rec = {
                "n": n,
                "delta": delta,
                "P": list(p),
                "P_length": len(p[0]) + len(p[1]),
                "hop1_branches_nsubs_ge2": hop1_keep,
                "matched_Q_exactly": exact,
                "matched_Q_up_to_rotation_inversion": matched is not None,
                "Q_claim": list(q_claim),
                "Q_claim_length": len(q_claim[0]) + len(q_claim[1]),
                "Q_after_y_to_XXy_cyclic_total": auto_len,
                "Q_after_y_to_XXy_aut_min_len": mu_auto,
                "claimed_mu_bound_n_plus_12": n + 12,
                "auto_len_le_n_plus_12": auto_len <= n + 12,
                "mu_auto_le_n_plus_12": mu_auto <= n + 12,
                "hop1_iso": path[0] if path else None,
                "hop2_iso": path[1] if path else None,
            }
            ok = (
                rec["matched_Q_exactly"]
                and rec["auto_len_le_n_plus_12"]
                and rec["mu_auto_le_n_plus_12"]
            )
            rec["identities_ok"] = ok
            records.append(rec)
            if ok:
                n_ok += 1
            else:
                n_fail += 1
            print(
                f"n={n} δ={delta:+d} exact={rec['matched_Q_exactly']} "
                f"auto_len={auto_len} mu={mu_auto} bound={n+12} P={p[0]}|{p[1]}"
            )

    # Map U124 initial rows onto parametric P_{n,δ} up to rotation/inversion.
    import csv

    initial_path = ROOT / "data" / "ms_unsolved_reps" / "aca_124_initial.csv"
    u124_hits = []
    with initial_path.open(newline="", encoding="utf-8") as handle:
        initial_rows = list(csv.DictReader(handle))
    for rec in records:
        target = canon_pair(*rec["P"])
        for row in initial_rows:
            if canon_pair(row["r1"], row["r2"]) == target:
                u124_hits.append(
                    {
                        "name": row["name"],
                        "n": rec["n"],
                        "delta": rec["delta"],
                        "initial": [row["r1"], row["r2"]],
                    }
                )
    summary = {
        "n_checked": len(records),
        "n_ok": n_ok,
        "n_fail": n_fail,
        "status": "PASS" if n_fail == 0 else "FAIL",
        "u124_initial_exact_P_hits": u124_hits,
        "caveat": (
            "cov_branches implements gated subword CoV, which is a Lemma-11 "
            "composite on a trivial-group presentation, not an elementary "
            "certificate. Matching Q does not trivialize U124."
        ),
    }
    payload = {"summary": summary, "rows": records}
    path = OUT / "ms_template_identities.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if n_fail:
        sys.exit(1)


if __name__ == "__main__":
    main()
