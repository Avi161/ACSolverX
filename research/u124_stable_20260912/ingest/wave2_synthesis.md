# Wave 2 coordinator synthesis

Date: 2026-09-12. Computation via `scripts/run_proof_guarded.py --timeout-seconds 60`.

## What was checked

1. Common-suffix peel identities on `Q_{n,δ}` and the Family A prefix analogue
   (`code/q_peel.py`, `tables/q_peel.json`).
2. Whether AC1/AC3 reorientation restores a peelable suffix
   (`code/q_peel_orientations.py`).
3. Whitehead primitivity of every best-table relator and of the cyclic
   products `r1 r2`, `r1 r2⁻¹` (`code/primitive_relator_census.py`).
4. Complete depth-1 AC2 neighbourhood of all 124 best pairs
   (`code/elementary_ac2_scan.py`).

## Claims allowed

- C11 is an elementary identity, 14/14. It is not a U124 solve. Repeating
  the displayed peel does not descend `n`. A second orientation-peel on
  `Q_{2,±1}` reaches `YXyxYYXyx` by ordinary AC and **raises** μ 14→18.
- C12 is a general stable finish line **if** a relator is primitive, citing
  C1. U124 hits: **0/248 relators, 0/248 products**. Closest Whitehead
  minimum is 5, not 1.
- C13: no best-table pair has a cyclic-length-reducing AC2 child. Exact for
  that neighbourhood, not an AC obstruction.
- C14 is an inventory of shared donors (11+11+… rows), a target for a later
  companion theorem, not a reduction.

## Claims forbidden

Do not say U124 is solved, that an `x`-run drop is progress, that n-fold
peel is available, that Aut-min 5 is “almost primitive” in the sense that
makes C12 fire, or that depth-1 failure obstructs longer routes.

## Next legal experiments

1. Independent Sol audit of C11–C12 (`ingest/advisor_wave2.md`).
2. Theory on companions of the shared donors `YXXyxYx` and `YXXXyxYx`
   other than “Aut the donor to a generator”.
3. Bézout against a defining word other than `v = YXX` (that shape is
   absent on Q’s first relator).
4. Cyclic-complement on spellings other than Q / Aut image / Aut-min floor.
5. Keep development rows off holdout when inventing the next recognizer.
