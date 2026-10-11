"""n-generator search and the stable-AC (SAC) transform.

* ``triangulate(pres) -> Sac``: define digrams until every relator has length <= 3 (``acx.ngen.sac``).
* ``lift(pres, sac, path, start)``: a solve of the root as elementary stable AC moves on ``pres`` (``acx.ngen.lift``).
* ``solve(pres, NGenConfig)`` and ``verify(pres, result)`` (``acx.ngen.solve``).
"""
from .lift import lift
from .sac import Sac, check, define, triangulate
from .solve import NGenConfig, NGenResult, solve, verify
