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
- **Resume point:** prove the joint inverse scalar identity
  \(L_{\ne0}(b^-_{n,e})+Q(b^-_{n,e})=[e\geq1]\), equivalently the remaining
  pure-increment theorem \(\Phi(b^-_{n,e})=1\).  Its exact unresolved schema
  is 36 paired raw bits plus 210 same-slot module-order predicates on the
  collision-aggregated 84-token stream.  Then prove the diagonal defect.
- **Nonclaim:** positive covariance is not by itself the \(j\)-edge values and
  does not prove the other chambers, diagonal identity, unary delta,
  period-two lift, AK(3), stable AC, or AC.

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
