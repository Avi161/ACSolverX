from experiments.stable_ac.mms02_path_gauge_conjugacy_certificate import (
    decide_path_gauge_conjugacy,
)


def test_path_gauge_hnn_rewrite_forces_one_base_conjugator():
    decision = decide_path_gauge_conjugacy()
    assert decision.base_relator == "bdAbDBaD"
    assert decision.source_normal == "yaD"
    assert decision.target_normal == "yAd"
    assert decision.forced_b_power == 2
    assert decision.forced_base_conjugator == "BB"


def test_path_gauge_class_two_shadow_selects_the_forced_conjugator():
    decision = decide_path_gauge_conjugacy()
    assert decision.rank_three_relator_coordinate == (1, 0, -1, 0, 0, 0)
    assert decision.class_two_source == (0, 1, 1)
    assert decision.class_two_target == (0, 1, -1)
    assert decision.class_two_forced_conjugate == decision.class_two_target


def test_path_gauge_forced_conjugator_fails_in_the_free_base_factor():
    decision = decide_path_gauge_conjugacy()
    assert decision.forced_condition_defect == "aDbbDA"
    assert decision.free_factor_defect == "DbbD"


def test_path_gauge_nonconjugacy_scope_is_pinned():
    decision = decide_path_gauge_conjugacy()
    assert decision.source_abelianization == (0, -1)
    assert decision.target_abelianization == (0, 1)
    assert decision.verdict == "PATH_GAUGE_ROWS_NOT_CONJUGATE_UP_TO_INVERSION"
