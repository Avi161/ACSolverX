# AK(3) A--D finite-quotient module barrier

## Statement

Let

\[
B=BS(3,4)*\langle z\rangle
 =\langle x,y,z\mid yx^3y^{-1}=x^4\rangle,
\qquad
t=zxz^{-1},
\qquad
q=zy.
\]

Let \(H\) be any finite quotient of \(B\), and use the same letters for
the images of \(x,y,z,t,q\) in \(H\). Let \(M\) be an arbitrary right
\(\mathbb Z[H]\)-module. No finiteness, field, or characteristic
assumption is made on \(M\).

Fix \(\sigma\in\{+1,-1\}\), \(g\in H\), and \(v\in M\). Put

\[
S=v+vt+vt^2+vt^3.
\]

Assume the four-state relations

\[
vt^4=v,\qquad
vq(1+x+x^2)=Sz,\qquad
vg=-\sigma S.
\tag{1}
\]

Then

\[
vt=v
\qquad\text{and}\qquad
3v(qz^{-1})=4v.
\tag{2}
\]

Consequently \(vg=-4\sigma v\). For exactly the following three
literal representatives,

\[
(\sigma,g)=(+1,qz^{-1}),\qquad
(\sigma,g)=(-1,1),\qquad
(\sigma,g)=(-1,qz^{-1}),
\tag{3}
\]

relations (1) force \(v=0\).

This is a finite-quotient module barrier. It is not an arbitrary
conjugator closure theorem.

## Finite-order lemma

Let \(n=\operatorname{ord}_H(x)\). For every positive integer \(k\),

\[
\operatorname{ord}_H(x^k)=\frac{n}{\gcd(n,k)}.
\]

The elements \(x^3\) and \(x^4\) are conjugate, so they have equal
orders. Hence

\[
\gcd(n,3)=\gcd(n,4).
\]

The left side belongs to \(\{1,3\}\), while the right side belongs to
\(\{1,2,4\}\). Their only possible common value is \(1\). Therefore

\[
\gcd(n,12)=1.
\tag{4}
\]

This argument applies to every finite quotient and has no order bound.
The computational check for \(1\le n\le300\) is only a replay of (4).

Since \(t=zxz^{-1}\), the element \(t\) also has order \(n\). By (4)
there is an integer \(a\), chosen with \(0\le a<n\), such that

\[
4a\equiv1\pmod n.
\]

Using \(vt^4=v\) repeatedly gives \(vt^{4a}=v\). Since
\(t^{4a}=t\), it follows that

\[
vt=v.
\tag{5}
\]

Similarly there is an integer \(b\), chosen with \(0\le b<n\), such that
\(3b\equiv1\pmod n\). These two inverse congruences are what
`finite_cyclic_collapse_certificate` replays.

## Collapse of the HNN index gap

Put \(w=vz\). From \(zx=tz\) and (5),

\[
wx=vzx=vtz=vz=w.
\tag{6}
\]

The Baumslag--Solitar relation gives \(yx^3=x^4y\), so (6) yields

\[
wyx^3=wx^4y=wy.
\tag{7}
\]

Because \(3b\equiv1\pmod n\), equation (7) implies

\[
wyx=wy.
\tag{8}
\]

Now \(S=4v\), and \(q=zy\). The middle relation in (1), followed by
(8), gives

\[
3wy
=wy(1+x+x^2)
=vq(1+x+x^2)
=Sz
=4w.
\tag{9}
\]

Since \(wy=vq\), right multiplication of (9) by \(z^{-1}\) proves

\[
3v(qz^{-1})=4v.
\tag{10}
\]

Thus every finite quotient erases the \(3\)-versus-\(4\) HNN index gap
seen by a four-state vector. It may still detect the kernel component
of the particular element \(g\).

## The three literal representatives

Write \(h=qz^{-1}\). By (1) and (5),

\[
vg=-4\sigma v,
\tag{11}
\]

while (10) says \(3vh=4v\). The following arguments use only integer
identities and the fact that right multiplication by a group element
is invertible.

### \((\sigma,g)=(+1,h)\)

Here \(vh=-4v\). Together with \(3vh=4v\), this gives \(16v=0\).
Hence

\[
4(vh)=-16v=0.
\]

Invertibility of right multiplication by \(h\) gives \(4v=0\).
Equation \(vh=-4v\) then gives \(vh=0\), and invertibility gives
\(v=0\).

### \((\sigma,g)=(-1,1)\)

Here (11) is \(v=4v\), so \(3v=0\). Therefore

\[
3vh=(3v)h=0.
\]

Equation (10) gives \(4v=0\). Finally
\(v=4v-3v=0\).

### \((\sigma,g)=(-1,h)\)

Here \(vh=4v\). Together with \(3vh=4v\), this gives \(8v=0\).
Consequently

\[
2(vh)=8v=0.
\]

Invertibility of right multiplication by \(h\) gives \(2v=0\).
Thus \(vh=4v=0\), and a second use of invertibility gives \(v=0\).

No division by \(2\), \(3\), or \(4\) occurs in any of these
arguments.

## Scope

Result 56 says that the free-group projection of a relative
conjugator lies in one of three fibers:

\[
\sigma=+1:\ \pi(c)=qz^{-1},
\qquad
\sigma=-1:\ \pi(c)\in\{1,qz^{-1}\}.
\]

Those projection conditions do not say that the image \(g\) of \(c\)
in \(H\) is literally \(qz^{-1}\) or \(1\). A kernel component can
survive in \(H\), and the argument above makes no claim about such an
element. The conclusion \(v=0\) is therefore restricted to the three
literal equalities in (3). Any successful finite certificate for a
nonliteral member of a Result 56 fiber must use more than its
projection.
