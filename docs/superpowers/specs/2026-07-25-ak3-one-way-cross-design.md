# AK(3) one-way cross-traffic design

Date: 2026-07-25

## Objective

Classify every finite history in which all \(B/D\) cross multiplications
flow in one direction: one slot remains a passive source and every cross
event targets the other slot. If a final one-\(z\) isolator is removed,
prove that the endpoint returns classically to AK(3). When the modified
target is removed and the passive source survives, require that source's
final quotient shadow to be restored up to conjugation and inversion. If
the passive source itself is removed, require its final isolator to have
the same quotient normal closure as the baseline source.

This includes the previously open two-\(D\)-factor branch.

## Direction \(D\to B\)

Put

\[
G=\langle x,t\mid x^3=t^4\rangle,\qquad
H=G*\langle z\rangle,
\]

\[
p=xt,\qquad B=z^{-1}p,\qquad D=t^{-1}zxz^{-1}.
\]

Quotient by the passive source:

\[
K_D
=H/\langle\!\langle D\rangle\!\rangle
=\langle G,z\mid zxz^{-1}=t\rangle.
\]

This is an HNN extension identifying \(\langle x\rangle\) with
\(\langle t\rangle\), so Britton's lemma embeds \(G\).

All \(D\)-source factors vanish in \(K_D\). A normalized final target
\(z^{-1}e\) must therefore be conjugate to \(B\); stable-letter exponent
excludes \(B^{-1}\). Length-one HNN conjugacy forces

\[
[e]_G=e_n=t^{-n}px^n,\qquad n\in\mathbb Z.
\]

The survivor evaluates to

\[
D[z\mapsto e_n]
=t^{-n}D[z\mapsto p]t^n.
\]

For exactly two displayed source factors with signs
\(\epsilon,\eta\), torus weight forces \(n=\epsilon+\eta\). Thus the only
tails are \(e_2,e_0,e_{-2}\).

## Direction \(B\to D\)

Quotient by the passive source:

\[
K_B
=H/\langle\!\langle B\rangle\!\rangle
\cong G,
\qquad z=p.
\]

Let the final target normalize to \(I=z^{-1}e\). Modulo the passive source,
it is conjugate, up to inversion, to the baseline target \(D\). Therefore

\[
p^{-1}[e]_G
=aD(p)^\delta a^{-1}.
\]

Writing \(m=aD(p)^\delta a^{-1}\), the surviving \(B\)-slot evaluates to

\[
B[z\mapsto e]
=e^{-1}p
=m^{-1}
\]

in \(G\). It is already conjugate, up to inversion, to the baseline braid
endpoint \(D(p)\). The fixed-\(R\) lemma lifts this quotient statement to
classical AC equivalence.

The \(z\)-exponent gives an immediate parity check: a \(D\)-target hit by
exactly two \(B^{\pm1}\)-factors has even \(z\)-exponent and cannot itself
be a one-\(z\) isolator. More generally, target inversion preserves this
parity, so when every event source is a conjugate of \(B^{\pm1}\), only an
odd number of cross factors can end in a one-\(z\) target. Every history
which does produce such an isolator is covered by the source quotient.

## Source-eliminated roles

If the passive \(B\)-source rather than its \(D\)-target is eliminated, the
passive-source absorption theorem returns the endpoint to AK(3). A passive
\(D\)-source cannot become a one-\(z\) isolator because its \(z\)-exponent
is zero.

Together, these statements close every finite one-way cross history with a
final one-\(z\) eliminator.

## Verification

The replay should pin:

- the exact seam recurrences \(e_n\mapsto e_{n+1}\) and
  \(e_n\mapsto e_{n-1}\);
- the four signed two-\(D\) histories and the table
  \(n=\epsilon+\eta\);
- the exact identity
  \(D(e_n)=t^{-n}D(p)t^n\);
- representative actual tails equal to \(e_n\) only modulo \(R\);
- the \(K_B\) survivor formula \(e^{-1}p=m^{-1}\); and
- the two-\(B\)-factor exponent-parity obstruction.

The replay illustrates exact algebra. Unbounded completeness comes from
the two source quotients and the HNN conjugacy theorem.

## Scope

The source slot must stay in its final quotient normal closure at every
cross event, every cross event must target the other slot, and a surviving
source must finish with its baseline quotient shadow up to conjugation and
inversion when it survives, or the same quotient normal closure when it is
removed. The theorem does not cover alternating target roles, temporary
feedback into the source, an unrestored surviving source, a changed source
normal closure at deletion, a changed retained relator, a multi-\(z\)
primitive eliminator, another stabilization, or dual-source compression.

AK(3) remains open.
