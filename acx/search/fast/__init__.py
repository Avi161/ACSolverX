"""The fast (numba) backend: ``run(start, cfg)`` matches ``acx.search.spec`` step for step; ``kernels`` holds the
per-state kernels other searches call directly."""
from .best_first import run
from .kernels import children, decode, encode
