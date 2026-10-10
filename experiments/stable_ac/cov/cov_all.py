"""Brute-force subword CoV: every substitution pattern, one start per class.

``cov.enumerate_cov`` takes ONE substitution pattern per z-word (a greedy
left-to-right pass on the stored rotation, plus at most one seam match that the
linear pass did not already shadow) and drops z-words through the no-collapse
gate. This module is the exhaustive family, tag ``suballpxyb8``:

* z ranges over every cyclic subword w of a relator r with 2 <= |w| <= |r| - 1,
  seam included, ``w ~ w⁻¹`` deduped. No other gate. |w| = 1 is a rename.
  |w| = |r| makes w a rotation of r^±1, so z = 1 in the group: replacing w by
  z elsewhere deletes a copy of r, which is the greedy's own S-move.
* an occurrence is any cyclic window equal to ``w`` or ``w⁻¹`` — the seam is a
  position like any other, never a second pass.
* a pattern is any set of pairwise non-overlapping occurrences in r1 together
  with any such set in r2, at least one occurrence in total. Partial
  substitution is a legal CoV (z = w holds wherever it is applied), and which
  occurrences are taken changes the output.
* each pattern is destabilized on both targets (x, y) and from every isolating
  relator (r1′, r2′), as in ``cov.cov_branches``.

Outputs are then quotiented by ``equivalence_classes.lib.words.relabel_key``:
relator order, cyclic rotation and inversion of a relator, and the 8 signed
permutations of {x, y} (x↔y, x→X, y→Y). The last 8 are the elementary
automorphisms; they give the greedy an isomorphic search graph (node counts
differ only through heap ties), so one start per class is searched and the
class of the input itself is dropped (it is the control row). Outputs that are
automorphic to the input by a length-changing automorphism are a different
class and are kept.

Isolation from the defining relator Z·w (``cov.cov_branches``'s
``allow_defining_iso``) is out of scope here, as in the subword sweep: that
branch returns the same pair for every pattern, an elementary Nielsen image.
"""

from itertools import product

from experiments.equivalence_classes.lib.words import relabel_key
from experiments.greedy_tests.spec.words import inverse, reduce_word, word_to_str
from experiments.stable_ac.cov import cov

FAMILY_TAG = "suballpxyb8"

X, Y, Z = cov.X_GEN, cov.Y_GEN, cov.Z_GEN


def class_key(r1, r2):
    """The pair up to relator order, rotation, inversion and the 8 relabelings."""
    return relabel_key((word_to_str(tuple(r1)), word_to_str(tuple(r2))))


def subwords(r1, r2, min_len=cov.SUBWORD_MIN_LEN, proper=True):
    """Every cyclic subword w of a relator r, ``w ~ w⁻¹`` deduped.

    ``proper`` (the family rule) keeps 2 <= |w| <= |r| - 1 and drops any w that
    is a whole rotation of either relator or its inverse, even when it also
    sits strictly inside the other one. ``proper=False`` adds |w| = |r|.
    """
    cycs = [reduce_word(tuple(rel), cyclic=True) for rel in (r1, r2)]
    seen, whole = set(), set()
    for cyc in cycs:
        n = len(cyc)
        doubled = cyc + cyc
        for length in range(min_len, n + 1):
            for i in range(n):
                w = doubled[i:i + length]
                w = max(w, inverse(w))
                seen.add(w)
                if length == n:
                    whole.add(w)
    if proper:
        seen -= whole
    return tuple(sorted(seen, key=lambda w: (len(w), w)))


def occurrences(cyc, w):
    """``(start, sign)`` for every cyclic window of ``cyc`` equal to w / w⁻¹."""
    n, L = len(cyc), len(w)
    if L > n:
        return ()
    w_inv = inverse(w)
    doubled = cyc + cyc
    out = []
    for i in range(n):
        chunk = doubled[i:i + L]
        if chunk == w:
            out.append((i, 1))
        elif chunk == w_inv:
            out.append((i, -1))
    return tuple(out)


def patterns(occs, n, L):
    """Every set of pairwise non-overlapping occurrences, the empty set first."""
    masks = []
    for start, _ in occs:
        mask = 0
        for j in range(L):
            mask |= 1 << ((start + j) % n)
        masks.append(mask)
    out = []

    def extend(k, used, chosen):
        if k == len(occs):
            out.append(tuple(chosen))
            return
        extend(k + 1, used, chosen)
        if not used & masks[k]:
            chosen.append(occs[k])
            extend(k + 1, used | masks[k], chosen)
            chosen.pop()

    extend(0, 0, [])
    return out


def substitute_pattern(cyc, chosen, L):
    """``cyc`` with each chosen occurrence replaced by ±z, freely reduced."""
    if not chosen:
        return cyc
    n = len(cyc)
    base = chosen[0][0]  # rotate a chosen window to the front: none then wraps
    rot = cyc[base:] + cyc[:base]
    at = {(start - base) % n: sign for start, sign in chosen}
    out, i = [], 0
    while i < n:
        if i in at:
            out.append(Z * at[i])
            i += L
        else:
            out.append(rot[i])
            i += 1
    return reduce_word(tuple(out), cyclic=False)


def raw_covs(r1, r2, default_cap=cov.DEFAULT_CAP, cap_headroom=cov.CAP_HEADROOM,
             reject_len=cov.REJECT_LEN, iso_targets=("x", "y"), proper=True):
    """Yield a ``CoVResult`` for every (z, pattern, target, isolating relator).

    Nothing is deduplicated here. Skipped: an output with an empty relator, and
    an output relator longer than ``reject_len`` (the solver's structural cap).
    """
    c1 = reduce_word(tuple(r1), cyclic=True)
    c2 = reduce_word(tuple(r2), cyclic=True)
    for w in subwords(c1, c2, proper=proper):
        L = len(w)
        r_def = cov.defining_relator(w)
        p1 = patterns(occurrences(c1, w), len(c1), L)
        p2 = patterns(occurrences(c2, w), len(c2), L)
        for ch1, ch2 in product(p1, p2):
            if not ch1 and not ch2:
                continue
            r1s = substitute_pattern(c1, ch1, L)
            r2s = substitute_pattern(c2, ch2, L)
            for target in iso_targets:
                gen = X if target == "x" else Y
                for iso_index, r_iso, keep in ((0, r1s, r2s), (1, r2s, r1s)):
                    ok, expr = cov.isolate(r_iso, x=gen)
                    if not ok:
                        continue
                    r_a = cov.substitute_generator(keep, gen, expr)
                    r_b = cov.substitute_generator(r_def, gen, expr)
                    if not r_a or not r_b:
                        continue
                    assert not any(abs(g) == gen for g in r_a + r_b)
                    if max(len(r_a), len(r_b)) > reject_len:
                        continue
                    o1, o2 = cov.relabel(r_a, target), cov.relabel(r_b, target)
                    yield cov.CoVResult(
                        applicable=True, r1=o1, r2=o2, n_cov=1,
                        cap=max(default_cap, max(len(o1), len(o2)) + cap_headroom),
                        z_word=w, iso_index=iso_index, iso_gen=target, expr=expr,
                        n_subs=len(ch1) + len(ch2),
                        meta={"pattern": (ch1, ch2),
                              "intermediate": (r1s, r2s, r_def)},
                    )


def enumerate_classes(r1, r2, **knobs):
    """One ``CoVResult`` per class, the input's own class removed.

    The representative is the first raw CoV of the class in ``raw_covs`` order,
    searched exactly as produced. ``meta["multiplicity"]`` counts the raw CoVs
    that fell in the class; ``meta["class_key"]`` is the dedup key.
    """
    own = class_key(r1, r2)
    reps, count = {}, {}
    for res in raw_covs(r1, r2, **knobs):
        o1 = reduce_word(res.r1, cyclic=True)
        o2 = reduce_word(res.r2, cyclic=True)
        if not o1 or not o2:
            continue
        key = class_key(o1, o2)
        if key == own:
            continue
        count[key] = count.get(key, 0) + 1
        if key not in reps:
            res.meta["class_key"] = key
            reps[key] = res
    for key, res in reps.items():
        res.meta["multiplicity"] = count[key]
    return tuple(reps.values())
