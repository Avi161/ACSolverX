"""S-move semantics for the ACS environment, batched in PyTorch.

A port of `envs/ac_moves.py` (JAX), done **bug-for-bug**. Every edge case that
file has is reproduced rather than repaired, because the point is parity with
the checkpoint that was trained against it:

- `_concatenate`'s `jnp.argmin(mask)` returns **0** when nothing cancels
  (`argmin` of an all-`True` boolean array), not `max_length`.
- The over-length branch (`new_size > max_length`) leaves the relator alone but
  still runs `cyclic_reduce` on it. That is the "no-op" the search literature
  calls a length-cap rejection.
- `s_move` compares the concatenation against the *rotated* first relator and,
  when they are equal, discards the whole move -- including the Booth rotation.

Every function takes and returns `int64` tensors of shape `(B, L)` (one relator
per row) or `(B, n_gen * L)` (a whole presentation), so the batch axis is the
env axis and nothing here is presentation-specific.

**`booth_rotation_index` is a bug-for-bug port and is NOT lex-min.**
`envs/ac_moves.py:booth_lex_min_rotation_masked` claims to return the index of
the lexicographically smallest rotation. It does not: its `set_f` block tests
`s2[i] != s2[k]` where textbook Booth tests `s2[i] != s2[k + j + 1]`, and the
resulting word differs from the true lex-min rotation on ~6% of random words at
L = 24 (measured over 20k words; see `tests/ppo/test_booth.py`). The obvious
O(L^2) brute force is therefore *not* a safe substitute -- it would silently
change the canonical form of every state, and with it the dynamics the shipped
checkpoint was trained against. `lex_min_rotation_index` is kept below as the
brute force it is, used only by the test that documents the divergence.
"""

import torch

__all__ = [
    "reverse_nonzero", "cyclic_reduce", "concatenate", "rotate_k",
    "booth_rotation_index", "lex_min_rotation_index", "s_move",
    "decode_action", "encode_action",
]


def _pos(n, device):
    return torch.arange(n, device=device, dtype=torch.int64)


def reverse_nonzero(r):
    """`envs/ac_moves.py:_reverse_nonzero` -- reverse the non-zero prefix in place.

    The JAX version scatters (`reversed.at[new_positions].set(arr)`); since
    `new_positions` is a permutation this is the equivalent gather.
    """
    B, L = r.shape
    pos = _pos(L, r.device).unsqueeze(0)
    n = (r != 0).sum(-1, keepdim=True)
    src = torch.where(pos < n, n - 1 - pos, pos.expand(B, L))
    return torch.gather(r, 1, src)


def cyclic_reduce(r):
    """`envs/ac_moves.py:cyclic_reduce`, restricted to the one relator it touches.

    `num_cancel` is the first index at which the word stops agreeing with the
    inverse of its own reversal, i.e. the number of letters cancelling off each
    end; `max_length` when the word cancels away entirely (JAX takes the min of
    `where(~mask, indices, max_length)`, which has no `False` to find).
    """
    B, L = r.shape
    pos = _pos(L, r.device).unsqueeze(0)
    mask = r == -reverse_nonzero(r)
    num_cancel = torch.where(~mask, pos.expand(B, L), torch.full_like(r, L)).amin(-1, keepdim=True)
    rlen = (r != 0).sum(-1, keepdim=True)
    gathered = torch.gather(r, 1, (pos + num_cancel) % L)
    return torch.where(pos >= rlen - 2 * num_cancel, torch.zeros_like(r), gathered)


def concatenate(ri, rj):
    """`envs/ac_moves.py:_concatenate(0, 1, ...)` applied to `[ri | rj]`.

    Returns the new relator 0 (relator 1 is never touched by that function).
    The seam cancellation count is the index of the first position where `rj`
    stops being the inverse of the reversed `ri`; when there is no such
    position, JAX's `argmin` over an all-`True` mask yields `0`, and that is
    what is reproduced here.
    """
    B, L = ri.shape
    pos = _pos(L, ri.device).unsqueeze(0)
    mismatch = rj != -reverse_nonzero(ri)
    first_mismatch = torch.where(mismatch, pos.expand(B, L), torch.full_like(ri, L)).amin(-1, keepdim=True)
    num_cancel = torch.where(mismatch.any(-1, keepdim=True), first_mismatch, torch.zeros_like(first_mismatch))

    ith_len = (ri != 0).sum(-1, keepdim=True)
    jth_len = (rj != 0).sum(-1, keepdim=True)
    new_size = ith_len + jth_len - 2 * num_cancel
    head = ith_len - num_cancel

    rolled = torch.gather(rj, 1, (pos - (ith_len - 2 * num_cancel)) % L)
    updated = torch.where(
        (pos >= head) & (pos < new_size),
        rolled,
        torch.where(pos < head, ri, torch.zeros_like(ri)),
    )
    # Over-length concatenations are silently discarded; the relator is left as
    # it was and still gets cyclically reduced.
    return cyclic_reduce(torch.where(new_size > L, ri, updated))


def rotate_k(r, k):
    """`envs/ac_moves.py:rotate_relator_k` -- rotate the non-zero prefix left by `k`.

    `k` is `(B,)` and may be negative; `%` follows Python/JAX sign conventions,
    so the result is non-negative. An empty relator divides by zero in JAX and
    then discards the garbage via the padding mask, so clamping the modulus to 1
    here is equivalent: the output is the unchanged all-zero relator either way.
    """
    B, L = r.shape
    pos = _pos(L, r.device).unsqueeze(0)
    nz = r != 0
    length = nz.sum(-1, keepdim=True).clamp(min=1)
    idx = (pos + k.reshape(B, 1) % length) % length
    return torch.gather(r, 1, torch.where(nz, idx, pos.expand(B, L)))


_BOOTH_INNER_CAP = 4096  # runaway guard; the real bound is O(L) amortised


def booth_rotation_index(r):
    """Batched port of `envs/ac_moves.py:booth_lex_min_rotation_masked`.

    Faithful down to the `s2[i] != s2[k]` comparison in the `set_f` block, which
    is what makes this *not* a lex-min rotation (see the module docstring). The
    JAX `fori_loop` becomes a Python loop over its 2L fixed iterations; the inner
    `while_loop` becomes a masked loop that runs until every row has exited.

    All dynamic indices are provably in range: `k <= i` gives `i - k - 1 >= 0`,
    and `f[m] <= m` gives `k + j + 1 <= i`, so no clamping is needed except on
    the discarded `f[j]` read of already-inactive rows.
    """
    B, L = r.shape
    dev = r.device
    length = (r != 0).sum(-1)
    s2 = torch.cat([r, r], dim=1)
    f = torch.full((B, 2 * L), -1, dtype=torch.int64, device=dev)
    k = torch.zeros(B, dtype=torch.int64, device=dev)
    rows = torch.arange(B, device=dev)

    for i in range(1, 2 * L):
        si = s2[:, i]
        j = f[rows, i - k - 1]

        for _ in range(_BOOTH_INNER_CAP):
            ijk = k + j + 1
            s_ijk = s2[rows, ijk]
            valid = (i < length) & (ijk < length)
            active = (j != -1) & ((si != s_ijk) | ~valid)
            if not bool(active.any()):
                break
            k = torch.where(active & ((ijk >= length) | (si < s_ijk)), i - j - 1, k)
            j = torch.where(active, f[rows, j.clamp(min=0)], j)
        else:  # pragma: no cover - only reachable if the JAX while_loop diverges
            raise RuntimeError("Booth inner loop did not converge")

        sk = s2[rows, k]
        neq = (si != sk) | (i >= length) | (k >= length)
        settled = (j == -1) & neq
        f[rows, i - k] = torch.where(settled, torch.full_like(j, -1), j + 1)
        k = torch.where(settled & ((si < sk) | (k >= length)), torch.full_like(k, i), k)

    return k


def lex_min_rotation_index(r):
    """True lexicographically smallest rotation of the non-zero prefix.

    Brute force over all `length` rotations, ranked by a base-5 positional key
    (letters live in `{-2,-1,1,2}`, so `letter + 2` is a digit in `0..4`, and
    `5**24 < 2**63` keeps the key exact in `int64`). Ties break to the smallest
    index, which is cosmetic: tied rotations are equal as words.

    **Not used by the environment.** It exists so the test suite can show, in
    the repo, that `booth_rotation_index` is not computing what its upstream
    name claims -- and therefore that the cheap substitution is unavailable.
    """
    B, L = r.shape
    dev = r.device
    pos = _pos(L, dev)
    length = (r != 0).sum(-1)
    safe = length.clamp(min=1)

    # rots[b, k, p] = the p-th letter of the k-th left rotation of r[b].
    idx = (pos.view(1, 1, L) + pos.view(1, L, 1)) % safe.view(B, 1, 1)
    rots = torch.gather(r.unsqueeze(1).expand(B, L, L), 2, idx)
    digits = torch.where(pos.view(1, 1, L) < length.view(B, 1, 1), rots + 2, torch.zeros_like(rots))

    weights = torch.tensor([5 ** (L - 1 - p) for p in range(L)], dtype=torch.int64, device=dev)
    key = (digits * weights.view(1, 1, L)).sum(-1)
    big = torch.full_like(key, torch.iinfo(torch.int64).max)
    key = torch.where(pos.view(1, L) < length.view(B, 1), key, big)

    winners = key == key.amin(-1, keepdim=True)
    first = torch.where(winners, pos.view(1, L).expand(B, L), torch.full_like(key, L)).amin(-1)
    return torch.where(length > 0, first, torch.zeros_like(first))


def s_move(x, i, r, k1, k2, max_length):
    """`envs/ac_moves.py:s_move`, batched. `x` is `(B, 2 * max_length)`.

    `i` selects which relator receives the product, `r` whether relator 1 is
    inverted for the computation, `k1`/`k2` the left rotations applied to the
    two relators before multiplying. All four are `(B,)` integer tensors.
    """
    L = max_length
    rel0, rel1 = x[:, :L], x[:, L:]

    # Step 1: optionally invert relator 1, for the computation only.
    rel1c = torch.where(r.reshape(-1, 1) == 1, -reverse_nonzero(rel1), rel1)

    # Steps 2-4: rotate both relators, then multiply them.
    a = rotate_k(rel0, k1)
    b = rotate_k(rel1c, k2)
    new_rel = concatenate(a, b)

    # Step 5: substitute into the i-th relator of the ORIGINAL x, then rotate
    # that relator to its lex-min form. A product equal to the rotated first
    # relator is discarded outright -- x is returned untouched.
    rotated = rotate_k(new_rel, booth_rotation_index(new_rel))
    into_0 = (i.reshape(-1, 1) == 0)
    out = torch.cat([torch.where(into_0, rotated, rel0),
                     torch.where(into_0, rel1, rotated)], dim=1)
    return torch.where((new_rel == a).all(-1, keepdim=True), x, out)


# --- packed action index ----------------------------------------------------
# The policy emits a single integer in [0, n_gen * 2 * L * L). The packing is
# fixed by `network.RelativeDualRingActorCritic`'s logit layout and decoded in
# `ppo_ac_s.py:113-123`; `wrappers.LogPathsProbsS.encode_action` is its inverse.

def decode_action(flat, max_length):
    """flat -> (i, r, k1, k2), matching `ppo_ac_s.py:113-123`."""
    L = max_length
    k1 = flat // (4 * L) + 1
    rem = flat % (4 * L)
    k2_tmp = rem // 4
    ij = rem % 4
    i = ij // 2
    j = ij % 2
    k2 = torch.where(j == 0, k2_tmp, -k2_tmp - 1)  # == k2_tmp * (-1)**j - j
    return i, j, k1, k2


def encode_action(i, j, k1, k2, max_length):
    """(i, r, k1, k2) -> flat, matching `wrappers.py:214-216`."""
    signed = torch.where(j == 0, k2, -(k2 + j))  # == (k2 + j) * (-1)**j
    return ((k1 - 1) * max_length + signed) * 4 + (i * 2 + j)
