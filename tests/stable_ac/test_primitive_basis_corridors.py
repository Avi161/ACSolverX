import pytest

from experiments.stable_ac.rank3_compression.primitive_certificate import (
    build_certificate,
    verify_certificate,
)
from experiments.stable_ac.rank3_compression.primitive_bases import (
    NielsenMove,
    apply_basis,
    apply_nielsen,
    enumerate_bases,
    nielsen_reduce,
    primitive_basis_classes,
    replay_nielsen,
    signed_pair_key,
)


AK3 = ("xxxYYYY", "xyxYXY")


def _is_signed_standard(pair):
    return (
        len(pair[0]) == len(pair[1]) == 1
        and pair[0].lower() != pair[1].lower()
    )


def test_nielsen_witness_reduces_a_basis():
    moves = nielsen_reduce(("x", "xy"))
    assert moves is not None
    assert _is_signed_standard(replay_nielsen(("x", "xy"), moves))


def test_nielsen_rejects_nonbasis():
    assert nielsen_reduce(("xx", "y")) is None


def test_nielsen_rejects_letters_outside_rank_two_basis():
    with pytest.raises(ValueError, match="only x and y"):
        nielsen_reduce(("x", "z"))


def test_nielsen_replay_strictly_decreases_length():
    start = ("xy", "x")
    moves = nielsen_reduce(start)
    assert moves is not None
    state = start
    for move in moves:
        child = apply_nielsen(state, move)
        assert sum(map(len, child)) < sum(map(len, state))
        state = child
    assert _is_signed_standard(state)


def test_bad_nielsen_move_is_rejected():
    with pytest.raises(ValueError, match="target"):
        apply_nielsen(("x", "y"), NielsenMove(2, "right", 1))


def test_complete_total_four_basis_ball():
    bases = enumerate_bases(4)
    assert len(bases) == 200
    assert all(sum(map(len, row.basis)) <= 4 for row in bases)
    assert all(
        _is_signed_standard(replay_nielsen(row.basis, row.moves))
        for row in bases
    )


def test_apply_basis_is_simultaneous():
    assert apply_basis(("xY", "yx"), ("xy", "X")) == ("xyx", "y")


def test_apply_basis_rejects_invalid_image_alphabet():
    with pytest.raises(ValueError, match="only x and y"):
        apply_basis(AK3, ("x", "z"))


def test_total_four_basis_classes():
    classes = primitive_basis_classes(AK3, 4)
    assert len(classes) == 9
    assert sorted(len(cls.members) for cls in classes) == [
        16,
        16,
        16,
        16,
        24,
        24,
        24,
        24,
        40,
    ]
    assert sum(len(cls.members) for cls in classes) == 200


def test_signed_renaming_preserves_key():
    pair = apply_basis(AK3, ("x", "xy"))
    renamed = apply_basis(pair, ("Y", "x"))
    assert signed_pair_key(pair) == signed_pair_key(renamed)


def test_small_primitive_certificate_replays():
    data = build_certificate(
        max_basis_total=2,
        max_word_length=2,
        max_template_length=4,
    )
    assert data["schema"] == "ak3-primitive-basis-corridors-v1"
    assert data["basis_count"] == 8
    assert data["class_count"] == 1
    verify_certificate(data)
