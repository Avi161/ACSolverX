"""Helper boxes split by presentation: a partition, and the same path sample as a full run."""

import pytest

from experiments.stable_ac.rank3 import aws_rank3_split_helpers as S
from experiments.stable_ac.rank3 import words as W


def test_groups_partition_the_presentations():
    g = S.groups(640)
    assert sorted(i for ids in g for i in ids) == list(range(640))
    assert [len(ids) for ids in g] == [216, 216, 208]


@pytest.mark.parametrize("n", range(1, 11))
def test_sample_fraction_is_the_full_runs(n):
    full = min(1.0, S.FULL_TARGET / (W.n_words(n) * 640))
    for ids in S.groups(640):
        k = len(ids)
        assert min(1.0, S.target(k) / (W.n_words(n) * k)) == full


def test_target_refuses_a_group_size_that_changes_the_fraction():
    with pytest.raises(AssertionError):
        S.target(213)


def test_rendered_script_runs_its_own_presentations_and_log():
    src = open(S.HELPER).read()
    for name, ids in zip("ABC", S.groups(640)):
        out = S.render(src, name, ids)
        assert f"run_arm{name}.log" in out and S.LOG not in out
        flags = f"--path-sample-target {S.target(len(ids))} --pres {','.join(map(str, ids))} )"
        assert out.count(flags) == 1
        assert len(out.splitlines()) == len(src.splitlines()) + 1
