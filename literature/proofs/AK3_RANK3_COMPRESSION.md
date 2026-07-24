# Hidden-cancellation rank-3 corridors for AK(3)

Date: 2026-07-24

Status: the corridor theorem and the displayed AK(3) corollary are **PROVEN**.
The short-corridor existence statement in Section 6 is **UNVERIFIED** until
the complete finite certificate is built and replayed.

## 1. Conventions

Let \(F(a,b,z)\) be the free group on the displayed basis. Words use lowercase
letters for generators and uppercase letters for inverses. For a word \(u\):

- \(\overline u\) denotes ordinary free reduction;
- \(u^{-1}\) denotes reverse order with every letter inverted;
- \(\operatorname{sub}_z(I,w)\) is the free reduction of the word obtained
  from \(I\) by replacing \(z\) with \(w\) and \(z^{-1}\) with \(w^{-1}\).

Relators are group elements of the ambient free group. Thus inserting or
deleting adjacent inverse pairs changes a spelling, not the relator. Cyclic
rotation and inversion are AC1/AC3 conventions and will be named when used.

Write \(\sim_{\mathrm{st}}\) for stable Andrews--Curtis equivalence. The
stable moves are AC1--AC3 together with AC4, which adjoins a fresh generator
and its generator relator, and AC5, its inverse. We use two results already
proved in `literature/proofs/PROOFS.tex`:

1. **Substitution and removal.** On a presentation of the trivial group,
   adjoining or deleting a defining relator \(g^{-1}u\), together with the
   corresponding substitution \(g\mapsto u\), is a stable-AC composite.
2. **Stable ambient automorphism principle.** Applying an automorphism of the
   ambient free group to every relator of a balanced trivial-group
   presentation is a stable-AC composite.

The trivial-group hypothesis is essential in the first item and is part of
every theorem below.

## 2. One displayed substitution is an AC1--AC3 composite

Let

\[
 D=z^{-1}w
\]

be one relator of a tuple.

Suppose another relator has a freely equal spelling \(U=u w v\). Multiplying
\(U\) on the right by the conjugate

\[
 v^{-1}D^{-1}v=v^{-1}w^{-1}zv
\]

gives

\[
 (uwv)(v^{-1}w^{-1}zv)=uzv.
\]

Relator multiplication, inversion, and conjugation are AC1--AC3 composites,
so this replaces the displayed occurrence \(w\) by \(z\).

For a displayed inverse occurrence, spell \(U=u w^{-1}v\). The cyclic rotation
\(wz^{-1}\) of \(D=z^{-1}w\) is a conjugate of \(D\), and

\[
 (uw^{-1}v)\bigl(v^{-1}(wz^{-1})v\bigr)=uz^{-1}v.
\]

Thus a displayed \(w^{-1}\) may likewise be replaced by \(z^{-1}\).

The displayed blocks need not survive free reduction. If a word \(J\) is
written first and only then freely reduced, every \(w^{\pm1}\) block displayed
in \(J\) is still an available spelling of the same free-group element.
Consequently the replacements may be performed before the boundary
cancellations. This is the hidden-cancellation mechanism used below.

## 3. Rank-3 corridor theorem

### Theorem 3.1 (one-stabilization isolator corridor) — PROVEN

Let

\[
 P=\langle a,b\mid R,S\rangle
\]

be a balanced presentation of the trivial group. Let \(w=w(a,b)\) be a
freely reduced word and let \(I=I(a,b,z)\) be a word such that:

1. \(I\) contains exactly one occurrence of \(b^{\pm1}\);
2. \(I\) contains at least one occurrence of \(z^{\pm1}\);
3. \(\operatorname{sub}_z(I,w)\) is \(S\), up to free reduction, cyclic
   rotation, and inversion.

Rotate and, if necessary, invert \(I\) only enough to write

\[
 I=b^\varepsilon q,
 \qquad \varepsilon\in\{+1,-1\},
\]

where \(q\) contains no \(b^{\pm1}\). Define

\[
 e=
 \begin{cases}
 q^{-1},&\varepsilon=+1,\\
 q,&\varepsilon=-1.
 \end{cases}
\]

Let

\[
 R'=\overline{R[b\mapsto e]},
 \qquad
 D'=\overline{(z^{-1}w)[b\mapsto e]}.
\]

Then

\[
 \langle a,b\mid R,S\rangle
 \sim_{\mathrm{st}}
 \langle a,z\mid R',D'\rangle.
\]

After any chosen rank-two relabeling of \(\{a,z\}\), the resulting pair is
still stably AC-equivalent to the input.

### Proof

**Stabilize.** Apply substitution-and-removal right-to-left to adjoin the
fresh generator \(z\) with defining relator

\[
 D=z^{-1}w.
\]

This is an honest stable-AC composite, not an arbitrary Tietze move.

**Expose the template.** By hypothesis, the free-group element represented
by \(S\) has the spelling obtained from \(I\) by replacing every displayed
\(z\) by \(w\) and every displayed \(z^{-1}\) by \(w^{-1}\). Choose that
freely equal spelling for the relator \(S\).

**Compress.** Apply Section 2 once for every displayed \(w^{\pm1}\) block.
The blocks are disjoint in the unreduced template spelling, even when
adjacent free cancellations conceal them in the reduced spelling of \(S\).
The result is the relator \(I\). Hence

\[
 (R,S,D)\sim_{\mathrm{AC1-3}}(R,I,D).
\]

**Isolate \(b\).** The unique \(b\)-letter in \(I\) permits the displayed
rotation \(I=b^\varepsilon q\). If \(\varepsilon=+1\), invert the relator to
obtain the defining form \(b^{-1}q^{-1}=b^{-1}e\). If
\(\varepsilon=-1\), it already has the defining form \(b^{-1}q=b^{-1}e\).
Apply substitution-and-removal left-to-right: delete \(b\) and \(I\), and
substitute \(b=e\) in the two remaining relators. These are exactly \(R'\)
and \(D'\).

**Relabel.** The surviving basis is \(\{a,z\}\). Any desired signed
permutation taking it to a named rank-two basis is an ambient automorphism,
and the stable ambient automorphism principle realizes it by stable moves.
This proves the theorem. \(\square\)

## 4. The hidden AK(3) corridor

Use the exact AK(3) words

\[
 A=x^3y^{-4}=\texttt{xxxYYYY},
 \qquad
 B=xyxy^{-1}x^{-1}y^{-1}=\texttt{xyxYXY}.
\]

The second relator has the freely equal conjugacy spelling

\[
 B=(xy)x(xy)^{-1}y^{-1}.
\]

Choose

\[
 w=xy,\qquad I=zxz^{-1}y^{-1}=\texttt{zxZY}.
\]

Literal substitution gives

\[
 \begin{aligned}
 \operatorname{sub}_z(I,w)
   &=(xy)x(xy)^{-1}y^{-1}\\
   &=xyx\,y^{-1}x^{-1}y^{-1}\\
   &=B.
 \end{aligned}
\]

The spelling contains two displayed \(w^{\pm1}\) blocks. The inverse block is
partly concealed after free reduction; this is why a reduced left-to-right
subword picker does not model the transform as a two-substitution branch.

Rotate \(I\) to

\[
 y^{-1}zxz^{-1},
\]

so \(\varepsilon=-1\), \(q=zxz^{-1}\), and

\[
 y=e=zxz^{-1}.
\]

Substitution in the power relator gives

\[
 \begin{aligned}
 x^3y^{-4}
   &\longmapsto x^3(zx^{-1}z^{-1})^4\\
   &\longrightarrow x^3zx^{-4}z^{-1}.
 \end{aligned}
\]

The defining relator gives

\[
 z^{-1}xy
   \longmapsto z^{-1}xz xz^{-1}.
\]

Therefore Theorem 3.1 proves the following.

### Corollary 4.1 — PROVEN

\[
 \mathrm{AK}(3)
 \sim_{\mathrm{st}}
 \left\langle x,z\ \middle|\
 x^3zx^{-4}z^{-1},\ z^{-1}xzxz^{-1}
 \right\rangle.
\]

Relabeling \(z\) as \(y\) gives the exact rank-two pair

```text
xxxyXXXXY | YxyxY
```

This is a genuine orbit-escaping stable transform, but not a
trivialization.

## 5. What the new presentation does and does not buy

The existing complete Whitehead canonicalizer returns

```text
minimum total length: 14
representative: YXXYx | YYYYXyyyx
automorphism witness: x -> Y, y -> x
```

for `xxxyXXXXY | YxyxY`. The command used for this independent algebra check
is:

```bash
.venv/bin/python3 - <<'PY'
from experiments.equivalence_classes.lib.autcanon import aut_canon
print(aut_canon(("xxxyXXXXY", "YxyxY")))
PY
```

The AK(3) orbit floor is 13, so this corridor first moves uphill. Stable
trivializations are allowed to do that. The calculation neither proves nor
refutes the conjecture.

The structural gain is different: the presentation lies outside the
one-substitution/visible-subword model because the isolator uses both \(z\)
and \(z^{-1}\) arising from a freely expanded conjugacy word. It supplies a
strictly broader, exact rank-3 proof mechanism to classify.

## 6. First finite candidate lemma

### Short rank-3 corridor lemma — UNVERIFIED

There exists a Theorem 3.1 corridor for AK(3) satisfying

\[
 1\le |w|\le4,\qquad
 2\le |I|\le6,\qquad
 c_z(I)\ge2,
\]

whose output has Aut(\(F_2\))-minimum total relator length at most 12.

Here \(I\) is required to be freely and cyclically reduced, to contain exactly
one occurrence of the eliminated generator in either sign, and
\(c_z(I)\) counts \(z^{\pm1}\). The finite certificate enumerates precisely
this statement.

A positive would place AK(3) in the stable class of a length-at-most-12
presentation, after which the known classical theorem must still be expanded
into a replayable AC certificate. A negative refutes only this bounded
candidate lemma. It is not an invariant, an AC obstruction, or evidence that
no longer or primitive-isolator corridor exists.

## 7. Next loop if the finite lemma is false

The next structural enlargement is not a blind increase of the two length
bounds. Replace the unique eliminated generator by a primitive word
\(v(a,b)\) with an explicit Nielsen reduction witness, normalize \(v\) to a
basis letter using the stable ambient automorphism theorem, and study
templates

\[
 I=zuz^{-1}v^{-1}.
\]

This **primitive-isolator corridor lemma** strictly includes Theorem 3.1's
generator-isolator mechanism while retaining a proof-producing basis test.
