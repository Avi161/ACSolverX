# The μ-descent solve criterion (ac-advisor-reviewed, verdict REVISE → this is the revised form)

*2026-07-21. The finish line for `experiments/stable_ac/cov/mu_ladder.py`. Reviewed by the ac-advisor gate; all five must-address items are incorporated below.*

## Proposition A (CoV is a stable move, any n_subs) — closes the citation gap

**Statement.** Let `P = ⟨x,y | R,S⟩` be a balanced presentation of the trivial group and `Q` the output of one gated subword-CoV transform of `P` (any `n_subs ≥ 1`, transformed-relator or defining-relator isolation). Then `P ~st Q`.

**Why the shipped theorems don't cover this.** `PROOFS.tex` Thms 1–3 and the line-242 corollary conclude via `Q = {φR, φS}` for `φ ∈ Aut(F₂)` — they cover only the orbit-preserving cases (`n_subs = 1` transformed-relator; defining-relator any `n_subs`). A μ-descending hop is by construction NOT an automorphic image, so those citations do not apply to the hops the ladder uses.

**Proof (direct Lemma-11 decomposition; every step a stable-AC move on a trivial-group presentation).** (S1) Stabilize with `z := w`: adjoin generator `z` and relator `z` (AC4), then transform relator `z` to `z⁻¹w` — legitimate because `w` is trivial in the presented group (the group is trivial), so this is exactly the substitution-and-removal supermove packaged as the Prop in `PROOFS.tex` (arXiv:2408.15332 Lemma 11); elementary-move cost unbounded, never counted as linear. (S2) Each substitution of an occurrence of `w` by `z` in a relator is one AC-composite: if cyclically `R = u w v`, then multiplying `R` by the conjugate `v⁻¹ (z⁻¹w)⁻¹ v` of the relator `(z⁻¹w)⁻¹` gives `u z v` (AC2 + AC3 + free reduction); repeat for each of the `n_subs` occurrences. Every intermediate is balanced (3 relators, 3 generators) and presents the trivial group (AC moves preserve the normal closure). (S3–S4) After substitution the isolator relator contains the eliminated generator `a` exactly once, cyclically `a · e⁻¹` with `e` a-free; eliminating each occurrence of `a` in the other relators by multiplying with conjugates of the isolator (AC2 + AC3) makes them `a`-free, and removing `(a, a·e⁻¹)` is the inverse of a Lemma-11 stabilization with word `e` — stable equivalence is symmetric, so this destabilization is a stable-AC composite. (S5) The relabel is an automorphic image, covered by `PROOFS.tex` Thm 3. ∎ (Flagged for migration to `PROOFS.tex` as a formal proposition; the argument uses only the already-packaged Prop, AC1–AC3 composites, and Thm 3.)

By induction, a finite CoV chain gives `P ~st Q_final`.

## The criterion

Let `Q'` = `aut_canon`'s canonical representative of `Q_final`'s orbit and `μ` its total (cyclically reduced) length — the same `|r₁|+|r₂|` ruler MM03 uses, and cyclically reduced ⇒ freely reduced, so `Q'` is inside MM03's covered set.

**(i) μ ≤ 12 ⇒ the source class is stably AC-trivializable.** Chain: `P ~st Q_final` (Prop A, per hop) `~st Q'` (`PROOFS.tex` Thm 3 — `Q'` IS an automorphic image of `Q_final`) `~AC trivial` (MM03 Thm 1.1: every balanced 2-generator trivial-group presentation of total length ≤ 12 satisfies the AC conjecture — a computer-assisted exhaustion with constructive GA certificates, covering every freely-reduced pair; degenerate one-relator shapes cannot present the trivial group, so both relators are automatically non-empty).

**(ii) μ = 13 is NEVER a removal.** Havas–Ramsay (IJAC 13, 2003 — primary text NOT in this repo; consistent secondary paraphrases: `mms02` §1, the Two-Hump paper §2, `ak_3_universal_test/RESULTS.md`) makes a length-13 trivial-group presentation AC-equivalent to standard or to AK(3), so the honest claim is "the class's stable fate collapses onto AK(3)-or-trivial". An `aut_canon` comparison CANNOT decide which: AK(3)'s length-13 AC-class provably holds at least two Aut-orbits (orbit-2 = `YYXXyx|YYYxyXX` is AC-equivalent to AK(3) yet a different orbit), so "not AK(3)'s orbit" does not imply "trivializable". A μ=13 landing IN AK(3)'s orbit gives `P ~st AK(3)` — structural news if `P` is not already known to be in that situation (aca_115 already is).

**(iii) Constructiveness, honestly.** The z-chain is recorded and each hop re-derivable; the CoV prefix is certified structurally (Prop A), never as a bounded elementary path (Lemma-11 cost is unbounded). The ≤ 12 endpoint's explicit AC path is expected from a modest greedy run, but MM03 calls lengths 11–12 its own hardest cases — if the path resists a local ≤ 1,000-node budget, the segment is certified by MM03-existence and labeled so, not silently assumed replayed.

## The verification bar (ALL required before "class X removed from the 124 (stably)")

1. μ ≤ 12, not 13.
2. Independent hop-by-hop re-derivation of the z-chain through the pure-Python `cov.py` spec; recompute `aut_canon` on the endpoint from scratch.
3. Per hop: no-collapse gate respected, isolator carries the eliminated generator exactly once, every intermediate abelianization-trivial (the Lemma-11 hypothesis), hop decomposes per Prop A.
4. Materialize the endpoint's AC path (≤ 1,000 nodes locally, else Colab) and replay through `verify_results.py`; if it resists, label the segment "MM03-existence, not replayed".
5. Confirm the endpoint is a cyclically-reduced balanced 2-generator TRIVIAL-group presentation (not MM03's order-120 exception family) of total ≤ 12.
6. **aca_115 tripwire**: a μ ≤ 12 hit for AK(3)'s class is presumed a bug until independently reproduced — it would settle an OPEN problem.
7. Claim wording: "stably AC-trivial; certificate = [CoV chain, structurally certified] + [AC path]" — never "solved" unqualified, never any AK(3) implication.

## Completeness caveat

The ladder at cap 24 is not proven cap-invariant beyond depth 2 (the cap-48 null was measured at depth 2 only), and the beam prunes — a class the ladder fails to descend is NOT evidence of a wall. Found chains are unaffected.
