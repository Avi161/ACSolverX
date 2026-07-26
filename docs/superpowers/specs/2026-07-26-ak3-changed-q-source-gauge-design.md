# AK(3) changed-q-source gauge design

Date: 2026-07-26

## Objective

Decide whether changing the surviving stabilizer source from the literal
word q to

\[
Q=qV
\]

can escape the full-q-traffic closure when \(V\) is a consequence of
passive q-free sources that remain distinct.

## General mechanism

Let \(F=F(X)*\langle q\rangle\), let passive q-free relators
\(S_1,\ldots,S_k\) generate the normal subgroup \(L\), and take
\(V\in L\). The word \(Q=qV\) is primitive via the transvection

\[
\tau_V(q)=qV.
\]

Straightening and deleting \(Q\) induces the evaluation

\[
\sigma_V(q)=V^{-1},
\qquad
\sigma_V|_{F(X)}=\operatorname{id}.
\]

Modulo \(L\), this is the ordinary q-deletion map. Every multiplier in
\(\langle\!\langle Q\rangle\!\rangle\) vanishes under \(\sigma_V\).
This remains true for later \(Q\)-traffic into the passive slots
themselves, so they return literally after deletion and restore all
other survivors to their ordinary-q endpoint by classical AC moves.

## AK specialization

At

\[
(\beta(R),W,D,q),
\]

keep \(D=t^{-1}zxz^{-1}\) literal while changing the final source to
\(Q=qD\). Subsequent traffic from \(Q\) into any other slot, including
the D-slot, disappears when \(Q\) is deleted.

The exact endpoint is

\[
(R_D,W_D,D),
\]

where

\[
R_D=D^{-1}x^3Dt^{-4},
\qquad
W_D=R_Dz^{-1}(D^{-1}xDt)D^{-1}.
\]

Explicit products of conjugates of \(D^{\pm1}\) restore this to
\((R,U,D)\), and one conjugate of \(R^{-1}\) changes \(U=RB\) back to
\(B\).

## Boundary

The proof requires \(V\) to be q-free and to lie in the normal closure
of passive source slots that remain literal through \(Q\)'s manufacture
and distinct until deletion. Later changes to those slots must come only
from \(Q\)-traffic. The changed source must remain \(Q\) and be deleted
first. It does not cover q-dependent \(V\), loss of the passive slots, a
further change to \(Q\), or primitive-pair compression.
