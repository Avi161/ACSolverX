# The germ count is the criterion — "it only re-describes the relators" is NOT

**Filed 2026-08-04, S-line (`claude/stable-ac-conjecture-stabilization-rwo9as`).**
**REVISED the same session, after this file's own headline was refuted.** The revision is
the lesson; the original framing is kept in §4 so the error stays legible.

## 1. What is actually true

Two ways of spending extra generators are settled:

- **Chord refinement / triangulation is a CW subdivision.** The new 1-cell is a chord drawn
  *inside* an existing 2-cell, so `|K_{P'}| ≅ |K_P|`: not only is the γ_N = 0 predicate
  preserved, the **entire defect histogram is bit-identical** (1,525 triangulations, zero
  deviations; AK(3) sits at `minimum_defect` 4 at rank 2 *and* at rank 9, with the same
  census size 86,400, because a peel never changes an original germ's degree). Audited.
- **Generator splitting (a length-2 bigon definition `uG`) is monotone.** `link(P)` is a
  **minor** of `link(P')` — contract the bigon's two link edges, which are `u⁻—g⁻` and
  `u⁺—g⁺` and are never loops and always vertex-disjoint — so γ_N cannot fall. 1,600+
  splits, none below base. The bookkeeping gap closed under audit and the sketch is now a
  proof.

The property both share is **the germ count**: a new edge carrying exactly **two 2-cell
germs from two distinct 2-cells** is a chord, and two discs glued along one boundary arc
form a disc.

> **Before proposing any high-rank mechanism, state how many 2-cell germs its new edges
> carry.** Exactly two, from two distinct 2-cells ⇒ provably inert. Three or more ⇒ the
> space genuinely changes and anything may happen.

## 2. What is FALSE, and cost this line a wrong lesson

The original version of this file generalised the above into:

> ~~"Adding generators is worth nothing as long as the added generators only re-describe the
> existing relators."~~ — **REFUTED, same session.**

AK(3) has a **cubic triangular form `C1` at rank 13** reached from it by 7 chord refinements
and 4 SPLITs — verified end to end here by un-SPLITting and un-merging back to AK(3)'s exact
relators — which *does* only re-describe AK(3)'s relators, presents the trivial group
(Todd–Coxeter index 1), and has **γ_N = 1, strictly below AK(3)'s γ_N = 2**.

The SPLIT move that did it introduces a fresh generator with a **length-3** definition
`tuv`, used in `k ≥ 1` further positions — so its edge carries **three or more** germs. It
re-describes the relators *and* changes the space, because "re-describes" is a statement
about the group and the germ count is a statement about the complex. **They are not the
same criterion, and only the second one is the theorem.**

## 3. The useful corollaries

- Subdivision is a **free re-coordinatisation**: it preserves the whole census, so a
  presentation may be moved to any rank for presentational convenience without perturbing a
  single Neuwirth measurement.
- Splitting bounds γ_N from **above**, so a defect-0 verdict computed after splitting is a
  valid certificate for the base, while a positive verdict after splitting proves nothing
  about it. Record which side of a bound each instrument sits on before reading it
  (`parallel-runs-and-bound-direction.md`).

## 4. Units, and the error that started this file

`gamma_N_factorial_n` returns `minimum_defect`; this project's **γ_N is
`minimum_defect // 2`**. Comparing the two manufactures a factor-2 anomaly and invites a
wrong theory to explain it. That happened here: a "γ_N went 2 → 4 under triangulation" line
was written, and a trap ("only the predicate is invariant, not the value") was filed on the
strength of it, before the units were checked. Both were wrong; the value is invariant.

Two wrong generalisations in one file, from the same habit — taking a theorem with a precise
hypothesis (two germs, from two distinct 2-cells) and restating it in looser, more memorable
language ("only re-describes the relators"). The looser statement is what gets quoted, and
it is the one that is false.
