# AK(3) research promise ledger

This ledger prevents a bounded engineering failure or a context switch from
silently abandoning a mathematically live route. A route leaves this file only
after a verified proof closes it or an exact theorem refutes its stated
mechanism. Search exhaustion, timeout, storage pressure, and failure to find a
finite quotient do not close a route.

## 1. MMS02 rank-three donor factorization — active

- **Priority:** highest-value active theory route to stable AK(3).
- **Exact target:** with `Tpub=(A,B,Xyz)` and
  `Txy=(A,B,zYX)`, prove `Txy ~AC Tpub` by rank-three AC1--AC3 moves, or
  directly AC-trivialize `Tpub`. The verified corridor makes this sufficient
  for stable AK(3), not ordinary AK(3).
- **Current reduction:** with `r=xyxZXY`, `q=Xy`, `v=Xyz`, the target is an
  exact donor-indexed factorization from `(r,q,v)` to `(A,B,v)`. The full
  factorization is equivalent to the open bridge, not an auxiliary theorem.
- **Verified-plan first legs:** S1 has eight current-donor conjugate factors
  taking `(r,q,v)` to `(A,q,v)`; S2 has two current-donor factors taking
  `(r,q,v)` to `(r,B,v)`. These are separate branches.
- **Verified checkpoint:** the canonical 28,419-byte donor certificate has
  SHA-256 `829f89a191cfe9cfeb1c86d194c1ec3e29a05941277206c1c091ab0152bfbbff`.
  Independent replay verifies the separate 9-action triangular transcript,
  the S1/S2 8/2-macro branches, all 49 primitive actions, donor restoration,
  and exact branch endpoints. The two reduced second-stage gates are
  `Q_A=<x,y | xYxYXyyXYxyXy>` with defect `YXyyXYxyxY`, and
  `Q_B=<x,y | XyyXYXyxYYxy>` with defect `YxYXyxYYxyXyyyXY`.
- **Gate A closed negatively:** exact Magnus rewriting makes `Q_A` an
  ascending HNN extension of a free rank-two base. After shifting the defect
  into that base it freely reduces to
  `ba^-1ba^-1b^-1ab^-2`, so `delta_D != 1` in `Q_A`. This refutes only the
  S1 sequential completion.
- **Gate B closed negatively:** after the Nielsen change `a=xY,t=y`, exact
  Magnus rewriting again gives an ascending HNN extension of a free rank-two
  base. The shifted defect freely reduces to the nonempty 13-letter word in
  Equation (28) of the two-gate note, so `delta_K != 1` in `Q_B`. This refutes
  only the S2 sequential completion.
- **Quotient ceiling proved:** in `G_-=<x,y,z | A,B>`, the two kill words
  `zYX` and `Xyz` are normal generators. A general one-buffer transfer lemma
  proves `(1,zYX) ~AC (1,Xyz)` inside `G_-`. Therefore no finite,
  Alexander, metabelian, or other quotient invariant of the image triple can
  obstruct the unrestricted all-row path. The remaining gate is the literal
  relation-identity lift through `normal_closure(A,B)`.
- **Lift concentrated to two residuals:** the quotient transfer can use only
  the first and third rows, leaving `B` literally fixed, or only the second
  and third rows, leaving `A` literally fixed. A lift therefore ends in
  `(E_A,B,V_A)` or `(A,E_B,V_B)`, with exactly one base residual in
  `normal_closure(A,B)` and one relative kill-word residual. No third residual
  is required.
- **Two residuals now have finite symbolic SLP certificates:** the 134-primitive
  `Txy` replay gives a literal conjugate-product `H` in `zYX` with
  `H*(Xyz)^-1` in `normal_closure(A,B)`. The 53-move published corridor plus
  the AK3 normal-closure certificate gives a literal conjugate-product `K` in
  `Xyz` with `(zYX)^-1*K^-1` in the same normal closure. Build--kill--swap
  therefore reaches `(E_A,B,H_A)` or `(A,E_B,H_B)` with both displayed
  residuals certified in `normal_closure(A,B)`. Four focused checks pass.
  The endpoint substitutions and donor-restoring macros are not flattened by
  the checker; finiteness follows by structural induction on the SLP.
- **Closure reduced to two named word problems:** restoring the active base
  residual first makes the kill-word residual automatic. Both branches have
  the same defect `d=(zYX)H`: test `d=1` in `<x,y,z | B,AH>` or in
  `<x,y,z | A,BH>`. A positive factorization in either quotient proves the
  bridge; a negative result closes only its named branch.
- **Both restoration-first gates are false:** weighted Fox rows over
  `Z[t,t^-1]` put the common defect outside the relator row span for both
  `<x,y,z | B,AH>` and `<x,y,z | A,BH>`. The first fails by Laurent-span
  degree and the second by a pinned nonzero long-division remainder. This
  closes only base-first cleanup; interleaved Peiffer cleanup remains open.
- **Sequential cleanup ledger frozen:** A kill-first fails at
  `H_A*(Xyz)^-1 in Ncl(E_A,B)`; its second gate passes only the necessary
  Alexander filter. B kill-first fails at
  `E_B*B^-1 in Ncl(A,Xyz)`, so its first gate is unnecessary. Together with
  the two restoration-first failures, every ordering that restores each
  residual exactly once is closed. Do not add more sequential categories;
  only genuinely interleaved Peiffer cleanup remains.
- **Common-kill target normalization:** the signed involution
  `phi(x,y,z)=(Z,Y,X)` exchanges `zYX` and `Xyz`. Applying it to the
  certified 134-primitive trivialization proves
  `(phi(A),phi(B),Xyz) ~AC (x,y,z)`. Hence the unrestricted bridge is
  equivalently `(A,B,Xyz) ~AC (phi(A),phi(B),Xyz)`. This is not a fixed-kill
  path and does not reopen the frozen sequential ledger; it gives an exact
  alternative target with the published kill row already literal.
- **Ambient-automorphism-only common-kill route closed:** after killing
  `Xyz`, the source and common-kill target base pairs have exact rank-two
  Whitehead floors 21 and 19. They are not in the same ambient Aut orbit.
  Thus no stable ambient automorphism preserving the kill row's normal
  closure, followed only by base-row normalization and kill-row donor
  cleanup, proves the bridge. Within this ambient-automorphism-only
  mechanism, an escape needs genuine base-row multiplication visible after
  projection or alteration of the kill row.
- **One projected multiplication also closed:** normalizing one arbitrary-
  conjugator base-row multiplication gives 64 oriented cases and 32 ambient
  matrices. In every case the unchanged row's cyclic length misses its
  assigned common-kill target length. Thus a successful path within this
  low-depth inventory must contain at least two base-row multiplications
  visible after projection or alter the kill row. Retained stabilization
  rows remain outside this theorem. Freeze the ledger here; do not add a
  two-multiplication census as another bounded category.
- **Direct Tpub thickenability route closed:** the exact 29-corner link has
  nine parallel classes and four spherical macro rotations among 144. Every
  repeated class is forced into one reversed block. Exhausting all four
  schemes, 3,120 scheme--phase pairs, and 18,720 component seeds finds no
  compatible spherical rotation. Hence this one word-realized presentation
  complex is not thickenable. This is not AC-invariant and does not obstruct
  an AC-equivalent thickenable representative, the bridge, or stable AK(3).
- **Pinned-seam donor class frozen:** among the twelve products obtained by
  multiplying displayed $A$ or $B$ by a cyclic shift of $v^{\pm1}$, exactly
  four shorten at a cyclic seam. Complete spherical-scheme and signed-rank
  audits find all four exact complexes nonthickenable. This closes only the
  tail-free boundary-cancelling class. Do not extend it to another donor
  census; surviving conjugator tails, unshortened products, multi-move paths,
  retained stabilizations, the bridge, and stable AK(3) remain open.
- **One-tag stable endpoint isolated:** one fresh row gives a literal path
  `(r,q,v,t) ~ (A,B_t,v,rt)`, where the second-row discrepancy is the exact
  commutator `L_t`. Cleaning `B_t` first is obstructed by the already-proved
  nontriviality of `[X,r]` in the Gate-A Magnus group. Restoring `rt` first is
  obstructed by a new HNN extension which embeds that same group and retains
  `r != 1`. Freeze these two direct first-substitution gates. The sufficient
  open object at this endpoint is the interleaved relative Peiffer class
  `(A,B_t,v,rt) -> (A,B,v,t)`; it is not necessary, is not closed, and gives
  no stable-AK(3) claim.
- **All nilpotent boundary shadows evaluated:** after undoing the final donor
  macro, the relative endpoint is `(q,rt) -> (B,t)` over fixed `(A,v)`.  In
  the Gate-A quotient, `gamma_2=gamma_n` for every `n>=2`, and both `r` and
  the discrepancy `D` lie in that stable subgroup.  Hence every nilpotent
  quotient identifies both ordered pairs literally with `(x^-1,t)`.  This
  closes lower-central invariants of the boundary words only.  It is not a
  class-two crossed-module calculation or a Peiffer lift; those require
  explicit 2-cell lifts and the relative move action.
- **First legal interchange evaluated and frozen:** a no-self-donor path
  transforms the normalized pair `(q,rt)` to `(q0,Omega*t)`.  The middle
  discrepancy is the old `L_t`, and its direct cleanup is still blocked by
  `T_B`; the final `Omega` is outside `Ncl(A,v,q0)` by `T_t`.  This closes
  only those cleanups at their respective checkpoints.  Cleaning the first
  row after the third arrow and further alternating changes to both live rows
  remain open.  Do not add another finite
  alternation category: the next tagged checkpoint must construct a genuine
  continuation or control the full relative Peiffer class.
- **Full factorwise metabelian shadow closed positively:** the exact Gate-A
  Alexander module is `Z[1/2]`, with `x` acting by doubling.  In its
  semidirect coordinates, `q=(1/2,-1)`, `r=(3,0)`, `D=(-3/4,0)`, and
  `B=(7/8,-1)`, so conjugation of `q` by `D^-1` is literally `B`.  Since
  `B` normally generates the Gate-A quotient, the whole pair
  `(q,rt) -> (B,t)` is AC-equivalent after killing `Q_A''`, even with the tag
  factor left free.  Thus every metabelian quotient of the tagged ambient
  group is blind.  This does not lift the conjugacy to `Q_A` or close the
  relative Peiffer class.
- **Unchanged metabelian conjugator does not lift:** the literal defect
  `E=D^-1*q*D*B^-1` lies in `Q_A''` but is nontrivial.  After shifting into
  the Magnus base it has Britton form
  `delta^-1*b*x^-1*delta^2*x*b^-1`; the middle word has nonzero
  `a`-exponent and cannot lie in the associated subgroup.  This closes only
  conjugation by the displayed `D^-1`.  A `Q_A''`-corrected conjugator,
  multi-row Peiffer lift, or different full relative path remains possible.
  Do not open a finite conjugator ledger.
- **Complete displayed correction coset obstructed:** the infinite family
  `n*D^-1`, with `n in Q_A''`, reduces in `Q_A''/Q_A'''` to one twisted
  coboundary equation.  The ascending-HNN direct limit and exact Fox
  coefficient reduce it to a Laurent Mahler equation.  Dividing its forced
  dyadic product leaves coefficient equations at degrees `0,2p,4p,6p`
  which require the same coefficient to equal both one and zero.  Hence no
  element of the complete coset `Q_A''*D^-1` conjugates `q` to `B`.  This
  does not classify other metabelian conjugators or obstruct multi-row
  Peiffer lifts and different full paths.
- **All literal conjugators obstructed:** in the factorwise metabelian group,
  the centralizer of `q=(1/2,-1)` is exactly `<q>`.  Therefore every quotient
  conjugator from `q` to `B` is `D^-1*q^j`.  Any literal lift has the form
  `n*D^-1*q^j` with `n in Q_A''`; the power of `q` cancels around `q`, leaving
  the same twisted-coboundary equation already disproved for every `n`.
  Hence `q` and `B` are not conjugate in `Q_A`.  This closes every single-row
  literal conjugation lift of (105), not a multi-row Peiffer lift, another
  quotient path, or the unrestricted bridge.
- **Tagged source normalized completely:** modulo `q=Xy` and `v=Xyz`, one
  has `y=x`, `z=1`, and both `A` and `r` freely reduce to `x`.  Thus
  `r*A^-1 in Ncl(q,v)` and `r in Ncl(A,q,v)`, so exact donor macros remove
  `r` from `rt` while restoring all three donor rows.  The canonical relative
  class is now exactly the tagged normal-generator gate `(q,t) -> (B,t)` in
  `Q_A*<t>`.  Nonconjugacy of `q` and `B` does not decide this two-row AC
  orbit; no tag-rigidity or destabilization theorem is known here.
- **First tagged defect module identified:** for
  `G_t=Q_A*<t> -> (Q_A/Q_A'')*<t>`, Bass--Serre theory shows that the kernel
  is the free product of the conjugates of `Q_A''` indexed by the quotient
  factor cosets.  The quotient graph is itself the Bass--Serre tree of the
  quotient free product, so there is no extra Kurosh free factor.  Its
  abelianization is therefore the induced module
  `Z[Gbar] tensor_{Z[H]} (Q_A''/Q_A''')`, and the identity-coset copy embeds.
  The canonical quotient conjugation has exact residual `([E],0)` in this
  module.  This is not yet an obstruction to the tagged pair: arbitrary AC
  loops at `(B,t)` may have affine Fox defects which cancel it.  A quotient
  loop has no canonical lift; the complete defect set must include every
  tame lift and the vertical kernel projecting to the identity loop.
- **Resume point:** both sequential donor completions are closed. Work on the
  unrestricted common-kill target, the genuinely interleaved closure of one
  symbolic residual pair, or the literal relative Peiffer structure at the
  one-tag endpoint.  Do not escalate through more ambient lower-central
  quotients or metabelian quotients: they are all blind.  For the tagged route,
  every literal conjugator from `q` to `B` is now closed, and the coefficient
  `r` has been removed from the source.  Work on the complete tagged gate
  `(q,t) -> (B,t)` by evaluating the complete lifted defect set of `([E],0)`
  in the induced kernel module, including the vertical tame-operator kernel,
  or by constructing a full path.
  If the linear orbit contains zero, escalate once to the tame relative
  crossed-module basis; do not infer an AC path.  A multi-row Peiffer lift or
  another full relative path may bypass the closed single-row gate.  Do not
  add another finite
  alternation or conjugator category.  The lifts are complete, but no closure
  to `(A,B,Xyz)` is proved. Do not add
  another sequential cleanup or pinned-donor category. No fixed-base or
  failed-search result is evidence against the bridge.
- **Two-gate theorem:** either positive gate would have constructively
  AC-trivialized `Tpub`; both are now disproved, so the theorem closes the
  sequential ansatz without closing the bridge. See
  `literature/proofs/AK3_MMS02_TPUB_TWO_GATE_BRIDGE.md`.
- **Nonclaim:** neither first leg alone proves the bridge, AC, or stable AC.

## 2. Old--new covariance program — active

- **Proved positive-chamber load:** algebraically,
  \(E_{P/C/Q}=[d=1]\), \(E_{\rm fixed}=0\), \(E_{\rm base}=0\), and
  \(E_{\rm singleton}=1\). Hence
  \(\mathbb B(A_{n,d},b_{n,d})=[d>1]\) for \(d\geq1\), independently of
  \(n\). Bound commits: `bc4338cb`, `c172c173`.
- **Inverse old--new load proved:** the inverse-\(Q\) chain telescope,
  piecewise connector topology, 36-edge \((8,14,14)\) support, and membership
  pairing are proved.  The exact occurrence sweep gives outer load
  \([e=0]\) and tie load `0`; fixed/base loads vanish and the singleton
  load is `1`.  Hence
  \(\mathbb B(A^-_{n,e},b^-_{n,e})=[e\geq1]\), independently of \(n\).
- **Inverse pure increment and edge law proved:** the approved
  [all-power inverse certificate](../.scratch/period_two_inverse_pure_increment_certificate.md)
  evaluates the 36 paired raw bits and all 3,486 pairs of the 84-token stream
  on twelve exhaustive symbolic cells.  It gives
  \(L(b^-_{n,e})=0\), \(Q(b^-_{n,e})=1\), and
  \(\Phi(b^-_{n,e})=1\), hence \(J^-_{n,e}=[e=0]\).  The frozen manifest is
  `.scratch/period_two_inverse_pure_increment_manifest.json`, SHA-256
  `4e821f1cc9b721281178341b458669de3ac7191314a8e613fb7a37866e40b0cd`.
- **Positive raw load and edge law proved:** the separate
  [positive-chamber theorem](../literature/proofs/AK3_POSITIVE_J_EDGE_RAW_LOAD.md)
  proves \(L(b_{n,d})=0\) for every \(d\geq1\).  With the already proved
  \(Q(b_{n,d})=1\) and
  \(\mathbb B(A_{n,d},b_{n,d})=[d>1]\), it gives
  \(J_{n,d}=[d=1]\).  Together with the inverse theorem, the \(j\)-edge law
  is complete in every chamber.
- **Diagonal defect reduced to one boundary row:** the
  [exact reduction](../literature/proofs/AK3_DIAGONAL_DEFECT_REDUCTION.md)
  combines the global \(j\)-edge law with the four-corner identity to prove
  \(\mathcal D_{i,j+1}=\mathcal D_{ij}\), hence
  \(\mathcal D_{ij}=\mathcal D_{i0}\).  Equivalently,
  \(u_{ij}=c_i+[j=i]\) and
  \(\mathcal D_{ij}=c_{i+1}+c_i\).  The same argument proves the complete
  augmented equality
  \(\mathscr C(a,g)=\mathbb B(b,f)+\mathbb B(b,g)+\mathbb B(f,g)\), without
  termwise vanishing.
- **Sharper boundary target:** the
  [pure-\(P\) normal form](../literature/proofs/AK3_PURE_P_INCREMENT_NORMAL_FORM.md)
  specializes the defect at \(j=i\).  Its endpoint words are
  \(\operatorname{red}(P_\nu^iC_\nu)\), with no \(Q_\nu\)-factor, and its
  forest mask is one two-ray \(P\)-connector plus three differences of
  literal short connectors.  Diagonal vanishing makes
  the \(c_i\) constant; the proved seed \(u_{00}=1\) forces \(c_0=0\).
  Hence proving this diagonal pure-\(P\) increment zero proves the full
  diagonal identity.
- **Pure-\(P\) raw theorem proved:** the
  [all-power certificate](../.scratch/period_two_diagonal_pure_p_raw_certificate.md)
  collision-aggregates 46 signed rows to 42 active coordinates of profile
  \((9,15,18)\) and evaluates all 84 literal raw observables on the four
  exhaustive cells \(i=0,1,2,\geq3\).  A separate replay reconstructs the
  source rows, factor order, fibers, observables, and source-bound pump
  premises without importing the producing checker.  Both replays give
  \(L_{\ne0}(q_i)=0\), and the slot-zero theorem gives \(L(q_i)=0\) for
  every \(i\geq0\).  Current hash prefixes: manifest 6f83559c, independent
  replay 179e868d, independent tests a08021d7; the source-bound raw-locality
  section digest is 4e0de9fd.
- **Quadratic theorem proved:** deterministic collision splicing gives
  a 48-chord label-preserving matching of the 96-token stream.  Exact
  reduced-cone separation proves that its sole repeated chord label occurs
  at \(X_{3,i+1}\); the two corresponding intervals are nested, so every
  crossing is heterochromatic and \(Q(q_i)\) is the total chord-crossing
  parity.  The [frozen certificate](../.scratch/period_two_diagonal_pure_p_quadratic_certificate.md)
  proves all 39 adjacent all-power rank comparisons in each of four
  exhaustive cells; the 48 prefix bits have weight 21.  A genuinely
  independent source-row reconstruction agrees with an explicit
  4,560-pair direct kernel ledger without reading the producer's scalar.
  Hence \(Q(q_i)=1\) for every \(i\geq0\).
- **Diagonal finite-old terms proved:** exact AST interval counts
  \(0,28,18,24,0\) give fixed chronology parity
  \(28+24=52=0\); source-forest separation kills the fixed equal-label
  prefixes and, by the even-fiber theorem, their transported-label ranks.
  The radius-two base core is disjoint from the mask, while the singleton
  has membership one and prefix bits \((0,0,1,0,1,0)\).  Hence
  \(E_{\rm fixed}=0\), \(E_{\rm base}=0\), and
  \(E_{\rm singleton}=1\) for every \(i\geq0\).
- **Diagonal old--new term proved:** exact indexed support lists for the four
  powered head--tail pairings give
  \((H_1,H_2,H_3,H_4)=(1,1,0,0)\).  The powered subtotal is therefore
  zero; adding the finite-old subtotal gives
  \(\mathbb B(A_i^\Delta,q_i)=1\) for every \(i\geq0\).
- **Diagonal and unary theorem proved:** the three exact values
  \(L(q_i)=0\), \(\mathbb B(A_i^\Delta,q_i)=1\), and \(Q(q_i)=1\) give
  \(\mathscr C(A_i^\Delta,q_i)=0\).  Thus \(c_{i+1}=c_i\); the seed
  \(u_{00}=1\) gives \(c_0=0\), so
  \(u_{ij}=\delta_{ij}\), \(\mathcal D_{ij}=0\), and
  \(I_{ij}=[i-j=-1]+[i-j=0]\).  The last-coordinate first-family unary
  matrix therefore has infinite rank, even after its row-only and constant
  rank-one terms.
- **Full-lift quotient scope:** Equation (1.10) is exact only over the fixed
  quotient witness $\mathbf h^*$.  The row-centralizer gauge is not
  complete: four literal-lift-compatible prefix-Hurwitz symmetries preserve
  the recurrence, and iterating the first carries $\mathbf h^*$ through
  infinitely many row-gauge classes.  The fixed-fiber terminal theorem
  therefore transfers to this whole Hurwitz orbit.  Full quotient promotion
  can follow from Hrg-Class plus RG-Lift, another complete lift-compatible
  action, or direct obstructions on the remaining quotient fibers.  Even
  after such coverage, the terminal theorem obstructs only the named
  depth-four recurrence $(8,3,5,-3,5)$, not AK(3).
- **Resume point:** keep the free-group period-two lift separate.  The unary
  theorem lives after the complete-cover/\(c^2=1\) reduction and neither
  constructs literal correction words in \(F(c,t)\) nor cancels their
  nonabelian residual in \([N,N]\).  It does give the exact sieve
  \(S_\infty(D_{ij})=1+\delta_{ij}\), excluding every off-diagonal anchored
  correction.  The coordinate-four theorem proves \(R_{4,i}=0\) for every
  \(i\geq0\), so \(V_{i,4}\) is two-periodic.  Its seed values are both one
  while the required fourth target bit is zero; every diagonal anchored
  correction is therefore excluded as well.  The complete anchored family
  \(D_{ij}\) now fails a necessary class-two syndrome.  The former
  constructive target was the fourteen-coordinate
  all-power diagonal sequence
  \(V_i=(U_1(D_{ii}),\ldots,U_{14}(D_{ii}))\), which must equal
  `11101011010101` before a diagonal candidate can pass the recorded
  syndrome.  The next constructive target is the full quadratic cokernel
  equation on arbitrary balanced source-pair corrections, with every mixed
  polarization retained.  The universal relative-displacement map
  \(\Xi\) sends a wedge \(e_{qH}\wedge e_{rH}\) to the unoriented double
  coset of \(q^{-1}r\).  Since all five lifting operators have augmentation
  zero, it gives an integral surjection from the full class-two cokernel:
  non-self-inverse double-coset pairs contribute signed \(\mathbb Z\)
  buckets, while inversion-fixed classes contribute \(\mathbb Z/2\).
  Reducing gives the infinite-dimensional mod-two histogram indexed by
  nontrivial \(H\backslash Q/H\) modulo inversion.  Thus every candidate
  must kill both the integral and mod-two relative-displacement maps.  The
  complete balanced source pair has an exact
  anchored expansion through both source slots, and its \(\Xi\)-defect is
  the affine constant plus all anchored unary buckets plus every mixed
  bucket.  The anchored family has nonzero \(\Xi\)-defect, but no theorem
  controls all mixed buckets; per-double-coset noncancellation is now the
  exact global obstruction target.  The mixed \(\Xi\)-Hessian is now one
  exact vector-valued literal-stream cut: one-token local and fixed-base
  terms cancel under polarization, while within-occurrence and external
  central-label comparisons retain their actual source shortlex predicate
  and relative double-coset bucket.  Diagonal \(Q\)-invariance cannot be
  applied to intermediate ordered-half tensors, so this consolidation is
  not an order-free cancellation.  Integrally, however, every
  non-self-inverse bucket admits a \(Q\)-invariant orientation.  Pairing the
  equal positive/negative occurrence counts cancels its section-order
  tensors and gives an exact signed cross-correlation formula with the 120
  relative occurrence multipliers.  Hence mixed-Hessian shortlex difficulty
  is confined to inversion-fixed \(\mathbb Z/2\)-buckets; the free
  correlations remain unbounded and unevaluated.  Those 120
  occurrence pairs further compress to a fixed \(5\times5\) integral
  Fox--Hessian matrix \(\mathbf H\) satisfying
  \(\mathbf H_{st}+\mathbf H_{ts}^*=L_s^*L_t\).  On homogeneous directions
  this proves the free-bucket tensor is antisymmetric; it does not make any
  oriented bucket vanish.  The remaining free problem is the restriction
  of this form to the complete anchored generating family plus its affine
  unary term.  The weighted Green identity removes the untransported
  merged-support shortlex sum, but the correct ordered-half wedge reader is
  not \(Q\)-equivariant, so transported leaf terms do not cancel by signed
  occurrence augmentation.  Projected linear/outer terms outside that
  section package are period 40 from \(i=0\).  The approved 84-record raw
  pump makes every slot-two/three/four one-vertex transport term period
  dividing 20 for \(i\geq3\); the explicit word
  \(y_i=(\texttt{cTc})(\gamma^{-1})^{i+1}\texttt t\) proves the same
  slot-zero transport bound directly from \(i=0\).  With
  \(\Delta_i=D_{i+1}-D_i\), the exact period-two proof object is
  \(G_i=u_{14}(\Delta_i)+\beta_{14}(D_i,\Delta_i)\); proving
  \(G_{i+1}=G_i\) would prove the complete fourteen-coordinate recurrence.
  Its fourth coordinate is now proved separately and already excludes the
  whole diagonal family.  Equivalently, for
  \(E_i=D_{i+2}-D_i\), the all-index target is
  \(R_{k,i}=\lambda_k\Pi_{\rho_k}(M_B(D_{i+2})-M_B(D_i))=0\); the smallest
  proved exact obligation is its conservative 2,380-bit window
  \(1\leq k\leq14,\ 0\leq i\leq169\).  Coordinate four is now evaluated
  to zero for every index, leaving exactly 2,210 unevaluated values in the
  other thirteen coordinates.  These remaining diagonal coordinates are
  no longer needed to exclude the anchored family.
  The exact ordered-reader decomposition rewrites the actual transported
  leaf as a common invariant Green scalar, the one-vertex defect, and the
  differentiated inversion term.  The common scalar cancels because the
  active occurrence counts are \((6,0,2,2,2)\), and the one-vertex part is
  finite-periodic from \(i=3\).  The two valid transport
  representations are transported-old-order plus one-vertex defect, or
  canonical-new-order plus the full section defect; mixing them would
  double-count the order change.  The pure inversion cocycle now pairs
  every positive/negative occurrence into one relative action
  \(m=q_-q_+^{-1}\).  All three slot-zero relative kernels vanish because
  the old and new slot-zero states are singletons modulo two.  Only the
  slot-two, slot-three, and slot-four relative kernels remain.  Modulo two,
  the old diagonal source current is exactly the four-path connector
  \(K_i\), and its two-step shell is \(K_i+K_{i+2}\); the fixed-base
  remainder is zero in slots two and four and singleton--shell only in
  slot three.  Slot-four fixed-base vanishing follows from the exact
  \(T\)-inversion split: the base head is \(ct\) of length two, while every
  \(t\)-initial shell head has length at least 29.
  The slot-four \(T\)-kernel is exactly a weighted incidence across
  length gaps one and two, with no lexical comparison.  Its complete
  source remainder is the xor of six within-block weights in each of the
  next two powered \(P_*\)-blocks, hence exactly twelve finite-action
  weights.  Repeated-block covariance does not kill the resulting one-sided
  \(L_4\)-boundary in general.  Exact substitution in the eleven pinned
  finite actions now evaluates it completely: its all-index fourteen-bit
  vector is `01000000100000`, with ones only in coordinates two and nine.
  This is a slot-four inversion-source term, not the complete crossed
  derivative.  The slot-three fixed-base polarization is also zero by an
  exact length gap.  For \(i\geq1\), the slot-two source is exactly 22
  finite-action weights on two new levels, two adjacent seams, and two
  terminal incidences; their evaluated all-index stable vector is
  `10000000000010`, with survivors \(k=1,13\).  The separately evaluated
  seed is `10010001000010`, with survivors \(k=1,4,8,13\).  Thus the
  slot-two inversion source is completely known for every index.
  The slot-three source has an exact \(G\)-cancellation-depth signature.
  Collision-first ranking reduces it to nine within-level reversals on
  each of the two new powered levels, hence exactly 18 finite-action
  weights for every index.  There are no cross-level, terminal, or seed
  contributions.  Exact finite-action substitution gives slot-three vector
  `10000000100010` on even indices and `11000000000010` on odd indices.
  Xoring all three slots gives the complete differentiated-inversion source
  `01010001000000` at the seed, coordinate nine alone on positive odd
  indices, and coordinate two alone on positive even indices.  Removing
  this source does not remove the four ordered product profiles
  \(H_k(\delta a,qb)\), \(H_k(a,q\delta b)\),
  \(H_k(\delta a,q\delta b)\), and
  \(H_k(\delta a+q\delta b,o_{q,r})\).  Those profiles do not factor through
  projected linear states.  Literal-stream flattening nevertheless absorbs
  their complete AST xor, including inverse, transport, and quotient-section
  legs, into a coordinate-specific local weight plus one weighted cut on the
  central labels of the sixteen occurrences.  The local weights are covered
  by the approved raw pump, while the 152 leaf schemas cover every moving
  label comparison.  The fully expanded fixed literal stream has unreduced
  mass 216, so every fixed-event comparison leg also has length below 372.
  The leaf bound \(L=372\), with the sound two-sided
  allowance for whole-core cancellation, gives onset 130.  Hence the
  protected catalog proves only \(R_{k,i+40}=R_{k,i}\) for \(i\geq130\),
  giving the 2,380-bit window above.  The fourth coordinate now contributes
  all 170 proved zeros inside that window; 2,210 values remain unevaluated,
  so no all-coordinate vanishing or period-two claim is proved.  In the
  fourth three-point coordinate, however, the powered element acts
  trivially and every one-step-shell chord label has an all-index constant
  projected color.  The frozen crossing set then proves termwise that the
  coordinate-four new--new contribution \(Q_4(q_i)\) is constant from the
  seed.  The coordinate-four local contribution is also constant on the
  protected cell \(i\geq3\), because the raw first-half lists are fixed and
  the moving central color is constant.  Its all-index extension is reduced
  to the three finite seams between cells \(0,1,2,\geq3\).  A frozen
  negative slot-two record shows why the scalar raw bit cannot decide those
  seams: it has scalar weight zero but coordinate-four local weight one.
  Pairing the two-step shell by its two 48-chord matchings removes source
  shortlex outside the endpoint blocks of the old--shell polarization:
  every external fixed atom, complete intervening occurrence, and
  occurrence-prefix base cancels between corresponding shifted chords.
  Old fixed atoms inside an endpoint occurrence remain in its local prefix.
  The exact survivor is a 48-row ledger of within-occurrence three-color
  prefix differences.  The matching one-step-shell local prefix cancels
  slotwise: increasing positive chronology and decreasing negative
  chronology count every unordered weighted pair twice.  This converts the
  48 rows to the natural-side simultaneous-shift seams \(\Theta\).  The
  aggregate seam then vanishes: the projected shell mask is index-independent
  in each slot, consecutive old masks differ by that shell, and the
  resulting self-pair is zero by alternation.  The source-bound seam
  projection then evaluates the nonzero-slot local term as zero in the four
  exhaustive cells \(i=0,1,2,i\geq3\).  The separate slot-zero occurrence
  weights are index-independent and cancel between the two consecutive
  shell atoms.  Hence \(L_4(q_i)=0\) and \(R_{4,i}=0\) for every
  \(i\geq0\), excluding the complete anchored family as stated above.
  The section cocycle is not killed pointwise by
  invariant covectors: two tracked four-point coordinates have explicit
  nonzero quotient-section residuals.  Any survivor must then solve the full exterior-module cokernel
  equation in \(\Lambda^2M\), not merely the fifteen-bit quotient.  The
  companion cross kernels and other primitive families remain open; no
  full-Hessian rank claim follows.
- **Nonclaim:** no period-two free-group witness, AK(3), stable AC, or AC
  conclusion is proved.  Even a successful lift still needs a separately
  proved implication to the relevant AK(3) move/factorization target.

## 3. Thickenability frontier — preserved

- **Known checkpoint:** the exact 1,000-map Aut(F2) frontier has a verified
  bounded null with no spherical candidate. It is not an Aut-closure and does
  not transport negative thickenability across arbitrary Nielsen images.
- **Resume point:** improve only with a new exact word-realized topology
  mechanism or a rigorously larger externally run frontier; quarantine every
  positive pending independent rotation replay and Regina `isBall()`.
- **Nonclaim:** bounded negatives do not disprove thickenability, AC, or stable
  AC.

## 4. Orbit-2 classical AC search — preserved external-scale route

- **Exact start:** `YYXXyx | YYYxyXX`, classically AC-equivalent to AK(3) and
  better connected at the length-13 floor.
- **Resume point:** local work is only a <=1,000-node pipeline preflight and
  independent path replay; a production budget belongs on Colab or another
  user-controlled multi-CPU runner.
- **Nonclaim:** an unsolved budget or ceiling is never counterexample evidence.

## Checkpoint discipline

Every material route update records the exact artifact or commit, the next
resumable action, and the strongest honest nonclaim. Changed proof/runtime
implementations are tested, committed, logged with UTC and bound SHA, and
pushed before an experiment. Long experiments remain single-threaded,
foreground, guarded, and followed by exact cleanup audits.
