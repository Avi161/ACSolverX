"""Invert an automorphism of F2, by Nielsen reduction with tracking.

Why this exists
---------------
The search records, for each root ``P``, a change of variables ``phi`` carrying it to its
Aut-minimal representative: ``canon(phi(P)) == rep``. Two roots ``A``, ``B`` in the same
Aut-class therefore come with *two* substitutions into a shared third form. That is a valid
proof, but it is not the statement a reader wants. The readable statement is a **single**
substitution:

    canon(psi(A)) == canon(B),   psi = phi_B^-1 . phi_A

which says outright "B is A with these words substituted for the generators". Getting it needs
``phi_B^-1``, which is what this module computes.

How
---
Nielsen-reduce the pair ``(u, v) = (phi(x), phi(y))`` to a pair of single letters, carrying
tracking words ``(A, B)`` with the invariant

    u_t == phi(A_t)   and   v_t == phi(B_t)      (start: A = x, B = y)

At the end ``u`` is a single letter ``g`` (possibly inverted). ``phi(A) == g``, so
``phi^-1(g) == A`` -- and if ``g`` came out inverted, ``phi^-1(|g|) == A^-1``. Same for ``v``.

The result is *checked, never trusted*: ``invert`` verifies ``phi(phi^-1(x)) == x`` and
``phi^-1(phi(x)) == x`` on both generators before returning, and raises otherwise. Downstream,
``verify_proofs.py`` re-checks the composite by pure substitution and never calls this file --
so a bug here cannot make a bad certificate pass, it can only fail to produce one.

Termination: each move strictly shortens ``|u| + |v|``, and Nielsen's theorem says a basis of
F2 reduces to a pair of distinct generators.
"""
from experiments.equivalence_classes.lib.words import apply_hom, free_reduce, inv

ID = {"x": "x", "y": "y"}


def _pairs(u, v, a, b):
    """Every elementary Nielsen move on (u, v), each carrying its tracking words."""
    return [
        (free_reduce(u + v), v, free_reduce(a + b), b),
        (free_reduce(u + inv(v)), v, free_reduce(a + inv(b)), b),
        (free_reduce(v + u), v, free_reduce(b + a), b),
        (free_reduce(inv(v) + u), v, free_reduce(inv(b) + a), b),
        (u, free_reduce(v + u), a, free_reduce(b + a)),
        (u, free_reduce(v + inv(u)), a, free_reduce(b + inv(a))),
        (u, free_reduce(u + v), a, free_reduce(a + b)),
        (u, free_reduce(inv(u) + v), a, free_reduce(inv(a) + b)),
    ]


def invert(phi):
    """phi^-1, as a dict 'x'->word, 'y'->word. Raises if phi is not an automorphism."""
    u, v = free_reduce(phi["x"]), free_reduce(phi["y"])
    a, b = "x", "y"

    while True:
        n = len(u) + len(v)
        if n == 0:
            raise ValueError(f"not an automorphism: x->{phi['x']}, y->{phi['y']}")
        best = None
        for cu, cv, ca, cb in _pairs(u, v, a, b):
            if cu and cv and len(cu) + len(cv) < n:
                if best is None or len(cu) + len(cv) < len(best[0]) + len(best[1]):
                    best = (cu, cv, ca, cb)
        if best is None:
            break
        u, v, a, b = best

    if len(u) != 1 or len(v) != 1 or u.lower() == v.lower():
        raise ValueError(f"not an automorphism: x->{phi['x']}, y->{phi['y']} "
                         f"(Nielsen-reduced to {u!r}, {v!r})")

    # phi(a) == u. If u is an inverted generator, phi(a^-1) == |u|, so phi^-1(|u|) == a^-1.
    out = {u.lower(): (a if u.islower() else inv(a)),
           v.lower(): (b if v.islower() else inv(b))}

    for g in ("x", "y"):                       # never trust it -- prove it, both ways round
        if apply_hom(out[g], phi) != g or apply_hom(phi[g], out) != g:
            raise ValueError(f"inverse check failed for phi: x->{phi['x']}, y->{phi['y']}")
    return out


def compose(f, g):
    """f . g -- apply g first, then f."""
    return {"x": apply_hom(g["x"], f), "y": apply_hom(g["y"], f)}
