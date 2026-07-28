# An exact period-two witness for the hardest depth-four recurrence

## Status

After imposing \(c^2=1\), the hardest unresolved depth-four recurrence has
an exact solution. The final row is \(Z=t\) literally, not merely conjugate
to \(t\).

This proves that the period-two quotient is blind to the class. It does not
lift the witness to the original free group \(F(c,t)\), so the original
depth-four class remains open.

## 1. Quotient coordinates

Put
\[
G=\langle c,t\mid c^2=1\rangle=C_2*\mathbb Z,
\qquad
H=\ker(G\to C_2)=F(p,q),
\]
where
\[
p=t,\qquad q=ctc.
\]
Conjugation by \(c\) induces the involution
\[
\alpha(p)=q,\qquad\alpha(q)=p.
\]
Writing an element as \(wc^\epsilon\), with \(w\in H\), gives
\[
(u,\epsilon)(v,\delta)
=\bigl(u\alpha^\epsilon(v),\epsilon+\delta\bmod2\bigr).
\tag{1}
\]

The source rows reduce to
\[
A=t^{-2}ct^{-2}ct^2c=ac,\qquad
B=t^{-3}ctctc=bc,
\tag{2}
\]
with
\[
a=p^{-2}q^{-2}p^2,\qquad b=p^{-3}qp.
\tag{3}
\]

Use upper-case letters for inverses:
\[
P=p^{-1},\qquad Q=q^{-1}.
\]
Thus
\[
a=PPQQpp,\qquad b=PPPqp.
\]

## 2. The witness

Choose the four zero-parity conjugators
\[
h_0=QQppp,\qquad h_1=1,\qquad
h_2=Qppp,\qquad h_3=p.
\tag{4}
\]
The resulting rows have normal forms
\[
\begin{array}{c|c}
\text{row}&\text{normal form}\\ \hline
R&PPqPq\\
S&(PPPqqPqq)c\\
X=h_2Sh_2^{-1}&(qPQp)c\\
Y=h_3Sh_3^{-1}&(PPqqPq)c\\
e&=p.
\end{array}
\tag{5}
\]

Here \(e\) is the final target and is literally \(p=t\).

## 3. Exact free reductions

The recurrence begins with
\[
R=Ah_0B^{-1}h_0^{-1},\qquad
S=Bh_1R^{-1}h_1^{-1}.
\]
Using (1)--(4), their freely reduced \(H\)-components are
\[
\begin{aligned}
r
 &=a\,\alpha(h_0)b^{-1}h_0^{-1}\\
 &=PPQQpp\;PPqqq\;PQppp\;PPPqq\\
 &\longrightarrow PPqPq,
\end{aligned}
\tag{6}
\]
and
\[
\begin{aligned}
s
 &=b\,\alpha(r^{-1})\\
 &=PPPqp\;PqPqq\\
 &\longrightarrow PPPqqPqq.
\end{aligned}
\tag{7}
\]

The two conjugates of \(S\) are
\[
\begin{aligned}
x
 &=h_2s\alpha(h_2^{-1})\\
 &=Qppp\;PPPqqPqq\;QQQp\\
 &\longrightarrow qPQp,
\end{aligned}
\tag{8}
\]
and
\[
\begin{aligned}
y
 &=h_3s\alpha(h_3^{-1})\\
 &=p\;PPPqqPqq\;Q\\
 &\longrightarrow PPqqPq.
\end{aligned}
\tag{9}
\]

Because \(X\) and \(Y\) are odd, the \(H\)-component of
\(XR^{-1}Y\) is
\[
x\alpha(r^{-1})\alpha(y).
\]
Its complete free reduction is
\[
\begin{aligned}
qPQpPqPqqQQppQp
&\to qPQqPqqQQppQp
\to qPPqqQQppQp\\
&\to qPPqQppQp
\to qPPppQp
\to qPpQp\\
&\to qQp
\to p.
\end{aligned}
\tag{10}
\]
Therefore
\[
e=XR^{-1}Y=p.
\tag{11}
\]
Equivalently,
\[
R=Ye^{-1}X,
\tag{12}
\]
so the exact necessary-and-sufficient backward class system is solved.

## 4. Independent direct replay in \(C_2*\mathbb Z\)

Let \(T=t^{-1}\). Substituting \(p=t,\ q=ctc\) and reducing only by
\[
cc=1,\qquad tT=Tt=1
\]
gives
\[
\begin{array}{c|l}
\text{element}&\text{reduced word}\\ \hline
A&TTcTTcttc\\
B&TTTctctc\\
h_0&cTTcttt\\
h_1&1\\
h_2&cTcttt\\
h_3&t\\
R&TTctcTctc\\
S&TTTcttcTctt\\
U&TTcttcTc\\
Y&TTcttcTct.
\end{array}
\tag{13}
\]
Direct multiplication verifies
\[
\begin{aligned}
R&=Ah_0B^{-1}h_0^{-1},\\
S&=BR^{-1},\\
U&=Rh_2S^{-1}h_2^{-1},\\
Y&=h_3Sh_3^{-1}.
\end{aligned}
\tag{14}
\]
The last two words in (13) satisfy
\[
Y=Ut
\]
as reduced words. Hence
\[
Z=U^{-1}Y=t
\tag{15}
\]
literally.

The Bass--Serre translation lengths are
\[
\ell_T(R)=8,\qquad
\ell_T(S)=\ell_T(U)=\ell_T(Y)=6.
\]
Thus the witness lies in the equal-length hyperbolic-\(S\) alternative. It
does not conflict with the independent theorem excluding elliptic \(S\).

## 5. Consequence and exact certificate

The quotient recurrence is nonempty, so no obstruction factoring through
\(c^2=1\) can close the original hardest depth-four class.

The checker
\[
\texttt{experiments/stable\_ac/depth4\_period\_two\_witness.py}
\]
replays (13)--(15) with a separate reduced-word implementation for
\(C_2*\mathbb Z\). In particular it verifies both
\[
XR^{-1}Y=t,\qquad Yt^{-1}X=R
\]
and the original four recurrence equations.

The only unresolved issue is lifting: the cancellations in this witness may
use \(c^2=1\) essentially. No free-group witness is asserted.
