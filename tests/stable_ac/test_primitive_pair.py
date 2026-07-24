from experiments.stable_ac.rank3_compression.primitive_pair import (
    AK3,
    enumerate_primitive_pair_corridors,
)
from experiments.stable_ac.rank3_compression.rank3_whitehead import (
    check_reduction,
)


def test_small_primitive_pair_census_is_complete_and_replayable():
    census = enumerate_primitive_pair_corridors(
        AK3,
        max_word_length=2,
        max_template_length=4,
    )
    assert census.distinct_cyclic_rank3_count == 88
    assert census.tested_relator_pair_count == 264
    assert census.distinct_relator_pair_count > 0
    assert sum(census.minimum_distribution.values()) == 264
    for row in census.primitive_rows:
        check_reduction(row.pair, row.reduction)
