# A14 — Adversarial audit of S6 (move classification), S8 (splitting monotonicity) and S4 (cubic normal form)

Auditor task, branch `claude/stable-ac-conjecture-stabilization-rwo9as`
(**must be merged into `fable/proof` by the user**). Date 2026-08-04.
Targets are **not edited** by this file; every repair is written as an instruction for the
orchestrator to apply.

**Instruments.** All numbers below come from a from-scratch re-implementation of the
Neuwirth census (`scratchpad/aud.py`): my own link builder (germs, corner involution `A`,
occurrence involution `B`), my own compatible-rotation enumerator, my own
`defect = nA − nC + 2L − nAC`, my own free/cyclic reduction, and my own HLT Todd–Coxeter
(`scratchpad/tc.py`). Nothing is imported from `neuwirth_rank_n.py`, `coset_enum.py` or any
sweep script. The instrument was validated before use on three anchors it had to reproduce
blind:

| anchor | census | my defect histogram | repo value |
|---|---|---|---|
| `("xyXY","xxy")` | 12 | `{0:2, 2:6, 4:4}` | matches S6 §10 |
| `("xyXY","yYxxy")` | 144 | `{2:26, 4:94, 6:24}` | matches S6 §10 |
| AK(3) `("xyxYXY","xxxYYYY")` | 86,400 | `{4:724, 6:14882, 8:55438, 10:15356}` | matches S3 §5 R2 |

Todd–Coxeter validated on `⟨x,y\|x²,y³,(xy)⁵⟩ = 60`, `(xy)⁴ = 24`, `⟨x,y\|x³,y²,(xy)³⟩ = 12`,
`⟨x,y\|xyXY,x³,y³⟩ = 9`, AK(3) index 1.

---

## 0. Verdicts

| target | verdict | one-line reason |
|---|---|---|
| **S6 T1** (AC1 = homeomorphism) | **CONFIRMED** | proof correct; 0 deviations in my own re-census |
| **S6 T4** (AC4/AC5 = wedge on a disc) | **CONFIRMED** | the "no complementary face" worry is void: an embedded compact 1-complex is nowhere dense in `S²`, so `S² ∖ Λ` is always a nonempty open set — a triangulation of `S²` has open triangles, which is all the proof needs |
| **S6 T4′** (first slide over a fresh stabilizer = subdivision) | **CONFIRMED** | the degenerate (monogon) chord geometry does go through; checked separately, plus 72 bases including length‑1 relators, histogram-identical every time |
| **S6 T2** (single-generator AC3 = a spike) | **CONFIRMED** | `build_link_n` really is rotation-invariant (its corner involution wraps around); 110 rotations and 156 (conjugate, spike) pairs, 0 histogram mismatches |
| **S6 T0** (move (0) changes the space) | **CONFIRMED** | local-homology argument correct; both certificates reproduce |
| **S6 flip table** | **AMEND — three defects, one of them serious** | the rates do **not** survive the trivial-group restriction (§1.5); the `M0` row is the `M2nc` row re-partitioned, not an independent census (§1.3); the `M3` denominators are 14 pairs short (§1.4) |
| **S6 §8 headline collapse** | **AMEND (antecedent already refuted in-session)** | "stable ACC becomes a statement purely about AC2" is conditional on Conjecture SR, which `S11` (A10) refuted **on the trivial group**. S6 still records SR as `[OPEN]`, "0 counterexamples" |
| **S8 Conjecture + [GAP-S8-1]** | **AMEND — gaps dischargeable, conjecture survives** | the bookkeeping closes exactly (§2.1) and the sketch upgrades to a proof; 1,000+ new splits, none below base |
| **S8 [GAP-S8-2]** | **AMEND — the stated worry is vacuous** | the bigon's two link edges are `u⁻—g⁻` and `u⁺—g⁺`; they are **never** loops and are always vertex-disjoint; the degenerate "re-route every occurrence" split is fine |
| **S8 §4 headline negative** | **REFUTED by this session's own S4B** | "adding generators is worth nothing as long as they only re-describe the existing relators" is false: `C1` re-describes AK(3) and has `γ_N = 1 < 2` |
| **S4 Thm S4.1** (sign rigidity) | **CONFIRMED** | brute force over every cyclically reduced length-3 word at `N ≤ 4`: 0 violations |
| **S4 Prop S4.2** (`N ≤ 3` obstruction) | **CONFIRMED** | independent enumeration: 0 of 20 (`N=2`) and 0 of 1,816 (`N=3`) have `\|det\| = 1` |
| **S4 §4a census / Lemma S4.4** | see §3 | |

---

*(sections filled below)*
