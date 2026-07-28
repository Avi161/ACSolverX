# AK depth-four theory handoff

Date: 2026-07-28

Branch: `codex/proofs`

## Last complete theorem checkpoint

Commit `881ce85` proves Result 136: an exact quaternion representation
into \(SU(2)\) separates the final fixed-entry conjugacy-class product
from both orientations of the primitive target.  Consequently every
row reached from the first proper AK image with at most three AC2
multiplications is nonprimitive.

The standalone proof is
`literature/proofs/AK3_SU2_FIXED_COMMUTATOR_OBSTRUCTION.md`.
The complete stable-AC suite passed at that checkpoint:

```text
548 passed in 364.58s
```

AK(3), stable Andrews--Curtis, and Andrews--Curtis remain open.  Do not
mark the goal complete.

## Verified next frontier

Direct signed source-leaf enumeration gives 82 canonical row multisets
at AC2 depth four.  Twenty-eight already occur through depth three, so
there are exactly 54 new classes.  All 54 have coprime exponent vectors
and therefore survive the abelian primitivity gate.

Killing the majority source divides them by the number of surviving
minority conjugates:

| row length | minority leaves | classes |
|---:|---:|---:|
| 5 | 1 | 10 |
| 7 | 2 | 14 |
| 7 | 3 | 14 |
| 8 | 3 | 16 |

Thus the new geometric problem has no four-minority case: 24 classes
use at most two minority conjugates, while 30 use exactly three.

## Verified low-minority closure

`.scratch/depth4_provenance_check.py` reproduces the 82/28/54 counts
and the 10/14/30 split, then closes all 24 one/two-minority classes in
the established quotients

\[
Q_A=C_3*C_4,
\qquad
Q_B=C_2*C_3.
\]

For one minority leaf, exact cyclic normal-form comparison suffices.  For
two minority leaves, the checker uses the finite Bass--Serre connector
normal form from the depth-three proof.  It streams reduced connectors
through the safe bound, cyclically rotates both signed source images,
and compares the exactly reduced product with every cyclic target
rotation.

The terminating prune is also exact.  If the two source images have
syllable length \(L\), a connector has length \(k\), and the target has
length \(T\), the raw word has length \(R=2L+2k\).  Reduction to the
target loses exactly \(R-T\) syllables.  Since the first connector is
internally reduced, any changed connector syllables occur at its two
boundary seams and each costs at least one unit of this loss.  Hence a
contiguous block of at least \(k-(R-T)\) connector syllables survives
unchanged in the cyclic target.  A connector branch is discarded when
no such cyclic target subword exists.  During the remaining exact word
reduction, monotone accumulated syllable loss gives a second safe early
exit.  In every case where the subword prune is nonvacuous here,
\(R-T\le4<L\), so neither source word can disappear and expose an
additional internal connector seam.

The ten one-minority records have no connector bound.  Their exact
target-length data are

| signature | quotient | minority length | target length |
|---|---|---:|---:|
| `(5,1,4,-1,-4)` | \(Q_B\) | 14 | 30 |
| `(5,1,4,-1,-2)` | \(Q_B\) | 14 | 22 |
| `(5,1,4,-1,0)` | \(Q_B\) | 14 | 14 |
| `(5,1,4,-1,2)` | \(Q_B\) | 14 | 6 |
| `(5,1,4,-1,4)` | \(Q_B\) | 14 | 2 |
| `(5,4,1,-4,-1)` | \(Q_A\) | 6 | 26 |
| `(5,4,1,-4,1)` | \(Q_A\) | 6 | 22 |
| `(5,4,1,-2,-1)` | \(Q_A\) | 6 | 14 |
| `(5,4,1,-2,1)` | \(Q_A\) | 6 | 10 |
| `(5,4,1,0,-1)` | \(Q_A\) | 6 | 2 |

The fourteen two-minority connector records are

| signature | quotient | minority length | target length | connector bound | candidate products certified |
|---|---|---:|---:|---:|---:|
| `(7,2,5,-2,-5)` | \(Q_B\) | 14 | 48 | 12 | 86,632 |
| `(7,2,5,-2,-3)` | \(Q_B\) | 14 | 40 | 8 | 20,776 |
| `(7,2,5,-2,-1)` | \(Q_B\) | 14 | 32 | 4 | 4,312 |
| `(7,2,5,-2,1)` | \(Q_B\) | 14 | 24 | 2 | 1,568 |
| `(7,2,5,-2,3)` | \(Q_B\) | 14 | 16 | 2 | 1,568 |
| `(7,2,5,-2,5)` | \(Q_B\) | 14 | 8 | 2 | 1,568 |
| `(7,2,5,0,-1)` | \(Q_B\) | 14 | 4 | 2 | 1,568 |
| `(7,5,2,-5,-2)` | \(Q_A\) | 6 | 34 | 13 | 14,108,688 |
| `(7,5,2,-5,2)` | \(Q_A\) | 6 | 26 | 9 | 391,824 |
| `(7,5,2,-3,-2)` | \(Q_A\) | 6 | 22 | 7 | 65,232 |
| `(7,5,2,-3,2)` | \(Q_A\) | 6 | 14 | 3 | 1,728 |
| `(7,5,2,-1,-2)` | \(Q_A\) | 6 | 10 | 2 | 648 |
| `(7,5,2,-1,0)` | \(Q_A\) | 6 | 6 | 2 | 648 |
| `(7,5,2,-1,2)` | \(Q_A\) | 6 | 2 | 2 | 648 |

None contains a target.  The deterministic record hashes are

```text
54-signature SHA-256:
f6bdbc8bcb71936ccef6703577a727cc263729a603d9200c17981ba2284a50dd

24-certificate SHA-256:
5771323340314606a35f044cbca02a5d1ddf4a2bf88f2dc6b070ddda995f5199
```

Focused verification plus the established depth-three regression:

```text
tests/stable_ac/test_ak_depth_four_barriers.py
tests/stable_ac/test_ak_depth_three_free_product_barrier.py
7 passed in 22.97s
```

## Exact three-conjugate SU(2) lemma to formalize

If \(C_\alpha\) is the \(SU(2)\) conjugacy class with quaternion angle
\(\alpha\in[0,\pi]\), the product of three copies has angle interval

\[
C_\alpha^3:
\begin{cases}
[0,3\alpha],&0\le\alpha\le\pi/3,\\
[0,\pi],&\pi/3\le\alpha\le2\pi/3,\\
[3\alpha-2\pi,\pi],&2\pi/3\le\alpha\le\pi.
\end{cases}
\]

This follows by composing the standard two-class interval twice.  In
scalar form, with minority scalar s and target scalar t, separation is
certified by either

\[
s>\frac12,
\qquad
t<4s^3-3s,
\]

or

\[
s<-\frac12,
\qquad
t>4s^3-3s.
\]

The lemma is theoretically exact but has not yet been added to the
formal proof ledger or certificate tests.

## Numerical depth-four SU(2) lead

The following is **[unverified] numerical screening**, not a theorem.

When B is the majority source, impose \(B=1\) using equal-angle
quaternions with

\[
d=\frac{\cos^2\theta-1/2}{\sin^2\theta}.
\]

The two exact rational choices

\[
\cos^2\theta=\frac{37}{50}
\qquad\text{and}\qquad
\cos^2\theta=\frac25
\]

numerically separate 11 of the 15 three-minority signatures.  The four
not separated are

```text
(7,3,4,-1,-2)  vector (-5,6)
(8,3,5,-3, 5)  vector (-4,7)
(8,3,5,-1,-1)  vector (-4,5)
(8,3,5,-1, 3)  vector ( 0,1)
```

When A is the majority source, impose \(A=X^3Y^{-4}=1\) with
\(\angle X=\pi/3\), \(\angle Y=\pi/4\).  The rational axis dot
products

\[
m\in\left\{-\frac13,-\frac14,\frac8{15},\frac45\right\}
\]

numerically separate 13 of the 15 three-minority signatures.  The two
not separated are

```text
(8,5,3,-1,-1)  vector (-4,5)
(8,5,3,-1, 3)  vector ( 0,1)
```

Together these leads would close 24 of the 30 three-minority classes,
leaving six, if converted to exact radical or rational-interval
certificates.

## Exact continuation order

1. Optimize and finish the 24 one/two-minority free-product
   certificates.
2. Prove the three-class \(SU(2)\) angle interval and add a test for it.
3. Replace the numerical scalar comparisons above by exact radical or
   directed rational-interval certificates.
4. Attack the six remaining signatures using a different majority-
   killing representation or an exact triple-class calculation in
   \(C_3*C_4\) and \(C_2*C_3\).
5. Only after all 54 are closed may the ledger claim original-source
   depth-four closure; then repeat at the first proper image.
