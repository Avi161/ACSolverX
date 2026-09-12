"""Whitehead primitivity census of every U124 relator, one word at a time.

A single primitive relator in a unimodular balanced trivial-group pair would
give a stable-AC finish line after a stable Aut realization: the pair-length
μ-ladder can miss this because shrinking one relator to a generator may
lengthen the companion.

This script does not apply automorphisms to pairs and does not claim a solve.
Failure of the recognizer is not an obstruction.
"""

from __future__ import annotations

import csv
import json
import math
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.words import (  # noqa: E402
    abelian_det,
    cyc_reduce,
    exp_sums,
    free_reduce,
    inv,
)
from experiments.stable_ac.rank3_compression.rank3_whitehead import (  # noqa: E402
    check_word_reduction,
    is_primitive_word,
    reduce_word,
)

DATA = ROOT / "data" / "ms_unsolved_reps" / "aca_124_best.csv"
OUT = ROOT / "research" / "u124_stable_20260912" / "tables"

CONTROLS = {
    "generator_x": "x",
    "conjugate_xyx": "xyX",
    "commutator": "xyXY",
    "ak3_r1": "xxxYYYY",
    "ak3_r2": "xyxYXY",
    "ms_upper_donor": "YXXyxYx",
    "ms_lower_donor": "YXyXYxx",
}


def abelian_gcd(word: str) -> int:
    ex, ey = exp_sums(word)
    return math.gcd(abs(ex), abs(ey))


def reduce_f2(word: str):
    return reduce_word(free_reduce(word), generators=("x", "y"))


def serialize_reduction(result) -> dict[str, object]:
    return {
        "minimum_total": result.minimum_total,
        "minimum": result.minimum,
        "phi": result.phi,
        "n_steps": len(result.steps),
        "primitive": bool(is_primitive_word(result)),
    }


def product_cyclic(r1: str, r2: str, invert_second: bool) -> str:
    second = inv(r2) if invert_second else r2
    return cyc_reduce(r1 + second)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    control_rows = {}
    for name, word in CONTROLS.items():
        result = reduce_f2(word)
        check_word_reduction(word, result)
        control_rows[name] = serialize_reduction(result)

    if not control_rows["generator_x"]["primitive"]:
        raise AssertionError("control x is not primitive")
    if not control_rows["conjugate_xyx"]["primitive"]:
        raise AssertionError("control xyX is not primitive")
    if control_rows["commutator"]["primitive"]:
        raise AssertionError("commutator xyXY must not be primitive")
    if control_rows["ak3_r1"]["primitive"] or control_rows["ak3_r2"]["primitive"]:
        raise AssertionError("AK3 relators must not be primitive")

    with DATA.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 124:
        raise AssertionError(f"expected 124 rows, got {len(rows)}")

    relator_records = []
    primitive_hits = []
    min_hist = Counter()
    gcd_blocked = 0
    for row in rows:
        name = row["name"]
        pair = (row["r1"], row["r2"])
        if abs(abelian_det(*pair)) != 1:
            raise AssertionError(f"{name} is not unimodular")
        for which, word in (("r1", pair[0]), ("r2", pair[1])):
            agcd = abelian_gcd(word)
            record = {
                "id": f"{name}:{which}",
                "name": name,
                "which": which,
                "word": word,
                "length": len(word),
                "abelian_gcd": agcd,
            }
            if agcd != 1:
                gcd_blocked += 1
                record.update(
                    {
                        "minimum_total": None,
                        "minimum": None,
                        "phi": None,
                        "n_steps": 0,
                        "primitive": False,
                        "skipped": "abelian_gcd_ne_1",
                    }
                )
            else:
                result = reduce_f2(word)
                check_word_reduction(word, result)
                record.update(serialize_reduction(result))
                record["skipped"] = ""
                min_hist[result.minimum_total] += 1
                if record["primitive"]:
                    primitive_hits.append(record)
            relator_records.append(record)

        for invert_second, tag in ((False, "r1_r2"), (True, "r1_r2inv")):
            prod = product_cyclic(pair[0], pair[1], invert_second)
            agcd = abelian_gcd(prod)
            prod_rec = {
                "id": f"{name}:{tag}",
                "name": name,
                "which": tag,
                "word": prod,
                "length": len(prod),
                "abelian_gcd": agcd,
            }
            if not prod:
                prod_rec.update(
                    {
                        "minimum_total": 0,
                        "minimum": "",
                        "phi": None,
                        "n_steps": 0,
                        "primitive": False,
                        "skipped": "freely_trivial_product",
                    }
                )
            elif agcd != 1:
                prod_rec.update(
                    {
                        "minimum_total": None,
                        "minimum": None,
                        "phi": None,
                        "n_steps": 0,
                        "primitive": False,
                        "skipped": "abelian_gcd_ne_1",
                    }
                )
            else:
                result = reduce_f2(prod)
                check_word_reduction(prod, result)
                prod_rec.update(serialize_reduction(result))
                prod_rec["skipped"] = ""
            relator_records.append(prod_rec)

    donor_counts: Counter[str] = Counter()
    for row in rows:
        donor_counts[row["r1"]] += 1
        donor_counts[row["r2"]] += 1
    shared = [
        {"word": word, "count": count}
        for word, count in donor_counts.most_common()
        if count >= 3
    ]

    elapsed = time.perf_counter() - started
    summary = {
        "n_rows": 124,
        "n_relators": 248,
        "primitive_relators": len(primitive_hits),
        "primitive_hits": primitive_hits,
        "relator_min_length_histogram": {
            str(k): min_hist[k] for k in sorted(min_hist)
        },
        "abelian_gcd_blocked_relators": gcd_blocked,
        "controls": control_rows,
        "shared_relators_count_ge_3": shared,
        "elapsed_seconds": round(elapsed, 3),
        "status": "recognizer_census_not_a_solve",
        "note": (
            "A primitive relator is a sufficient stable-AC finish line only after "
            "an explicit stable realization of the witnessing automorphism and "
            "elementary elimination of the resulting generator. Zero hits here "
            "do not obstruct other routes."
        ),
    }
    out = OUT / "primitive_relator_census.json"
    payload = dict(summary)
    payload["records"] = relator_records
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "primitive_relators": summary["primitive_relators"],
                "relator_min_length_histogram": summary["relator_min_length_histogram"],
                "abelian_gcd_blocked_relators": gcd_blocked,
                "shared_relators_count_ge_3": [
                    f"{row['word']}:{row['count']}" for row in shared[:12]
                ],
                "elapsed_seconds": summary["elapsed_seconds"],
                "status": summary["status"],
            },
            indent=2,
        )
    )
    print("wrote", out)


if __name__ == "__main__":
    main()
