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
Neither `C^2` nor `C^5` is a legal available donor row. In fact the pure
power-row target is impossible, by the unimodularity proposition below.
A constructive use of these consequences must keep live generator tags
or other non-power terms until cancellation is legally justified. Treating
the pure consequences as available relators silently enlarges the move
class. No AC conclusion follows from this paragraph.

### Unimodularity forbids pure power rows, not tagged power cancellation

**Proposition.** No balanced presentation of the trivial group contains
a relator freely equal to a conjugate of $w^k$ with $|k|>1$. This applies
at every stage of any stable AC sequence from such a presentation.

**Proof.** For $n$ generators and $n$ relators, let $M$ be the integer
matrix whose rows are their exponent-sum vectors. Trivial abelianization
means that these rows generate $\mathbb Z^n$, so $\det M=\pm1$.
A row for a conjugate of $w^k$ is $k$ times the exponent-sum vector of
$w$. Expansion of the determinant in that row makes $k$ divide
$\det M$, a contradiction. Stabilization and destabilization preserve
balancedness and the presented trivial group, so the argument applies
at every rank. $\square$

Thus even one pure `C^2` or `C^5` donor row is impossible; the issue is
not merely arranging their simultaneous availability. If the live word
$C$ is literally a commutator in the current free generators, even a
row equal to $C$ would have zero exponent vector. Introducing a new
generator $c$ for that commutator changes the literal word under discussion,
but a pure $c^k$ row still fails the proposition for $|k|>1.

There is a positive tagged model, not a transfer theorem for AK3. On
free generators $c,d$, put

\[
 r=c^2d,\qquad s=c^5d^2.
\]

The exponent matrix has rows $(2,1),(5,2)$ and determinant $-1$.
More importantly, literal free reduction verifies

\[
 s c^{-1}= {}^{c^3}r\;{}^c r.
\]

With $r$ retained and restored as donor, left-multiply $s$ by the inverse
of the displayed product to obtain $c$. Then two left multiplications of
$r=c^2d$ by the inverse of the donor $c$ give $d$; swap the rows to obtain
$(c,d)$. These are ordinary AC moves, using the established restored-donor
conjugation macros, and the word test replays them literally. The
unimodular matrix alone was not used to infer AC triviality.

This corrects the power-row interface: a power-based continuation needs
actual tagged or interleaved rows and a legal route to cancel the tags.
No route from the AK3 target to this model is supplied. It is a positive
control for a feasible move pattern, not a new residual ledger, bridge
certificate, stable AK3 proof, or ordinary AK3 proof.

### Literal test of a tag on the actual inversion defect

The simple tagged model above does not arise merely by declaring its
rows to be consequences. Here is one legal test using the actual raw pair
$R=\mathtt{uCuCuccUU}$, $E=\mathtt{cuCucuCUcUU}$ from the retained-donor
switch below. That switch implies the literal product identity

\[
 H=\mathtt{ucUc}
 ={}^{\mathtt{ucuCucUU}}R\;
  {}^{\mathtt{ucU}}R^{-1}\;
  {}^{\mathtt{uC}}E\;{}^{\mathtt C}E.
\]

Stabilize by a new generator and row $d$, then right-multiply that row
by the displayed product, restoring each donor. The new row is
$S=dH=\mathtt{ducUc}$, not $H$. With $S$ retained, put

\[
 R_n=\mathtt{uCuCDCDCU},\qquad
 E_n=\mathtt{cuCuccdcUU}.
\]

The exact old-times-new-inverse defects are

\[
 EE_n^{-1}={} ^{\mathtt{cuCucc}}S^{-1},\qquad
 RR_n^{-1}={} ^{\mathtt{uCuCucUD}}S\;
                  {}^{\mathtt{uCuCD}}S.
\]

Left-multiplying each old recipient by the inverse of its displayed
product gives $(R_n,E_n,S)$ legally. The row $E_n$ contains $d$ exactly
once and defines $d=\mathtt{CCUcUCuuC}$. Substitution into the other two
rows and defining-row removal give the exact pair

\[
 (\mathtt{uCUcuCuccUUcuCucU},\quad
  \mathtt{CCUcUCuuCucUc}).
\]

The boundary certificate and independent word replay check the product,
both defects, and the disappearance of the defining row. This evaluates
one actual legal use of the tag; it does not reach the binomial control.
A short exploratory strict-descent calculation reached total cyclic
length 19, not an improvement over the existing length-15 endpoint; no
minimality assertion is made. Neither a tag family nor a residual ledger
is opened. This corridor supplies no terminal cancellation or AK3 claim.

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
must directly realize a simplifying row replacement or a tagged power-row
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

### Complete exact-complex rotation audit

The preceding success-only check can be completed for this one small tuple
without a block assumption. Rename $(a,b,u)$ to $(x,z,t)$, giving the
literal rows `txTZ`, `tzTZZxZ`, `zzXZt`. Their six germ degrees are
$(3,3,8,8,5,5)$. After fixing the first dart in each cyclic order at
the three positive germs, the generator-end reversal uniquely determines
the three negative orders. Thus all compatible orientable rotations are
enumerated by

\[
 (3-1)!(8-1)!(5-1)!=241920
\]

choices. The literal corner involution $A$, generator involution $B$,
paired germ stars, dart partition and connectedness are checked before
counting cycles of $\sigma A$. The complete face-count histogram is

| faces | rotations |
| --- | ---: |
| 2 | 115836 |
| 4 | 109814 |
| 6 | 15840 |
| 8 | 424 |
| 10 | 6 |

For six vertices and sixteen edges, a sphere would require twelve faces.
The maximum Euler characteristic is instead $6-16+10=0$, attained by six
rotations, so the minimum compatible orientable genus is exactly one.
The independent replay reconstructs the dart data from the literal words
and recounts all rotations using a separate cycle counter. As a positive
control, the connected triangular-basis tuple `(xzt,zt,t)` has two choices,
both spherical. The pinned certificate is
`mms02_boundary_exact_rotation_certificate.py`.

This completes the orientable rotation check for this exact complex only.
It excludes the direct orientable-thickening certificate at this endpoint;
it is not invariant under AC moves and does not restrict other stabilized
representatives. No new transport variants or residual categories are
opened, and no AK3 obstruction follows.

### The closed loop does not give a rank-dropping substitution

One possible reuse of the frozen loop is to iterate its formal generator
substitution. Track the original generators $p,q$ through the chosen
defining-row eliminations and ambient substitutions. These are literal
word representatives, not canonical maps independent of the transcript.
The simultaneous substitutions and the resulting images are:

| substitution | image of original $p$ | image of original $q$ |
| --- | --- | --- |
| $p\mapsto t,\ q\mapsto aT^3$ | `t` | `aTTT` |
| $t\mapsto caa,\ a\mapsto a$ | `caa` | `ACAACAAC` |
| $c\mapsto x,\ a\mapsto Xu$ | `uXu` | `UUxUUxU` |
| $x\mapsto uC,\ u\mapsto u$ | `uc` | `UCUCU` |
| $c\mapsto Uau,\ u\mapsto u$ | `au` | `UUAUA` |
| $a\mapsto Q,\ u\mapsto pQPP$ | `QpQPP` | `ppqpqPqppqPq` |

The last line combines the defining equation $u=baBB$ with the signed
rename $a=Q,b=p$. Intermediate $x$ is renamed $t$ before its elimination;
the newly introduced commutator letter $c$ is not the earlier ambient $c$.
Row multiplications, conjugations and the final swap do not themselves
change this generator bookkeeping.

**Proposition (formal iteration only).** The endomorphism
$f:F(p,q)\to F(p,q)$ given by the last line is injective. Every positive
iterate has noncyclic image and sends every nonidentity free-group word
to a nonidentity word.

**Proof.** With rows indexed by output letters $p,q$ and columns by input
generators, exponent sums give

\[
 f_{\mathrm{ab}}=M=\begin{pmatrix}-1&3\\-2&5\end{pmatrix},
 \qquad \det M=1.
\]

The subgroup $H=\langle f(p),f(q)\rangle$ is free by Nielsen--Schreier.
It has rank at most two because two elements generate it, and at least
two because their images in $\mathbb Z^2$ are independent. Thus $H$ is
free of rank two. The surjection $F(p,q)\to H$, composed with an abstract
isomorphism $H\cong F(p,q)$, is injective by Hopficity of finite-rank free
groups. See [Baumslag, Chapter III, Theorems 7--9](https://www.macs.hw.ac.uk/~lc45/Teaching/kggt/Baumslag-book.pdf)
for the residual-finiteness/Hopficity argument. Hence $f$ and its iterates
are injective. Alternatively, noncyclicity alone follows immediately from
$\det M^k=1$ for every $k\geq1$. $\square$

The independent word replay pins all six stages and the exponent matrix.
Its can-fail control $p\mapsto p,q\mapsto p^2$ kills $[p,q]$, whereas
the displayed substitution does not. The all-word conclusion comes from
the proof, not this finite control. Determinant one does not by itself
assert that $f$ is an automorphism, and no surjectivity claim is made.

This closes only the proposed rank-drop or free-annihilation mechanism
from iterating the chosen substitution alone. It does not encode the
live donor-row corrections, preclude word shortening, or constrain
general AC moves. In particular it is not an obstruction to using the
full corridor in a different construction. The balanced trivial-group
hypothesis remains required for the separate stable ambient simulation.
The transport route stays frozen, with no new residual ledger and no
bridge, stable AK3, or ordinary AK3 conclusion.

## A single defining tag preserves the AC-plus-automorphism orbit

Let $F=F(X)$, where $X$ consists of $n$ generators, and let
$r,s_2,\ldots,s_n,u,v\in F$. Introduce a fresh generator $t$ and put

\[
h=utv,\qquad p=rh=rutv.
\]

**Lemma.** At the exact checkpoint
$(p,s_2,\ldots,s_n,h)$, suppose that $p$ eliminates an original generator
occurring exactly once, with exponent $\pm1$, in the freely reduced word
$p$. Alternatively, suppose a certified free-basis complement for $p$ in
$F(X,t)$ is supplied. After deleting the defining row $p$ and its generator,
the remaining presentation is a common basis transport of
$(r^{-1},s_2,\ldots,s_n)$. Identifying the resulting free basis with $X$,
the endpoint therefore lies in the AC-plus-automorphism orbit of
$(r,s_2,\ldots,s_n)$, allowing row inversion and reordering.

**Proof.** Set

\[
H=F(X,t)/\langle\!\langle p\rangle\!\rangle.
\]

The homomorphism $F(X,t)\to F(X)$ fixing every element of $X$ and sending
$t$ to $u^{-1}r^{-1}v^{-1}$ kills $p$. It therefore induces $H\to F(X)$.
The inclusion of $F(X)$ induces its inverse: the composite on $F(X)$
fixes $X$, while the composite on $H$ also fixes $t$ because
$t=u^{-1}r^{-1}v^{-1}$ in $H$. Thus $H\cong F(X)$, with $X$ a free basis,
and the image of $h=utv$ is exactly $r^{-1}$.

Solving the stipulated single occurrence of the eliminated original
generator gives a free basis $Y$ for the same quotient $H$. Under the
alternative hypothesis, the images of the supplied basis complement give
such a basis $Y$. Consequently all surviving rows are expressed in $Y$
by one common basis change from their expressions in $X$, which are
$s_2,\ldots,s_n,r^{-1}$. Reorder these rows and invert the first row to
compare with the original tuple. After identifying $Y$ with $X$, the
common basis change is an automorphism of the rank-$n$ free group.
$\square$

This algebraic statement does not require the group presented by the full
tuple to be trivial. It does not assert that $h=utv$ can be constructed by
legal moves for arbitrary $u,v$: legality of reaching the checkpoint must
be separately certified. A stable-AC interpretation likewise requires the
relevant move certificates and hypotheses for the defining deletion and
ambient basis transport.

The worked regression
[`test_rejected_half_twist_tag_returns_literally_to_ak3`](../../tests/stable_ac/test_mms02_terminal_preimage_killer_certificate.py)
pins the half-twist-tag construction and its exact return. It is a finite
control, not the proof of this all-word lemma.

**Corollary (fixed-pivot compression).** After the displayed checkpoint,
let a finite AC path leave $p$ fixed: it is never a recipient and is not
permuted. Temporary conjugation or inversion of $p$ for use as a donor is
allowed provided it is restored. This path projects to an ordinary AC path
on the remaining $n$ rows in $H$. Final defining-$p$ elimination changes
only the common free basis used to express those rows.

**Proof.** Under the quotient map to $H$, any donation of a conjugate of
$p^{\pm1}$ is the identity. Conjugation and inversion of a remaining row
project to the corresponding ordinary AC moves, and its conjugating word
projects to a word in $H$. Multiplication using another remaining row
likewise projects to ordinary row multiplication; reordering remaining
rows is unchanged. Omit the projected identity steps. The defining-row
deletion then expresses this projected AC path in the deletion basis $Y$
instead of $X$, as in the lemma. $\square$

These statements do not preclude shorter or useful representatives within
the same orbit, and the corollary does not obstruct solving the projected
AC problem. Fixed-pivot interleavings after formation of $p$ are covered;
modifications before that checkpoint or changes to the pivot are not.
Tags with multiple occurrences of $t$ are also outside the lemma. The route
remains frozen; no new ledger or AK3 conclusion is introduced.
