"""Policy beam search as an ``acx`` solver: row in, ``acx`` S-move path out, replayed by ``acx.verify``.

The reduced presentation is encoded as the environment observation (relator order and rotation as given: the policy was
trained on dataset rows, not canonical forms) and every environment action is translated into the ``acx`` S-move that
gives the same state up to rotation and inversion. A solution counts only after ``replay`` accepts it on the row.
"""
import time

import torch

from ..core.capcount import blank
from ..core.moves import apply_raw, enumerate_moves
from ..core.words import Presentation, canonical_rels, canonical_word, reduce
from ..search.engine import Result, as_presentation
from ..verify.replay import replay
from . import L
from .beam import beam_search
from .moves import decode_action, s_move
from .policy import pretrained


def encode(rels, L=L):
    """Two relator words of length at most ``L`` -> ``(2L,)`` observation."""
    if len(rels) != 2 or max(map(len, rels)) > L:
        raise ValueError(f"the environment takes two relators of length <= {L}: {rels}")
    return torch.tensor([g for r in rels for g in r + (0,) * (L - len(r))], dtype=torch.int64)


def decode(x, L=L):
    """Inverse of ``encode``: the two relators of an observation."""
    return tuple(tuple(int(g) for g in x[k * L:(k + 1) * L] if g) for k in (0, 1))


def to_acx_path(pres, actions, L=L, cyclic=True):
    """The ``acx`` S-move path equivalent to the environment ``actions`` on ``pres``.

    Each environment child is matched to the ``acx`` move of the current canonical state whose reduced
    canonical child is the same pair of relators (``ValueError`` if none: a no-op or a bad seam).
    """
    x = encode(tuple(reduce(r, cyclic) for r in pres.rels), L)
    cur, path = pres.reduced(cyclic).canonical(), []
    for t, a in enumerate(actions):
        x = s_move(x[None], *decode_action(torch.tensor([a]), L), L)[0][0]
        want = canonical_rels(tuple(reduce(r, cyclic) for r in decode(x, L)))
        for m in enumerate_moves(cur.rels):
            raw = apply_raw(cur.rels, m)
            if canonical_word(reduce(raw[m.i], cyclic)) in want:         # cheap test before the full child
                child = canonical_rels(tuple(reduce(r, cyclic) for r in raw))
                if child == want:
                    path.append(m)
                    cur = Presentation(cur.n_gen, child)
                    break
        else:
            raise ValueError(f"action {t} ({a}) is not an S-move of {cur}")
    return path


def solve(pres, model=None, width=1024, steps=150, alpha=0.0, cap=L):
    """Beam-search ``pres`` (a ``Presentation`` or relator strings); the path is replay-verified.

    ``pops`` counts the states scored by the network. ``cap`` limits every child (``acx.rl.beam``) and
    the replay; it must be at most ``L = 24``, the policy's observation width (``None`` raises: the
    network cannot see a longer relator). Rows with other than two generators, or a relator longer than
    ``cap``, come back unsolved with ``stats["skipped"]`` set.
    """
    if cap is None or not 0 < cap <= L:
        raise ValueError(f"acx.rl needs 0 < cap <= {L} (the policy's observation width), got {cap}")
    pres = as_presentation(pres)
    start, rels = pres.reduced().canonical(), tuple(reduce(r) for r in pres.rels)
    t0, stats = time.perf_counter(), dict(backend="rl-beam", width=width, steps=steps, alpha=alpha, cap=cap)
    actions = None
    if start.is_trivial():
        actions = []
        stats.update(blank(cap=cap))
    elif pres.n_gen != 2 or len(rels) != 2 or not all(0 < len(r) <= cap for r in rels):
        stats["skipped"] = "needs 2 generators and 2 nonempty relators of length <= cap"
        stats.update(blank(cap=cap))
    else:
        actions, beam_stats = beam_search(model or pretrained(), encode(rels), L=L, cap=cap,
                                          width=width, steps=steps, alpha=alpha)
        stats.update(beam_stats)
    path = end = None
    if actions is not None:
        path = tuple(to_acx_path(pres, actions)) if actions else ()
        end = replay(pres, path, cap=cap)[-1]
    stats["seconds"] = time.perf_counter() - t0
    return Result(path is not None, stats.get("evaluated", 0), path, start, end, stats)
