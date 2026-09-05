# Boundary-automorphism corridor and the remaining donor gap

Status: **frozen transport cycle**. The final short-killer form returns
by explicit defining-row elimination to the same original length-15 pair;
see the convergence audit at the end. These intermediate equivalences
are retained, but they are not a new rank-two reduction.
The corridor from Section 6.88 of
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

## Second transport and a four-letter live coefficient

The same retained donor permits one more useful transport. Set
$g_2=t_0^2ct_0^{-2}$ and $E_2=g_2C_0^{-1}=\mathtt{uCuccuCUcUU}$.
The literal second-switch identity is

\[
 E_2({}^{t_0}E_1)^{-1}
 ={}^{\mathtt{uCuccuCUcUU}}R\;
  {}^{\mathtt{uCuccU}}R^{-1}.
\]

For an algebraic derivation, put $M=C_0({}^{t_0}C_0)$.
The first switch gives $M={}^{C_0w}R\,R^{-1}$, while
${}^{t_0}E_1=g_2C_0^{-1}M$. Taking the difference gives the displayed
two-factor product. Again this is a legal recipient correction, not an
additional relation asserted from a quotient calculation.

Here the Magnus coordinates of $E_2$ are
$(1,C),(2,c),(2,c),(3,C),(2,c)$, with final height zero; those of $R$
are $(1,C),(2,C),(3,c),(3,c)$, with final height one.
They suggest a rank-two automorphism fiber, but the following transcript
is needed to promote that suggestion to stable AC.

Apply the invertible ambient substitution $c\mapsto u^{-1}au$ and
stabilize by the defining row $D=\mathtt{uaUB}$. The balanced
trivial-presentation hypothesis is retained from the source corridor.
The two substituted rows are $R_0=\mathtt{AuAuaaU}$ and
$E_{20}=\mathtt{AuaauAUaU}$. Each table entry lists, in order, the
signed conjugators of the named restored donor for **old times new inverse**.
Thus multiply the old recipient by the inverse of that product on the left.

| old recipient | new recipient | donor | signed conjugators |
| --- | --- | --- | --- |
| `AuaauAUaU` | `AbbuBUb` | $D$ | $+$ `A`, $+$ `Ab`, $-$ `AbbuB`, $+$ `AbbuBU` |
| `AuAuaaU` | `ABubb` | $D$ | $-$ `AB`, $+$ `ABu`, $+$ `ABub` |
| `ABubb` | `AAbbbAbbu` | $F$ | $+$ `AB`, $+$ `AAbb` |

After the first correction, invert that recipient and conjugate it by $b$.
It becomes $F=\mathtt{ubUBBaB}$. This supplies the donor used in the last
line without changing $D$. In particular `ABubb` includes final height
one; an extra terminal `U` would be incorrect.

The two defining rows now express the automorphism

\[
 \psi(a)=b,\qquad \psi(b)=ba^{-1}b^2,
 \qquad \psi^{-1}(a)=a^2b^{-1}a,\quad\psi^{-1}(b)=a.
\]

Both inverse compositions are literal free-group identities. The remaining
row has coefficient $P=\mathtt{AAbbbAbb}$. Conjugate $Pu$ by $b^2$;
the exact defect from the shorter row is

\[
 {}^{b^2}(Pu)(\mathtt{bbABu})^{-1}
 ={}^{\mathtt{bbAAbb}}F^{-1}\;{}^{\mathtt{bbAB}}F^{-1}.
\]

Correcting by these restored donors proves the terminal theorem of this
section: **the sufficient target $P_T$ is stably AC-equivalent to**

\[
 (\mathtt{uaUB},\quad\mathtt{ubUBBaB},\quad\mathtt{bbABu}).
\]

The live coefficient has shortened from eight letters to four, and the
fiber map is now the explicitly invertible map above. This is a constructive
reformulation, not a trivialization. The boundary certificate's second-switch,
Magnus-corridor and short-killer decisions pin all displayed defects;
independent replay includes a corrupted-factor rejection control. No
knot-group identification, meridional-conjugacy claim, or new exclusion
census is needed for this theorem. The remaining obligation is to trivialize
this complete tuple by legal moves, not merely show that its group is trivial.

## The specific literature cleanup does not transfer

A direct comparison with a known simple knot-group killer is worth testing
before developing more transport formulas. Let

\[
 a\mapsto\mathtt{Mn},\quad b\mapsto\mathtt{NmnMMn},\quad
 u\mapsto\mathtt{Nmn},\qquad
 r=\mathtt{mNmnMNmNMn},\quad j=\mathtt{NmnMnMNmm}.
\]

Under this free substitution, the two retained rows $D,F$ map literally
to $1$ and ${}^{\mathtt{NmnM}}r$, respectively; the live row maps to $j$.
The words `aBu` and `aBua` map to $m$ and $n$.
For $w=[n,m^{-1}]=\mathtt{nMNm}$, the word $r$ is the cyclic shift by
two letters of $w^{-1}mw n^{-1}=\mathtt{MnmNmnMNmN}$.
This is the $q=-1$ presentation in
[Cha–Suzuki, Proposition 2.2, p. 1140](https://msp.org/agt/2016/16-2/agt-v16-n2-p15-s.pdf),
whose negative-$q$ simple normal generator specializes to
$g=wn=\mathtt{nMNmn}$. The comparison here requires only a homomorphism;
it does not assert a new stable-AC corridor from a group isomorphism.

Over $\mathbb F_7$, assign

\[
 m\mapsto\begin{pmatrix}1&1\\0&1\end{pmatrix},\qquad
 n\mapsto\begin{pmatrix}1&0\\3&1\end{pmatrix}.
\]

Direct multiplication gives $r\mapsto I$, so **both retained donors
are killed**. The live killer is not killed: its image is
$\left(\begin{smallmatrix}3&1\\6&0\end{smallmatrix}\right)$.
The candidate $g$ has image
$\left(\begin{smallmatrix}6&3\\2&0\end{smallmatrix}\right)$.
Thus the traces of $(j,m,n,g)$ are $(3,2,2,6)$.
Trace is invariant under conjugation and inversion in $\mathrm{SL}_2$.
Consequently no sequence of conjugations, inversions and multiplications
of the live row by conjugates of these fixed restored donors can turn it
into any of the three specific candidate pullbacks or their inverses.

The scope is essential: this excludes only the specified donor macros.
It does not cover arbitrary paths that use the live row to change the
donors and later restore them, or arbitrary ambient changes. It is not
an AC invariant of the complete tuple. As a can-fail control, conjugates
of $m$ retain trace two and are not separated from $m$. Replacing the
lower-left entry three by one fails $r\mapsto I$ and must be rejected
before any trace argument. The independent boundary tests pin these
controls and the source-row evaluations. This closes the proposed direct
literature transfer; it does not start a new exclusion census or resolve
the all-row cancellation problem.

## Convergence audit: the short-killer form returns to the starting pair

The final row `bbABu` defines $u=ba b^{-2}$. Eliminate that defining
generator using the established legal substitution-and-removal procedure.
The remaining two words are exactly

\[
 (\mathtt{baBBabbABB},\quad\mathtt{babABBBaB}).
\]

Now apply the signed generator rename $a\mapsto q^{-1}$, $b\mapsto p$.
Equivalently, substitute $(a,b,u)\mapsto
(\mathtt{Q},\mathtt{p},\mathtt{pQPP})$ into the preceding three-row
tuple. Its last row freely vanishes. The first row, conjugated by `qP`,
is `PPQppqPQ`; the second, conjugated by `QPqP`, is `PPPQQpq`.
Swapping these two rows gives

\[
 (\mathtt{PPPQQpq},\quad\mathtt{PPQppqPQ}),
\]

which is the **same ordered length-15 endpoint** certified in Section
6.87 of the main bridge document. These equalities are literal and are
pinned by `decide_boundary_transport_return()` and independent replay;
they do not rely on a Whitehead-minimum or orbit-classification claim.

Thus the displayed transport-and-return corridor is a closed stable-AC
equivalence loop. Its automorphism descriptions and donor identities
remain valid, but the four-letter coefficient is not a net reduction
beyond the existing rank-two endpoint. This does not prove that every
other continuation must return. As a convergence decision, however, this
transport route is now frozen: no further variants are promoted merely
for producing a shorter coefficient or a different mapping-torus form.
A reopening requires an actual cancellation or a separately justified
route that breaks this cycle.

A success-only geometric probe of the short three-row tuple also found
no witness: its ten-edge simple link support has eight spherical cyclic
orders among 1,728 tested orders, and the corresponding contiguous
parallel-edge block schemes gave no compatible signed ranks (960 phase
tuples, 7,680 component-seed attempts). The standard rigid-support solver
correctly reports this support as unsupported. The probe does **not**
exhaust general embeddings for this nonrigid support and proves no
nonthickenability theorem. It supplies no reason to reopen the frozen
transport route or to claim stable AK3.
