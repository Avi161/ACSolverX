# `results/equivalence_classes/`

Outputs of the AC-equivalence analysis of the 261 "unsolved" Miller–Schupp representatives.
The findings themselves live in [`../greedy_baseline/EQUIVALENCE_FINDING.md`](../greedy_baseline/EQUIVALENCE_FINDING.md);
this directory is the evidence behind them.

## What is here

| file | contents |
|---|---|
| `sweep_<moves>_<max_total>_<budget>[_ms][_j].json` | one sweep: config, stats, the resulting classes, and **a replayable certificate for every merge** (the Definition 2.1 move list plus the explicit automorphism applied at each step) |
| `classes_<stem>.csv` | the deliverable: one row per distinct problem, with the `Aut`-minimal presentation to actually run |
| `run_*.log` | the run logs, including throughput |

Naming: `moves` is `seam` (the baseline's cancelling-seam move set) or `full` (every `(k1,k2)`);
`max_total` is the cap on **`Aut`-minimal** total length; `budget` is nodes per source. `_ms`
means the 550 raw Miller–Schupp presentations were seeded as bridge sources; `_j` means the 783
states the 1M-node sweep recorded were seeded too.

## Reproducing / checking

```bash
# re-run a sweep (CPU only, single core, no numba warm-up beyond the first call)
.venv/bin/python3 experiments/equivalence_classes/run_sweep.py 26 30 seam

# CHECK IT. This is the gate: it re-derives every merge from data/ by pure substitution,
# shares none of the search's inference, and exits non-zero on any failure.
.venv/bin/python3 experiments/equivalence_classes/verify_certificates.py \
    results/equivalence_classes/sweep_seam_26_30.json

# format the verified result
.venv/bin/python3 experiments/equivalence_classes/make_class_table.py \
    results/equivalence_classes/sweep_seam_26_30.json
```

**No number from a sweep goes into the write-up until `verify_certificates.py` exits 0 on that
exact JSON.**

## How to read a merge

Each entry in `merges` is one of:

- `aut` — the two roots are `Aut(F₂)`-equivalent (a change of variables relates them). No search
  was involved; this is decided exactly by Whitehead's algorithm.
- `aca` — a path was found. `path_a` and `path_b` each go from a root's `Aut`-minimal form to a
  shared `Aut`-class. A step is `[move, phi, rep]`: apply the Definition 2.1 move
  `(target, jsign, k1, k2)`, then the automorphism `phi`, canonicalise, and you land on `rep`.

Both kinds prove the same thing — **the two presentations are the same problem**: one is
AC-trivial if and only if the other is, so solving either settles both. **Neither kind claims a
path of AC moves joins the two presentations.** That is a strictly stronger statement and it is
not made here.

`pre_union` (only in `_j` sweeps) lists states the 1M-node sweep *recorded* for a given root.
These are AC-reachable from that root by construction — `min_relator` / `max_relator` are by
definition states `expand_node_nj` emitted from it — but the sweep stored the state and not the
path, so they are not replayable. The verifier checks their **provenance** (the state really is
that row's field in the jsonl); the reachability rests on the solver's semantics.

## Counts are upper bounds

The search is sound and incomplete: a length cap or a node budget removes edges, never adds them.
**Every merge found is a proof; no merge found proves nothing.** More budget, a higher cap, or the
enlarged move set can only merge further.
