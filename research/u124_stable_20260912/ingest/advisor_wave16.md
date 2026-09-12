# Wave 16 stable-AC legality audit (C31)

Source: ac-advisor `bc-b4bc8abe-6674-5185-a7fd-ae6212fdd001`, 2026-09-12.
Coordinator recorded APPROVE. The k=3 nine-config census was not
re-enumerated.

## BLOCKERS

None.

## WARNINGS

- `independent_checker=false`; same-code replay plus planted control,
  not a second implementation. Status stays IDENTITY-CHECKED NEGATIVE.
- Observed minimum 9 is a census fact for this pool, not a length
  theorem and not a comparative control against C29's minimum 7.
- Tests spot-check identities and stored JSON; they do not independently
  replay the census.
- Not a U124 solve.

## ALLOWED CLAIMS

- C31.1: on the seven consecutive BS rows, unique combo of `y` is
  `(0,-1)`, so `R^+ = C^{-1}` and `S = D`. C29's orientation would be
  wrong on this donor.
- C31.2: nine-config typed Cartesian 1,519,059 products, observed
  min length 9, no hit. Parallel to C15, different donor (`YXXYxxyx`
  vs `YXXXyxYx`).
- C31.3: aca_32 exact L1=2 Cartesian 1,104 products, min length 9,
  no hit.
- Score remains `0/124`. Bounded negative, not a counterexample.

## VERDICT: APPROVE
