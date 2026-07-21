# The obstruction barrier: why no abelian/quotient-type invariant can separate stable-AC classes

*ACSolverX theory note, 2026-07-21. Honest labeling up front: this is a rigor pass on standard folklore — no new mathematics. The contribution is stating the hierarchy precisely, tabulating exactly which named invariants die and why, and pinning where any real obstruction must live. Every non-trivial input is classical and cited. Companion to `STABLE_AC_NEW.tex`.*

## Setup

To a balanced presentation `P = ⟨x₁,…,xₙ | r₁,…,rₙ⟩` of the **trivial group** associate its presentation 2-complex `K_P` (one 0-cell, n 1-cells, n 2-cells; `χ(K_P) = 1`). `~st` is stable AC-equivalence (AC1–AC3 + AC4/AC5). Topologically, `~st` corresponds to **3-deformation** of the presentation complexes (Hog-Angeloni–Metzler–Sieradski, *Two-dimensional Homotopy and Combinatorial Group Theory*; move-level conversion also in Lackenby arXiv:2606.06122 §2).

## Proposition A (every such `K_P` is contractible) — standard

`π₁(K_P) = 1`; `H₁ = G^ab = 0`, and `χ = 1` with `H₁ = 0` forces `H₂ = 0`; a simply connected CW complex with vanishing reduced homology is weakly contractible (Hurewicz) hence contractible (Whitehead's theorem).

## Proposition B (the simple-homotopy layer collapses too) — classical

`Wh(1) = K₁(ℤ)/{±1} = 0`. Hence any homotopy equivalence between two such complexes has vanishing Whitehead torsion, i.e. is automatically a **simple** homotopy equivalence. Simple-homotopy type carries no information beyond homotopy type here — and by Proposition A the homotopy type is that of a point.

## Theorem C (the barrier)

Let `𝓘` be any invariant of finite 2-complexes invariant under homotopy equivalence — a fortiori under simple-homotopy equivalence. Then `𝓘` takes one and the same value (`𝓘(pt)`) on the complexes of ALL balanced presentations of the trivial group. No such invariant distinguishes two of them, let alone separates their `~st`-classes. *Proof: Proposition A.*

**What this kills, item by item:**

| invariant | value on every balanced trivial-group presentation | dies by |
|---|---|---|
| abelianization, `H_k(G)`, `H^k(G)` | 0 (G = 1) | trivially |
| exponent-sum matrix, `abs(det)` | unimodular, det = ±1 (checked 18,044/18,044 on the repo's data) | coker = H₁ = 0 |
| finite / nilpotent / pro-C quotient counts, `Hom(G, F)` | one point | G = 1 |
| normal closure `⟨⟨r₁,…,rₙ⟩⟩ ∩ F` | the whole free group | the `PROOFS.tex` sharpness Prop |
| `π₂(K_P)` as ℤ[G]-module, algebraic 2-type, chain-homotopy type | 0 / that of a point | Prop A (contractible ⇒ π₂ = 0) |
| Whitehead / Reidemeister torsion, simple-homotopy type | trivial | Prop B (Wh(1) = 0) |

The `π₂`-module / algebraic-2-type invariants are the subtlest entries — for general 2-complexes they genuinely separate homotopy types — but contractibility zeroes them here.

## The precise locus of any real obstruction

Coarse to fine: homotopy type ⊇ simple-homotopy type ⊇ 3-deformation type (⟷ `~st`). Proposition A collapses the first layer, Proposition B the second. The ONLY uncollapsed layer is 3-deformation type — and "are two balanced trivial-group presentations 3-deformation equivalent" is precisely the stable Andrews–Curtis question, OPEN (AK(3) stable triviality open; the generalized Andrews–Curtis conjecture for 3-deformations is exactly this gap).

**Conclusion.** Any invariant that could separate `~st`-classes of balanced trivial-group presentations must be a 3-deformation invariant strictly finer than simple-homotopy type on contractible 2-complexes. There is no coarser, more computable shadow retaining any information: every abelian, quotient, homological, `π₂`-module, or torsion-type candidate factors through a layer Propositions A–B annihilate. Search consequence for this project: do not spend effort on invariant-based pruning or invariant-based counterexample hunting at those layers; the decidable, genuinely 3-dimensional predicate available instead is thickenability (Lackenby; see `experiments/stable_ac/thickenable/NEUWIRTH_FEASIBILITY.md`).
