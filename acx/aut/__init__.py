"""Automorphisms of F2: Whitehead canonical form, orbit test, certificate transport.

``aut_canon(pres)`` is the Aut-minimal representative with its witness ``phi`` (``whitehead``); ``orbit_key`` gives
``(total, rep)`` from the pure (``"spec"``) or numba (``"fast"``) implementation, parity-tested in ``tests/test_aut.py``;
``automorphism`` / ``are_automorphic`` relate two presentations; ``transport`` and ``solve_via_aut_min`` carry a solve
of the representative back to the row as elementary AC moves, counted only after they replay on it.
"""
from .transport import solve_via_aut_min, transport
from .whitehead import AUTOS, are_automorphic, aut_canon, automorphism, check, images, invert


def orbit_key(pres, backend="spec", level_cap=50_000):
    """``(total, rep)``: the Aut(F2)-orbit invariant, from either backend."""
    if backend == "fast":
        from .fast import aut_min
        return aut_min(pres, level_cap)
    if backend != "spec":
        raise ValueError(f"backend {backend!r} not in ('spec', 'fast')")
    return tuple(aut_canon(pres, level_cap)[:2])
