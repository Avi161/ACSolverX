"""Certificate transport: a solve of an automorphic image becomes an elementary AC path on the original row.

``transport`` carries a path over an automorphism with the ``Emitter`` (``emitter.py``), which writes the elementary
moves; ``solve_via_aut_min`` searches the Aut-minimal representative and transports the solve back to the row.
"""
from ..core.config import SearchConfig
from ..core.moves import Move, is_elementary
from ..core.words import canonical_rels
from ..verify.decode import decode
from ..verify.replay import replay
from .autos import AUTOS, apply_table, images, invert, sub_table
from .emitter import Emitter
from .whitehead import aut_canon


def transport(pres, phi, path, start, cyclic=True):
    """Elementary AC moves solving ``pres``, from ``path`` solving ``start`` ~ ``phi(pres)``.

    ``path`` replays from ``start`` exactly as given (``Result.start`` of the search that found it), and ``start`` is
    ``phi(pres)`` up to conjugating, inverting and reordering the relators. The result is replayed on ``pres``
    (``normalize=False``) before it is returned. With ``psi = phi^-1`` the current words stay exactly ``psi`` of the
    current state of ``path`` (freely reduced):

    * **align**: words equal to ``psi`` of the state up to conjugation, inversion and order are brought to it by
      ``swap``, ``invert`` and conjugation.
    * **S-move** ``r_i <- rot_k1(r_i) . rot_k2(r_j^s)``: the child is conjugate to ``r_i . c^-1 r_j^s c``, so in the
      original frame it is ``w_i <- w_i . psi(c)^-1 w_j^s psi(c)`` (conjugate, multiply, conjugate back; see
      ``Emitter.s_move``). An elementary move maps to itself, a conjugation by ``g`` to one by the word ``psi(g)``.
    * **tail**: the path ends at single letters, so the words end at the basis ``(psi(x), psi(y))``; precomposing
      with the factors of ``phi``, last first, is a sequence of Nielsen moves and gives ``x, y``.
    """
    if pres.n_gen != 2 or start.n_gen != 2:
        raise ValueError("transport through Aut(F2) needs two generators")
    psi = images(invert(phi))
    tab = sub_table(psi)
    em = Emitter(pres)
    states = replay(start, path, cyclic=cyclic, normalize=False)
    for state, mv in zip(states, path):
        if is_elementary(mv):
            em.align(tuple(apply_table(r, tab) for r in state.rels))
            em.dict_move(mv, tab)
        else:
            rels = canonical_rels(state.rels)
            em.align(tuple(apply_table(r, tab) for r in rels))
            em.s_move(rels, Move(*mv), tab)
    em.align(psi)                                              # the basis (psi(x), psi(y))
    for k in reversed(phi):
        em.precompose(AUTOS[k])
    replay(pres, em.moves, cyclic=cyclic, normalize=False)
    return em.moves


def solve_via_aut_min(pres, cfg=None, **overrides):
    """Search the Aut-minimal representative of ``pres``; return ``(result, elementary path or None)``.

    The representative's path is carried to ``pres`` and replayed there; only then does the solve count for
    ``pres``. A row that is its own representative (freely reduced, ``cyclic`` search) needs no automorphism, so
    the shorter decoded path is returned instead of a transport.
    """
    from ..search import search
    cfg = (cfg or SearchConfig()).replace(**overrides)
    ac = aut_canon(pres)
    res = search(ac.rep, cfg)
    if res.path is None:
        return res, None
    if cfg.cyclic and res.start == pres.reduced().canonical() and pres.reduced(False) == pres:
        return res, decode(pres, res.path)
    return res, transport(pres, ac.phi, res.path, res.start, cfg.cyclic)
