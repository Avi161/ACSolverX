"""Elementary AC1+AC2+AC3 deletion of a generator relator from its companion.

Given a pair ``(x, s)``, every displayed ``x^{±1}`` in ``s`` is removed by
the conjugated-donor sequence from advisor_wave2:

If ``s = p x^ε q``, change the first relator ``x`` by AC1/AC3 to
``q^{-1} x^{-ε} q``, multiply the companion by that donor (AC2), then
restore the first relator.

This is not a Tietze substitution and does not use Lemma 11. It does not
by itself prove C12: the ambient automorphism that produced ``(x, s)`` is
C1 and remains non-effective.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.words import (  # noqa: E402
    abelian_det,
    exp_sums,
    free_reduce,
    inv,
)

OUT = ROOT / "research" / "u124_stable_20260912" / "tables"


def conjugate(word: str, conjugator: str) -> str:
    return free_reduce(inv(conjugator) + word + conjugator)


def first_x(word: str) -> tuple[int, int] | None:
    for index, letter in enumerate(word):
        if letter.lower() == "x":
            return index, 1 if letter.islower() else -1
    return None


def letter(eps: int) -> str:
    if eps == 1:
        return "x"
    if eps == -1:
        return "X"
    raise ValueError(f"eps must be ±1, got {eps}")


def delete_one_x(pair: tuple[str, str]) -> tuple[tuple[str, str], list[dict[str, str]]]:
    """One displayed deletion. First relator must freely reduce to x or X."""
    r1, s = pair
    r1 = free_reduce(r1)
    s = free_reduce(s)
    if r1 not in ("x", "X"):
        raise ValueError(f"first relator must be x or X, got {r1!r}")
    hit = first_x(s)
    if hit is None:
        raise ValueError("companion has no displayed x")
    index, eps = hit
    prefix, suffix = s[:index], s[index + 1 :]
    moves: list[dict[str, str]] = []
    current_first = r1
    if current_first == "x" and eps == 1:
        current_first = "X"
        moves.append({"ac": "AC1", "on": "r1", "to": current_first})
    elif current_first == "X" and eps == -1:
        current_first = "x"
        moves.append({"ac": "AC1", "on": "r1", "to": current_first})
    # Now current_first is x^{-ε}. Conjugate by suffix: suffix^{-1} x^{-ε} suffix.
    donor = conjugate(current_first, suffix)
    if donor != current_first:
        moves.append(
            {
                "ac": "AC3",
                "on": "r1",
                "conjugator": suffix,
                "to": donor,
            }
        )
        current_first = donor
    expected_donor = free_reduce(inv(suffix) + letter(-eps) + suffix)
    if current_first != expected_donor:
        raise AssertionError(
            f"donor spelling {current_first!r} != {expected_donor!r}"
        )
    new_s = free_reduce(s + current_first)
    expected_s = free_reduce(prefix + suffix)
    if new_s != expected_s:
        raise AssertionError(f"AC2 identity failed: {new_s!r} != {expected_s!r}")
    moves.append({"ac": "AC2", "on": "r2", "times": "r1", "to": new_s})
    # Restore first relator to x by undoing AC3 then AC1.
    restored = current_first
    if suffix:
        restored = conjugate(restored, inv(suffix))
        moves.append(
            {
                "ac": "AC3",
                "on": "r1",
                "conjugator": inv(suffix),
                "to": restored,
            }
        )
    if restored == "X":
        restored = "x"
        moves.append({"ac": "AC1", "on": "r1", "to": restored})
    if restored != "x":
        raise AssertionError(f"failed to restore generator x, got {restored!r}")
    return (restored, new_s), moves


def delete_all_x(s: str) -> dict[str, object]:
    pair = ("x", free_reduce(s))
    all_moves: list[dict[str, str]] = []
    steps = 0
    while first_x(pair[1]) is not None:
        pair, moves = delete_one_x(pair)
        all_moves.extend(moves)
        steps += 1
        if steps > 64:
            raise RuntimeError("deletion did not terminate")
    leftover = pair[1]
    ey = exp_sums(leftover)[1]
    return {
        "input": free_reduce(s),
        "leftover": leftover,
        "y_exponent": ey,
        "steps": steps,
        "n_moves": len(all_moves),
        "moves": all_moves,
        "terminal_is_y_pm1": leftover in ("y", "Y"),
        "det_if_paired_with_x": abelian_det("x", free_reduce(s)),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cases = {
        "already_y": "y",
        "yx": "yx",
        "xy": "xy",
        "Yx": "Yx",
        "xY": "xY",
        "yxYxy": "yxYxy",  # y-exponent +1, mixed x
        "xyXYy": "xyXYy",  # commutator times y, y-exponent +1
        "YxyXY": "YxyXY",  # inverse-first mixed, y-exponent -1
        "xxYx": "xxYx",
    }
    rows = []
    for name, word in cases.items():
        rec = delete_all_x(word)
        rec["id"] = name
        det = rec["det_if_paired_with_x"]
        if abs(det) == 1 and not rec["terminal_is_y_pm1"]:
            raise AssertionError(f"{name}: unimodular but leftover {rec['leftover']!r}")
        if rec["leftover"] and rec["leftover"].lower().strip("y") != "":
            raise AssertionError(f"{name}: leftover is not a y-word: {rec['leftover']!r}")
        rows.append(rec)
    # Negative control: y-exponent 0 should leave empty or y^0 after deleting x.
    zero = delete_all_x("xyXY")
    if zero["leftover"] != "":
        raise AssertionError(f"commutator leftover {zero['leftover']!r}")
    rows.append({"id": "commutator_xyXY", **zero})
    summary = {
        "n_cases": len(rows),
        "unimodular_finish_at_y_pm1": [
            row["id"] for row in rows if abs(row["det_if_paired_with_x"]) == 1
        ],
        "rows": rows,
        "status": "elementary_replay_not_a_u124_solve",
        "note": (
            "This replays only C12 step 4, after the pair is already (x, s). "
            "The Aut that produces that pair is C1 and is not expanded here."
        ),
    }
    path = OUT / "c12_generator_deletion.json"
    path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "n_cases": summary["n_cases"],
                "unimodular_finish_at_y_pm1": summary["unimodular_finish_at_y_pm1"],
                "status": summary["status"],
            },
            indent=2,
        )
    )
    print("wrote", path)


if __name__ == "__main__":
    main()
