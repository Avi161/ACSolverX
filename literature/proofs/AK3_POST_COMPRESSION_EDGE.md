# A classical edge after one-edge AK(3) compression

Date: 2026-07-24

Status: the stable implication is **PROVEN**. The finite floor-12 candidate in
Section 4 is **UNVERIFIED** until its certificate is built and replayed.

## 1. Certified roots

Let \({\cal E}\) be the finite set of rank-two outputs in the exact
one-edge-compression certificate. The prior theorem proves

\[
 \mathrm{AK}(3)\sim_{\mathrm{st}} E
 \qquad(E\in{\cal E}).
\]

Let \({\cal C}\) be the set obtained by freely/cyclically reducing each
relator and quotienting pairs by:

- relator order;
- cyclic rotation;
- relator inversion.

These operations are AC1--AC3 symmetries. Therefore every
\(C\in{\cal C}\) is also stably AC-equivalent to AK(3). The production
one-edge certificate has 20 such canonical roots; that count is a certificate
datum, not an assumption of the theorem.

## 2. Full Definition-2.1 children

Fix \(C=(R_0,R_1)\in{\cal C}\). Choose a target \(i\), let \(j=1-i\), choose
\(\delta\in\{+1,-1\}\), and choose cyclic rotations

\[
 U=\operatorname{rot}(R_i),\qquad
 V=\operatorname{rot}(R_j^\delta).
\]

Define

\[
 R_i'=\operatorname{cyc}(UV)
\]

and leave the other relator's cyclic conjugacy class unchanged. Canonicalize
the resulting pair under order, rotation, and inversion.

Every such child is classically AC-equivalent to \(C\): conjugate the target
to \(U\), invert and conjugate the other relator to \(V\), multiply the target
by the other relator, restore the non-target relator, and cyclically reduce
the target by conjugation. These are AC1--AC3 operations.

Unlike the preceding seam theorem, this finite decision enumerates **every**
pair of rotations. It needs no cancellation hypothesis.

## 3. Floor-12 stable implication

### Theorem 3.1 — PROVEN

If a child \(D\) from Section 2 has complete Aut(\(F_2\))-minimum total
relator length

\[
 \mu(D)\le12,
\]

then AK(3) is stably AC-trivial.

### Proof

Choose the certified root \(C\) and edge \(C\sim_{\mathrm{AC}}D\). The
one-edge-compression theorem gives

\[
 \mathrm{AK}(3)\sim_{\mathrm{st}}C.
\]

Let \(\phi\in\operatorname{Aut}(F_2)\) be a complete Whitehead witness with
total length at most 12. The stable ambient automorphism theorem gives

\[
 D\sim_{\mathrm{st}}\phi(D).
\]

The pair \(\phi(D)\) is a balanced two-generator presentation of the trivial
group: all preceding transformations preserve the presented group. By
MM03 Theorem 1.1, as recorded and scoped in `MU_CRITERION.md`, every such
presentation of total length at most 12 is classically AC-trivial. Hence

\[
 \mathrm{AK}(3)
 \sim_{\mathrm{st}}C
 \sim_{\mathrm{AC}}D
 \sim_{\mathrm{st}}\phi(D)
 \sim_{\mathrm{AC}}\langle x,y\mid x,y\rangle.
\]

Thus AK(3) is stably AC-trivial. \(\square\)

### Constructiveness

The corridor, classical edge, and Whitehead automorphism all carry explicit
witnesses. MM03 supplies the final classical existence theorem. An elementary
AC path for the length-at-most-12 endpoint must still be replayed locally
within 1,000 nodes or labeled `MM03-existence, not replayed`.

## 4. Finite candidate

### Post-compression floor-12 lemma — UNVERIFIED

Among all full Definition-2.1 children of the 20 canonical roots in the
production one-edge-compression certificate, at least one has complete
Aut-floor at most 12.

The exact decision must:

1. bind the verified upstream certificate and its trace;
2. reconstruct its canonical output roots;
3. enumerate both targets, both signs, and every pair of cyclic rotations;
4. freely and cyclically reduce without a length-pruning cap;
5. retain one literal move witness for every canonical root-child edge;
6. compute a complete Whitehead witness for every distinct child;
7. independently replay every edge and witness;
8. rerun and compare the full deterministic payload.

## 5. Negative scope

If the complete minimum is greater than 12, only the finite lemma in Section
4 is refuted. If, moreover, every child has floor greater than the roots'
minimum 14, the certificate proves a strict one-edge local-minimum statement
for these compression roots.

It does not prove:

- that every stable representative of AK(3) has the same local wall;
- that a two-edge path cannot cross the wall;
- that longer or nontriangular compression corridors fail;
- that AK(3) is stably nontrivial.

A blind second-neighborhood traversal is not licensed by this theorem and
would violate the local 1,000-node search cap. A null therefore redirects the
proof loop toward a symbolic ridge-crossing identity or a different
compression mechanism.
