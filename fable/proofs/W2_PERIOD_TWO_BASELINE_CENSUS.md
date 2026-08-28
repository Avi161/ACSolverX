# W2: the period-two witness is not the only quotient baseline

Date: 2026-08-28 · Checkers: `checkers/period_two_solution_census.py`
(generator), `checkers/period_two_census_verify.py` (independent
cyclic-form replay; different formulation), fixture
`checkers/period_two_census_chains.json` · Guarded runs, complete for the
stated caps.

## Statement

In `Q = <c,t | c^2> = C2 * Z`, with the fixed source rows
`A = t^-2ct^-2ct^2c`, `B = t^-3ctctc`, consider the period-two image of the
hardest depth-four recurrence:

```text
R = A h0 B^-1 h0^-1,  S = B h1 R^-1 h1^-1,
U = R h2 S^-1 h2^-1,  Z = U^-1 h3 S h3^-1,   solution iff Z in Cl_Q(t),
```

with `h0..h3` ranging over ALL of `Q` (both parities). The gauge — right
multiplication of each `h_i` by the (twisted) centralizer of the element it
conjugates — is fully absorbed by recording the chain `(R, S, U)`; distinct
chains are essentially distinct quotient solutions.

**Census result (complete for its caps).** With
`len(R), len(S), len(U) <= 12` and final conjugator `len(g) <= 5`:

- exactly **17 essential chains** solve the full system;
- the codex witness chain `(TTctcTctc, TTTcttcTctt, TTcttcTc)` is among
  them (positive control — falsifiable, and found);
- **16 chains are NOT the witness**;
- every chain has hyperbolic `S` (0 elliptic hits — consistent with the
  proved elliptic obstruction, a genuine cross-check);
- pre-terminal dynamic range: 3 admissible `R` values, 8 `(R,S)` pairs,
  24 chains before the terminal filter (the control-can-move check);
- all 17 chains re-verify under an independent replay that uses only
  conjugacy-class normal-form equalities (`ALL 17 CHAINS VERIFY`).

Ten of the 17 share the witness's `R`; the 17 sort into 3 R-classes —
the first equation is rigid at this scale, the multiplicity lives in the
`S, U` freedom.

## Why this matters for the codex tower

The anchored lift family of
`AK3_DEPTH4_PERIOD_TWO_FULL_LIFT_BOUNDARY.md` (eq. 1.6–1.10) corrects the
witness's conjugators by elements of `N` and `[N,N]`, so EVERY member of
that family reduces in `Q` to the witness's baseline. Each of the 16 other
chains therefore generates a lift family disjoint from (1.10). A completed
universal noncancellation theorem over (1.10) would close the witness's
family only. Closing the depth-four signature through the period-two route
additionally requires, for each other baseline: (i) a layer-1
(relation-module) obstruction — a dead baseline needs no tower — or
(ii) inclusion in a uniform argument. Which of the 16 are live at layer 1
is the immediate next question (W2b), not answered here.

## Scope and nonclaims

- The caps are a **ceiling, not a budget**: raising them can only add
  chains. 17 is a lower bound on the essential solution count; nothing here
  suggests the set is finite.
- The terminal search bound (`g <= 5` in the generator, re-verified at
  `<= 6`) can only under-count; found chains are constructive and exact.
- No claim about the free-group depth-four class, the bridge, AK(3),
  stable AC, or AC. This is a scope-quantification of one quotient layer
  of one signature.
- The census space is `Cl_Q` (both conjugator parities); if the codex
  analysis elsewhere proves solutions must have even-parity conjugators,
  the count may reduce — that hypothesis is not proved in the documents
  read here (flagged by the advisor review as well).

## Replay

```bash
python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- \
  python3 fable/proofs/checkers/period_two_solution_census.py
python3 scripts/run_proof_guarded.py --timeout-seconds 60 -- \
  python3 fable/proofs/checkers/period_two_census_verify.py
```

## W2c addendum: cap growth curve

Rerunning the census at higher caps (GPAD fixed at 5):

| CAP | admissible R | (R,S) pairs' S-total | chains |
|---:|---:|---:|---:|
| 12 | 3 | 8 | **17** |
| 13 | 7 | 25 | **36** |
| 14 | 7 | 25 | **55** |
| 15 | 14 | 70 | **67** |

The essential-chain count grows strictly with the cap and shows no
plateau; the witness is re-found at every cap, elliptic-S hits stay zero.
Together with W2b (live fraction 6/17 at cap 12), the working conclusion
is that the period-two quotient layer carries an unboundedly growing —
plausibly infinite — family of essential baselines, a nontrivial fraction
of them live at layer 1. A per-baseline tower cannot terminate; closing
the signature through this quotient requires a uniform argument over all
baselines (or a different quotient). Caps are ceilings: every number is a
lower bound.
