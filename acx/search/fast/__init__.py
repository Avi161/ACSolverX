"""The fast (numba) backend: ``run(start, cfg)`` matches ``acx.search.spec`` step for step.

``best_first`` is the engine (the pop loop), with ``arrays`` (state storage), ``heap``, ``dedup`` and ``cap_stats``
(the cap counters). ``kernels`` holds the per-state kernels that other searches (hybrid, CoV, n-generator) call
directly.
"""
from .best_first import run
from .kernels import children, decode, encode
