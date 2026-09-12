#!/usr/bin/env python3
"""C20: one associated-subgroup pinch after displayed D·B^{±1} is a round trip.

Also probes whether C12's Whitehead+deletion finish line fires on D or on
the C19 / S_{n,-1} pairs. A primitive hit is not a U124 solve: C1 remains
non-effective, and the incoming C16 route still uses Lemma 11.
"""
from __future__ import annotations

import json
import math
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.words import (  # noqa: E402
    SIGNED_PERMS,
    abelian_det,
    canon_pair,
    cyc_reduce,
    exp_sums,
    free_reduce,
    inv,
)
from experiments.stable_ac.rank3_compression.rank3_whitehead import (  # noqa: E402
    apply_automorphism,
    check_word_reduction,
    compose,
    is_primitive_word,
    reduce_word,
    second_kind_automorphisms,
)

CODE = Path(__file__).resolve().parent
if str(CODE) not in sys.path:
    sys.path.insert(0, str(CODE))

import c12_generator_deletion as c12  # noqa: E402
import c16_escape_scan as esc  # noqa: E402
import theory_wave1_replay as tw  # noqa: E402
from elementary_ac2_scan import children  # noqa: E402

OUT = ROOT / "research" / "u124_stable_20260912" / "tables"

D = "XuuuXUU"


def yu(word: str) -> str:
    return word.replace("u", "y").replace("U", "Y")


def uy(word: str) -> str:
    return word.replace("y", "u").replace("Y", "U")


def B_word(n: int) -> str:
    return "U" + "x" * n + "u" + "X" * (n + 1)


def pinch_occurrences(word: str, stable: str = "u") -> list[dict]:
    """Opposite-sign stable boundaries with only x-letters between, plus
    start index in the cyclically reduced spelling."""
    reduced = cyc_reduce(word)
    length = len(reduced)
    doubled = reduced + reduced
    out: list[dict] = []
    seen: set[tuple] = set()
    for i in range(length):
        left = doubled[i]
        if left.lower() != stable:
            continue
        xexp = 0
        only_x = True
        for step in range(1, length):
            right = doubled[i + step]
            if right.lower() == stable:
                if only_x and right == left.swapcase():
                    key = (i, xexp, left, right)
                    if key not in seen:
                        seen.add(key)
                        out.append(
                            {
                                "start": i,
                                "span": step + 1,
                                "k": xexp,
                                "left": left,
                                "right": right,
                                "word": reduced,
                            }
                        )
                break
            if right.lower() == "x":
                xexp += 1 if right == "x" else -1
            else:
                only_x = False
                break
    return out


def rewrite_bs_pinch(occ: dict, n: int) -> str | None:
    """Replace one valid BS(n,n+1) associated-subgroup pinch by its x-power."""
    k = int(occ["k"])
    if occ["left"] == "U" and occ["right"] == "u":
        if k == 0 or k % n != 0:
            return None
        replacement = tw.pw("x", (k // n) * (n + 1))
    elif occ["left"] == "u" and occ["right"] == "U":
        if k == 0 or k % (n + 1) != 0:
            return None
        replacement = tw.pw("x", (k // (n + 1)) * n)
    else:
        return None
    rotated = occ["word"][occ["start"] :] + occ["word"][: occ["start"]]
    rest = rotated[occ["span"] :]
    return free_reduce(replacement + rest)


def apply_first_valid_pinch(word: str, n: int) -> dict:
    occs = pinch_occurrences(word)
    for occ in occs:
        if not esc.associated_bs_pinch(occ["k"], occ["left"], occ["right"], n):
            continue
        after = rewrite_bs_pinch(occ, n)
        if after is None:
            continue
        return {
            "ok": True,
            "k": occ["k"],
            "left": occ["left"],
            "right": occ["right"],
            "after": after,
            "after_cyc": cyc_reduce(after),
        }
    return {
        "ok": False,
        "occs": [{"k": o["k"], "left": o["left"], "right": o["right"]} for o in occs],
    }


def round_trip_row(n: int) -> dict:
    products = {
        "D*B": free_reduce(D + B_word(n)),
        "B*D": free_reduce(B_word(n) + D),
        "D*Binv": free_reduce(D + inv(B_word(n))),
        "B*Dinv": free_reduce(B_word(n) + inv(D)),
    }
    rec: dict = {"n": n, "B": B_word(n)}
    for name, word in products.items():
        pinch = apply_first_valid_pinch(word, n)
        rec[name] = {
            "product": word,
            "product_cyc": cyc_reduce(word),
            "ok": pinch["ok"],
            "k": pinch.get("k"),
            "after_cyc": pinch.get("after_cyc"),
            "equals_D": pinch.get("after_cyc") == cyc_reduce(D) if pinch["ok"] else False,
            "equals_Dinv": (
                pinch.get("after_cyc") == cyc_reduce(inv(D)) if pinch["ok"] else False
            ),
            "cyclic_of_D": tw.same_cyclic(pinch.get("after", ""), D) if pinch["ok"] else False,
            "cyclic_of_Dinv": (
                tw.same_cyclic(pinch.get("after", ""), inv(D)) if pinch["ok"] else False
            ),
        }
    rec["round_trip"] = (
        rec["D*B"]["equals_D"]
        and rec["B*D"]["equals_D"]
        and rec["D*Binv"]["cyclic_of_D"]
        and rec["B*Dinv"]["cyclic_of_Dinv"]
    )
    return rec


def classify_after_pinch(after_cyc: str, n: int) -> str:
    if tw.same_cyclic(after_cyc, D):
        return "cyclic_D"
    if tw.same_cyclic(after_cyc, inv(D)):
        return "cyclic_Dinv"
    if tw.same_cyclic(after_cyc, B_word(n)):
        return "cyclic_B"
    if tw.same_cyclic(after_cyc, inv(B_word(n))):
        return "cyclic_Binv"
    if not after_cyc:
        return "empty"
    return "other"


def apply_all_valid_pinches(word: str, n: int) -> list[dict]:
    """Every valid associated-subgroup rewrite on this spelling, not just the first."""
    out = []
    for occ in pinch_occurrences(word):
        if not esc.associated_bs_pinch(occ["k"], occ["left"], occ["right"], n):
            continue
        after = rewrite_bs_pinch(occ, n)
        rec = {
            "k": occ["k"],
            "left": occ["left"],
            "right": occ["right"],
            "start": occ["start"],
        }
        if after is None:
            rec.update({"ok": False, "class": "pinch_failed"})
        else:
            after_cyc = cyc_reduce(after)
            rec.update(
                {
                    "ok": True,
                    "after_cyc": after_cyc,
                    "class": classify_after_pinch(after_cyc, n),
                }
            )
        out.append(rec)
    return out


def depth1_pinch_roundtrips(n: int) -> dict:
    """Depth-1 ordinary AC2 neighbourhood of ⟨D, B⟩, n fixed.

    Uniqueness is `canon_pair` (cyclic/inverse canonicalization of both
    rows, then slot order). Every valid pinch occurrence on both rows of
    every unique representative is rewritten. Raw children are counted
    but not separately classified.
    """
    r1, r2 = D, esc.c19_identity(n)["product"]
    seen = set()
    counts = {
        "raw": 0,
        "unique": 0,
        "valid_pinch_children": 0,
        "pinch_applications": 0,
        "cyclic_D": 0,
        "cyclic_Dinv": 0,
        "cyclic_B": 0,
        "cyclic_Binv": 0,
        "empty": 0,
        "empty_on_D_slot": 0,
        "empty_on_B_slot": 0,
        "other": 0,
        "pinch_failed": 0,
        "disallowed_rewrites": 0,
    }
    residues = []
    no_pinch = []
    allowed = {"cyclic_D", "cyclic_Dinv", "cyclic_B", "cyclic_Binv", "empty"}
    for a, b, move in children(r1, r2):
        counts["raw"] += 1
        key = canon_pair(a, b)
        if key in seen:
            continue
        seen.add(key)
        counts["unique"] += 1
        child_had_valid = False
        child_keeps_d = tw.same_cyclic(a, D)
        for word, slot in ((a, "r1"), (b, "r2")):
            rewrites = apply_all_valid_pinches(word, n)
            if not rewrites:
                continue
            child_had_valid = True
            for rec in rewrites:
                counts["pinch_applications"] += 1
                if not rec["ok"]:
                    counts["pinch_failed"] += 1
                    counts["disallowed_rewrites"] += 1
                    continue
                klass = rec["class"]
                counts[klass] += 1
                if klass == "empty":
                    counts["empty_on_D_slot" if slot == "r1" else "empty_on_B_slot"] += 1
                    if slot == "r1":
                        counts["disallowed_rewrites"] += 1
                elif klass not in allowed:
                    counts["disallowed_rewrites"] += 1
                if klass == "other" and len(residues) < 12:
                    residues.append(
                        {
                            "slot": slot,
                            "word": word,
                            "after_cyc": rec.get("after_cyc"),
                            "k": rec["k"],
                            "class": klass,
                            "move": move,
                        }
                    )
        if child_had_valid:
            counts["valid_pinch_children"] += 1
        elif len(no_pinch) < 20:
            no_pinch.append(
                {
                    "r1": a,
                    "r2": b,
                    "len": len(cyc_reduce(a)) + len(cyc_reduce(b)),
                    "keeps_D": child_keeps_d,
                    "r2_len": len(cyc_reduce(b)),
                    "move": move,
                }
            )
    counts["n_no_pinch"] = counts["unique"] - counts["valid_pinch_children"]
    counts["no_pinch_all_keep_D"] = all(row["keeps_D"] for row in no_pinch) if no_pinch else False
    counts["no_pinch_min_len"] = min((row["len"] for row in no_pinch), default=None)
    counts["no_pinch_max_len"] = max((row["len"] for row in no_pinch), default=None)
    counts["all_rewrites_allowed"] = (
        counts["disallowed_rewrites"] == 0
        and counts["other"] == 0
        and counts["pinch_failed"] == 0
        and counts["empty_on_D_slot"] == 0
        and counts["valid_pinch_children"] > 0
    )
    counts["all_round_trip"] = counts["all_rewrites_allowed"]
    return {
        "n": n,
        "counts": counts,
        "residues": residues,
        "no_pinch_children": no_pinch,
        "uniqueness": "canon_pair cyclic/inverse then slot order",
    }


def conjugator_to_cyclic_core(word: str) -> tuple[str, str]:
    """Write a freely reduced word as p * core * p^{-1} with core cyclically reduced."""
    reduced = free_reduce(word)
    prefix = []
    while len(reduced) >= 2 and reduced[0] == reduced[-1].swapcase():
        prefix.append(reduced[0])
        reduced = reduced[1:-1]
    return "".join(prefix), reduced


def first_kind_automorphisms() -> list[dict[str, str]]:
    identity = {"x": "x", "y": "y"}
    out = [identity]
    seen = {("x", "y")}
    for _, img in SIGNED_PERMS:
        key = (img["x"], img["y"])
        if key not in seen:
            seen.add(key)
            out.append({"x": img["x"], "y": img["y"]})
    return out


def reduce_word_with_first_kind(word: str) -> dict:
    """Stock second-kind Whitehead plus length-preserving signed permutations.

    The shared reducer only accepts strictly shortening maps, so it never
    applies a first-kind permutation that could unlock a Type-II descent.
    """
    identity = {"x": "x", "y": "y"}
    current = cyc_reduce(word)
    total = len(current)
    phi = dict(identity)
    steps: list[dict[str, str]] = []
    seconds = second_kind_automorphisms(("x", "y"))
    firsts = first_kind_automorphisms()
    while True:
        best = None
        for first in firsts:
            for sec in seconds:
                auto = compose(sec, first)
                image = cyc_reduce(apply_automorphism(current, auto))
                if len(image) >= total:
                    continue
                cand = (len(image), image)
                if best is None or cand < best[0]:
                    best = (cand, image, auto)
        if best is None:
            return {
                "minimum": current,
                "minimum_total": total,
                "phi": phi,
                "n_steps": len(steps),
                "primitive": total == 1,
            }
        _, image, auto = best
        current = image
        total = len(current)
        phi = compose(auto, phi)
        steps.append(auto)


def nielsen_basis_search(
    target: str,
    max_states: int = 8000,
    max_len: int = 14,
) -> dict:
    """BFS of Nielsen automorphisms looking for φ(x) cyclically equal to target.

    Tracks the ordered basis (φ(x), φ(y)) without independently cyclically
    reducing the two components (that would not be a single Aut).
    """
    target_cyc = cyc_reduce(target)
    target_inv = cyc_reduce(inv(target))

    def neighbors(a: str, b: str) -> list[tuple[str, str, str]]:
        ia, ib = inv(a), inv(b)
        raw = [
            (ia, b, "inv1"),
            (a, ib, "inv2"),
            (b, a, "swap"),
            (free_reduce(a + b), b, "a*=b"),
            (free_reduce(a + ib), b, "a*=binv"),
            (free_reduce(b + a), b, "a:=b*a"),
            (free_reduce(ib + a), b, "a:=binv*a"),
            (a, free_reduce(b + a), "b*=a"),
            (a, free_reduce(b + ia), "b*=ainv"),
            (a, free_reduce(a + b), "b:=a*b"),
            (a, free_reduce(ia + b), "b:=ainv*b"),
        ]
        out = []
        seen = set()
        for na, nb, lab in raw:
            na, nb = free_reduce(na), free_reduce(nb)
            if not na or not nb or len(na) > max_len or len(nb) > max_len:
                continue
            key = (na, nb)
            if key not in seen:
                seen.add(key)
                out.append((na, nb, lab))
        return out

    start = ("x", "y")
    q = deque([(start, [])])
    seen = {start}
    while q and len(seen) < max_states:
        (a, b), path = q.popleft()
        a_cyc = cyc_reduce(a)
        if a_cyc == target_cyc or a_cyc == target_inv:
            return {
                "found": True,
                "phi_x": a,
                "phi_y": b,
                "path": path,
                "states": len(seen),
                "inverted": a_cyc == target_inv,
            }
        for na, nb, lab in neighbors(a, b):
            key = (na, nb)
            if key in seen:
                continue
            seen.add(key)
            q.append((key, path + [lab]))
    return {"found": False, "states": len(seen), "max_states": max_states}


def serialize_whitehead(word: str, nielsen: bool = False) -> dict:
    labeled = yu(word) if "u" in word.lower() else word
    result = reduce_word(labeled, generators=("x", "y"))
    check_word_reduction(labeled, result)
    phi_image = apply_automorphism(labeled, result.phi)
    prefix, core = conjugator_to_cyclic_core(phi_image)
    full = reduce_word_with_first_kind(labeled)
    rec = {
        "word": word,
        "labeled": labeled,
        "minimum": result.minimum,
        "minimum_total": result.minimum_total,
        "primitive": bool(is_primitive_word(result)),
        "n_steps": len(result.steps),
        "phi": dict(result.phi),
        "phi_image": phi_image,
        "conjugator": prefix,
        "core": core,
        "exp": list(exp_sums(labeled)),
        "abelian_gcd": math.gcd(abs(exp_sums(labeled)[0]), abs(exp_sums(labeled)[1])),
        "first_kind_minimum": full["minimum"],
        "first_kind_minimum_total": full["minimum_total"],
        "first_kind_primitive": full["primitive"],
        "first_kind_n_steps": full["n_steps"],
        "first_kind_phi": full["phi"],
    }
    if nielsen and not rec["primitive"] and not rec["first_kind_primitive"]:
        rec["nielsen"] = nielsen_basis_search(labeled)
        if rec["nielsen"].get("found"):
            rec["nielsen_primitive"] = True
        else:
            rec["nielsen_primitive"] = False
    return rec


def c12_after_whitehead(donor: str, companion: str, whitehead: dict) -> dict:
    """Apply the Whitehead Aut of the donor to both rows, AC3-normalize the
    donor to a generator, then run elementary generator deletion.

    The Aut itself is C1 and is not expanded here.
    """
    primitive = whitehead.get("primitive") or whitehead.get("first_kind_primitive")
    if not primitive:
        return {
            "fired": False,
            "reason": "donor_not_primitive",
            "stock_min": whitehead.get("minimum_total"),
            "first_kind_min": whitehead.get("first_kind_minimum_total"),
            "nielsen_found": (whitehead.get("nielsen") or {}).get("found"),
        }
    phi = (
        whitehead["phi"]
        if whitehead.get("primitive")
        else whitehead["first_kind_phi"]
    )
    r1 = apply_automorphism(yu(donor), phi)
    r2 = apply_automorphism(yu(companion), phi)
    prefix, core = conjugator_to_cyclic_core(r1)
    if core.lower() != "x" and core.lower() != "y":
        return {
            "fired": False,
            "reason": "core_not_generator",
            "core": core,
            "phi_r1": r1,
            "phi_r2": r2,
        }
    # AC3 on the first relator only: conjugate by prefix^{-1} to drop the
    # conjugator. Companion is not conjugated (ordinary one-relator AC3).
    normalized = core
    companion_kept = r2
    if prefix:
        # r1 = prefix * core * prefix^{-1}; AC3 by prefix^{-1} yields core.
        pass
    if normalized.lower() == "y":
        swap = {"x": "y", "y": "x"}
        normalized = apply_automorphism(normalized, swap)
        companion_kept = apply_automorphism(companion_kept, swap)
        # Signed permutation of generators is a Nielsen Aut (C1), not expanded.
        c1_swap = True
    else:
        c1_swap = False
    if normalized == "X":
        normalized = "x"
        inverted_first = True
    else:
        inverted_first = False
    deletion = c12.delete_all_x(companion_kept)
    leftover = deletion["leftover"]
    return {
        "fired": leftover in ("y", "Y"),
        "c1_swap": c1_swap,
        "inverted_first": inverted_first,
        "phi_r1": r1,
        "phi_r2": r2,
        "normalized_first": normalized,
        "leftover": leftover,
        "y_exponent": deletion["y_exponent"],
        "delete_steps": deletion["steps"],
        "n_moves": deletion["n_moves"],
        "terminal_is_y_pm1": deletion["terminal_is_y_pm1"],
        "det": abelian_det(yu(donor), yu(companion)),
        "note": (
            "Whitehead Aut and any generator swap are C1. Deletion moves "
            "are elementary AC1–AC3. Not a U124 certificate."
        ),
    }


def family_probe() -> dict:
    donor_wh = serialize_whitehead(D, nielsen=True)
    rows = []
    for n in range(2, 8):
        s_donor, s_comp = tw.s_pair(n, -1)
        c19_donor, c19_comp = esc.c19_identity(n)["donor"], esc.c19_identity(n)["product"]
        q1, q2 = tw.q_prime(n, -1)
        rec = {
            "n": n,
            "det_S": abelian_det(yu(s_donor), yu(s_comp)),
            "det_C19": abelian_det(yu(c19_donor), yu(c19_comp)),
            "det_Qprime": abelian_det(q1, q2),
            "S_c12": c12_after_whitehead(s_donor, s_comp, donor_wh),
            "C19_c12": c12_after_whitehead(c19_donor, c19_comp, donor_wh),
            "Qprime_r1_whitehead": serialize_whitehead(q1),
            "Qprime_r2_whitehead": serialize_whitehead(q2),
            "S_companion_whitehead": serialize_whitehead(s_comp),
            "C19_B_whitehead": serialize_whitehead(c19_comp),
        }
        rows.append(rec)
    stored = []
    for tag, a_u, b_u, p, b, c in esc.STORED_HITS:
        a_hat, b_hat = esc.endpoint_from_params(a_u, b_u, p, b, c)
        stored.append(
            {
                "id": tag,
                "r1": a_hat,
                "r2": b_hat,
                "r1_whitehead": serialize_whitehead(a_hat),
                "r2_whitehead": serialize_whitehead(b_hat),
                "det": abelian_det(yu(a_hat), yu(b_hat)),
            }
        )
    return {
        "D_whitehead": donor_wh,
        "family": rows,
        "stored_c16": stored,
        "any_S_c12_finish": any(r["S_c12"].get("fired") for r in rows),
        "any_C19_c12_finish": any(r["C19_c12"].get("fired") for r in rows),
        "any_Qprime_r1_primitive": any(
            r["Qprime_r1_whitehead"]["primitive"]
            or r["Qprime_r1_whitehead"]["first_kind_primitive"]
            for r in rows
        ),
        "any_Qprime_r2_primitive": any(
            r["Qprime_r2_whitehead"]["primitive"]
            or r["Qprime_r2_whitehead"]["first_kind_primitive"]
            for r in rows
        ),
        "any_stored_primitive": any(
            rec["r1_whitehead"]["primitive"]
            or rec["r1_whitehead"]["first_kind_primitive"]
            or rec["r2_whitehead"]["primitive"]
            or rec["r2_whitehead"]["first_kind_primitive"]
            for rec in stored
        ),
    }


def main() -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    identities = [round_trip_row(n) for n in range(2, 8)]
    round_ok = all(r["round_trip"] for r in identities)
    depth1 = [depth1_pinch_roundtrips(n) for n in range(2, 8)]
    probes = family_probe()
    other_residues = sum(r["counts"]["other"] for r in depth1)
    b_mins = {
        r["n"]: r["C19_B_whitehead"]["first_kind_minimum_total"]
        for r in probes["family"]
    }
    summary = {
        "round_trip_ok": round_ok,
        "n_checked": len(identities),
        "claim_scope": "displayed identities any n>=2 by free cancellation; neighbourhood n=2..7",
        "pinch_is_not_an_ac_move": True,
        "D_primitive": probes["D_whitehead"]["primitive"],
        "D_whitehead_min": probes["D_whitehead"]["minimum_total"],
        "D_first_kind_primitive": probes["D_whitehead"]["first_kind_primitive"],
        "D_first_kind_min": probes["D_whitehead"]["first_kind_minimum_total"],
        "B_first_kind_minima": b_mins,
        "D_nielsen_found": (probes["D_whitehead"].get("nielsen") or {}).get("found"),
        "D_nielsen_states": (probes["D_whitehead"].get("nielsen") or {}).get("states"),
        "depth1_all_rewrites_allowed": all(
            r["counts"]["all_rewrites_allowed"] for r in depth1
        ),
        "depth1_all_round_trip": all(r["counts"]["all_round_trip"] for r in depth1),
        "depth1_other_residues": other_residues,
        "depth1_no_pinch_all_keep_D": all(
            r["counts"]["no_pinch_all_keep_D"] for r in depth1
        ),
        "depth1_counts": {r["n"]: r["counts"] for r in depth1},
        "any_S_c12_finish": probes["any_S_c12_finish"],
        "any_C19_c12_finish": probes["any_C19_c12_finish"],
        "any_Qprime_r1_primitive": probes["any_Qprime_r1_primitive"],
        "any_Qprime_r2_primitive": probes["any_Qprime_r2_primitive"],
        "any_stored_primitive": probes["any_stored_primitive"],
        "solved_u124": 0,
    }
    report = {
        "summary": summary,
        "statement": (
            "For n>=2 the four displayed freely reduced products D·B, B·D, "
            "D·B^{-1}, B·D^{-1} satisfy: each listed associated-subgroup "
            "rewrite returns a cyclic conjugate of D or D^{-1}. This is "
            "equality modulo B (a BS/Britton preflight), not an AC1–AC5 "
            "move. For n=2..7, every valid pinch occurrence on both rows of "
            "every canon_pair-unique depth-1 AC2 child rewrites to cyclic D, "
            "D^{-1}, B, B^{-1}, or empty; empty occurs only on the B slot."
        ),
        "identities": identities,
        "depth1_pinches": depth1,
        "probes": probes,
        "notes": [
            "The associated-subgroup rewrite is not an AC1–AC5 move.",
            "A valid pinch on D·B that is B's own BS pinch is not a C5 finish.",
            "Uniqueness is canon_pair (cyclic/inverse of each row, then slot order).",
            "No-pinch children are serialized with lengths; they keep D.",
            "Whitehead Aut / generator swap are C1 and are not expanded.",
            "Incoming C16 still has two Lemma-11 uses. Not a U124 solve.",
        ],
    }
    path = OUT / "c20_roundtrip.json"
    path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("c20 round trip")
    print(json.dumps(summary, indent=2))
    print(f"wrote {path}")
    if not round_ok:
        raise SystemExit(2)
    if not summary["depth1_all_rewrites_allowed"]:
        raise SystemExit(3)
    return report


if __name__ == "__main__":
    main()
