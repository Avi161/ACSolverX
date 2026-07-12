# `results/equivalence_classes/`

Outputs of the AC-equivalence analysis of the 261 "unsolved" Miller–Schupp representatives.
The findings themselves live in [`../greedy_baseline/EQUIVALENCE_FINDING.md`](../greedy_baseline/EQUIVALENCE_FINDING.md);
this directory is the evidence behind them.

## What is here

| file | contents |
|---|---|
| **`PROOFS.md`** | **the proof book** — all 126 classes, derived step by step and **checkable with a pencil**: every substitution, inversion, rotation and concatenation is written out as its own line, so nothing has to be taken on faith |
| **`certificates.json`** | the same, machine-readable and **self-contained**: it needs neither a sweep nor the search to be checked |
| `sweep_<moves>_<max_total>_<budget>[_ms][_j].json` | one sweep: config, stats, the resulting classes, and a replayable certificate for every merge, in the search's own idiom |
| `classes_<stem>.csv` | the deliverable: one row per distinct problem, with the `Aut`-minimal presentation to actually run |
| `merges_<stem>.csv` | the merge list: `kind`, both `pres_id`s, the number of AC moves on each side |
| `run_*.log` | the run logs, including throughput |

Naming: `moves` is `seam` (the baseline's cancelling-seam move set) or `full` (every `(k1,k2)`);
`max_total` is the cap on **`Aut`-minimal** total length; `budget` is nodes per source. `_ms`
means the 550 raw Miller–Schupp presentations were seeded as bridge sources; `_j` means the 783
states the 1M-node sweep recorded were seeded too.

## The verification pipeline

To check the shipped result — all 126 classes, from the raw data, sharing no inference with the
search that produced it:

```bash
.venv/bin/python3 experiments/equivalence_classes/verify_proofs.py
```

It reads `certificates.json` and `data/ms_unsolved_reps/ms_reps_unsolved.csv` and **nothing else**.
For every edge it re-reads both presentations from the CSV *by row number* (so a wrong `pres_id`
carrying the right words is caught, and the reverse), replays every Definition 2.1 move by string
substitution, re-proves every change of variables is an automorphism of F₂ by Nielsen reduction,
and requires both sides to land on the recorded meeting state. Then it rebuilds the partition from
the verified edges alone and requires it to equal the 126 reported classes — because verifying every
edge is a *different claim* from verifying the count, and an over-merge would pass the first while
failing the second. Exits non-zero on any failure.

The checker is itself mutation-tested: `test_equivalence.py` tampers with the certificates seven
ways and requires each to be rejected.

## Reproducing from scratch

```bash
# 1. re-run a sweep (CPU only, single core)
.venv/bin/python3 experiments/equivalence_classes/run_sweep.py 26 30 seam

# 2. CHECK IT. Re-derives every merge from data/ by pure substitution, exits non-zero on failure.
.venv/bin/python3 experiments/equivalence_classes/verify_certificates.py \
    results/equivalence_classes/sweep_seam_26_30.json

# 3. flatten the verified sweep into the proof book, then check THAT independently
.venv/bin/python3 experiments/equivalence_classes/make_proof_book.py \
    results/equivalence_classes/sweep_seam_26_30.json
.venv/bin/python3 experiments/equivalence_classes/verify_proofs.py

# 4. format the verified result
.venv/bin/python3 experiments/equivalence_classes/make_class_table.py \
    results/equivalence_classes/sweep_seam_26_30.json
```

**No number from a sweep goes into the write-up until `verify_certificates.py` exits 0 on that
exact JSON.**

## How to read a merge

**The trap.** Every presentation is printed in **canonical form**, and canonicalising freely reduces
each relator, may invert it, rotates it to its lex-least form, and may swap the two relators. So
substituting `y → Y` into a relator does **not** hand you the target string literally — you must
still invert and rotate. That is bookkeeping, not mathematics (inverting a relator restates `r = 1`
as `r⁻¹ = 1`; rotating it is conjugation, `vu = u⁻¹(uv)u`; both are AC moves), but it is invisible
unless written down. `PROOFS.md` writes it down for every step, and `verify_proofs.py` replays each
printed step literally rather than just checking the endpoints.

In `certificates.json` / `PROOFS.md` each edge is one of:

- `cv` — **a change of variables and nothing else** (93 of 135). One substitution `psi` with
  `canon(psi(A)) == canon(B)`: B *is* A with new words substituted for the generators. Checkable by
  hand in one line.
- `ac` — **AC moves were needed** (42 of 135). Both roots are driven by Definition 2.1 moves to a
  common `Aut`-class. A step is `move` → `after_move` → `phi` → `state`: apply the move
  `(target, jsign, k1, k2)`, then the automorphism `phi`, canonicalise, land on `state`.
  On **6** of them every step's `phi` is the identity, so the path is AC moves and nothing else;
  those are flagged `pure_ac_path` and give `A ~AC psi(B)` — an AC path to a *relabelled* B.

In the raw sweep JSON the same two are named `aut` and `aca`.

Both kinds prove the same core thing — **the two presentations are the same problem**: one is
AC-trivial if and only if the other is, so solving either settles both. Except for the 6 noted above,
**neither kind claims a path of AC moves joins the two presentations.** That is a strictly stronger
statement and it is not made here. And even those 6 join `A` to `psi(B)`, never to `B` itself:
`psi` is not the identity on any of them.

`pre_union` (only in `_j` sweeps) lists states the 1M-node sweep *recorded* for a given root.
These are AC-reachable from that root by construction — `min_relator` / `max_relator` are by
definition states `expand_node_nj` emitted from it — but the sweep stored the state and not the
path, so they are not replayable. The verifier checks their **provenance** (the state really is
that row's field in the jsonl); the reachability rests on the solver's semantics.

## Counts are upper bounds

The search is sound and incomplete: a length cap or a node budget removes edges, never adds them.
**Every merge found is a proof; no merge found proves nothing.** More budget, a higher cap, or the
enlarged move set can only merge further.
