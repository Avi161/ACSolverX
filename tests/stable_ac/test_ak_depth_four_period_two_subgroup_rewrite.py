from experiments.stable_ac.depth4_period_two_subgroup_rewrite_certificate import (
    CORE,
    CORE_BASE,
    path_between,
    subgroup_rewrite_certificate,
)
from experiments.stable_ac import depth4_period_two_degree_two_escape_certificate as escape


def test_complete_cover_and_fixed_paths() -> None:
    certificate = subgroup_rewrite_certificate()

    assert certificate.core_vertices == 4
    assert certificate.core_directed_edges == 16
    assert certificate.core_free_rank == 5
    assert certificate.fixed_paths == (
        ("ctcTcttct", "aGbaGaGbAA", "tt"),
        ("ttct", "aaBgA", "ctcTctt"),
        ("", "aaBgA", "ctcTctcTT"),
        ("ctcT", "aGaGbA", "tcTT"),
    )


def test_depth_six_k_words_round_trip() -> None:
    certificate = subgroup_rewrite_certificate()

    assert certificate.depth_six_words_checked == 127
    assert certificate.depth_six_k_elements > 0
    assert certificate.depth_six_round_trips == certificate.depth_six_k_elements
