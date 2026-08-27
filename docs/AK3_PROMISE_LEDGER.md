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
- **Resume point:** prove the joint two-ray \(P\)-period lemma (7.1) in the
  pure-\(P\) normal-form note:
  \(\mathscr C(A_{i,i},A_{i+1,i+1}+A_{i,i})=0\).  Its slot-zero raw part is
  proved zero.  Collision aggregation leaves 42 nonzero-slot raw coordinate
  templates (84 literal occurrence observables) and a 96-token quadratic
  stream; the nonzero raw, old--new, and new--new terms remain one open joint
  xor.  With the seed, this would prove \(u_{ij}=\delta_{ij}\).
- **Nonclaim:** the completed \(j\)-edge law does not prove the \(i\)-edge
  law; the reduction does not prove the diagonal identity.  The unary delta,
  period-two lift, AK(3), stable AC, and AC remain open.

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
