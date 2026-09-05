# Squaring-target continuation: working calculations only

Status: no new AC or stable-AC theorem. The certified starting point is
Section 6.88 of `AK3_MMS02_TPUB_TWO_GATE_BRIDGE.md`. The changes of
presentation below have not been compiled into a restored-donor transcript;
they must not be cited as an additional verified stable-AC corridor.

## Candidate coordinates

Preliminary substitutions through `c=t a^-2` suggest the two rows

```
ccaaCA
caacaCAACAA
```

where capitals denote inverses. Under `c=x, a=Xy`, literal substitution
gives `xyXyXYx` and `yXyyXYxYYxYx`. The first, after a cyclic conjugation,
has Magnus form `y_2 y_1 y_0^-1`. Thus the candidate base map is

\[
 \phi(u)=v,\qquad \phi(v)=uv^{-1},\qquad
 \phi^{-1}(u)=vu,\qquad \phi^{-1}(v)=u.
\]

Using these coordinate identities, the second row rewrites to a height-one
word with base coefficient `uvUVUVU`. Its next two images are `vuVUUV`
and `uvUVU`. All these finite word calculations, both inverse-map
compositions, and the following commutator identity were checked by free
reduction under the short computation guard:

\[
 C=[u,v],\qquad \phi(C)=C^{-1},\qquad
 \mathtt{uvUVU}=Cu^{-1}.
\]

**Missing certificate:** the preceding quotient substitutions have not yet
been individually assigned to distinct, restored donor rows. The free-word
checks verify the displayed coordinate calculations, not that missing AC
transcript.

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

Introducing a commutator generator and formally eliminating `t,v` gives
the candidate pair `uCuCuccUU`, `cuCucuCUcUU` over `u,c`. Literal ambient
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
must supply the missing legal transcript or directly realize a simplifying
row replacement; group consequence manipulations alone do not close AK3.
