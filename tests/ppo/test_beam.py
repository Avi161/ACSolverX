"""Beam decode: the kills that keep it honest, and the resume contract.

Every budget here obeys the repo cap -- `beam_width * max_steps <= 1000` -- so
nothing in this file can turn into a production search by accident.
"""

import json

import numpy as np
import pytest

torch = pytest.importorskip("torch")

from experiments.ppo import acs_data, acs_spec                       # noqa: E402
from experiments.ppo.beam import (                                   # noqa: E402
    beam_search_one, decode_path, make_hash_vec, repair_jsonl, run_beam, summarise)
from experiments.ppo.policy import RelativeDualRingActorCritic       # noqa: E402
from experiments.ppo.run_ppo import LOCAL_EXPANSION_CAP              # noqa: E402

L = 24


@pytest.fixture(scope="module")
def model():
    torch.manual_seed(0)
    return RelativeDualRingActorCritic(max_len=L).eval()


@pytest.fixture(scope="module")
def presentations():
    return acs_data.load_presentations("AC19_extended", L)


def test_budgets_here_respect_the_local_cap():
    assert 16 * 40 <= LOCAL_EXPANSION_CAP
    assert 8 * 30 <= LOCAL_EXPANSION_CAP


def test_a_found_path_replays_to_the_trivial_presentation(model, presentations):
    dev = torch.device("cpu")
    x = torch.as_tensor(presentations, dtype=torch.int64, device=dev)
    hv = make_hash_vec(x.shape[1], dev)
    gen = torch.Generator(device=dev)
    gen.manual_seed(0)

    found = 0
    for idx in range(40):
        solved, plen, path = beam_search_one(
            model, x[idx], hv, beam_width=16, max_steps=40, generator=gen)
        if not solved:
            continue
        found += 1
        assert plen == len(path)
        state = presentations[idx].astype(int).tolist()
        for a in path:
            state, _, term = acs_spec.step(state, a, L)
        assert term, f"beam path for {idx} does not end trivial"
        assert len(decode_path(path, L)) == plen
    assert found > 0, "no presentation solved; fixture no longer exercises this path"


def test_a_solved_beam_reports_the_step_it_solved_on(model, presentations):
    dev = torch.device("cpu")
    x = torch.as_tensor(presentations, dtype=torch.int64, device=dev)
    hv = make_hash_vec(x.shape[1], dev)
    for idx in range(40):
        solved, plen, path = beam_search_one(model, x[idx], hv, beam_width=16, max_steps=40)
        if solved:
            assert 1 <= plen <= 40
            # truncating the path by one must NOT already be trivial
            state = presentations[idx].astype(int).tolist()
            for a in path[:-1]:
                state, _, term = acs_spec.step(state, a, L)
            assert plen == 1 or not term
            return
    pytest.skip("no solve in the fixture window")


def test_noop_actions_cannot_survive(model):
    """A move the env silently rejects must kill its beam, not farm log-prob."""
    dev = torch.device("cpu")
    # x^-1 y x y^-1 style start: long enough that most concatenations overflow
    row = [1] * 20 + [0] * 4 + [2] * 20 + [0] * 4
    x0 = torch.tensor(row, dtype=torch.int64, device=dev)
    hv = make_hash_vec(48, dev)
    solved, plen, path = beam_search_one(model, x0, hv, beam_width=8, max_steps=30)
    state = row
    for a in path:
        nxt, _, _ = acs_spec.step(state, a, L)
        assert nxt != state, "a no-op reached the recorded path"
        state = nxt


def test_run_beam_is_resumable_and_appends_jsonl(model, presentations, tmp_path):
    out = tmp_path / "beam.jsonl"
    first = run_beam(model, presentations, str(out), start=0, end=6, beam_width=8,
                     max_steps=30, progress=lambda *_: None)
    assert first["attempted"] == 6
    rows = [json.loads(l) for l in open(out) if l.strip()]
    assert [r["presentation_idx"] for r in rows] == list(range(6))

    again = run_beam(model, presentations, str(out), start=0, end=6, beam_width=8,
                     max_steps=30, progress=lambda *_: None)
    assert again["attempted"] == 0, "resume must skip presentations already recorded"
    assert len(open(out).readlines()) == 6

    grown = run_beam(model, presentations, str(out), start=0, end=9, beam_width=8,
                     max_steps=30, progress=lambda *_: None)
    assert grown["attempted"] == 3
    summary = summarise(str(out))
    assert summary["rows"] == 9
    assert 0 <= summary["solved"] <= 9


def test_a_torn_trailing_line_is_repaired_before_the_next_append(model, presentations, tmp_path):
    """Tolerating the stub at read time is NOT enough -- it must be truncated.

    Left in place the stub has no newline, so the next appended row lands on the
    same line and a recoverable truncated-final line becomes a corrupt interior
    line that no later read can undo.
    """
    out = tmp_path / "torn.jsonl"
    run_beam(model, presentations, str(out), start=0, end=3, beam_width=8,
             max_steps=30, progress=lambda *_: None)
    with open(out, "a") as fh:
        fh.write('{"presentation_idx": 3, "sol')
    result = run_beam(model, presentations, str(out), start=0, end=4, beam_width=8,
                      max_steps=30, progress=lambda *_: None)
    assert result["attempted"] == 1
    assert summarise(str(out))["rows"] == 4
    rows = [json.loads(l) for l in open(out)]
    assert [r["presentation_idx"] for r in rows] == [0, 1, 2, 3]


def test_repair_truncates_only_an_unterminated_tail(tmp_path):
    intact = tmp_path / "intact.jsonl"
    intact.write_text('{"a": 1}\n{"a": 2}\n')
    assert repair_jsonl(str(intact), progress=lambda *_: None) == 0
    assert intact.read_text() == '{"a": 1}\n{"a": 2}\n'

    torn = tmp_path / "torn.jsonl"
    torn.write_text('{"a": 1}\n{"a": 2}\n{"a"')
    assert repair_jsonl(str(torn), progress=lambda *_: None) == 4
    assert torn.read_text() == '{"a": 1}\n{"a": 2}\n'

    only = tmp_path / "only.jsonl"
    only.write_text('{"a"')
    assert repair_jsonl(str(only), progress=lambda *_: None) == 4
    assert only.read_text() == ""

    assert repair_jsonl(str(tmp_path / "absent.jsonl"), progress=lambda *_: None) == 0


def test_summarise_reports_mean_path_length_over_solves_only(tmp_path):
    out = tmp_path / "s.jsonl"
    with open(out, "w") as fh:
        for i, (s, n) in enumerate([(True, 4), (False, -1), (True, 10)]):
            fh.write(json.dumps({"presentation_idx": i, "solved": s, "path_length": n}) + "\n")
    got = summarise(str(out))
    assert got["rows"] == 3 and got["solved"] == 2
    assert np.isclose(got["mean_path_length"], 7.0)
