# Diagonal defect reduction to one boundary row

## Status and scope

For the complete endpoint scalar \(u_{ij}\in\mathbb F_2\), put

\[
 J_{ij}:=u_{i,j+1}+u_{ij},
 \qquad
 \mathcal D_{ij}:=u_{i+1,j+1}+u_{ij}.
 \tag{0.1}
\]

The completed \(j\)-edge theorem is

\[
 \boxed{J_{ij}=[i-j=0]+[i-j=1]\qquad(i,j\geq0).}
 \tag{0.2}
\]

This note combines (0.2) with the already proved four-corner identity to
show that \(\mathcal D_{ij}\) is constant in \(j\). It does not prove that
this constant is zero. The remaining diagonal target is the one-parameter
family

\[
 \boxed{\mathcal D_{i0}=0\qquad(i\geq0),}
 \tag{0.3}
\]

which remains open.

## 1. Inputs

In the chamber \(d=i-j\geq1\), the positive \(j\)-edge theorem is

\[
 J_{ij}=[d=1].
 \tag{1.1}
\]

See <code>AK3_POSITIVE_J_EDGE_RAW_LOAD.md</code>, equations (6.1)--(6.4).
In the complementary chamber \(e=j-i\geq0\), the inverse theorem is

\[
 J_{ij}=[e=0]=[d=0].
 \tag{1.2}
\]

See <code>AK3_OLD_NEW_INVERSE_Q_CONNECTORS.md</code>, equations
(7.28)--(7.32). Equations (1.1)--(1.2) have disjoint domains and together
cover every integer value of \(d=i-j\), giving (0.2).

The exact four-corner identity is

\[
 \boxed{
 J_{i+1,j+1}+J_{ij}
 =\mathcal D_{i,j+1}+\mathcal D_{ij}.}
 \tag{1.3}
\]

It follows directly from the four endpoint values and contains no
covariance assumption. See
<code>.scratch/period_two_augmented_cut_covariance.md</code>, equations
(5.6)--(5.7), lines 440--457.

## 2. Constancy of the diagonal defect

The shift \((i,j)\mapsto(i+1,j+1)\) preserves \(i-j\). Therefore (0.2)
gives

\[
 J_{i+1,j+1}=J_{ij}.
 \tag{2.1}
\]

Substitution in (1.3) gives

\[
 \mathcal D_{i,j+1}+\mathcal D_{ij}=0,
 \qquad
 \boxed{\mathcal D_{i,j+1}=\mathcal D_{ij}.}
 \tag{2.2}
\]

Induction on \(j\) proves

\[
 \boxed{\mathcal D_{ij}=\mathcal D_{i0}\qquad(i,j\geq0).}
 \tag{2.3}
\]

Thus the full diagonal identity \(\mathcal D_{ij}=0\) is equivalent to the
boundary family (0.3). Equation (2.3) is a reduction, not a proof of that
boundary family.

### Complete augmented cochain equality

The same global \(j\)-edge theorem closes the formerly conditional
four-corner cochain equality. In the notation of
<code>.scratch/period_two_augmented_cut_covariance.md</code>, let

\[
\begin{aligned}
 a&=a_{B+D_{ij}},\\
 b&=a_{B+D_{i,j+1}}+a_{B+D_{ij}},\\
 f&=a_{B+D_{i+1,j+1}}+a_{B+D_{ij}},\\
 g&=a_{B+D_{i+1,j+2}}+a_{B+D_{i+1,j+1}}
   +a_{B+D_{i,j+1}}+a_{B+D_{ij}}.
\end{aligned}
 \tag{2.4}
\]

The exact identity proved there is

\[
 J_{i+1,j+1}+J_{ij}
 =\mathscr C(a,g)+\mathbb B(b,f)
  +\mathbb B(b,g)+\mathbb B(f,g).
 \tag{2.5}
\]

See equations (5.3)--(5.4), lines 376--438. The left side is zero by
(2.1), so the complete augmented cochain equality is now

\[
 \boxed{
 \mathscr C(a,g)
 =\mathbb B(b,f)+\mathbb B(b,g)+\mathbb B(f,g).}
 \tag{2.6}
\]

Equation (2.6) is an equality of the complete displayed aggregates. It does
not assert that any one of its raw, old--new, or new--new constituents
vanishes separately, and it does not imply \(\mathcal D_{ij}=0\).

## 3. Equivalent row-constant form of \(u\)

Fix \(i\). From (0.1)--(0.2),

\[
 u_{i,j+1}+u_{ij}=[j=i]+[j=i-1],
 \tag{3.1}
\]

where an indicator with a negative index is absent from the domain
\(j\geq0\). Hence each row has one exceptional diagonal value and is
constant everywhere else. There is a unique \(c_i\in\mathbb F_2\) such
that

\[
 \boxed{u_{ij}=c_i+[j=i].}
 \tag{3.2}
\]

For example, \(c_i=u_{i,i+1}\); this definition also handles \(i=0\)
without treating \(u_{00}\) as the row constant.

Substituting (3.2) into the diagonal defect gives

\[
\begin{aligned}
 \mathcal D_{ij}
 &=u_{i+1,j+1}+u_{ij}\\
 &=c_{i+1}+[j+1=i+1]+c_i+[j=i]\\
 &=\boxed{c_{i+1}+c_i}.
\end{aligned}
 \tag{3.3}
\]

Thus (2.3) is equivalently the statement that every diagonal defect is the
adjacent difference of the row constants, and the remaining target is

\[
 \boxed{
 \mathcal D_{i0}=0
 \iff c_{i+1}=c_i
 \qquad(i\geq0).}
 \tag{3.4}
\]

## 4. Sharper pure-\(P\) ray target

Choosing \(j=i+1\) in (3.2) gives

\[
 \boxed{c_i=u_{i,i+1}.}
 \tag{4.1}
\]

The logical roles of the seed and the diagonal recurrence are distinct:

1. diagonal vanishing gives only
   \(c_{i+1}=c_i\), hence \(c_i=c_0\) for every \(i\);
2. equation (3.2) at \((i,j)=(0,0)\) gives
   \(u_{00}=c_0+1\);
3. the proved seed \(u_{00}=1\) therefore gives \(c_0=0\).

The seed is the exact finite base case in
<code>.scratch/direct_unary_identity.md</code>, lines 333--336. Combining
these three statements yields

\[
 \boxed{
 \bigl(\mathcal D_{ij}=0\text{ for all }i,j\bigr)
 \iff
 \bigl(u_{i,i+1}=0\text{ for all }i\bigr),}
 \tag{4.2}
\]

with the proved seed understood on the forward implication. More
explicitly, the reverse implication needs no seed: if all
\(u_{i,i+1}=c_i\) vanish, then (3.3) gives
\(\mathcal D_{ij}=0\). The forward implication first makes the \(c_i\)
constant and then uses \(u_{00}=1\) to identify that constant as zero.

The approved source words are

\[
 W^w_{\nu,i,j}
 =\operatorname{red}\bigl(P_\nu^iC_\nu Q_\nu^{\,i-j}\bigr).
 \tag{4.3}
\]

See <code>.scratch/period_two_augmented_cut_covariance.md</code>, lines
238--245. On the ray \(j=i+1\), equation (4.3) becomes

\[
 \boxed{
 W^w_{\nu,i,i+1}
 =\operatorname{red}\bigl(P_\nu^iC_\nu Q_\nu^{-1}\bigr).}
 \tag{4.4}
\]

Thus only the \(P_\nu\)-block is powered; \(C_\nu Q_\nu^{-1}\) is a fixed
tail. By contrast, the earlier boundary defect
\(\mathcal D_{i0}\) starts from

\[
 W^w_{\nu,i,0}
 =\operatorname{red}\bigl(P_\nu^iC_\nu Q_\nu^i\bigr),
 \tag{4.5}
\]

which couples powered \(P_\nu\)- and \(Q_\nu\)-blocks. Therefore the
one-parameter pure-\(P\) ray

\[
 \boxed{u_{i,i+1}=0\qquad(i\geq0)}
 \tag{4.6}
\]

is the narrower next target.

No identity in (4.6) is proved here. Consequently this note proves neither
the diagonal identity nor the \(i\)-edge law, unary delta identity,
period-two lift, AK(3), stable Andrews--Curtis, or Andrews--Curtis.

## 5. One-powered inverse increment target

The pure-\(P\) ray can be approached through adjacent increments at the
fixed inverse level \(e=1\). Put

\[
 A_i^*:=A^-_{i,1}=A_{i,i+1},
 \qquad
 p_i:=A^-_{i+1,1}+A^-_{i,1}.
 \tag{5.1}
\]

Here \(A^-_{n,e}=A_{n,n+e}\) is the inverse endpoint notation from
<code>AK3_OLD_NEW_INVERSE_Q_CONNECTORS.md</code>, equation (0.2).
Exact polarization gives

\[
\begin{aligned}
 \mathscr C(A_i^*,p_i)
 &=\Phi(A^-_{i+1,1})+\Phi(A^-_{i,1})\\
 &=u_{i+1,i+2}+u_{i,i+1}\\
 &=c_{i+1}+c_i.
\end{aligned}
 \tag{5.2}
\]

Thus the narrow increment target is

\[
 \boxed{\mathscr C(A_i^*,p_i)=0\qquad(i\geq0).}
 \tag{5.3}
\]

If (5.3) holds, then all \(c_i\) are equal. The proved seed \(c_0=0\)
then gives \(c_i=0\) and hence \(u_{i,i+1}=0\) for every \(i\). Conversely,
the pure endpoint identity (4.6) immediately implies (5.3).

At both endpoints the six source words have the form

\[
\begin{aligned}
 W^-_{\nu}(i,1)
 &=\operatorname{red}\bigl(P_\nu^iC_\nu Q_\nu^{-1}\bigr),\\
 W^-_{\nu}(i+1,1)
 &=\operatorname{red}\bigl(P_\nu^{i+1}C_\nu Q_\nu^{-1}\bigr).
\end{aligned}
 \tag{5.4}
\]

Therefore \(Q_\nu^{-1}\) is fixed and only the \(P_\nu\)-primitive is
powered.

The slot-zero raw part of this increment is already zero. The all-power
slot-zero theorem is

\[
 R_0(Y(d,m))=[d<0],
 \tag{5.5}
\]

proved in
<code>.scratch/period_two_complete_cochain_identity.md</code>, lines
443--503. Both diagonal endpoints in (5.1) have the same exponent
\(d=i-(i+1)=-1\). Each endpoint therefore has slot-zero raw value one, and
the increment xor is

\[
 \boxed{L_0(p_i)=1+1=0.}
 \tag{5.6}
\]

After (5.6), target (5.3) is exactly the joint identity

\[
 \boxed{
 L_{\ne0}(p_i)
 +\mathbb B(A_i^*,p_i)
 +Q(p_i)=0.}
 \tag{5.7}
\]

The nonzero-slot raw term, complete old--new term, and new--new quadratic
term in (5.7) remain open. Equation (5.7) is the proof object; no termwise
vanishing is asserted or required.
