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

NEVER = torch.iinfo(torch.int64).max       # sorts after every real hash: an empty slot of the visited table
MINUS_INF = float("-inf")


def hash_vector(n, seed=0xACABDED):
    """The random int64 vector whose dot product hashes a state."""
    g = torch.Generator().manual_seed(seed)
    return torch.randint(-(2 ** 62), 2 ** 62, (n,), generator=g, dtype=torch.int64)


def forward(model, states, chunk):
    """``model(states)`` in chunks of ``chunk`` rows: ``(logits, value)``."""
    out = [model(states[lo:lo + chunk]) for lo in range(0, len(states), chunk)]
    return torch.cat([o[0] for o in out]), torch.cat([o[1] for o in out])


class Visited:
    """The hashes of every state a beam has held, as a sorted table of fixed size (empty slots hold ``NEVER``)."""

    def __init__(self, first_hash, size):
        self.table = torch.full((size,), NEVER, dtype=torch.int64)
        self.table[0] = first_hash
        self.table = self.table.sort().values

    def contains(self, hashes):
        """Boolean mask: which of ``hashes`` are in the table."""
        pos = torch.searchsorted(self.table, hashes).clamp(max=self.table.numel() - 1)
        return self.table[pos] == hashes

    def add(self, hashes, alive):
        """Add the hashes of the ``alive`` beams (the others go in as ``NEVER``)."""
        added = torch.where(alive, hashes, torch.full_like(hashes, NEVER))
        self.table = torch.cat([self.table, added]).sort().values[:self.table.numel()]


def best_of_each_hash(hashes, score):
    """Mask that keeps, for every distinct hash, the entry with the highest ``score`` (the first on ties)."""
    by_score = torch.argsort(-score, stable=True)
    order = by_score[torch.argsort(hashes[by_score], stable=True)]      # equal hashes: best beam first
    first = torch.ones_like(hashes, dtype=torch.bool)
    first[1:] = hashes[order][1:] != hashes[order][:-1]
    keep = torch.zeros_like(first)
    keep[order] = first
    return keep


def top_children(model, states, live, cum, alpha, chunk):
    """Score every action of the ``live`` beams: the global top-``width`` ``(total score, flat index)``.

    Children of dead beams and illegal actions score ``-inf``; the flat index is ``parent * (4 L^2) + action``.
    """
    width, n_actions = len(states), 4 * (states.shape[1] // 2) ** 2
    logits, value = forward(model, states[live], chunk)
    log_prob = torch.log_softmax(logits, -1) + alpha * value[:, None]
    scores = torch.full((width, n_actions), MINUS_INF)
    scores[live] = log_prob.masked_fill(logits < -1e8, MINUS_INF)
    return torch.topk((cum[:, None] + scores).reshape(-1), width)


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
    n_actions = 4 * L * L
    hash_vec = hash_vector(x0.numel())
    states = x0[None].expand(width, -1).clone()
    alive = torch.zeros(width, dtype=torch.bool)
    alive[0] = True
    cum = torch.where(alive, 0.0, MINUS_INF)                         # cumulative log-prob of each beam
    action_seqs = torch.full((width, steps), -1, dtype=torch.int64)
    visited = Visited((x0 * hash_vec).sum(), width * steps)
    evaluated, solution = 0, None
    counter = CapCount(L if cap is None else cap)
    for t in range(steps):
        live = alive.nonzero().squeeze(1)
        if len(live) == 0:
            break
        top, idx = top_children(model, states, live, cum, alpha, chunk)
        evaluated += len(live)
        parent, action = idx // n_actions, idx % n_actions
        old = states[parent]
        new, over, size, total = s_move(old, *decode_action(action, L), L, cap)
        action_seqs = action_seqs[parent]
        action_seqs[:, t] = action

        real = top > MINUS_INF                                       # a live parent and a legal action
        counter.pop(None)                                            # step t + 1 selected
        for total_i, longest_i in zip(total[real & over].tolist(), size[real & over].tolist()):
            counter.drop_now(total_i, longest_i)

        finished = (new != 0).sum(-1) == 2                           # both relators of length 1
        solved = finished & real
        alive = real & ~finished & (t + 1 < steps) & ~(old == new).all(-1)     # a no-op child is dead
        hashes = (new * hash_vec).sum(-1)
        score = torch.where(alive, top, torch.full_like(top, MINUS_INF))
        alive &= best_of_each_hash(hashes, score) & ~visited.contains(hashes)
        cum = torch.where(alive, top, torch.full_like(top, MINUS_INF))
        visited.add(hashes, alive)
        states = new
        if solved.any():
            solution = action_seqs[int(solved.nonzero()[0]), :t + 1].tolist()
            break
    return solution, {"evaluated": evaluated, **counter.record()}
