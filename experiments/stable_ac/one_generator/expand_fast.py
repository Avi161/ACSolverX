"""Numba node-expansion for NRelatorSolver's hot loop.

Profiling a 2-gen solve (50k nodes) showed ~60% of the time in pure-Python per-neighbor
work: ``_relator_bytes(canonical_relator(...))`` (a dict-comprehension byte encoding, 36%)
and ``get_neighbors`` (24%). This module does the whole per-node expansion in ``@njit`` —
decode the canonical byte key, generate every substitution neighbour (EXACTLY the order of
``greedy_nrel.get_neighbors``), canonicalize the one changed relator, and assemble each
child's canonical byte key + total length — leaving only the heap and visited dict (the
search state) in Python. Byte-for-byte identical to the Python path (see the differential
gate in tests), so node counts / solved set / retraced paths are unchanged; it just runs
~2.5-3x faster, for both the n=2 solve and the n=3 harvest greedy.

The neighbour rule mirrors get_neighbors: for every unordered pair {a,b} (a<b), each
candidate c in {r_b, r_b^-1}, and each rotation of r_a and c, if the boundary letters
cancel, ``neighbour = reduce(roll(r_a,i) . roll(c,j))`` is emitted into slot a (r_a ->
neighbour) THEN slot b (r_b -> neighbour). Children with len 0 or >= max_len are dropped
(the solver dropped the latter too), so the KEPT-child order matches the solver exactly.
"""
import numpy as np
from numba import njit

import greedy_nrel as gn

reduce_relator = gn.reduce_relator
canonical_relator = gn.canonical_relator
INT = gn.INT_DTYPE
NGEN_MAX = gn.NGEN_MAX
L = gn.L

MAXREL = 8                      # supports n_gen up to 8 (we use 2 and 3)
MAXCHILD = 8192                 # max kept children per node
_KW = MAXREL * (L + 1)          # max joined-key bytes

_B2I = np.zeros(256, dtype=INT)
for _b, _v in gn._RANK_BYTE_TO_INT.items():
    _B2I[_b] = _v
_I2B = np.zeros(2 * NGEN_MAX + 1, dtype=np.int64)
for _v, _b in gn._INT_TO_RANK_BYTE.items():
    _I2B[_v + NGEN_MAX] = _b


@njit(cache=True)
def _cmp_part(a, alen, b, blen):
    """(len, bytes) order used by canonical_key's part sort: -1/0/1."""
    if alen != blen:
        return -1 if alen < blen else 1
    for t in range(alen):
        if a[t] != b[t]:
            return -1 if a[t] < b[t] else 1
    return 0


@njit(cache=True)
def _expand(key_u8, n_gen, max_len, b2i, i2b, ngen_max,
            out_keys, out_klen, out_tl):
    """Fill out_* with the kept children of the state encoded by key_u8; return count.
    out_keys[c, :out_klen[c]] = child canonical byte key; out_tl[c] = its total length."""
    # decode key -> relators R (ints) and keep the raw canonical byte parts
    R = np.zeros((MAXREL, L + 1), dtype=INT)
    rlen = np.zeros(MAXREL, dtype=INT)
    parts = np.zeros((MAXREL, L + 1), dtype=np.uint8)
    plen = np.zeros(MAXREL, dtype=INT)
    nr = 0
    pos = 0
    n = len(key_u8)
    for i in range(n + 1):
        if i == n or key_u8[i] == 0:
            ln = i - pos
            if nr < MAXREL:
                for t in range(ln):
                    parts[nr, t] = key_u8[pos + t]
                    R[nr, t] = b2i[key_u8[pos + t]]
                plen[nr] = ln
                rlen[nr] = ln
            nr += 1
            pos = i + 1
    nc = 0
    total_all = 0
    for k in range(n_gen):
        total_all += plen[k]

    inv = np.empty(L + 1, dtype=INT)          # inverse of r_b when c_is_inv
    buf = np.empty(2 * (L + 1), dtype=INT)     # roll(r_a,i) . roll(c,j)
    npart = np.empty(L + 1, dtype=np.uint8)    # canonical bytes of neighbour
    order = np.empty(MAXREL, dtype=np.int64)

    for a in range(n_gen):
        la = rlen[a]
        if la == 0:
            continue
        for b in range(a + 1, n_gen):
            lb = rlen[b]
            for c_is_inv in range(2):
                lc = lb
                if c_is_inv == 1:
                    for t in range(lb):
                        inv[t] = -R[b, lb - 1 - t]
                if lc == 0:
                    continue
                for i in range(la):
                    last = R[a, (la - 1 - i) % la]
                    for j in range(lc):
                        if c_is_inv == 0:
                            first = R[b, (-j) % lc]
                        else:
                            first = inv[(-j) % lc]
                        if last != -first:
                            continue
                        # neighbour = reduce( roll(R[a], i) . roll(c, j) )
                        m = 0
                        for t in range(la):
                            buf[m] = R[a, (t - i) % la]
                            m += 1
                        if c_is_inv == 0:
                            for t in range(lc):
                                buf[m] = R[b, (t - j) % lc]
                                m += 1
                        else:
                            for t in range(lc):
                                buf[m] = inv[(t - j) % lc]
                                m += 1
                        red = reduce_relator(buf[:m])
                        lnn = len(red)
                        if lnn == 0 or lnn >= max_len:
                            continue
                        # canonical bytes of the changed relator
                        cr = canonical_relator(red)
                        npl = len(cr)
                        for t in range(npl):
                            npart[t] = i2b[cr[t] + ngen_max]
                        # emit into slot a then slot b (matches get_neighbors)
                        for ci in (a, b):
                            if nc >= MAXCHILD:
                                break
                            # selection-sort the n_gen parts (part[ci] replaced by npart)
                            # by (len, bytes); write joined key + tl
                            for k in range(n_gen):
                                order[k] = k
                            for x in range(n_gen):
                                best = x
                                for y in range(x + 1, n_gen):
                                    ky = order[y]
                                    kb = order[best]
                                    ay = npart if ky == ci else parts[ky]
                                    aly = npl if ky == ci else plen[ky]
                                    ab = npart if kb == ci else parts[kb]
                                    alb = npl if kb == ci else plen[kb]
                                    if _cmp_part(ay, aly, ab, alb) < 0:
                                        best = y
                                if best != x:
                                    tmp = order[x]
                                    order[x] = order[best]
                                    order[best] = tmp
                            kp = 0
                            for x in range(n_gen):
                                k = order[x]
                                pk = npart if k == ci else parts[k]
                                pl = npl if k == ci else plen[k]
                                if x > 0:
                                    out_keys[nc, kp] = 0
                                    kp += 1
                                for t in range(pl):
                                    out_keys[nc, kp] = pk[t]
                                    kp += 1
                            out_klen[nc] = kp
                            out_tl[nc] = total_all - plen[ci] + npl
                            nc += 1
    return nc


# preallocated per-process buffers (solve is single-threaded within a worker)
_OUT_KEYS = np.empty((MAXCHILD, _KW), dtype=np.uint8)
_OUT_KLEN = np.empty(MAXCHILD, dtype=np.int64)
_OUT_TL = np.empty(MAXCHILD, dtype=np.int64)


def expand_into(key_bytes, n_gen, max_len):
    """Fill the module buffers (_OUT_KEYS/_OUT_KLEN/_OUT_TL) with this node's children and
    return the count. The solver iterates the buffers directly (no per-node list), consuming
    them before the next call — safe because a search is single-threaded within a process."""
    key_u8 = np.frombuffer(key_bytes, dtype=np.uint8)
    return _expand(key_u8, n_gen, max_len, _B2I, _I2B, NGEN_MAX,
                   _OUT_KEYS, _OUT_KLEN, _OUT_TL)


def expand(key_bytes, n_gen, max_len):
    """Python wrapper: canonical byte key -> list of (child_key_bytes, total_len) in the
    exact order the solver's get_neighbors path would keep them (used by the diff gate)."""
    nc = expand_into(key_bytes, n_gen, max_len)
    return [(_OUT_KEYS[c, :_OUT_KLEN[c]].tobytes(), int(_OUT_TL[c])) for c in range(nc)]


def warm(n_gen):
    """Trigger JIT compilation for a given n_gen before forking workers."""
    import greedy_nrel as _gn
    if n_gen == 2:
        st = (np.array([1, 2], INT), np.array([1, -2], INT))
    else:
        st = (np.array([1, 2, 1], INT), np.array([1, 1, 1, -2, -2], INT),
              np.array([3, -1], INT))
    expand(_gn.state_to_key(_gn.canonical_tuple(st)), n_gen, L)
