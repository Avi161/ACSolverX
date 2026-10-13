"""The Python entry to the kernels for other searches (hybrid, CoV, n-generator, tests)."""
import numpy as np

from .encoding import encode
from .expand import child_width, expand, expand_drops, max_children
from .score import priority_id, score


def children(rels, n_gen=2, cap=24, cyclic=True, priority="length", drops=False):
    """The scored children of one canonical state (``cap=None`` is uncapped).

    Returns ``(syms, lens, moves, scores, rejected)``; child ``c`` is ``decode(syms[c], lens[c], n_gen)``, reached
    by ``Move(*moves[c])``. With ``drops`` it appends ``(dsyms, dlens, dscores)``: the children the cap dropped,
    one per cut-shift repeat class (``expand_drops``), for the cap counters.
    """
    syms, lens = encode(rels, n_gen)
    rows = max(max_children(lens), 1)
    width = max(child_width(lens), syms.shape[1])
    out = np.zeros((rows, len(lens), width), dtype=np.uint8)
    out_len = np.zeros((rows, len(lens)), dtype=np.int32)
    out_mv = np.zeros((rows, 5), dtype=np.int32)
    kernel_cap = -1 if cap is None else cap
    pid = priority_id(priority, rels)
    if drops:
        dout = np.zeros((rows, len(lens), width), dtype=np.uint8)
        dout_len = np.zeros((rows, len(lens)), dtype=np.int32)
        dprio = np.zeros(rows, dtype=np.float64)
        count, rejected, dcount, _, _ = expand_drops(syms, lens, n_gen, kernel_cap, cyclic, out, out_len, out_mv,
                                                     dout, dout_len, dprio, pid, np.inf, True)
    else:
        count, rejected = expand(syms, lens, n_gen, kernel_cap, cyclic, out, out_len, out_mv)
    scores = np.array([score(out[c], out_len[c], n_gen, pid) for c in range(count)])
    result = (out[:count], out_len[:count], out_mv[:count], scores, rejected)
    if drops:
        result += (dout[:dcount], dout_len[:dcount], dprio[:dcount])
    return result
