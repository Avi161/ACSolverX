# S7 — What stabilization DEPTH buys: the rank filtration, and where "10 generators" can and cannot help

Orchestrator note, S-line. Branch `claude/stable-ac-conjecture-stabilization-rwo9as`
(merge into `fable/proof`). Written after S1 (Triangulation Lemma + Cor. F1), S2
(literature), S3 (subdivision invariance). Status of every claim is labelled.

## 1. The primitive, quoted from source

`Lemma 11` of the session goal is **Lemma 11, "Substitution and Removal"**, of
arXiv:2408.15332 (Shehper et al.), read this session from a clone of
`github.com/ammedmar/ac_paper` @ `d86984d`, `sec/stable.tex:28–30`
[VERIFIED-FROM-SOURCE, A2]:

> Let `P = ⟨x₁,…,xₙ, y | r₁,…,rₙ, y⁻¹w⟩` be a presentation of the trivial group, where `w`
> is a word in `x₁,…,xₙ`. Then `P' = ⟨x₁,…,xₙ | r₁',…,rₙ'⟩` is stably AC-equivalent to `P`,
> where `rᵢ'` is `rᵢ` with all occurrences of `y` replaced by `w`.

Two things in the source that the S-line must respect:

- The proof runs entirely at rank `n+1`: substitute, rewrite `y⁻¹w` into `y` using that
  `w` is a product of conjugates of the `rᵢ'`, then AC5. **No excursion above `n+1`.**
- The authors state explicitly that the number of elementary moves is **unbounded** —
  there is no known bound on the number `m` of conjugate factors, and finding one is
  posed as an open problem. FRAMING trap 6, which calls the cost "exponentially many",
  conflates this with Lackenby's (4⁺) conversion. Corrected here: **Lemma 11's cost is
  unknown, not exponential.**

The S0 "free-definition move" (S-a) is the same primitive from the other end, and A1
proved it **sharp as a biconditional**: `(r₁..rₙ, z) ~_{AC1–AC3} (r₁..rₙ, zw)` at rank
`n+1` **iff** `w ∈ ⟪r₁..rₙ⟫`. So the trivial-group hypothesis is not a convenience — it is
exactly the condition under which a stabilized generator may be defined to be *anything*.

## 2. The filtration

For `P`, `Q` balanced of rank `n`, write **`P ~^{(k)} Q`** iff some AC1–AC5 chain joins
them whose rank never exceeds `n+k`. Then

    ~^{(0)} ⊆ ~^{(1)} ⊆ ~^{(2)} ⊆ … ,   ⋃ₖ ~^{(k)} = stable AC-equivalence,

`~^{(0)}` is ordinary AC-equivalence, and the stable AC conjecture is: every balanced
presentation of 1 is `~^{(k)}`-equivalent to standard **for some k**. The session question
— "does AK(3) or one of the 124 unsolved MS classes get easy at 9 or 10 generators?" — is
exactly: **is the useful `k` small, and is the filtration strict?**

**Literature status [A2, Q4]: nothing is known about this filtration.** No strictness
result, no collapse result, no published search above rank 3, and the `AC_k` of
Gilman–Myasnikov indexes tuple length, not stabilization budget (notation collision — do
not cite it here). So every statement below is this line's own.

## 3. What is settled

**(a) `k = 1` already buys the entire change of variables.** [A1, Cor. F1, proved]
For every `φ ∈ Aut(Fₙ)` and every balanced `P` of the trivial group,
`P ~^{(1)} φ(P)`. The chain is: AC4; define `z := w` by Lemma S-a; substitute the target
generator away; convert the leftover relator to a single generator (second use of
triviality); AC5. One elementary substitution per excursion, composed over a Nielsen
generating set.

  *Consequence for the session hypothesis.* "Change of variables" — the first half of the
  user's instruction — is **entirely a depth-1 phenomenon**. Going to 9 or 10 generators
  cannot buy a coordinate change that 3 generators do not already buy. Whatever high rank
  is worth, it is not worth it for CoV.

**(b) Depth costs nothing in thickenability if the new generators are abbreviations.**
[S3, proved; audit pending] A stabilized generator used exactly twice makes the refinement
a **subdivision** of the presentation complex: same space, same γ_N. Measured: 480 random
triangulations of 13 bases (120 of them AK(3)) reproduced the base's `minimum_defect`
exactly, zero deviations, and never reached 0. AK(3) sits at `minimum_defect` 4 (γ_N = 2)
at rank 2 **and** at rank 9.

  *Consequence.* The most natural "just add more generators" mechanism — abbreviate long
  relators until everything is short — is provably inert. This is the single most useful
  negative of the session: it rules out an entire family of high-rank attacks in one line,
  and it explains why Lackenby can subdivide freely inside his Lemma 3.1 without ever
  worrying about losing thickenability.

**(c) So the depth question is a question about AC2 and AC3 only.** AC1 is a
reparametrization, AC4/AC5 wedge on and remove a disc, and chord refinements are
subdivisions. Every change in the homeomorphism type of `|K|` along a stable chain — hence
every gain or loss of thickenability — is attributable to free reduction (move (0)),
AC3 conjugation, and AC2 multiplication. [The AC3 half is the subject of task A8 and is
**[OPEN]** here; the claim that AC1/AC4/AC5 are inert is proved in S3 §4 and A8.]

## 4. What depth `k ≥ 2` could buy, stated precisely

Since CoV is depth-1 and abbreviation is inert, a depth-`k` chain can only help by making
AC2 slides available that no depth-1 chain has. Concretely, at rank `n+k` a relator may be
multiplied by a conjugate of a relator that itself already involves several of the new
generators — an "entangled" slide with no depth-1 serialization. The precise open question:

> **Q(F2).** Is `~^{(1)} = ~^{(k)}` for all `k`? Equivalently: can every stable AC chain be
> rewritten so that at most one extra generator is alive at any moment?

A YES would be a strong negative for the session hypothesis — it would say **"10
generators" is provably worth exactly what 3 generators are worth**, and would reduce
stable ACC to a depth-1 statement, which is a genuinely simpler object (the excursion is a
single Lemma-11 round trip). A NO, with an explicit witness pair, would be the first
strictness result for the AC stabilization hierarchy and would justify high-rank search
outright.

**First, the level below it is BLOCKED, and that is worth recording because it says where
the untouched territory actually starts.** Ask instead whether `~^{(0)} ⊊ ~^{(1)}` — does the
*first* stabilization already buy something? By Cor. F1, `P ~^{(1)} φ(P)` for every
`φ ∈ Aut(Fₙ)`. So if the **unstable pairwise automorphism principle fails** — i.e. if some
balanced presentation `P` of the trivial group has `P ≁_AC φ(P)` — then `~^{(0)} ⊊ ~^{(1)}`
immediately. That principle is open and is **conjectured FALSE by Panteleev–Ushakov**
(`FRAMING` §3, which forbids using it as if proven). Therefore:

> Proving `~^{(0)} ⊊ ~^{(1)}` is at least as hard as refuting the unstable pairwise
> automorphism principle. By the route-selection rule of `FRAMING` §6 that is a reduction to
> another open problem, so **strictness at level 1 is BLOCKED** and should not be attacked
> on this line.

(The converse is not available: `~^{(0)} = ~^{(1)}` would give the unstable principle, but
nothing shows `~^{(1)}` is *generated* by automorphism moves — a rank-`n+1` excursion may do
more than realize an `Aut(Fₙ)` element. So this is a one-way implication and is used only in
the blocking direction.)

That is exactly why **Q(F2) is posed at `k ≥ 2`**: level 1 collapses onto a known open
problem, while levels 2 and above are untouched by anything in the literature (A2, Q4).

Neither direction of Q(F2) is settled here. What can be said now:

- **Not obviously YES.** The naive serialization argument fails: to simulate a rank-`n+2`
  slide `rᵢ ← rᵢ · u (rⱼ involving y₁ and y₂) u⁻¹` at depth 1, one would have to remove
  `y₂` first, and Lemma 11 removal *substitutes `y₂`'s definition back*, which undoes
  exactly the entanglement that made the slide interesting.
- **Not obviously NO either**, because the free-definition move is so strong: at depth 1
  the relator `y⁻¹w` may be redefined to `y⁻¹w'` for *any* `w'` at the moment the other
  relators are still `y`-free (A1's biconditional applies: `w⁻¹w'` has zero `y`-exponent
  and lies in `⟪r₁..rₙ⟫^{F_{n+1}}`), so a great deal of depth-2 bookkeeping can be
  re-expressed as a sequence of depth-1 redefinitions.

**The circularity trap that must not be walked into.** The tempting composite is:
define `y := w`; replace an occurrence of `w` inside `rᵢ` by `y`; *redefine* `y := w'`;
remove by Lemma 11 — apparently rewriting `w ↦ w'` inside `rᵢ` for arbitrary `w'`. That
composite is **not legal in general**, and the reason is worth recording because it looks
legal: once `rᵢ` contains `y`, the redefinition `y⁻¹w → y⁻¹w'` must be effected by
conjugates of the *other* relators, which now include `y`, so A1's biconditional no longer
delivers every `w'`. If it did, arbitrary triviality-preserving local rewriting would be a
stable move and stable ACC would follow immediately — the surest sign that the step is
wrong. Any future proposal on this line that rewrites a subword must show its `w⁻¹w'` lies
in the normal closure of the *other* relators **at the moment the redefinition is made**.

## 5. What this says about the session's target presentations

- **AK(3)** (`aca_115` of `data/ms_unsolved_reps/aca_124.csv`, the `13_1` representative,
  and the minimal open case): its Aut(F₂)-orbit and its whole triangulation family are
  now accounted for — depth-1 and topologically inert respectively. Its γ_N is 2 at every
  rank reachable by abbreviation. Any high-rank progress must come from entangled AC2
  slides, which is what task A7's rank-`N` search is built to look for.
- **The 124 unsolved MS classes**: the same applies class-wide, but the arithmetic below was
  wrong and is corrected here after audit A12.
  **[CORRECTED.]** The `aca_*` classes are **not** `Aut(F₂)` orbits. The source branch's own
  README defines ACA as "AC moves *together with* change of variables", and says explicitly
  that **124 is an upper bound**; the Aut-orbit table is a different file
  (`solved_640_aut_orbits.csv`). Its `PROOFS.md` records 137 identification edges = 93
  change-of-variables edges + 44 AC edges. So Cor. F1 does real work but less of it than
  claimed: deleting only the 93 cv edges leaves `261 − 44 = 217` components, so **F1
  collapses at most 217 objects to at most 124**. The correct sentence is "*at most* 124",
  and it depends on 137 certificates computed on another branch (3 spot-checked this
  session), so it is not purely a theorem of this line. AK(3) = `aca_115` is verified.

## 6. Open items this note hands on

1. **Q(F2)** above — strictness or collapse of `~^{(k)}`. First target: find any pair
   `P, Q` with `P ~^{(2)} Q` and a proof or strong evidence that `P ≁^{(1)} Q`.
2. Bound `m` in Lemma 11 (the authors' own open problem) — a bound would make depth-1
   excursions *searchable*, converting Cor. F1 from an existence statement into an
   algorithm.
3. A8: does AC3 change `|K|`? If AC3 is also inert, then AC2 alone carries every
   thickenability change and the search space for "find a thickenable member" collapses
   dramatically.
