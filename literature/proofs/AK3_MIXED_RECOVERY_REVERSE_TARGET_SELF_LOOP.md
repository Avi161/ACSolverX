# Reverse-target mixed recovery and one \(D\)-catalyst is an AK(3) self-loop

Date: 2026-07-24

Status: **PROVEN** for every quotient-equal recovery word and every relative
conjugator in one subsequent multiplication targeting \(D\). There is no
word-length or conjugator-length bound. This closes a stable mechanism; it
does not trivialize AK(3).

## 1. Setup

Put

\[
R=x^3t^{-4},\qquad D=t^{-1}zxz^{-1}.
\tag{1.1}
\]

Let \(U(x,t)\) be an arbitrary word satisfying

\[
U=t
\quad\text{in}\quad
\langle x,t\mid R\rangle ,
\tag{1.2}
\]

and write

\[
w=\overline{xU},\qquad B_U=z^{-1}w.
\tag{1.3}
\]

The bar denotes free reduction. In string notation,

```text
R   = xxxTTTT
B_U = Z w
D   = TzxZ
```

The arbitrary-recovery construction stably reaches

\[
(R,B_U,D)
\tag{1.4}
\]

from AK(3), so this rank-three tuple presents the trivial group.

Directly eliminating \(z=w\) through \(B_U\) gives

\[
Q(U)=(R,S_0(U)),
\qquad
S_0(U)=t^{-1}wxw^{-1}.
\tag{1.5}
\]

The arbitrary-recovery self-loop theorem proves

\[
Q(U)\sim_{\mathrm{AC1-3}}\operatorname{AK}(3).
\tag{1.6}
\]

The forward one-\(D\) theorem targets \(B_U\), removes that modified slot,
and retains \(D\). Here the roles are reversed: one multiplication targets
\(D\), the modified \(D\)-slot is removed, and the restored source
\(B_U\) survives.

## 2. Statement

### Theorem 2.1

Independently conjugate and orient \(D\) and \(B_U\), perform one relator
multiplication with \(D\) as target and \(B_U\) as source, and then restore
the source slot to exactly \(B_U\). Suppose the new target has one
\(z^{\pm1}\)-occurrence after free and cyclic reduction.

Up to target inversion and cyclic conjugation, the new target is one of

\[
z^{-1}t^{-1}wx,
\qquad
z^{-1}twx^{-1}.
\tag{2.1}
\]

Using that target as a generator isolator and applying the
substitution-and-removal stable composite leaves a rank-two pair
classically AC-equivalent to \(Q(U)\), hence to AK(3).

Thus arbitrary recovery followed by one arbitrary-relative-conjugator
multiplication targeting \(D\) is a classical self-loop after elimination.

## 3. Why reversing the factors creates no new isolator

The bridge argument in
`literature/proofs/AK3_MIXED_RECOVERY_ONE_D_SELF_LOOP.md`, Sections 3--4,
classifies cyclic conjugacy classes of products of arbitrary conjugates and
orientations of \(B_U\) and \(D\).

For completeness, normalize the relative conjugator to a shortest bridge
between the axes of the two cyclically reduced factors. If their axes are
disjoint, the cyclically reduced product has the form

\[
V_DcV_Bc^{-1},
\qquad c\ne1,
\tag{3.1}
\]

where \(V_D,V_B\) are signed cyclic rotations. Its \(z\)-incidence is

\[
\nu_z(V_DcV_Bc^{-1})
=\nu_z(D)+\nu_z(B_U)+2\nu_z(c)
=3+2\nu_z(c)\ge3.
\tag{3.2}
\]

It cannot be a one-\(z\) isolator.

If the axes intersect, the bridge is empty and the residue is the cyclic
reduction of \(V_DV_B\). Factor order is irrelevant at this classification
stage because

\[
V_DV_B
\quad\text{and}\quad
V_BV_D
\tag{3.3}
\]

are conjugate, hence have the same cyclic reduction class. Whole-target
inversion again normalizes one factor orientation and transfers the
relative sign to the other. Therefore the complete forced-seam analysis
from the forward theorem applies unchanged.

Reducing the three initial \(z^{\pm1}\)-occurrences to one must cancel the
unique positive \(z\) from \(D^{\pm1}\) with the unique \(z^{-1}\) from
\(B_U\). The two signed seams give precisely

\[
\operatorname{cyc}(z^{-1}t^{-1}wx),
\qquad
\operatorname{cyc}(z^{-1}twx^{-1}),
\tag{3.4}
\]

which proves the completeness of (2.1). This symmetry concerns only the
cyclic class of the modified target. It does not identify the surviving
relator after elimination; that survivor must be computed with the
target/source roles fixed.

## 4. The surviving \(B_U\)-slot

The two targets in (2.1) isolate

\[
e_+(U)=t^{-1}wx,
\qquad
e_-(U)=twx^{-1},
\tag{4.1}
\]

where \(z=e_\pm(U)\). Any conjugation or inversion temporarily applied to
the source to realize the multiplication is undone before elimination, so
the surviving source is exactly

\[
B_U=z^{-1}w.
\tag{4.2}
\]

After substitution its two possible values are

\[
C_\pm(U)=e_\pm(U)^{-1}w.
\tag{4.3}
\]

The positive branch satisfies the literal free identity

\[
\begin{aligned}
C_+(U)
&=(t^{-1}wx)^{-1}w\\
&=x^{-1}w^{-1}tw\\
&=w^{-1}S_0(U)^{-1}w.
\end{aligned}
\tag{4.4}
\]

The negative branch satisfies

\[
\begin{aligned}
C_-(U)
&=(twx^{-1})^{-1}w\\
&=xw^{-1}t^{-1}w\\
&=(t^{-1}w)^{-1}S_0(U)(t^{-1}w).
\end{aligned}
\tag{4.5}
\]

Thus \(C_+\) is a conjugate of \(S_0^{-1}\), while \(C_-\) is a conjugate
of \(S_0\). One AC1 move when necessary and one AC3 move give

\[
(R,C_\pm(U))
\sim_{\mathrm{AC1-3}}
(R,S_0(U))
=Q(U).
\tag{4.6}
\]

Combining (4.6) with (1.6) proves Theorem 2.1.

The deletion of the modified \(D\)-slot is the
substitution-and-removal stable composite, not a bare AC5 move. Its
trivial-group hypothesis holds by (1.4), and no elementary move-count bound
is claimed.

## 5. Scope

The theorem is unbounded simultaneously in the recovery word \(U\) and in
the relative conjugator used by the multiplication. It covers the order

1. change \(B=z^{-1}xt\) to \(B_U=z^{-1}xU\) using consequences of \(R\);
2. use one \(B_U^{\pm1}\)-multiplication with \(D\) as target;
3. restore the source \(B_U\); and
4. eliminate \(z\) through the modified \(D\)-slot.

It does not cover a \(D\)-factor used before recovery is complete, two or
more \(D\)-factors, a multiplication targeting \(R\), a changed retained
relator or recovery equation, an isolator with several
\(z^{\pm1}\)-occurrences, a second stabilization, or dual-source
primitive-pair compression.

AK(3) remains open.
