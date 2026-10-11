"""Automorphisms of F2: Whitehead canonical form, orbit test, certificate transport.

* ``aut_canon(pres) -> AutCanon(total, rep, phi)``: the Aut-minimal canonical
  representative and the automorphism (factors of ``AUTOS``) that maps ``pres``
  onto it (``whitehead``).
* ``orbit_key(pres, backend)``: ``(total, rep)`` from the pure (``"spec"``) or
  numba (``"fast"``) implementation; the two are parity-tested in
  ``tests/test_aut.py``, and this is the only way the fast one is used.
* ``automorphism(p, q)`` (factors mapping ``p`` onto ``q``, or None), ``are_automorphic(p, q)``.
* ``transport(pres, phi, path, start)``: a solve of ``start`` ~ ``phi(pres)``
  becomes an elementary AC path on ``pres`` (replayed before it is returned);
  ``solve_via_aut_min`` chains canon, search and transport.

An aut-assisted solve counts for a row only after its transported path replays
on that row.
"""
from .transport import solve_via_aut_min, transport
from .whitehead import AUTOS, AutCanon, are_automorphic, aut_canon, automorphism, check, images, invert


def orbit_key(pres, backend="spec", level_cap=50_000):
    """``(total, rep)``: the Aut(F2)-orbit invariant, from either backend."""
    if backend == "fast":
        from .fast import aut_min
        return aut_min(pres, level_cap)
    if backend != "spec":
        raise ValueError(f"backend {backend!r} not in ('spec', 'fast')")
    return tuple(aut_canon(pres, level_cap)[:2])
