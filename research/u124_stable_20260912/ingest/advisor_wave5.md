# Wave 5 stable-AC legality audit (C20)

Source: ac-advisor `bc-f62c048a-129e-50ef-b4e2-4f2955f8589c`, 2026-09-12.
Coordinator applied the REVISE below.

## BLOCKERS

1. **The pinch is not an AC move.** Calling the rewrite an “AC2 round
   trip” overstates legality. The identities are equality modulo `B`
   (BS/Britton preflight). They do not expand into AC1–AC5 and are not
   a certificate.
2. **Neighbourhood claims were scoped too broadly.** Full-neighbourhood
   counts are computational for `n=2..7`, not a theorem for all `n≥2`.
   The first implementation stopped after the first pinching slot and
   first valid occurrence, and uniqueness was `canon_pair` before other
   representatives were examined.
3. **“The ten no-pinch children lengthen `B`” was not serialized.**
   Keep-`D` is the machine-checked fact; lengths must be in the JSON.
4. **C12 needs both relators.** `D` having Whitehead minimum 7 is not
   enough by itself; `B_n` must also be non-primitive.

## WARNINGS

- Bounded negatives are not obstructions to depth ≥ 2, other donors,
  or raw pre-`canon_pair` spellings.
- Incoming C16 still has two non-effective C0 uses. C19 remains no
  U124-row shortening (`ingest/advisor_wave4.md`).
- The JSON is produced by the same program cited for the identities.
  Displayed four-product cancellations are hand-auditable; the finite
  neighbourhood counts are not an independent second implementation.

## ALLOWED CLAIMS

- **Yes:** the four displayed products, for the listed `B_n`, rewrite
  by one associated-subgroup pinch to cyclic `D` or `D⁻¹`. Uniform in
  `n≥2` by free cancellation.
- **Yes, after rescoping:** for `n=2..7`, every valid pinch occurrence
  on both rows of every `canon_pair`-unique depth-1 AC2 child rewrites
  to cyclic `D`/`D⁻¹`/`B`/`B⁻¹` or empty, with empty only on the `B`
  slot.
- **No:** C20 is not a U124 solve, best-table shortening, C5 finish,
  or general Britton obstruction.
- **Yes:** for `n=2..7`, Whitehead minima are 7 for `D` and `2n+3` for
  `B_n`; C12 does not fire on this pair.

## VERDICT: REVISE (applied)

Required wording is now in `THEOREM_CATALOGUE.md` C20. The replay
checks every valid occurrence, serializes the ten no-pinch children
with lengths, and records both Whitehead minima.
