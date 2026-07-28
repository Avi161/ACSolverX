# An SU(2) obstruction to the last AK depth-three residue

## 1. Statement

Let

\[
H=\langle x,y\mid b\rangle,
\]

where

\[
\begin{aligned}
a&=x^3(yxyx^{-1}y^{-1})^{-4},\\
b&=\texttt{xyxyXYxyxYXYXyxYXY},\\
c&=yx^{-1}.
\end{aligned}
\]

The last first-image depth-three residue is equivalent to

\[
\operatorname{Cl}_H(a)\cap
a\operatorname{Cl}_H(c^\eta)\ne\varnothing
\quad\text{for some }\eta\in\{\pm1\}.
\tag{1.1}
\]

We construct a homomorphism \(\rho:H\to SU(2)\) for which the image
intersection is empty for both signs.  Consequently (1.1) has no
solution.

## 2. Algebraic quaternion representation

Write a unit quaternion as \((r,v)\in\mathbb R\oplus\mathbb R^3\), with

\[
(r,v)(s,w)=(rs-v\cdot w,\ rw+sv+v\times w).
\tag{2.1}
\]

Let m be a root in \((-1,-4/5)\) of

\[
P(T)=216T^3-144T^2-66T+169.
\tag{2.2}
\]

Such a root exists because

\[
P(-1)=-125<0,
\qquad
P(-4/5)=\frac{2381}{125}>0.
\tag{2.3}
\]

Choose unit vectors p and q with \(p\cdot q=m\), for example

\[
p=(0,0,1),
\qquad
q=(\sqrt{1-m^2},0,m).
\tag{2.4}
\]

Put

\[
R=\sqrt{\frac25},
\qquad
S=\sqrt{\frac35},
\qquad
X=(R,Sp),
\qquad
Y=(R,Sq).
\tag{2.5}
\]

These are unit quaternions and hence elements of \(SU(2)\).

## 3. The defining relator dies

Set \(G=YX\) and \(U=GYG^{-1}\).  Conjugation preserves scalar part,
so \(U=(R,Su)\) for a unit vector u.  Direct multiplication of two
equal-angle quaternions gives

\[
XUX-UXU
=S\bigl(2(R^2-S^2p\cdot u)-1\bigr)(p-u)
\tag{3.1}
\]

in the vector coordinate; the scalar coordinates agree.  Thus the
braid relation follows from

\[
p\cdot u=\frac{R^2-1/2}{S^2}=-\frac16.
\tag{3.2}
\]

Quaternion conjugation acts on \(\mathbb R^3\) by the corresponding
rotation.  Since \(G=YX\), Rodrigues' formula gives

\[
p\cdot u
=\frac{36m^3-24m^2-11m+24}{25}.
\tag{3.3}
\]

The equation that the right side equal \(-1/6\) is precisely
\(P(m)=0\).  Therefore

\[
XUX=UXU.
\tag{3.4}
\]

Now

\[
u=(yx)y(yx)^{-1}=yxyx^{-1}y^{-1}
\]

and b is the freely expanded word

\[
xux(uxu)^{-1}.
\]

Hence \(x\mapsto X\), \(y\mapsto Y\) kills b and defines

\[
\rho:H\longrightarrow SU(2).
\tag{3.5}
\]

## 4. Exact scalar parts

Let \(A=\rho(a)\) and \(C=\rho(c)\).  Write
\(R=\cos\theta\), \(S=\sin\theta\).  Since \(p\cdot u=-1/6\),

\[
\begin{aligned}
A_0:=\operatorname{scal}(A)
&=\cos(3\theta)\cos(4\theta)
  +(p\cdot u)\sin(3\theta)\sin(4\theta)\\
&=\frac{167}{125}\sqrt{\frac25}.
\end{aligned}
\tag{4.1}
\]

In particular,

\[
0<A_0<1,
\qquad
A_0^2=\frac{55778}{78125}>\frac12.
\tag{4.2}
\]

On the other hand, \(C=YX^{-1}\), so

\[
C_0:=\operatorname{scal}(C)
=R^2+S^2(p\cdot q)
=\frac{2+3m}{5}< -\frac{2}{25}<0.
\tag{4.3}
\]

Both \(C\) and \(C^{-1}\) have scalar part \(C_0\).

## 5. Separation of the class product

Suppose that an element conjugate to A were equal to \(AD\), where D
is conjugate in \(SU(2)\) to \(C^\eta\).  Write

\[
A=(A_0,v),
\qquad
D=(C_0,d).
\]

Conjugacy preserves scalar part.  Taking scalar parts of the supposed
equality therefore gives

\[
A_0C_0-v\cdot d=A_0,
\]

or

\[
v\cdot d=A_0(C_0-1).
\tag{5.1}
\]

But Cauchy--Schwarz and the unit quaternion equations give

\[
|v\cdot d|
\le
\sqrt{1-A_0^2}\sqrt{1-C_0^2}.
\tag{5.2}
\]

By (4.2),

\[
\sqrt{1-A_0^2}<A_0.
\]

By \(-1<C_0<0\),

\[
\sqrt{1-C_0^2}<1-C_0.
\]

Thus

\[
|v\cdot d|
<A_0(1-C_0),
\tag{5.3}
\]

whereas the absolute value demanded by (5.1) is exactly
\(A_0(1-C_0)\).  This contradiction works for both signs.

### Theorem 5.1

For \(\eta=\pm1\),

\[
\operatorname{Cl}_{SU(2)}(\rho(a))\cap
\rho(a)\operatorname{Cl}_{SU(2)}(\rho(c)^\eta)
=\varnothing.
\]

Therefore

\[
\boxed{
\operatorname{Cl}_H(a)\cap
a\operatorname{Cl}_H(c^\eta)=\varnothing
\quad(\eta=\pm1).}
\]

The last first-image depth-three residue has no solution.  Combined
with the other seventeen source-leaf certificates, this proves that no
row reached from the first proper AK image with at most three AC2
multiplications is primitive.
