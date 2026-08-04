# S-line: high-rank stabilization — session plan (fable line, branch `claude/stable-ac-conjecture-stabilization-rwo9as`)

Started 2026-08-04 06:31 UTC. Branch must be merged into `fable/proof` by the user.
Standing frame: `FRAMING.md` (statements, traps, what does NOT count). This file adds the
S-line: **what arbitrarily many stabilizations buy**, which is the question this session
was opened on.

## 0. The question

Earlier fable work lived at rank 2 and rank 3. The open question this session attacks:

> Does a hard presentation (AK(3); the 124 unsolved MS AC-classes `aca_0..aca_123` of
> `data/ms_unsolved_reps/aca_124.csv`, of which `aca_115` **is** AK(3)) become tractable
> once the rank is allowed to grow well past 3 — say to 9 or 10 generators?

and, the prize version,

> Is there a *uniform* mechanism that trivializes ANY balanced presentation of 1 once
> enough stabilizations are allowed? (That would prove the stable AC conjecture.)

## 1. The mechanism this session is built on

Write P = ⟨x₁..xₙ | r₁..rₙ⟩, balanced, presenting the **trivial** group.

**(S-a) The free-definition move.** After AC4 adjoins (z, z), the relator `z` may be
replaced by `z·w` for **any** w ∈ F(x₁..xₙ). Reason: the group is trivial, so
w ∈ ⟪r₁..rₙ⟫, i.e. w = Π uⱼ r_{iⱼ}^{εⱼ} uⱼ⁻¹, and each factor is applied by
AC3 (conjugate r_{iⱼ} by uⱼ) + AC2 (multiply into z) + AC3 (conjugate back). The chain
is long but stable AC-equivalence does not count moves. **The triviality hypothesis is
sharp** — this is trap 2 of `FRAMING.md`, restated at rank n.

So a stabilized generator may be *defined* to equal any word: `z = w`. That is the
"change of variables" idea in its stable form, and it is the engine of everything below.

**(S-b) Triangulation.** Apply (S-a) with w = (a₁a₂)⁻¹ where a₁a₂ is the length-2 prefix
of a relator rᵢ = a₁a₂a₃…a_m of length m ≥ 4. The new relator is `z a₂⁻¹a₁⁻¹` (length 3)
and the product move rᵢ ← (z a₂⁻¹a₁⁻¹)·rᵢ shortens rᵢ to `z a₃…a_m` (length m−1).
Iterating m−3 times per relator:

> **Triangulation Lemma (to be proven and audited — task A1).** Every balanced
> presentation P of the trivial group, rank n, total length L, is stably AC-equivalent —
> using only AC4 and AC1–AC3, **never a destabilization**, at terminal rank
> N = n + Σᵢ max(0, |rᵢ|−3) — to a balanced presentation P_Δ of the trivial group in
> which **every relator has length ≤ 3**.

For AK(3) = ⟨x,y | xyx(yxy)⁻¹, x³y⁻⁴⟩: |r₁| = 6, |r₂| = 7, so N = 2 + 3 + 4 = **9**.
Nine generators, nine relators, each of length three. The user's "maybe 10 generators"
lands exactly on the triangulation rank of AK(3).

## 2. Why high rank might be *easier*, not harder — the enabling observation

Thickenability (Neuwirth) is decided by a census over compatible rotation systems whose
size is ≈ Π_germs (deg−1)!. For a triangular presentation the link graph has 2N germs
and 3N edges, i.e. **average germ degree exactly 3** — independent of N. At rank 2 with
AK(3)'s length 13 the germ degrees are ~6.5 and the census explodes; at rank 9 with all
relators of length 3 the census is ~2^{2N} ≈ 10⁵ and the exact γ_N is *cheap*.

> **More stabilization shortens relators, which thins the link graph, which makes the
> decidable thickenability test cheaper — the opposite of the usual rank-vs-cost
> tradeoff.** This is the reason the S-line is worth running.

## 3. The payoff chain

1. P_Δ is balanced and presents the trivial group (Tietze).
2. If P_Δ (or any member of the family of triangulations / their Aut(F_N) images /
   their bounded AC-neighbourhoods) is **thickenable**, then by Lackenby Thm 1.3
   [status: UNVERIFIED, see `LITERATURE_STATUS.md` — task A2 must settle it] P_Δ is
   AC-trivializable at rank N.
3. AC-trivializable at rank N + (P ~st P_Δ) ⇒ **P is stably AC-trivial**.

For P = AK(3) that is the named huge result of `FRAMING.md` §2. For the 124 MS classes
it would be a large sweep of open cases.

Failure mode, respected in advance: every triangulation of AK(3) is non-thickenable ⇒
bounded negative, written up, and the *shape* of the negative (a γ_N floor that survives
rank growth) is itself the first evidence about the rank filtration.

## 4. The rank filtration — the second, incompatible route

Define P ~^{(k)} Q iff some AC1–AC5 chain joins them without the rank ever exceeding
n+k. Stable ACC is ∪ₖ ~^{(k)}. Questions this session states precisely and attacks:

- **F1.** Is ~^{(1)} already the full Aut(Fₙ)-orbit closure? (The rank-n stable ambient
  automorphism principle: one stabilization per Nielsen move, then destabilize — task A1
  corollary. This says a *lot* of "change of variables" costs only ONE extra generator.)
- **F2.** Is the filtration strict? A γ_N-style quantity that is monotone in k would be
  the first invariant sensitive to *how much* stabilization is used.
- **F3.** The prize: is there k(n, L) such that every balanced presentation of 1 is
  ~^{(k)} standard? A uniform construction proves stable ACC.

Route-selection rule (FRAMING §6) is kept: §3 (positive, thickenability at high rank)
and §4/F2 (negative, a rank-monotone obstruction) are incompatible mechanisms and both
stay live.

## 5. Traps specific to this line (added to FRAMING's list)

- T-S1. **Triangulation is not a homotopy-invariance argument.** P_Δ is 3-deformation
  equivalent to P but NOT homeomorphic to it; thickenability is *not* a homotopy
  invariant, so nothing may be inferred about P_Δ from P or vice versa. That is exactly
  why the test is informative — and exactly why "K_P is non-thickenable so K_{P_Δ} is"
  is a fallacy.
- T-S2. **Direction of the bound.** A construction that exhibits a thickenable member
  bounds the obstruction from ABOVE. Silence from a search bounds nothing (lessons:
  `parallel-runs-and-bound-direction.md`, `calibrate-one-sided-hunts-on-a-positive-ladder.md`).
  Every null in this session must come with a measured detection rate on a positive
  ladder before it is read.
- T-S3. **Every high-rank member must carry a replayed certificate** that it really is
  in the stable class: the AC4/AC1–AC3 chain, machine-replayed from P, not asserted by
  the generator that produced it.
- T-S4. Relators of length < 3 make the rank-n Neuwirth solver return UNSUPPORTED, and
  germs of degree < 3 break its 3-connectivity fast path. The exact census
  `gamma_N_factorial_n` is the right tool at high rank; the fast path is not.
- T-S5. The (S-a) chain is exponentially long in elementary moves (FRAMING trap 6,
  "Lemma 11 / Lackenby (4⁺)"). Never quote a move count across this construction.

## 6. Task board

| id | task | kind |
|---|---|---|
| A1 | Prove the Triangulation Lemma + the rank-n stable ambient automorphism principle (F1) | theory |
| A2 | Literature: Lackenby Thm 1.3; identify "Lemma 11"; is triangular normal form / bounded-stabilization hierarchy known? | verification |
| A3 | `triangulate.py` — the transform, the choice family, and a **replay certifier** | build |
| A4 | Exact γ_N over the triangulation family; positive ladder first (AC-trivial controls), then AK(3), then the 124 | compute |
| A5 | Adversarial audit of A1 and of every claim built on A3/A4 | audit |
