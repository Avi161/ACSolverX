# The two-hop MS descent template (proposition, proven for all n)

*2026-07-21, follow-up to the ladder discovery. Full derivation by an opus theory agent, independently machine-checked (76 symbolic-vs-tool checks, 0 mismatches); status labels per project convention.*

## The family and the template

The ten ladder-template classes are the Miller–Schupp family in two sign variants: `P_{n,δ} = ⟨x,y | y⁻¹x⁻³yᵟx², y⁻⁽ⁿ⁺¹⁾x⁻¹yⁿx⟩`, δ = −1: aca_120/34/58/81/97 and δ = +1: aca_121/122/123/85/98 for n = 3..7. The recorded chain `z₁ = xy, z₂ = xⁿ` (the "xᵏ" equals the MS parameter exactly).

## Proposition (PROVEN for all n ≥ 2, both δ)

Applying the gated subword CoVs **z₁ = xy** (isolate x from the MS relator; n_subs = 2) then **z₂ = xⁿ** (isolate x from the transformed first relator; n_subs = 4) sends `P_{n,δ}`, up to relabel, to

`Q_{n,δ} = ⟨x,y | x⁻¹y⁻¹xy·x²·y·xᵟ·y⁻¹x⁻², y⁻¹x²y·xⁿᵟ·y⁻¹x⁻²⟩`

— a CONSTANT (n-free) length-11 first relator plus a single telescoped power block. Mechanism: hop 1's isolation is a conjugation `x = y⁻ⁿ z yⁿ` that inflates x²-runs into xⁿ-runs (uphill: μ 2n+10 → 4n+9); hop 2's isolation `x = y²zyᵟz⁻¹y⁻²` collapses them by the telescoping identity `(y²zyᵟz⁻¹y⁻²)ⁿ = y²zyⁿᵟz⁻¹y⁻²`. Each hop is a gated n_subs ≥ 2 CoV, hence a stable move (Prop A, `MU_CRITERION.md`), so **`P_{n,δ} ~st Q_{n,δ}`** for the trivial-group members. A single fixed automorphism `y ↦ x⁻²y` gives **μ(Q_{n,δ}) ≤ n+12 (PROVEN all n)**; with μ(P) = 2n+10 (CHECKED n = 2..15, exact) the orbit-floor descent is **n − 2** — strict for n ≥ 3, zero at n = 2 (exactly why aca_117 never descended). The descent is invisible to raw length (hop-2 raw length exceeds the input's for n ≤ 7) — it exists only at the orbit-floor level, which is why nothing before the μ-ladder ever saw it.

## The wall (CHECKED, not proven)

The template cannot re-fire (Q is off the MS shape — no lone generator between large power runs), and the floors are robust: exhaustive depth-3 gated-CoV BFS from both n = 3 floor reps (86/104 orbits, defining-relator isolation included) stays at min μ = 15 with **no μ ≤ 13 anywhere, no AK(3) orbit, no trivial orbit**; the beam-32 ladder (~700 orbits/class) agrees for n = 3, 4, 5. The floor orbits have parametric shape (CHECKED n = 3..10): upper `(YXXyxYx, Yⁿ X y² x²)`, lower `(YXyXYxx, Yⁿ X² Y² x)`, μ = n+12 — a constant length-7 relator plus one Aut-protected yⁿ power block, with near-identity abelianization: the classic hard signature. Beam-prune and depth caveats forbid calling n+12 a proven floor.

## What this gives the project

1. Ten of the 124 collapse (stably, with explicit two-hop certificates) onto the one-parameter normal form `Q_{n,δ}` — the family's stable problem is now a SINGLE power-block question, a much cleaner target for theory and for search (the `mu_floors_r8` bench rows are exactly these floors).
2. The uniform template + telescoping identity is the first *structural* (non-enumerative) descent mechanism found in this project; hunting sibling templates on the other 23 descending classes is an obvious next step.
3. Consistency: hop 2 (k = 4 substitutions) descending is the k ≥ 2 length law's z-compression in action — theory and measurement agree.
