"""Beam-search decode of the policy (the evaluation path of the PPO stack).

Port of ``origin/experiments/ppo:experiments/ppo/beam.py`` (tip c73b11f2), itself the PyTorch version of
``beam/beam_search.py``: every step scores ``cum_log_prob + log_softmax(logits) + alpha * value``, keeps
the global top-``width`` over ``beam x action``, kills no-ops, drops duplicate states within the step and
states any beam has already visited in this search. Defaults match upstream (width 1024, 150 steps,
alpha 0, greedy). Deviations:

* the visited-set hash is 64-bit (upstream 32-bit: collisions at ``width * steps`` entries kill healthy
  beams) and its random vector is torch-seeded (identical to upstream's torch port);
* illegal actions (masked at ``-1e9`` by the network) are dead, not candidates. Upstream lets them fill
  the top-``width`` whenever a state has fewer legal moves than the width; such a child is a free product
  with no cancelling seam, not a Definition 2.1 move, and a "solve" through one cannot be replayed as
  S-moves. With the mask the result equals upstream's whenever upstream's path is all legal;
* only live beams go through the network (upstream scores all ``width`` rows every step), and the search
  stops when no beam is alive.

``cap`` (at most ``L = 24``, the width of the observation) limits the seam-reduced product of every
child; a selected child over it is killed and counted by the cap counters (``acx.core.capcount``).

**Cap counters.** A beam has no queue: its "pop" is the selection of the global top-``width`` children,
made from the network's scores before any move is applied, so the cap never changes what is selected. A
selected child over the cap took a beam slot that a larger cap would have filled with it, so it would
have been "popped" by definition: ``cap_would_pop == cap_dropped`` (a child counts once per step; the
beam keeps no per-state dedup of dropped children), ``cap_first_bind`` is the first step (1-based) that
selected one and ``cap_needed`` the shortest such seam-reduced product (the cap that admits it). Zero
means the run is the same at every cap up to ``L``; a ``cap_needed`` above ``L`` is a state the policy
cannot see at all (the observation holds ``L`` letters per relator). ``cap_dropped_min_total`` is the
least total (seam-reduced product plus the relator the move leaves alone) among them.
"""
import torch

from ..core.capcount import CapCount
from .moves import decode_action, s_move

NEVER = torch.iinfo(torch.int64).max


def hash_vector(n, seed=0xACABDED):
    g = torch.Generator().manual_seed(seed)
    return torch.randint(-(2 ** 62), 2 ** 62, (n,), generator=g, dtype=torch.int64)


def forward(model, states, chunk):
    out = [model(states[lo:lo + chunk]) for lo in range(0, len(states), chunk)]
    return torch.cat([o[0] for o in out]), torch.cat([o[1] for o in out])


@torch.no_grad()
def beam_search(model, x0, *, L=24, cap=None, width=1024, steps=150, alpha=0.0, chunk=4096):
    """Search from the ``(2L,)`` presentation ``x0``. Returns ``(actions, stats)``.

    ``actions`` is the list of flat actions of the best beam that reaches both relators of length 1
    (``None`` if none does within ``steps``); ``stats`` has ``evaluated`` (states scored by the
    network) and the cap counters (``acx.core.capcount.FIELDS``: the selected legal children whose
    product exceeded ``cap``, module docstring).
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
        new, over, size, total = s_move(old, *decode_action(action, L), L, cap, sizes=True)
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
