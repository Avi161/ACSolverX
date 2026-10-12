"""The n-generator search (``acx.ngen``): SAC triangulation, its replayable lift, ``solve``, and the rank-n sweep.

Method and results: ``docs/RANK3.md``. The sweep is the package ``acx.ngen.sweep`` (run it with ``python -m``).
"""
from .lift import lift
from .sac import check, define, triangulate
from .solve import NGenConfig, solve, verify

__all__ = ["NGenConfig", "check", "define", "lift", "solve", "triangulate", "verify"]
