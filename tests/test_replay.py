"""acx.verify.replay: every solved path replays; broken paths are rejected."""
import json

import pytest

from acx.core.config import SearchConfig
from acx.core.moves import Move, decode_path, encode_path, to_legacy
from acx.core.words import Presentation
from acx.search import search
from acx.verify import ReplayError, abs_det, replay


@pytest.mark.parametrize("priority", ["length", "s20_mk2"])
def test_every_solved_path_replays(ms640, priority):
    solved = 0
    for pres in ms640[:400:10]:
        r = search(pres, SearchConfig(priority=priority, budget=300, capture_path=True))
        if r.solved:
            solved += 1
            states = replay(pres, r.path, cap=24)
            assert states[0] == r.start and states[-1] == r.end
            assert len(states) == r.path_length + 1
    assert solved >= 30


def test_legacy_and_json_paths_replay(ms640):
    pres = ms640[322]
    r = search(pres, budget=300)
    legacy = ["_".join(map(str, to_legacy(m))) for m in r.path]       # main's path_moves strings
    assert replay(pres, decode_path(legacy))[-1] == r.end
    assert decode_path(json.loads(json.dumps(encode_path(r.path)))) == list(r.path)


def test_broken_paths_are_rejected(ms640):
    pres = ms640[322]
    path = list(search(pres, budget=300).path)
    m = path[3]
    with pytest.raises(ReplayError, match="illegal"):
        replay(pres, path[:3] + [m._replace(k2=(m.k2 + 1) % 40)] + path[4:])
    with pytest.raises(ReplayError, match="non-trivial"):
        replay(pres, path[:-1])
    with pytest.raises(ReplayError, match="cap"):
        replay(pres, path, cap=8)
    with pytest.raises(ReplayError, match="det"):
        replay(Presentation.parse("xx", "y"), [])
    with pytest.raises(ReplayError, match="illegal"):
        replay(pres, [Move(0, 0, 1, 0, 0)])


def test_elementary_and_stable_paths():
    p = Presentation.parse("xy", "y")
    path = [{"op": "invert", "target": 2}, {"op": "multiply", "target": 1, "source": 2},
            {"op": "conjugate", "target": 1, "by": "Y"}, {"op": "swap"}]
    states = replay(p, path, normalize=False)
    assert states[-1].strs == ("Y", "yxY") and states[-1].is_trivial()
    z_out = [{"op": "invert", "target": 3}, {"op": "multiply", "target": 1, "source": 3},
             {"op": "invert", "target": 3}]
    stable = [{"op": "stabilize"}, {"op": "multiply", "target": 1, "source": 3}] + z_out
    states = replay(p, stable + [{"op": "destabilize"}] + path, normalize=False)
    assert [s.n_gen for s in states[:3]] == [2, 3, 3] and states[2].strs == ("xyz", "y", "z")
    bad = stable + [{"op": "multiply", "target": 3, "source": 2}, {"op": "destabilize"}]
    with pytest.raises(ReplayError, match="illegal"):
        replay(p, bad, normalize=False, require_trivial=False)
    with pytest.raises(ReplayError):
        abs_det(Presentation.parse("x", "y", "x"))
