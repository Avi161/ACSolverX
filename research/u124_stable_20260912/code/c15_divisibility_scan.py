"""C15 divisibility probes: AC3 by y-powers, and Whitehead images.

Asks whether every y-run length in the companion ``YXXXyxYx`` (or an
image) is a multiple of the BS parameter m. A yes would make Britton's
syllable hypothesis an identity problem. A no is a recognizer/orientation
negative for these exact moves, not an AC obstruction.

Not a heap search. Not a U124 solve.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.autcanon import AUTOS  # noqa: E402
from experiments.equivalence_classes.lib.words import (  # noqa: E402
    apply_hom,
    cyc_reduce,
    free_reduce,
    inv,
)

CODE = Path(__file__).resolve().parent
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))
from u124_census import syllables  # noqa: E402

OUT = ROOT / "research" / "u124_stable_20260912" / "tables"

DONOR = "YXXXyxYx"

# Compact companions from C15, m inferred from the y^m block after rotation.
ROWS = (
    ("aca_18", "YYYYxyyyX", 3),
    ("aca_20", "YYYYXyyyx", 3),
    ("aca_40", "YYYYYxyyyyX", 4),
    ("aca_42", "YYYYYXyyyyx", 4),
    ("aca_63", "YYYYYYxyyyyyX", 5),
    ("aca_65", "YYYYYYXyyyyyx", 5),
    ("aca_91", "YYYYYYYXyyyyyyx", 6),
    ("aca_93", "YYYYYYYxyyyyyyX", 6),
    ("aca_102", "YYYYYYYYxyyyyyyyX", 7),
    ("aca_104", "YYYYYYYYXyyyyyyyx", 7),
)


def y_run_lengths(word: str) -> list[int]:
    return [abs(exp) for gen, exp in syllables(word) if gen == "y"]


def all_divisible(word: str, m: int) -> bool:
    runs = y_run_lengths(word)
    return bool(runs) and all(length % m == 0 for length in runs)


def conjugate_by_ypower(word: str, k: int) -> str:
    if k == 0:
        return free_reduce(word)
    conjugator = ("y" * k) if k > 0 else ("Y" * (-k))
    return free_reduce(inv(conjugator) + word + conjugator)


def cyclic_orientations(word: str) -> list[str]:
    reduced = cyc_reduce(word)
    out = []
    seen = set()
    for base in (reduced, inv(reduced)):
        for k in range(len(base) or 1):
            rot = base[k:] + base[:k] if base else ""
            if rot not in seen:
                seen.add(rot)
                out.append(rot)
    return out


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    # Identity: y^{-(m-1)} W y^{m-1} starts with y^{-m} but keeps length-1 interiors.
    identity_rows = []
    for m in range(3, 8):
        conjugated = conjugate_by_ypower(DONOR, m - 1)
        identity_rows.append(
            {
                "m": m,
                "k": m - 1,
                "conjugated": conjugated,
                "y_runs": y_run_lengths(conjugated),
                "all_divisible_by_m": all_divisible(conjugated, m),
            }
        )
        if conjugated != free_reduce(
            ("Y" * m) + "XXX" + "yxYx" + ("y" * (m - 1))
        ) and conjugated != free_reduce("Y" * m + "XXXyxYx" + "y" * (m - 1)):
            # Keep the scan honest: record spelling, do not require one normal form.
            pass

    ac3_hits = []
    cyclic_hits = []
    aut_hits = []
    for name, companion, m in ROWS:
        for k in range(-(m + 2), m + 3):
            word = cyc_reduce(conjugate_by_ypower(DONOR, k))
            if all_divisible(word, m):
                ac3_hits.append(
                    {
                        "id": name,
                        "m": m,
                        "k": k,
                        "word": word,
                        "y_runs": y_run_lengths(word),
                    }
                )
        for rot in cyclic_orientations(DONOR):
            if all_divisible(rot, m):
                cyclic_hits.append(
                    {"id": name, "m": m, "word": rot, "y_runs": y_run_lengths(rot)}
                )
        for auto in AUTOS:
            image_donor = cyc_reduce(apply_hom(DONOR, auto))
            image_comp = cyc_reduce(apply_hom(companion, auto))
            if all_divisible(image_donor, m) or all_divisible(image_comp, m):
                aut_hits.append(
                    {
                        "id": name,
                        "m": m,
                        "phi": auto,
                        "image_donor": image_donor,
                        "image_companion": image_comp,
                        "donor_runs": y_run_lengths(image_donor),
                        "companion_runs": y_run_lengths(image_comp),
                        "donor_divisible": all_divisible(image_donor, m),
                        "companion_divisible": all_divisible(image_comp, m),
                    }
                )

    summary = {
        "donor": DONOR,
        "n_rows": len(ROWS),
        "ypower_identity": identity_rows,
        "n_ac3_ypower_hits": len(ac3_hits),
        "ac3_ypower_hits": ac3_hits,
        "n_cyclic_orientation_hits": len(cyclic_hits),
        "cyclic_orientation_hits": cyclic_hits,
        "n_whitehead_hits": len(aut_hits),
        "whitehead_hits": aut_hits[:40],
        "status": "divisibility_probe_not_a_solve",
        "note": (
            "Hits mean every y-run length is a multiple of m after the named "
            "move class. Zero hits rule out that exact orientation/Aut list, "
            "not every Britton-clearing construction."
        ),
    }
    path = OUT / "c15_divisibility_scan.json"
    path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "n_rows": summary["n_rows"],
                "ypower_identity_any_divisible": any(
                    row["all_divisible_by_m"] for row in identity_rows
                ),
                "n_ac3_ypower_hits": len(ac3_hits),
                "n_cyclic_orientation_hits": len(cyclic_hits),
                "n_whitehead_hits": len(aut_hits),
                "sample_m3_conjugate": identity_rows[0],
                "status": summary["status"],
            },
            indent=2,
        )
    )
    print("wrote", path)


if __name__ == "__main__":
    main()
