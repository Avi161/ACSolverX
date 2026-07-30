from __future__ import annotations

import ast
import copy
import importlib.util
import json
from pathlib import Path
from types import ModuleType

import pytest


ROOT = Path(__file__).resolve().parents[1]
GENERATOR_PATH = ROOT / ".scratch/mms02_sequential_donor_factorization_certificate.py"
VERIFIER_PATH = ROOT / ".scratch/verify_mms02_sequential_donor_factorization.py"
CERTIFICATE_PATH = (
    ROOT / ".scratch/mms02_sequential_donor_factorization_certificate.json"
)

PINNED_WORDS = {
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

QUOTIENTS = {
    "D_mod_A_v": {
        "name": "Q_A",
        "relator": "xYxYXyyXYxyXy",
        "defect": "YXyyXYxyxY",
    },
    "K_mod_B_v": {
        "name": "Q_B",
        "relator": "XyyXYXyxYYxy",
        "defect": "YxYXyxYYxyXyyyXY",
    },
}


def load_module(path: Path, name: str) -> ModuleType:
    assert path.is_file(), f"missing implementation artifact: {path.name}"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def modules() -> tuple[ModuleType, ModuleType]:
    return (
        load_module(GENERATOR_PATH, "mms02_sequential_donor_generator_under_test"),
        load_module(VERIFIER_PATH, "mms02_sequential_donor_verifier_under_test"),
    )


@pytest.fixture()
def certificate(modules: tuple[ModuleType, ModuleType]) -> dict[str, object]:
    generator, _ = modules
    built = generator.build_certificate()
    assert isinstance(built, dict)
    return built


def assert_rejected(verifier: ModuleType, candidate: object) -> None:
    with pytest.raises((AssertionError, TypeError, ValueError, KeyError)):
        verifier.verify(candidate)


def test_generator_and_verifier_are_separate_implementations() -> None:
    assert GENERATOR_PATH.is_file(), "generator is absent"
    assert VERIFIER_PATH.is_file(), "independent verifier is absent"

    tree = ast.parse(VERIFIER_PATH.read_text(encoding="utf-8"))
    imported_modules = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported_modules.update(
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    )
    assert not any(
        "mms02_sequential_donor_factorization_certificate" in name
        for name in imported_modules
    )


def test_pinned_identities_and_exact_transcript(
    modules: tuple[ModuleType, ModuleType], certificate: dict[str, object]
) -> None:
    generator, verifier = modules
    assert {key: certificate["words"][key] for key in PINNED_WORDS} == PINNED_WORDS
    assert generator.inverse(PINNED_WORDS["c"]) == PINNED_WORDS["C"]

    transcript = certificate["triangular_transcript"]
    assert tuple(transcript["start"]) == TRANSCRIPT_STATES[0]
    assert tuple(transcript["endpoint"]) == TRANSCRIPT_STATES[-1]
    assert transcript["action_count"] == 9
    assert len(transcript["actions"]) == 9

    observed_states = [tuple(transcript["start"])]
    observed_specs = []
    for action in transcript["actions"]:
        observed_states.append(tuple(action["after"]))
        observed_specs.append(
            (
                action["label"],
                action["kind"],
                action["target_index"],
                action.get("donor_index"),
                action.get("conjugator"),
            )
        )
    assert tuple(observed_states) == TRANSCRIPT_STATES
    assert tuple(observed_specs) == TRANSCRIPT_SPECS

    generator.validate_certificate(certificate)
    summary = verifier.verify(certificate)
    assert summary["transcript_endpoint"] == ["x", "y", "z"]


def test_s1_and_s2_are_independent_restored_donor_branches(
    modules: tuple[ModuleType, ModuleType], certificate: dict[str, object]
) -> None:
    _, verifier = modules
    branches = certificate["branches"]
    s1 = branches["S1"]
    s2 = branches["S2"]
    common_start = [PINNED_WORDS["r"], PINNED_WORDS["q"], PINNED_WORDS["v"]]

    assert s1["start"] == common_start
    assert s2["start"] == common_start
    assert s1["endpoint"] == [PINNED_WORDS["A"], PINNED_WORDS["q"], PINNED_WORDS["v"]]
    assert s2["endpoint"] == [PINNED_WORDS["r"], PINNED_WORDS["B"], PINNED_WORDS["v"]]
    assert s1["macro_count"] == 8
    assert s2["macro_count"] == 2
    assert s1["primitive_count"] == 32
    assert s2["primitive_count"] == 8

    assert tuple(
        (
            macro["target_index"],
            macro["donor_index"],
            macro["conjugator"],
            macro["donor_sign"],
        )
        for macro in s1["macros"]
    ) == S1_SPECS
    assert tuple(
        (
            macro["target_index"],
            macro["donor_index"],
            macro["conjugator"],
            macro["donor_sign"],
        )
        for macro in s2["macros"]
    ) == S2_SPECS

    for branch in (s1, s2):
        for macro in branch["macros"]:
            expected_kinds = (
                ["conjugate", "multiply", "conjugate"]
                if macro["donor_sign"] == 1
                else ["invert", "conjugate", "multiply", "conjugate", "invert"]
            )
            assert [step["kind"] for step in macro["primitive_expansion"]] == expected_kinds
            assert macro["donor_restored"] is True
            assert macro["donor_before"] == macro["donor_after"]

    assert certificate["counts"] == {
        "branch_macros": 10,
        "conjugations": 24,
        "inversions": 12,
        "multiplications": 13,
        "total_primitives": 49,
        "transcript_actions": 9,
    }
    assert verifier.verify(certificate)["branch_endpoints"] == {
        "S1": [PINNED_WORDS["A"], PINNED_WORDS["q"], PINNED_WORDS["v"]],
        "S2": [PINNED_WORDS["r"], PINNED_WORDS["B"], PINNED_WORDS["v"]],
    }


def test_rank_two_quotient_gates_are_exact_and_undecided(
    modules: tuple[ModuleType, ModuleType], certificate: dict[str, object]
) -> None:
    _, verifier = modules
    gates = certificate["quotient_gates"]
    assert gates["substitution"] == {"relation": "v=1", "z": "Yx", "Z": "Xy"}
    for gate_name, expected in QUOTIENTS.items():
        gate = gates[gate_name]
        assert gate["presentation"] == {
            "generators": ["x", "y"],
            "name": expected["name"],
            "relator": expected["relator"],
        }
        assert gate["defect"] == expected["defect"]
        assert gate["status"] == "undecided"
    verifier.verify(certificate)


def test_independent_verifier_rejects_case_index_and_restoration_mutations(
    modules: tuple[ModuleType, ModuleType], certificate: dict[str, object]
) -> None:
    _, verifier = modules

    wrong_case = copy.deepcopy(certificate)
    wrong_case["words"]["A"] = wrong_case["words"]["A"].swapcase()
    assert_rejected(verifier, wrong_case)

    zero_based = copy.deepcopy(certificate)
    zero_based["triangular_transcript"]["actions"][0]["target_index"] = 0
    assert_rejected(verifier, zero_based)

    donor_drift = copy.deepcopy(certificate)
    donor_drift["branches"]["S1"]["macros"][1]["primitive_expansion"].pop()
    assert_rejected(verifier, donor_drift)

    concatenated = copy.deepcopy(certificate)
    concatenated["branches"]["S2"]["start"] = concatenated["branches"]["S1"]["endpoint"]
    assert_rejected(verifier, concatenated)


def test_independent_verifier_rejects_conflated_transcript(
    modules: tuple[ModuleType, ModuleType], certificate: dict[str, object]
) -> None:
    _, verifier = modules
    conflated = copy.deepcopy(certificate)
    s1 = conflated["branches"]["S1"]
    conflated["triangular_transcript"]["endpoint"] = copy.deepcopy(s1["endpoint"])
    conflated["triangular_transcript"]["actions"] = [
        copy.deepcopy(action)
        for macro in s1["macros"]
        for action in macro["primitive_expansion"]
    ]
    conflated["triangular_transcript"]["action_count"] = 32
    assert_rejected(verifier, conflated)


@pytest.mark.parametrize("gate_name", tuple(QUOTIENTS))
def test_independent_verifier_rejects_altered_quotient_defects(
    modules: tuple[ModuleType, ModuleType],
    certificate: dict[str, object],
    gate_name: str,
) -> None:
    _, verifier = modules
    altered = copy.deepcopy(certificate)
    altered["quotient_gates"][gate_name]["defect"] += "x"
    assert_rejected(verifier, altered)


def test_canonical_certificate_matches_generator_and_independent_replay(
    modules: tuple[ModuleType, ModuleType], certificate: dict[str, object]
) -> None:
    _, verifier = modules
    assert CERTIFICATE_PATH.is_file(), "canonical certificate is absent"
    raw = CERTIFICATE_PATH.read_bytes()
    assert raw.endswith(b"\n") and not raw.endswith(b"\n\n")
    literal = json.loads(raw)
    assert literal == certificate
    assert verifier.verify(literal) == {
        "branch_endpoints": {
            "S1": [PINNED_WORDS["A"], PINNED_WORDS["q"], PINNED_WORDS["v"]],
            "S2": [PINNED_WORDS["r"], PINNED_WORDS["B"], PINNED_WORDS["v"]],
        },
        "branch_macros": {"S1": 8, "S2": 2},
        "total_primitives": 49,
        "transcript_actions": 9,
        "transcript_endpoint": ["x", "y", "z"],
    }
