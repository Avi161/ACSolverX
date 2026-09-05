from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any

SCHEMA = "acsolverx.mms02.sequential-donor-factorization"
VERSION = 1

BASE_WORDS = {
    "A": "xzYXyxZXYxyZ",
    "B": "XyxZXYXyxzXYxy",
    "C": "yxzXY",
    "c": "yxZXY",
    "h": "YX",
    "q": "Xy",
    "r": "xyxZXY",
    "u": "zYX",
    "v": "Xyz",
}

TRIANGLE = (
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

TRIANGLE_LEDGER = (
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

BRANCH_SPECS = {
    "S1": (
        (1, 2, "x", 1),
        (1, 2, "xx", -1),
        (1, 3, "xx", 1),
        (1, 2, "x", -1),
        (1, 2, "zY", 1),
        (1, 3, "zYx", -1),
        (1, 2, "zYx", 1),
        (1, 2, "zY", -1),
    ),
    "S2": (
        (2, 1, "YX", 1),
        (2, 1, "YXX", -1),
    ),
}

NONCLAIMS = [
    "S1 and S2 are separate branches from (r,q,v) and do not concatenate.",
    "The full sequential donor factorization is equivalent to the open MMS02 bridge and is not supplied here.",
    "The nine-action triangular transcript is separate from both donor branches.",
    "No normal-closure factorization or membership decision is claimed for D modulo <<A,v>>.",
    "No normal-closure factorization or membership decision is claimed for K modulo <<B,v>>.",
    "No finite quotient, finite-group enumeration, or search result is claimed.",
]

TOP_LEVEL_KEYS = {
    "branches",
    "convention",
    "counts",
    "identities",
    "nonclaims",
    "quotient_gates",
    "schema",
    "triangular_transcript",
    "version",
    "words",
}


def _check(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def inverse(word: str) -> str:
    _check(isinstance(word, str), "word is not a string")
    _check(all(letter in "xyzXYZ" for letter in word), "word has an invalid letter")
    result: list[str] = []
    for letter in reversed(word):
        result.append(letter.upper() if letter.islower() else letter.lower())
    return "".join(result)


def free_reduce(word: str) -> str:
    _check(isinstance(word, str), "word is not a string")
    _check(all(letter in "xyzXYZ" for letter in word), "word has an invalid letter")
    current = word
    while True:
        reduced: list[str] = []
        index = 0
        changed = False
        while index < len(current):
            if (
                index + 1 < len(current)
                and current[index].swapcase() == current[index + 1]
            ):
                changed = True
                index += 2
            else:
                reduced.append(current[index])
                index += 1
        next_word = "".join(reduced)
        if not changed:
            return next_word
        current = next_word


def _conjugated(conjugator: str, word: str) -> str:
    return free_reduce(conjugator + word + inverse(conjugator))


def _commutator(first: str, second: str) -> str:
    return free_reduce(first + second + inverse(first) + inverse(second))


def _substitute_v_trivial(word: str) -> str:
    pieces: list[str] = []
    for letter in word:
        if letter == "z":
            pieces.append("Yx")
        elif letter == "Z":
            pieces.append("Xy")
        else:
            pieces.append(letter)
    return free_reduce("".join(pieces))


def _object(value: object, field: str) -> dict[str, Any]:
    _check(isinstance(value, dict), f"{field} is not an object")
    return value


def _list(value: object, field: str) -> list[Any]:
    _check(isinstance(value, list), f"{field} is not a list")
    return value


def _row_tuple(value: object, field: str) -> tuple[str, str, str]:
    rows = _list(value, field)
    _check(len(rows) == 3, f"{field} does not contain three rows")
    _check(all(isinstance(word, str) for word in rows), f"{field} has a nonword row")
    for word in rows:
        _check(all(letter in "xyzXYZ" for letter in word), f"{field} has invalid case")
    return rows[0], rows[1], rows[2]


def _index(action: dict[str, Any], field: str) -> int:
    value = action.get(field)
    _check(type(value) is int and 1 <= value <= 3, f"{field} is not 1-based")
    return value


def _action_keys(kind: str) -> set[str]:
    keys = {"after", "before", "kind", "label", "ordinal", "target_index"}
    if kind == "multiply":
        keys.add("donor_index")
    elif kind == "conjugate":
        keys.add("conjugator")
    return keys


def _play_action(
    current: tuple[str, str, str],
    literal: object,
    *,
    ordinal: int,
    label: str,
    kind: str,
    target_index: int,
    donor_index: int | None,
    conjugator: str | None,
) -> tuple[str, str, str]:
    action = _object(literal, "action")
    _check(set(action) == _action_keys(kind), "primitive action key set mismatch")
    _check(action["ordinal"] == ordinal, "primitive ordinal mismatch")
    _check(action["label"] == label, "primitive label mismatch")
    _check(action["kind"] == kind, "primitive kind mismatch")
    _check(_index(action, "target_index") == target_index, "primitive target mismatch")
    _check(_row_tuple(action["before"], "action.before") == current, "primitive before mismatch")

    target = target_index - 1
    next_rows = list(current)
    if kind == "invert":
        _check(donor_index is None and conjugator is None, "invert metadata mismatch")
        next_rows[target] = inverse(next_rows[target])
    elif kind == "multiply":
        _check(conjugator is None and donor_index is not None, "multiply metadata mismatch")
        _check(_index(action, "donor_index") == donor_index, "primitive donor mismatch")
        donor = donor_index - 1
        _check(donor != target, "primitive multiplies a row by itself")
        next_rows[target] = free_reduce(next_rows[target] + next_rows[donor])
    elif kind == "conjugate":
        _check(donor_index is None and isinstance(conjugator, str), "conjugate metadata mismatch")
        _check(action["conjugator"] == conjugator, "primitive conjugator mismatch")
        next_rows[target] = _conjugated(conjugator, next_rows[target])
    else:
        raise AssertionError(f"unknown primitive kind {kind!r}")

    computed = next_rows[0], next_rows[1], next_rows[2]
    _check(_row_tuple(action["after"], "action.after") == computed, "primitive after mismatch")
    return computed


def _expected_words() -> dict[str, str]:
    words = dict(BASE_WORDS)
    words["K"] = _commutator(words["u"], words["C"])
    words["D"] = _conjugated(words["h"], _commutator("X", words["r"]))
    _check(inverse(words["c"]) == words["C"], "C=c^-1 failed")
    _check(free_reduce(words["r"] + inverse(words["K"])) == words["A"], "A=rK^-1 failed")
    _check(free_reduce(words["q"] + inverse(words["D"])) == words["B"], "B=qD^-1 failed")
    return words


def _verify_transcript(literal: object) -> tuple[str, str, str]:
    transcript = _object(literal, "triangular_transcript")
    _check(
        set(transcript)
        == {"action_count", "actions", "endpoint", "kind_counts", "start"},
        "triangular transcript key set mismatch",
    )
    current = _row_tuple(transcript["start"], "transcript.start")
    _check(current == TRIANGLE_LEDGER[0], "triangular transcript start mismatch")
    actions = _list(transcript["actions"], "transcript.actions")
    _check(len(actions) == 9 and transcript["action_count"] == 9, "triangular transcript length mismatch")
    for ordinal, spec in enumerate(TRIANGLE, start=1):
        label, kind, target, donor, conjugator = spec
        current = _play_action(
            current,
            actions[ordinal - 1],
            ordinal=ordinal,
            label=label,
            kind=kind,
            target_index=target,
            donor_index=donor,
            conjugator=conjugator,
        )
        _check(current == TRIANGLE_LEDGER[ordinal], "triangular transcript state mismatch")
    _check(current == ("x", "y", "z"), "triangular transcript endpoint is not standard")
    _check(_row_tuple(transcript["endpoint"], "transcript.endpoint") == current, "stored triangular endpoint mismatch")
    _check(
        transcript["kind_counts"]
        == {"conjugate": 4, "invert": 2, "multiply": 3},
        "triangular kind counts mismatch",
    )
    return current


def _primitive_specs(
    branch_name: str,
    macro_ordinal: int,
    target: int,
    donor: int,
    conjugator: str,
    sign: int,
) -> tuple[tuple[str, str, int, int | None, str | None], ...]:
    specs: list[tuple[str, str, int, int | None, str | None]] = []

    def add(kind: str, action_target: int, action_donor: int | None, word: str | None) -> None:
        ordinal = len(specs) + 1
        specs.append(
            (
                f"{branch_name}.{macro_ordinal}.{ordinal}",
                kind,
                action_target,
                action_donor,
                word,
            )
        )

    if sign == -1:
        add("invert", donor, None, None)
    add("conjugate", donor, None, conjugator)
    add("multiply", target, donor, None)
    add("conjugate", donor, None, inverse(conjugator))
    if sign == -1:
        add("invert", donor, None, None)
    return tuple(specs)


def _verify_branches(
    literal: object,
) -> tuple[dict[str, list[str]], list[dict[str, Any]]]:
    branches = _object(literal, "branches")
    _check(set(branches) == {"S1", "S2"}, "branch names mismatch")
    words = _expected_words()
    common_start = (words["r"], words["q"], words["v"])
    endpoints = {
        "S1": (words["A"], words["q"], words["v"]),
        "S2": (words["r"], words["B"], words["v"]),
    }
    expected_branch_counts = {
        "S1": {"conjugate": 16, "invert": 8, "multiply": 8},
        "S2": {"conjugate": 4, "invert": 2, "multiply": 2},
    }
    all_primitives: list[dict[str, Any]] = []

    for branch_name in ("S1", "S2"):
        branch = _object(branches[branch_name], branch_name)
        _check(
            set(branch)
            == {
                "endpoint",
                "macro_count",
                "macros",
                "primitive_count",
                "primitive_kind_counts",
                "start",
            },
            f"{branch_name} key set mismatch",
        )
        current = _row_tuple(branch["start"], f"{branch_name}.start")
        _check(current == common_start, f"{branch_name} does not start at (r,q,v)")
        specs = BRANCH_SPECS[branch_name]
        macros = _list(branch["macros"], f"{branch_name}.macros")
        _check(len(macros) == len(specs), f"{branch_name} macro list length mismatch")
        primitive_counter: Counter[str] = Counter()

        for macro_ordinal, (literal_macro, spec) in enumerate(
            zip(macros, specs), start=1
        ):
            macro = _object(literal_macro, f"{branch_name}.macro")
            _check(
                set(macro)
                == {
                    "after",
                    "before",
                    "conjugator",
                    "donor_after",
                    "donor_before",
                    "donor_index",
                    "donor_restored",
                    "donor_sign",
                    "factor",
                    "ordinal",
                    "primitive_expansion",
                    "target_index",
                },
                "macro key set mismatch",
            )
            target, donor, conjugator, sign = spec
            _check(macro["ordinal"] == macro_ordinal, "macro ordinal mismatch")
            _check(_index(macro, "target_index") == target, "macro target mismatch")
            _check(_index(macro, "donor_index") == donor, "macro donor mismatch")
            _check(target != donor, "macro target equals donor")
            _check(macro["conjugator"] == conjugator, "macro conjugator mismatch")
            _check(type(macro["donor_sign"]) is int and macro["donor_sign"] == sign, "macro sign mismatch")
            _check(_row_tuple(macro["before"], "macro.before") == current, "macro before mismatch")

            donor_before = current[donor - 1]
            _check(macro["donor_before"] == donor_before, "macro donor-before mismatch")
            signed_donor = donor_before if sign == 1 else inverse(donor_before)
            expected_factor = _conjugated(conjugator, signed_donor)
            _check(macro["factor"] == expected_factor, "macro factor mismatch")
            expected_primitives = _primitive_specs(
                branch_name, macro_ordinal, target, donor, conjugator, sign
            )
            primitives = _list(macro["primitive_expansion"], "macro primitives")
            _check(len(primitives) == len(expected_primitives), "macro primitive length mismatch")

            for primitive_ordinal, (literal_action, primitive_spec) in enumerate(
                zip(primitives, expected_primitives), start=1
            ):
                label, kind, action_target, action_donor, action_conjugator = primitive_spec
                current = _play_action(
                    current,
                    literal_action,
                    ordinal=primitive_ordinal,
                    label=label,
                    kind=kind,
                    target_index=action_target,
                    donor_index=action_donor,
                    conjugator=action_conjugator,
                )
                primitive_counter[kind] += 1
                all_primitives.append(_object(literal_action, "primitive action"))

            _check(_row_tuple(macro["after"], "macro.after") == current, "macro after mismatch")
            _check(macro["donor_after"] == current[donor - 1], "macro donor-after mismatch")
            _check(macro["donor_after"] == donor_before, "macro donor was not restored")
            _check(macro["donor_restored"] is True, "macro restoration flag is not true")
            _check(
                current[target - 1]
                == free_reduce(_row_tuple(macro["before"], "macro.before")[target - 1] + expected_factor),
                "macro target is not right-multiplied by its factor",
            )

        _check(current == endpoints[branch_name], f"{branch_name} endpoint identity failed")
        _check(_row_tuple(branch["endpoint"], f"{branch_name}.endpoint") == current, f"{branch_name} stored endpoint mismatch")
        _check(branch["macro_count"] == len(specs), f"{branch_name} macro count mismatch")
        _check(branch["primitive_count"] == sum(primitive_counter.values()), f"{branch_name} primitive count mismatch")
        _check(dict(sorted(primitive_counter.items())) == expected_branch_counts[branch_name], f"{branch_name} primitive kind counts failed")
        _check(branch["primitive_kind_counts"] == expected_branch_counts[branch_name], f"{branch_name} stored primitive kind counts failed")

    return {name: list(endpoint) for name, endpoint in endpoints.items()}, all_primitives


def _verify_identities(literal: object, branches: dict[str, Any]) -> None:
    words = _expected_words()
    s1_factors = [macro["factor"] for macro in branches["S1"]["macros"]]
    s2_factors = [macro["factor"] for macro in branches["S2"]["macros"]]
    expected = {
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
            "factors": s1_factors[:4],
            "product": free_reduce("".join(s1_factors[:4])),
        },
        "C_inverse_of_c": {"expected": words["C"], "product": inverse(words["c"])},
        "D_inverse_factorization": {
            "expected": inverse(words["D"]),
            "factors": s2_factors,
            "product": free_reduce("".join(s2_factors)),
        },
        "K_inverse_factorization": {
            "expected": inverse(words["K"]),
            "factors": s1_factors,
            "product": free_reduce("".join(s1_factors)),
        },
    }
    _check(literal == expected, "identity ledger mismatch")
    for name, identity in expected.items():
        _check(identity["product"] == identity["expected"], f"literal identity failed: {name}")


def _verify_quotients(literal: object) -> None:
    words = _expected_words()
    expected = {
        "D_mod_A_v": {
            "defect": _substitute_v_trivial(words["D"]),
            "normal_closure_generators": ["A", "v"],
            "presentation": {
                "generators": ["x", "y"],
                "name": "Q_A",
                "relator": _substitute_v_trivial(words["A"]),
            },
            "status": "undecided",
        },
        "K_mod_B_v": {
            "defect": _substitute_v_trivial(words["K"]),
            "normal_closure_generators": ["B", "v"],
            "presentation": {
                "generators": ["x", "y"],
                "name": "Q_B",
                "relator": _substitute_v_trivial(words["B"]),
            },
            "status": "undecided",
        },
        "substitution": {"Z": "Xy", "relation": "v=1", "z": "Yx"},
    }
    _check(literal == expected, "rank-two quotient gate mismatch")
    _check(expected["D_mod_A_v"]["presentation"]["relator"] == "xYxYXyyXYxyXy", "Q_A relator mismatch")
    _check(expected["D_mod_A_v"]["defect"] == "YXyyXYxyxY", "Q_A defect mismatch")
    _check(expected["K_mod_B_v"]["presentation"]["relator"] == "XyyXYXyxYYxy", "Q_B relator mismatch")
    _check(expected["K_mod_B_v"]["defect"] == "YxYXyxYYxyXyyyXY", "Q_B defect mismatch")


def verify(certificate: object) -> dict[str, object]:
    root = _object(certificate, "certificate")
    _check(set(root) == TOP_LEVEL_KEYS, "certificate top-level key set mismatch")
    _check(root["schema"] == SCHEMA, "certificate schema mismatch")
    _check(type(root["version"]) is int and root["version"] == VERSION, "certificate version mismatch")
    _check(root["words"] == _expected_words(), "literal pinned words mismatch")
    _check(
        root["convention"]
        == {
            "commutator": "[s,t]=s t s^-1 t^-1",
            "conjugation": "target := free_reduce(w target w^-1)",
            "multiplication": "target := free_reduce(target donor)",
            "reduction": "free only; no cyclic rotation or cyclic reduction",
            "row_indices": "1-based",
            "uppercase": "inverse",
        },
        "literal convention mismatch",
    )

    transcript_endpoint = _verify_transcript(root["triangular_transcript"])
    branch_endpoints, branch_primitives = _verify_branches(root["branches"])
    branches = _object(root["branches"], "branches")
    _verify_identities(root["identities"], branches)
    _verify_quotients(root["quotient_gates"])
    _check(root["nonclaims"] == NONCLAIMS, "nonclaim ledger mismatch")

    transcript_actions = _list(
        _object(root["triangular_transcript"], "transcript")["actions"],
        "transcript.actions",
    )
    all_kinds = Counter(
        action["kind"] for action in [*transcript_actions, *branch_primitives]
    )
    expected_counts = {
        "branch_macros": 10,
        "conjugations": all_kinds["conjugate"],
        "inversions": all_kinds["invert"],
        "multiplications": all_kinds["multiply"],
        "total_primitives": len(transcript_actions) + len(branch_primitives),
        "transcript_actions": len(transcript_actions),
    }
    _check(
        expected_counts
        == {
            "branch_macros": 10,
            "conjugations": 24,
            "inversions": 12,
            "multiplications": 13,
            "total_primitives": 49,
            "transcript_actions": 9,
        },
        "replayed action counts mismatch",
    )
    _check(root["counts"] == expected_counts, "stored action counts mismatch")

    return {
        "branch_endpoints": branch_endpoints,
        "branch_macros": {"S1": 8, "S2": 2},
        "total_primitives": 49,
        "transcript_actions": 9,
        "transcript_endpoint": list(transcript_endpoint),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Independently replay the MMS02 donor certificate"
    )
    parser.add_argument("certificate", type=Path)
    args = parser.parse_args()
    literal = json.loads(args.certificate.read_text(encoding="utf-8"))
    print(json.dumps(verify(literal), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
