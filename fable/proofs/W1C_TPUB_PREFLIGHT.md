# W1c: bounded greedy preflight on the bridge triples

Date: 2026-08-28 · Checker: `checkers/tpub_greedy_preflight.py` (imports
`experiments/stable_ac/solvern.py` unmodified) · Budget: 1,000 nodes (repo
hard cap for locally launched searches) · cap 64 · guarded run.

## Results

| triple | solved | nodes | path | min total length reached |
|---|---|---:|---:|---:|
| `Txy = (A,B,zYX)` (control) | **yes** | 12 | 11 macros | 3 |
| `Tpub = (A,B,Xyz)` (target) | no | 1,000 | — | **14** (from 29) |

- The control reproduces the certified trivialization: the found 11-macro
  path opens with the same macro `(2,1,-1,3,0)` as the certified 134-move
  path in `.scratch/mms02_u_xy_bridge.md`. Pipeline validated end to end.
- The target is not solved at the local cap, but greedy descends from total
  29 to total 14 within 1,000 nodes. Whether 14 is a hump floor or a
  waypoint is exactly what a production budget decides.

## Production handoff (user-run, Colab)

A solve of `Tpub` at ANY budget proves the bridge
`(A,B,zYX) ~AC (A,B,Xyz)` and therefore **AK(3) stably AC-trivial** through
the MMS02 corridor (promise-ledger route 1). Recommended production
configuration:

```python
from experiments.stable_ac.solvern import Pres, search_n, str_to_word
A = "xzYXyxZXYxyZ"; B = "XyxZXYXyxzXYxy"
rels = tuple(tuple(int(g) for g in str_to_word(s)) for s in (A, B, "Xyz"))
stats = search_n(Pres(3, rels), budget=5_000_000, cap=100)
```

- budget 5e6 first (RAM per the repo's measured-memory law: states ≈
  82.9·b^0.981 × ~214 B ⇒ ~90 GB at 5e6 with the rank-2 constant — the
  rank-3 constant is untested; start at 1e6 and watch RSS), cap sweep
  {64, 100} — never lower the cap to buy speed (repo lesson).
- If solved: `stats["path_moves"]` is the bridge certificate; replay and
  commit it, then the AK(3) stable-triviality writeup follows the corridor
  in `.scratch/mms02_u_xy_bridge.md` + `literature/proofs/AK3_RANK3_COMPRESSION.md`.

## Scope and nonclaims

An unsolved budget is never counterexample evidence (repo rule). This note
makes no bridge, AK(3), stable AC, or AC claim; it validates the pipeline
and sizes the production attempt.
