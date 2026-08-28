# Fable lane lessons

## 2026-08-28

### Grep the hypothesis before building the instrument

[TRAP] W1 built a complete finite-orbit decision procedure whose refutation
branch was mathematically unreachable: with the base rows killed, both
kill-word images normally generate the image (both triples present the
trivial group), and a 5-line chain then forces connectivity in ANY group.
The repo's `cited-theorem-hypothesis-never-fires` lesson, violated verbatim
— the hypothesis an obstruction needs (distinct normal closures) fires on
0 of 180 A5 homs.

[WORKS] Before designing any invariant-based test, compute the invariant's
value on both endpoints BY HAND first (here: normal closure = everything on
both sides, 2 minutes), and only build machinery if they can differ.

### Check for decidability theorems before running decision computations

[TRAP] The A5/S5/PSL(2,7)/A6 sweeps re-derived, group by group, a corollary
of Borovik–Lubotzky–Myasnikov 2005 Thm 1.1 (finite AC-graph components =
abelianization preimages), which settles every finite group at once and was
citable in the first hour.

[WORKS] For any "does this finite structure obstruct" question, do the
literature pass FIRST and treat computation as validation of the cited
theorem, not as the source of truth.

### A positive control must be able to fail

[TRAP] W1's control (certified-trivial triple's image orbit contains the
trivializer) was itself forced by the same vacuity, so it could not have
detected a wrong move model.

[WORKS] Pair every positive control with an adversarial control — a
deliberately broken variant (e.g. a move set missing `mult`) asserted to
FAIL — before reading any result.

### Block on the advisor gate, don't race it

[TRAP] The W1 checker was implemented, run, and committed while the
ac-advisor review was still in flight; the review returned BLOCK and the
committed note needed a retraction pass.

[WORKS] For each new workstream: write the plan, get the advisor verdict,
reconcile, then implement. Concurrency is for independent derivation and
literature agents, not for the gate itself.

### Secondary literature on AK(3) stable status is actively wrong

[TRAP] 2025–26 print (Lisitsa arXiv:2501.18601 abstract; arXiv:2607.23611)
asserts AK(3) is stably AC-trivial; the claim delegates to the MMS02 chain
voided by the misprint found in Shehper et al. arXiv:2408.15332 v2 App. F.

[WORKS] AK(3) stable AC status is OPEN. Cite Shehper et al. for the
misprint; trust the repo's own `ac-advisor.md` record over search-engine
summaries; verify any "settled" claim against the primary chain.

### A descending greedy profile can be a disguised self-loop

[TRAP] The Tpub preflight's 29 -> 14 descent was pitched as making a
production run "genuinely promising"; Tietze-collapsing the floor state and
aut_canon-ing the result showed the floor IS AK(3) itself (plus one z
letter) — the search had looped back to the original problem.

[WORKS] Before selling any descent profile on a stabilized/transformed
start, eliminate the auxiliary generator at the floor state and aut_canon
the residue; if it lands in the source orbit, the descent is a self-loop
and the route's difficulty equals the source's.

### Ask what a SUCCESSFUL separation would prove, before hunting invariants

[TRAP] W5 opened as "find an invariant separating the MMS02 bridge triples".
A five-lemma reduction (basis change + z-elimination + the certified rank-2
replays) then showed the bridge is EQUIVALENT to "AK(3) is AC-trivial after
exactly one stabilization" — so any separating invariant is a partial negative
resolution of the headline open problem. The hunt was never a shortcut, and
every null it produces is the expected behaviour of a cheap invariant on a hard
question, not evidence.

[WORKS] Before building an invariant battery, spend the first hour reducing
the two endpoints to canonical form. If the reduction lands on a known open
statement, say so and re-aim; if a probe then *does* separate, treat it as a
red flag on the probe, not as a discovery.

### A constructive connectivity method needs its positive control at every parameter

[TRAP] The free-nilpotent chain construction succeeded at class 2, failed at
class 3 with row-local gadgets, and fails at class 4 today. Each failure looks
like "the quotient might separate the bridge" and is nothing of the kind: the
certified-AC-trivial triple's own control failed in exactly the same runs, i.e.
the gadget pool was too small. Class 3 was fixed by adding a cross-row
`transfer` gadget (row-local corrections span only rank 6 of the 8-dimensional
degree-3 Lie layer).

[WORKS] Run the positive control at EVERY parameter value, and have the
checker withhold the verdict automatically when the control fails, rather than
printing a null the reader has to discount by hand.

### A dead stratum in a truncated support is a statement about the truncation

[TRAP] W2f found five parameter strata (32 of 67 chains) with ZERO one-hop
solvable windows mod 3 or mod 5 — read as candidate module obstructions. W2g
then proved the opposite on the whole finite-index part: the full-module image
is exactly ker(eps) (`d = 1`), every window is solvable over Z, and explicit
integral corrections exist at 27 windows the sweep called dead at every prime.
The one-hop restriction (corrections supported near the defect) was the killer,
not the module. Before reading any truncated-search null as an obstruction,
state the truncation as a hypothesis and test the un-truncated question in a
quotient where it is decidable — here one Stallings fold + a finite double-coset
computation settled in milliseconds what 5,427 window solves could not.

### Pin the base coset before trusting any coset-table invariant

[TRAP] W2g's first release computed every trace from the wrong coset: union-find
re-rooted the base class during folding, `find(0) != 0`, and the generators of
Gamma no longer traced to the base state — producing 3 spurious `d = 2` chains
and a failed constructive lift, while all controls stayed green because none
checked the algebraic fiat directly. The catch came from replacing an inert
mutation control (asserting a quantity the code excluded by construction) with
an EFFECTIVE one: assert the omega-rows of the L2..L4 columns vanish
identically (the fiat, made checkable) and that a corrupted operator breaks the
vanishing. A control must assert the load-bearing step itself, not a shadow of
it; and any union-find under a distinguished base point must pin that base's
root explicitly.

### A solution verified through the operators that produced it is not verified

[TRAP] W2b–W2i all check a layer-1 solution by recomputing `D + Σ L_i x_i`
with the same `L_i` that built the system. That is an identity, not a test:
`build_operators_general`'s `L0` column omits a `q(h1)` factor (the exact
variation of `S` conjugates `δ_R` by `S·q(h1)`, not by `S`), so on the 59 of
67 census chains with `q(h1) ≠ 1` a "VERIFIED layer-1 solution" is not a
solution at all — and every control in five notes stayed green. The codex
witness has `H1 = ()`, which is exactly why the original certificate is right
and the generalisation is not: the bug lives in the coordinate the reference
case sets to zero.

[WORKS] Verify a solution in the object the equation is about, not in the
linearisation. Here: put `n_r = σ(x_r)`, replay the literal recurrence in
`F(c,t)`, and assert the residual lands in `[N,N]`. 354 mismatches over 2,010
probes, all in column 0, and the corrected operator matches 2,010/2,010. When
a derived calculus generalises a worked example, probe every column against
the ground truth on a case where the example's special value (`h1 = 1`,
`g = 1`, `k = 0`) is NOT taken.

### A wrong operator is not uniformly wrong — find the column the theorem leans on

[TRAP] The `L0` defect looked fatal to five notes at once. It was fatal to
exactly one of them. W2f's liveness sweep is a computation *about* `L0`, so
every number moved (live chains 21 → 31, three of five "dead strata"
refuted); W2g's `d = 1`, W2h's coverage and W2i's `d₂ = 1` all reduce to the
`L1` column — `bridge·(B − S)`, which contains no `h1` — and to identities
(`L2 = 1 − U⁻¹R`, `L3 + L4 = U⁻¹ − 1`, `X, U, w ∈ Γ`) that no perturbation of
`L0` can reach. Suspending all five was right; assuming all five were wrong
would have been as sloppy as the original bug.

[WORKS] When a shared input is found defective, do not re-run everything and
compare totals. Ask, per claim, *which column carries it*, and compute that
directly: `--mode dsource` split `d` into its `L0` and `L1` contributions and
showed `L1` alone gives gcd 1 on 44/44 chains — turning "the number came out
the same" into "the theorem could not have been affected". The `L0` rows moved
on 24 of those 44 and vanish identically on some, so the immunity is a real
fact about the proof, not a coincidence about the data.

[WORKS] Corollary for the repair itself: re-derive **every** column, not the
one you already suspect, and widen the probe set before declaring the others
clean. W2j proved `L0` wrong and columns 1–4 clean on six probe vertices; the
repair re-derived all five from the variation and re-probed on the whole
radius-4 ball (20 vertices, 6,700 checks, 67 chains) before saying so.

### Periodicity is not linearity — check the polarisation before planning

[TRAP] W2j proved `G(n) mod 2` depends only on `n mod 2` for a degree-≤2
integer-coefficient map (`2·quadratic + linear shifts` are even), and the
next plan read that as "mod 2 the map is affine-LINEAR, so mod-2
attainability is GF(2) linear algebra on `ker(L) mod 2`". It is not:
`n_j² = n_j` over `F₂` absorbs only the DIAGONAL coefficient; the
polarisations `b_jk` survive and were odd on 979 of 1,047 measured cross
pairs. The decision problem is a system of `F₂`-quadratic forms, and the
planned method does not exist.

[WORKS] Before building on "the map is linear mod q", measure the
polarisation directly on literal evaluations — `Φ(e_j+e_k) − Φ(e_j) − Φ(e_k)
+ Φ(0)` — on real data, by a code path that does not go through the fitted
model, and count how many pairs are odd. It costs one evaluation per pair.

### A bounded non-attainability is never an obstruction, at ANY modulus

[TRAP] The instinct that "a failure mod `p^k` is window-independent" is
backwards for an attainability question. Enlarging the direction set can only
enlarge the value set, so "no solution mod `p^k` on `S`" says nothing about
`S ∪ {F}` — exactly the same monotonicity that makes W2f's dead strata a
statement about the truncation. The only finite computation that transfers is
the *membership* `−c₀ ∈ V_S` (the linear relaxation): it is monotone in `S`,
so a YES kills every linear certificate on the whole family at once.

[WORKS] And check whether that useful branch can fire before spending the
budget. Here `rank V_S ≤ m + m(m−1)/2 + m` while the coordinate universe grows
at least as fast, so `−c₀ ∈ V_S` is a measure-zero coincidence at every rank
reachable — the finite computation is one-sided in precisely the direction
that cannot fire, and no amount of enlarging `S` changes that. Say so instead
of shipping 51 "unattainable on S" lines as if they accumulated.

### Report a diagnostic only after testing that it is basis-independent

[TRAP] The Hamming weight and support of `−c₀` reduced modulo the variation
space looked like a canonical invariant: on one baseline the SAME 11
coordinates survived as the space's rank grew 9 → 119 across three direction
families. Re-running the elimination on the reversed generator list — which
re-indexes every coordinate — showed the reduced representative is
order-dependent on 17 of 35 baselines. Only the boolean membership is an
invariant.

[WORKS] Any quantity computed by an elimination should be recomputed under a
permuted input before it is named in a note; make that a control (it can
fail, and it did).
