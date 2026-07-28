from experiments.stable_ac.depth4_pronilpotent_certificate import (
    pronilpotent_base_certificate,
)


def test_full_kernel_equation_has_the_claimed_laurent_target_base() -> None:
    certificate = pronilpotent_base_certificate()

    assert certificate.source_a_laurent == (
        (0, -1),
        (4, -1),
        (6, 1),
        (7, -1),
        (10, 1),
        (11, -1),
    )
    assert certificate.source_b_laurent == ((0, -1), (7, 1), (8, -1))
    assert certificate.h3_laurent == (
        (0, 1),
        (1, 1),
        (2, 2),
        (3, 2),
        (4, 1),
        (5, 1),
        (8, -1),
        (11, 1),
    )
    assert certificate.laurent_augmentations == (-2, -1, -1, 0, -1, 1)
    assert certificate.laurent_target == ((0, 1),)


def test_period_two_specialization_reaches_the_target_through_class_two() -> None:
    certificate = pronilpotent_base_certificate()

    assert certificate.source_a_word == (-1, -1, -2, -2, 1, 1)
    assert certificate.source_b_word == (-1, -1, -1, 2, 1)
    assert certificate.source_a_vector == (0, -2)
    assert certificate.source_b_vector == (-2, 1)
    assert certificate.g0_vector == (-1, 1)
    assert certificate.r_vector == (0, -1)
    assert certificate.s_vector == (-1, 1)
    assert certificate.u_vector == (-1, 0)
    assert certificate.z_vector == (1, 0)
    assert certificate.z_class_two_coordinate == (1, 0, 4)
    assert certificate.class_two_target_coordinate == (1, 0, 4)


def test_laurent_base_can_hit_every_shifted_target_letter() -> None:
    for target_index in (-7, 0, 13):
        certificate = pronilpotent_base_certificate(target_index)
        assert certificate.laurent_target == ((target_index, 1),)
