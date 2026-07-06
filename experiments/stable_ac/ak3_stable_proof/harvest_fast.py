"""Numba hot path for Lane-D harvest.

``harvest_one`` in ``plateau_elim.py`` spends ~82% of a combo iterating the whole
visited set and, per 3-gen state, running ``stable_moves.eliminate`` (pure-Python,
per-letter substitution + free/cyclic reduction) for every once-occurring generator,
then ``greedy_nrel.canonical_key`` on the survivors. That is ~25M ``eliminate`` calls
per 200k-budget combo. This module does the identical computation inside ``@njit``,
reusing the already-gold-verified jitted primitives (``reduce_relator``,
``inverse_relator``, ``canonical_relator``), so a combo's harvest phase runs ~1-2 orders
of magnitude faster with byte-for-byte identical output (see ``test`` differential gate).

Semantics mirror ``stable_moves.eliminate`` EXACTLY (that is the oracle):
  * find (gen, ri) with abs(gen) occurring exactly once in relator ri, in the same
    ri-major / gen-minor order as ``find_eliminable``;
  * express gen from ri (invert ri first if the occurrence is -gen), rotate to [gen]+v,
    sub = inverse(v); substitute gen:=sub / -gen:=v into the OTHER relators in ascending
    index order; cyclic-reduce (== reduce_relator); drop candidates whose any relator
    exceeds l_cap, is empty, or whose total length exceeds harvest_tl_cap; renumber
    generators above gen down by one; canonical-key for first-wins dedup.

Fixed to the stabilized-AK(3) shape: n_gen == n_rel == 3.  ``harvest_key`` takes the raw
canonical byte key (as produced by ``greedy_nrel.state_to_key``) and returns the
per-state survivors; ``plateau_elim`` does the cross-state dedup and record building.
"""
import numpy as np
from numba import njit

import greedy_nrel as gn

reduce_relator = gn.reduce_relator          # free + cyclic reduce (== presentation.cyclic_reduce)
inverse_relator = gn.inverse_relator
canonical_relator = gn.canonical_relator

INT = gn.INT_DTYPE
N_REL = 3
N_GEN = 3
MAXC = 9                                    # <= n_rel * n_gen eliminable (gen, ri) pairs
_SUBBUF = 4096                              # scratch for one substituted word (pre-reduce)

# byte <-> signed-letter LUTs matching greedy_nrel's rank-byte encoding (NGEN_MAX=3).
_B2I = np.zeros(256, dtype=np.int64)
for _b, _v in gn._RANK_BYTE_TO_INT.items():
    _B2I[_b] = _v
_I2B = np.zeros(2 * gn.NGEN_MAX + 1, dtype=np.int64)   # index by signed letter offset
for _v, _b in gn._INT_TO_RANK_BYTE.items():
    _I2B[_v + gn.NGEN_MAX] = _b                          # letter v -> byte, offset by NGEN_MAX


@njit(cache=True)
def _letter_byte(v, i2b, ngen_max):
    return i2b[v + ngen_max]


@njit(cache=True)
def _decode_key(key_u8, b2i, R, rlen):
    """Split key bytes on 0x00 into <=N_REL relators, decode via LUT into R/rlen.
    Returns the number of relators found (must be N_REL for a well-formed 3-gen key)."""
    ri = 0
    pos = 0
    n = len(key_u8)
    for i in range(n + 1):
        if i == n or key_u8[i] == 0:
            L = i - pos
            if ri < N_REL:
                for t in range(L):
                    R[ri, t] = b2i[key_u8[pos + t]]
                rlen[ri] = L
            ri += 1
            pos = i + 1
    return ri


@njit(cache=True)
def _canon_bytes(rel, i2b, ngen_max, out):
    """Canonical relator -> rank bytes into out; returns length."""
    c = canonical_relator(rel)
    for t in range(len(c)):
        out[t] = i2b[c[t] + ngen_max]
    return len(c)


@njit(cache=True)
def _lt_partkey(a, alen, b, blen):
    """(len, bytes) order used by canonical_key's part sort."""
    if alen != blen:
        return alen < blen
    for t in range(alen):
        if a[t] != b[t]:
            return a[t] < b[t]
    return False


@njit(cache=True)
def _harvest_key(key_u8, l_cap, htl_cap, b2i, i2b, ngen_max,
                 out_key, out_klen, out_cand, out_clen, out_gen, out_ri):
    """Fill preallocated buffers with survivors for one state; return survivor count.

    out_key[c, :out_klen[c]]  canonical key bytes for dedup (== greedy_nrel.canonical_key)
    out_cand[c, s, :out_clen[c, s]]  renumbered reduced relator s (s in 0,1), eliminate order
    out_gen[c], out_ri[c]     the (gen, ri) that produced survivor c
    """
    R = np.zeros((N_REL, l_cap + 1), dtype=INT)
    rlen = np.zeros(N_REL, dtype=INT)
    nr = _decode_key(key_u8, b2i, R, rlen)
    nc = 0
    if nr != N_REL:
        return nc

    sub = np.empty(_SUBBUF, dtype=INT)      # substitution word for +gen
    ivs = np.empty(_SUBBUF, dtype=INT)      # substitution word for -gen (= v)
    buf = np.empty(_SUBBUF, dtype=INT)      # scratch substituted word
    ca = np.empty(l_cap + 1, dtype=INT)     # candidate relator bytes (canonical) a
    cb = np.empty(l_cap + 1, dtype=INT)     # candidate relator bytes (canonical) b

    for ri in range(N_REL):                 # ri-major / gen-minor == find_eliminable order
        rl = rlen[ri]
        for gen in range(1, N_GEN + 1):
            # count occurrences of +-gen in relator ri
            cnt = 0
            pos = -1
            for t in range(rl):
                a = R[ri, t]
                if (a if a >= 0 else -a) == gen:
                    cnt += 1
                    pos = t
            if cnt != 1:
                continue

            # express gen from ri: r = ri (invert if occurrence is -gen), rotate to [gen]+v
            rrel = R[ri, :rl].copy()
            if rrel[pos] == -gen:
                rrel = inverse_relator(rrel)
                for t in range(len(rrel)):
                    a = rrel[t]
                    if (a if a >= 0 else -a) == gen:
                        pos = t
                        break
            # rr = rrel[pos:] + rrel[:pos]  -> rr[0] == gen ; v = rr[1:]
            vlen = rl - 1
            for t in range(vlen):
                ivs[t] = rrel[(pos + 1 + t) % rl]   # v = inverse-substitution for -gen
            # sub = inverse(v)
            for t in range(vlen):
                sub[t] = -ivs[vlen - 1 - t]

            # substitute into the two OTHER relators (ascending index, skip ri)
            ok = True
            slot = 0
            ca_len = 0
            cb_len = 0
            for j in range(N_REL):
                if j == ri:
                    continue
                m = 0
                jl = rlen[j]
                for t in range(jl):
                    a = R[j, t]
                    if a == gen:
                        for u in range(vlen):
                            buf[m] = sub[u]
                            m += 1
                    elif a == -gen:
                        for u in range(vlen):
                            buf[m] = ivs[u]
                            m += 1
                    else:
                        buf[m] = a
                        m += 1
                red = reduce_relator(buf[:m])
                if len(red) > l_cap:
                    ok = False
                    break
                # renumber: generators with abs > gen shift down by one
                if slot == 0:
                    for t in range(len(red)):
                        a = red[t]
                        aa = a if a >= 0 else -a
                        if aa > gen:
                            ca[t] = (aa - 1) if a > 0 else -(aa - 1)
                        else:
                            ca[t] = a
                    ca_len = len(red)
                else:
                    for t in range(len(red)):
                        a = red[t]
                        aa = a if a >= 0 else -a
                        if aa > gen:
                            cb[t] = (aa - 1) if a > 0 else -(aa - 1)
                        else:
                            cb[t] = a
                    cb_len = len(red)
                slot += 1

            if not ok:
                continue
            if ca_len == 0 or cb_len == 0:
                continue
            if ca_len + cb_len > htl_cap:
                continue

            # canonical key == greedy_nrel.canonical_key([cand_a, cand_b])
            kba = np.empty(l_cap + 1, dtype=np.int64)
            kbb = np.empty(l_cap + 1, dtype=np.int64)
            na = _canon_bytes(ca[:ca_len], i2b, ngen_max, kba)
            nb = _canon_bytes(cb[:cb_len], i2b, ngen_max, kbb)
            if _lt_partkey(kba, na, kbb, nb):
                first, flen, second, slen = kba, na, kbb, nb
            else:
                first, flen, second, slen = kbb, nb, kba, na
            kpos = 0
            for t in range(flen):
                out_key[nc, kpos] = first[t]
                kpos += 1
            out_key[nc, kpos] = 0
            kpos += 1
            for t in range(slen):
                out_key[nc, kpos] = second[t]
                kpos += 1
            out_klen[nc] = kpos
            # store renumbered reduced relators in eliminate order (a then b)
            for t in range(ca_len):
                out_cand[nc, 0, t] = ca[t]
            for t in range(cb_len):
                out_cand[nc, 1, t] = cb[t]
            out_clen[nc, 0] = ca_len
            out_clen[nc, 1] = cb_len
            out_gen[nc] = gen
            out_ri[nc] = ri
            nc += 1
    return nc


def harvest_key(key_bytes, l_cap, htl_cap):
    """Python wrapper: raw canonical byte key -> list of survivors.
    Each survivor: (ck_bytes, [relA_int_list, relB_int_list], gen, ri)."""
    key_u8 = np.frombuffer(key_bytes, dtype=np.uint8)
    out_key = np.empty((MAXC, 2 * (l_cap + 1)), dtype=np.uint8)
    out_klen = np.empty(MAXC, dtype=np.int64)
    out_cand = np.empty((MAXC, 2, l_cap + 1), dtype=INT)
    out_clen = np.empty((MAXC, 2), dtype=np.int64)
    out_gen = np.empty(MAXC, dtype=np.int64)
    out_ri = np.empty(MAXC, dtype=np.int64)
    nc = _harvest_key(key_u8, l_cap, htl_cap, _B2I, _I2B, gn.NGEN_MAX,
                      out_key, out_klen, out_cand, out_clen, out_gen, out_ri)
    res = []
    for c in range(nc):
        ck = out_key[c, :out_klen[c]].tobytes()
        rels = [out_cand[c, 0, :out_clen[c, 0]].tolist(),
                out_cand[c, 1, :out_clen[c, 1]].tolist()]
        res.append((ck, rels, int(out_gen[c]), int(out_ri[c])))
    return res


def harvest_visited(visited, l_cap, htl_cap):
    """Harvest every state in ``visited`` (iterable of canonical byte keys) with reused
    buffers, doing the cross-state first-wins dedup in the tight loop. Returns
    ``{ck_bytes: (relA_list, relB_list, gen, ri, src_hex)}`` — the deduped survivors,
    identical to the pure-Python harvest_one ``seen`` (minus the constant form/word)."""
    kw = 2 * (l_cap + 1)
    out_key = np.empty((MAXC, kw), dtype=np.uint8)
    out_klen = np.empty(MAXC, dtype=np.int64)
    out_cand = np.empty((MAXC, 2, l_cap + 1), dtype=INT)
    out_clen = np.empty((MAXC, 2), dtype=np.int64)
    out_gen = np.empty(MAXC, dtype=np.int64)
    out_ri = np.empty(MAXC, dtype=np.int64)
    seen = {}
    for key in visited:
        key_u8 = np.frombuffer(key, dtype=np.uint8)
        nc = _harvest_key(key_u8, l_cap, htl_cap, _B2I, _I2B, gn.NGEN_MAX,
                          out_key, out_klen, out_cand, out_clen, out_gen, out_ri)
        if nc == 0:
            continue
        src_hex = None
        for c in range(nc):
            ck = out_key[c, :out_klen[c]].tobytes()
            if ck in seen:
                continue
            if src_hex is None:
                src_hex = key.hex()
            seen[ck] = (out_cand[c, 0, :out_clen[c, 0]].tolist(),
                        out_cand[c, 1, :out_clen[c, 1]].tolist(),
                        int(out_gen[c]), int(out_ri[c]), src_hex)
    return seen


def warm():
    """Trigger JIT compilation (call once in the parent before forking workers)."""
    from stable_moves import eliminate  # noqa: F401
    k = gn.state_to_key(gn.canonical_tuple(
        (np.array([1, 2, 1], INT), np.array([1, 1, 1, -2, -2, -2, -2], INT),
         np.array([3, -1, -2], INT))))
    harvest_key(k, 24, 20)
    harvest_visited([k], 24, 20)
