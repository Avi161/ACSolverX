# AK(3) research promise ledger

This ledger prevents a bounded engineering failure or a context switch from
silently abandoning a mathematically live route. A route leaves this file only
after a verified proof closes it or an exact theorem refutes its stated
mechanism. Search exhaustion, timeout, storage pressure, and failure to find a
finite quotient do not close a route.

## 1. MMS02 rank-three donor factorization — active

- **Exact target:** `(A,B,zYX) ~AC (A,B,Xyz)` by rank-three AC1--AC3 moves.
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
- **Resume point:** prove a second-stage normal-closure factorization or give an
  exact homomorphism refuting only its named sequential ansatz. Do not use a
  failed quotient search as evidence. Before extending the JSON schema, harden
  ordinal fields to reject booleans/floats that compare equal to integers.
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
- **Resume point:** keep the free-group period-two lift separate.  The unary
  theorem lives after the complete-cover/\(c^2=1\) reduction and neither
  constructs literal correction words in \(F(c,t)\) nor cancels their
  nonabelian residual in \([N,N]\).  The companion cross kernels and other
  primitive families also remain open; no full-Hessian rank claim follows.
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
