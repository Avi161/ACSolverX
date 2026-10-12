"""Translation between an ``acx`` presentation and the environment: the observation and the actions.

The policy sees a ``(2L,)`` int tensor ``[r1 | r2]`` and acts by flat actions (``acx.rl.moves``). ``to_acx_path`` turns
a list of such actions into the ``acx`` S-moves that give the same states up to rotation and inversion.
"""
import torch

from ..core.moves import apply_raw, enumerate_moves
from ..core.words import Presentation, canonical_rels, canonical_word, reduce
from . import L
from .moves import decode_action, s_move


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
    current, path = pres.reduced(cyclic).canonical(), []
    for step, action in enumerate(actions):
        x = s_move(x[None], *decode_action(torch.tensor([action]), L), L)[0][0]
        want = canonical_rels(tuple(reduce(r, cyclic) for r in decode(x, L)))
        for move in enumerate_moves(current.rels):
            raw = apply_raw(current.rels, move)
            if canonical_word(reduce(raw[move.i], cyclic)) in want:      # cheap test before the full child
                child = canonical_rels(tuple(reduce(r, cyclic) for r in raw))
                if child == want:
                    path.append(move)
                    current = Presentation(current.n_gen, child)
                    break
        else:
            raise ValueError(f"action {step} ({action}) is not an S-move of {current}")
    return path
