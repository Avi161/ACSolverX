from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

SCHEMA = "acsolverx.mms02.sequential-donor-factorization"
VERSION = 1

PINNED = {
    "A": "xzYXyxZXYxyZ",
    "B": "XyxZXYXyxzXYxy",
    "u": "zYX",
    "c": "yxZXY",
    "C": "yxzXY",
    "r": "xyxZXY",
    "q": "Xy",
    "v": "Xyz",
    "h": "YX",
}

TRANSCRIPT_SPECS = (
    ("I3", "invert", 3, None, None),
    ("M32", "multiply", 3, 2, None),
    ("I3", "invert", 3, None, None),
    ("C_yx(3)", "conjugate", 3, None, "yx"),
    ("M13", "multiply", 1, 3, None),
    ("C_XY(3)", "conjugate", 3, None, "XY"),
    ("C_Yx(1)", "conjugate", 1, None, "Yx"),
    ("M21", "multiply", 2, 1, None),
    ("C_Xy(1)", "conjugate", 1, None, "Xy"),
)

TRANSCRIPT_STATES = (
    ("xyxZXY", "Xy", "Xyz"),
    ("xyxZXY", "Xy", "ZYx"),
    ("xyxZXY", "Xy", "Z"),
    ("xyxZXY", "Xy", "z"),
    ("xyxZXY", "Xy", "yxzXY"),
    ("x", "Xy", "yxzXY"),
    ("x", "Xy", "z"),
    ("Yxy", "Xy", "z"),
    ("Yxy", "y", "z"),
    ("x", "y", "z"),
)

S1_SPECS = (
    (1, 2, "x", 1),
    (1, 2, "xx", -1),
    (1, 3, "xx", 1),
    (1, 2, "x", -1),
    (1, 2, "zY", 1),
    (1, 3, "zYx", -1),
    (1, 2, "zYx", 1),
    (1, 2, "zY", -1),
)

S2_SPECS = (
    (2, 1, "YX", 1),
    (2, 1, "YXX", -1),
)

NONCLAIMS = [
    "S1 and S2 are separate branches from (r,q,v) and do not concatenate.",
    "The full sequential donor factorization is equivalent to the open MMS02 bridge and is not supplied here.",
    "The nine-action triangular transcript is separate from both donor branches.",
    "No normal-closure factorization or membership decision is claimed for D modulo <<A,v>>.",
    "No normal-closure factorization or membership decision is claimed for K modulo <<B,v>>.",
    "No finite quotient, finite-group enumeration, or search result is claimed.",
]


def inverse(word: str) -> str:
    if not isinstance(word, str) or not all(letter in "xyzXYZ" for letter in word):
        raise ValueError(f"invalid free-group word: {word!r}")
    return word[::-1].swapcase()


def free_reduce(word: str) -> str:
    if not isinstance(word, str) or not all(letter in "xyzXYZ" for letter in word):
        raise ValueError(f"invalid free-group word: {word!r}")
    stack: list[str] = []
    for letter in word:
        if stack and stack[-1] == letter.swapcase():
            stack.pop()
        else:
            stack.append(letter)
    return "".join(stack)


def commutator(left: str, right: str) -> str:
    return free_reduce(left + right + inverse(left) + inverse(right))


def conjugate(conjugator: str, word: str) -> str:
    return free_reduce(conjugator + word + inverse(conjugator))


def substitute_z(word: str) -> str:
    image = "Yx"
    expanded = "".join(
        image if letter == "z" else inverse(image) if letter == "Z" else letter
        for letter in word
    )
    return free_reduce(expanded)


def _row_index(value: object, field: str) -> int:
    if type(value) is not int or not 1 <= value <= 3:
        raise ValueError(f"{field} must be a 1-based row index")
    return value - 1


def apply_action(
    rows: tuple[str, str, str], action: dict[str, object]
) -> tuple[str, str, str]:
    if not isinstance(rows, tuple) or len(rows) != 3:
        raise ValueError("rows must be a three-word tuple")
    current = list(rows)
    target = _row_index(action.get("target_index"), "target_index")
    kind = action.get("kind")

    if kind == "invert":
        current[target] = inverse(current[target])
    elif kind == "multiply":
        donor = _row_index(action.get("donor_index"), "donor_index")
        if donor == target:
            raise ValueError("multiply donor and target must differ")
        current[target] = free_reduce(current[target] + current[donor])
    elif kind == "conjugate":
        conjugator = action.get("conjugator")
        if not isinstance(conjugator, str):
            raise ValueError("conjugate action requires a literal conjugator")
        current[target] = conjugate(conjugator, current[target])
    else:
        raise ValueError(f"unknown primitive action: {kind!r}")
    return tuple(current)  # type: ignore[return-value]


def _action_record(
    rows: tuple[str, str, str],
    *,
    ordinal: int,
    label: str,
    kind: str,
    target_index: int,
    donor_index: int | None = None,
    conjugator: str | None = None,
) -> tuple[dict[str, object], tuple[str, str, str]]:
    action: dict[str, object] = {
        "before": list(rows),
        "kind": kind,
        "label": label,
        "ordinal": ordinal,
        "target_index": target_index,
    }
    if donor_index is not None:
        action["donor_index"] = donor_index
    if conjugator is not None:
        action["conjugator"] = conjugator
    after = apply_action(rows, action)
    action["after"] = list(after)
    return action, after


def _build_transcript() -> dict[str, object]:
    rows = TRANSCRIPT_STATES[0]
    actions: list[dict[str, object]] = []
    for ordinal, (label, kind, target, donor, conjugator) in enumerate(
        TRANSCRIPT_SPECS, start=1
    ):
        action, rows = _action_record(
            rows,
            ordinal=ordinal,
            label=label,
            kind=kind,
            target_index=target,
            donor_index=donor,
            conjugator=conjugator,
        )
        actions.append(action)
        if rows != TRANSCRIPT_STATES[ordinal]:
            raise AssertionError(
                f"pinned transcript identity failed at action {ordinal}: {rows!r}"
            )
    return {
        "action_count": len(actions),
        "actions": actions,
        "endpoint": list(rows),
        "kind_counts": dict(sorted(Counter(a["kind"] for a in actions).items())),
        "start": list(TRANSCRIPT_STATES[0]),
    }


def _build_macro(
    rows: tuple[str, str, str],
    *,
    branch_name: str,
    ordinal: int,
    target_index: int,
    donor_index: int,
    conjugator: str,
    donor_sign: int,
) -> tuple[dict[str, object], tuple[str, str, str]]:
    if donor_sign not in (-1, 1):
        raise ValueError("donor sign must be +1 or -1")
    if target_index == donor_index:
        raise ValueError("macro target and donor must differ")

    before = rows
    donor_before = before[donor_index - 1]
    signed_donor = donor_before if donor_sign == 1 else inverse(donor_before)
    factor = conjugate(conjugator, signed_donor)
    primitive_expansion: list[dict[str, object]] = []

    primitive_specs: list[tuple[str, int, int | None, str | None]] = []
    if donor_sign == -1:
        primitive_specs.append(("invert", donor_index, None, None))
    primitive_specs.extend(
        (
            ("conjugate", donor_index, None, conjugator),
            ("multiply", target_index, donor_index, None),
            ("conjugate", donor_index, None, inverse(conjugator)),
        )
    )
    if donor_sign == -1:
        primitive_specs.append(("invert", donor_index, None, None))

    for primitive_ordinal, (kind, target, donor, primitive_conjugator) in enumerate(
        primitive_specs, start=1
    ):
        action, rows = _action_record(
            rows,
            ordinal=primitive_ordinal,
            label=f"{branch_name}.{ordinal}.{primitive_ordinal}",
            kind=kind,
            target_index=target,
            donor_index=donor,
            conjugator=primitive_conjugator,
        )
        primitive_expansion.append(action)

    donor_after = rows[donor_index - 1]
    if donor_after != donor_before:
        raise AssertionError(f"{branch_name} macro {ordinal} failed donor restoration")
    expected_target = free_reduce(before[target_index - 1] + factor)
    if rows[target_index - 1] != expected_target:
        raise AssertionError(f"{branch_name} macro {ordinal} inserted the wrong factor")

    return (
        {
            "after": list(rows),
            "before": list(before),
            "conjugator": conjugator,
            "donor_after": donor_after,
            "donor_before": donor_before,
            "donor_index": donor_index,
            "donor_restored": True,
            "donor_sign": donor_sign,
            "factor": factor,
            "ordinal": ordinal,
            "primitive_expansion": primitive_expansion,
            "target_index": target_index,
        },
        rows,
    )


def _build_branch(
    name: str,
    specs: tuple[tuple[int, int, str, int], ...],
    endpoint: tuple[str, str, str],
) -> dict[str, object]:
    start = (PINNED["r"], PINNED["q"], PINNED["v"])
    rows = start
    macros: list[dict[str, object]] = []
    for ordinal, (target, donor, conjugator, sign) in enumerate(specs, start=1):
        macro, rows = _build_macro(
            rows,
            branch_name=name,
            ordinal=ordinal,
            target_index=target,
            donor_index=donor,
            conjugator=conjugator,
            donor_sign=sign,
        )
        macros.append(macro)
    if rows != endpoint:
        raise AssertionError(f"{name} endpoint identity failed: {rows!r} != {endpoint!r}")
    primitives = [action for macro in macros for action in macro["primitive_expansion"]]
    return {
        "endpoint": list(rows),
        "macro_count": len(macros),
        "macros": macros,
        "primitive_count": len(primitives),
        "primitive_kind_counts": dict(
            sorted(Counter(action["kind"] for action in primitives).items())
        ),
        "start": list(start),
    }


def _expected_quotient_gates(words: dict[str, str]) -> dict[str, object]:
    return {
        "D_mod_A_v": {
            "defect": substitute_z(words["D"]),
            "normal_closure_generators": ["A", "v"],
            "presentation": {
                "generators": ["x", "y"],
                "name": "Q_A",
                "relator": substitute_z(words["A"]),
            },
            "status": "undecided",
        },
        "K_mod_B_v": {
            "defect": substitute_z(words["K"]),
            "normal_closure_generators": ["B", "v"],
            "presentation": {
                "generators": ["x", "y"],
                "name": "Q_B",
                "relator": substitute_z(words["B"]),
            },
            "status": "undecided",
        },
        "substitution": {"Z": "Xy", "relation": "v=1", "z": "Yx"},
    }


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def build_certificate() -> dict[str, object]:
    words = dict(PINNED)
    words["K"] = commutator(words["u"], words["C"])
    words["D"] = conjugate(words["h"], commutator("X", words["r"]))

    _require(inverse(words["c"]) == words["C"], "pinned C=c^-1 identity failed")
    _require(
        free_reduce(words["r"] + inverse(words["K"])) == words["A"],
        "pinned A=r K^-1 identity failed",
    )
    _require(
        free_reduce(words["q"] + inverse(words["D"])) == words["B"],
        "pinned B=q D^-1 identity failed",
    )

    transcript = _build_transcript()
    s1_endpoint = (words["A"], words["q"], words["v"])
    s2_endpoint = (words["r"], words["B"], words["v"])
    branches = {
        "S1": _build_branch("S1", S1_SPECS, s1_endpoint),
        "S2": _build_branch("S2", S2_SPECS, s2_endpoint),
    }

    f_factors = [macro["factor"] for macro in branches["S1"]["macros"][:4]]
    k_inverse_factors = [
        macro["factor"] for macro in branches["S1"]["macros"]
    ]
    d_inverse_factors = [
        macro["factor"] for macro in branches["S2"]["macros"]
    ]
    identities = {
        "A_from_r_K_inverse": {
            "expected": words["A"],
            "product": free_reduce(words["r"] + inverse(words["K"])),
        },
        "B_from_q_D_inverse": {
            "expected": words["B"],
            "product": free_reduce(words["q"] + inverse(words["D"])),
        },
        "C_factorization": {
            "expected": words["C"],
            "factors": f_factors,
            "product": free_reduce("".join(f_factors)),
        },
        "C_inverse_of_c": {"expected": words["C"], "product": inverse(words["c"])},
        "D_inverse_factorization": {
            "expected": inverse(words["D"]),
            "factors": d_inverse_factors,
            "product": free_reduce("".join(d_inverse_factors)),
        },
        "K_inverse_factorization": {
            "expected": inverse(words["K"]),
            "factors": k_inverse_factors,
            "product": free_reduce("".join(k_inverse_factors)),
        },
    }
    for name, identity in identities.items():
        _require(identity["product"] == identity["expected"], f"{name} failed")

    all_actions = list(transcript["actions"])
    all_actions.extend(
        action
        for branch in branches.values()
        for macro in branch["macros"]
        for action in macro["primitive_expansion"]
    )
    kind_counts = Counter(action["kind"] for action in all_actions)
    counts = {
        "branch_macros": sum(branch["macro_count"] for branch in branches.values()),
        "conjugations": kind_counts["conjugate"],
        "inversions": kind_counts["invert"],
        "multiplications": kind_counts["multiply"],
        "total_primitives": len(all_actions),
        "transcript_actions": transcript["action_count"],
    }

    certificate: dict[str, object] = {
        "branches": branches,
        "convention": {
            "commutator": "[s,t]=s t s^-1 t^-1",
            "conjugation": "target := free_reduce(w target w^-1)",
            "multiplication": "target := free_reduce(target donor)",
            "reduction": "free only; no cyclic rotation or cyclic reduction",
            "row_indices": "1-based",
            "uppercase": "inverse",
        },
        "counts": counts,
        "identities": identities,
        "nonclaims": NONCLAIMS,
        "quotient_gates": _expected_quotient_gates(words),
        "schema": SCHEMA,
        "triangular_transcript": transcript,
        "version": VERSION,
        "words": words,
    }
    validate_certificate(certificate)
    return certificate


def _rows(value: object, field: str) -> tuple[str, str, str]:
    if not isinstance(value, list) or len(value) != 3 or not all(
        isinstance(word, str) for word in value
    ):
        raise ValueError(f"{field} must be a JSON row triple")
    return tuple(value)  # type: ignore[return-value]


def _validate_action(
    action: object,
    current: tuple[str, str, str],
    *,
    ordinal: int,
) -> tuple[str, str, str]:
    if not isinstance(action, dict):
        raise TypeError("primitive action must be an object")
    _require(action.get("ordinal") == ordinal, "primitive ordinal mismatch")
    _require(_rows(action.get("before"), "action.before") == current, "action before mismatch")
    computed = apply_action(current, action)
    _require(_rows(action.get("after"), "action.after") == computed, "action after mismatch")
    return computed


def validate_certificate(certificate: dict[str, object]) -> None:
    if not isinstance(certificate, dict):
        raise TypeError("certificate must be an object")
    _require(certificate.get("schema") == SCHEMA, "schema mismatch")
    _require(certificate.get("version") == VERSION, "version mismatch")
    words = certificate.get("words")
    _require(isinstance(words, dict), "words must be an object")
    expected_words = dict(PINNED)
    expected_words["K"] = commutator(PINNED["u"], PINNED["C"])
    expected_words["D"] = conjugate(PINNED["h"], commutator("X", PINNED["r"]))
    _require(words == expected_words, "literal pinned words mismatch")

    transcript = certificate.get("triangular_transcript")
    _require(isinstance(transcript, dict), "triangular transcript must be an object")
    current = _rows(transcript.get("start"), "transcript.start")
    _require(current == TRANSCRIPT_STATES[0], "transcript start mismatch")
    actions = transcript.get("actions")
    _require(isinstance(actions, list) and len(actions) == 9, "transcript must have nine actions")
    for ordinal, (action, spec) in enumerate(zip(actions, TRANSCRIPT_SPECS), start=1):
        _require(isinstance(action, dict), "transcript action must be an object")
        label, kind, target, donor, conjugator = spec
        _require(action.get("label") == label, "transcript label mismatch")
        _require(action.get("kind") == kind, "transcript kind mismatch")
        _require(action.get("target_index") == target, "transcript target mismatch")
        _require(action.get("donor_index") == donor, "transcript donor mismatch")
        _require(action.get("conjugator") == conjugator, "transcript conjugator mismatch")
        current = _validate_action(action, current, ordinal=ordinal)
        _require(current == TRANSCRIPT_STATES[ordinal], "transcript state mismatch")
    _require(_rows(transcript.get("endpoint"), "transcript.endpoint") == current, "transcript endpoint mismatch")
    _require(transcript.get("action_count") == 9, "transcript action count mismatch")

    branches = certificate.get("branches")
    _require(isinstance(branches, dict) and set(branches) == {"S1", "S2"}, "branch set mismatch")
    for branch_name, specs, endpoint in (
        ("S1", S1_SPECS, (PINNED["A"], PINNED["q"], PINNED["v"])),
        ("S2", S2_SPECS, (PINNED["r"], PINNED["B"], PINNED["v"])),
    ):
        branch = branches[branch_name]
        _require(isinstance(branch, dict), f"{branch_name} must be an object")
        current = _rows(branch.get("start"), f"{branch_name}.start")
        _require(current == (PINNED["r"], PINNED["q"], PINNED["v"]), f"{branch_name} start mismatch")
        macros = branch.get("macros")
        _require(isinstance(macros, list) and len(macros) == len(specs), f"{branch_name} macro count mismatch")
        primitive_count = 0
        for ordinal, (macro, spec) in enumerate(zip(macros, specs), start=1):
            _require(isinstance(macro, dict), "macro must be an object")
            target, donor, conjugator, sign = spec
            _require(macro.get("ordinal") == ordinal, "macro ordinal mismatch")
            _require(macro.get("target_index") == target, "macro target mismatch")
            _require(macro.get("donor_index") == donor, "macro donor mismatch")
            _require(macro.get("conjugator") == conjugator, "macro conjugator mismatch")
            _require(macro.get("donor_sign") == sign, "macro donor sign mismatch")
            _require(_rows(macro.get("before"), "macro.before") == current, "macro before mismatch")
            donor_before = current[donor - 1]
            _require(macro.get("donor_before") == donor_before, "macro donor-before mismatch")
            signed = donor_before if sign == 1 else inverse(donor_before)
            _require(macro.get("factor") == conjugate(conjugator, signed), "macro factor mismatch")
            primitives = macro.get("primitive_expansion")
            expected_length = 3 if sign == 1 else 5
            _require(isinstance(primitives, list) and len(primitives) == expected_length, "macro primitive count mismatch")
            for primitive_ordinal, action in enumerate(primitives, start=1):
                current = _validate_action(action, current, ordinal=primitive_ordinal)
            primitive_count += len(primitives)
            _require(_rows(macro.get("after"), "macro.after") == current, "macro after mismatch")
            _require(macro.get("donor_after") == current[donor - 1], "macro donor-after mismatch")
            _require(macro.get("donor_after") == donor_before, "macro donor not restored")
            _require(macro.get("donor_restored") is True, "macro restoration flag mismatch")
        _require(current == endpoint, f"{branch_name} endpoint identity failed")
        _require(_rows(branch.get("endpoint"), f"{branch_name}.endpoint") == endpoint, f"{branch_name} stored endpoint mismatch")
        _require(branch.get("macro_count") == len(specs), f"{branch_name} stored macro count mismatch")
        _require(branch.get("primitive_count") == primitive_count, f"{branch_name} primitive count mismatch")

    identities = certificate.get("identities")
    _require(isinstance(identities, dict), "identities must be an object")
    for name, identity in identities.items():
        _require(isinstance(identity, dict), f"{name} must be an object")
        _require(identity.get("product") == identity.get("expected"), f"{name} identity failed")
    _require(certificate.get("quotient_gates") == _expected_quotient_gates(expected_words), "quotient gate mismatch")
    _require(certificate.get("nonclaims") == NONCLAIMS, "nonclaim ledger mismatch")
    _require(
        certificate.get("counts")
        == {
            "branch_macros": 10,
            "conjugations": 24,
            "inversions": 12,
            "multiplications": 13,
            "total_primitives": 49,
            "transcript_actions": 9,
        },
        "combined action counts mismatch",
    )


def _summary(certificate: dict[str, Any]) -> dict[str, object]:
    return {
        "branch_endpoints": {
            name: branch["endpoint"] for name, branch in certificate["branches"].items()
        },
        "branch_macros": {
            name: branch["macro_count"] for name, branch in certificate["branches"].items()
        },
        "total_primitives": certificate["counts"]["total_primitives"],
        "transcript_actions": certificate["counts"]["transcript_actions"],
        "transcript_endpoint": certificate["triangular_transcript"]["endpoint"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the MMS02 donor certificate")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--output", type=Path)
    args = parser.parse_args()

    certificate = build_certificate()
    validate_certificate(certificate)
    if args.output is not None:
        payload = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
        if args.output.exists():
            _require(args.output.read_text(encoding="utf-8") == payload, "existing output differs from validated certificate")
        else:
            args.output.write_text(payload, encoding="utf-8")
    print(json.dumps(_summary(certificate), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
