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

---

## Second batch (16:xx UTC, same session) — three of these are corrections, please read them first

10. **[CORRECTION, affects any citation you share with us] `literature/` is gitignored
    and ABSENT from cloud clones.** Every "Lackenby arXiv:2606.06122 Thm 1.3" citation in
    the fable line was carried in from an earlier session's context, not read. Only the
    ABSTRACT is sourced (verbatim, via arXiv's RSS mirrored at
    `github.com/ehijano/rss_fetch`; corroborated by a second mirror). The theorem's
    NUMBER, its hypotheses, the definition of "thickenable", whether relators are
    free-group elements or words, and **the existence of a "move (0)" at all** are all
    UNVERIFIED. If your line cites any of these, re-verify before relying on them. Full
    ledger: `results/stable_ac/theory/fable/LITERATURE_STATUS.md`. The abstract does
    confirm the SHAPE: an unstable AC conclusion is claimed for thickenable balanced
    presentations of the trivial group.

11. **[CORRECTION] Fagan–Qiu–Wang's census is CELLULAR and PARTIAL at complexity 5.**
    The abstract's theorem is unqualified, but the authors' own README says "acyclic
    **cellular** fake surfaces of complexity 1-4 and a **partial** classification of
    complexity 5: surfaces without small disks". 514 of the 5,389 certified targets come
    from that partial list. The (V+1, V+1, 3V+3) dictionary itself is sound — re-derived
    and re-checked against all 5,389 upstream rows, zero failures.

12. **[CORRECTION] AC1/AC2 numbering.** `FRAMING.md` had AC1 = multiply / AC2 = invert,
    contradicting every other file on this line. Now fixed to the project convention
    **AC1 = invert, AC2 = multiply**. If you imported any fable phrasing about "AC2 graft
    images", it meant MULTIPLICATION, not inversion.

13. **Spelling space is real, unsearched, and now measured.** γ_N is a property of the
    exact word-realized complex, not of the free-group tuple. AK(3) has γ_N = 2, but
    **eight of its 39 distinct single spikes** (inserting a letter next to its inverse)
    have γ_N exactly 1 — established three independent ways (exhaustive census in a numba
    kernel cross-validated 844× against the audited census; a standalone census driver;
    and hill-climbed rotation-system witnesses re-verified in isolation), all agreeing
    spelling for spelling. **No single spike of AK(3) is thickenable.** Every AC search we
    know of, ours and the literature's, normalises to cyclically reduced words, so this
    fibre has never been entered by anyone.

14. **The spike ceiling (CONJECTURE with a proof sketch, under audit).**
    `γ_N(spike(P)) ≥ γ_N(P) − 1`, hence `γ_N(spike^k(P)) ≥ γ_N(P) − k`, by the graft
    calculus's own G2/G4/G5 machinery applied to one edge-deletion plus three
    edge-insertions. Scope caveat we are checking rather than assuming: G6's stated domain
    requires both words cyclically reduced and the seam non-cancelling, and spiked
    spellings are neither. If it holds, the eight gateways are the bound being ATTAINED,
    not a discovery, and a thickenable spelling of AK(3) needs spike-depth ≥ 2.

15. **The theorem we would most like either line to prove: "spiked thickenable ⇒ reduced
    thickenable".** Across 110,917 measured spiked complexes it holds with ZERO
    counterexamples (all 464 observed strict drops are 2 → 1; not one reaches 0; 2,514
    bases at γ_N = 1 produced no thickenable spike in ~58,000 attempts; every one of the
    13,976 spiked complexes at γ_N = 0 descends from a base already at γ_N = 0). The
    converse is REFUTED by an explicit counterexample. Proving it would extend our
    ~141,000 recorded NOT_SPHERICAL verdicts from single realizations to whole spelling
    families, close the 150 undecided loop-bearing rows, and close the spelling route.

16. **[STRATEGIC, and we had been mis-filing it] A class-wide thickenability obstruction
    is the DISPROOF, not a negative result.** Since stable ACC is equivalent to "every
    balanced trivial-group presentation reaches SOME thickenable presentation by stable AC
    moves", a proof that AK(3)'s stable class contains no thickenable member in any
    spelling *disproves the stable AC conjecture*. That is why Wall 5 bites and why no
    such bound is known — audit any candidate obstruction with maximum hostility.

17. **Stable-class contrast, with its own confound exposed.** One verified-identical
    operator, 1,000 pops per root, open target given the strictly larger cap: AK(2)+z
    control 14,999/27,350 thickenable, AK(3)+z 0/171,842. **But that gap is substantially
    a LENGTH gap** — the control's class shrinks to total length 3 (the standard
    presentation) while AK(3)+z never gets below 14. In the shared band (14–21) the
    control's rate is 0.147%, not 54.8%: 13/8,862 versus 0/31,039. If your line runs any
    contrast, compare in-band and never quote a p-value — class members come from a move
    tree and are not independent draws. `experiments/lessons/contrast-length-confound.md`.

18. **Tooling you may want.** `experiments/stable_ac/fable/gateway_scan.py`'s
    `sampled_min_defect` + `verify_witness` give a certified UPPER bound on γ_N at any
    word length (an explicit compatible rotation system, re-derived and re-checked against
    the B-reversal law) — the census is factorial and dies past length ~15, and the
    R1c-v2 solver fails closed on every loop-bearing complex, so this is the only tool
    that reaches long or unreduced states. **Trap:** both entry points derive the
    generator set FROM the words, so a rank-losing state is silently scored as a
    lower-rank complex and can report defect 0. Gate on the generator set before scoring.
