"""acx.verify.decode: substitution paths become elementary AC paths that replay on the raw row."""
import json

import pytest

from acx.core.config import SearchConfig
from acx.core.moves import Move, enumerate_moves, stabilize, step
from acx.core.words import Presentation, canonical_rels, inverse, is_cyclically_reduced
from acx.search import search
from acx.verify import ReplayError, replay
from acx.verify.decode import decode, decode_and_replay, pack, unpack


@pytest.fixture(scope="module")
def solves(ms640):
    """The first 60 MS640 rows the spec backend solves at budget 500 (default cap 24): ``(pres, path)``."""
    out = []
    for pres in ms640:
        r = search(pres, SearchConfig(budget=500))
        if r.solved:
            out.append((pres, r.path))
        if len(out) == 60:
            break
    assert len(out) == 60
    return out


def test_ms640_solves_decode_and_replay(solves):
    sub = elem = 0
    for pres, path in solves:
        moves, states = decode_and_replay(pres, path)
        assert states[0] == pres and states[-1].is_trivial()
        it = iter(states)                                     # every search state, in order, is a decoded state
        assert all(any(s == c for s in it) for c in replay(pres, path))
        assert {m["op"] for m in moves} <= {"invert", "swap", "conjugate", "multiply"}
        assert all(m["by"] in "xyXY" for m in moves if m["op"] == "conjugate")
        sub, elem = sub + len(path), elem + len(moves)
    print(f"\ndecoded {len(solves)} MS640 solves: {sub} substitution moves -> {elem} elementary moves "
          f"({elem / sub:.2f} per substitution move)")
    assert elem >= sub


def test_decoded_end_is_canonical_trivial_and_json_safe(solves):
    pres, path = solves[7]
    moves, states = decode_and_replay(pres, path)
    assert json.loads(json.dumps(moves)) == moves
    assert states[-1].rels == replay(pres, path)[-1].rels
    assert unpack(json.loads(json.dumps(pack(moves)))) == moves
    assert replay(pres, unpack(pack(moves)), normalize=False)[-1].is_trivial()


def test_non_canonical_and_unreduced_starts(solves):
    pres, path = solves[3]
    shuffled = Presentation(2, (inverse(pres.rels[1]), pres.rels[0]))
    r = search(shuffled, SearchConfig(budget=500))
    assert r.solved and r.start == pres.reduced().canonical()
    assert replay(shuffled, decode(shuffled, r.path), normalize=False)[-1].is_trivial()
    with pytest.raises(ValueError, match="freely reduced"):
        decode(Presentation(2, ((1, -1, 2), (2,))), [])


def test_mixed_path_with_elementary_and_stable_moves(solves):
    pres, path = solves[5]
    mixed = [{"op": "invert", "target": 1}, {"op": "swap"}, {"op": "stabilize"}, {"op": "destabilize"},
             *path[:1], {"op": "invert", "target": 2}, *path[1:]]
    assert replay(pres, mixed)[-1].is_trivial()
    moves, states = decode_and_replay(pres, mixed)
    assert states[-1].is_trivial() and {"op": "stabilize"} in moves and {"op": "swap"} in moves
    assert unpack(json.loads(json.dumps(pack(moves)))) == moves


def test_s_move_after_a_dict_move_that_breaks_cyclic_reduction(solves):
    """The S-move then indexes ``canonical_rels`` of words that are not cyclically reduced (``_frame``)."""
    conj = {"op": "conjugate", "target": 1, "by": "x"}
    pres = next(p for p, _ in solves if not all(map(is_cyclically_reduced, step(p.reduced().canonical(), conj).rels)))
    rels = step(pres.reduced().canonical(), conj).rels
    done = 0
    for m in list(enumerate_moves(canonical_rels(rels)))[:20]:
        mid = replay(pres, [conj, m], require_trivial=False)[-1]
        assert replay(pres, decode(pres, [conj, m]), normalize=False, require_trivial=False)[-1] == mid
        r = search(mid, SearchConfig(budget=500))
        if r.solved:
            moves, states = decode_and_replay(pres, [conj, m, *r.path])
            done += states[-1].is_trivial()
    assert done


def test_three_generators(solves):
    pres = stabilize(solves[2][0])
    r = search(pres, SearchConfig(budget=3000))
    assert r.solved and pres.n_gen == 3
    moves, states = decode_and_replay(pres, r.path)
    assert states[-1].is_trivial() and states[-1].n_gen == 3


def test_illegal_and_incomplete_paths_are_refused(solves):
    pres, path = solves[4]
    with pytest.raises(ValueError):
        decode(pres, [Move(0, 0, 1, 0, 0)])
    with pytest.raises(ReplayError, match="non-trivial"):
        decode_and_replay(pres, path[:-1])
