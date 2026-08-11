"""Potential-based reward shaping from the heuristic-search block features.

The baseline reward is ``1000 if terminated else -min(nnz, 10)`` and ``nnz`` *is*
the total length ``L``. Above ``L = 10`` it is flat, so on every presentation that
matters the agent gets no gradient at all until it terminates. This module supplies
a potential ``Phi(s) = -lam * (w_L*L + w_K*K + w_MK*MK + w_S*S)`` whose difference
``F(s, s') = gamma*Phi(s') - Phi(s)`` is added to that reward.

Potential-based shaping is policy-invariant (Ng, Harada & Russell 1999): the optimal
policy is unchanged, and because ``F`` telescopes, no cycle can farm it. Two conditions
the proof needs, both of which are the caller's job:

  * ``Phi`` must be **zero at every episode end**, truncation included. ``acs_env`` folds
    ``terminated | truncated`` into one ``done``; bootstrapping ``Phi(s')`` past a horizon
    cut-off would pay an agent for sitting in a low-``h`` state until step 96.
  * the same ``gamma`` the learner discounts with. ``shaping_term`` takes it explicitly.

The features are the ones from ``experiments/heuristic_search/core/hsearch.py``: a relator
is a **cyclic** word and its blocks are the maximal runs of one generator read around the
ring. ``L + 20*S + 2*MK`` is the ordering that, on 70,723 Aut orbits at budget 100,000, cut
the unsolved residual from 221 (length alone) to 39 -- see
``results/heuristic_search/hsearch_ac19_hard100k/RESULTS.md``.

Nothing here enumerates a run. Because a cyclic word alternates generators around the ring,
the x-runs and y-runs of a relator that uses both generators are **equal in number**, so the
whole block analysis collapses into one quantity: ``T``, the number of cyclic positions where
the generator changes. Then ``k = T // 2``, the pooled mean run length of a generator is
``(its letters) / (its runs)``, and the seam merge that ``blocks()`` does by hand is already
accounted for -- reading transitions cyclically never counts the wrapping run twice. That is
what makes this cheap enough to run on 2,380 envs every step.

Traps, all of them pinned in ``tests/ppo/test_shaping.py``:

  * ``blocks()`` keys on ``c in "xX"``, so the **sign is irrelevant** -- what matters is
    ``abs(v) == 1`` vs ``abs(v) == 2``, not ``v > 0``.
  * ``feats`` reports ``k = 0`` for a relator that uses only one generator, which is *not*
    the same as "one block". Only ``S`` sees such a relator's letters.
  * the two means in ``S`` are pooled **across both relators**, not averaged per relator.
  * ``lam = 0`` must reproduce the unshaped reward bitwise. It is the control arm.
"""

import torch

# (w_L, w_K, w_MK, w_S). `s20mk2` is the treatment; `length` is the control's ordering,
# kept only so a test can show the machinery reduces to plain length.
#
# `hsolve.RECOMMENDED` is deliberately NOT here and must not be added. It was tuned on
# ~60 presentations, its xyimb term flips sign between the two shipped configs, and the
# user has ruled it out for this work. `w_K` stays in the signature because `K` is a real
# feature `features()` returns -- not as an invitation to reintroduce those weights.
WEIGHTS = {
    "s20mk2": (1.0, 0.0, 2.0, 20.0),
    "length": (1.0, 0.0, 0.0, 0.0),
}


def _relator_stats(v):
    """Block statistics for one left-packed relator slot.

    `v` is `(M, L)`: the relator's letters at positions `0..n-1` and zero padding after,
    which is the layout `acs_data.repad` writes and `acs_moves` preserves. Returns
    `(n, nx, ny, k, xruns, yruns)`, each `(M,)`.
    """
    nz = v != 0
    n = nz.sum(1)
    isx = (v.abs() == 1) & nz
    isy = nz & ~isx
    nx = isx.sum(1)
    ny = isy.sum(1)

    # A boundary at position i needs i to be a real letter; i-1 then always is, because
    # the slot is left-packed. So masking on `nz[:, 1:]` alone is exact.
    interior = ((isx[:, 1:] != isx[:, :-1]) & nz[:, 1:]).sum(1)
    # The ring closes from the last real letter back to the first. This one comparison is
    # what makes the count cyclic, and it is why no seam merge is needed afterwards.
    last = isx.gather(1, (n - 1).clamp(min=0).unsqueeze(1)).squeeze(1)
    seam = (isx[:, 0] != last) & (n > 1)
    t = interior + seam.to(interior.dtype)

    both = (nx > 0) & (ny > 0)
    half = t // 2                       # x-runs == y-runs around a ring using both
    zero = torch.zeros_like(half)
    one = torch.ones_like(half)
    # A single-generator relator has one run of that generator and, per `feats`, k = 0.
    k = torch.where(both, half, zero)
    xruns = torch.where(both, half, torch.where(nx > 0, one, zero))
    yruns = torch.where(both, half, torch.where(ny > 0, one, zero))
    return n, nx, ny, k, xruns, yruns


def features(x, n_gen=2, max_length=24):
    """`(L, K, MK, S)` for a batch of flat states, matching `hsearch.feats`.

    `x` is `(..., n_gen * max_length)`; each returned tensor is `x.shape[:-1]`, float32.
    Only `n_gen == 2` is supported -- the block features are defined on x and y.
    """
    if n_gen != 2:
        raise ValueError(f"block features are defined for n_gen=2, got {n_gen}")
    lead = x.shape[:-1]
    flat = x.reshape(-1, n_gen * max_length)
    n1, nx1, ny1, k1, xr1, yr1 = _relator_stats(flat[:, :max_length])
    n2, nx2, ny2, k2, xr2, yr2 = _relator_stats(flat[:, max_length:])

    length = (n1 + n2).to(torch.float32)
    knots = (k1 + k2).to(torch.float32)
    max_knots = torch.maximum(k1, k2).to(torch.float32)

    # Pooled over BOTH relators: `feats` concatenates the run lists before averaging.
    rx = (xr1 + xr2).to(torch.float32)
    ry = (yr1 + yr2).to(torch.float32)
    mx = torch.where(rx > 0, (nx1 + nx2).to(torch.float32) / rx.clamp(min=1), rx.new_zeros(()))
    my = torch.where(ry > 0, (ny1 + ny2).to(torch.float32) / ry.clamp(min=1), ry.new_zeros(()))
    # `smb = min(mx, my)` when both generators appear, else `mx or my` -- the non-zero one.
    smaller = torch.where((rx > 0) & (ry > 0), torch.minimum(mx, my),
                          torch.where(rx > 0, mx, my))

    return (length.reshape(lead), knots.reshape(lead),
            max_knots.reshape(lead), smaller.reshape(lead))


def heuristic(x, weights="s20mk2", n_gen=2, max_length=24):
    """The scalar `h` the potential is built from. Lower is better, as in the search."""
    w = WEIGHTS[weights] if isinstance(weights, str) else weights
    w_l, w_k, w_mk, w_s = w
    length, knots, max_knots, smaller = features(x, n_gen, max_length)
    return w_l * length + w_k * knots + w_mk * max_knots + w_s * smaller


def potential(x, lam, weights="s20mk2", n_gen=2, max_length=24):
    """`Phi(s) = -lam * h(s)`. Negative because low `h` is a good state."""
    if lam == 0.0:
        return torch.zeros(x.shape[:-1], dtype=torch.float32, device=x.device)
    return -float(lam) * heuristic(x, weights, n_gen, max_length)


def shaping_term(x_old, x_new, done, lam, gamma, weights="s20mk2",
                 n_gen=2, max_length=24):
    """`F = gamma * Phi(s') - Phi(s)`, with `Phi(s') = 0` wherever the episode ended.

    `done` must be `terminated | truncated`. Zeroing on truncation as well as termination
    is what stops the horizon cut-off from being a place to park.
    """
    if lam == 0.0:
        return torch.zeros(x_old.shape[:-1], dtype=torch.float32, device=x_old.device)
    phi = potential(x_old, lam, weights, n_gen, max_length)
    phi_next = potential(x_new, lam, weights, n_gen, max_length)
    phi_next = torch.where(done, torch.zeros_like(phi_next), phi_next)
    return float(gamma) * phi_next - phi
