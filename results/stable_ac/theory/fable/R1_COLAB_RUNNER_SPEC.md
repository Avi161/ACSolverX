# R1 production runner spec (Colab tier — for the user; fable line, 29-07-2026)

Production budgets are the user's, on Colab. This spec parameterizes the committed fable
modules into three runs, per the notebook lessons (3-cell CONFIG/SETUP/RUN pattern,
TIME-based heartbeat — 60 s in-search beat + ~5 min cumulative line — and the
Restart → Run All contract; results jsonl on local disk with whole-file Drive mirror;
resume identity in the filename stem; no dates in resume keys).

## Run A — deep harvest (extends R1d beyond the local round)

- Roots: the 32 path states (indices 0–31) + every novel state from the local round;
  ITERATIVE re-rooting allowed on this tier (novel states become roots), rounds until no
  novel state appears (report a plateau, never a wall).
- Budget: 20,000 pops/root (sweep-check smaller budgets by prefix — a search at B is the
  first B pops of any longer run); per-relator cap: sweep 15 → 20 → 25 (the cap is
  structural: raising it exposes states unreachable at ANY budget below it — report per
  cap, never pooled).
- Every distinct state: canonical key (rotation × inversion × swap), support class,
  E-score; γ_N-test all supported classes (K₄/K₄−e/C₄ + P₄/one-loop/paw when ported +
  rank-n 3-connected when implemented); factorial fallback ≤ 5·10⁶ rotations; UNSUPPORTED
  counted separately.
- Row schema: exact words, reduced words + reduction flag, canonical key, root chain
  (move path to AK(3) — the membership certificate), support + multiplicities, E,
  verdict, counters/witness. Any YES: verify witness in-notebook AND persist immediately
  (a computed result reaches disk before anything else is attempted — heavy-mode lesson).
- Resume: jsonl keyed by canonical key; unique-row-count progress (never line count).

## Run A′ — the AK(2) control (added after the local control experiment)

Identical harvest machinery rooted at AK(2) = (`xxYYY`,`xyxYXY`) (trivial, provably
AC-trivial class), run until cumulative ΣE ≫ 1. Purpose: end-to-end validation that the
pipeline finds hits at the E rate in a class where hits are legitimate. Interpretation
matrix: AK(2) hits at ~E rate + AK(3) zero at matched ΣE ⇒ genuine class-level phenomenon
(R3′ target); both at ~E rate ⇒ the hunt is a pure scale problem; both zero at ΣE ≫ 1 ⇒
suspect the model or the solver (cross-check with Run B). Local round 1 (1,000 pops):
1,251 canonical members, all NOT_SPHERICAL.
SEARCH-PRIORITY NOTE for Run A and A′: best-first by E-DESCENDING (not length) — E
rewards concentrated corner distributions; length-ascending under-samples the high-E tail.

## Run B — false-NO alarm control at scale

Random cyclically-reduced pairs at total lengths {17, 21, 25, 29} with supports in the
decided classes, ≥ 250k pairs per length tier: record predicted E and observed YES rate;
verify every YES witness. Zero hits at a tier where ΣE ≫ 1 = solver alarm — STOP and
report, do not continue harvesting with a suspect solver.

## Run C — rank-3 sweeps (after R1c implementation lands)

Targets in priority order: (1) z-stabilized variants of the 54 path states and P25
(z⁻¹w insertions per the CoV family enumeration, applied at rank 3 WITHOUT immediate
destabilization); (2) MMS3(w) members for short w with exponent-sum ±1 — each row FIRST
gets a TC triviality certificate (the family contains non-trivial groups, e.g. an
SL(2,5) member; a γ_N = 0 on a non-trivial-group row proves nothing); (3) the B₃-route
3-generator elimination stages (R1B doc). Supports outside 3-connected+factorial scope
are counted UNSUPPORTED pending P/S-node schemes.

## Ceilings to respect in all runs

A YES anywhere transfers to AK(3) ONLY through a verified membership chain (classical
chain ⇒ AC-trivial; stable chain ⇒ stably AC-trivial; say which). All-negative outcomes
are bounded negatives about tested realizations at tested caps/budgets — the route
ceiling (R1 succeeds iff AK(3) is (stably) AC-trivial) means a negative sweep never
becomes evidence about AK(3) itself.

## Run C amendments (after rank-3 round 1, 09:10 UTC)

Round-1 facts: the canonical-key move closures of AK3+z (5,075 states) and P25+z (93) are
CLOSED and contain zero 3-connected-planar supports (z-germ degree<3 or 2-cuts
everywhere); 25 small-census states all min genus 2; no spherical state. Amendments:
1. Per-relator cap for rank-3 roots grown from length-25 states: >= 26 (cap 15 freezes
   P25+z after 93 pops).
2. The seen-set canonical key makes all AC3 (conjugation) children duplicates — the
   rotation freedom is never explored. Round 2 keeps the canonical seen-set but must
   expand from EVERY new exact realization (exact-word frontier, canonical dedup for
   counting only), or add explicit relator-rotation moves.
3. Plain stabilization (r1, r2, "z") has a structurally disconnected link; grow z into
   other relators (AC1 with the z-relator) before any support test — a z-entangling move
   bias is REQUIRED, not an optimization.
4. Until the R1c-v2 cut-scheme solver lands, rank-3 decisions come only from the
   factorial fallback (cap 2e6; only ~1% of round-1 states) — budget accordingly or wait
   for v2.

## Amendment 3 (14:21 UTC) — Run D: the matched-operator contrast at scale (TOP PRIORITY)

The local 1,000-pop matched contrast (ak2_battery.py / ak3_matched_control.py, results
committed) ended at AK(3) ΣE 5.03 with 0 observed vs AK(2) 649/397 — p between 0.7%
and 5%. Run D scales EXACTLY this pair of harvests with the rotation-expanded operator
(operator identity member-by-member, as the committed modules already verify):
AK(2) and AK(3), same pops (start 100k), caps root+4, decisions via the committed
solver stack, two-sided ΣE accounting per the lesson. Interpretation: AK(3) hits ⇒ hit
protocol (witness + TC + full replay; Lackenby-flagged chain to AC-triviality); zero
at ΣE ≳ 300 ⇒ phenomenon-level evidence that AK(3)'s classical class contains no
thickenable members in reach — R3′'s concrete target. Run D supersedes Run B's priority.

## Amendment 4 (15:45 UTC) — Run E: meet-in-the-middle at ranks 4-6 (NEW, top priority with Run D)

Instruments committed: `certified_targets.py` (5,389 certified stably-AC-trivial
targets from the FQW fake-surface census, validated in-session), `target_meet.py`
(backward closure + corpus intersection), `gateway_scan.py` (gamma_hat priority).

Established locally: the detector fires on both positive controls and scales with depth
(AK(2) classical 46 -> 276, AK(2)+z stable 72 -> 1,543 from depth 1 to depth 2) while
AK(3) stays at 0 on both the classical and the stable side. And the binding constraint
is now identified: AC1/AC2/AC3 preserve rank, no census target is destabilisable (0 of
5,389), so only the 19 rank-2 and rank-3 targets were ever eligible against our
corpora. The other 5,370 sit at ranks 4-6.

Run E therefore:
1. Forward harvests from AK(3) with 2, 3 and 4 plain stabilisations (ranks 4, 5, 6),
   rotation-expanded operator, caps root+4, at Colab scale (100k+ pops each).
   Rank 6 is the headline: stabilised AK(3) has 6 generators and total length 17; the
   514 complexity-5 targets have 6 generators and total length 18.
2. Backward closure of ALL 5,389 targets to depth 2-3 with the state cap raised well
   above 400k (depth 2 truncated there locally), matching per rank.
3. Forward priority by gamma_hat ascending (gateway_scan), not by length or E.
4. Interpretation: any AK(3)-side match => AK(3) is stably AC-equivalent to a certified
   stably-trivial presentation => AK(3) STABLY AC-TRIVIAL (the session's headline
   sub-goal), subject to the hit protocol (explicit AC1-AC5 move list + full replay +
   TC certificate) and to the flags recorded in R6 (FQW full text unverified; the
   relabelling match leans on the stable ambient automorphism theorem). Zero matches at
   this scale, with both controls firing, is the strongest negative the route can give.
