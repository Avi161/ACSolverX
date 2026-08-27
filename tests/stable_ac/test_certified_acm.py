import hashlib
import json
from pathlib import Path

from experiments.stable_ac.supermoves.certified_acm import (
    ACMCertificate,
    NormalFactor,
    apply_certified_acm,
    atomic_move_bound,
    bounded_acm_successors,
    certified_target_word,
    commutator_wrap_certificate,
    cyclic_key,
    cyclic_reduce,
    expand_atomic_moves,
    free_reduce,
    inverse,
    replay_atomic_moves,
)
from experiments.stable_ac.supermoves.aca124_acm_census import census_rows


def test_exact_target_and_atomic_replay_agree():
    source = ("YXXyxYx", "YYYYYYXyxyX")
    certificate = ACMCertificate(
        target_index=0,
        source_exponent=-1,
        source_conjugator="xy",
        factors=(
            NormalFactor(1, 1, "X"),
            NormalFactor(1, -1, "yx"),
        ),
    )
    expected = apply_certified_acm(source, certificate)
    moves = expand_atomic_moves(source, certificate)
    assert replay_atomic_moves(source, moves) == expected
    assert expected[0] == certified_target_word(source, certificate)
    assert expected[1] == source[1]
    assert len(moves) == atomic_move_bound(certificate) == 13


def test_bounded_generator_returns_only_replayable_targets():
    source = ("YXXyxYx", "YYYYYYXyxyX")
    successors = bounded_acm_successors(
        source,
        target_index=0,
        max_width=3,
        max_conjugator_length=1,
        beam_size=48,
        relator_cap=64,
    )
    assert len(successors) >= 48
    assert any(len(item.certificate.factors) >= 2 for item in successors)
    for successor in successors:
        moves = expand_atomic_moves(source, successor.certificate)
        assert len(moves) == successor.atomic_bound
        assert replay_atomic_moves(source, moves) == successor.relators


def test_generator_works_without_triviality_or_thickenability_assumptions():
    source = ("xyXY", "xxxy")
    successors = bounded_acm_successors(
        source,
        target_index=1,
        max_width=2,
        max_conjugator_length=1,
        beam_size=16,
    )
    assert successors
    assert all(item.relators[0] == source[0] for item in successors)


def test_exhaustive_bounded_family_and_universal_example():
    source = ("x", "y")
    successors = bounded_acm_successors(
        source,
        target_index=0,
        max_width=1,
        max_conjugator_length=0,
        beam_size=None,
    )
    assert len(successors) == 2

    certificate = commutator_wrap_certificate(source, 0, 1)
    target = apply_certified_acm(source, certificate)
    assert target == ("xyXYx", "y")
    assert replay_atomic_moves(
        source, expand_atomic_moves(source, certificate)
    ) == target
    commutator = free_reduce(
        target[0] + target[1] + inverse(target[0]) + inverse(target[1])
    )
    assert len(commutator) == 12
    assert atomic_move_bound(certificate) == 6


def test_exhaustive_mode_does_not_prune_prefixes():
    source = ("x", "y")
    successors = bounded_acm_successors(
        source,
        target_index=0,
        max_width=2,
        max_conjugator_length=1,
        beam_size=None,
        generators=("x", "y"),
    )
    assert len(successors) == 12
    keys = {cyclic_key(item.relators[0]) for item in successors}
    certificate = ACMCertificate(
        0,
        source_exponent=-1,
        factors=(NormalFactor(1, -1), NormalFactor(1, -1, "x")),
    )
    assert cyclic_key(certified_target_word(source, certificate)) in keys
    assert cyclic_reduce("XYXYx") == "YXY"


def test_census_replays_every_action_and_records_orbit_escape():
    rows = [{"name": "toy", "r1": "x", "r2": "y"}]

    def deliberately_separating_key(pair):
        return sum(map(len, pair)), pair

    payload = census_rows(
        rows,
        deliberately_separating_key,
        max_width=2,
        max_conjugator_length=1,
        beam_size=16,
        relator_cap=20,
    )
    assert payload["summary"]["class_count"] == 1
    assert payload["summary"]["replay_failures"] == 0
    assert payload["summary"]["classes_with_nonautomorphic_action"] == 1


def test_persisted_aca124_census_and_aca0_witness():
    root = Path(__file__).resolve().parents[2]
    path = root / "results/stable_ac/theory/aca124_witnessed_acm.json"
    payload = json.loads(path.read_text())
    claimed_hash = payload.pop("payload_sha256")
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    assert hashlib.sha256(encoded.encode()).hexdigest() == claimed_hash
    assert payload["summary"] == {
        "class_count": 124,
        "classes_with_actions": 124,
        "classes_with_nonautomorphic_action": 124,
        "replay_failures": 0,
        "total_distinct_actions": 40876,
    }
    aca0 = next(row for row in payload["records"] if row["name"] == "aca_0")
    witness = aca0["first_nonautomorphic"]
    assert witness["target"] == ["YXXyxYx", "YYYYYYXyXyxY"]
    assert witness["atomic_bound"] == 3
    assert witness["target_representative"] != aca0["source_representative"]
