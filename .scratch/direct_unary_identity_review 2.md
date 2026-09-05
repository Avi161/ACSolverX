# Hostile referee review of direct_unary_identity.md

## Overall verdict: **REVISE**

The exact reduction in Sections 1--4 survives adversarial checking. In
particular, I found no sign, diagonal, orientation, or integrality
counterexample to Theorems 2.1 and 3.1, the homomorphism statement, or the
difference-word identities for \(u_{00},I_{ij},J_{ij}\). The proposed
remaining obstruction in Section 5 does not survive unchanged: consecutive
same-label matching is not intrinsic to the answer, and the stated
forest-chord lemma is not yet a concrete event-level lemma. It also risks
silently replacing the sixteen literal correction occurrences (with fixed
base data in every endpoint residual) by the twelve active *directional*
occurrences from the mixed-Hessian normal form.

1. **Theorem 2.1 (sign, diagonal, and stable-sort formula): APPROVE.**

   For a signed Schreier stream \((x_a,\varepsilon_a)\), the implementation
   at "_KernelStream._append_kernel_letter" adds the previous linear
   coordinate tensored with \(\varepsilon_a e_{x_a}\), plus
   \(e_{x_a}\otimes e_{x_a}\) only when \(\varepsilon_a=-1\). Hence, for
   \(x\ne y\),

   \[
   A_{xy}=\sum_{a<b,\ x_a=x,\ x_b=y}\varepsilon_a\varepsilon_b.
   \]

   This agrees exactly with "_kernel_product", "_kernel_inverse", and the
   orientation retained by "_residual_tensor_to_wedge": the retained entry
   is \(A_{xy}\) when the shortlex key of \(x\) is smaller than that of
   \(y\). Modulo two all products of signs are one. The inverse correction is
   genuinely diagonal and cannot affect this off-diagonal readout.

   The hypothesis \(W\in[K,K]\) supplies the missing integral fact: every
   signed exponent sum is zero, so every unsigned multiplicity \(m_x\) is
   even. Thus, for \(x\ne y\), the two chronological orientation counts add
   to \(m_xm_y=0\pmod2\). This proves both the displayed \(<\) formula and
   its \(>\) version. The restriction to \([K,K]\) is essential, but it is
   stated.

   A fixed literal sanity check is the commutator
   \(W=r_xr_yr_x^{-1}r_y^{-1}\), with \(x<y\). Its events are
   \(x^+,y^+,x^-,y^-\). The three chronological \(x\)-before-\(y\) pairs
   give parity one, while \(A_{xy}=1-1+1=1\). There is no orientation-sign
   mismatch.

2. **Invariance under adjacent Schreier cancellation: APPROVE.**

   An adjacent \(r_xr_x^{-1}\) or \(r_x^{-1}r_x\) contributes two identical
   comparison bits with every event outside the pair. Its internal pair is
   diagonal. Deleting it therefore changes the stable-sort count by zero
   modulo two. Adjacency is important: it ensures that every third event is
   on the same side of both deleted endpoints. The manuscript uses exactly
   this hypothesis.

3. **The chord formula with labels occurring more than twice: APPROVE.**

   Fix distinct labels \(x,y\). For a consecutive \(x\)-chord, the parity
   of crossing \(y\)-chords equals the number of \(y\)-endpoints in its open
   interval. The consecutive \(x\)-intervals are precisely the regions in
   which the number of preceding \(x\)'s is odd. Summing over all such
   intervals therefore gives the number of chronological
   \(x\)-before-\(y\) pairs. Nothing in this argument assumes that either
   label occurs exactly twice.

   For example, \([r_x,r_y]^2\) has label stream
   \(x,y,x,y,x,y,x,y\). Consecutive pairing gives two crossings, hence zero
   modulo two; the stable-sort count is \(4+3+2+1=10\), also zero. This is a
   direct four-occurrence-per-label replay of the load-bearing case.

4. **Arbitrary same-label pairing: REVISE, with a useful corrected
   strengthening.**

   The unqualified claim that *total* chord-crossing parity is independent
   of the chosen perfect pairing is false. The raw stream
   \(x^+,x^+,x^-,x^-\) represents
   \(r_x^2r_x^{-2}=1\in[K,K]\). Consecutive pairing
   \((1,2),(3,4)\) has no crossing, whereas the perfect pairing
   \((1,3),(2,4)\) has one same-label crossing. The latter cannot equal the
   exterior readout, which has no diagonal-label contribution.

   There is, however, a stronger correct theorem that is directly useful.
   Define \(\operatorname{cr}_{\ne}\) to count only crossings between chords
   with *distinct* labels. Then \(\operatorname{cr}_{\ne}\) is independent
   of the perfect matching chosen inside every even-multiplicity label, and

   \[
   \phi_\infty(W)=\operatorname{cr}_{\ne}(W).
   \]

   Indeed, for any \(x\)-chord, its number of crossing \(y\)-chords modulo
   two is the number of \(y\)-endpoints inside it, independent of the
   \(y\)-matching. Summing over \(x\)-chords and then over \(y\)-endpoints,
   the number of \(x\)-chords straddling a \(y\)-endpoint is the number of
   preceding \(x\)-endpoints modulo two, independent of the \(x\)-matching.
   This recovers the chronological \(x\)-before-\(y\) count.

   Consequently, lines 279--282 overstate the obstruction: one need not find
   the *consecutive* mate of every event. An explicit provenance-based
   perfect matching of events with the same final post-"c_vertex" label is
   enough if the readout is changed to \(\operatorname{cr}_{\ne}\). If the
   manuscript keeps counting all chord crossings, it must instead prove
   that the chosen provenance matching has even (preferably zero)
   monochromatic crossing parity.

   This strengthening does **not** remove chronology. Swapping two adjacent
   events of distinct labels toggles the stable-sort parity. Thus the
   shortlex order inside each actual correction leaf, and the positions it
   induces in the literal stream, remain load-bearing.

5. **Homomorphism claim: APPROVE.**

   For \(W,V\in[K,K]\), the cross contribution in the concatenated stream is

   \[
   \sum_{x<y}m_x(W)m_y(V),
   \]

   which vanishes modulo two because every \(m_x(W)\) and \(m_y(V)\) is
   even. Therefore
   \(\phi_\infty(WV)=\phi_\infty(W)+\phi_\infty(V)\). The inverse identity
   follows either from this and \(WW^{-1}=1\), or directly from the
   class-two inverse formula in characteristic two. No hidden conjugation
   invariance is being assumed.

6. **Integral membership of residuals in \([K,K]\): APPROVE, but make the
   justification explicit.**

   Corrections are words in \(K\), so they do not change the quotient of the
   residual. The quotient is already trivial. The Reidemeister--Schreier
   relation-module coordinate is the integral abelianization of the free
   kernel \(K\), with basis \(r_x\). For the fixed base \(B\), the lift
   certificate proves that the defect plus the correction image is zero.
   For an integral homogeneous direction \(F\),
   \(\operatorname{correction\_image}(F)=0\). Linearity of the abelianized
   occurrence operators then gives

   \[
   [\mathcal R(F)]_{K_{\rm ab}}
   =d+\operatorname{correction\_image}(B)
     +\operatorname{correction\_image}(F)=0.
   \]

   Hence \(\mathcal R(F)\in[K,K]\) integrally, not merely modulo two. The
   manuscript should state this one-line calculation or define
   "homogeneous" at (4.1); otherwise the central membership assertion looks
   stronger than what "_symbolic_residual_coordinate" itself asserts (that
   function checks the quotient there, while the wedge reader checks the
   linear coordinate later).

7. **Difference-word identities for \(u_{00},I,J\): APPROVE.**

   Write
   \(q(D)=\phi_\infty(\mathcal R(D))+\phi_\infty(\mathcal R(0))\).
   The existing definition of the edge data is
   \(I_{ij}=q(D_{i+1,j})+q(D_{ij})\) and
   \(J_{ij}=q(D_{i,j+1})+q(D_{ij})\). The base term occurs twice and
   vanishes. The homomorphism and inverse identities then give

   \[
   \begin{aligned}
   I_{ij}&=\phi_\infty(\mathcal R(D_{i+1,j})\mathcal R(D_{ij})^{-1}),\\
   J_{ij}&=\phi_\infty(\mathcal R(D_{i,j+1})\mathcal R(D_{ij})^{-1}),\\
   u_{00}&=\phi_\infty(\mathcal R(D_{00})\mathcal R(0)^{-1}).
   \end{aligned}
   \]

   Applying Theorem 3.1 gives (4.3). The indicator offsets in (4.4) also
   agree with the definitions: the \(i\)-edge meets the diagonal at
   \(i-j=-1,0\), and the \(j\)-edge at \(i-j=0,1\).

8. **Bookkeeping-elimination claim: APPROVE for Sections 1--4; REVISE for
   the proposed continuation.**

   The literal scan genuinely eliminates a *separate final* wedge
   orientation comparison and a separately propagated tensor. It does not
   claim that the underlying defects vanish. The raw word still contains
   the section and transport defects; "_KernelStream" applies "c_vertex" at
   emission time; raw inverse signs determine emission and are forgotten
   only after membership in \([K,K]\) has supplied even multiplicities; and
   "lift_module_vector" still shortlex-sorts each merged support. Thus the
   exact equivalence in Sections 1--4 does not hide the previously identified
   defects.

   Section 5 is not yet at the same literal resolution. The phrase "the
   twelve fixed AST occurrence positions" comes from deleting the four
   slot-one *direction* occurrences in the anchored mixed Hessian. A unary
   endpoint is instead the full residual at \(B+D_{ij}\): its AST has sixteen
   correction occurrences, fixed base entries are present in every slot,
   and the shortlex section is formed from the merged current
   \(B_s+D_{ij,s}\), not from independently concatenated base and direction
   sections. Any forest proof must explicitly show how those fixed/base
   events, literal events, section interleavings, and raw transport events
   enter its matching. Merely referring to twelve directional occurrence
   nodes would reintroduce exactly the unary omission that the literal
   difference words were meant to cure.

9. **"Forest-chord telescoping lemma" as the sharper remaining lemma:
   REVISE.**

   As written, it is a research program rather than a falsifiable local
   lemma. The correction-image boundary relation gives global signed
   coefficient cancellation at each final label; it does not by itself
   produce "the two" events belonging to a leaf, prove that they have equal
   post-"c_vertex" labels, or place them in a single leaf interval. The
   boundary potential \(\lambda\) is specified only by its support, not by a
   formula independent of the desired crossing parity. With \(\lambda\)
   undefined, (5.2) can absorb the conclusion and is therefore potentially
   circular.

   A concrete non-circular replacement should provide:

   1. a literal event index set for both endpoint residuals, including all
      base, section, transport, inverse, and literal-source events;
   2. an explicit fixed-point-free matching (preferably an involution) whose
      matched events are proved to have equal final "c_vertex" labels for all
      \(i,j\);
   3. either the heterochromatic readout
      \(\operatorname{cr}_{\ne}\), or a proof that monochromatic crossings of
      this matching contribute zero;
   4. a precise leaf-removal operation and the induced change in the global
      chronological positions after the canonical shortlex merge;
   5. an explicit formula for \(\lambda\), followed by an independent proof
      of the local straddling identity and its three boundary values.

   The matching-independence result in item 4 above is a real simplification:
   a source-tree or AST-provenance matching may replace the difficult search
   for consecutive mates. It cannot eliminate construction of the actual
   event chronology, and it does not yet supply the missing label-preserving
   matching.

10. **Final disposition of the eight requested attacks.**

    - (i) stable-sort/sign/diagonal formula: **APPROVE**;
    - (ii) adjacent Schreier cancellation: **APPROVE**;
    - (iii) consecutive chord pairing with multiplicity \(>2\): **APPROVE**;
    - (iv) homomorphism: **APPROVE**;
    - (v) integral residual membership: **APPROVE**, with an explicit
      abelianization line requested;
    - (vi) \(I,J,u_{00}\) difference words: **APPROVE**;
    - (vii) removal of final orientation/tensor bookkeeping: **APPROVE** for
      the exact reformulation, **REVISE** for any twelve-occurrence forest
      implementation;
    - (viii) sharper remaining lemma: **REVISE** as under-specified and not
      yet demonstrably non-circular.

The all-index delta identity remains open exactly as the manuscript says.
The revision requested here strengthens the chord reduction and makes the
remaining obligation more precise; it does not revive any bounded-grid or
mixed-Hessian argument.

## Revision rereview

Revised subject SHA-256:
`5d510819e66e7ba60d4cc1c2f23c1f3685cc194379d94f565c9181a1538b454d`.

**APPROVE — zero open findings.**  The revision now gives the integral
\(K_{\rm ab}\) calculation; proves matching independence for
\(\operatorname{cr}_{\ne}\) while retaining the monochromatic
\(r_x^2r_x^{-2}\) counterexample; and states the
\(\operatorname{cr}_{\rm con}/\operatorname{cr}_{\ne}\) edge identities
precisely.  It also keeps all sixteen correction occurrences with each
merged \(B_s+F_s\) section, proves the conditional two-stream relative-order
criterion, and specifies the staged delete \(\to\) reorder \(\to\) insert
formula so deleted--deleted and inserted--inserted crossings are not double
counted.  Finally, it retains only the finite seed fact \(u_{00}=1\), leaves
both all-index edge identities open, and makes no all-index delta overclaim.
