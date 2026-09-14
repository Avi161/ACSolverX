# Retained-donor central pinches — PASS

Write D = z⁻¹wᵏ with w = hᵈzᵃ. In the free group,

    D w D⁻¹ w⁻¹ = z⁻¹ w z w⁻¹ = z⁻¹ hᵈ z h⁻ᵈ.

The exponent k cancels by free reduction; no quotient inference replaces the donor. The implementation represents the first D in its exact signed cyclic frame and represents w D⁻¹ w⁻¹ with the corresponding composed conjugator. The original donor remains an unchanged nontarget row.

Put B=hᵈ and C=z⁻¹BzB⁻¹. For the pinch L=z⁻¹Bz, the right correction is B⁻¹C⁻¹B=L⁻¹B. For L=zBz⁻¹, conjugating C by z⁻¹B gives L⁻¹B. The existing signed-power correction transports either identity to all integer multiples of d. For a wrapping target, the final correction is conjugated by suffix·frame⁻¹; this restores the original target frame exactly. Normalization preserves every nontarget row and its donor index.

`verification_central_checks.py` checks eight signed rank-four examples with generator labels up to 10²⁵. Six need nontrivial circular frame restoration. Every consequence and emitted right-product identity is checked independently, every endpoint retains all four relators, and every wrong donor-sign mutation is rejected. These events pass `known_trivial=False`: they are ordinary relator products. Five budget controls also pass. Public `probe` normalizes its input, so the internal donor-index remapping uses unchanged canonical nontarget donors; arbitrary unnormalized direct calls to internal helpers are outside that invariant.

The composed wrapper first takes saved valid conjugate-exchange prefixes, including longer intermediates, and applies this ordinary rule with its remaining shared allowance. Its accepted Whitehead and peeling suffixes remain separate certified events. All 33 saved `central_exchange_all33.json` records replay with their inherited stable lineage and add no new gain beyond imported seeds. The new probe costs remain separate from historical seed discovery work. Results and hashes are in `verification_central.json`; no census search was rerun.
