"""Rank-preserving structure of all-triangle AC states: when can a unit or a
length-two relator appear?

All statements below are about *ordinary* AC normal-product substitutions

    R_i  <-  rot(R_i) . rot(R_j^eps)          (i != j, eps = +-1)

applied to a state whose relators are cyclic words, and read modulo cyclic
rotation and inversion (``search.canonical``).  Rank and the declared generator
set are fixed throughout: no generator is added or removed.

Lemma 1 (parity).  The cyclically reduced length of a product of cyclic words of
lengths p and q is congruent to p + q modulo 2.  Free reduction and cyclic
reduction each delete two letters at a time, so the parity of the concatenation
p + q is preserved.  Consequences for an all-triangle state (every |R_i| = 3):

  * triangle x triangle has even length, hence lies in {0, 2, 4, 6}: a **unit
    relator cannot be created in one move**;
  * quartic x triangle has odd length, hence lies in {1, 3, 5, 7}: a **length-two
    relator cannot be created from a quartic and a triangle**.

So from an all-triangle state the only one-move route to length two is
triangle x triangle, and every route to a unit passes through a relator of
length != 3.

Lemma 2 (bigon necessity).  Write inv2(u, v) = (v^-1, u^-1) for the involution
induced on cyclic digrams by inversion.  If a single triangle x triangle
substitution yields a relator of cyclic length two, then the two relators
involved share a cyclic digram modulo inv2.

  Proof sketch.  Length 6 -> 2 deletes exactly two inverse pairs.  With
  a = a1 a2 a3 and b = b1 b2 b3 the deletions occur at the seam (a3 b1) and then
  either again at the seam (a2 b2) or at the cyclic wrap (a1 vs b3).
    - Two seam deletions force b1 b2 = (a2 a3)^-1, so inv2(a2, a3) is a digram
      of b.
    - One seam and one wrap deletion force b1 = a3^-1 and b3 = a1^-1, so
      inv2(a3, a1) = (a1^-1, a3^-1) is a digram of b.
  Either way a digram of a matches one of b under inv2.  []

The converse fails exactly when the two relators coincide as canonical cyclic
words: then the matched rotation cancels completely and the product has length
zero rather than two.  ``check_bigon_criterion`` machine-checks both directions.

Definition.  A state is *digram-disjoint* when no two distinct relators share a
cyclic digram modulo inv2.  By Lemma 2 a digram-disjoint all-triangle state
admits **no** one-move length-two relator, and by Lemma 1 none of length one, so
its entire cap-3 neighbourhood is empty and its cap-4 neighbourhood consists
only of length-four relators.
"""
from __future__ import annotations

import search


def cyclic_digrams(word):
    """The cyclic digrams of ``word`` (empty for length < 2)."""
    n = len(word)
    if n < 2:
        return set()
    return {(word[k], word[(k + 1) % n]) for k in range(n)}


def inv2(digram):
    """The involution induced on digrams by inverting the word."""
    u, v = digram
    return (-v, -u)


def canonical_digram(digram):
    return min(digram, inv2(digram))


def digram_profile(state):
    return [{canonical_digram(d) for d in cyclic_digrams(w)} for w in state]


def shared_digram_pairs(state):
    """[(i, j, sorted shared canonical digrams)] over i < j."""
    profile = digram_profile(state)
    out = []
    for i in range(len(state)):
        for j in range(i + 1, len(state)):
            common = profile[i] & profile[j]
            if common:
                out.append((i, j, sorted(common)))
    return out


def is_digram_disjoint(state):
    return not shared_digram_pairs(state)


def coupling(state):
    """How much digram sharing the state has: (pairs, total shared digrams).

    Lemma 2 makes a positive first coordinate a *necessary* condition for a
    one-move length-two relator, so a search that maximises it is climbing
    toward the only gate through which a bigon can appear.
    """
    pairs = shared_digram_pairs(state)
    return len(pairs), sum(len(c) for _, _, c in pairs)


def rotation_product(target, donor, sign, target_cut, donor_cut):
    """The canonical cyclic product used by every substitution move."""
    base = donor if sign == 1 else search.inverse(donor)
    left = target[target_cut:] + target[:target_cut]
    right = base[donor_cut:] + base[:donor_cut]
    return search.canonical(left + right)


def one_step_products(state, relator_cap):
    """Every (i, j, sign, k1, k2, product) with 1 <= |product| <= relator_cap.

    ``attempted`` counts every rotation product formed, which is the unit the
    campaign reports as search work.
    """
    out, attempted = [], 0
    for i, target in enumerate(state):
        for j, donor in enumerate(state):
            if i == j or not target or not donor:
                continue
            for sign in (1, -1):
                base = donor if sign == 1 else search.inverse(donor)
                for k1 in range(len(target)):
                    left = target[k1:] + target[:k1]
                    for k2 in range(len(base)):
                        attempted += 1
                        product = search.canonical(left + base[k2:] + base[:k2])
                        if 1 <= len(product) <= relator_cap:
                            out.append((i, j, sign, k1, k2, product))
    return out, attempted


def shortest_relator(state):
    return min((len(w) for w in state), default=0)


def has_bigon(state):
    return any(len(w) == 2 for w in state)


def has_unit(state):
    return any(len(w) == 1 for w in state)


def check_parity_lemma(state, relator_cap=64):
    """Every one-move product has length congruent to |R_i| + |R_j| mod 2."""
    violations = []
    for i, target in enumerate(state):
        for j, donor in enumerate(state):
            if i == j:
                continue
            for sign in (1, -1):
                base = donor if sign == 1 else search.inverse(donor)
                for k1 in range(len(target)):
                    for k2 in range(len(base)):
                        product = rotation_product(target, donor, sign, k1, k2)
                        if (len(product) - len(target) - len(donor)) % 2:
                            violations.append((i, j, sign, k1, k2, product))
    return violations


def check_bigon_criterion(state):
    """Compare Lemma 2's necessary condition against brute force.

    Returns a dict with the brute-force bigon witnesses, whether the state is
    digram-disjoint, and any necessity violation (a bigon with no shared
    digram).  ``degenerate`` flags the equal-relator case in which sharing does
    not produce a bigon.
    """
    products, attempted = one_step_products(state, relator_cap=max(map(len, state), default=3) * 2)
    bigons = [p for p in products if len(p[-1]) == 2]
    shared = shared_digram_pairs(state)
    necessity_violated = bool(bigons) and not shared
    return {
        'bigons': bigons,
        'shared_digram_pairs': shared,
        'digram_disjoint': not shared,
        'necessity_violated': necessity_violated,
        'degenerate_equal_relators': len(set(state)) < len(state),
        'rotation_products': attempted,
    }
