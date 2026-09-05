# Boundary-automorphism corridor and the remaining donor gap

Status: the corridor from Section 6.88 of
`AK3_MMS02_TPUB_TWO_GATE_BRIDGE.md` to the boundary-automorphism tuple
below now has a literal restored-donor certificate. Its trivialization
remains open: the power-two/power-five consequences are still not licensed
donor rows. No AK3 resolution is claimed.

## Certified change of presentation

Write the starting rows as $R_1=taTB$, $R_2=tbTAA$, $J=AAbbAt$.
Set $H=ttaTTAA$, $J'=AAtaaTAt$ and $L=taT$. With
${}^g w=gwg^{-1}$, the first two literal defects are

\[
 R_2H^{-1}={}^tR_1^{-1},\qquad
 J(J')^{-1}={}^{AA}R_1^{-1}\;{}^{AA L}R_1^{-1}.
\]

Use these products to replace the two recipients, restoring $R_1$ after
each donor use. Neither recipient now contains $b$, so the defining
$b$-row can be removed. Substitute $t\mapsto ca^2$; the image of $H$
is `caacaCAACAA` and the image of $J'$ is `AAcaaCAcaa`. Conjugating
the latter by `caa` gives the two rows

```
ccaaCA
caacaCAACAA
```

where capitals denote inverses. Under `c=x, a=Xu`, literal substitution
and conjugation of the first row by $x$ give
$K_*=\mathtt{xxuXuXU}$ and $H_*=\mathtt{uXuuXUxUUxUx}$.
Adjoin $v=xux^{-1}$ with defining row $D=xuXV$, and put $E=xvXvU$.
The literal identity

\[
 K_*E^{-1}={}^xD\;{}^{xvX}D
\]

replaces the first row using the restored $D$-donor. These defining rows
now give the base map

\[
 \phi(u)=v,\qquad \phi(v)=uv^{-1},\qquad
 \phi^{-1}(u)=vu,\qquad \phi^{-1}(v)=u.
\]

Conjugate the live row by $x^2$. Its resulting word is
$Z=\mathtt{xxuXuuXUxUUxUX}$. Its seven Magnus coordinates are
$(2,u),(1,u),(1,u),(0,U),(1,U),(1,U),(2,U)$, with final height one.
Let $F=\mathtt{uvUVUx}$. The exact defect $ZF^{-1}$ is the product of
the eight donor factors in this table, in the displayed order:

| donor | sign | conjugator |
| --- | --- | --- |
| $D$ | $+1$ | `x` |
| $E$ | $+1$ | empty word |
| $D$ | $+1$ | `uV` |
| $D$ | $+1$ | `u` |
| $D$ | $-1$ | `uvUV` |
| $D$ | $-1$ | `uvUVV` |
| $E$ | $-1$ | `uvUVU` |
| $D$ | $-1$ | `uvUVUx` |

Left-multiplying $Z$ by the inverse of that product gives $F$. The
defining donors remain distinct from the live recipient and are restored.
For $C=[u,v]$, the finite word identities also give

\[
 C=[u,v],\qquad \phi(C)=C^{-1},\qquad
 \mathtt{uvUVU}=Cu^{-1}.
\]

**Certified conclusion.** The squaring target, and hence the sufficient
target $P_T$, is stably AC-equivalent to
$(xuXV,xvXvU,uvUVUx)$. The preceding defects, substitutions, defining-row
expansion/removal and permutations are its proof. Every ambient step uses
the established balanced trivial-presentation hypothesis.
`experiments/stable_ac/mms02_boundary_automorphism_corridor_certificate.py`
pins the transcript; the corresponding test file independently replays
the word identities and rejects a corrupted transport factor. Rename
$x=t$ in the rest of this note.

## Group-triviality calculation, not an AC trivialization

Consider the candidate tuple

\[
 (tut^{-1}v^{-1},\quad tvt^{-1}vu^{-1},\quad Cu^{-1}t).
\]

Its relations imply `t=u C^-1`. Since conjugation by `t` inverts `C`,
one gets `u C u^-1=C^-1`. The first row then gives `v=u C^-2`.
Substituting in `C=[u,v]` yields `C=C^-4`, hence `C^5=1`.
In the second row, `t v t^-1` simplifies to `u`, whereas `u v^-1`
simplifies to `C^-2`; therefore `u=C^-2`. Now `u` both commutes with and
inverts `C`, giving `C^2=1`. The two powers force `C=1`, then `u=v=t=1`.
Sol checked these group-theoretic implications and their orientations.

The critical unresolved step is **not** the integer gcd calculation.
Neither `C^2` nor `C^5` has been realized as a legal donor row. Treating
these consequences as available relators would silently enlarge the move
class. No AC conclusion follows from this paragraph.

## Constructive probe and convergence boundary

Introducing a commutator generator and legally eliminating `t,v` gives
the certified pair `uCuCuccUU`, `cuCucuCUcUU` over `u,c`, by the transcript below. Literal ambient
normalization and one cyclic product return to total length 15, with
endpoint `PPQPqqppQ`, `PPqpQQ` (here `p,q` are normalized generators).
This did not improve the certified length-15 target; no additional descent
or obstruction ledger is opened.

A metabelian-guided trial to replace the first raw row by a conjugate of
`ucc`, using only the second row as donor, produced the unreduced defect
`uCuCuccUUccuCCCUcUCC` for conjugator `ccuCCCU`. The attempted strictly
shortening relator substitutions did not reduce it. This is only a failed
certificate attempt, not a normal-closure or conjugacy obstruction.

Do not expand this note with new residual categories. A useful next advance
must directly realize a simplifying row replacement or the power-row
argument; group consequence manipulations alone do not close AK3.

## A legal retained-donor switch

Uppercase letters denote inverses, and $^{h}r=hrh^{-1}$.
Stabilize by the defining row $E=c[u,v]^{-1}$. The old killer
$J=[u,v]u^{-1}t$ and $J'=cu^{-1}t$ satisfy $J(J')^{-1}=E^{-1}$
literally, so multiplication by the restored donor corrects the killer.
Eliminate $t$ using $t_0=uC$, then eliminate $v$ using
$w=t_0ut_0^{-1}=\mathtt{uCucU}$. These are defining-row removals, not
the addition of arbitrary normal-closure consequences. The surviving pair is

\[
 R=\mathtt{uCuCuccUU},\qquad E_0=\mathtt{cuCucuCUcUU}.
\]

Put $C_0=[u,w]$, $g=t_0ct_0^{-1}=\mathtt{ucU}$, and
$E_1=gC_0=\mathtt{ucuCucUCUcU}$. Free reduction proves the exact identity

\[
 E_1\bigl({}^{t_0}E_0\bigr)^{-1}
 ={}^{\mathtt{ucuCucUU}}R\;{}^{\mathtt{ucU}}R^{-1}.
\]

Thus conjugate the recipient $E_0$ by $t_0$, then left-multiply it by
the displayed product, restoring $R$ after each factor. The resulting
pair is $(R,E_1)$. In particular, the product is used with its displayed
sign, not inverted. This realizes one boundary-transport consequence
without treating a commutator-inversion consequence as an extra donor.

`decide_boundary_donor_switch()` in the boundary certificate pins both
defining substitutions and both donor factors. Independent free-word
tests replay them. This theorem certifies a stable equivalence only;
neither row has been made primitive, and the power-row cancellation and
the sufficient target's trivialization remain open.
