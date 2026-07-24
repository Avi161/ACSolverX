# AK(3) immediate two-stabilization corridor design

Date: 2026-07-24

Status: theorem architecture derived; finite preflight checked; no certificate
yet. Every numerical preflight fact below is **[unverified]** until the
independent certificate is committed and replayed.

## Objective

The two previous proof attempts classified one-stabilization hidden corridors:

1. in the original basis;
2. in every primitive basis of total image length at most four.

Both exact candidates had minimum output floor 14. This attempt changes the
stable rank. It adjoins two defining generators and removes both original
generators in triangular order.

The first finite candidate is:

> **Immediate two-stabilization lemma [unverified].** There are freely reduced
> words \(w_z,w_t\) of length at most two and a freely/cyclically reduced
> braid template \(I_y(x,y,z,t)\) of length at most six, containing both new
> generators and exactly one \(y^{\pm1}\), such that two immediate
> substitution-and-removal steps produce a rank-two output of Aut-floor at
> most 12.

“Immediate” means that, after removing \(y\), one of the three relators
already contains exactly one \(x^{\pm1}\). No intervening AC multiplication
is allowed before the second removal. This makes the candidate finite and
theorem-shaped.

## General triangular-removal theorem

Let

\[
 P=\langle x,y\mid R,S\rangle
\]

present the trivial group. Adjoin

\[
 D_z=z^{-1}w_z(x,y),\qquad
 D_t=t^{-1}w_t(x,y)
\]

by two generalized stabilizations.

Let \(I_y(x,y,z,t)\) satisfy:

1. replacing \(z^{\pm1},t^{\pm1}\) by
   \(w_z^{\pm1},w_t^{\pm1}\) and freely reducing gives \(S\), up to cyclic
   rotation and inversion;
2. \(I_y\) contains exactly one \(y^{\pm1}\).

Use the two defining relators to replace every displayed
\(w_z^{\pm1},w_t^{\pm1}\) block in a freely expanded spelling of \(S\).
This is an AC1--AC3 composite by the same occurrence-replacement proof as the
one-stabilization theorem. Rotate \(I_y\) to \(y^\varepsilon q\), solve
\(y=e_y(x,z,t)\), and remove \(y,I_y\) by Lemma 11.

The three surviving relators are

\[
 R_y=R[y\mapsto e_y],\quad
 Z_y=(z^{-1}w_z)[y\mapsto e_y],\quad
 T_y=(t^{-1}w_t)[y\mapsto e_y].
\]

If one of these, say \(J_x\), contains exactly one \(x^{\pm1}\), rotate it,
solve \(x=e_x(z,t)\), and remove \(x,J_x\) by a second Lemma-11 application.
Substituting \(x=e_x\) in the other two relators leaves a balanced
presentation on \(z,t\), which may be stably relabelled to \(x,y\).

This proves stable equivalence of the input and output. The dependency graph
is triangular:

```text
y depends on x,z,t
x depends only on z,t after y is eliminated
```

The reverse removal order is included by swapping the names \(x,y\).

## Exact finite family

Use the AK(3) source words:

```text
R = xxxYYYY
S = xyxYXY
```

Enumerate:

1. every nonempty freely reduced \(w_z,w_t\) over `xXyY` with individual
   lengths one or two: 16 choices each, 256 ordered pairs;
2. every freely and cyclically reduced template over `xXyYzZtT` of length
   two through six;
3. templates with exactly one `y/Y`, at least one `z/Z`, and at least one
   `t/T`;
4. only templates whose simultaneous literal expansion
   `z -> w_z`, `t -> w_t` freely reduces to an orientation of `S`;
5. each of the three surviving relators as the possible second isolator,
   accepting exactly one `x/X`.

For every accepted triangular certificate:

1. solve \(y=e_y\);
2. independently derive \(R_y,Z_y,T_y\);
3. solve \(x=e_x\) from the named second isolator;
4. substitute \(x=e_x\) in the other two relators;
5. relabel \(z\mapsto x,t\mapsto y\);
6. canonicalize and compute the complete Aut-floor and witness.

The finite candidate is proved exactly when one output floor is at most 12.

## Preflight observations

The disposable preflight, using separate local word routines, reported:

| quantity | preflight value |
|---|---:|
| structural templates before defining-word expansion | 43,296 |
| accepted literal braid identities | 31,232 |
| distinct rank-3 intermediates | 3,224 |
| triangular certificates before output deduplication | 18,528 |
| distinct rank-2 outputs | 352 |
| minimum output floor | 13 |

The output-floor distribution was:

```text
13: 64
14: 128
16: 16
23: 16
24: 40
25: 16
27: 16
28: 40
43: 16
```

The sampled floor-13 rows had AK(3)'s Aut representative
`YXYxyx | YYYYxxx`; the certificate must check all 64 before stating that as
a result.

## Fixed braid-factor subfamily

The especially natural choice \(w_z=xy,w_t=yx\) illustrates why literal
word order is load-bearing.

The valid factorization is

\[
 xyxy^{-1}x^{-1}y^{-1}
 =(xy)x\,y^{-1}(yx)^{-1},
\]

giving the template

\[
 zxy^{-1}t^{-1}.
\]

The invalid ordering

\[
 (xy)x(yx)^{-1}y^{-1}
\]

freely reduces to \(xy^{-1}\), not the braid relator. A nine-move solve found
from the tuple derived using that invalid ordering is quarantined and is not
evidence about AK(3).

For the valid fixed defining words, the preflight found 180 accepted
templates but only 20 distinct rank-3 tuples. Every one has at least two
\(x^{\pm1}\)-occurrences in each surviving relator, so none admits the
immediate second removal. A separate 1,000-pop rank-3 search on each of the
20 found no solution and minimum total length 16. Those bounded search facts
are corroboration only; the structural exact-one-letter census is the
load-bearing negative.

## Certificate architecture

Create:

- `literature/proofs/AK3_TWO_STABILIZATION.md`;
- `experiments/stable_ac/rank3_compression/two_stabilization.py`;
- `experiments/stable_ac/rank3_compression/two_stabilization_certificate.py`;
- `tests/stable_ac/test_two_stabilization.py`;
- `results/stable_ac/theory/ak3_two_stabilization.json`;
- `results/stable_ac/theory/AK3_TWO_STABILIZATION.md`.

The enumerator must expose pure interfaces for:

- simultaneous substitution of `z,t`;
- exact isolator solution for either old generator;
- derivation of the three rank-3 relators;
- second removal and rank-two relabelling;
- deterministic enumeration and complete trace hashing.

The verifier must independently:

1. regenerate all 256 defining-word pairs and 43,296 structural templates;
2. replay every accepted source identity literally;
3. recompute both isolator expressions and the final relators;
4. verify every Aut witness;
5. rerun the complete enumeration and compare counts, trace, output
   partition, floors, and verdict.

No AC graph search is needed for the candidate decision. The fixed-pair
1,000-pop searches may be recorded separately but cannot affect the verdict.

## Expected adjudication

The preflight predicts `REFUTED` with minimum 13. That prediction is not a
certificate.

If the certificate instead finds floor at most 12, expand the two
stabilizations, both compression phases, both removals, and the classical
endpoint certificate into an independently replayed AC1--AC5 proof.

If it confirms minimum 13, do not increase the word/template bounds
automatically. The next theorem permits one **second-stage compression**
before removing \(x\): after the \(y\)-removal, use the surviving defining
relators to replace one additional displayed block in \(R_y,Z_y\), or \(T_y\)
and then seek the unique \(x\)-occurrence. This changes the removal mechanism
rather than merely increasing a radius.

## Constraints

- New task files only; do not modify existing solvers, runners, notebooks, or
  certificates.
- The local AC search cap remains 1,000; the word/template census is a finite
  equation decision, not an AC graph search.
- CPU only; use `.venv/bin/python3`.
- Commit and push `codex/proofs` at least every twenty minutes.
- No pull request or merge.
