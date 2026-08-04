# S12 — The Stable Certificate Hunt: a general method for proving stable AC-triviality, and what high rank contributes to it

S-line, branch `claude/stable-ac-conjecture-stabilization-rwo9as` (merge into
`fable/proof`). This is the S-line's answer to the session's second question — *"is there a
simple general way of solving any presentation with this technique?"* Status: **method
statement + soundness proof (this file); its measured basis is S10; its application is
tasks A7/A9/A10/A11.**

## 1. The method

> **Stable Certificate Hunt.** Input: a balanced presentation `P` of the trivial group,
> rank `n`. Choose a depth `k`.
> 1. Stabilize `k` times (AC4) to `P^{+k}`, rank `N = n+k`.
> 2. Search the AC1–AC3 move graph at rank `N` (beam / random restarts / greedy), keeping
>    total length under a cap. **Weight the moves by their measured flip rates (S6 §1):**
>    - **AC2** `r_i → freered(r_i r_j^{±1})` is the *only* slide measured to create the
>      certificate — 73 creates in 1,863 pairs, i.e. **7.0 % of non-thickenable bases gain
>      it**. This is the engine; spend the budget here.
>    - **move (0)** free/cyclic reduction: 315 creates in 2,510, **0 destroys in 997**.
>      Always reduce. Never search un-reduced spellings — by the same measurement, spiking
>      can only preserve or destroy (this closes the spelling route for the positive
>      direction; see S11).
>    - **AC3 bare conjugation is counterproductive**: 315 destroys in 3,507, **0 creates in
>      2,195**. Downweight or drop it.
>    - AC1, cyclic rotation, AC4/AC5, chord refinement, and — by Theorem T4′ — the *first*
>      slide over a fresh stabilizer `r_i → r_i z^{±1}` are all provably inert. Budget spent
>      on them cannot move γ_N, so a stabilized generator must be pushed past the
>      subdivision regime (three or more 2-cell germs) before a state is worth scoring.
> 3. For each state `Q` reached, decide **orientable thickenability** — γ_N(Q) = 0 — by the
>    Neuwirth compatible-rotation census.
> 4. On a hit: stop. `P` is stably AC-trivial, and the hit is a finite, checkable
>    certificate.

It is a *semi-algorithm*: it can prove stable AC-triviality and can never disprove it.

## 2. Soundness

Suppose the hunt returns `Q` at rank `N` with γ_N(Q) = 0.

1. `Q` is balanced and presents the trivial group — AC1–AC4 preserve both.
2. γ_N(Q) = 0 ⟺ `|K_Q|` PL-embeds in an **orientable** 3-manifold (`R1E` Thm D, the repo's
   bridge; `[UNVERIFIED against Neuwirth's paper — lit_AK3_NEUWIRTH.md is absent from this
   clone]`).
3. `Q` satisfies the hypothesis of **Lackenby Thm 1.3** — *balanced + presents the trivial
   group + presentation 2-complex thickenable ⇒ AC-trivializable*, with no stabilization
   and no rank restriction found in any channel (`S2_LITERATURE_HIGH_RANK.md` Q1; the
   theorem is SOURCE-RELAYED, not read in full from the LaTeX, and it is the method's
   single load-bearing import).

   **[REPAIRED after audit A12 — this was the weak step.]** The first draft argued only
   "an orientable PL 3-manifold is a 3-manifold", which silently picks the *weakest* of the
   three inequivalent definitions of "thickenable" that `S2` explicitly flags (some
   3-manifold / some orientable / closed orientable) — and `S2` only *relayed* the weakest
   reading; the abstract, its one source-verified text, does not define the word. The repair
   discharges all three at once: Theorem D's sufficiency builds a global PL embedding into a
   **compact** orientable 3-manifold `W`; the double of `W` is **closed** orientable; and
   `N(K_Q) ≅ B³ ⊂ S³` exhibits `K_Q` as a spine. So whichever of the three Lackenby means,
   the hypothesis is met.

   **Note the direction:** the orientability mismatch of S3's trap T-S9 obstructs *negative*
   readings only. A hit is not encumbered by it.
4. So `Q ~AC standard_N`, and `P ~st P^{+k} ~AC Q ~AC standard_N ~st standard_n`. ∎

Two things the method does **not** give: any statement when it finds nothing (silence is
worth exactly its measured detection rate — `calibrate-one-sided-hunts-on-a-positive-ladder.md`),
and any bound on `k` or on the search length.

## 2a. Why the hunt beats plain AC search — the target is enormously bigger

A plain AC search must reach **one** state: the standard presentation. The certificate hunt
may stop at **any** thickenable state, and S10 measures how many of those there are. Among
presentations that are AC-trivial by construction, the thickenable fraction is 0.87 at
rank 4 near standard, 0.41 at rank 2 near standard, and still 0.21 at rank 2 far from
standard (walk length 70–120). So the goal region is not one state out of the whole class —
it is a **constant fraction** of it, and a large one.

That is the method's actual edge, and it is worth stating because the same measurement
carries the matching caveat: the density **falls with distance from standard**, which has an
obvious explanation — the standard presentation is itself thickenable (its complex is a
wedge of discs, which embeds in `R³`), so certificates cluster around it. The hunt's
advantage therefore shrinks as one moves away from standard, and it shrinks exactly in the
region where the hard presentations live. Both halves of that are measurements, not
intuitions, and both belong in any assessment of the method.

## 3. Why this is not merely a restatement

`FRAMING` §3 rules out "reduction of stable ACC to a different open problem". This is not
that: thickenability is **decidable** (Neuwirth; and polynomial-time by Fulek–Tóth per
`S2` Q5), so step 3 is an algorithm, not an oracle. The method converts an undecidable-looking
search into a decidable test applied along a search — and `FRAMING` R4 records that no
computational method has ever searched AC4/AC5 space directly, which is exactly the gap
this fills.

## 4. What high rank contributes — three distinct things, only two of which are real

| claim | verdict |
|---|---|
| **(a)** More generators give more *moves*, so the search reaches more states | true but vacuous — it is just the definition of stable equivalence |
| **(b)** More generators let you *abbreviate* long relators into a tractable form | **REFUTED.** S3: abbreviation is a subdivision, γ_N and the whole defect histogram are invariant (1,525/1,525). S8: splitting is monotone, never decreases γ_N (632/632). Bookkeeping buys nothing |
| **(c)** More generators make the *certificate more common* | **REFUTED** (`S10_S12_AUDIT.md`). S10's rank axis was a relator-length axis in disguise: at fixed **total** length, `mean relator length = total / rank`. Holding **per-relator** length fixed instead, the thickenable fraction is 0.868 / 0.868 / 0.834 / 0.780 at ranks 2/3/4/5 — flat, then slightly decreasing |
| **(d)** More generators make the *test computable* where it was not | **TRUE BUT NOT ABOUT RANK.** The census is `∏(deg−1)!` and a germ's degree is its letter's occurrence count, so this is the statement that *short relators are cheap to decide*. Rank enters only because, at fixed total length, more generators means shorter relators — the same confound as (c), read as a feature |

So the honest answer to "does going to 9 or 10 generators make AK(3) easier" is:

> **No — not by any mechanism, and not by any population effect this session could
> measure.** Abbreviation is provably inert (S3), splitting is monotone (S8), change of
> variables is depth-1 (S7/F1), AC4/AC5 and the first slide over a fresh stabilizer are
> provably inert (S6 T4/T4′), and the one measurement that looked positive turned out to be
> measuring relator length. What is real, and worth keeping, is that **short relators are
> cheap to decide and long ones are not** — which is a reason to prefer presentations with
> short relators, reachable by raising the rank, but it is a statement about *length*, and
> raising the rank is merely one way to buy it.
>
> Two experimental readings of the same conclusion, both from length-matched controls:
> A7's depth ladder returns 39/40 hits on an AC-trivial control across rank ceilings 2–6 and
> **0/40 on AK(3)** on the same rungs and seeds; and this file's own `--target` mode shows
> control detection *falling* from 6/6 at depth 0 to 2/6 at depth 1 at fixed budget —
> exactly what Theorem T4′ predicts, since budget spent on the inert first slide cannot move
> γ_N.

## 5. The depth to choose

`S7` settled that change of variables — the other half of the session's brief — is entirely
a **depth-1** phenomenon: the whole `Aut(F_n)` orbit lies in `~^{(1)}` (`S1` Cor. F1). So
depth beyond 1 is not bought for coordinate changes; it is bought for the population effect
(c) and computability (d), both of which are already strong at depth 2–4. The open question
`Q(F2)` — whether `~^{(1)} = ~^{(k)}` — remains, and until it is settled there is no
theoretical reason to prefer large `k`; S10 gives an empirical reason to prefer `k ≈ 2–4`.

## 6. Falsifiable predictions this method makes

Recorded now so that the experiments cannot be read after the fact:

- **P1.** Run on an AC-trivial presentation of moderate length at depth 2–4, the hunt should
  succeed at a rate near the S10 density (≳ 70 %) within a modest node budget. *If it does
  not, the density baseline does not transfer to the search's reachable set and S10 §5 must
  be discounted.*
- **P2.** Run on AK(3) at depth 2–4 with the same budget, it should succeed if AK(3) is
  stably AC-trivial. Extended silence, **with P1's rate measured on a matched ladder**, is
  evidence for the disproof side — bounded, quantified, and not a proof.
- **P3.** Run on the 124 unsolved Miller–Schupp classes, any hit settles that class outright
  (Lackenby, §2). This is the cheapest available shot at a new result and is task A11.

## 7. Honest limitations

1. The whole chain rests on Lackenby Thm 1.3, which `S2` could only relay from an abstract
   plus two secondary restatements — the LaTeX source has no public mirror. If Thm 1.3 turns
   out to need a hypothesis `S2` did not see (a rank bound, or "AC-trivializable" meaning
   *stably*), the method degrades from "proves AC-triviality" to "proves stable
   AC-triviality" — which is still exactly what this session wants for AK(3), so the method
   survives either reading. **Recorded because that robustness is the reason to keep going
   without the source.**
2. The Neuwirth bridge γ_N = 0 ⟺ orientably thickenable is cited from repo notes whose
   source file is absent from this clone (`literature-absent-in-cloud-clones.md` is exactly
   about this failure mode). A hit must be re-verified by `witness_check_n`, and the
   underlying claim re-read from Neuwirth before any write-up leaves the branch.
3. Nothing here bounds `k`, the search length, or the number of elementary moves inside
   Lemma 11 (the authors' own open problem, `S7` §1).
