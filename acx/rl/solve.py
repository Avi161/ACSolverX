"""Policy beam search as an ``acx`` solver: row in, ``acx`` S-move path out, replayed by ``acx.verify``.

The reduced presentation is encoded as the environment observation (relator order and rotation as given: the policy was
trained on dataset rows, not canonical forms) and every environment action is translated into the ``acx`` S-move that
gives the same state up to rotation and inversion (``acx.rl.codec``). A solution counts only after ``replay`` accepts it
on the row.
"""
import time

from ..core.capcount import blank
from ..core.config import require_int
from ..core.words import as_presentation, reduce
from ..search.engine import Result
from ..verify.replay import replay
from . import L
from .beam import beam_search
from .codec import encode, to_acx_path
from .policy import pretrained


def solve(pres, model=None, width=1024, steps=150, alpha=0.0, cap=L):
    """Beam-search ``pres`` (a ``Presentation`` or relator strings); the path is replay-verified.

    ``pops`` counts the states scored by the network. ``cap`` limits every child (``acx.rl.beam``) and
    the replay; it must be at most ``L = 24``, the policy's observation width (``None`` raises: the
    network cannot see a longer relator). Rows with other than two generators, or a relator longer than
    ``cap``, come back unsolved with ``stats["skipped"]`` set.
    """
    if require_int(cap, "cap") > L:
        raise ValueError(f"acx.rl needs cap <= {L} (the policy's observation width), got {cap}")
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
