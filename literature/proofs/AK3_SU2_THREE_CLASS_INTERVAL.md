# The exact \(SU(2)\) three-class interval and five depth-four certificates

## 1. Products of two classes

Write

\[
C_\alpha=\{(\cos\alpha,\sin\alpha\,u):u\in S^2\},
\qquad 0\le\alpha\le\pi .
\]

If \(u,v\) are unit vectors, the scalar part of a product from
\(C_\alpha C_\beta\) is

\[
\cos\alpha\cos\beta-\sin\alpha\sin\beta\,u\mathbin{\cdot}v.
\]

As \(u\mathbin{\cdot}v\) varies over \([-1,1]\), the attainable product
angles are exactly

\[
\left[|\alpha-\beta|,\,
\pi-|\pi-\alpha-\beta|\right].
\tag{1}
\]

## 2. Products of three equal classes

**Theorem.** The angle set of \(C_\alpha^3\) is

\[
\begin{cases}
[0,3\alpha],&0\le\alpha\le\pi/3,\\
[0,\pi],&\pi/3\le\alpha\le2\pi/3,\\
[3\alpha-2\pi,\pi],&2\pi/3\le\alpha\le\pi.
\end{cases}
\tag{2}
\]

Indeed, (1) first gives every intermediate angle

\[
0\le\delta\le 2\min(\alpha,\pi-\alpha).
\]

The product map from \(C_\alpha^3\) to its scalar part is continuous and
its domain is connected, so its angle image is one interval. Its lower
endpoint is

\[
\min_\delta|\delta-\alpha|=\max(0,3\alpha-2\pi).
\]

The upper endpoint is \(\pi\) precisely when
\(\delta=\pi-\alpha\) lies in the displayed intermediate interval,
equivalently when \(\alpha\ge\pi/3\). Otherwise the upper endpoint is
\(3\alpha\). This proves (2).

If \(s=\cos\alpha\) is the source scalar and \(t\) is the target scalar,
(2) gives the exact separation criteria

\[
s>\frac12,\qquad t<4s^3-3s,
\tag{3}
\]

or

\[
s<-\frac12,\qquad t>4s^3-3s.
\tag{4}
\]

The same interval applies to every sign pattern because a quaternion and
its inverse have the same scalar part and hence the same \(SU(2)\)
conjugacy class.

## 3. Majority-killing representations

Let

\[
A=x^3y^{-4},\qquad B=xyxy^{-1}x^{-1}y^{-1}.
\]

To kill \(B\), take equal-angle quaternions

\[
X=(r,\sqrt{1-r^2}\,p),\qquad
Y=(r,\sqrt{1-r^2}\,q).
\]

Direct quaternion multiplication proves \(XYX=YXY\) when

\[
p\mathbin{\cdot}q=\frac{r^2-1/2}{1-r^2}.
\tag{5}
\]

For the certificates below, \(r^2=37/50\), so the right side of (5) is
\(12/13\). We use axes

\[
p=(0,0,1),\qquad q=(5/13,0,12/13).
\tag{6}
\]

To kill \(A\), take \(X\) of angle \(\pi/3\) and \(Y\) of angle
\(\pi/4\). Then

\[
X^3=Y^4=-1
\]

for arbitrary axes. The two certificates use axis dot products
\(-1/3\) and \(4/5\).

These identities are exact; the directed interval computation is used
only to evaluate the minority and target scalar inequalities.

## 4. Five exact certificates

For a signature \((N,n_A,n_B,c_A,c_B)\), the primitive target vector is

\[
(p,q)=(3c_A+c_B,-4c_A-c_B).
\tag{7}
\]

The following table gives the exact representation and a decimal display
of the certified rational-interval margin
\((4s^3-3s)-t\). The proof uses the full rational lower endpoint, not the
decimal display.

| signature | target vector | representation | margin lower bound |
|---|---:|---|---:|
| \((7,3,4,-3,2)\) | \((-7,10)\) | (6), kill \(B\) | \(0.254346492566\) |
| \((7,3,4,-3,4)\) | \((-5,8)\) | (6), kill \(B\) | \(0.039467213294\) |
| \((7,4,3,-2,-3)\) | \((-9,11)\) | kill \(A\), axes \(-1/3\) | \(0.011333735141\) |
| \((8,3,5,-3,1)\) | \((-8,11)\) | (6), kill \(B\) | \(0.356421931301\) |
| \((8,5,3,-3,1)\) | \((-8,11)\) | kill \(A\), axes \(4/5\) | \(0.108275845615\) |

Every source interval lies strictly above \(1/2\), and every margin is
strictly greater than \(1/1000\). Therefore (3) excludes the primitive
target from the product of the three arbitrary signed minority
conjugacy classes.

The replayable exact certificate is
experiments/stable_ac/depth4_three_class_certificates.py. It constructs
outward rational intervals for every square root by integer square root
at scale \(10^{30}\), evaluates every quaternion word with outward
rounding, and proves all five strict inequalities. Its regression test is
tests/stable_ac/test_ak_depth_four_three_class.py.

## 5. Consequence

The 24 low-minority free-product certificates, the 19 bi-invariant
metric certificates, and the five certificates above close 48 of the 54
new depth-four source-leaf classes. Exactly the six previously isolated
signatures remain:

\[
\begin{array}{c|c}
\text{signature}&\text{primitive vector}\\ \hline
(7,3,4,-1,-2)&(-5,6)\\
(8,3,5,-3,5)&(-4,7)\\
(8,3,5,-1,-1)&(-4,5)\\
(8,3,5,-1,3)&(0,1)\\
(8,5,3,-1,-1)&(-4,5)\\
(8,5,3,-1,3)&(0,1).
\end{array}
\]

This is an exact reduction, not a proof of depth-four closure.
