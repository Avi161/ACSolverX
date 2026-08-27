# All-power diagonal pure-\(P\) raw certificate

## Status and theorem

For

\[
 q_i=A_{i+1,i+1}+A_{i,i},\qquad i\geq0,
 \tag{0.1}
\]

the slot-zero calculation in the pure-\(P\) normal-form theorem and the
certificate below prove

\[
\boxed{
 L_0(q_i)=0,\qquad L_{\ne0}(q_i)=0,\qquad L(q_i)=0
 \quad(i\geq0).}
 \tag{0.2}
\]

This is only the raw theorem. The old--new term, \(Q(q_i)\), the complete
diagonal scalar, the diagonal identity, the period-two lift, AK(3), stable
Andrews--Curtis, and Andrews--Curtis remain open.

## 1. Exact collision interface

The five source families contain

\[
 14+18+4+6+4=46
 \tag{1.1}
\]

signed literal traversals. Exact integral collision aggregation gives
44 fibers. Two cross-family fibers have even coefficient, leaving
42 active coordinates with slot profile

\[
 (|S_2|,|S_3|,|S_4|)=(9,15,18).
 \tag{1.2}
\]

Each active coordinate has its two correction occurrences, so the nonzero
raw ledger contains \(2\cdot42=84\) literal observables. The authoritative
family derivation and factor order are in
literature/proofs/AK3_PURE_P_INCREMENT_NORMAL_FORM.md, equations
(4.4a)--(4.4c).

## 2. Exhaustive all-power cells

The parameter ray is partitioned into the four disjoint cells

\[
 i=0,\qquad i=1,\qquad i=2,\qquad i\geq3.
 \tag{2.1}
\]

Direct expansion evaluates the first three cells. At the base of the
unbounded cell, every one of the 84 observables has exactly one positive
common-phase affine core. The certificate replays the module word at
\(i=3,4\), checks the complete first-half raw signature, verifies

\[
 \text{split}+\text{increment}\,|R|>|q|+1,
 \tag{2.2}
\]

and requires noncentral first-half labels, strict central-length separation,
positive central slope, and exact schema expansion. The source-bound
boundary-locality lemma in Section 4.1 of the theory note then extends the
base transition to every \(i\geq3\).

The computed nonzero raw xors are

| cell | observables | \(L_{\ne0}\) |
|:---|---:|---:|
| \(i=0\) | 84 | 0 |
| \(i=1\) | 84 | 0 |
| \(i=2\) | 84 | 0 |
| \(i\geq3\) | 84 | 0 |

No expected xor is hardcoded.

## 3. Independent replay

The frozen primary manifest is deliberately marked provisional. Promotion
comes from a separate replay which does not import the producing checker or
call its manifest builder. It independently reconstructs:

1. all 39 authoritative source rows and their 46 old/new signed contexts;
2. the reversed-prefix/root/incidence factor order and all 138 powered
   schemas;
3. all 44 collision fibers, their integral sums, the 42 active coordinates,
   and profile (1.2);
4. all 84 tokens and literal raw observables in every cell; and
5. every unbounded pump premise in the source-bound locality lemma.

The replay recomputes each xor from the 84 raw values. Its nine hostile
tests mutate provenance, factor order, fibers, observables, pump witnesses,
support, computed xor, and the theory hash. All mutations are rejected.
Hostile Sol xhigh review approved the source selection, common-phase pump,
independence boundary, and final theorem (0.2).

## 4. Frozen bindings

| artifact | SHA-256 |
|:---|:---|
| primary checker | 57b70bd181aa376855d87f209e72ae98b39d45afc9c68d8149103dbbda7aab17 |
| primary tests | 2439745e302ad01cae1908814d48aad3afff228ac767f03bbc0ae9d5cc112f07 |
| primary manifest | 96da011ff66adb4bf8f0c74903895c39762bb80e58bf60f874766ea6499dd00c |
| independent replay | 3b0d94f8eb3e686cbeed155f25b8ccdcdd1b1b5a618ae18b5c190685ccea4a51 |
| independent tests | 1a5e18ba464328707ece0452563559be8f3fbd373e5dc1b7c255f0562db328d4 |

Guarded primary generation and canonical replay pass with zero generation
failures. The 13 primary mutation tests and nine independent hostile tests
pass. The final independent replay returns 46 provenance rows, 42 active
coordinates, and cell xors \(0,0,0,0\).

## 5. Remaining scalar

Substituting (0.2) into the exact pure-\(P\) increment interface leaves

\[
\boxed{\mathbb B(A_i^\Delta,q_i)+Q(q_i)=0}
 \tag{5.1}
\]

as the complete remaining diagonal obligation. Neither summand is
evaluated here, and no termwise vanishing is asserted.
