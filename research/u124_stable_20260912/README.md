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
   C24: `.../code/c24_even_k.py`.
   C25: `.../code/c25_alt_words.py` (full census) or `--annotate-existing`.
   C26: `.../code/c26_y_exact_l1.py` (full census) or `--annotate-existing`.
   C27: `.../code/c27_archival_k4.py`. C28:
   `.../code/c28_depth2_ac2.py` (re-run under the 60s guard until
   `census_complete`; each invocation resumes for 50s). C29:
   `.../code/c29_yxx_family.py` (full census) or `--annotate-existing`.
   Do not re-run the 1.65M nine-config census. C30:
   `.../code/c30_x_exact_l1.py` (full census) or `--annotate-existing`.
   Do not re-run the MITM cells. C31:
   `.../code/c31_yxxy_family.py` (full census) or `--annotate-existing`.
   Do not re-run the 1.52M nine-config census. C32:
   `.../code/c32_x_exact_l1.py` (full census) or `--annotate-existing`.
   C33: `.../code/c33_len7_donors.py` (full census) or `--annotate-existing`.
   Do not re-run the 1.74M nine-config census. C34:
   `.../code/c34_x_exact_l1.py` (full census) or `--annotate-existing`.
   Do not re-run the MITM cells. C35:
   `.../code/c35_yxxx_family.py` (full census) or `--annotate-existing`.
   Do not re-run the 579,870 nine-config census.
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
   C24: even `k` is an abelian obstruction for Gate 1 (`L1=1`);
   103,765,444,800 five-factor prefix/one-letter products never equal
   `ξ`; Gate 2 on `Q'` has even `L1`, so odd `k` is impossible, and
    four-factor hits only the `δ=−1`, `n=2..5` window (no hit).
    Advisor REVISE applied. C25: `x` is abelian-equivalent to `ξ` on
    `Q'` (nine-config Cartesian 3-factor products miss `x`; `X` by
    inversion); `y` has `L1=|n+2δ|+1`, with `k=1` abelian-legal only
    at `(n,δ)=(2,-1)` and then blocked by `|S|=7`; on C15, `y` and
    `x^{-1}yx` are abelian-equivalent to `B^{-1}` (`L1=1`, `|B|=2m+3`),
    and 2,884,950 products miss the positive one-letter class of `y`.
    A hit would be a normal-closure candidate, not a C12/C22.6 path.
    C26: exact-L1 typed products for `y` on `Q'` in the `2≤L1≤7`
    window: two Cartesian cells miss (observed minima 11 and 13);
    six MITM cells miss. C27: archival initial depth-1 AC2 misses
    (36 μ-floor spellings included); `k=4` extra-pair products for
    `y` on `Q'_{3,-1}` miss (5,128,200 products, observed min length
    11). Advisor APPROVE. C28: depth ≤ 2 ordinary AC2 misses on all
    124 archival initial rows (36 μ-floor spellings included; 19,066,394
    unique grandchildren, 0 length drops) and on parametric P/Q/Family A
    (36 pairs). Advisor REVISE applied. C29: `YXXyxYx` family `y ≡ D^{-1}`
    (`L1=1`); k=3 nine-config misses (`1,650,843` products, observed
    min length 7, no hit). Advisor APPROVE. C30: exact-L1 for defining word `x` on the
    same eleven rows misses (`107,212` Cartesian products, observed
    minima 11 and 15; eight MITM cells, typed search-space
    `43,999,380,138`, not enumerated products). Advisor REVISE applied.
    C31: `YXXYxxyx` family,
    seven consecutive BS companions with `y ≡ C^{-1}` (`L1=1`); k=3
    nine-config misses (`1,519,059` products, observed min length 9);
    aca_32 exact L1=2 misses (1,104 products). Advisor APPROVE. C32:
    exact-L1 for defining word `x` on those eight rows misses (`51,412`
    Cartesian products, observed min length 11). Advisor REVISE applied.
    C33: remaining length-7 donors `YXyXYxx` and `YYXXyxx` (`y ≡ D^{-1}`,
    `L1=1`); k=3 nine-config misses (`1,737,522` products, observed min
    length 7). Advisor APPROVE. C34: exact-L1 for defining word `x` on
    eight C33 rows in `2≤L1≤7` misses (`59,884` Cartesian products,
    observed min length 9; four MITM cells, typed search-space
    `69,587,713,197`, not enumerated products). Advisor APPROVE.
    C35: last unused length-7 donor in the listed shared-donor
    inventory, `YXXXyxx` (`x ≡ D^{-1}`, `L1=1`); k=3 nine-config
    misses (`579,870` products, observed min length 7). Plan advisor
    REVISE applied. Still 0/124.

## File ownership

| path | owner |
|---|---|
| `README.md`, `RECONSTRUCTION.md`, `THEOREM_CATALOGUE.md`, `tables/` | coordinator |
| `code/u124_census.py`, `code/ms_template_identities.py`, `code/jsonl_atomic.py`, `code/q_peel.py`, `code/primitive_relator_census.py`, `code/elementary_ac2_scan.py`, `code/wave2_structural.py`, `code/q_peel_orientations.py`, `code/shared_donor_families.py`, `code/c12_generator_deletion.py`, `code/primitive_aggregates.py`, `code/wave3_structural.py`, `code/c15_divisibility_scan.py`, `code/theory_wave1_replay.py`, `code/c16_escape_scan.py`, `code/c19_continuation.py`, `code/c20_roundtrip.py`, `code/c21_depth2.py`, `code/c22_gate_witness.py`, `code/c23_three_factor.py`, `code/c24_even_k.py`, `code/c25_alt_words.py`, `code/c26_y_exact_l1.py`, `code/c27_archival_k4.py`, `code/c28_depth2_ac2.py`, `code/c29_yxx_family.py`, `code/c30_x_exact_l1.py`, `code/c31_yxxy_family.py`, `code/c32_x_exact_l1.py`, `code/c33_len7_donors.py`, `code/c34_x_exact_l1.py`, `code/c35_yxxx_family.py` | coordinator / Terra |
| `ingest/advisor_*.md` | Sol advisor |
| `ingest/theory_*.md` | theory agent |
| `ingest/proofs_machinery.md` | proofs-extract agent |
| `ingest/leftover_pipeline.md` | leftover-extract agent |
| `certs/` | certificate compilers only; atomic JSONL |

## Computation policy

No heap search above 1,000 charged units per presentation in this environment.
Structural/symbolic checks first. Development rows stay off the frozen holdout
panel recorded in `tables/panels.json`.
