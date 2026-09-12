# Final bounded analysis of the rank-three corridor

An additional signed parameter line is ordinary-AC soluble:

\[
 m=-1,\qquad |k-n|=1,\qquad k,n\in\mathbb Z.
\]

This extends the stated parameter coverage. It uses the same unit-elimination mechanism as the known m=0 line, and those two lines have explicitly related coordinates after cleanup. It is not claimed as an independent new mechanism, a bibliographic novelty result, or a solution of the actual seed (m,k,n)=(2,1,2).

## Ordinary proof of the additional line

Start with the literal freely reduced triple

\[
 D=z x^{-1}y^n,\qquad I=z^{-1}xyx,\qquad
 C=z y^k z^{-1}yx.
\]

Use the restored-donor convention of `stable_rank3_patterns.md`: appending donor J with sign e and conjugator q means multiplying the target on the right by q⁻¹Jᵉq, then restoring J. Set Q=x⁻¹yⁿ. The free-group identity

\[
 D\,(Q^{-1}IQ)=xy^{n+1}
\]

replaces D by A=xyⁿ⁺¹ in one such donor use. No assumption on the presented group is used.

Use A to remove the two x letters of I and the one x letter of C. The exact result is

\[
 (A,I_1,C_1)=
 \bigl(xy^{n+1},\ z^{-1}y^{-2n-1},\ z y^k z^{-1}y^{-n}\bigr). \tag{1}
\]

Invert I₁ and cyclically conjugate it to J=zy²ⁿ⁺¹. Use J to remove both z letters from C₁. The resulting third relator is yᵏ⁻ⁿ. Since k−n=±1, correct its sign to obtain y, then clear y from A and J. The tuple becomes (x,z,y). A relator interchange, expanded into AC1 and AC2, gives exactly (x,y,z).

Here every removal is an ordinary restored-donor operation. For a unit-shaped donor R=ah, with h containing no a or a⁻¹, the replacements a→h⁻¹ and a⁻¹→h have exact errors

\[
 a^{-1}h^{-1}=a^{-1}R^{-1}a,
 \qquad ah=R.
\]

In a recipient P L Q, append the corresponding error conjugated by Q. For a positive a occurrence the donor sign/conjugator are (−1,aQ); for a negative occurrence they are (+1,Q). Every use restores R. Each replacement strictly reduces the recipient's number of a letters, since h contains none. Free reduction can only remove more letters of that generator. Thus the three clearing stages terminate, including n=−1, n=0, k=0 and negative exponents. No literal no-cancellation assumption or root extraction is needed.

The final relator swap has the six-step right-multiplication realization, for rows (a,b):

\[
 a\leftarrow ab,\quad a\leftarrow a^{-1},\quad
 b\leftarrow ba,\quad b\leftarrow b^{-1},\quad
 a\leftarrow ab,\quad a\leftarrow a^{-1}.
\]

It sends (a,b) to (b,a). All conjugations in the attached fixtures are expanded into single signed generator letters. There is no ambient automorphism, stabilization, or implicit relator permutation in these ordinary certificates.

## Relationship to the m=0 line and the suggested reflection

For m=0, the first restored-I operation gives yxyⁿ, which conjugates to the same A=xyⁿ⁺¹. Clearing x from the other relators gives

\[
 (A,z^{-1}y^{-n},z y^k z^{-1}y^{-n}). \tag{2}
\]

The m=−1 cleanup (1) is identified with (2) by the genuine triangular coordinate change

\[
 z_{\rm new}=z_{\rm old}y^{n+1},\qquad
 z_{\rm old}=z_{\rm new}y^{-n-1},
\]

followed by conjugating its second relator by yⁿ⁺¹. Indeed it becomes

\[
 y^{n+1}z_{\rm new}^{-1}y^{-2n-1}
 \ \sim\ z_{\rm new}^{-1}y^{-n},
\]

and the third relator becomes z_new yᵏ z_new⁻¹y⁻ⁿ because the added y powers commute with yᵏ. This explains the shared solvability mechanism. The ordinary proof above does not rely on realizing this coordinate change as an AC macro.

At the first derived donor

\[
 A_m=x^{-m}y x^{m+1}y^n,
\]

the reflection m↦−m−1 is visibly induced by reversing the word and cyclically rotating it. Word reversal can be represented by inverting every ambient generator and then inverting the relator. That observation alone is not a proof of a symmetry of the full original triple: it must act on I and C as well. No unrestricted full-family m↦−m−1 symmetry is asserted here. The explicit identification of the two relevant cleaned-up lines is enough to rule out a claim of a fundamentally different mechanism.

## Two exact rank-two descriptions

Write Q=xᵐyⁿ. Since D=zQ contains z once, the triangular ambient coordinate change z_new=z_old Q, followed by removal using the literal unit z_new, gives the pair

\[
 S_{m,n}=x^m y^n x^{-m}yx,
 \qquad
 T_{m,k,n}=y^{-n}x^{-m}y^k x^m y^{n+1}x. \tag{3}
\]

This is an unconditional free-group coordinate and quotient identity. Its stable-AC realization uses the stated known-trivial-input ambient convention. If the pair (3) itself has an ordinary trivialization, its quotient first proves the original group trivial, after which that convention applies without circularity. It is not generally an ordinary rank-preserving equivalence claim.

The audited corridor gives the other exact pair

\[
 \bigl(Uy^kU^{-1}y^{-n},\;VU\bigr),\qquad
 U=x^{-2m}yx,\quad V=x^m y^n x^m, \tag{4}
\]

where VU freely reduces to S_m,n. It arises from the triple

\[
 (ty^kt^{-1}y^{-n},\ t^{-1}U,\ Vt)
\]

by eliminating t through its defining relator t⁻¹U. Both descriptions retain two relators; neither discards the relation descended from the stable helper.

## Why the actual BS(1,2) entry is not a terminal certificate

For the actual (m,k,n)=(2,1,2), the first corridor relator is the genuine BS(1,2) word ty t⁻¹y⁻² in the rank-three basis (t,y,x). Its one-relator quotient is BS(1,2) free-product ⟨x⟩. The other two relators have t exponent ±1 but also contain the independent generator x. The rank-two terminal argument needs a companion in the free group on exactly the BS stable letter and its base letter. It cannot treat words involving x as powers of y or silently delete one companion.

After t is eliminated, (4) only resembles a rank-two BS donor with “stable letter U”. Keeping y and replacing the ambient x by U is not an automorphism here: the exponent vectors of (U,y) are

\[
 (1-2m,1),\quad (0,1),
\]

with determinant 1−2m, which is −3 at m=2. Thus U,y do not generate the ambient free group at the actual seed. The fact that U contains y once makes U individually primitive; it does not make the pair (U,y) a basis.

Even m=1, where that determinant is −1, does not justify this replacement. The subgroup generated by y and x⁻²yx is proper. An explicit folded based graph has vertices 0,1,2 and directed edges

\[
 0\xrightarrow{y}0,\quad 0\xrightarrow{x^{-1}}1,
 \quad 1\xrightarrow{x^{-1}}2,\quad 2\xrightarrow{y}1,
\]

with inverse edges understood. Its two fundamental loops are precisely y and x⁻²yx. It has no x-edge leaving the basepoint, so x is not in the subgroup. This is a concrete reason that determinant ±1 is not a basis certificate.

A valid next BS step would require an additional exact operation that eliminates x while retaining the BS donor and a companion with stable exponent ±1, or a verified free basis in which the retained pair really is BS(1,2) plus such a companion. For an actual rank-two BS(1,2) pair, that exponent condition permits cyclic pinch reduction to one stable letter. For general consecutive BS(p,p+1) with both power magnitudes greater than one, the stronger condition that the companion actually reaches stable length one under the divisibility-constrained cyclic Britton reductions remains necessary for the cited sufficient completion argument. These requirements are absent from a determinant computation.

## A precise connection with the existing MS residue theorem

The line n=−1,k=−2, with m≥1, illustrates why general extension is not automatic. The pair (3) is

\[
 S=x^m y^{-1}x^{-m}yx,
 \qquad T=yx^{-m}y^{-2}x^{m+1}.
\]

Invert S and move its initial x⁻¹ to the end; rotate T after its prefix yx⁻ᵐ. The two relators become

\[
 y^{-1}x^m yx^{-m-1},\qquad
 y^{-1}y^{-1}x^{m+1}yx^{-m}. \tag{5}
\]

In the notation of `ms_family_extensions.md`, using y as stable letter and x as base letter, this is exactly R_m together with S_(0,m+1,−m). Its two residues are

\[
 r\equiv 1\pmod m,\qquad s\equiv 1\pmod{m+1}.
\]

The proved residue transfers therefore reach the same-sign unit cell S_(0,1,1), the AK(m)-type cell described in that source. Its sufficient terminal criterion succeeds for m=1 and m=2, and fails for every m≥3: neither residue is zero, and they cannot be represented as opposite unit residues. Failure of that criterion is not an obstruction theorem. It shows exactly where invoking the already-proved MS result stops; claiming this whole line solved would go beyond that result.

This calculation does not identify the actual (2,1,2) seed with that line or with an AK presentation. No unproved parameter symmetry is used to transfer such a conclusion.

## Tiny full-certificate check

`rank3_corridor_final_analysis_checks.json` contains all 14 requested fixtures n=−3,…,3 and k=n±1 at m=−1. Every stored move is zero-based AC1, AC2 or one-letter AC3, and every final tuple is exactly (x,y,z). The aggregate is 1,263 elementary moves. The already-frozen independent integer and separate string checkers both replay every full stream and agree at every elementary state; the named algebraic checkpoints are also checked. Emission plus both replays used 0.005024 CPU seconds. No search was run.

Certificate JSON SHA-256: `eb45233d69d5223234cf309064e02a2461589a6394d5d250fc46a1ba5b6210c5`.

For an independent read-only replay, import `replay_integer` and `replay_string` from `stable_rank3_ac_independent_audit.py`, load each row's `initial` and `moves`, and require equality of the two returned state lists and final row `endpoint`. The companion JSON pins that checker's SHA-256.

The general proof is the free-word donor identity, the exact replacement errors, and decreasing generator-occurrence counts above. Finite signed fixtures check the implementation and signs; they do not establish the infinite quantifiers by enumeration.
