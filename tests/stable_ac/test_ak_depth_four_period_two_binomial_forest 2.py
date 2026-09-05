from experiments.stable_ac.depth4_period_two_binomial_forest_certificate import (
    period_two_binomial_forest_certificate,
)


def test_binomial_subgroup_has_the_exact_rs_kernel_basis() -> None:
    certificate = period_two_binomial_forest_certificate()

    assert certificate.ambient_generators == ("p", "(qPQp)c", "(qPPq)c")
    assert certificate.rs_kernel_generators == (
        "p",
        "qPPqPqpQ",
        "qPQpqPqpQ",
        "qPQppQPq",
        "qPQppQQp",
    )


def test_stallings_core_proves_the_rs_images_have_rank_five() -> None:
    certificate = period_two_binomial_forest_certificate()

    assert certificate.core_vertices == 4
    assert certificate.core_undirected_edges == 8
    assert certificate.core_rank == 5
    assert certificate.core_directed_edges == 16
    assert certificate.core_sha256 == "b1b76817d3ec409ca12fbe52e9c7765727936b33b2fc33d8132279e2abba1dfe"


def test_three_binomial_operators_have_no_finite_support_syzygy() -> None:
    certificate = period_two_binomial_forest_certificate()

    assert certificate.free_rank_three
    assert certificate.torsion_free
    assert certificate.incidence_graph_is_forest
    assert certificate.finite_support_kernel_is_zero
