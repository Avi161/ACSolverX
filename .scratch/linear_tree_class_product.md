# Exact SU(2) obstruction to the Result 135 class product

## Outcome

There is a rigorous separating homomorphism

\[
\rho:H=\langle x,y\mid b\rangle\longrightarrow SU(2)
\]

for which

\[
\operatorname{Cl}_{SU(2)}(\rho(a))\cap
\rho(a)\operatorname{Cl}_{SU(2)}(\rho(c)^\eta)=\varnothing
\qquad(\eta=\pm1).
\]

Consequently

\[
\boxed{\operatorname{Cl}_{H}(a)\cap a\operatorname{Cl}_{H}(c^\eta)
=\varnothing\quad\text{for both }\eta=\pm1.}
\]

Thus the exact residue in Result 135 is obstructed, rather than solved.

## Construction

Write unit quaternions as \((r,v)\in\mathbb R\oplus\mathbb R^3\),
so they model \(SU(2)\).  Let \(m\) be a root in \((-1,-4/5)\) of

\[
P(T)=216T^3-144T^2-66T+169.
\tag{1}
\]

Such a root exists because \(P(-1)=-125<0\) and
\(P(-4/5)=2381/125>0\).  Put

\[
p=(0,0,1),\qquad q=(\sqrt{1-m^2},0,m),
\]

and define

\[
X=\left(\sqrt{\frac25},\sqrt{\frac35}\,p\right),\qquad
Y=\left(\sqrt{\frac25},\sqrt{\frac35}\,q\right).
\tag{2}
\]

Both are unit quaternions.  Send \(x\mapsto X\), \(y\mapsto Y\).

## Verification that the relator dies

Set \(G=YX\) and \(U=GYG^{-1}\).  If

\[
R=\sqrt{\frac25},\qquad S=\sqrt{\frac35},
\]

then \(X=(R,Sp)\) and \(U=(R,Su)\) for a unit vector \(u\).
For two equal-angle unit quaternions \((R,Sp)\) and \((R,Su)\), direct
quaternion multiplication gives

\[
XUX-UXU
=S\bigl(2(R^2-S^2p\!\cdot\!u)-1\bigr)(p-u)
\tag{3}
\]

in the vector coordinate (the scalar coordinates already agree).
Hence the braid relation follows if

\[
p\cdot u=\frac{R^2-1/2}{S^2}=-\frac16.
\tag{4}
\]

Conjugation by \((R,Sv)\) rotates \(\mathbb R^3\) through angle
\(2\theta\) about \(v\), where \(R=\cos\theta\), \(S=\sin\theta\).
As \(u=R_YR_Xq\), Rodrigues' formula, with \(p\cdot q=m\), gives

\[
p\cdot u
=\frac{36m^3-24m^2-11m+24}{25}.
\tag{5}
\]

Equation (1) is exactly the assertion that the right side of (5) is
\(-1/6\).  Thus (3) proves \(XUX=UXU\).

Now \(u=(yx)y(yx)^{-1}=yxyXY\), and free expansion gives

\[
b=xux(uxu)^{-1}
=\texttt{xyxyXYxyxYXYXyxYXY}.
\]

Therefore \(b(X,Y)=1\), and (2) defines the claimed homomorphism
\(\rho:H\to SU(2)\).

## Scalar parts of a and c

The freely reduced identity

\[
a=x^3u^{-4}=\texttt{xxxyxYYYYXY}
\]

shows that, if \(\theta\in(0,\pi)\) is defined by
\(\cos\theta=\sqrt{2/5}\), then the scalar part of
\(A=\rho(a)=X^3U^{-4}\) is

\[
\begin{aligned}
A_0
&=\cos(3\theta)\cos(4\theta)
 +(p\cdot u)\sin(3\theta)\sin(4\theta)\\
&=\frac{167}{125}\sqrt{\frac25}.
\end{aligned}
\tag{6}
\]

In particular \(0<A_0<1\), and

\[
A_0^2=\frac{55778}{78125}>\frac12.
\tag{7}
\]

For \(C=\rho(c)=YX^{-1}\), quaternion multiplication instead gives

\[
C_0=R^2+S^2(p\cdot q)=\frac{2+3m}{5}< -\frac{2}{25}<0,
\tag{8}
\]

because \(m<-4/5\).  Notice that \(C\) and \(C^{-1}\) have the same
scalar part and indeed the same conjugacy class in \(SU(2)\).

## Separation of the class product

Suppose, for contradiction, that a conjugate of \(A\) belongs to
\(A\operatorname{Cl}(C^\eta)\).  Taking scalar parts (equivalently,
half-traces) and conjugating the whole equality reduces this to

\[
\operatorname{scal}(AD)=A_0
\tag{9}
\]

for some conjugate \(D=(C_0,d)\) of \(C^\eta\).  Write
\(A=(A_0,v)\).  Equation (9) is

\[
v\cdot d=A_0(C_0-1).
\tag{10}
\]

But Cauchy--Schwarz, (7), and (8) imply

\[
|v\cdot d|
\le \sqrt{1-A_0^2}\sqrt{1-C_0^2}
< A_0(1-C_0).
\tag{11}
\]

Indeed \(A_0>\sqrt{1-A_0^2}\) by (7), while
\(1-C_0>\sqrt{1-C_0^2}\) because \(-1<C_0<0\).  The right side of
(11) is exactly the absolute value required by (10), a contradiction.

This argument excludes the full ambient \(SU(2)\) conjugacy class, not
merely conjugators lying in \(\rho(H)\), so it is a fortiori a valid
quotient obstruction for H.

## Geometric interpretation

If \(A\) and \(C\) have quaternion angles \(\alpha,\gamma\in(0,\pi)\),
the trace equation requires

\[
\tan(\gamma/2)\le |\tan\alpha|.
\]

Here (7) gives \(\alpha<\pi/4\), whereas (8) gives
\(\gamma>\pi/2\), so the required inequality fails with room to spare.
