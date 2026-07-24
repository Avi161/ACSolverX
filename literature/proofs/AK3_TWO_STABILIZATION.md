# Triangular two-stabilization corridors for AK(3)

Date: 2026-07-24

Status: the triangular-removal theorem is **PROVEN**. The finite AK(3)
candidate in Section 6 is **UNVERIFIED** until its certificate is built and
replayed.

## 1. Setup

Let

\[
 P=\langle x,y\mid R,S\rangle
\]

be a balanced presentation of the trivial group. Introduce fresh generators
\(z,t\) and freely reduced defining words \(w_z,w_t\in F(x,y)\). Write

\[
 D_z=z^{-1}w_z,\qquad D_t=t^{-1}w_t.
\]

For a word \(I\in F(x,y,z,t)\), define

\[
 \operatorname{sub}_{z,t}(I;w_z,w_t)
\]

by simultaneously replacing

\[
 z\mapsto w_z,\quad z^{-1}\mapsto w_z^{-1},
 \quad t\mapsto w_t,\quad t^{-1}\mapsto w_t^{-1}
\]

and freely reducing.

As in `AK3_RANK3_COMPRESSION.md`, a relator with exactly one occurrence of
\(g^{\pm1}\) can be rotated to \(g^\varepsilon q\), where \(q\) is
\(g\)-free. Its solution is

\[
 E(g^\varepsilon q)=
 \begin{cases}
 q^{-1},&\varepsilon=+1,\\
 q,&\varepsilon=-1.
 \end{cases}
\]

## 2. Two families of displayed substitutions

Adjoin \(z,t\) with relators \(D_z,D_t\) using the substitution-and-removal
lemma right-to-left twice. This is a pair of stable-AC composites.

Suppose a freely expanded spelling of a relator contains a displayed
\(w_z\) block. If the spelling is \(u w_z v\), right multiplication by

\[
 v^{-1}D_z^{-1}v=v^{-1}w_z^{-1}zv
\]

replaces it by \(z\). A displayed \(w_z^{-1}\) is replaced by \(z^{-1}\)
using the cyclic rotation \(w_z z^{-1}\) of \(D_z\). These are AC1--AC3
composites.

The identical argument with \(D_t\) replaces displayed
\(w_t^{\pm1}\) blocks by \(t^{\pm1}\). Because every block is displayed in
the unreduced template spelling, the two families may be interleaved in any
order even when free cancellations conceal parts of the blocks in the
reduced source relator.

Consequently, if

\[
 \operatorname{sub}_{z,t}(I;w_z,w_t)
\]

is an orientation of a source relator, that source relator can be changed to
\(I\) by AC1--AC3 moves while retaining \(D_z,D_t\).

## 3. Triangular-removal theorem

### Theorem 3.1 (immediate two-stabilization corridor) — PROVEN

Assume:

1. \(\operatorname{sub}_{z,t}(I_y;w_z,w_t)\) is \(S\), up to free
   reduction, cyclic rotation, and inversion;
2. \(I_y\) contains exactly one occurrence of \(y^{\pm1}\).

Let

\[
 e_y=E(I_y)\in F(x,z,t).
\]

Define the three surviving relators

\[
 R_y=\overline{R[y\mapsto e_y]},\qquad
 Z_y=\overline{D_z[y\mapsto e_y]},\qquad
 T_y=\overline{D_t[y\mapsto e_y]}.
\]

Suppose one of \(R_y,Z_y,T_y\), call it \(J_x\), contains exactly one
occurrence of \(x^{\pm1}\). Let

\[
 e_x=E(J_x)\in F(z,t).
\]

Delete \(J_x\) from the ordered triple and substitute \(x=e_x\) in the
other two relators, obtaining \(U(z,t),V(z,t)\). Then

\[
 \langle x,y\mid R,S\rangle
 \sim_{\mathrm{st}}
 \langle z,t\mid U,V\rangle.
\]

Any signed relabeling of \(z,t\) as a rank-two basis preserves the conclusion.

### Proof

**Two stabilizations.** Adjoin \(z,t\) with defining relators \(D_z,D_t\).
The tuple is

\[
 (R,S,D_z,D_t)
\]

over \(F(x,y,z,t)\).

**First compression.** Spell \(S\) as the freely equal word obtained from
\(I_y\) by expanding \(z,t\). Section 2 replaces every displayed defining
block and changes \(S\) to \(I_y\) by AC1--AC3 moves:

\[
 (R,S,D_z,D_t)\sim_{\mathrm{AC1-3}}(R,I_y,D_z,D_t).
\]

**Remove \(y\).** Rotate and, when required, invert \(I_y\) to the defining
form \(y^{-1}e_y\). Apply substitution-and-removal left-to-right. It deletes
\((y,I_y)\) and substitutes \(y=e_y\) in the other relators. The resulting
rank-three presentation is exactly

\[
 \langle x,z,t\mid R_y,Z_y,T_y\rangle.
\]

**Remove \(x\).** By hypothesis, \(J_x\) contains one \(x^{\pm1}\). Rotate
and invert it to \(x^{-1}e_x\). A second substitution-and-removal deletes
\((x,J_x)\) and substitutes \(x=e_x\) in the remaining two relators. These
are \(U,V\).

**Relabel.** The surviving basis is \(\{z,t\}\). A signed relabeling is an
ambient automorphism, realized stably by the stable ambient automorphism
principle. Compose the chains. \(\square\)

### Remark 3.2 (triangular dependency)

The order is load-bearing:

\[
 y=e_y(x,z,t),\qquad x=e_x(z,t).
\]

The first expression may depend on \(x\); after substitution into \(J_x\), the
second must depend only on the surviving generators. This is the acyclic
dependency graph

```text
y -> x -> {z,t}.
```

Swapping \(x,y\) gives the reverse triangular order. If the second relator
still contains multiple \(x\)-occurrences, Theorem 3.1 does not apply without
an additional AC compression phase.

## 4. The order audit for the AK(3) braid relator

Let

\[
 B=xyxy^{-1}x^{-1}y^{-1}.
\]

Take \(w_z=xy\) and \(w_t=yx\).

The valid spelling is

\[
 B=(xy)x\,y^{-1}(yx)^{-1},
\]

so the valid template is

\[
 I_y=zxy^{-1}t^{-1}=\texttt{zxYT}.
\]

Literal expansion gives

\[
 (xy)x\,y^{-1}(yx)^{-1}
 =xyxYXY=B.
\]

It isolates

\[
 y=t^{-1}zx.
\]

By contrast,

\[
 (xy)x(yx)^{-1}y^{-1}
\]

freely reduces to \(xy^{-1}\). Therefore

\[
 \operatorname{sub}_{z,t}(\texttt{zxTY};xy,yx)=\texttt{xY}\ne B.
\]

Any tuple derived by treating `zxTY` as the braid relator is disconnected
from Theorem 3.1. In particular, the previously observed nine-move rank-three
solve from that invalid tuple is quarantined and is not an AK(3) certificate.

## 5. Worked valid rank-three tuple

For the valid template `zxYT`, rotate to

\[
 y^{-1}t^{-1}zx,
\]

so

\[
 e_y=t^{-1}zx=\texttt{Tzx}.
\]

With

\[
 R=x^3y^{-4},\qquad D_z=z^{-1}xy,\qquad D_t=t^{-1}yx,
\]

Theorem 3.1's first stage gives:

\[
 \begin{aligned}
 R_y&=x^3(x^{-1}z^{-1}t)^4
       =x^2z^{-1}t(x^{-1}z^{-1}t)^3
       =\texttt{xxZtXZtXZtXZt},\\
 Z_y&=z^{-1}xt^{-1}zx
       =\texttt{ZxTzx},\\
 T_y&=t^{-2}zx^2
       =\texttt{TTzxx}.
 \end{aligned}
\]

Their \(x^{\pm1}\)-occurrence counts are respectively \(5,2,2\). Thus this
natural fixed template has no immediate second removal.

The finite census permits every valid template within its bounds, not only
this one.

## 6. Finite AK(3) candidate

### Immediate two-stabilization lemma — UNVERIFIED

There exist:

- nonempty freely reduced \(w_z,w_t\in F(x,y)\) with
  \(1\le|w_z|,|w_t|\le2\);
- a freely and cyclically reduced \(I_y\) of length two through six over
  \(x,y,z,t\);
- exactly one \(y^{\pm1}\) in \(I_y\);
- at least one occurrence of each of \(z^{\pm1},t^{\pm1}\);

such that:

1. expanding \(z,t\) gives an orientation of the AK(3) braid relator;
2. one of the three rank-three relators after removing \(y\) contains exactly
   one \(x^{\pm1}\);
3. the rank-two output after removing \(x\) has Aut-floor at most 12.

The word-equation census decides this exact statement. It is not an AC graph
search.

The disposable preflight found 352 distinct raw outputs and minimum floor 13.
That observation is not part of the theorem and remains unverified until the
complete census and Aut witnesses replay.

## 7. Scope and next theorem

A positive at floor at most 12 would give a stable chain to a presentation
covered by the classical length theorem; a separate classical AC certificate
and full move replay would still be required.

A negative refutes only the immediate finite lemma. It does not address:

- longer defining words or templates;
- a second relator that becomes isolating only after an AC multiplication;
- nontriangular dependencies;
- more than two stabilizations.

The planned next mechanism after a null is a **second-stage compression
theorem**: after removing \(y\), use one displayed occurrence replacement
from either surviving defining relation before testing a relator for its
unique \(x\)-occurrence.
