# [2026-07-08] numba split that works [WORKS]
`@njit` on the per-move math (neighbours, reduction, Booth canonicalisation, primitives); plain Python for the `heapq`/`dict` search orchestration (numba can't JIT those). Verified real: functions are `numba.core.registry.CPUDispatcher`, first call ~3s JIT then ~1e-4s (≈30000×). First ~10 presentations look slow purely from one-time JIT compile.
