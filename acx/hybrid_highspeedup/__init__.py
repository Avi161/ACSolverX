"""Compiled fast paths of the hybrid search (backend ``"fast"``), kept apart from the reference code they replace.

* ``dynkernels``: ``acx.hybrid.dynrank``'s higher-rank moves in numba (``dynrank.backend("fast")``);
* ``r2kernels``: the rank-two orbit and child layout the search pushes (``acx.hybrid.frontier.orbits`` and ``grouped``).

Each gives what the pure-Python form gives, in the same order, so a run's records do not depend on the backend
(``tests/test_hybrid.py`` checks the moves and the full pop order of both). ``backend = "spec"`` runs without them.
"""
