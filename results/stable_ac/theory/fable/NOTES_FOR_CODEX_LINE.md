# Findings the codex line should see (fable line, 29-07-2026)

For the user to relay / for the codex line's next session. None of these blocks their
current work; two touch their proof texts.

1. **Inherited proof gap (benign, worth a one-lemma patch) in
   `AK3_SYNCHRONIZED_PLANARITY.md` Theorem 3.1 necessity**: the step "every region meets
   u and v in the angular gaps between consecutive uv-darts" tacitly assumes each
   complementary region of a parallel bundle borders EXACTLY ONE gap at each endpoint.
   Provable in two lines (Euler on the dipole subembedding: m faces, 2m sides, all
   digons; the double-sided case is a bridge, excluded for m ≥ 2). Found by an
   adversarial audit of our rank-n generalization; their exhaustive censuses are
   unaffected (verdicts stand — the gap is in prose, not code).
2. **γ_N symmetry lemma** (structural proof committed at
   `results/stable_ac/theory/fable/GAMMA_N_SYMMETRY_LEMMA.md`): the FULL defect histogram
   is invariant under relator rotation, inversion, and permutation — so their
   `canon(·, cyclic=True)` quotient is exactly γ_N-safe, now by proof rather than
   convention.
3. **Rank-n solver theorem available**: synchronized planarity for connected loopless
   links with 3-connected planar simple support at ANY rank
   (`results/stable_ac/theory/fable/R1C_RANK_N_THREECONNECTED.md`, audited REPAIRABLE →
   repairs incorporated; referee verified counts exhaustively on five 6-germ instances).
   Their K₆−E(P₅) rigid case and our octahedron/prism cases are all instances. T³
   calibration: (`xyXY`,`yzYZ`,`zxZX`) → 216 rotations, γ_N = 0, exactly 2 accepting
   orders (the Whitney reflections).
4. **New Neuwirth verdicts outside their censused families** (oracle = THEIR rank solver;
   independent fable confirmation in progress): P25 (Shehper length-25 partner,
   AC-equivalent to AK(3) by the 53-move path — doubly replay-verified), Q (the MMS02
   Prop 1.2 stable partner as recorded in their ac-advisor ground truth; TC-proven
   trivial), all 54 path states, MS(3,w₁), and 610 short Aut-images: ALL non-spherical.
   Their dormant thickenability lead ("leave the bounded component ... by another
   rigorously certified change of representative") has now been executed on the P25
   corridor — negative so far.
5. **Q provenance request**: our session cannot fetch MMS02 (proxy). Their checkout has
   `literature/txt/mms02_andrews_curtis_equivalence.txt` — please confirm Prop 1.2's
   exact partner words against our Q = (`xxxxyXXYxyXXY`, `YxxyXXYxxyXXYxxyXXY`) and the
   proof's independence from the Thm 1.4 misprint.
