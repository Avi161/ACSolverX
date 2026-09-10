"""One search call = one verified cost.

``cost(pair, budget, cap, config)`` runs ``greedy_search_hcompact`` (``config=None`` is the
plain length-ordered greedy, ``S20_MK2`` the shipped heuristic) and, when the engine claims
a solve, replays the returned moves through ``words.replay_move`` -- pure Python, never the
engine's own replay -- from ``canon_pair(pair)``; a claim that does not end on two distinct
single letters raises ``ReplayError``.  Node counts are heap pops.

``verify_from_original(orig_pair, seq, path_moves)`` is the full-chain check for an atlas
record: apply the automorphism sequence one Whitehead automorphism at a time
(``apply_pair``), then replay the moves, and demand the trivial presentation at the end.
It uses nothing from the engine and nothing from ``orbit.ball``'s bookkeeping.

Set ``OMP_NUM_THREADS=1 NUMBA_NUM_THREADS=1`` in the environment before importing; the
first call in a process pays ~1-2 s of JIT warmup (``warmup()``).
"""
import os
import sys
from pathlib import Path

os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('NUMBA_NUM_THREADS', '1')

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from experiments.equivalence_classes.lib.autcanon import AUTOS  # noqa: E402
from experiments.equivalence_classes.lib.words import apply_pair, canon_pair, replay_move  # noqa: E402
from experiments.search.heuristics import S20_MK2  # noqa: E402,F401  (re-exported for callers)

CONFIGS = {'greedy': None, 's20': S20_MK2}


class ReplayError(RuntimeError):
    """The engine claimed a solve that the independent replay rejects."""


def is_trivial(state):
    a, b = state
    return len(a) == 1 and len(b) == 1 and a.lower() != b.lower()


def parse_move(m):
    return tuple(int(v) for v in m.split('_'))


MAX_REPLAY_LEN = 512   # no state of a cap-64 certificate is longer; beyond this the replay is off-track


def replay(pair, path_moves, max_len=MAX_REPLAY_LEN):
    """Replay ``path_moves`` from ``canon_pair(pair)``; returns the final state.

    A certificate replayed from the wrong start never cancels and doubles in length every
    move, so the replay stops (and returns the oversized state, which is not trivial) as soon
    as a relator exceeds ``max_len``.
    """
    state = canon_pair(*pair)
    for m in path_moves:
        state = replay_move(state, parse_move(m) if isinstance(m, str) else tuple(m))
        if max(len(state[0]), len(state[1])) > max_len:
            break
    return state


def cost(pair, budget, cap=48, config=None):
    """``{solved, nodes, path_moves, max_expanded}`` for one search; raises ReplayError."""
    from experiments.heuristic_search.core.hcompact import greedy_search_hcompact
    r1, r2 = pair
    res = greedy_search_hcompact(r1, r2, budget, max_relator_length=cap, config=config,
                                 track_path=True)
    solved = bool(res['solved'])
    moves = list(res['path_moves']) if solved else []
    if solved:
        end = replay(pair, moves)
        if not is_trivial(end):
            raise ReplayError(f'{pair}: engine claimed a solve, replay ends on {end}')
    return {'solved': solved, 'nodes': int(res['nodes_explored']), 'path_moves': moves,
            'max_expanded': int(res['max_relator_length_expanded'])}


def verify_from_original(orig_pair, seq, path_moves):
    """True iff applying ``AUTOS[i]`` for ``i in seq`` (elementary steps) to ``orig_pair`` and
    then replaying ``path_moves`` ends on the trivial presentation."""
    state = canon_pair(*orig_pair)
    for i in seq:
        state = apply_pair(state, AUTOS[i])
    return is_trivial(replay(state, path_moves))


def warmup():
    """Pay the numba JIT cost once per process, on both arms."""
    for cfg in CONFIGS.values():
        cost(('YXyx', 'YYxx'), 50, cap=48, config=cfg)
