"""Beam-search decode of the policy: width x steps, cap counters, no illegal action.

Every step scores ``cum_log_prob + log_softmax(logits) + alpha * value``, keeps the global top-``width`` over
``beam x action``, kills no-ops, drops duplicate states within the step and states any beam has already visited (a
64-bit hash). Illegal actions (masked at ``-1e9`` by the network) are dead, never candidates, since a "solve" through
one cannot be replayed as S-moves; only live beams go through the network and the search stops when none is alive.
``cap`` (at most ``L = 24``, the observation width) limits the seam-reduced product of every child.
"""
import torch

from ..core.capcount import CapCount
from .moves import decode_action, s_move

NEVER = torch.iinfo(torch.int64).max


def hash_vector(n, seed=0xACABDED):
    """The random int64 vector whose dot product hashes a state."""
    g = torch.Generator().manual_seed(seed)
    return torch.randint(-(2 ** 62), 2 ** 62, (n,), generator=g, dtype=torch.int64)


def forward(model, states, chunk):
    """``model(states)`` in chunks of ``chunk`` rows: ``(logits, value)``."""
    out = [model(states[lo:lo + chunk]) for lo in range(0, len(states), chunk)]
    return torch.cat([o[0] for o in out]), torch.cat([o[1] for o in out])


@torch.no_grad()
def beam_search(model, x0, *, L=24, cap=None, width=1024, steps=150, alpha=0.0, chunk=4096):
    """Search from the ``(2L,)`` presentation ``x0``. Returns ``(actions, stats)``.

    ``actions`` is the list of flat actions of the best beam that reaches both relators of length 1 (``None`` if none
    does within ``steps``); ``stats`` has ``evaluated`` (states scored by the network) and the cap counters.

    **Cap counters** (``acx.core.capcount``). A beam has no queue: its "pop" is the selection of the global
    top-``width`` children, made from the network's scores before any move is applied, so the cap never changes what is
    selected. A selected child over the cap took a beam slot that a larger cap would have filled with it, so
    ``cap_would_pop == cap_dropped`` (a child counts once per step). ``cap_first_bind`` is the first step (1-based) that
    selected one and ``cap_needed`` the shortest such seam-reduced product (the cap that admits it); a ``cap_needed``
    above ``L`` is a state the policy cannot see. ``cap_dropped_min_total`` is the least total among them. Zero dropped
    means the run is the same at every cap up to ``L``.
    """
    B, n_act, minf = width, 4 * L * L, float("-inf")
    hv = hash_vector(x0.numel())
    states = x0[None].expand(B, -1).clone()
    alive = torch.zeros(B, dtype=torch.bool)
    alive[0] = True
    cum = torch.where(alive, 0.0, minf)
    seqs = torch.full((B, steps), -1, dtype=torch.int64)
    visited = torch.full((B * steps,), NEVER, dtype=torch.int64)
    visited[0] = (x0 * hv).sum()
    visited = visited.sort().values
    stats = dict(evaluated=0)
    cc = CapCount(L if cap is None else cap)
    for t in range(steps):
        live = alive.nonzero().squeeze(1)
        if not len(live):
            break
        logits, value = forward(model, states[live], chunk)
        stats["evaluated"] += len(live)
        scores = torch.full((B, n_act), minf)
        scores[live] = (torch.log_softmax(logits, -1) + alpha * value[:, None]).masked_fill(logits < -1e8, minf)
        top, idx = torch.topk((cum[:, None] + scores).reshape(-1), B)
        parent, action = idx // n_act, idx % n_act
        old = states[parent]
        new, over, size, total = s_move(old, *decode_action(action, L), L, cap)
        seqs = seqs[parent]
        seqs[:, t] = action
        real = top > minf                                            # a live parent and a legal action
        cc.pop(None)                                                 # step t + 1 selected
        hit = real & over
        if hit.any():
            for tot, longest in zip(total[hit].tolist(), size[hit].tolist()):
                cc.drop_now(tot, longest)
        done = (new != 0).sum(-1) == 2
        solved = done & real
        alive = real & ~done & (t + 1 < steps) & ~(old == new).all(-1)
        h = (new * hv).sum(-1)
        by_score = torch.argsort(-torch.where(alive, top, torch.full_like(top, minf)), stable=True)
        order = by_score[torch.argsort(h[by_score], stable=True)]    # equal hashes: best beam first
        first = torch.ones(B, dtype=torch.bool)
        first[1:] = h[order][1:] != h[order][:-1]
        keep = torch.zeros(B, dtype=torch.bool)
        keep[order] = first
        pos = torch.searchsorted(visited, h).clamp(max=visited.numel() - 1)
        alive &= keep & (visited[pos] != h)
        cum = torch.where(alive, top, torch.full_like(top, minf))
        visited = torch.cat([visited, torch.where(alive, h, torch.full_like(h, NEVER))]).sort().values[:B * steps]
        states = new
        if solved.any():
            return seqs[int(solved.nonzero()[0]), :t + 1].tolist(), {**stats, **cc.record()}
    return None, {**stats, **cc.record()}
