# `clustering/` — unsupervised structure of the minimal automorphic states

> **📊 Full write-up, every table and chart:** <https://claude.ai/code/artifact/b9e07614-f290-44cd-807c-2d02e327ec98>

Takes the 113 solved Aut(F₂)-orbit reps + 124 unsolved ACA-class reps of the Miller–Schupp benchmark and asks whether **unsupervised** clustering of their shape recovers the solved / unsolved split without being shown it. It does, well beyond a permutation null.

| file | role |
|---|---|
| `features.py` | 17 rotation-invariant representations, incl. the training-free analogue of the Two-Hump paper's Dual-Ring Transformer (circular autocorrelation). Rotation-invariance is a **hard gate**, not an assumption. |
| `sweep.py` | hand-rolled KMeans / Ward / spectral / DBSCAN + ARI, NMI, balanced accuracy (no sklearn — this branch stays dependency-light). |
| `run_cluster_237.py` | the main sweep, with the permutation null over the whole grid and the provenance-matched control population. |
| `signed_knots.py` | signed block decomposition `(generator, length, exponent sum)`. |
| `within_bucket.py` | per-knot-bucket analysis with a length control. |
| `rank_signals.py` | every candidate statistic on one footing — both populations, raw / length-removed / matched-band AUC. |
| `holdout_eval.py` | 70/30 stratified splits over 200 seeds; refit on train, score on the untouched test. |

Outputs: [`results/clustering/`](../../results/clustering/README.md). Tests: `pytest tests/clustering -q --runslow`.

**Two rules this package exists to enforce.** Every representation must be rotation-invariant — a relator is a ring, and a feature that can see where the canonicaliser cut it is measuring the tie-break, not the mathematics. And every result carries a **provenance-matched control**: the 124 unsolved reps are local minima of an upstream bounded AC reduction, so a raw comparison against the 113 partly measures how each side was produced, not what it is.

The search heuristic built on these features: [`../heuristic_search/`](../heuristic_search/README.md).
