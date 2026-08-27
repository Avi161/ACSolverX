from __future__ import annotations

import copy
import importlib.util
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / ".scratch/period_two_inverse_pure_increment_checker.py"


def load_checker():
    spec = importlib.util.spec_from_file_location(
        "tested_inverse_pure_increment_checker", CHECKER
    )
    if spec is None or spec.loader is None:
        raise RuntimeError(CHECKER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def assert_rejected(checker, manifest, mutate) -> None:
    changed = copy.deepcopy(manifest)
    mutate(changed)
    assert checker.verification_failures(changed)


def main() -> None:
    checker = load_checker()

    parser_failed = False
    try:
        checker.argument_parser().parse_args(["--write", "--check"])
    except SystemExit:
        parser_failed = True
    assert parser_failed

    manifest = checker.build_manifest()
    assert checker.verification_failures(manifest) == []
    assert manifest["format"] == "period-two-inverse-pure-increment-direct-q-v3"
    assert len(manifest["cells"]) == 12
    assert len(manifest["cell_results"]) == 12
    assert len(manifest["provenance"]) == 92
    assert len({row["id"] for row in manifest["provenance"]}) == 92
    assert all(
        len(checker.matching_cells(e, n)) == 1
        for e in range(8)
        for n in range(8)
    )
    assert manifest["raw_parser_guard"] == {
        "raw_p": "tc",
        "raw_p_inverse": "cT",
        "module_parser_p": "t",
    }
    schemas = {schema["id"]: schema for schema in manifest["schemas"]}
    first_path_schema = schemas[manifest["provenance"][0]["module_schema"]]
    first_slot_zero_schema = schemas["inverse:slot0:delta0:module"]
    assert (
        first_slot_zero_schema["normal_form"]["q_core"]
        == first_path_schema["normal_form"]["q_core"]
    )
    assert (
        first_slot_zero_schema["normal_form"]["p_core"]
        == first_path_schema["normal_form"]["p_core"]
    )
    assert [cell["base_n"] for cell in manifest["cells"] if cell["n"] == "ge3"] == [
        3,
        3,
        3,
    ]

    pump_count = 0
    for result in manifest["cell_results"]:
        assert result["collision"]["active_fiber_count"] == 36
        assert result["collision"]["active_slot_profile"] == {
            "2": 8,
            "3": 14,
            "4": 14,
        }
        assert result["coordinate_count"] == 38
        assert len(result["tokens"]) == 84
        assert len({token["id"] for token in result["tokens"]}) == 84
        assert len(result["raw_records"]) == 72
        assert len(result["quadratic"]["pairs"]) == 3486
        assert result["quadratic"]["pair_count"] == 3486
        assert result["computed"]["Phi"] == 1
        assert result["computed"]["remaining_scalar"] == int(
            result["cell"]["e"] != 0
        )
        replay = result["direct_base_semantic_replay"]
        assert replay["token_count"] == 84
        assert not replay["coordinate_failures"]
        assert not replay["extra_coordinates"]
        assert not replay["label_failures"]
        assert not replay["raw_failures"]
        assert not replay["pair_failures"]
        assert all(replay["totals_match"].values())
        for raw in result["raw_records"]:
            assert raw["base"]["rho"] == sum(
                not equality for equality in raw["base"]["equalities"]
            ) % 2
            for pump in raw["pumps"]:
                pump_count += 1
                assert pump["primitive_core_shield"]
                assert pump["one_step_signature_matches"]
                assert pump["core_length"] == 8
                if pump["variable"] == "n":
                    assert pump["block"] == "p"
                    assert pump["base_exponent"] >= 9
        pair_ids = {
            f"pair:{left['id']}|{right['id']}"
            for index, left in enumerate(result["tokens"])
            for right in result["tokens"][index + 1 :]
        }
        assert pair_ids == {
            pair["id"] for pair in result["quadratic"]["pairs"]
        }
        assert all(
            checker.recompute_pair_bit(pair) == pair["bit"]
            for pair in result["quadratic"]["pairs"]
        )
    assert pump_count == 7 * 72

    assert_rejected(
        checker,
        manifest,
        lambda changed: changed["raw_parser_guard"].__setitem__("raw_p", "t"),
    )
    assert_rejected(
        checker,
        manifest,
        lambda changed: changed["cell_results"][8]["raw_records"][0]["pumps"][0].__setitem__(
            "primitive_core_shield", False
        ),
    )
    assert_rejected(
        checker,
        manifest,
        lambda changed: changed["cell_results"][0]["collision"]["fibers"][0]["members"].pop(),
    )
    assert_rejected(
        checker,
        manifest,
        lambda changed: changed["cell_results"][0]["tokens"].pop(),
    )
    assert_rejected(
        checker,
        manifest,
        lambda changed: changed["cell_results"][0]["quadratic"]["pairs"].pop(),
    )
    assert_rejected(
        checker,
        manifest,
        lambda changed: changed["cell_results"][0]["raw_records"][0]["base"].__setitem__(
            "rho", changed["cell_results"][0]["raw_records"][0]["base"]["rho"] ^ 1
        ),
    )
    assert_rejected(
        checker,
        manifest,
        lambda changed: changed["cell_results"][0]["quadratic"]["pairs"][0].__setitem__(
            "bit", changed["cell_results"][0]["quadratic"]["pairs"][0]["bit"] ^ 1
        ),
    )
    assert_rejected(
        checker,
        manifest,
        lambda changed: changed["cell_results"][0]["computed"].__setitem__(
            "Phi", changed["cell_results"][0]["computed"]["Phi"] ^ 1
        ),
    )
    print("PASS: period-two inverse pure-increment checker tests")


if __name__ == "__main__":
    main()
