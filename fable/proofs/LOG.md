# Fable lane log

## 2026-08-28 · cycle 1 (setup)

Lane created on branch `fable/proofs`. Charter in `PROGRAM.md`. W1 selected as the
opening workstream: finite AC-graph decision for the MMS02 bridge — decisive in both
outcomes, complete-closure (not budgeted-search) methodology, and disjoint from the
codex class-two tower. Opus agents launched: plan review (ac-advisor), independent
derivation of the A5 data, and a known-results sweep on AC-graphs of finite groups.
No AK(3), stable AC, or AC claim is made.

## 2026-08-28 · cycle 1 · `1e8d86b`

W1 first theorem: complete A5 closure proves the A5 obstruction blind for the full
bridge (all 6 nontrivial hom classes connect; surjective orbits are all of A5^3 minus
the frozen identity tuple; controls green). Note: `W1_BRIDGE_FINITE_TEST.md`. Next:
generator-reduced move set, larger quotients (W1b), and rank-3 greedy preflight on
Tpub within the 1,000-node cap.

## 2026-08-28 · cycle 2 · `6a9a257`

ac-advisor BLOCK on W1 sustained and repaired: the finite test was theorem-forced
(vacuity lemma; BLM 2005). W1 closed as a method-closure result with full retraction
of the earlier inferences; five lessons recorded; W3 repointed at the Lackenby
thickenability lever (thickenable => unstable AC-trivializable), pending its own
advisor gate. No AK(3), stable AC, or AC claim.

## 2026-08-28 · cycle 3 · `f7a696d`

Composed the MMS02 corridor with the mu/orbit machinery (own idea): mu(Q)=21 (new
orbit), Tpub floor state proved a disguised AK(3) self-loop (W1c downgraded), and a
second elimination yields a new mu=14 stable rep. All basins drain to the 13-floor.
Note: W4_CORRIDOR_REPS.md. No AK(3), stable AC, or AC claim.

## 2026-08-28 · cycle 4 · `975a5ba`

W2 census: the period-two backward system has 17 essential gauge-free solutions at
caps (12,12,12,g5) — the witness plus 16 others, all hyperbolic-S, independently
verified. Quantifies the uniqueness gap: the codex anchored family (1.10) covers one
of 17. Next: layer-1 liveness per extra baseline (W2b). Note:
W2_PERIOD_TWO_BASELINE_CENSUS.md. No AK(3), stable AC, or AC claim.

## 2026-08-28 · cycle 5 · `1b982fe`

W2b liveness sweep: six of the 17 baselines are live at the relation-module layer
(witness + 5; four share the witness R,S). Eleven inconclusive, zero dead. The
gauge-representative dependence of one-hop windows was caught by the witness control
and absorbed into the method. Note: W2B_BASELINE_LIVENESS.md.

## 2026-08-28 · cycle 6 · `6f72ee0`

W2c cap curve: 17 -> 36 -> 55 -> 67 essential baselines at caps 12-15, strictly
growing. With W2b (6 live at cap 12), the period-two route needs a uniform argument;
per-baseline towers cannot terminate. Addendum in W2_PERIOD_TWO_BASELINE_CENSUS.md.

## 2026-08-28 · cycle 7 · `cbe0d8c`

W3a: independent component probe cross-validates the certified ceiling-17 closure
(1,000 states exactly) and proves ceiling 18 exceeds the local pop law (>=1,243).
Colab handoff recorded. Note: W3A_COMPONENT_CEILING.md.

## 2026-08-28 · cycle 8 · `bb29a0e`

W3b orbit sweep: all 1,508 AK(3) μ-ladder orbits × 8 signed relabels decided —
12,064/12,064, of which 12,016 NOT_SPHERICAL and 48 UNSUPPORTED (6 orbits, none
mixed). Zero SPHERICAL verdicts, so the Pipeline-B tripwire never fired. The orbit
representatives are now a first-class artifact, reproducing every count the committed
ladder summary holds. Bounded null: 8 relabels are not the Aut(F₂)-orbit, and only a
validated positive decides. Note: W3B_ORBIT_THICKENABILITY.md. No AK(3), stable AC, or
AC claim.

## 2026-08-28 · cycle 9 · `1721718`

W2d uniform structure: the growing period-two baseline family collapses to a
six-parameter normal form. Each step `NEW = P·(conj of Q^-1)` obeys
`|NEW| = |P| + |cyc Q^-1| + 2k - 2d`, so a length cap PINS the conjugator to a
literal prefix of `P^-1` — one lemma at all three levels, indexing a chain by three
prefix lengths, three rotation indices and a terminal conjugator. New checker
`period_two_normal_form.py` runs it as a generator against the census enumeration:
exact at caps 12–17 (17/36/55/67/91/106, 0 missed, 0 spurious), with a non-vacuity
control that asserts strict pinning at cap 19 where it must fail (64 census R, 32
pinned, 32 missed). Also: the U-fiber depends on S only through `cyc(S)` (proved from
the verifier's conditions), so 17 chains are 9 invariant triples and one of W2b's six
live baselines is the witness's own class at a different S representative; the R-count
is exponential, not linear. Note: `W2D_UNIFORM_STRUCTURE_DRAFT.md` (DRAFT; only the
normal form is checker-backed). Limits: nothing claimed past cap 18, GPAD ceiling 5
under-counts, pinning lemma unproved. No AK(3), stable AC, or AC claim.

## 2026-08-28 · cycle 10 · `4fa1440`

W2e liveness class-invariance: REFUTED at the window level, with the obstruction
proved. The 17 cap-12 chains form 12 `(R, cyc S, U)` classes (five of size 2, all the
same conjugation `gamma = Tctt` across the witness U-fiber). On exactly balanced,
centralizer-indexed gauge-aligned windows, 161/405 strict window pairs mismatch —
one member's GF(p) system solvable, the other's not — hard counterexamples, robust at
K=2 and under a second gamma. Theory: closed forms for L0..L4 show the alignment
right-multiplies only part of L0/L1 while fixing L2, so no right-unit intertwiner of
the relation module exists; obstruction terms E0, E1 exhibited and nonzero on all five
pairs. Chain-level (∃-window) invariance stays open (NOT-LIVE inconclusive by W2b
doctrine). Consequence: W2D's hoped 106→31 class reduction is unavailable at layer 1;
a uniform argument must be uniform in the pinned `(k2, p2)` representative parameters
under the §4.1 transformation law. Checker `period_two_liveness_invariance.py`
(controls mutation-verified, exit 2 on control failure) independently reproduces
W2b's six live chains. Note: W2E_LIVENESS_CLASS_INVARIANCE.md. No AK(3), stable AC,
or AC claim.

## 2026-08-28 · cycle 11 · `19ee7dd`

W5 (open-exploration lane, non-base-killing regime): the MMS02 bridge is proved
EQUIVALENT to "AK(3) is AC-trivial after exactly one stabilization" (Theorem
W5.1, four machine-checked lemmas: Aut-invariance via Nielsen, the two basis
changes, literal AC2 z-elimination, and the recorded rank-2 endpoints Q and P;
Q ~AC AK(3) re-verified with the existing 53-move Appendix-F checker). Corollary:
any invariant separating the two bridge triples is a partial negative resolution
of the open stable-AC question for AK(3) — the invariant hunt is not a shortcut.
Battery: abelianization blind (11-op chain exhibited); Fox/Alexander over
Z[F3^ab] blind by theorem (junk ideal = augmentation ideal), "det J up to units"
refuted by its own certified-positive control, cyclic Alexander Δ = t^4-3t^3+
5t^2-3t+1 identical on both sides; free nilpotent class 2 and class 3 blind by
explicit verified chains (47 and 991 moves), class 4 verdict withheld (positive
control fails). Zero states popped anywhere. Notes: W5_BRIDGE_INVARIANTS.md;
checkers bridge_reduction.py, bridge_invariant_probe.py, nilpotent_bridge_chain.py,
w5_words.py, w5_linalg.py. Two lessons appended. No AK(3), stable AC, AC, or
bridge claim.

## 2026-08-28 · cycle 12 · `270c1de`

W2f: layer-1 one-hop solvability computed as an explicit function of the
six-parameter normal form, for all 67 census chains at caps 12–15 over the
centralizer-indexed window family (5,427 fully-decided windows at K=1, per
prime). Live fractions (mod 2,3,5): 6/17, 16/36, 19/55, 21/67 — stable-to-
falling, so layer-1 liveness is NOT generic; W2b's six cap-12 live chains
reproduced chain for chain on the rebuilt window family. Uniform facts: mod-5
solvability implies mod-2 and mod-3 at every one of the 5,427 windows, and the
chain verdict equals the mod-5 verdict at every cap. No subset of the seven
parameter coordinates of size ≤ 4 determines liveness. Five exact dead strata
(union 32 of 67 chains, no live member) have ZERO windows solvable mod 3 or
mod 5 — largest is g ∉ {"", "TTc"} (22 chains), which survives K=2 on a
7-chain sample (2,625 windows, 0 at every prime) and alternative terminal
conjugators deduped by w = g t g⁻¹. Mechanism attempt NEGATIVE: the t-exponent
abelianization M → Z[x,x⁻¹] is inert (solvable at all 2,106 windows tested),
ruling out W2D (d.3)'s candidate. Latent W2e defect found and fixed: ball(10)
conjugator search silently returns None on 15/67 chains at cap 15 (would have
read never-tested as dead); replaced by a closed-form free-product conjugator,
controlled byte-identical against the ball wherever both exist — W2e's
committed cap-12 results unaffected. Note: W2F_PARAMETRIC_SOLVABILITY.md;
checker period_two_parametric_solvability.py. Next decisive question recorded
in §8: does a non-abelian quotient of Q kill the g-stratum (its parameter
enters only through L3/L4, the operators W2e proves representative-stable).
No AK(3), stable AC, or AC claim.

## 2026-08-28 · cycle 13 · `11e57cd`

W6 rank-3 feasibility: the Neuwirth/Lackenby route is rank-general on the repo's
records (theory gate open, with the arxiv-egress caveat recorded and Theorem 2's
connected-link hypothesis tracked). Lemma W6.1 (z-row splitting, proved +
numerically confirmed): a bare z row is thickenability-inert — gamma_N(r1,r2,z) =
gamma_N(r1,r2) exactly — so W5.1's (3)-(4) as spelled ARE the rank-2 question and
the genuinely new object is Tpub alone. Targets: (AK3,z) NOT thickenable (exact
gamma_N = 2, 86,400 orderings enumerated); (Q1,Q2,z) NOT thickenable (splitting +
certified K4-e negative); Tpub UNDECIDED (connected, planar, kappa = 2, 4 spherical
rotations, outside every certified family). Rank-3 AC ball from (AK3,z) closes at
ceilings 16/18/20 with 17/125/503 canonical states (exceeds the pop law at 22);
zero states in certified families at 20, zero non-planar link graphs anywhere, 24
K6-E(P5) states at 22 all NOT_SPHERICAL. Zero positives; quarantine doctrine
holds. Checker rank3_link_graph.py, 29 controls green. Next: build the missing
certified family (2-connected planar 6-germ, four macro rotations, P4-style
shifts) with certified-AC-trivial Txy as its free positive control. Note:
W6_RANK3_FEASIBILITY.md. No AK(3), stable AC, AC, or thickenability-positive claim.

## 2026-08-28 · cycle 14 · `3dc0d61`

W2g: W2F §8's death-certificate hunt REVERSED into a liveness theorem. Exact
operator identities give L2M+L3M+L4M = I_Γ·M (Γ = <R,U,w>, telescoping), so
M/(L2+L3+L4)M ≅ Z[Ω] with Ω = Γ\Q/<c> — a double-coset character no finite
quotient of Q can see (W2F §8's own route executed over 221 finite quotients:
blind, only the augmentation survives). Stallings folding: [Q:Γ] = 4 on 44/67
census chains, ∞ on 23. On all 44 the image of L0M+L1M in Z[Ω] is exactly
ker ε (d = 1): EVERY window is layer-1 solvable over Z — every k, every K,
every prime — covering 15/22 g-stratum chains. W2f's zero-mod-3/5 strata are
one-hop support-truncation artifacts on that part, confirmed constructively by
27 explicit verified integral corrections at windows the sweep calls dead at
all primes. 7 infinite-index stratum chains stay open. Review caught a real
defect pre-commit: union-find re-rooted the base coset during folding (3
spurious d = 2 chains, failed lift); fixed by pinning the base root, and
caught by replacing an inert mutation control with an effective vanishing
control (Ω-rows of L2..L4 identically zero; corruption breaks it). W2F gains
§6.5 post-hoc correction; two lessons filed. Verdict:
NO_DEATH_CERTIFICATE_AND_PROVABLY_LIVE on the finite-index part. Consequence
for the program: layer 1 of the period-two quotient obstructs NOTHING on the
finite-index part — the scope gap moves to layer 2 ([N,N]) or to the
infinite-index chains. Note: W2G_G_STRATUM_DEATH.md; checker
g_stratum_death.py. No AK(3), stable AC, or AC claim.

## 2026-08-28 · cycle 15 · `ef08153`

W6b: the missing certified family from W6 is built, proved, and decides Tpub.
Lemma A (bundle arcs cut S^2 into m regions) + Lemma B (decoupling, proved
outright: bundles in book form with pinned reversal alignment whenever H minus
each multi-bundle's endpoints stays connected — strictly weaker than the
3-connectivity the K6-E(P5) argument needed) + Lemma C (P4 shifts, for repo
agreement). Tpub: 2.0858e16 orderings collapse to 3,120 cases, all consumed,
0 spherical — gamma_N >= 1, NOT thickenable for this exact spelling (link
connected, so Theorem 2 is an equivalence there). Txy control NOT_SPHERICAL,
doctrine-consistent. Validation: 0 disagreements vs complete brute force on
344 instances including AK(3) (86,400 orderings) and 71 truncated instances in
Tpub's own macro structure with both verdicts present; both pinned P4
decisions reproduced; 153 PASS / 0 FAIL controls; zero quarantine events on
real targets. Ball coverage: 902/2,513 rank-3 AC-ball states decided, all
NOT_SPHERICAL. The W5.1 positive route is now closed for the three recorded
spellings AND Tpub; the target moves to AC-reachable respellings (cut family
next: unblocks 898 of 1,204 undecided ceiling-22 states). Note:
W6B_TPUB_DECISION.md; checker rank3_shift_family_solver.py. No AK(3), stable
AC, AC, or thickenability-positive claim.

## 2026-08-28 · cycle 16 · `2f81a0a`

W6c: the cut family is proved and implemented (Lemma G piece contraction,
Lemma H cut decoupling — verified as a SET identity against directly
enumerated rotation systems — Lemma I book contraction with a declared
fail-closed budget, Lemma F generalised bare-row splitting). Validation 279
checks / 0 failures; K4-e degeneracy in the strong form; 7 corruption
controls each move a verdict; W6b delegation verdict-identical, 0 decisions
lost. +1,027 ball states decided, all NOT_SPHERICAL; ceilings 16 and 18 are
COMPLETE (17/17, 125/125): no thickenable state anywhere in the closed
rank-3 AC ball around (AK3,z) at ceilings <= 18 for the declared move set —
a clean bounded null. Ceiling 20: 479/503; ceiling 22: 1,691/1,868. Zero
quarantine events on real targets. Residual: shared-vertex multi-cut (58 at
c22, 4 at c20) is the next family; remaining buckets are closure-size
limited. Note: W6C_CUT_FAMILY.md; checker rank3_cut_family_solver.py. No
AK(3), stable AC, AC, or thickenability-positive claim.

## 2026-08-28 · cycle 17 · `848a054`

W2h: layer 1 of the period-two quotient is obstruction-free for the ENTIRE
census — d = 1 on all 23 infinite-index chains (Stallings core + exact Cayley-
tree cones, Lemma 5 column collapse, integer Hermite membership), so with W2g
all 67 baselines are layer-1 live; explicit verified corrections on 22/23.
Honest asymmetry: the infinite-index all-window claim is EVIDENCED by an exact
margin law (depth = L − μ, exact 19/23 over four L values), not proved — the
(k2,k3) closure has no infinite-index analogue. Controls: 25,460 identity
checks / 0 mismatches, 38,190 vanishing rows / 0 failures, corruptions fire
67/67, finite specialization reproduces W2g 44/44, synthetic positive fires
23/23. Consequence: the dead-baseline escape hatch is closed for every
baseline; a per-baseline layer-2 tower cannot terminate; the codex route's
survival question moves to d2 — the same double-coset invariant on Λ²M (same
five operators diagonally, same Γ), where signed 2-torsion could carry the
first genuine obstruction, at exactly the prime (p = 2) layer 1 found
permissive. The WIP checkpoint d39f105 is superseded by this reviewed state.
Note: W2H_INFINITE_INDEX_LIVENESS.md; checker infinite_index_liveness.py.
No AK(3), stable AC, or AC claim.

## 2026-08-28 · cycle 18 · `8db0718`

W2i: the layer-2 fork resolves to BLINDNESS-WITH-STRUCTURE. Γ = <R,U,w> is
torsion-free on 67/67 chains, so Λ²M's coinvariants are free — W2h's predicted
2-torsion at p = 2 is identically absent, for a reason independent of the
operators. Lemma 6 block-diagonalizes pair orbits over displacement classes
(layer 2 = layer 1 one level finer, on Γ\Q); d₂ = 1 on 1,936 sampled blocks and
at every displacement class of all 44 finite-index chains by the z-free
reduction (Lemma 7); the operator image exactly fills ker Ξ_Z, upgrading the
source's (3.17) surjection to an isomorphism Ξ_Z: C₂ ≅ W_Q. Consequence:
Ξ_Z(Θ(F)) = 0 is necessary AND sufficient for the layer-2 equation (3.8) —
the entire layer-2 question is the affine-quadratic residual class Θ, nothing
else; a linear obstruction cannot exist. Two corrections to W2h recorded
(hypotheses of the Λ²M identification; the unreachable "d₂ = 1 ⇒ blind"
framing), W2H gains a post-hoc correction section. Controls: 73,968 vanishing
rows / 0, 49,312 Ξ rows / 0, 16,080 Γ-invariance / 0 with fold-found
witnesses, corruptions fire 67/67, Λ¹ specialization reproduces W2g 44/44,
synthetic fires 1,056/1,056, torsion path fired on the deliberate Γ' control
(268/268 verified swap witnesses). Next: evaluate Ξ_Z(Θ(F)) beyond the codex
witness — now the whole layer-2 question. Note: W2I_LAYER2_D2.md; checker
layer2_d2_invariant.py. No AK(3), stable AC, or AC claim.

## 2026-08-28 · cycle 19 · `ea3da2a`

W2j: the literal Θ evaluator reproduces the codex escape certificate exactly
(all four parity classes, bit for bit) and evaluates Ξ_Z(Θ) across the census:
nonzero on 55/55 chains with exact layer-1 solutions, affine-quadratic
confirmed, and 0 unattainable on every tested sublattice (window-bounded; the
constant-parity route to a window-independent obstruction is closed by data —
parity is non-constant on 24/24 families). CRITICAL FINDING UNDERNEATH: the
lane's build_operators_general has a wrong L0 column on 59/67 chains (missing
q(h1) factor; the exact variation conjugates δ_R by S·q(h1)) — it coincides
with truth exactly at the codex witness (H1 = ()), where every prior control
was anchored. Literal probes: 354/2,010 mismatches, all column 0; corrected
operator 2,010/2,010. Consequence: W2b/W2e/W2f/W2g/W2h/W2i layer-1 and d₂
claims that ran through L0 on the 59 h1-nontrivial chains are SUSPENDED
pending re-derivation (cycle 20); operator-independent results stand (census,
normal form, Γ structure, torsion-freeness, W3/W5/W6 lanes). Lesson filed: a
solution verified through the operators that produced it is not verified.
Note: W2J_THETA_RESIDUAL.md; checker theta_residual_evaluator.py. No AK(3),
stable AC, or AC claim.
