"""acx.verify.replay: every solved path replays; broken paths are rejected."""
import itertools
import json
import random

import pytest

from acx.core.config import SearchConfig
from acx.core.moves import Move, decode_path, elementary_step, encode_path
from acx.core.words import Presentation
from acx.search import search
from acx.verify import ReplayError, abs_det, replay
from acx.verify.replay import det


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
    legacy = [f"{m.i + 1}_{m.s}_{m.k1}_{m.k2}" for m in r.path]       # the baseline's path_moves strings
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


def leibniz(m):
    """The determinant as the signed sum over permutations."""
    n = len(m)
    total = 0
    for perm in itertools.permutations(range(n)):
        inversions = sum(perm[i] > perm[j] for i in range(n) for j in range(i + 1, n))
        product = 1
        for row, col in enumerate(perm):
            product *= m[row][col]
        total += (-1) ** inversions * product
    return total


def test_det_matches_leibniz():
    """The fraction-free elimination equals the sum over permutations, zeros and row swaps included."""
    rng = random.Random(0)
    for _ in range(2000):
        n = rng.randint(1, 5)
        m = [[rng.randint(-4, 4) for _ in range(n)] for _ in range(n)]
        assert det(m) == leibniz(m), m
    assert det([]) == 1


# Each way an elementary move can be malformed, on <x, y | xy, y>, with the words of the error it must raise.
MALFORMED = [
    pytest.param({"op": "teleport"}, "unknown move", id="unknown op"),
    pytest.param({"op": "invert", "target": 0}, "out of range", id="invert target 0"),
    pytest.param({"op": "invert", "target": True}, "out of range", id="invert target True"),
    pytest.param({"op": "invert", "target": 3}, "out of range", id="invert target 3"),
    pytest.param({"op": "conjugate", "target": 1, "by": "xy"}, "one generator", id="conjugate by two letters"),
    pytest.param({"op": "conjugate", "target": 1, "by": "z"}, "one generator", id="conjugate by a third generator"),
    pytest.param({"op": "swap", "a": 1, "b": 3}, "out of range", id="swap with a third relator"),
    pytest.param({"op": "multiply", "target": 1, "source": 1}, "distinct", id="multiply by itself"),
    pytest.param({"op": "destabilize"}, "still occurs", id="destabilize a generator in use"),
    pytest.param({"op": "invert"}, "needs 'target'", id="invert without target"),
    pytest.param({"op": "conjugate", "by": "x"}, "needs 'target'", id="conjugate without target"),
    pytest.param({"op": "conjugate", "target": 1}, "needs 'by'", id="conjugate without letter"),
    pytest.param({"op": "multiply", "source": 2}, "needs 'target'", id="multiply without target"),
    pytest.param({"op": "multiply", "target": 1}, "needs 'source'", id="multiply without source"),
]


@pytest.mark.parametrize("op, message", MALFORMED)
def test_elementary_step_refuses_every_malformed_op(op, message):
    """A malformed move is a ``ValueError`` saying what is wrong (never a bare ``KeyError``), and a path holding it
    is simply not valid."""
    p = Presentation.parse("xy", "y")
    with pytest.raises(ValueError, match=message):
        elementary_step(p, op)
    with pytest.raises(ReplayError):
        replay(p, [op], normalize=False, require_trivial=False)
