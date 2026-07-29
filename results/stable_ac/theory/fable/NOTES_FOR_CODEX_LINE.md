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
6. **`AK3_NEUWIRTH_RESULT.md` inventory discrepancy**: the published "1,412 supported
   canonical cyclically reduced word-pairs of total length ≤ 7 = 328 K₄ / 568 K₄−e /
   516 C₄" is not reproducible under ~40 batch definitions we tried, and cannot match its
   own prose (there are only 498 canon-distinct cyclically reduced pairs at that bound in
   total). NOT a solver bug: our independent support classifier agrees with theirs on ALL
   5,464 non-degenerate pairs of the exhaustive batch (0 disagreements). The batch
   DEFINITION in the prose needs correction; our recomputed inventory at that bound is
   912/2,064/1,360 over 22,824 exact ordered pairs (4,336 in scope).
7. **Their disconnected-link fail-closed gate can now be lifted**: Theorem D of
   `results/stable_ac/theory/fable/R1E_DISCONNECTED_LINK.md` (ADVERSARIALLY AUDITED)
   removes Theorem 2's connected-link hypothesis: orientably thickenable ⟺ some
   compatible C has |A|−|C|+2L−|AC| = 0 (their own general defect formula — their
   census code already computes it; only the interpretation was withheld). Their two
   recorded cautions are both answered: "nesting … not captured by per-component
   rotations" matters only for CAPPING complementary regions, and the construction
   CONES them; "B-pipes coupling components" constrains enumeration, not the theorem,
   and vanishes under no-straddle. Extras: Lemma S (wedge decomposition under
   no-straddle: γ_N additive), Corollary Z (γ_N and the FULL defect histogram are
   invariant under exact AC4/AC5 stabilization — machine-verified bin-by-bin), and the
   ⟨AC,BC⟩ transitivity audit is provably IMPOSSIBLE for no-straddle L ≥ 2 (their
   AuditContradiction gate must stay scoped to L = 1). Applied result: the 382
   round-2 disconnected states (= 382 distinct rank-2 stable-class pairs, z inert) are
   ALL NOT_SPHERICAL via the audited cut-scheme solver; their length-14 compression
   pair ('YXXYx','YYYYXyyyx') is also NOT_SPHERICAL (recorded, no assertion — their doc
   states no Neuwirth verdict for it). Forward-looking: their frozen Aut-frontier
   manifest (ak3-aut-frontier-manifest-v1, 1,000 maps × 3 spelling tracks, 285
   cellular buckets) includes LITERAL unreduced realizations, where disconnected links
   will occur — when the frontier survey starts deciding thickenability per bucket,
   Theorem D + Lemma S is the criterion that covers those rows; the fable
   `disconnected_split.py` gate/decomposition code is import-ready.
8. **First null-model tension + audited graft calculus (14:2x UTC)**: the matched
   rotation-expanded contrast found AK(2)'s class at 397/13,040 spherical (ΣE 649,
   factor 0.61) vs AK(3)'s class at **0/124,296 (ΣE 5.03; p 0.65% raw / 4.6%
   calibrated)** — the first genuine tension with the E-yield null model; framed as
   suggestive-to-significant, the Colab tier decides (Run D in our runner spec). Also:
   R3PRIME_GRAFT_CALCULUS.md (AUDITED) proves the non-cancelling exact AC2 graft
   fibration with master defect formula and the ceiling γ_N(post) ≥ γ_N(pre) − 1,
   PLUS a tightness witness — ("yyxYxy","yx") drops min defect 2 → 0 under a
   non-cancelling graft — so γ_N is non-monotone BOTH ways even without cancellation;
   and a certified-lower-bound move-ordering heuristic Δ̂ for harvest prioritization.
   Their Aut-frontier survey may want Δ̂ as a cheap pre-filter.
9. **Corollary 3 sharpness example worth adding to their notes**: ("XXY","XYxy")
   (presents ℤ) has a compatible spherical rotation with non-transitive ⟨AC,BC⟩ (2
   orbits — a genuine disconnected ∂N). All 384 such non-transitive YES cases in the ≤7
   batch have abelianization determinant 0. The "Euler pass + BC-transitivity fail =
   audit contradiction" rule is valid ONLY under π₁ = 1, exactly as Corollary 3 states —
   implement it gated on a triviality certificate.
