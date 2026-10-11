"""Batched substitution move of the Two-Hump environment, in PyTorch.

Port of ``envs/ac_moves.py`` (JAX; ``origin/experiments/ppo:experiments/ppo/acs_moves.py``,
tip c73b11f2), kept bug for bug because the shipped policy was trained against it:

* ``concatenate``: when nothing cancels at the seam the cancellation count is 0 (``argmin`` of an
  all-true mask); a product longer than ``L`` (or a smaller ``cap``) is dropped but the left factor is
  still cyclically reduced. The beam kills such no-ops and counts them as ``cap_rejected``.
* ``booth_rotation_index`` is NOT the least rotation (its ``set_f`` block compares ``s2[i] != s2[k]``
  where Booth compares ``s2[i] != s2[k+j+1]``; ~6% of random words at ``L=24`` differ). It only fixes
  the representative shown to the policy; ``acx`` canonicalises independently of it.
* a product equal to the rotated left factor discards the whole move.

Tensors are ``int64``: ``(B, L)`` per relator, ``(B, 2L)`` per presentation (``[r1 | r2]``, letters
``+-1 = x^+-1``, ``+-2 = y^+-1``, 0 = padding).

An action is one integer in ``[0, 4 L^2)`` decoded to ``(i, r, k1, k2)``: relator ``i`` is replaced by
``rot_left(r_1, k1) . rot_left(r_2 ** (-1 if r else 1), k2)`` (the product is formed in that order whatever
``i`` is) and the seam must cancel. Every such move is an ``acx`` S-move of the canonical state up to
rotation and inversion (the cancelled run can always be cut at the other junction of the cyclic word),
which is what ``acx.rl.solve`` relies on.
"""
import torch


def _pos(n, dev):
    return torch.arange(n, device=dev, dtype=torch.int64)


def reverse_nonzero(r):
    """Reverse the nonzero prefix of every row."""
    B, L = r.shape
    pos = _pos(L, r.device)[None]
    n = (r != 0).sum(-1, keepdim=True)
    return torch.gather(r, 1, torch.where(pos < n, n - 1 - pos, pos.expand(B, L)))


def cyclic_reduce(r):
    B, L = r.shape
    pos = _pos(L, r.device)[None]
    mask = r == -reverse_nonzero(r)
    cancel = torch.where(~mask, pos.expand(B, L), torch.full_like(r, L)).amin(-1, keepdim=True)
    n = (r != 0).sum(-1, keepdim=True)
    return torch.where(pos >= n - 2 * cancel, torch.zeros_like(r), torch.gather(r, 1, (pos + cancel) % L))


def concatenate(ri, rj, cap):
    """``(ri . rj`` with the seam cancelled and cyclically reduced, ``over)``: ``over`` marks a seam-reduced
    product longer than ``cap``, which is dropped (the result is then ``ri`` cyclically reduced)."""
    B, L = ri.shape
    pos = _pos(L, ri.device)[None]
    miss = rj != -reverse_nonzero(ri)
    first = torch.where(miss, pos.expand(B, L), torch.full_like(ri, L)).amin(-1, keepdim=True)
    cancel = torch.where(miss.any(-1, keepdim=True), first, torch.zeros_like(first))
    li, lj = (ri != 0).sum(-1, keepdim=True), (rj != 0).sum(-1, keepdim=True)
    size, head = li + lj - 2 * cancel, li - cancel
    rolled = torch.gather(rj, 1, (pos - (li - 2 * cancel)) % L)
    out = torch.where((pos >= head) & (pos < size), rolled, torch.where(pos < head, ri, torch.zeros_like(ri)))
    over = size > cap
    return cyclic_reduce(torch.where(over, ri, out)), over.squeeze(-1)


def rotate_left(r, k):
    """Rotate the nonzero prefix left by ``k`` (``(B,)``, any sign)."""
    B, L = r.shape
    pos = _pos(L, r.device)[None]
    nz = r != 0
    n = nz.sum(-1, keepdim=True).clamp(min=1)
    return torch.gather(r, 1, torch.where(nz, (pos + k.reshape(B, 1) % n) % n, pos.expand(B, L)))


def booth_rotation_index(r):
    """Port of ``booth_lex_min_rotation_masked`` (see the module note: not the least rotation)."""
    B, L = r.shape
    n = (r != 0).sum(-1)
    s2 = torch.cat([r, r], 1)
    f = torch.full((B, 2 * L), -1, dtype=torch.int64, device=r.device)
    k = torch.zeros(B, dtype=torch.int64, device=r.device)
    rows = torch.arange(B, device=r.device)
    for i in range(1, 2 * L):
        si = s2[:, i]
        j = f[rows, i - k - 1]
        while True:
            ijk = k + j + 1
            s_ijk = s2[rows, ijk]
            active = (j != -1) & ((si != s_ijk) | ~((i < n) & (ijk < n)))
            if not bool(active.any()):
                break
            k = torch.where(active & ((ijk >= n) | (si < s_ijk)), i - j - 1, k)
            j = torch.where(active, f[rows, j.clamp(min=0)], j)
        sk = s2[rows, k]
        settled = (j == -1) & ((si != sk) | (i >= n) | (k >= n))
        f[rows, i - k] = torch.where(settled, torch.full_like(j, -1), j + 1)
        k = torch.where(settled & ((si < sk) | (k >= n)), torch.full_like(k, i), k)
    return k


def s_move(x, i, r, k1, k2, L, cap=None):
    """Apply ``(i, r, k1, k2)`` to the ``(B, 2L)`` presentations ``x``; returns ``(new x, over)``.

    ``cap`` (default and at most ``L``) is the length limit on the seam-reduced product; a product over
    it leaves the row unchanged (a no-op) and sets ``over``. At ``cap = L`` this is the environment.
    """
    r1, r2 = x[:, :L], x[:, L:]
    r2 = torch.where(r.reshape(-1, 1) == 1, -reverse_nonzero(r2), r2)
    a = rotate_left(r1, k1)
    prod, over = concatenate(a, rotate_left(r2, k2), L if cap is None else cap)
    rot = rotate_left(prod, booth_rotation_index(prod))
    into0 = i.reshape(-1, 1) == 0
    out = torch.cat([torch.where(into0, rot, x[:, :L]), torch.where(into0, x[:, L:], rot)], 1)
    return torch.where((prod == a).all(-1, keepdim=True), x, out), over


def decode_action(flat, L):
    """Flat action -> ``(i, r, k1, k2)`` (``ppo_ac_s.py:113-123``)."""
    k1, rem = flat // (4 * L) + 1, flat % (4 * L)
    ij = rem % 4
    j, k2 = ij % 2, rem // 4
    return ij // 2, j, k1, torch.where(j == 0, k2, -k2 - 1)


def encode_action(i, j, k1, k2, L):
    signed = torch.where(j == 0, k2, -(k2 + j))
    return ((k1 - 1) * L + signed) * 4 + (i * 2 + j)
