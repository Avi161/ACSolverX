import json

import pytest

from experiments.search import ac_decode
from experiments.search.ac_decode import decode_elementary, replay_elementary
from experiments.search.cascade_heuristics import search
from experiments.search.decode_ac_jsonl import (
    decode_file, pack_move, replay_packed, unpack_move,
)


PAIR = ("YYXyx", "Yx")


def _mixed_solve():
    got = search(PAIR, budget=20, cap=255, starter_budget=500,
                 rewrite_budget=1000, intermediate_cap=None)
    assert got["solved"]
    assert any(step["kind"] == "automorphism" for step in got["steps"])
    return got


def test_mixed_path_decodes_without_bridge_search(monkeypatch):
    got = _mixed_solve()
    monkeypatch.setattr(ac_decode, "bridge", lambda *a, **k: (_ for _ in ()).throw(
        AssertionError("elementary decoding must not search")))
    moves = decode_elementary(PAIR, got["states"], got["steps"])
    assert replay_elementary(PAIR, moves) == ["x", "y"]
    assert {move["op"] for move in moves} <= {
        "invert", "swap", "conjugate", "multiply"}
    assert all(len(move.get("by", "x")) == 1 for move in moves)


def test_elementary_replay_rejects_unknown_and_non_generator_operations():
    with pytest.raises(ValueError, match="unknown"):
        replay_elementary(PAIR, [{"op": "automorphism"}])
    with pytest.raises(ValueError, match="one generator"):
        replay_elementary(PAIR, [{"op": "conjugate", "target": 1, "by": "xy"}])
    with pytest.raises(ValueError, match="target"):
        replay_elementary(PAIR, [{"op": "invert", "target": 0}])
    with pytest.raises(ValueError, match="distinct"):
        replay_elementary(PAIR, [{"op": "multiply", "target": 1, "source": 1}])


def test_jsonl_has_one_verified_elementary_record_per_input(tmp_path):
    got = _mixed_solve()
    source = tmp_path / "mixed.jsonl"
    output = tmp_path / "elementary.jsonl"
    source.write_text(json.dumps({
        "pres_id": 7, "r1": PAIR[0], "r2": PAIR[1], "solved": True,
        "winner": got["winner"], "states": got["states"], "steps": got["steps"],
    }) + "\n" + json.dumps({
        "pres_id": 8, "r1": "xx", "r2": "yy", "solved": False,
    }) + "\n")
    summary = decode_file(source, output)
    rows = [json.loads(line) for line in output.read_text().splitlines()]
    assert summary["rows"] == 2 and summary["solved"] == summary["decoded"] == 1
    assert [row["pres_id"] for row in rows] == [7, 8]
    assert rows[0]["replay_verified"] and rows[0]["final_state"] == ["x", "y"]
    assert rows[0]["schema"] == "elementary_ac_v1"
    assert len(rows[0]["source_sha256"]) == 64
    assert replay_packed(PAIR, rows[0]["elementary_moves"]) == ["x", "y"]
    assert rows[1]["decoded"] is False and rows[1]["elementary_moves"] == []


def test_tampered_mixed_state_is_rejected():
    got = _mixed_solve()
    states = [list(state) for state in got["states"]]
    states[1] = ["Y", "X"]
    with pytest.raises((AssertionError, ValueError)):
        decode_elementary(PAIR, states, got["steps"])


def test_failed_decode_never_leaves_a_plausible_final_jsonl(tmp_path):
    source = tmp_path / "bad.jsonl"
    output = tmp_path / "elementary.jsonl"
    output.write_text("old\n")
    source.write_text(json.dumps({
        "pres_id": 1, "r1": "x", "r2": "y", "solved": True,
        "states": [["Y", "X"]], "steps": [{"kind": "bad"}],
    }) + "\n")
    with pytest.raises(ValueError):
        decode_file(source, output)
    assert output.read_text() == "old\n"
    assert not (tmp_path / "elementary.jsonl.partial").exists()


def test_jsonl_decode_rejects_input_as_output(tmp_path):
    source = tmp_path / "runs.jsonl"
    original = json.dumps({"pres_id": 1, "solved": False, "r1": "x", "r2": "y"}) + "\n"
    source.write_text(original)
    with pytest.raises(ValueError, match="must differ"):
        decode_file(source, source)
    assert source.read_text() == original


def test_jsonl_temp_file_cannot_collide_with_source(tmp_path):
    source = tmp_path / "elementary.jsonl.partial"
    output = tmp_path / "elementary.jsonl"
    original = json.dumps({
        "pres_id": 1, "solved": False, "r1": "x", "r2": "y",
    }) + "\n"
    source.write_text(original)
    assert decode_file(source, output)["rows"] == 1
    assert source.read_text() == original
    assert json.loads(output.read_text())["pres_id"] == 1


def test_packed_move_round_trip_and_validation():
    moves = [
        {"op": "invert", "target": 1}, {"op": "swap"},
        {"op": "conjugate", "target": 2, "by": "X"},
        {"op": "multiply", "target": 1, "source": 2},
    ]
    assert [unpack_move(pack_move(move)) for move in moves] == moves
    with pytest.raises(ValueError, match="invalid packed"):
        unpack_move(["C", 1])


def test_campaign_path_shape_is_accepted(tmp_path):
    source = tmp_path / "campaign.jsonl"
    output = tmp_path / "elementary.jsonl"
    source.write_text(json.dumps({
        "name": "terminal", "r1": "x", "r2": "y", "solved": True,
        "path": [["Y", "X"]], "path_moves": [],
    }) + "\n")
    assert decode_file(source, output)["decoded"] == 1
    row = json.loads(output.read_text())
    assert row["pres_id"] == "terminal"
    assert replay_packed(("x", "y"), row["elementary_moves"]) == ["x", "y"]
