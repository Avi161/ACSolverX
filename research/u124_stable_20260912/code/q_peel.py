"""Elementary common-suffix peel on Q_{n,δ} and Family A Q(n).

These are free-group identities realized by AC1+AC2 (and AC3 only if a
cyclic orientation is chosen first). They are not U124 solves.

The adjoining-t catalyst that replaces the common tail v by a new generator
and then isolates t reproduces the same peeled pair; it is not a return to
the original pair, and it is unnecessary once the elementary multiply is
written down.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.words import (  # noqa: E402
    cyc_reduce,
    free_reduce,
    inv,
)

OUT = ROOT / "research" / "u124_stable_20260912" / "tables"

G = "XYxyxxy"  # x^{-1} y^{-1} x y x^2 y
U = "Yxxy"  # y^{-1} x^2 y
V = "YXX"  # y^{-1} x^{-2}
COMM = "YXyx"  # [y^{-1}, x^{-1}] = y^{-1} x^{-1} y x


def q_pair(n: int, delta: int) -> tuple[str, str]:
    xd = "x" if delta == 1 else "X"
    return free_reduce(G + xd + V), free_reduce(U + xd * n + V)


def family_a_q(n: int) -> tuple[str, str]:
    return free_reduce("YY" + "X" * n + "yxx"), free_reduce("YYxyxyXYxyX")


def peel_suffix(r1: str, r2: str) -> str:
    """R2 * R1^{-1} after free reduction. Cancels a common suffix."""
    return free_reduce(r2 + inv(r1))


def claimed_peel(n: int, delta: int) -> str:
    xd = "x" if delta == 1 else "X"
    if n < 1:
        raise ValueError("n must be at least 1")
    return free_reduce(U + xd * (n - 1) + inv(G))


def power_block_length(word: str, letter: str = "x") -> int:
    """Longest consecutive run of letter^{±1} in a freely reduced word."""
    reduced = free_reduce(word)
    best = 0
    run = 0
    prev = ""
    for char in reduced:
        if char.lower() != letter:
            best = max(best, run)
            run = 0
            prev = ""
            continue
        if not prev or char == prev:
            run += 1
            prev = char
        else:
            best = max(best, run)
            run = 1
            prev = char
    return max(best, run)


def cyclic_v_power_times_v_free(word: str, v: str) -> dict[str, object] | None:
    """True if some cyclic conjugate is v^{±m} * (v-free) or the reverse, m>=1."""
    reduced = cyc_reduce(word)
    n = len(reduced)
    if not v or n == 0:
        return None
    orientations = [reduced[i:] + reduced[:i] for i in range(n)]
    orientations += [inv(w) for w in orientations]
    v_inv = inv(v)
    for spelling in orientations:
        for block, name in ((v, "v"), (v_inv, "v_inv")):
            m = 0
            rest = spelling
            while rest.startswith(block):
                rest = rest[len(block) :]
                m += 1
            if m >= 1 and block not in rest and inv(block) not in rest:
                return {
                    "form": f"{name}^{m} * v_free",
                    "m": m,
                    "v_free": rest,
                    "orientation": spelling,
                }
            m = 0
            rest = spelling
            while rest.endswith(block):
                rest = rest[: -len(block)]
                m += 1
            if m >= 1 and block not in rest and inv(block) not in rest:
                return {
                    "form": f"v_free * {name}^{m}",
                    "m": m,
                    "v_free": rest,
                    "orientation": spelling,
                }
    return None


def syllable_two_block(word: str) -> bool:
    reduced = cyc_reduce(word)
    if not reduced:
        return False
    for spelling in (reduced, inv(reduced)):
        for offset in range(len(spelling)):
            rot = spelling[offset:] + spelling[:offset]
            runs = []
            letter = rot[0].lower()
            sign = 1 if rot[0].islower() else -1
            length = 1
            for char in rot[1:]:
                gen = char.lower()
                s = 1 if char.islower() else -1
                if gen == letter and s == sign:
                    length += 1
                else:
                    runs.append((letter, sign * length))
                    letter, sign, length = gen, s, 1
            runs.append((letter, sign * length))
            if len(runs) == 2 and runs[0][0] != runs[1][0]:
                return True
    return False


def check_q_identities() -> list[dict[str, object]]:
    records = []
    g_inv = inv(G)
    if free_reduce(g_inv) != free_reduce(V + COMM):
        raise AssertionError("g^{-1} != v [y^{-1},x^{-1}]")
    if free_reduce(COMM) != "YXyx":
        raise AssertionError("commutator spelling drifted")

    for delta in (-1, 1):
        for n in range(2, 9):
            r1, r2 = q_pair(n, delta)
            peeled = peel_suffix(r1, r2)
            claimed = claimed_peel(n, delta)
            with_comm = free_reduce(
                U + ("x" if delta == 1 else "X") * (n - 1) + V + COMM
            )
            second = peel_suffix(r1, peeled)
            v_shape_r1 = cyclic_v_power_times_v_free(r1, V)
            rec = {
                "family": "Q",
                "n": n,
                "delta": delta,
                "r1": r1,
                "r2": r2,
                "input_length": len(r1) + len(r2),
                "peeled_r2": peeled,
                "peeled_length": len(r1) + len(peeled),
                "peel_matches_claimed": peeled == claimed,
                "peel_is_u_xpow_v_commutator": peeled == with_comm,
                "second_peel": second,
                "second_peel_equals_first": second == peeled,
                "second_peel_equals_original_r2": second == r2,
                "length_drop": (len(r1) + len(peeled)) < (len(r1) + len(r2)),
                "r1_two_block": syllable_two_block(r1),
                "peeled_two_block": syllable_two_block(peeled),
                "r1_v_power_shape": v_shape_r1,
                "r2_x_run": power_block_length(r2, "x"),
                "peeled_x_run": power_block_length(peeled, "x"),
            }
            if not rec["peel_matches_claimed"] or not rec["peel_is_u_xpow_v_commutator"]:
                raise AssertionError(f"Q peel identity failed n={n} delta={delta}: {rec}")
            records.append(rec)
    return records


def check_family_a_prefix() -> list[dict[str, object]]:
    """Both claimed Q(n) spellings start with y^{-2}; prefix cancel is R1^{-1} R2? No.

    R1 = p A, R2 = p B with p = YY. Then R1^{-1} = A^{-1} p^{-1}, so
    R2 * R1^{-1} = p B A^{-1} p^{-1}, a conjugate of B A^{-1}.
    After AC3 (cyclic conjugate) that conjugate is B A^{-1}.
    """
    records = []
    prefix = "YY"
    for n in range(2, 8):
        r1, r2 = family_a_q(n)
        if not (r1.startswith(prefix) and r2.startswith(prefix)):
            raise AssertionError(f"Family A Q({n}) lost common prefix")
        a = r1[len(prefix) :]
        b = r2[len(prefix) :]
        product = peel_suffix(r1, r2)
        conjugated = free_reduce(prefix + b + inv(a) + inv(prefix))
        ba_inv = free_reduce(b + inv(a))
        rec = {
            "family": "A",
            "n": n,
            "r1": r1,
            "r2": r2,
            "input_length": len(r1) + len(r2),
            "r2_times_r1_inv": product,
            "conjugate_form": conjugated,
            "matches_conjugate": product == conjugated,
            "core_b_a_inv": ba_inv,
            "core_length": len(ba_inv),
            "core_two_block": syllable_two_block(ba_inv),
            "length_drop_if_keep_r1_and_core": (len(r1) + len(ba_inv))
            < (len(r1) + len(r2)),
        }
        if product != conjugated:
            raise AssertionError(f"Family A prefix identity failed n={n}")
        records.append(rec)
    return records


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    q_rows = check_q_identities()
    a_rows = check_family_a_prefix()
    summary = {
        "q_cases": len(q_rows),
        "q_identities_pass": all(r["peel_matches_claimed"] for r in q_rows),
        "q_length_drops": sum(1 for r in q_rows if r["length_drop"]),
        "q_second_peel_restores_r2": sum(
            1 for r in q_rows if r["second_peel_equals_original_r2"]
        ),
        "q_r1_v_power_shape_hits": sum(
            1 for r in q_rows if r["r1_v_power_shape"] is not None
        ),
        "family_a_cases": len(a_rows),
        "family_a_identities_pass": all(r["matches_conjugate"] for r in a_rows),
        "family_a_core_two_block": sum(1 for r in a_rows if r["core_two_block"]),
        "g": G,
        "u": U,
        "v": V,
        "commutator": COMM,
        "q_rows": q_rows,
        "family_a_rows": a_rows,
        "status": "identity_checked_not_a_solve",
    }
    path = OUT / "q_peel.json"
    path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {k: summary[k] for k in (
                "q_cases",
                "q_identities_pass",
                "q_length_drops",
                "q_second_peel_restores_r2",
                "q_r1_v_power_shape_hits",
                "family_a_identities_pass",
                "family_a_core_two_block",
                "status",
            )},
            indent=2,
        )
    )
    print("wrote", path)


if __name__ == "__main__":
    main()
