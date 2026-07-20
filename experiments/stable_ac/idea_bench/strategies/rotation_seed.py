"""rotation_seed: the cheap CONTROL — NOT a change of variables. Re-seeds the SAME
presentation (same group, same Aut-orbit) as every cyclic rotation of r1 paired with
every cyclic rotation of r2, plus the inverse (reversed + case-swapped) of each relator
rotated the same way. Only the start STRING differs; the coordinates don't. Rationale:
the greedy canonicalizes internally, but its Booth-seed and tie-break are sensitive to
the exact start string, so re-seeding alone might flip a solve. This measures how much
of any CoV "win" elsewhere in the benchmark is really just string-seed luck vs a genuine
coordinate change. Pure string ops, no search; ranked shortest-total-length first (all
candidates are equal length here since rotation/inversion never changes word length, so
this is effectively a stable pass-through that keeps the original pair first); deduped;
capped at 60. The original pair is always candidate 0, so this strategy never regresses
coverage relative to baseline."""

import math

NAME = "rotation_seed"
KIND = "transform"

MAX_CANDIDATES = 60


def _rotate(w, k):
    if not w:
        return w
    k %= len(w)
    return w[k:] + w[:k]


def _inverse(w):
    return "".join(c.swapcase() for c in reversed(w))


def _sample_offsets(length, n):
    """Up to n evenly spaced rotation offsets in [0, length), always including 0."""
    if length <= 0:
        return [0]
    n = max(1, min(n, length))
    step = max(1, math.ceil(length / n))
    return list(range(0, length, step))


def _variants(w, per_orientation):
    """Rotations of w and of inv(w) at sampled offsets, deduped, w's own rotations
    first (offset 0 = w itself)."""
    out, seen = [], set()
    for base in (w, _inverse(w)):
        for k in _sample_offsets(len(base), per_orientation):
            rw = _rotate(base, k)
            if rw in seen:
                continue
            seen.add(rw)
            out.append(rw)
    return out


def candidates(r1, r2, cap):
    # Budget variants per relator so the Cartesian product stays close to
    # MAX_CANDIDATES; the final slice below is the hard guarantee regardless.
    per_orientation = max(1, math.isqrt(MAX_CANDIDATES // 2))
    v1 = _variants(r1, per_orientation)
    v2 = _variants(r2, per_orientation)

    out, seen = [], set()
    out.append((r1, r2, cap))          # original pair first: never regress coverage
    seen.add((r1, r2))
    for a in v1:
        for b in v2:
            if (a, b) in seen:
                continue
            seen.add((a, b))
            out.append((a, b, cap))

    # Shortest-total-length first (a stable no-op here: rotation/inversion preserve
    # length, so every candidate ties and insertion order — original pair, then
    # rotation variants — is kept).
    out.sort(key=lambda t: len(t[0]) + len(t[1]))
    return out[:MAX_CANDIDATES]
