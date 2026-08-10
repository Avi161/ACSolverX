"""The verifier must FAIL on tampered certificates, or it certifies nothing.

Modelled on `tests/stable_ac/test_verify_results.py`: build a real beam jsonl,
confirm it verifies, then damage it one way at a time and require each damage to
be caught. A verifier that only ever passes is decoration.
"""

import json

import pytest

torch = pytest.importorskip("torch")

from experiments.ppo import acs_data, acs_spec                        # noqa: E402
from experiments.ppo.beam import run_beam                             # noqa: E402
from experiments.ppo.policy import RelativeDualRingActorCritic        # noqa: E402
from experiments.ppo.verify_beam import (                             # noqa: E402
    dataset_and_length, main, verify_file)

L = 24
STEM = "AC19_extended"


@pytest.fixture(scope="module")
def presentations():
    return acs_data.load_presentations(STEM, L)


@pytest.fixture
def beam_file(tmp_path, presentations):
    """A genuine run, named exactly as `beam_tag` would name it."""
    torch.manual_seed(0)
    model = RelativeDualRingActorCritic(max_len=L).eval()
    out = tmp_path / f"beam-610model_params-{STEM}-w8-t30-L{L}.jsonl"
    run_beam(model, presentations, str(out), start=0, end=10, beam_width=8,
             max_steps=30, progress=lambda *_: None)
    return out


def _rows(path):
    return [json.loads(l) for l in open(path) if l.strip()]


def _rewrite(path, rows):
    with open(path, "w") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")


def test_the_dataset_comes_from_the_filename(beam_file):
    assert dataset_and_length(str(beam_file)) == (STEM, L)


def test_an_unparseable_name_refuses_instead_of_guessing(tmp_path):
    stray = tmp_path / "my-run.jsonl"
    stray.write_text("")
    with pytest.raises(ValueError, match="not a beam jsonl name"):
        dataset_and_length(str(stray))
    assert dataset_and_length(str(stray), dataset=STEM, max_length=L) == (STEM, L)


def test_a_real_run_verifies(beam_file):
    got = verify_file(str(beam_file), log=lambda *_: None)
    assert got["failures"] == []
    assert got["solved"] > 0, "fixture no longer exercises the solved path"
    assert got["verified"] == got["solved"]
    assert main([str(beam_file)]) == 0


def test_a_tampered_path_is_caught(beam_file):
    """The core property: a path that does not replay to trivial must fail."""
    rows = _rows(beam_file)
    solved = next(r for r in rows if r["solved"])
    solved["path"] = [(solved["path"][0] + 1) % (2 * 2 * L * L)] + solved["path"][1:]
    _rewrite(beam_file, rows)
    got = verify_file(str(beam_file), log=lambda *_: None)
    assert any("does not reach a trivial" in why for _, _, why in got["failures"])
    assert main([str(beam_file)]) == 1


def test_a_solve_claimed_with_no_moves_is_caught(beam_file):
    rows = _rows(beam_file)
    solved = next(r for r in rows if r["solved"])
    solved["path"] = []
    _rewrite(beam_file, rows)
    got = verify_file(str(beam_file), log=lambda *_: None)
    assert got["failures"], "an empty path cannot certify a solve"


def test_a_path_length_that_disagrees_with_the_moves_is_caught(beam_file):
    rows = _rows(beam_file)
    solved = next(r for r in rows if r["solved"])
    solved["path_length"] = solved["path_length"] + 3
    _rewrite(beam_file, rows)
    got = verify_file(str(beam_file), log=lambda *_: None)
    assert any("path_length" in why for _, _, why in got["failures"])


def test_a_path_that_solves_early_and_wanders_back_is_caught(beam_file, presentations):
    """Ending trivial is not enough -- the path must not have solved sooner.

    The beam returns on its first termination, so it cannot emit such a row; a
    mis-gathered `seqs[parent]` could. It over-reports `path_length`, which is
    the paper's second published column, while the solve count still looks right.

    Building one needs a genuine excursion: a single appended move cannot do it,
    because a trivial presentation has no S-move back to itself (concatenating
    two distinct generators can never cancel to length 2), so an appended move
    trips the reach-trivial check instead. Search for a two-move round trip.
    """
    rows = _rows(beam_file)
    solved = next(r for r in rows if r["solved"])
    state = [int(v) for v in presentations[solved["presentation_idx"]]]
    for a in solved["path"]:
        state, _, _ = acs_spec.step(state, int(a), L)

    excursion = None
    for a in range(2 * 2 * L * L):
        left, _, _ = acs_spec.step(list(state), a, L)
        if left == state:                                   # a no-op never leaves
            continue
        for b in range(2 * 2 * L * L):
            back, _, term = acs_spec.step(list(left), b, L)
            if term:
                excursion = [a, b]
                break
        if excursion:
            break
    assert excursion, "no two-move round trip out of the trivial presentation"

    solved["path"] = solved["path"] + excursion
    solved["path_length"] = len(solved["path"])
    _rewrite(beam_file, rows)
    got = verify_file(str(beam_file), log=lambda *_: None)
    assert any("prefix" in why for _, _, why in got["failures"])


def test_a_single_appended_move_is_caught_too(beam_file):
    """The cheap over-long case, and it reports the move the path really solved on.

    Tracking the FIRST termination is what makes this a prefix diagnosis rather
    than a bare "does not end trivial": the row's real cost is recoverable from
    the failure message.
    """
    rows = _rows(beam_file)
    solved = next(r for r in rows if r["solved"])
    real_cost = solved["path_length"]
    solved["path"] = solved["path"] + [solved["path"][-1]]
    solved["path_length"] = len(solved["path"])
    _rewrite(beam_file, rows)
    got = verify_file(str(beam_file), log=lambda *_: None)
    assert any(f"at move {real_cost} of {real_cost + 1}" in why
               for _, _, why in got["failures"])


def test_an_unsolved_row_carrying_a_path_is_caught(beam_file):
    rows = _rows(beam_file)
    unsolved = next((r for r in rows if not r["solved"]), None)
    if unsolved is None:
        pytest.skip("fixture solved everything")
    unsolved["path"] = [0, 1]
    _rewrite(beam_file, rows)
    got = verify_file(str(beam_file), log=lambda *_: None)
    assert any("unsolved row carries a path" in why for _, _, why in got["failures"])


def test_a_row_indexing_outside_the_evaluation_set_is_caught(beam_file):
    rows = _rows(beam_file)
    rows[0]["presentation_idx"] = 10 ** 9
    _rewrite(beam_file, rows)
    got = verify_file(str(beam_file), log=lambda *_: None)
    assert any("outside" in why for _, _, why in got["failures"])


def test_corrupt_json_is_a_failure_not_a_silent_skip(beam_file):
    with open(beam_file, "a") as fh:
        fh.write('{"presentation_idx": 99, "solv\n')
    got = verify_file(str(beam_file), log=lambda *_: None)
    assert any("not valid json" in why for _, _, why in got["failures"])
