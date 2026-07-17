# [2026-07-16] Citing a theorem whose hypothesis your data never meets [TRAP]

## What happened

I told the user twice that every `n_subs = 1` CoV row is a relabel "by the only-occurrence corollary, holding empirically — 5867 rows, zero exceptions". The number was right. The attribution was wrong, and nothing in the pipeline could have caught it.

`PROOFS.tex`'s Corollary *Only-occurrence degeneracy* is a corollary of the *Exact relator-minus-one factorization* theorem. That theorem's hypothesis 1 is `R = w^η a^ε` — the **two-letter isolator**, i.e. `|w| = |R| − 1` exactly. The paper says so in its own §"Claims to avoid": *"The proof applies only to the stated two-letter isolator."*

The shipped subwords family has a no-collapse gate (`MIN_TRANSFORMED_LEN = 3`) that rejects any `w` collapsing a relator below 3 letters. `R_z = z^η a^ε` has length 2. **So the gate rejects exactly the case the corollary covers.** Measured over relator words of length 2..5: all 544326 `n_subs = 1` rows sit at `|R| − 1 − |w| ≥ 1` — **none at gap 0**. Not one shipped row was ever inside the scope of the theorem I was citing for it.

The claim was true. The reason was invented. A cited theorem is not a *decoration* on a measurement — it is a claim that the measurement's cause is understood, and if it were wrong the number would still have looked fine.

## Why it held anyway (the real reason)

The conclusion generalizes, and the proof does not need `|w| = |R| − 1` at all. With the single occurrence in `R`: `S_z = S`, and `R_z` is forced to be the isolator. Isolation needs exactly one `a` in `R_z = z^η t`, so `t = b^m a^ε b^n` (pure `b`-powers around it), giving `a = (b^n z^η b^m)^{−ε} =: α`. Then **`ψ : a ↦ α, b ↦ b` is an isomorphism `F(a,b) → F(b,z)` for any `|w|`** — inverse `z ↦ (b^{−n} a^{−ε} b^{−m})^η`. The kept relators are `ψ(S)` and `z^{−1}ψ(w)`, and `ψ(R) = ψ(w)^η z^{−η}`, a rotation of the latter when `η = +1` and its inverse when `η = −1`. So output `= {ψ(R), ψ(S)}` up to order/rotation/inversion. Verified as an identity on 544326/544326 rows.

The proof's real load-bearing hypothesis is not `|w|` at all — it is **"the isolator is `R_z`"**, which holds only because `S` has no `z` *and* `allow_defining_iso=False`. In the universe family `Zw` is a legal isolator and the argument does not reach it. I nearly shipped the claim unqualified; the scope came from being asked "what about the universe family", not from my own reading.

## The rules

- **Before citing a theorem for a measured regularity, check its hypothesis actually fires on the rows you measured.** Grep the data for the hypothesis as a predicate (here: `|R| − 1 − |w| == 0`). A count of zero means the citation is wrong no matter how clean the number is.
- **A gate that removes a degenerate case also removes the theorem about that case.** The no-collapse gate and the relator-minus-one corollary talk about the *same* configuration; adding the gate silently orphaned every proof keyed to it. When you add a gate, re-check which cited results still have a non-empty scope.
- **Pin the mechanism, not the conclusion.** `test_n_subs_one_is_an_automorphism_for_any_w_length` asserts `output == {ψ(R), ψ(S)}`, not `aut_canon` equality. An orbit-equality assert would pass just as green if the transform silently became a *different* rename — the identity is what the proof claims, so the identity is what the test must hold. Mutation-checked: inverting `expr` is rejected by 30/30 AK(3) rows.
- **Name the hypothesis you did NOT verify.** The scope note ("subwords family only; `iso_index=2` is untested by this proof") is the part a reader cannot reconstruct.

## Second occurrence — same family as the |r|-2 error

This is the second time in one session that a claim about the *input's shape* stood in for a property of the *result*. First: I asserted a per-relator `|w| ≤ |R|-2` bound was theorem-backed, and told the user 496/521 "correctly survive" it when they are precisely the theorem's degenerate case — see [gate-a-candidate-by-effect-not-provenance](gate-a-candidate-by-effect-not-provenance.md). Both errors survived because the *numbers* were checked and the *reasoning attached to them* was not. Check both, and treat a citation as a testable claim.
