# Wave 9 stable-AC legality audit (C24)

Source: ac-advisor `bc-186f02b5-03a5-57b3-8593-fb1c0aa6b3bd`, 2026-09-12.
Coordinator applied the REVISE below. The five-factor / four-factor
censuses were not re-enumerated; annotations and stored `aca_43`
reason were refreshed from the existing JSON.

## BLOCKERS (as filed)

1. “Six length-3 targets” ignored free reduction of rotations.
   Applied: four free-group targets `{ξ, ξ⁻¹, x, x⁻¹}`; extras `x^{±1}`
   are not Gate 1 witnesses.
2. MITM overclaimed as typed conjugate products.
   Applied: `|F|^k` tuples from a globally deduplicated factor-word pool.
3. Counts `1/9/100` looked empirical. Applied: closed
   `N_k = ∑_{r odd} C(k,r) C(r,(r+1)/2) C(k-r,(k-r)/2)`, matched to
   the `n=2..7` enumeration.
4. “Independently replayed” overstated. Applied: same-code
   deterministic replay; planted MITM hit/miss control.
5. `aca_43` `k=4` as “smallest remaining” omitted C22.4’s `k=2`.
   Applied: C22.4 cross-reference.

## WARNINGS

- JSON is produced by the cited program, not a second implementation.
- Extra `x^{±1}` hits would not install `ξ`.
- `k≥7`, longer conjugators, and Gate 2 `k=L1≥6` remain open.
- Not a U124 solve.

## ALLOWED CLAIMS

- C24.1: even `k` is abelian-impossible for Gate 1, all `n≥2`.
- C24.2: no prefix/one-letter 5-tuple from the dedup pool equals `ξ^{±1}`.
- C24.3: Gate 2 L1 even on every `Q'`; four-factor window `δ=−1`, `n=2..5`.
- Score remains `0/124`.

## VERDICT: REVISE (applied)
