# U124 stable Andrews–Curtis campaign (2026-09-12)

Living campaign to prove **constructive stable-AC triviality** for as many of
the 124 retained unresolved Miller–Schupp ACA components as possible.

This directory is the resume surface. Another agent should start here.

## Objective (do not shrink)

Prove rigorous stable-AC trivializations of the U124 presentations, preferably
by **infinite-family theorems**. Elementary moves are only:

- AC1 invert a relator
- AC2 multiply one relator by another
- AC3 conjugate a relator
- AC4/AC5 stabilize/destabilize by a generator–relator pair

Ambient automorphisms are allowed only when their **stable realization** is
cited or constructed. A quotient equality, Tietze transformation, or silent
substitution is not a certificate.

## Authoritative inputs (hashed this campaign)

Copied onto `codex/proofs` from `claude/ac19-theorem-strength-8v1wp6`:

| file | sha256 (prefix) | role |
|---|---|---|
| `data/ms_unsolved_reps/aca_124_initial.csv` | `614bce2d3250a1acca81ec9de0fc0deb` | archival starts; **identical** to `aca_124.csv` on this branch |
| `data/ms_unsolved_reps/aca_124_best.csv` | `8df25b3fc585553f80886934707b147c` | 36 μ-floor substitutions applied; total length 2446 → 2356 |
| `data/ms_unsolved_reps/aca_124_reduced.csv` | `5be80a918b2b970e9bba7557a168908d` | ledger for those 36 |
| `data/ms_unsolved_reps/README_aca_124.md` | `8458cac9bef803d99d78f4fb4cb59644` | schema and caveats |

U124 is an **upper bound** from bounded equivalence search, not 124 proven
distinct exact AC classes. The 124 `n_members` sum to 261 Aut-minimal reps of
550 unsolved MS cells.

## Missing sources (do not invent them)

- Branch `codex/theory-patterns-3h` and directory `research/theory_patterns_20260912/` **are not on origin**.
- Named supermoves notes (`FINAL_START_HERE.md`, `SHORTCUT_CATALOGUE.md`,
  `bs_theorems.md`, `ONE_SIDED_MAGNUS.md`, `AXIS_FACTOR_THEOREM.md`, …) **are
  not in git**. Closest audit:
  `research/residual_20260909/THEOREMS_PROOFS_AND_FREQUENCY.md` on
  `claude/ac19-theorem-strength-8v1wp6`.
- `literature/proofs/PROOFS.tex` is **cited everywhere and absent** from every
  fetched branch. Lemma 11 is reconstructed from
  `results/equivalence_classes/LEMMA_11_AND_THE_126_CLASSES.md` and
  arXiv:2408.15332.

Worktrees for study (read-only): `/tmp/acx-worktrees/{proofs,theorem,leftover,fable}`.

## How to resume

1. Read `RECONSTRUCTION.md`, `THEOREM_CATALOGUE.md`, `tables/u124_status.csv`.
2. Re-run `python3 research/u124_stable_20260912/code/u124_census.py` from repo root.
3. Re-run `python3 research/u124_stable_20260912/code/ms_template_identities.py`.
4. Wave 2 (guarded, 60 s): `python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- python3 research/u124_stable_20260912/code/wave2_structural.py`
   and `.../code/q_peel_orientations.py`.
   Wave 3: `.../code/wave3_structural.py` (C12 step-4 replay + primitive aggregates).
   Theory wave 1 (C16–C18): `.../code/theory_wave1_replay.py`.
   C16 escapes / C19: `.../code/c16_escape_scan.py`.
   C19 continuation / C20: `.../code/c19_continuation.py` and
   `.../code/c20_roundtrip.py`.
   C21: `.../code/c21_depth2.py`.
   C22: `.../code/c22_gate_witness.py`.
   C23: `.../code/c23_three_factor.py`.
5. Treat only independently replayed certificates as progress.
6. Advisor reviews live in `ingest/advisor_*.md`. Theory drafts live in
   `ingest/theory_*.md` until they pass independent replay. Catalogue C16–C18
   is coordinator-replayed in `code/theory_wave1_replay.py`. C19 is an
   elementary length-3 drop on the δ=−1 C16 endpoint; C20 shows that
   a Britton preflight after depth-1 AC2 on that pair returns `D` or
   `D^{-1}` (not an AC move, not C5 progress). C21: depth-2 from the
   ten no-pinch children never beats C19 length; C16 Gate 2 is not
   bare AC5. C22: Gate 1 cannot be a product of one or two conjugates
   of the Q' relators (`ξ ≡ R^δ`, length 7 vs 3); the C16 isolator
   template is a C6 corridor whose output is not C16; C15’s free
   bridge to `P_{m,+1}` is not a depth-1 AC2. C23: no three-factor
   prefix/one-letter conjugate product equals `ξ` (min length 7 on
   1,529,400 products); after AC4, F3 depth-2 never produces `D`.
   Still 0/124.

## File ownership

| path | owner |
|---|---|
| `README.md`, `RECONSTRUCTION.md`, `THEOREM_CATALOGUE.md`, `tables/` | coordinator |
| `code/u124_census.py`, `code/ms_template_identities.py`, `code/jsonl_atomic.py`, `code/q_peel.py`, `code/primitive_relator_census.py`, `code/elementary_ac2_scan.py`, `code/wave2_structural.py`, `code/q_peel_orientations.py`, `code/shared_donor_families.py`, `code/c12_generator_deletion.py`, `code/primitive_aggregates.py`, `code/wave3_structural.py`, `code/c15_divisibility_scan.py`, `code/theory_wave1_replay.py`, `code/c16_escape_scan.py`, `code/c19_continuation.py`, `code/c20_roundtrip.py`, `code/c21_depth2.py`, `code/c22_gate_witness.py`, `code/c23_three_factor.py` | coordinator / Terra |
| `ingest/advisor_*.md` | Sol advisor |
| `ingest/theory_*.md` | theory agent |
| `ingest/proofs_machinery.md` | proofs-extract agent |
| `ingest/leftover_pipeline.md` | leftover-extract agent |
| `certs/` | certificate compilers only; atomic JSONL |

## Computation policy

No heap search above 1,000 charged units per presentation in this environment.
Structural/symbolic checks first. Development rows stay off the frozen holdout
panel recorded in `tables/panels.json`.
