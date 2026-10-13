"""The hybrid solver: solves balanced two-generator presentations by a cascade and one best-first search.

    from acx.hybrid import solve
    res = solve(Presentation.parse("YYXyx", "Yx"))       # HybridConfig() defaults
    res.solved, res.kind, res.units, len(res.path)       # res.path replays under acx.verify.replay

Modules, in the order a solve uses them:

* ``cascade``, ``pinch``: stages A-C on the canonical pair and the finishing gates;
* ``search``: the best-first search over rank two (``frontier``, ``kernels``) and higher rank (``dynrank``);
* ``capwatch``: the cap counters of the limits ``r2_cap``, ``dyn_cap`` and ``slack``;
* ``solver``: ``solve``, the config and the result;
* ``elementary``, ``frame``: the certificate as elementary AC moves, replayed by ``acx.verify.replay``.

A result is an ``ac_path`` (rank two throughout) or a ``stable_cert`` (the path used higher rank).
"""
from .elementary import certify
from .solver import HybridConfig, HybridResult, decode_steps, encode_steps, solve

__all__ = ["HybridConfig", "HybridResult", "certify", "decode_steps", "encode_steps", "solve"]
