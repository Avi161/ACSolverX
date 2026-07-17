# [2026-07-16] Gate a CoV candidate by what its substitution DOES, not by where the word came from [TRAP]

Designing the subword z-family for the CoV length sweep, I set out to exclude the degenerate candidates and reached for a **provenance** rule: bound `|w|` per relator at `|w| <= |r_i| - 2`, i.e. classify a word by the relator it was read off. It was backed by a real theorem (`literature/proofs/PROOFS.tex`, relator-minus-one factorization: `|w| = |r|-1` is ordinary rank-two substitution plus a signed rename) and by a census showing 0/1263 such rows left the input's Aut(F₂)-orbit. It was still wrong, and the user caught it with one example.

`r1 = xyxxy`, `r2 = yxxy`, `w = yxx`. `|w| = 3 = |r1| - 2`, so `w` is a legitimate interior subword of r1 and every per-relator provenance rule keeps it. But `w` also occurs in **r2**, and takes it to `zy` — length 2. That is the two-letter isolator `z^η·a^ε`, precisely the theorem's degenerate hypothesis. Its outputs are `(yx, YYXY)` and `(X, YYx)`: primitive relators, i.e. starts that solve in ~1 node and measure nothing.

The provenance rule was only ever a **proxy** for the property that actually matters — "did the substitution collapse a relator to the two-letter isolator?" — and the proxy leaks in exactly the cross-relator case, because a word's length relative to *one* relator says nothing about its effect on the *other*. Testing the property directly (substitute into both relators, reject if either drops below 3 letters) is both stricter and simpler: it **strictly contains** the provenance rule (`|w| = |r|-1` collapses that relator to 2, `|w| = |r|` collapses it to 1), so no `|w|` bound is needed at all and the family loses its last knob.

Censused over the 66-row benchmark (enumeration only, no searches):

| rule | valid rows | new Aut-orbits | primitive-output rows |
|---|---|---|---|
| old `\|w\| <= 4` | 1729 | 338 | 20 |
| provenance `\|r\|-2` | 6655 | 398 | 25 |
| no-collapse | 6625 | 394 | 9 |
| both | 6625 | 394 | 9 |

"Both" is identical to no-collapse alone — the containment, confirmed empirically.

**Those are scratch-script numbers, and two of the three are wrong for the shipped code.** Re-run through `enumerate_cov` itself: the gate takes 7895 rows → **6618** (not 6625), keeps **394** of 398 orbits (matches), and cuts primitive rows 25 → **12** (not 9). Two causes, both invisible to a hand-rolled census: `enumerate_cov` dedups distinct `(z, iso_gen)` pairs landing on the same output, and the shipped gate only counts a collapse when `n_subs >= 1` (faithful to "the substitution must not *bring* a relator to length 2"), which the census predicate omitted. The `n_subs` guard is not inert: benchmark row `0` has `r2 = 'Yx'`, an input relator already of length 2, and it alone accounts for the 8 candidates where the two predicates disagree. **A census that reimplements the predicate instead of calling the shipped one measures a different rule — publish numbers from the code that ships.** The 4 forfeited orbits are genuinely distinct Aut-orbits, but they are the theorem's `σ(R, S*)` with `(R,S) ~AC (R,S*)` — AC-equivalent to a relabeling of the input, so a CoV to them duplicates an ordinary-AC path instead of opening a disconnected region. Careful with this claim: the theorem gives AC-*equivalence*, NOT reachability within a node budget (that is the open question this whole project studies), so "the greedy gets them for free" would be an overreach.

A compounding error: I had cited 496/521 as cases the provenance rule "correctly keeps", reading the proofs' census line "4 multi-occurrence rows (actual substitution work)" as meaning non-degenerate. It does not. The same document's worked example for 496 ends `{3,7} = {3,7}` and says outright that the CoV "encoded that substitution and then renamed the basis". Real substitution work (`n_subs = 7`) and mathematical degeneracy are orthogonal; I conflated them.

**Rule:** when excluding degenerate candidates, name the degeneracy as a property of the *result* and test it on the result. A rule phrased over the input's shape (a length, an index, which relator it came from) is a proxy — before shipping it, find the case where the proxy and the property disagree. If a proxy is defensible only because a theorem's hypothesis holds, gate on the hypothesis itself: it is usually cheaper to check, strictly stronger, and it deletes the knob.
