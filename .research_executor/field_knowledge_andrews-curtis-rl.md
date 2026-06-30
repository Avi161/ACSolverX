# Field Knowledge — Andrews–Curtis trivialization via deep RL

*Persistent, goal-agnostic field cache for the ACSolverX codebase. Grounded in the
two local PDFs (*`literature/AC_Paper_for_ICML2026-2.pdf` *= "The Two-Hump Problem",
ICML 2026, this repo's own paper;* `literature/Math_ML_paper.pdf` *= Shehper et al.,
"What Makes Math Problems Hard for RL", arXiv 2408.15332) plus the classical AC /
combinatorial-group-theory and deep-RL-for-math literature. Reusable across any
future review in this field — contains NO reference to any specific active goal.*

Field detected: **Andrews–Curtis trivialization of balanced presentations of the
trivial group, attacked with deep reinforcement learning + classical search**
(combinatorial group theory ∩ deep RL for mathematical search).

---



## a. Field exemplars (who defines the field)

**Combinatorial group theory / Andrews–Curtis:**

- **J. J. Andrews & M. L. Curtis (1965)** — posed the AC conjecture: every balanced
presentation of the trivial group reduces to the trivial presentation by AC-moves
(relator inversion, multiplication, conjugation). The whole field's origin.
- **Selman Akbulut & Robion Kirby (1985)** — the AK(n) family of potential
counterexamples, tying AC to the smooth 4-D Poincaré / Schoenflies conjectures;
AK(3) is the canonical shortest open potential counterexample.
- **Charles Miller III & Paul Schupp (1999)** — the Miller–Schupp series MS(n,w), a
second large family of potential counterexamples; the standard RL benchmark family.
- **Martin Bridson (2015) & Boris Lishak (2017)** — proved that some AC-trivial
balanced presentations require trivialization sequences of length bounded below by a
*superexponential* (tower/Ackermann-type Δ) function of the presentation length —
the rigorous source of "length ≠ difficulty" and of astronomically deep paths.
- **Alexei Myasnikov, Alexei G. Myasnikov & Vladimir Shpilrain (2002), and Myasnikov
(1999)** — heuristic / genetic-algorithm search, Whitehead-style automorphism
methods, and the AK(n)↔MS(n,w) AC-equivalence; the prior-art "smart classical
search" tradition the RL work competes with.
- **George Havas & Colin Ramsay (2003); Bowman & McCaul (2006)** — exhaustive /
breadth-first enumeration; established that all balanced presentations of length
≤ 13 are either trivializable or AC-equivalent to AK(3) (the length-13 classification
the field still leans on).

**Deep RL / ML for mathematical search:**

- **John Schulman et al. (PPO, 2017; GAE, 2018)** — Proximal Policy Optimization, the
policy-gradient workhorse for sparse-reward, long-horizon mathematical search; the
RL algorithm of record in this subfield.
- **Andrew Ng, Daishi Harada & Stuart Russell (1999)** — potential-based reward
shaping; the policy-invariance theorem that licenses adding a learned heuristic to a
reward without changing the optimal policy.
- **Forest Agostinelli et al. (DeepCubeA, 2019)** — solved the Rubik's cube by learning
a cost-to-go heuristic (approximate value iteration) and using it in weighted A*/beam;
the closest "learn a distance-to-solved heuristic, then search with it" precedent,
and the cautionary contrast (Rubik scrambles from the solved state; the AC graph does
not admit useful scrambling).
- **Stanislas Polu & Ilya Sutskever (2020); Polu et al. (2023); Trinh et al.
(AlphaGeometry, 2024); Yang & Deng (2019)** — LLM / curriculum / proof-search lines
for theorem proving and olympiad math; the broader "RL/search for math" community
whose curriculum-learning lessons recur here.
- **Shehper, Medina-Mardones, Fagan, Lewandowski, Gruen, Qiu, Kucharski, Wang, Gukov
(2024) and the Two-Hump / ACSolverX authors (Fagan, Tarquini, Shehper, Manko, Gruen,
Huang, Butbaia, Passaro, Gukov, 2026)** — the two local papers; the people who framed
AC trivialization as a modern deep-RL benchmark, introduced substitution supermoves,
the Dual-Ring Transformer, the two-hump difficulty distribution, and the
topological/neighborhood hardness measures.

---



## b. Top papers (full citations + why each matters)

*Classical foundations and the two local PDFs are the load-bearing entries; ground
field-specific claims in these.*

1. **Andrews, J. J. & Curtis, M. L. (1965).** "Free groups and handlebodies."
  *Proc. Amer. Math. Soc.* 16(2):192–195. — States the AC conjecture and the three
   AC-moves; defines "AC-trivial" and "balanced presentation." The problem statement.
2. **Akbulut, S. & Kirby, R. (1985).** "A potential smooth counterexample in dimension
  4 to the Poincaré conjecture, the Schoenflies conjecture, and the Andrews–Curtis
   conjecture." *Topology* 24(4):375–390. — Introduces AK(n) = ⟨x,y | xyx=yxy,
   xⁿ=yⁿ⁺¹⟩. AK(1), AK(2) trivializable; AK(3) (length 13) is the famous shortest open
   case. Connects AC to 4-manifold topology — why solving it matters beyond group theory.
3. **Miller, C. F. & Schupp, P. E. (1999).** "Some presentations of the trivial group."
  *Contemp. Math.* 250:113–115. — The Miller–Schupp series MS(n,w)=⟨x,y | x⁻¹yⁿx=yⁿ⁺¹,
   x=w⟩ (w has x-exponent-sum 0). The benchmark family; AK(n) is AC-equivalent to
   MS(n, y⁻¹x⁻¹yxy).
4. **Bridson, M. R. (2015).** "The complexity of balanced presentations and the
  Andrews–Curtis conjecture." arXiv:1504.04187. — Superexponential lower bounds on
   trivialization length; the rigorous reason a *found* path length tells you almost
   nothing about a presentation's true distance and why naive depth-bounded search fails.
5. **Lishak, B. (2017).** "Balanced finite presentations of the trivial group."
  *J. Topology and Analysis* 9(2):363–378. — Explicit AC-trivial presentations whose
   trivialization length is bounded below by Δ(⌊log₂ k⌋) (Δ a tower function); e.g.
   Δ(13)=65536. The canonical "length ≠ difficulty, by a tower" result.
6. **Havas, G. & Ramsay, C. (2003).** "Breadth-first search and the Andrews–Curtis
  conjecture." *Int. J. Algebra and Computation* 13(1):61–68. — Exhaustive enumeration
   up to length 13; established the length-≤13 dichotomy (trivializable OR AC-equivalent
   to AK(3)). The classification the RL papers cite to interpret short-but-unsolved cases.
7. **Miasnikov, A. D. (1999).** "Genetic algorithms and the Andrews–Curtis conjecture."
  *Int. J. Algebra and Computation* 9(6):671–686. — Heuristic/evolutionary search; the
   prior-art "smart classical search" the RL methods must beat.
8. **Myasnikov, Myasnikov & Shpilrain (2002).** "On the Andrews–Curtis equivalence."
  *Contemp. Math.* 296:183–198. — AK(n)↔MS(n,w) AC-equivalence; Whitehead-automorphism
   reductions; the algebraic toolkit (and a known misprint later corrected by the
   companion paper) underlying the benchmark families.
9. **Schulman, J. et al. (2017).** "Proximal Policy Optimization Algorithms."
  arXiv:1707.06347. (+ **Schulman et al. (2016)**, GAE, arXiv:1506.02438.) — The RL
   algorithm both AC-RL papers use; clipped surrogate objective for stable updates in
   long-horizon sparse-reward settings.
10. **Ng, A., Harada, D. & Russell, S. (1999).** "Policy invariance under reward
  transformations: theory and application to reward shaping." *ICML*. — Potential-based
    shaping r' = r + γΦ(s') − Φ(s) leaves the optimal policy unchanged; the principled
    way to inject a learned heuristic into an RL reward without creating new fixed points.
11. **Agostinelli, F., McAleer, S., Shmakov, A. & Baldi, P. (2019).** "Solving the
  Rubik's cube with deep reinforcement learning and search." *Nature Machine
    Intelligence* 1(8):356–363. — Learns a cost-to-go (distance-to-solved) value via
    approximate value iteration, then searches with it (weighted A*/batch-greedy). The
    nearest precedent for "learn a distance heuristic, search with it"; also the
    cautionary contrast — Rubik admits scrambling from the goal, AC does not (scrambling
    the trivial presentation yields only easy or known-hard instances, no useful signal).
12. **Shehper, A., Medina-Mardones, A., Fagan, L., Lewandowski, B., Gruen, A., Qiu, Y.,
  Kucharski, P., Wang, Z. & Gukov, S. (2024).** "What makes math problems hard for
    reinforcement learning: a case study." arXiv:2408.15332 [= local
    `literature/Math_ML_paper.pdf`]. — PPO (ResNet, elementary AC-moves) solves 431/1190
    MS (T=200), all ⊂ greedy-solved; greedy 533, BFS 278. A **decoder-only Transformer**
    trained on 1.8M AC-equivalent presentations separates GS-solved vs GS-unsolved in
    embedding space (the binary-solvability "language" signal survives thousands of
    AC-moves). A **global hardness measure** = ℓ-increase = min length-increase over all
    trivializations = barcode of persistent reduced H₀ of the length-filtered based AC
    graph (giotto-TDA). **Local/topological hardness:** 5-step neighborhood sizes +
    barcode-vector features → XGBoost classifies PPO-solvability at **F1≈0.96** (length
    alone 0.885, neighborhood size 0.930, barcode vector 0.943). New math: length
    reduction of AK(n) to length n+11; AC-triviality of infinite MS subfamilies; two hard
    MS presentations solved by RL but not classical search (paths of length 195 and 381).
13. **Fagan, L., Tarquini, M., Shehper, A., Manko, M., Gruen, A., Huang, C., Butbaia, G.,
  Passaro, D. & Gukov, S. (2026).** "The Two-Hump Problem: Bridging the Difficulty Gap
    in Mathematical Reinforcement Learning." ICML 2026 [= local
    `literature/AC_Paper_for_ICML2026-2.pdf`]. — Identifies the **two-hump** difficulty
    distribution (easy/greedy-solvable + effectively-impossible, sparse valley between).
    Introduces **substitution supermoves** (S-moves; Ivanov 2018: substitutions realize
    all AC-transformations) as the right action space, and the **Dual-Ring Transformer**
    (cyclic relative-position self-attention per relator + cross-attention) which beats
    canonical-form preprocessing by ~25 solves. Releases **AC-19** (125,192 AC-trivial,
    length ≤19) and **AC-1M** (1,136,154 hard AC-trivial, length ≤30, generated by an
    automorphism generator–solver game). PPO-Sub-DRT solves 591 (→610 with AC-19/AC-1M);
    GS-Sub 640@1M nodes; hybrid beam (width 16,384) cuts mean path 13.77→12.39. Reduces
    the 550 unsolved MS to **261 distinct AC-equivalence classes** (the open hard set).
14. **Ivanov, S. (2018).** "On conjectures of Andrews and Curtis." *Proc. Amer. Math.
  Soc.* 146(6):2283–2298. — Substitutions suffice to realize all AC-transformations
    (assuming the conjecture); the theoretical license for using supermoves as the action
    space without losing completeness.
15. **Lyndon, R. C. & Schupp, P. E. (2001).** *Combinatorial Group Theory.* Springer. —
  Standard reference for free groups, Whitehead's algorithm (automorphic length
    minimization m(r)), cyclic words, and the machinery behind canonical forms.

---



## c. Field-standard pitfalls (specific failure modes, with source)



### Group-theory / AC traps

- **AK(n) local minima — the "second hump" / progress-violating moves.** Greedy
length-reduction stalls because escaping AK(3)-type basins *requires temporarily
increasing presentation length* (Two-Hump §2.1; companion §3.3). Any heuristic that
monotonically prefers shorter presentations is structurally unable to leave these
basins. Scrambling a known-hard presentation (e.g. AK(3)) only produces presentations
trapped in the *same* basin — no useful exploration signal (Two-Hump §3.1).
- **Length ≠ difficulty — by a tower function.** Bridson (2015) and Lishak (2017) prove
trivialization length can be superexponential (Δ-tower) in presentation length;
Δ(13)=65,536 for elementary AC-moves. A short presentation can be astronomically hard
(AK(3), length 13) and a longer one easy. Any feature set dominated by length silently
re-encodes the wrong signal (companion §8: length-only solvability F1=0.885, the floor).
- **A found path is only an UPPER bound on AC-distance.** Search returns *some*
trivializing sequence, never a proof of minimality. Treating an observed path length as
the true distance is a category error: the true distance may be far smaller (a shorter
path exists, unfound) and is provably unbounded above for hard cases. Every downstream
quantity derived from observed path length inherits this one-sided bias (Bridson/Lishak;
companion remark that greedy "does not necessarily find the shortest paths").
- **"Unsolved within budget" ≠ "non-trivializable."** A presentation unsolved by search
at budget B is *unsolved under that configuration*, not proven hard or a counterexample.
The companion paper is explicit (PU19: no AC-sequence with relator length ≤20
trivializes AK(3), yet this is "suggestive," not a proof). Over-claiming an unsolved
instance as a counterexample is the field's classic embarrassment risk.
- **Canonical-form / equivalence-class subtleties.** AC-triviality is invariant under
cyclic rotation of relators, relator inversion, and relator swap. A *canonical form*
must mod out all three to give one key per equivalence class. Pitfalls: (i) different
papers/codebases use different alphabet orders and different pair-orderings
(pure-lex vs length-then-lex) that produce the SAME equivalence classes but DIFFERENT
representative strings — mixing them silently misaligns labels; (ii) a per-move
normalization that rotates only the *one* relator just modified is **not** a canonical
form (no inverse-min, no pair-order) and must never be used as a cross-source key;
(iii) folding in generator automorphisms (x↔y, x↔x⁻¹) gives a coarser key — omitting
them is *safer* (a finer key never wrongly merges distinct states) but changes class
counts. (Two-Hump Appendix E; companion §2.)
- **Automorphisms can silently corrupt data.** Applying a non-invertible or wrong
"automorphism" to a trivial presentation can yield a presentation of a *non-trivial*
group, poisoning a dataset that is assumed all-trivial-by-construction. Automorphic
data generation (the AC-1M mechanism) must be gated by invertibility / abelianization /
trivial-group checks (Two-Hump §3.3, Appendix D). Note also automorphic images of an
easy presentation span a *range* of difficulties (Two-Hump Fig. 5) — they are not
uniformly hard.
- **Misprints and silent definitional drift in the source literature.** The companion
paper found a 20-year-old misprint in MMS02's Wirtinger presentation that undermined a
stable-AC-triviality claim. Re-derive from primaries; do not trust a transcribed
relator.



### ML / RL traps

- **Distribution shift when a learned heuristic steers search off-distribution (the
Caltech failure).** A value/heuristic trained on one method's trajectories, then used to
*guide* search, drives the search into states the model never saw and predicts blindly
there — the guided search can underperform the very baseline whose data trained it. Fix
pattern: train on a *mix* of trajectory sources that already contain the target
phenomenon; **DAgger**-style aggregation of the model's *own* on-policy visited states
each round; and an **uncertainty / OOD-abstention** output so search falls back to a
safe heuristic where the model is out-of-distribution. (Recurs across imitation-learning
literature; the prior AC value-guided attempt is the in-field instance.)
- **Constant fill-in for unsolved instances = false hardness.** Labeling every unsolved
instance with a fixed number (e.g. "200", "5×maxlen") tells the model a genuinely-hard
instance is *exactly as hard* as a mildly-hard one — a fabricated label that destroys the
hardness signal. Correct treatment: **right-censoring** ("distance > B" with full search
context: algorithm, node budget, horizon, beam width, action set, best length reached)
and a **one-sided (hinge/ordinal) loss** that penalizes only under-prediction.
- **Loose-upper-bound label contamination of every derived statistic.** If labels are
upper bounds (min over observed paths), then *any* statistic computed from them —
reweighting bands, "top-k% hardest," percentile-based thresholds, train/test
stratification — propagates the bias. The bias is *heteroscedastic*: heavily-visited /
central states get tight labels, rare / peripheral states get loose ones, so the model is
pushed to *under*-estimate difficulty exactly where difficulty matters most. Use
asymmetric losses (under-prediction penalized lighter), rank-based metrics (robust to
monotone label looseness), and self-tightening (min-aggregation as shorter paths appear).
- **Optimizing MAE when ranking is what the search consumes.** A heuristic is used to
*order* candidate states; absolute regression error is the wrong objective and the wrong
metric. Average MAE is dominated by the easy mass and hides whether the model is useful on
the hard tail. Report **Spearman / pairwise (sibling) ordering accuracy** and a
**downstream search test** (does ranking-by-f solve more at a *matched budget* than the
classical baseline?), calibrated *per difficulty band*.
- **Compute-asymmetry hidden by node-matched comparisons.** A learned heuristic that calls
a neural net per node can cost orders of magnitude more per node than a classical
length-compute. "Matched node budget" then flatters the learned method. The Two-Hump
paper's own automorphic-reward (Whitehead m(r), ~100× per-node) experiment was abandoned
for exactly this reason and yielded no extra solves under a fixed budget. Report
compute-matched (FLOPs / wall-clock), not only node-matched.
- **Naive reward substitution creates wrong fixed points.** Swapping a working terminal/
shaping reward for a learned-heuristic reward can introduce new optima the agent
converges to instead of the true goal. Use **potential-based shaping** (Ng et al. 1999),
Φ(s) = −(heuristic), which provably preserves the optimal policy — but note the
invariance theorem assumes Φ is *fixed*; alternating heuristic-updates with policy-updates
voids the per-update guarantee unless Φ is frozen within each policy-improvement phase.
- **Learned-value vs supervised-heuristic redundancy.** When a project already has a
learned value function (e.g. an RL critic = discounted cost-to-go), a newly-trained
supervised distance regressor that shares the same trunk may be *redundant* with it. The
honest baseline is the existing value head used directly as the search heuristic; the new
regressor must demonstrably beat it, or its marginal contribution is unproven. (A critic
trained under a length-shaped reward also partially encodes length — warm-starting from it
can re-import the very bias the project aims to remove; require a cold-vs-warm ablation.)
- **Eval sets too small / too correlated for conjecture targets.** The genuinely
interesting targets (named open counterexamples) are few and often from a single
structurally-correlated family. A hardness-recognition claim resting on a handful of
correlated instances has no statistical power. Use the *large* known-hard set (e.g. the
catalogued distinct hard equivalence classes) as the recognition eval, with the named
counterexample as an anchor — not as the whole eval.
- **Label leakage across equivalence classes / within paths.** Random row-level splits
leak: states of one trivialization path (≈ one move apart, near-duplicates) and
rotation/inverse/swap variants of one presentation land in both train and test, flattering
MAE. Split by **canonical equivalence class** (whole class in one fold); stride-subsample
and cap states per path to kill near-duplicate inflation.
- **PPO / deep-RL implementation sensitivity.** PPO results swing on advantage
normalization, value-loss clipping, KL-target early-stop, entropy coefficient, horizon
schedule, and network size (companion Appendix A; "37 Implementation Details of PPO").
Long-horizon credit assignment degrades and needs roughly linear-in-horizon extra
environment interactions (companion Fig. 10). Report seeds (min/max/mean over ≥5) — single
runs are not evidence.

---



## d. Field-expected verification checks (concrete sanity checks)

- **Replay-validate every path before trusting any label.** Re-apply each stored move
in a fresh environment and assert it reaches the trivial presentation in the claimed
number of steps. A label derived from an unvalidated path is worthless. (This is the
field's only real "unit test" — correctness of a trivialization is verified empirically
by replay, there is no analytic check.)
- **Canonicalize ALL sources through the SAME canonical form before joining.** Before
any cross-source merge / dedup / min-aggregation, route every presentation (raw
benchmark int8, env state, RL/beam path states) through one canonicalizer (rotation +
inverse + swap modded out, fixed alphabet order, fixed pair-order). Verify on a sample
that the three sources produce the *same* key for the same mathematical presentation
(round-trip test). Never key on a per-move partial normalization.
- **Action-space consistency gate.** The action that defines "one step" in the label
archive, the neighbor relation used to enumerate siblings, and the search's "one node
expansion" must be the *identical* move with identical encoding. (Action-packing
formulas duplicated across files are a known silent-corruption source — a mismatch
miscalibrates a distance-heuristic without erroring.) Assert equality on a sample.
- **Distance-as-class-invariant empirical check.** If labels are aggregated per
equivalence class, the distance must actually be a class invariant under the action
space. Verify empirically: replay from ≥2 distinct canonical representatives of the same
class and confirm identical min-distance. (It holds when the action space is
rotation/inverse/swap-equivariant *and* any length cap is length-based, since those
symmetries preserve the relator-length multiset — but this is load-bearing, so check it.)
- **Split by canonical class, not by row; verify zero key-overlap across folds.** Assert
no canonical key appears in two folds; assert byte-identical splits under a fixed seed
(determinism). For any frozen hold-out, assert its keys never enter training — *including*
through any data-aggregation/DAgger loop (filter the harvest by held-out canon keys and
test it).
- **Report ranking, not just MAE.** Spearman correlation and pairwise sibling-ordering
accuracy are the metrics that predict search quality; report them per difficulty band,
not as a single average dominated by easy cases. For a search heuristic, the decisive
test is downstream: solves-at-matched-budget vs the classical baseline.
- **Censored loss penalizes only under-prediction.** Verify the unsolved-instance loss is
one-sided (zero penalty for predicting ≥ the asserted floor B); verify B carries its full
search context and that no unsolved instance received a fabricated point label.
- **Report new-solves separately from path-shortening.** "Solved a previously-unsolved
instance" and "found a shorter path to an already-solved instance" are different claims
with different scientific weight; never aggregate them into one "improvement" number.
- **Seeds and compute disclosure.** Report min/max/mean over ≥5 seeds for any RL result;
report per-node compute and total compute (FLOPs / wall-clock) alongside node counts so a
learned heuristic's per-node cost is visible.
- **A discovered hard instance is a *candidate*, pending proof.** Any newly-surfaced
"hard basin" or "new counterexample" is unsolved-within-budget until proven otherwise;
corroborate across *multiple independent search algorithms* and runs (a local minimum
seen only by the heuristic being evaluated may be that heuristic's artifact, not a real
attractor) before claiming it as a hard class.

---



## e. Exemplar artifacts to emulate

- **DeepCubeA (Agostinelli et al. 2019) — "learn cost-to-go, then search with it."**
Borrow: the architecture of a learned distance-to-goal heuristic feeding weighted A* /
batch-greedy, with the heuristic trained by approximate value iteration. Borrow the
*discipline* of reporting solution-length distributions and node-expansion budgets. Note
the disanalogy explicitly (Rubik admits goal-scrambling for free training data; AC does
not) so the method is adapted, not copied.
- **The companion paper's topological/local hardness pipeline (Shehper et al. 2024,
§7–8).** Borrow: the persistent-H₀ barcode of the length-filtered based graph as a
*principled, transferable* hardness invariant (giotto-TDA), and the XGBoost-on-barcode +
neighborhood-size feature study with SHAP attribution (F1≈0.96 vs length-only 0.885) as
the template for "is this signal real and what carries it." Reuse its honesty about
"unsolved within budget ≠ hard" and its t-SNE separation evidence for a learnable
solvability invariant.
- **The Two-Hump paper's evaluation rigor (Fagan et al. 2026, Tables 1/4, Fig. 7–8,
Appendix I).** Borrow: report solve-count as min/max/mean over 5 seeds; report path-length
*distributions* (not just means) and break out PPO-vs-greedy on the subset solved by both;
give the classical baseline at *multiple* node budgets (614 / 10K / 100K / 1M / 10M) so a
learned method is compared at the right operating point; release minimal representatives of
the hard equivalence classes as a concrete, checkable benchmark. The released code/datasets
(AC-19, AC-1M, the 261-class catalogue) are the reproducibility bar to match.

