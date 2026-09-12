"""Recognizer aggregates requested by the C12 audit.

1. Count primitivity of the already-computed cyclic products in
   primitive_relator_census.json (no new Whitehead).
2. Whitehead-test unique new relators among depth-1 AC2 children of the
   best table. A miss is a bounded report, not an obstruction.
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

from experiments.equivalence_classes.lib.words import canon_rel, exp_sums  # noqa: E402
from experiments.stable_ac.rank3_compression.rank3_whitehead import (  # noqa: E402
    check_word_reduction,
    is_primitive_word,
    reduce_word,
)

CODE = Path(__file__).resolve().parent
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))
from elementary_ac2_scan import children  # noqa: E402

DATA = ROOT / "data" / "ms_unsolved_reps" / "aca_124_best.csv"
TABLES = ROOT / "research" / "u124_stable_20260912" / "tables"
CENSUS = TABLES / "primitive_relator_census.json"
OUT = TABLES / "primitive_aggregates.json"


def abelian_gcd(word: str) -> int:
    ex, ey = exp_sums(word)
    return math.gcd(abs(ex), abs(ey))


def product_aggregate(census: dict) -> dict[str, object]:
    by_which = Counter()
    primitive_by_which = Counter()
    skipped_by_which = Counter()
    hits = []
    for rec in census["records"]:
        which = rec["which"]
        by_which[which] += 1
        if rec.get("primitive"):
            primitive_by_which[which] += 1
            hits.append(
                {
                    "id": rec["id"],
                    "word": rec["word"],
                    "minimum": rec.get("minimum"),
                }
            )
        skipped = rec.get("skipped") or ""
        if skipped:
            skipped_by_which[f"{which}:{skipped}"] += 1
    return {
        "n_records_by_which": dict(by_which),
        "primitive_by_which": dict(primitive_by_which),
        "skipped_by_which": dict(skipped_by_which),
        "primitive_hits": hits,
        "n_product_records": by_which["r1_r2"] + by_which["r1_r2inv"],
        "n_product_primitive": primitive_by_which["r1_r2"]
        + primitive_by_which["r1_r2inv"],
        "n_relator_primitive": primitive_by_which["r1"] + primitive_by_which["r2"],
        "note": (
            "Product rows are the cyclically reduced stored-orientation "
            "words r1 r2 and r1 r2^{-1}, not Aut-orbit representatives."
        ),
    }


def depth1_unique_words(rows: list[dict[str, str]]) -> tuple[dict[str, str], int]:
    original_canons = {
        canon_rel(word) for row in rows for word in (row["r1"], row["r2"])
    }
    unique: dict[str, str] = {}
    n_children = 0
    for row in rows:
        kids = children(row["r1"], row["r2"])
        n_children += len(kids)
        for a, b, _move in kids:
            for word in (a, b):
                key = canon_rel(word)
                if key in original_canons or key in unique:
                    continue
                unique[key] = word
    return unique, n_children


def main() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    census = json.loads(CENSUS.read_text(encoding="utf-8"))
    products = product_aggregate(census)
    with DATA.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    unique, n_children = depth1_unique_words(rows)
    gcd_blocked = 0
    primitive_hits = []
    min_hist = Counter()
    tested = 0
    for word in unique.values():
        agcd = abelian_gcd(word)
        if agcd != 1:
            gcd_blocked += 1
            continue
        result = reduce_word(word, generators=("x", "y"))
        check_word_reduction(word, result)
        tested += 1
        min_hist[result.minimum_total] += 1
        if is_primitive_word(result):
            primitive_hits.append(
                {
                    "word": word,
                    "minimum": result.minimum,
                    "phi": result.phi,
                    "n_steps": len(result.steps),
                }
            )
    elapsed = time.perf_counter() - started
    summary = {
        "products": products,
        "depth1": {
            "n_children_enumerated": n_children,
            "n_unique_new_relators": len(unique),
            "n_abelian_gcd_blocked": gcd_blocked,
            "n_whitehead_tested": tested,
            "n_primitive": len(primitive_hits),
            "primitive_hits": primitive_hits,
            "min_length_histogram": {str(k): min_hist[k] for k in sorted(min_hist)},
            "note": (
                "Unique freely/cyclically reduced relators that appear as an "
                "AC2 child and are not one of the 248 stored best-table "
                "relators. A zero here is a bounded recognizer report."
            ),
        },
        "elapsed_seconds": round(elapsed, 3),
        "status": "recognizer_aggregates_not_a_solve",
    }
    OUT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "n_relator_primitive": products["n_relator_primitive"],
                "n_product_primitive": products["n_product_primitive"],
                "n_unique_new_relators": summary["depth1"]["n_unique_new_relators"],
                "n_depth1_primitive": summary["depth1"]["n_primitive"],
                "depth1_min_histogram": summary["depth1"]["min_length_histogram"],
                "elapsed_seconds": summary["elapsed_seconds"],
                "status": summary["status"],
            },
            indent=2,
        )
    )
    print("wrote", OUT)


if __name__ == "__main__":
    main()
