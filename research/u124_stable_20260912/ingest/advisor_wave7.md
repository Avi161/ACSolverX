# Wave 7 stable-AC legality audit (C22)

Source: ac-advisor `bc-3c3c989b-1e77-515f-8c68-943f2c2f5677`, 2026-09-12.
Coordinator applied the REVISE below, then added the omitted `(n,δ)=(3,+1)`
search so C22.3’s four-case set is actually enumerated.

## BLOCKERS (as filed)

1. C22.2 used `|D|=5` and `1+|S| ≥ 7`. Applied: `D = UYxy` has length 4;
   `1+|S| = n+6 ≥ 8`.
2. C22.3 claimed `{2,3}×{±1}` while JSON omitted `(3,+1)`. Applied: that
   case is now in the replay.
3. “Exhaustive two-factor conjugates” overstated the conjugator set.
   Applied: prefix- or one-letter conjugators only, including stored hits.
4. “2440 unique depth-1 children” omitted that these are source-row-local
   `canon_pair` classes from 4160 raw cyclic-AC2 candidates. Applied.

## WARNINGS

- Extra searches are capped (800 states, four factors, conjugator length
  two) and are not obstructions to longer products or to conjugators
  involving the new letter `u`.
- C22.5 is the twelve tested `Q'_{n,δ}`, not a theorem for all `n≥2`.
- The JSON is produced by the cited program, not a second implementation.
- Still two C0 uses on any C16/C6 route. Not a U124 solve.

## ALLOWED CLAIMS

- C22.1 is uniform in `n≥2`: no two-factor abelian combination of
  `{R^{±1},S^{±1}}` equals `ξ`; one conjugate of `R^δ` has length at
  least 7.
- C22.2’s depth-1 restore miss holds with the corrected lengths.
- C22.4 unimodularity and the literal power-product check for `n=2..7`.
- C22.5 hypotheses and the C22.6 free identity.
- Score remains `0/124`.

## VERDICT: REVISE (applied)
