"""Hash-verify U124 tables and emit the living 124-row status table.

Cheap recognizers only: exponent sums, syllable type, one-occurrence, two-block
shape, BS(m,m+1)-shaped donor, MS-floor shape. No heap search.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
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

DATA = ROOT / "data" / "ms_unsolved_reps"
OUT = ROOT / "research" / "u124_stable_20260912"
TABLES = OUT / "tables"

FILES = {
    "aca_124.csv": "archival_on_proofs_branch",
    "aca_124_initial.csv": "archival_initial",
    "aca_124_best.csv": "best_known_input",
    "aca_124_reduced.csv": "reduction_ledger",
    "README_aca_124.md": "schema_notes",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_pairs(path: Path) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return {row["name"]: row for row in csv.DictReader(handle)}


def syllables(word: str) -> list[tuple[str, int]]:
    word = free_reduce(word)
    if not word:
        return []
    runs: list[tuple[str, int]] = []
    letter = word[0].lower()
    sign = 1 if word[0].islower() else -1
    length = 1
    for char in word[1:]:
        gen = char.lower()
        s = 1 if char.islower() else -1
        if gen == letter and s == sign:
            length += 1
        else:
            runs.append((letter, sign * length))
            letter, sign, length = gen, s, 1
    runs.append((letter, sign * length))
    return runs


def one_occurrence_cyclic(word: str) -> bool:
    reduced = cyc_reduce(word)
    for spelling in (reduced, inv(reduced)):
        for offset in range(len(spelling) or 1):
            rot = spelling[offset:] + spelling[:offset] if spelling else ""
            if rot.lower().count("x") == 1 or rot.lower().count("y") == 1:
                return True
    return False


def two_block_shape(word: str) -> bool:
    """True if some cyclic orientation is a product of two pure generator powers."""
    reduced = cyc_reduce(word)
    if not reduced:
        return False
    for spelling in (reduced, inv(reduced)):
        n = len(spelling)
        for offset in range(n):
            rot = spelling[offset:] + spelling[:offset]
            runs = syllables(rot)
            if len(runs) == 2 and runs[0][0] != runs[1][0]:
                return True
    return False


def bs_mm1_shape(word: str) -> tuple[bool, int | None]:
    """Recognize b^{-1} a^m b a^{-(m+1)} up to rotation and inversion, m>=1."""
    reduced = cyc_reduce(word)
    if not reduced:
        return False, None
    for spelling in (reduced, inv(reduced)):
        n = len(spelling)
        for offset in range(n):
            runs = syllables(spelling[offset:] + spelling[:offset])
            if len(runs) != 4:
                continue
            (g0, e0), (g1, e1), (g2, e2), (g3, e3) = runs
            if g0 == g2 and g1 == g3 and g0 != g1 and abs(e0) == 1 and abs(e2) == 1 and e0 == -e2:
                if e1 * e3 < 0 and abs(abs(e1) - abs(e3)) == 1:
                    return True, min(abs(e1), abs(e3))
    return False, None


def ms_floor_match(r1: str, r2: str) -> dict[str, object] | None:
    """Match Aut-minimal MS-template floors from MS_TEMPLATE_PROPOSITION.md."""
    for a, b in ((r1, r2), (r2, r1)):
        if a == "YXXyxYx":
            # Y^n X y^2 x^2
            if b.startswith("Y") and b.endswith("Xyyxx"):
                n = len(b) - 5
                if n >= 2 and set(b[:n]) == {"Y"}:
                    return {"shape": "upper", "n": n, "delta": -1}
            # also YYYYXyyxx etc already covered
        if a == "YXyXYxx":
            # Y^n X^2 Y^2 x
            if "XXYYx" in b and b.endswith("XXYYx") and set(b[: -5]) <= {"Y"}:
                n = len(b) - 5
                if n >= 2 and set(b[:n]) == {"Y"}:
                    return {"shape": "lower", "n": n, "delta": 1}
    return None


def parametric_p(n: int, delta: int) -> tuple[str, str]:
    r1 = "Y" + "X" * 3 + ("y" if delta == 1 else "Y") + "x" * 2
    r2 = "Y" * (n + 1) + "X" + "y" * n + "x"
    return r1, r2


def main() -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for name, role in FILES.items():
        path = DATA / name
        digest = sha256(path)
        manifest[name] = {
            "role": role,
            "sha256": digest,
            "bytes": path.stat().st_size,
            "exists": True,
        }
        print(f"{digest}  {name}  {role}")

    initial = load_pairs(DATA / "aca_124_initial.csv")
    best = load_pairs(DATA / "aca_124_best.csv")
    proofs = load_pairs(DATA / "aca_124.csv")
    reduced = load_pairs(DATA / "aca_124_reduced.csv")

    assert set(initial) == set(best) == set(proofs) == set(reduced)
    assert len(initial) == 124
    assert {k: (initial[k]["r1"], initial[k]["r2"]) for k in initial} == {
        k: (proofs[k]["r1"], proofs[k]["r2"]) for k in proofs
    }

    init_total = sum(len(r["r1"]) + len(r["r2"]) for r in initial.values())
    best_total = sum(len(r["r1"]) + len(r["r2"]) for r in best.values())
    n_changed = sum(
        1
        for name in initial
        if (initial[name]["r1"], initial[name]["r2"])
        != (best[name]["r1"], best[name]["r2"])
    )
    mu_floor = sum(1 for row in reduced.values() if row.get("reduce_kind") == "mu_floor")
    assert n_changed == 36 == mu_floor
    assert init_total == 2446
    assert best_total == 2356

    # leftover 10M used the initial table (same hash as aca_124.csv)
    leftover_short = {
        "aca_36": (18, 17),
        "aca_55": (19, 18),
        "aca_78": (21, 19),
        "aca_88": (23, 21),
        "aca_99": (25, 22),
        "aca_100": (25, 22),
        "aca_105": (25, 24),
        "aca_106": (25, 24),
        "aca_107": (25, 22),
        "aca_109": (25, 23),
        "aca_110": (25, 22),
        "aca_111": (25, 23),
        "aca_113": (25, 23),
        "aca_114": (25, 23),
    }

    floors = {}
    floors_path = DATA / "mu_floors_r8.csv"
    if floors_path.exists():
        with floors_path.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                src = row["source_class"]
                floors[src] = row

    rows_out = []
    feature_counts = Counter()
    ms_hits = []
    for name in sorted(initial, key=lambda s: int(s.split("_")[1])):
        r1_i, r2_i = initial[name]["r1"], initial[name]["r2"]
        r1_b, r2_b = best[name]["r1"], best[name]["r2"]
        len_i = len(r1_i) + len(r2_i)
        len_b = len(r1_b) + len(r2_b)
        det_b = abelian_det(r1_b, r2_b)
        ex1, ey1 = exp_sums(r1_b)
        ex2, ey2 = exp_sums(r2_b)
        occ = one_occurrence_cyclic(r1_b) or one_occurrence_cyclic(r2_b)
        tb = two_block_shape(r1_b) and two_block_shape(r2_b)
        bs1, m1 = bs_mm1_shape(r1_b)
        bs2, m2 = bs_mm1_shape(r2_b)
        bs = bs1 or bs2
        ms = ms_floor_match(r1_b, r2_b)
        if occ:
            feature_counts["one_occurrence_best"] += 1
        if tb:
            feature_counts["two_block_both_best"] += 1
        if bs:
            feature_counts["bs_mm1_donor_best"] += 1
        if abs(det_b) == 1:
            feature_counts["unimodular_best"] += 1
        if ms:
            feature_counts["ms_floor_shape_best"] += 1
            ms_hits.append({"name": name, **ms, "r1": r1_b, "r2": r2_b})

        observed_ordinary = leftover_short.get(name)
        # leftover 10M stored no paths: observed, not certified
        certified_ordinary = len_i  # no replayed ordinary certificate on file
        certified_stable = None
        if name in floors:
            certified_stable = int(floors[name]["mu"])
        status_row = {
            "id": name,
            "archival_initial_length": len_i,
            "best_known_input_length": len_b,
            "best_certified_ordinary_ac_length": certified_ordinary,
            "best_certified_stable_ac_length": certified_stable if certified_stable is not None else "",
            "max_stable_rank_used": 3 if name in floors else "",
            "solved": "unsolved",
            "route_theorem": (
                "ms_template_floor" if ms else
                ("mu_floor_r8" if name in floors else "none")
            ),
            "certificate_status": (
                "mu_chain_recorded_pending_orbit_replay"
                if name in floors else
                "no_certificate"
            ),
            "r1_best": r1_b,
            "r2_best": r2_b,
            "r1_initial": r1_i,
            "r2_initial": r2_i,
            "n_members": initial[name]["n_members"],
            "abelian_det_best": det_b,
            "exp_r1_best": f"{ex1},{ey1}",
            "exp_r2_best": f"{ex2},{ey2}",
            "one_occurrence_best": int(occ),
            "two_block_both_best": int(tb),
            "bs_mm1_donor_best": int(bs),
            "bs_m": m1 or m2 or "",
            "ms_floor_shape": json.dumps(ms) if ms else "",
            "leftover_10m_observed_min_total": observed_ordinary[1] if observed_ordinary else "",
            "leftover_10m_observed_is_certified": "no",
            "reduce_kind": reduced[name].get("reduce_kind", ""),
        }
        rows_out.append(status_row)

    fieldnames = list(rows_out[0].keys())
    out_csv = TABLES / "u124_status.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_out)

    panels = {
        "development": sorted(
            {hit["name"] for hit in ms_hits}
            | {"aca_43", "aca_95", "aca_115", "aca_117", "aca_36", "aca_0"}
        ),
        "note": (
            "Development panel is the MS-template family, its sibling Family A, "
            "AK(3) tripwire aca_115, n=2 wall aca_117, and two generic rows. "
            "Do not quote holdout numbers as independent validation of rules "
            "invented on development."
        ),
    }
    remaining = [name for name in sorted(initial, key=lambda s: int(s.split("_")[1])) if name not in panels["development"]]
    panels["validation"] = remaining[::2]
    panels["holdout"] = remaining[1::2]
    (TABLES / "panels.json").write_text(json.dumps(panels, indent=2) + "\n", encoding="utf-8")

    summary = {
        "n_rows": 124,
        "initial_total_length": init_total,
        "best_total_length": best_total,
        "n_mu_floor_best": n_changed,
        "solved": 0,
        "hashes": manifest,
        "proofs_aca_124_equals_initial": True,
        "leftover_10m_table": "initial/archival, not best",
        "leftover_10m_solved": 0,
        "leftover_10m_observed_shorter_uncertified": 14,
        "theorem_strength_supermoves_10k_on_best": {"solved": 0, "shorter": 0},
        "feature_counts_on_best": dict(feature_counts),
        "ms_floor_hits": ms_hits,
        "missing_sources": [
            "codex/theory-patterns-3h",
            "research/theory_patterns_20260912",
            "literature/proofs/PROOFS.tex",
            "research/supermoves_20260908/FINAL_START_HERE.md",
        ],
    }
    (TABLES / "census_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({k: summary[k] for k in (
        "n_rows", "initial_total_length", "best_total_length",
        "n_mu_floor_best", "feature_counts_on_best", "solved"
    )}, indent=2))
    print("wrote", out_csv)


if __name__ == "__main__":
    main()
