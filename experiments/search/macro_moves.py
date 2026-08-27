"""Proof-carrying macro greedy: Definition 2.1 substitution + conjugate-donor AC moves.

Why a donor move is the one genuinely new move available at rank 2
------------------------------------------------------------------
The search state is a pair of cyclically reduced words, canonical up to rotation,
inversion and swap. On such states every single AC step "multiply a relator by a
conjugate of the other" has the form

    r_i  <-  cyc( r_i . w r_j^e w^-1 ),      e in {+1, -1},

and the conjugator ``w`` only matters modulo the centraliser of ``r_j^e`` (powers of
its root). The Definition 2.1 substitution move ``rot_k1(r_i) . rot_k2(r_j^e)``
realises exactly the cosets ``w = u v^-1`` with ``u`` a prefix of ``r_i`` and ``v`` a
prefix of ``r_j^e`` — and the implemented generator additionally requires the
concatenation seam to cancel. Everything else in the one-step AC neighbourhood is
unreachable in one substitution step.

The **conjugate-donor macro** closes that gap for a finite conjugator family:

    r_i  <-  r_i . (w r_j^e w^-1),        r_j unchanged (the donor is restored).

It is an explicit AC composite — for ``e = +1``: conjugate ``r_j`` by ``w^-1`` one
letter at a time (|w| primitive conjugations), right-multiply ``r_i`` by ``r_j``,
undo the conjugations; for ``e = -1`` wrap that in an invert/restore pair. Macro
cost 3 (5 when ``e = -1``); elementary cost ``2|w| + 1`` (``2|w| + 3``). So every
donor edge is ``AC_EQ`` — an ordinary Andrews–Curtis equivalence with a concrete
primitive expansion, never a stable or theorem-only edge. The independent
expansion + replay lives in ``certify.py``.

Conjugator families (all finite; sizes are search parameters, not hypotheses):

  * every freely reduced word with ``|w| <= donor_wmax`` (default 2) — includes
    ``w = ''``, i.e. the plain multiply the seam filter excludes;
  * OPT-IN (``donor_subw=(lo, hi)``, default off): every cyclic subword, and
    inverse of a cyclic subword, of the two current relators with length in
    that range — "bridge" words that can cancel deeply where prefix-product
    cosets cannot. Benchmarked as pure breadth: hundreds of extra children per
    node, none of which won a heap pop at tiny budgets, and enough discovered
    states to matter for memory — hence off by default;
  * goal-directed proposals (``goal_conjugators``): for each short candidate
    replacement ``s`` with ``|s| <= goal_smax`` (default 2), the defect
    ``r_i^-1 s`` is checked for conjugacy to ``r_j^e`` — a cyclic-word
    equality — and on a hit the extracted ``w`` makes ``r_i -> s`` a SINGLE
    donor edge. The proposer changes which children are offered, never what an
    edge means, so soundness is untouched.

Engine contract mirrors ``heuristics.greedy_search_h``: same eleven-key stats
dict, same ``(priority, depth, key)`` heap shape, same visited-set dedup, and a
control invariant pinned in ``tests/test_macro_moves.py`` — donor moves disabled
plus ``config=None`` reproduces the baseline pop for pop. Solved paths return
typed certificates (``path_certs``), one per edge:

    ["sub",   target, jsign, k1, k2]     Definition 2.1 substitution
    ["donor", target, jsign, w]          conjugate-donor with conjugator w
    ["ncrw",  target, [[jsign, w], ..]]  multi-factor normal-closure rewrite:
                                         r_i <- r_i . Π w_k r_j^{ε_k} w_k⁻¹,
                                         an exact chained-donor composite found
                                         by ``defect_factorization`` (the
                                         forest-flow/class-two pattern: abelian
                                         obstruction filter, then a peeling
                                         lift). Its intermediates live INSIDE
                                         the edge, so it also tunnels through
                                         the per-relator length cap.

``path_moves`` is intentionally left empty: donor edges are not expressible as
Definition 2.1 four-tuples, and half a certificate would be worse than none.
"""
import heapq

import numpy as np

from experiments.search.greedy_baseline import (
    _HB_CHECK_EVERY, arr_to_str, canonical_pair_nj, get_neighbors_with_moves_nj,
    inverse_relator_nj, reduce_relator_nj, state_to_key, str_to_arr,
)
from experiments.search.heuristics import make_priority

_INV = {"x": "X", "X": "x", "y": "Y", "Y": "y"}
_LETTERS = "XYxy"                       # deterministic enumeration order
_W_ARR_CACHE = {}                       # w -> (arr, inverse arr); words recur every node


def inv_word(w):
    """Inverse of a word given as an 'xXyY' string."""
    return "".join(_INV[c] for c in reversed(w))


def short_words(max_len):
    """Every freely reduced 'xXyY' word with length <= max_len; '' first, then (len, lex)."""
    out = [""]
    frontier = [""]
    for _ in range(max_len):
        nxt = []
        for w in frontier:
            for c in _LETTERS:
                if w and _INV[w[-1]] == c:
                    continue
                nxt.append(w + c)
        nxt.sort()
        out.extend(nxt)
        frontier = nxt
    return out


def cyclic_subwords(word, lo, hi):
    """Cyclic subwords of ``word`` with length in [lo, hi] (each <= len(word)).

    ``word`` must be cyclically reduced — then the doubled word is freely reduced
    across the seam and every slice is freely reduced too.
    """
    n = len(word)
    if n == 0 or lo > n:
        return []
    doubled = word + word
    out = []
    for length in range(lo, min(hi, n) + 1):
        for s in range(n):
            out.append(doubled[s:s + length])
    return out


def donor_conjugators(r1_str, r2_str, wmax=2, subw=(3, 4)):
    """The finite conjugator family for one state, deduped, in deterministic order.

    Short words first (the fixed universal block), then the state-dependent
    subword block sorted by (length, lex). Inverses of subwords are covered by
    also slicing the inverse words.
    """
    fam = short_words(wmax) if wmax >= 0 else []
    if subw is not None:
        lo, hi = subw
        lo = max(lo, wmax + 1)          # never re-enumerate the universal block
        pool = []
        for base in (r1_str, r2_str, inv_word(r1_str), inv_word(r2_str)):
            pool.extend(cyclic_subwords(base, lo, hi))
        seen = set(fam)
        for w in sorted(set(pool), key=lambda s: (len(s), s)):
            if w not in seen:
                seen.add(w)
                fam.append(w)
    return fam


def _reduce_str(w):
    """Free reduction on an 'xXyY' string (engine-local; certify.py has its own)."""
    out = []
    for c in w:
        if out and out[-1] == _INV[c]:
            out.pop()
        else:
            out.append(c)
    return "".join(out)


def goal_conjugators(r1_str, r2_str, smax=2):
    """Goal-directed conjugator proposals: one donor edge that REPLACES a relator.

    For a target ``r_i``, donor ``r_j``, sign ``e`` and a short desired word
    ``s``, the rewrite ``r_i -> s`` is a single donor edge iff the right defect
    ``f = r_i^-1 s`` is a conjugate of ``r_j^e`` — then ``f = w r_j^e w^-1`` and
    ``r_i . w r_j^e w^-1 = s`` exactly. Conjugacy of a defect to the donor is a
    cyclic-word equality, so the check is decidable per candidate and the
    conjugator falls out of the match: peel the conjugating shell
    (``f = U . core . U^-1``), locate ``core`` among the donor's rotations
    (``core = p^-1 r_j^e p`` with ``p`` the length-k prefix), and take
    ``w = U p^-1``. This is a PROPOSER, not a new move: the emitted edge is the
    ordinary donor certificate, so its soundness and verification are untouched
    (a wrong ``w`` would merely propose a different, still-legal child).

    ``s`` ranges over freely reduced words with ``1 <= |s| <= smax``. Returns
    ``{(target, jsign): [w, ...]}`` for the combos where any candidate fires.
    """
    out = {}
    small = [s for s in short_words(smax) if s]
    for target in (1, 2):
        ri, ro = (r1_str, r2_str) if target == 1 else (r2_str, r1_str)
        if not ri or not ro:
            continue
        ri_inv = inv_word(ri)
        for jsign in (1, -1):
            rho = ro if jsign == 1 else inv_word(ro)
            doubled = rho + rho
            found = []
            for s in small:
                f = _reduce_str(ri_inv + s)
                shell = []
                while len(f) >= 2 and f[0] == _INV[f[-1]]:
                    shell.append(f[0])
                    f = f[1:-1]
                if not f or len(f) != len(rho):
                    continue
                k = doubled.find(f)
                if k < 0 or k >= len(rho):
                    continue
                w = _reduce_str("".join(shell) + inv_word(rho[:k]))
                found.append(w)
            if found:
                out[(target, jsign)] = sorted(set(found), key=lambda t: (len(t), t))
    return out


def abelian_vec(w):
    """Exponent-sum vector (e_x, e_y) of an 'xXyY' word."""
    ex = sum(1 for c in w if c == "x") - sum(1 for c in w if c == "X")
    ey = sum(1 for c in w if c == "y") - sum(1 for c in w if c == "Y")
    return ex, ey


def defect_factorization(f, donor, max_factors=4):
    """Exact factorization of ``f`` as a product of conjugates of ``donor^±1``.

    The search-usable distillate of the forest-flow / class-two pipeline
    (solve a linear relaxation, then lift to a literal identity), specialised
    to one donor at rank 2:

      * layer-0 obstruction (the class-repair pattern): in the abelianisation,
        ``ab(f) = t·ab(donor)`` must hold for an integer ``t`` with
        ``|t| <= max_factors`` — when ``ab(donor) != 0`` this rejects most
        candidates before any string work;
      * the lift (the flow pattern): greedily PEEL rotated copies of the donor
        out of the defect — if ``f = p·ρ·q`` with ``ρ`` a rotation of
        ``donor^ε``, then ``f = (p ρ p⁻¹)·(p q)``, one conjugate factor plus a
        strictly shorter residual. Leftmost occurrence first, deterministic.

    Returns ``[(jsign, w), ...]`` with ``f == Π w_k donor^{jsign_k} w_k⁻¹``
    EXACTLY (free-group identity, factors in order), or ``None``. Every letter
    of the input is accounted for: success requires the final residual to be
    the empty word.
    """
    if not donor or not f:
        return None
    av_d = abelian_vec(donor)
    av_f = abelian_vec(f)
    if av_d != (0, 0):
        # t·av_d == av_f for integer t, |t| <= max_factors
        ok = False
        for t in range(-max_factors, max_factors + 1):
            if (t * av_d[0], t * av_d[1]) == av_f:
                ok = True
                break
        if not ok:
            return None
    elif av_f != (0, 0):
        return None
    n = len(donor)
    rot_of = {}                       # rotated string -> (jsign, k)
    for jsign, base in ((1, donor), (-1, inv_word(donor))):
        for k in range(n):
            rot = base[k:] + base[:k]
            rot_of.setdefault(rot, (jsign, k))
    factors = []
    while f:
        if len(factors) >= max_factors or len(f) < n:
            return None
        hit = None
        for pos in range(len(f) - n + 1):
            info = rot_of.get(f[pos:pos + n])
            if info is not None:
                hit = (pos, info)
                break
        if hit is None:
            return None
        pos, (jsign, k) = hit
        p = f[:pos]
        base = donor if jsign == 1 else inv_word(donor)
        w = _reduce_str(p + inv_word(base[:k]))   # rot_k(base) = base[:k]⁻¹·base·base[:k]
        factors.append((jsign, w))
        f = _reduce_str(p + f[pos + n:])
    return factors


def ncrw_conjugates(r1_str, r2_str, smax=2, max_factors=4):
    """Multi-factor normal-closure rewrite proposals: ``r_i -> s`` in ONE edge.

    For each target ``i`` and each short ``s`` (``1 <= |s| <= smax``), factor
    the right defect ``ρ(r_i⁻¹ s)`` into conjugates of the OTHER relator via
    ``defect_factorization``. A hit with ``m >= 2`` factors is returned as
    ``{(target, s): [(jsign, w), ...]}`` (single-factor hits are already the
    goal-directed donor proposer's). Each hit is an exact AC composite:
    ``r_i · Π (w_k r_j^{ε_k} w_k⁻¹) = s`` letter for letter.
    """
    out = {}
    small = [s for s in short_words(smax) if s]
    for target in (1, 2):
        ri, ro = (r1_str, r2_str) if target == 1 else (r2_str, r1_str)
        if not ri or not ro:
            continue
        ri_inv = inv_word(ri)
        for s in small:
            f = _reduce_str(ri_inv + s)
            if not f:
                continue
            factors = defect_factorization(f, ro, max_factors=max_factors)
            if factors is not None and len(factors) >= 2:
                out[(target, s)] = factors
    return out


def _w_arrays(w):
    hit = _W_ARR_CACHE.get(w)
    if hit is None:
        wa = str_to_arr(w)
        hit = (wa, inverse_relator_nj(wa))
        _W_ARR_CACHE[w] = hit
    return hit


def donor_children(r1, r2, conjugators, cyclic_reduce=True, extra=None):
    """All conjugate-donor children of a canonical pair, tagged with certificates.

    ``conjugators`` applies to every (target, jsign) combo; ``extra`` is an
    optional ``{(target, jsign): [w, ...]}`` of per-combo additions (the
    goal-directed proposals). Yields ``(nr1, nr2, cert)`` with the child pair
    RAW (reduced but not canonicalised — the caller canonicalises, exactly like
    the substitution path) and ``cert = ("donor", target, jsign, w)``.
    """
    out = []
    base = list(conjugators)
    base_set = set(base)
    for target in (1, 2):
        ri, ro = (r1, r2) if target == 1 else (r2, r1)
        if len(ri) == 0 or len(ro) == 0:
            continue
        for jsign in (1, -1):
            oj = ro if jsign == 1 else inverse_relator_nj(ro)
            ws = base
            if extra:
                more = [w for w in extra.get((target, jsign), ()) if w not in base_set]
                if more:
                    ws = base + more
            for w in ws:
                if w:
                    wa, wia = _w_arrays(w)
                    piece = np.concatenate((ri, wa, oj, wia))
                else:
                    piece = np.concatenate((ri, oj))
                nri = reduce_relator_nj(piece, cyclic_reduce)
                cert = ("donor", target, jsign, w)
                if target == 1:
                    out.append((nri, r2, cert))
                else:
                    out.append((r1, nri, cert))
    return out


# --------------------------------------------------------------------------- solver

class MacroSolver:
    """Best-first search over substitution + donor edges with a pluggable ordering.

    Everything structural is the baseline's: per-relator length cap, reduce +
    canonicalise per child, visited-set dedup on first discovery, the
    ``(priority, depth, key)`` heap shape and its depth tie-break. Substitution
    children are enumerated first (identical children keep the cheaper
    substitution certificate); donor children follow in deterministic family
    order. With ``donor_wmax=-1, donor_subw=None, config=None`` this IS the
    baseline search, pop for pop.
    """

    def __init__(self, r1, r2, max_nodes=10000, max_relator_length=24,
                 cyclic_reduce=True, config=None, donor_wmax=2, donor_subw=None,
                 goal_smax=2, ncrw_smax=0, ncrw_max_factors=4):
        self.max_nodes = max_nodes
        self.max_relator_length = max_relator_length
        self.cyclic_reduce = cyclic_reduce
        self.donor_wmax = donor_wmax
        self.donor_subw = donor_subw
        self.goal_smax = goal_smax
        self.ncrw_smax = ncrw_smax
        self.ncrw_max_factors = ncrw_max_factors
        self.priority = make_priority(config)

        # ONE dict per discovered state: key -> (parent key, certificate of the
        # edge in). A macro node offers hundreds of children, so a 1,000-pop
        # search discovers ~10^5-10^6 states; duplicating the keys across
        # visited/cert_in/new_seen structures is what OOM-killed the first
        # benchmark run. Min/max stats are tracked incrementally instead.
        self.visited = dict()
        self.pq = []

        r1_arr = str_to_arr(r1)
        r2_arr = str_to_arr(r2)
        self.initial_state = canonical_pair_nj(
            reduce_relator_nj(r1_arr, self.cyclic_reduce),
            reduce_relator_nj(r2_arr, self.cyclic_reduce),
        )

    @property
    def donor_enabled(self):
        return (self.donor_wmax >= 0 or self.donor_subw is not None
                or self.goal_smax >= 1)

    def _children(self, r1, r2, key):
        """(nr1_raw, nr2_raw, cert) for every legal edge out of a canonical pair."""
        out = [
            (nr1, nr2, ("sub", int(t), int(j), int(k1), int(k2)))
            for nr1, nr2, t, j, k1, k2 in get_neighbors_with_moves_nj(r1, r2)
        ]
        if self.donor_enabled:
            fam = donor_conjugators(key[0], key[1],
                                    wmax=self.donor_wmax, subw=self.donor_subw)
            extra = (goal_conjugators(key[0], key[1], smax=self.goal_smax)
                     if self.goal_smax >= 1 else None)
            out.extend(donor_children(r1, r2, fam, self.cyclic_reduce, extra=extra))
        if self.ncrw_smax >= 1:
            hits = ncrw_conjugates(key[0], key[1], smax=self.ncrw_smax,
                                   max_factors=self.ncrw_max_factors)
            for (target, s), factors in sorted(hits.items()):
                cert = ("ncrw", target, tuple((int(j), w) for j, w in factors))
                child = str_to_arr(s)
                if target == 1:
                    out.append((child, r2, cert))
                else:
                    out.append((r1, child, cert))
        return out

    def solve(self, progress=None):
        """Return (path, certs, nodes_visited); path/certs None if unsolved.

        Min/max discovered and max-expanded stats live on ``self`` afterwards
        (``min_key``/``max_key``/``max_expanded_key``).
        """
        init_key = state_to_key(self.initial_state)
        init_total = len(init_key[0]) + len(init_key[1])
        heapq.heappush(self.pq, (self.priority(*init_key), 0, init_key))
        self.visited[init_key] = (None, None)
        nodes_visited = 0
        self.max_expanded_key = init_key
        self.min_key, self._min_total = init_key, init_total
        self.max_key, self._max_total = init_key, init_total

        while self.pq and nodes_visited < self.max_nodes:
            _, depth, key = heapq.heappop(self.pq)
            nodes_visited += 1
            if progress is not None and nodes_visited % _HB_CHECK_EVERY == 0:
                progress(nodes_visited)
            if len(key[0]) + len(key[1]) > \
                    len(self.max_expanded_key[0]) + len(self.max_expanded_key[1]):
                self.max_expanded_key = key
            r1, r2 = str_to_arr(key[0]), str_to_arr(key[1])

            if len(r1) == 1 and len(r2) == 1:
                path, certs = [], []
                state_key = key
                while state_key is not None:
                    path.append(state_key)
                    parent, cert = self.visited[state_key]
                    if cert is not None:
                        certs.append(cert)
                    state_key = parent
                path.reverse()
                certs.reverse()
                return path, certs, nodes_visited

            for nr1, nr2, cert in self._children(r1, r2, key):
                nr1r = reduce_relator_nj(nr1, self.cyclic_reduce)
                nr2r = reduce_relator_nj(nr2, self.cyclic_reduce)
                if len(nr1r) <= self.max_relator_length and \
                        len(nr2r) <= self.max_relator_length:
                    canon = canonical_pair_nj(nr1r, nr2r)
                    key_new = state_to_key(canon)
                    if key_new not in self.visited:
                        self.visited[key_new] = (key, cert)
                        total = len(key_new[0]) + len(key_new[1])
                        if total < self._min_total:
                            self.min_key, self._min_total = key_new, total
                        elif total > self._max_total:
                            self.max_key, self._max_total = key_new, total
                        heapq.heappush(self.pq,
                                       (self.priority(*key_new), depth + 1, key_new))

        return None, None, nodes_visited


# --------------------------------------------------------------------------- replay

def cert_child_raw(r1, r2, cert):
    """Re-apply one certificate to a raw pair; returns the RAW child pair.

    The engine-side decoder (the independent, string-based one is
    ``certify.py``). ``("sub", ...)`` reproduces ``replay_move_nj``'s
    construction; ``("donor", ...)`` reproduces ``donor_children``'s.
    """
    kind = cert[0]
    if kind == "sub":
        _, target, jsign, k1, k2 = cert
        ri, ro = (r1, r2) if target == 1 else (r2, r1)
        oj = ro if jsign == 1 else inverse_relator_nj(ro)
        piece = np.concatenate((np.roll(ri, 2 * k1), np.roll(oj, 2 * k2)))
    elif kind == "donor":
        _, target, jsign, w = cert
        ri, ro = (r1, r2) if target == 1 else (r2, r1)
        oj = ro if jsign == 1 else inverse_relator_nj(ro)
        if w:
            wa = str_to_arr(w)
            piece = np.concatenate((ri, wa, oj, inverse_relator_nj(wa)))
        else:
            piece = np.concatenate((ri, oj))
    elif kind == "ncrw":
        _, target, factors = cert
        ri, ro = (r1, r2) if target == 1 else (r2, r1)
        parts = [ri]
        for jsign, w in factors:
            oj = ro if jsign == 1 else inverse_relator_nj(ro)
            if w:
                wa = str_to_arr(w)
                parts.extend((wa, oj, inverse_relator_nj(wa)))
            else:
                parts.append(oj)
        piece = np.concatenate(parts)
    else:
        raise ValueError(f"unknown certificate kind {kind!r}")
    if cert[1] == 1:
        return piece, r2
    return r1, piece


def certs_to_states(r1_str, r2_str, certs, cyclic_reduce=True):
    """Replay a certificate list into the canonical state sequence (len(certs)+1)."""
    r1 = reduce_relator_nj(str_to_arr(r1_str), cyclic_reduce)
    r2 = reduce_relator_nj(str_to_arr(r2_str), cyclic_reduce)
    r1, r2 = canonical_pair_nj(r1, r2)
    states = [[arr_to_str(r1), arr_to_str(r2)]]
    for cert in certs:
        nr1, nr2 = cert_child_raw(r1, r2, tuple(cert))
        nr1 = reduce_relator_nj(nr1, cyclic_reduce)
        nr2 = reduce_relator_nj(nr2, cyclic_reduce)
        r1, r2 = canonical_pair_nj(nr1, nr2)
        states.append([arr_to_str(r1), arr_to_str(r2)])
    return states


def macro_cost(cert):
    """Certificate-level action count of one edge (the graph-traversal cost)."""
    if cert[0] == "sub":
        return 1
    if cert[0] == "ncrw":
        return sum(3 if j == 1 else 5 for j, _ in cert[2])
    return 3 if cert[2] == 1 else 5


def elementary_cost(cert, parent_lens):
    """Strict one-letter-conjugation cost of one edge (the honest expansion cost).

    Substitution: rotating the target by k1 is min(k1, n1-k1) conjugations (left
    or right, whichever is shorter); the source rotation must also be undone
    (2x), plus the multiply, plus an invert/restore pair when jsign is -1.
    Donor: 2|w| + 1, plus 2 when jsign is -1. A multi-factor rewrite sums its
    factors' donor costs.
    """
    if cert[0] == "donor":
        _, _, jsign, w = cert
        return 2 * len(w) + 1 + (2 if jsign == -1 else 0)
    if cert[0] == "ncrw":
        return sum(2 * len(w) + 1 + (2 if j == -1 else 0) for j, w in cert[2])
    _, target, jsign, k1, k2 = cert
    n1 = parent_lens[0] if target == 1 else parent_lens[1]
    n2 = parent_lens[1] if target == 1 else parent_lens[0]
    rot1 = min(k1, n1 - k1) if n1 else 0
    rot2 = min(k2, n2 - k2) if n2 else 0
    return rot1 + 2 * rot2 + 1 + (2 if jsign == -1 else 0)


# --------------------------------------------------------------------------- entry

def _jsonable_cert(cert):
    """Certificate tuple -> nested lists (json-safe; ncrw factors included)."""
    if cert[0] == "ncrw":
        return ["ncrw", cert[1], [[j, w] for j, w in cert[2]]]
    return list(cert)


def macro_greedy_search(r1_str, r2_str, node_budget, max_relator_length=24,
                        cyclic_reduce=True, config=None, donor_wmax=2,
                        donor_subw=None, goal_smax=2, ncrw_smax=0,
                        ncrw_max_factors=4, progress=None):
    """Run the macro greedy on one presentation; return the baseline stats dict + extras.

    The eleven baseline keys are unchanged in meaning. ``path_moves`` is always
    ``[]`` (donor edges have no Definition 2.1 encoding); the certificate is
    ``path_certs``, replayable by ``certs_to_states`` and independently by
    ``certify.verify_solution``. Extra keys:

      engine            'sub+donor' (or 'sub' when donor moves are disabled)
      path_certs        [["sub", t, j, k1, k2] | ["donor", t, j, w], ...]
      macro_cost        sum of certificate-level action counts over the path
      elementary_cost   sum of strict one-letter-conjugation expansion costs
      n_donor_edges     how many path edges are donor macros
    """
    solver = MacroSolver(
        r1_str, r2_str,
        max_nodes=node_budget,
        max_relator_length=max_relator_length,
        cyclic_reduce=cyclic_reduce,
        config=config,
        donor_wmax=donor_wmax,
        donor_subw=donor_subw,
        goal_smax=goal_smax,
        ncrw_smax=ncrw_smax,
        ncrw_max_factors=ncrw_max_factors,
    )
    path, certs, nodes_visited = solver.solve(progress)

    min_key = solver.min_key
    max_key = solver.max_key
    exp_key = solver.max_expanded_key

    solved = path is not None
    if solved:
        path_states = [[k[0], k[1]] for k in path]
        path_certs = [_jsonable_cert(c) for c in certs]
        parent_lens = [(len(k[0]), len(k[1])) for k in path[:-1]]
        mcost = sum(macro_cost(c) for c in certs)
        ecost = sum(elementary_cost(c, pl) for c, pl in zip(certs, parent_lens))
        n_donor = sum(1 for c in certs if c[0] == "donor")
        n_ncrw = sum(1 for c in certs if c[0] == "ncrw")
        path_length = len(path_states) - 1
    else:
        path_states, path_certs = [], []
        mcost = ecost = n_donor = n_ncrw = None
        path_length = None

    parts = ["sub"]
    if solver.donor_enabled:
        parts.append("donor")
    if solver.ncrw_smax >= 1:
        parts.append("ncrw")
    return {
        "solved": solved,
        "nodes_explored": nodes_visited,
        "path_length": path_length,
        "min_relator_length": len(min_key[0]) + len(min_key[1]),
        "min_relator": [min_key[0], min_key[1]],
        "max_relator_length": len(max_key[0]) + len(max_key[1]),
        "max_relator": [max_key[0], max_key[1]],
        "max_relator_length_expanded": len(exp_key[0]) + len(exp_key[1]),
        "max_relator_expanded": [exp_key[0], exp_key[1]],
        "path": path_states,
        "path_moves": [],
        "engine": "+".join(parts),
        "path_certs": path_certs,
        "macro_cost": mcost,
        "elementary_cost": ecost,
        "n_donor_edges": n_donor,
        "n_ncrw_edges": n_ncrw,
    }
