"""The fast (numba) backend: ``run(start, cfg)`` matches ``acx.search.spec`` step for step.

``best_first`` holds the engine (arena, heap, dedup table; from hcompact);
``kernels`` holds the reusable per-state kernels (``expand``, ``score``,
``encode``/``decode``, and the Python entry ``children``; from hexpand), which
other searches (CoV-then-search, n-generator, hybrid) call directly.
"""
from .best_first import run
from .kernels import LENGTH, S20_MK2, children, decode, encode, expand, score
