# Stable Andrews–Curtis — session framing (fable line)

Session branch: `claude/ac-stable-ac-conjecture-ijfzgz` (to be merged into `fable/proof` by the
user; never into `main`). This document is the standing frame for every proof attempt on this
line. It follows the erdos-workflow discipline: precise statement → success criteria → what does
NOT count → traps → route portfolio. The parallel `codex/proofs` line
(active branch `research/w5/stable-ac-escape`) is a separate solver; this line must stay
complementary to it (their frontier: bounded classification of stable histories through AK(3)'s
rank-three compression root + Fox/finite-quotient/SU(2)/Hessian obstruction certificates, and
Neuwirth planarity censuses of AK(3)'s CoV family and small-length pairs).

## 1. Precise statements

Fix a balanced presentation P = ⟨x₁,…,xₙ | r₁,…,rₙ⟩ of the trivial group.
Moves (project operating-contract numbering — beware: papers permute the numbers):

- **AC1** (invert): rᵢ → rᵢ⁻¹.
- **AC2** (multiply): rᵢ → rᵢrⱼ, j ≠ i.

  [CORRECTED after adversarial audit: this file previously had AC1 and AC2 the other way
  round, contradicting `CLAUDE.md`, `R1E_DISCONNECTED_LINK.md` and
  `R3PRIME_GRAFT_CALCULUS.md`, which all use AC1 = invert / AC2 = multiply. Under the old
  numbering a phrase like "all AC2 graft images" read as *inversions*. The project
  convention above is now the single one in force on this line; papers permute these
  numbers, so always check a paper's own definition before quoting a move by number.]
- **AC3** (conjugate): rᵢ → w rᵢ w⁻¹, w ∈ F(x₁..xₙ).
- **(0)** free and cyclic reduction (Lackenby's move (0); harmless normalization).
- **AC4** (stabilize): adjoin fresh generator xₙ₊₁ and fresh relator xₙ₊₁.
- **AC5** (destabilize): inverse of AC4, allowed only when xₙ₊₁ occurs in no other relator.

**AC conjecture:** every balanced presentation of the trivial group is transformed to the
standard presentation ⟨x₁..xₙ | x₁,…,xₙ⟩ by AC1–AC3 (+(0)).
**Stable AC conjecture:** same with AC1–AC5.
**Minimal open case:** AK(3) = ⟨x,y | xyx(yxy)⁻¹, x³y⁻⁴⟩ (total length 13). Its AC-triviality
AND its stable AC-triviality are both open (the believed stable proof died with the MMS02
Thm 1.4 misprint — see traps). All length ≤ 12 presentations are AC-trivial; every length-13
2-generator presentation is AC-equivalent to standard or to AK(3) (Havas–Ramsay).

Three distinct claims — every lemma on this line must name which one it addresses:
- **trivial group**: the presented group is 1 (a hypothesis here, not a goal);
- **AC-trivial**: reachable from standard by AC1–AC3;
- **stably AC-trivial**: reachable from standard by AC1–AC5.
AC-trivial ⇒ stably AC-trivial. Neither converse is known; a stable counterexample is the
strictly stronger negative result.

## 2. What a complete resolution must establish

**Proof of stable ACC:** for EVERY balanced presentation of 1 (every rank n), an argument
producing a stable AC chain to standard. (A uniform mechanism — e.g. "every balanced
presentation of 1 reaches a thickenable presentation by stable moves", which suffices by
Lackenby 2026 Thm 1.2/1.3 — is acceptable; effective bounds are NOT required.)

**Disproof of stable ACC:** one explicit balanced presentation of 1 PLUS a proof that no
AC1–AC5 chain to standard exists — i.e. a quantity invariant under all five moves, computed
to differ between it and standard. "Search exhausted budget B" is never such a proof.

**A second, equivalent shape for the disproof — recorded because this line kept
mis-filing it as a negative result.** By the thickenability reformulation, stable ACC is
equivalent to: *every balanced presentation of the trivial group reaches SOME thickenable
presentation by stable AC moves.* Therefore

> a proof that AK(3)'s STABLE CLASS contains no thickenable member — in any spelling —
> **disproves the stable AC conjecture.**

This matters for how the γ_N machinery is valued. A spelling-independent, class-wide
LOWER bound on γ_N is not a "route closed, write up the negative" outcome; it is the
headline disproof, and that is precisely why no such bound is known. It also explains
Wall 5 (R3_INVARIANT_LANDSCAPE): natural class functionals are tautological because
Φ_min = 0 ⟺ the class contains a thickenable member, so any functional that could
witness the obstruction is the obstruction. Any candidate obstruction must therefore be
audited with maximum hostility — the prior against it is exactly the prior that stable
ACC is true. [Depends on the thickenability reformulation, which is [UNVERIFIED] this
session — see LITERATURE_STATUS.md §1.]

**Named sub-goal (huge result on its own, commit + notify immediately):** AK(3) is stably
AC-trivial (or AC-trivial, or any resolution of AK(3)'s stable class). This does not resolve
the conjecture but is a headline result: it is the unique minimal open case and the
first-listed open problem in the area.

## 3. Results that do NOT count as completion

- Any bounded-budget search outcome, positive expectation, or "no counterexample found".
- Closure/self-loop theorems for a bounded stratum of histories (that is the codex program;
  honest intermediate theorems, not resolutions).
- A new stable equivalence between two non-standard presentations (an edge, not a resolution)
  — unless one endpoint is proven thickenable/AC-trivial, in which case it transfers.
- Reduction of stable ACC to a different open problem (that marks a route BLOCKED).
- The unstable pairwise automorphism principle used as if proven (it is OPEN and conjectured
  FALSE by Panteleev–Ushakov; only the STABLE form is a theorem — PROOFS.tex Thm 3 /
  implicit in Lackenby §2).

## 4. Trap list (imported from project lessons — hard constraints)

1. **MMS02 Thm 1.4 is void** (misprinted 13th Wirtinger relator, found by Shehper et al.
   v2 App. F); Lisitsa 2501.18601 re-proves only the NON-stable P ~AC AK(3) link. Never cite
   either as settling AK(3) stable triviality. Two DISTINCT partner presentations (corrected
   29-07 after ac-advisor audit — an earlier revision of this file conflated them):
   **P25** = ⟨x,y | XYxYXyxYYxyXy, YXyyXYxyxYYx⟩ (total length 25, Shehper app/mms.tex),
   AC-equivalent to AK(3) by the doubly-verified 53-move path; and
   **Q** = ⟨x,y | xxxxyXXYxyXXY, YxxyXXYxxyXXYxxyXXY⟩ (total length **32**, recorded by the
   codex ac-advisor ground truth as MMS02 Prop 1.2's stable partner — that attribution is
   [unverified this session]; MMS02 itself is proxy-blocked). Q's GROUP TRIVIALITY is proven
   locally (Todd–Coxeter over the trivial subgroup completes with index 1, 453 cosets), so
   only Q's transfer edge to AK(3) awaits the MMS02 source read.
2. Cite the stable ambient automorphism principle only in its stable form; state the
   triviality hypothesis (it is sharp). Rank-2 proof only — higher rank needs the
   substitution-and-removal re-derivation.
3. Free-reduce every substituted relator completely, including the seam between unchanged
   prefix and substituted block; test parametric identities at negative/zero/positive
   parameters; cyclically reduce before conjugacy comparisons.
4. Exclude degenerate CoV candidates by what the transform DOES (no relator below length 3),
   never by input shape.
5. Move-numbering differs across papers (MMS/Lisitsa vs P–U vs Shehper); verify against each
   paper's own definitions before quoting.
6. Lemma 11 / Lackenby (4⁺) conversions cost exponentially many elementary moves — never
   compare "path lengths" across move formalisms without the conversion model.
7. Lackenby §6 switches frameworks (free semigroup, no move (0)); never import §6 statements
   into the §§1–5 framework carelessly.
8. Bridson/Lishak tower lower bounds SURVIVE stabilization: unsolved-at-budget is never
   evidence; those families are calibration anti-benchmarks.
9. "Killer" (normally generating) elements of torus-knot groups need not be meridians
   (Silver–Whitten–Williams); never infer "killer ⇒ braid class".
10. Local searches ≤ 1,000 nodes, CPU+numba only, new files only, never modify existing code,
    never open a PR, `literature/` is gitignored (`git add -f` for tracked proof notes;
    shareable summaries live here under `results/stable_ac/theory/`).

## 5. Key imported theorems (verified against ac-advisor's ground truth; re-verify from
sources before load-bearing use)

- **Lackenby arXiv:2606.06122** — P thickenable (presentation 2-complex embeds in a
  3-manifold; DECIDABLE, Neuwirth) and presents the trivial group ⇒ P is AC-trivializable
  (Thm 1.3), with an explicit doubly-exponential stable bound (Thm 1.2). Equivalent
  reformulation: stable ACC ⟺ every balanced presentation of 1 reaches SOME thickenable
  presentation by stable AC moves. **Thm 1.3 is [unverified this session]** (cited from two
  agreeing secondary restatements: ac-advisor ground truth + codex Corollary 3, which
  independently derives N ≅ B³ so Thm 1.3 supplies exactly the final "ball ⇒ AC-trivial"
  step); re-read §1/§3.1 from source before any transfer theorem is written.
- **MMS02 Prop 1.2** — AK(3) ~st Q (see trap 1 for Q's exact words, length 32, and the
  provenance flag). First stably equivalent pair not known AC-equivalent, per the codex
  ground truth.
- **PROOFS.tex Thm 3** (this project) — (R,S) ~st (φR,φS) for φ ∈ Aut(F₂) on balanced
  presentations of 1: the Aut(F₂)-orbit sits in one stable class.

## 6. Route portfolio (complementary to codex; kept deliberately incompatible)

- **R1 — Thickenability transfer along stable edges (positive direction; PRIMARY).**
  AK(3)'s stable class contains more than its Aut-orbit and CoV family: MMS02 Prop 1.2 gives
  P25, and the Prop 1.2 mechanism plausibly generates a whole family of stable neighbors.
  Every such neighbor is a decidable test: if ANY is thickenable, then (Lackenby Thm 1.3 +
  AC ⊆ stable AC + transitivity) **AK(3) is stably AC-trivial**. Codex Neuwirth-censused
  AK(3)'s own orbit/CoV family (all non-thickenable so far, exact minimum 13 stands); P25 and
  Prop-1.2-mechanism neighbors are OUTSIDE their censused families. Work items: verify Prop
  1.2 + extract exact words; port/extend a Neuwirth planarity certificate to length ~25;
  generalize the mechanism into a neighbor generator; run the decidable test on each neighbor.
  Failure mode to respect: all tested neighbors non-thickenable ⇒ bounded negative, write up.
- **R2 — Wirtinger chain repair (positive direction). STATUS: BLOCKED by the codex line,
  29-07 ~15:32 UTC** — do not re-open without new input. They reconstructed the 14-relator
  MMS02 corridor with the corrected r13 = x4 x12 x4^-1 and the printed x5 misprint; after
  the paper's deletion and eleven exact eliminations the corrected descendant reaches the
  trivial basis (45 primitive AC1–AC3 moves) while the misprinted one is exactly the
  published P and reaches AK(3) by all 53 Appendix-F moves. Their conclusion, which we
  adopt: **bridging the two descendants is equivalent to AC-trivializing AK(3)**, so the
  repair is not a proof but a restatement of the open problem. They further separate the
  corrected and misprinted r13 probes by an A5 quotient (cycle types 3 vs 5) and by
  Alexander polynomial (t^4-3t^3+5t^2-3t+1 vs 1), which blocks a fixed-base final-row
  substitution repair specifically. Their residual open piece is a literal rank-three
  bridge with all rows free — the one place our rank-3 machinery could still contribute.
- **R3 — Disproof-side invariant frontier (negative direction; kept alive).** Map what any
  stable-AC invariant must evade (semisimple TQFT blindness, Gompf standardness of
  Cappell–Shaneson spheres, homological triviality); identify genuinely unexplored invariant
  classes; write up blocked directions as results.
- **R4 — Stable-move-native search theory (background).** No computational method has ever
  searched AC4/AC5 space directly (Lisitsa 2025 challenge). Theory-driven targeted
  stabilization schedules (where Lemma-11/CoV proposes the stabilizing word) — design +
  soundness proofs here; production budgets are the user's.

- **S — high-rank stabilization (rank ≫ 3). STATUS: CLOSED, and the closure is now
  mechanistic rather than a null. START AT `S22_FINAL_ANSWER.md`**, not at S13 — S13 is the
  working record and contains three retracted sections kept verbatim. Added 2026-08-04:
  **stabilization is exactly inert for γ_N** (exact census: AK(3) holds `minimum_defect` 4 at
  ranks 2, 3, 4 and 5), so extra generators alone move nothing; where extra rank was measured
  against a fixed budget it **hurt** (0/32 at ceilings 3–6 vs 8/40 at ceiling 2). The one
  move that exploits new generators — A6's length-3 SPLIT — **destroys** certificates at
  69.6 % and has created one 0 times in 57,858, while plain **AC2** creates them 14 times in
  1,470 on *identical* parents: build future high-rank searches on AC2-rich move sets, not on
  SPLIT. **Lemma 11 is answered** (S19): its `m` *is* an algebraic/van Kampen area, and the
  uniform effective bound the authors pose is *equivalent* to Magnus's problem, so that
  sub-route is **BLOCKED**; family-specific bounds are untouched and remain open.
  **`γ_N` is not a stable-AC invariant** (S15.3, explicit witness) — the cleanest disproof
  idea on this line is dead. **`non-planar link ⇒ γ_N ≥ 1` is proved** (S20) — the line's
  first certified lower bound — but it bounds a *state's* γ_N not `Γ`, is not preserved by
  SPLIT, and is vacuous on AK(3) (whose link is exactly `K4`), so no disproof route opens.
  **METHODOLOGICAL WARNING, the session's most transferable finding (T-S20):**
  target-versus-control **cannot** settle this question. Three successive control designs
  were retracted, and an auditor matched controls on every axis the instrument can see —
  including relator shape and abelianisation — without the rate collapsing (59/64). Any
  control you can *verify* is solvable is, by that verification, close to a solution in a way
  an open target is not, and its hits escape through a length region the target is denied.
  Do not build a fourth version.

  *(Superseded text kept for continuity:)* Summary of what is now settled,
  so this route is not re-opened by accident: abbreviation-style stabilization is a **CW
  subdivision** and cannot change γ_N (S3, audited); generator splitting is **monotone**
  (S8); change of variables is entirely **depth-1** (S1 Cor. F1); AC4/AC5 and the first
  slide over a fresh stabilizer are inert (S6 T4/T4′); and the one measurement suggesting
  certificates get commoner with rank was measuring **relator length** (S10, retracted after
  audit). Live remnants: **Q(F2)** — is `~^{(1)} = ~^{(k)}` for `k ≥ 2`? (level 1 is BLOCKED,
  it reduces to Panteleev–Ushakov); the **six certified γ_N = 1 gateways** among the 124
  unsolved MS classes (S9/S13 §3a), which are rank-2 targets; and the **split-bracket
  instrument** (S8 read forwards gives cheap γ_N upper bounds where the direct sampler is
  blind).

Route-selection rule: at least two live routes with incompatible mechanisms at all times;
a route that reduces stable ACC to another open problem is BLOCKED and written up.
