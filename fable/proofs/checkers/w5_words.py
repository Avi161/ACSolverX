"""Minimal free-group word utilities for the W5 bridge-invariant probes.

Self-contained on purpose: this lane may not modify existing code, and the
checkers must be independently readable.  Words are strings over
``xyzXYZ``; lowercase is a generator, uppercase its inverse.
"""

from __future__ import annotations

GENS = "xyz"


def inv(w: str) -> str:
    """Formal inverse of a word."""
    return "".join(c.swapcase() for c in reversed(w))


def reduce_word(w: str) -> str:
    """Free reduction (stack based)."""
    out: list[str] = []
    for c in w:
        if out and out[-1] == c.swapcase():
            out.pop()
        else:
            out.append(c)
    return "".join(out)


def mul(*ws: str) -> str:
    return reduce_word("".join(ws))


def subst(w: str, images: dict[str, str]) -> str:
    """Substitute each generator by a word; ``images`` keyed by lowercase gen."""
    parts: list[str] = []
    for c in w:
        img = images[c.lower()]
        parts.append(img if c.islower() else inv(img))
    return reduce_word("".join(parts))


def abelianize(w: str) -> tuple[int, int, int]:
    v = [0, 0, 0]
    for c in w:
        i = GENS.index(c.lower())
        v[i] += 1 if c.islower() else -1
    return tuple(v)  # type: ignore[return-value]


def drop_gen(w: str, gen: str) -> str:
    """Delete every occurrence of ``gen`` (both signs) and freely reduce."""
    return reduce_word("".join(c for c in w if c.lower() != gen))


# ---------------------------------------------------------------- AC moves --

def check_ac2(before: tuple[str, ...], after: tuple[str, ...],
              i: int, j: int, e: int, w: str) -> bool:
    """Verify ``after`` = ``before`` with row i replaced by r_i * w r_j^e w^-1."""
    if i == j or e not in (1, -1):
        return False
    n = len(before)
    if len(after) != n:
        return False
    rj = before[j] if e == 1 else inv(before[j])
    want = mul(before[i], w, rj, inv(w))
    for k in range(n):
        exp = want if k == i else reduce_word(before[k])
        if reduce_word(after[k]) != exp:
            return False
    return True


def check_ac1(before: tuple[str, ...], after: tuple[str, ...], i: int) -> bool:
    """Verify ``after`` = ``before`` with row i inverted."""
    n = len(before)
    if len(after) != n:
        return False
    for k in range(n):
        exp = inv(reduce_word(before[i])) if k == i else reduce_word(before[k])
        if reduce_word(after[k]) != exp:
            return False
    return True


def apply_ac2(state: tuple[str, ...], i: int, j: int, e: int, w: str) -> tuple[str, ...]:
    rj = state[j] if e == 1 else inv(state[j])
    new = list(state)
    new[i] = mul(state[i], w, rj, inv(w))
    return tuple(new)


# --------------------------------------------------------- lane constants --

A = "xzYXyxZXYxyZ"
B = "XyxZXYXyxzXYxy"
K_XY = "zYX"      # Txy kill word (certified AC-trivial triple)
K_PUB = "Xyz"     # Tpub kill word (the open bridge endpoint)

# recorded elsewhere in the repo (.scratch/mms02_u_xy_bridge.md), used as controls
REC_PAIR_XY = ("xyxYXXY", "XyxYXXYXyxxyXYxy")
REC_PAIR_PUB = ("xYxYXyyXYxyXy", "XyyXYXyxYYxy")
AK3 = ("xxxYYYY", "xyxYXY")
