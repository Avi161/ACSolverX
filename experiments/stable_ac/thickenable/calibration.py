"""Calibration + target runner for the thickenability checker.  [unverified]

The load-bearing part of the whole deliverable.  A checker whose verdicts we do
not trust is worth only as much as the ground-truth cases we can pin it against.
This module (a) runs the checker on presentations whose thickenability is KNOWN
from the literature / solid topology and reports pass/fail, and (b) runs it on
the actual open targets (AK(3), its orbit-2 rep, the 35 mu-floor reps, 5 aca
class reps), surfacing every verdict WITH the one-sided/[unverified] caveats and
the SUSPECTED-BUG guard on any positive.

Honesty notes that fall out of the calibration (see run at bottom):
  * The POSITIVE side is validated: trivial-collapse, the torus (commutator),
    the trefoil-complement spine (a non-trivial-group 3-manifold spine), and
    RP^2 (embeds in the orientable RP^3) all read THICKENABLE correctly.
  * The NEGATIVE side is validated ONLY by a >=3-generator non-planar-link case
    (Whitehead graph = K3,3).  A citeable BALANCED 2-GENERATOR non-thickenable
    example is not established in the literature (memo (d)), so in the
    2-generator regime the checker is ONE-SIDED-CALIBRATED: its NOT_THICKENABLE
    verdicts there (including AK(3)'s) are unvalidated.
  * The specific reversal SIGN of the tube coupling (the single riskiest rule)
    is NOT distinguished by any calibration case: reverse and same-order give
    identical verdicts on every case here.  Calibration validates the coupling
    STRUCTURE (it is load-bearing -- it flips figure-8-ish YES->NO and makes
    AK(3) tractable), not the sign.  => do not trust a positive.
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass

from experiments.stable_ac.thickenable.check_thickenable import (
    Presentation,
    Verdict,
    check,
    check_strings,
)


def _repo_root() -> str:
    d = os.path.abspath(os.path.dirname(__file__))
    while True:
        if os.path.isdir(os.path.join(d, "experiments")) and os.path.isdir(
            os.path.join(d, "data")
        ):
            return d
        parent = os.path.dirname(d)
        if parent == d:
            raise RuntimeError("repo root (experiments/ + data/) not found")
        d = parent


# ---------------------------------------------------------------------------
# calibration cases: (label, r1, r2, expected_thickenable, ground-truth source)
# expected_thickenable: True / False.  TRIVIAL_COLLAPSE and THICKENABLE both
# count as True; NOT_THICKENABLE as False; UNKNOWN_SIZE never appears here.
# ---------------------------------------------------------------------------
@dataclass
class Case:
    label: str
    r1: str
    r2: str | None
    expected: bool
    source: str
    n_gen: int = 2


CALIBRATION: list[Case] = [
    # --- POSITIVE: thickenable, trivial group ---------------------------------
    Case("std <x,y|x,y>", "x", "y", True,
         "Lackenby 3.1 / memo hand-check: len-1 relators cancel, N(K)=B^3"),
    Case("std <x|x>", "x", None, True,
         "Lackenby 1: standard one-generator presentation is thickenable", 1),
    # --- POSITIVE: non-degenerate, thickenable --------------------------------
    Case("commutator <x,y|[x,y]>", "xyXY", None, True,
         "presentation complex = torus T^2, and T^2 embeds in S^3", 2),
    Case("trefoil spine <x,y|xyx=yxy>", "xyxYXY", None, True,
         "spine of the trefoil-knot complement (a 3-manifold): thickenable; "
         "non-trivial group -> guards the 'trivial' assumption", 2),
    Case("RP^2 <x|x^2>", "xx", None, True,
         "presentation complex = RP^2, which embeds (1-sided) in the "
         "orientable 3-manifold RP^3", 1),
    # --- NEGATIVE: not thickenable (>=3 gens, non-planar link) -----------------
    Case("K3,3-link <x,y,z|XXYXZYYZZ>", "XXYXZYYZZ", None, False,
         "Whitehead graph = K3,3 (non-planar link) -> cannot embed in ANY "
         "3-manifold (Carmesin I / van Kampen obstruction). SOLID ground truth. "
         "3-generator: exercises the general-n planarity path, NOT a 2-gen "
         "negative", 3),
]

# A citeable BALANCED 2-GENERATOR not-thickenable example is MISSING from the
# literature (memo (d)); the negative row above is 3-generator by necessity.
NEGATIVE_2GEN_STATUS = "MISSING (no citeable balanced 2-generator non-thickenable example)"


def run_calibration(max_rotations: int = 2_000_000) -> list[tuple[Case, Verdict, bool]]:
    rows = []
    for c in CALIBRATION:
        v = check(
            Presentation.from_strings(c.r1, c.r2, name=c.label, n_gen=c.n_gen),
            max_rotations=max_rotations,
        )
        got = v.thickenable
        ok = (got is True) == c.expected if got is not None else False
        rows.append((c, v, ok))
    return rows


def print_calibration_table(rows) -> bool:
    print("=" * 100)
    print("CALIBRATION  (ground-truth cases)   [ALL VERDICTS UNVERIFIED pending Regina]")
    print("=" * 100)
    print(f"{'case':<34}{'expected':<14}{'got':<20}{'OK':<5}")
    print("-" * 100)
    all_ok = True
    for c, v, ok in rows:
        exp = "THICKENABLE" if c.expected else "NOT_thickenable"
        print(f"{c.label:<34}{exp:<14}{v.status:<20}{'PASS' if ok else 'FAIL':<5}")
        all_ok = all_ok and ok
    print("-" * 100)
    print(f"negative 2-generator calibration: {NEGATIVE_2GEN_STATUS}")
    print(f"=> checker is ONE-SIDED-CALIBRATED in the 2-generator regime "
          f"(positives anchored; 2-gen negatives unvalidated).")
    print("sources:")
    for c, _, _ in rows:
        print(f"  - {c.label}: {c.source}")
    print("=" * 100)
    return all_ok


# ---------------------------------------------------------------------------
# target list
# ---------------------------------------------------------------------------
AK3 = ("AK(3)", "xxxYYYY", "xyxYXY")
AK3_ORBIT2 = ("AK(3)-orbit2", "YYXXyx", "YYYxyXX")


def load_floor_reps() -> list[tuple[str, str, str]]:
    path = os.path.join(_repo_root(), "data", "ms_unsolved_reps", "mu_floors_r8.csv")
    out = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            out.append((row["name"], row["r1"], row["r2"]))
    return out


def load_aca_reps(n: int = 5) -> list[tuple[str, str, str]]:
    path = os.path.join(_repo_root(), "data", "ms_unsolved_reps", "aca_124.csv")
    out = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            out.append((row["name"], row["r1"], row["r2"]))
    return out[:n]


def run_targets(max_rotations: int = 2_000_000) -> list[Verdict]:
    targets = [AK3, AK3_ORBIT2]
    targets += load_floor_reps()
    targets += load_aca_reps(5)
    verdicts = []
    for name, r1, r2 in targets:
        # mark_open: force the open-problem guard on for every target list entry
        v = check_strings(r1, r2, name=name, max_rotations=max_rotations, mark_open=True)
        verdicts.append(v)
    return verdicts


def print_targets(verdicts) -> None:
    print()
    print("=" * 100)
    print("TARGETS  (AK(3), orbit-2 rep, 35 mu-floor reps, 5 aca class reps)")
    print("  [unverified] -- a NEGATIVE settles nothing (one-sided payoff); a")
    print("  POSITIVE on any of these is a SUSPECTED BUG, never a result claim.")
    print("=" * 100)
    print(f"{'target':<20}{'r1|r2':<32}{'verdict':<20}{'search cost':<14}")
    print("-" * 100)
    suspected = 0
    for v in verdicts:
        flag = ""
        if v.thickenable:
            flag = "  <<< SUSPECTED BUG (do NOT claim)"
            suspected += 1
        cost = f"{v.rotation_cost:.2g}" if v.rotation_cost else "-"
        print(f"{v.presentation:<20}{'':<32}{v.status:<20}{cost:<14}{flag}")
    print("-" * 100)
    n_not = sum(1 for v in verdicts if v.status == "NOT_THICKENABLE")
    n_unk = sum(1 for v in verdicts if v.status == "UNKNOWN_SIZE")
    n_thick = sum(1 for v in verdicts if v.thickenable)
    print(f"summary: {len(verdicts)} targets -> {n_not} NOT_THICKENABLE, "
          f"{n_unk} UNKNOWN_SIZE (prototype size limit, NOT a NO), "
          f"{n_thick} THICKENABLE")
    if suspected:
        print(f"!! {suspected} THICKENABLE verdict(s) on open-problem inputs -- "
              f"SUSPECTED BUG in the [unverified] rotation rule. NOT a result.")
    else:
        print("no THICKENABLE verdicts on the targets (expected: negatives are "
              "inconclusive; the search simply found no genus-0 rotation, or hit "
              "the size cap).")
    print("=" * 100)


if __name__ == "__main__":
    rows = run_calibration()
    print_calibration_table(rows)
    verdicts = run_targets()
    print_targets(verdicts)
