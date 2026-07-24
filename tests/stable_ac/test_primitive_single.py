from experiments.stable_ac.rank3_compression.primitive_single import (
    enumerate_primitive_single_removals,
    remove_primitive_relator,
)
from experiments.stable_ac.rank3_compression.rank3_whitehead import (
    reduce_word,
)


def test_handcrafted_primitive_relator_removes_to_standard_pair():
    rank3 = ("xz", "z", "t")
    reduction = reduce_word(rank3[0])
    transformed, eliminated, output = remove_primitive_relator(
        rank3,
        relator_index=0,
        reduction=reduction,
    )
    assert len(transformed[0]) == 1
    assert eliminated in "xzt"
    assert output == ("X", "Yx")


def test_explicit_single_source_census_is_deterministic():
    sources = (("xz", "z", "t"),)
    first = enumerate_primitive_single_removals(
        sources=sources,
        upstream_trace="test",
    )
    second = enumerate_primitive_single_removals(
        sources=sources,
        upstream_trace="test",
    )
    assert first == second
    assert first.relators_tested == 3
    assert first.primitive_occurrence_count == 3
    assert first.minimum_output_floor == 2
