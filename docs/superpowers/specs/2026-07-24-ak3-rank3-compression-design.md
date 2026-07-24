# AK(3) rank-3 compression design

Date: 2026-07-24

Status: approved by the standing autonomous proof loop. The first structural
identity has been derived by hand; the general theorem, finite short-corridor
decision, and independent replay remain to be implemented.

## Objective and terminal condition

The objective is still a proof or disproof of the classical or stable
Andrews--Curtis conjecture. This subproject is one proof attempt, not a
replacement objective. It terminates successfully only if it produces either:

1. an independently replayable AC1--AC5 path from AK(3) to the standard
   presentation; or
2. an invariant proved unchanged by every AC1--AC5 move and proved to
   distinguish AK(3) from the standard presentation.

A bounded negative, a new stable-equivalent presentation, a lower search
score, or failure to find a path is an intermediate result. If the candidate
lemma below is false, its exact countercertificate is retained and the proof
loop moves to the next structural lemma.

## Structural observation

Write

\[
 P_0=\langle x,y\mid
 A=x^3y^{-4},\quad B=xyxy^{-1}x^{-1}y^{-1}\rangle.
\]

The braid relator has the freely reduced conjugacy form

\[
 B=(xy)x(xy)^{-1}y^{-1}.
\]

Adjoin \(z\) with defining relator \(D=z^{-1}xy\). In the freely equal
expanded spelling of \(B\), replace both \(xy\) and \((xy)^{-1}\) by \(z\)
and \(z^{-1}\). This turns \(B\) into

\[
 I=zxz^{-1}y^{-1}.
\]

The relator \(I\) isolates \(y\), with \(y=zxz^{-1}\). Substitution and
removal therefore give

\[
 P_0\sim_{\mathrm{st}}
 P_{14}=
 \left\langle x,z\ \middle|\ 
 x^3zx^{-4}z^{-1},\ z^{-1}xzxz^{-1}
 \right\rangle.
\]

After relabelling \(z\) as \(y\), the exact words are

```text
xxxyXXXXY | YxyxY
```

and their independently computed Aut(\(F_2\))-minimum representative is

```text
YXXYx | YYYYXyyyx
```

of total length 14. Thus the construction is not itself a solution. Its
importance is that it escapes the existing reduced-subword CoV model:
the second occurrence of \(xy\), namely \((xy)^{-1}=YX\), is exposed only
after a free expansion of the reduced braid relator.

## General corridor theorem

Let \(P=\langle a,b\mid R,S\rangle\) present the trivial group. Let \(w(a,b)\)
be freely reduced and let \(I(a,b,z)\) be a cyclic word satisfying:

1. \(I\) contains exactly one occurrence of \(b^{\pm1}\);
2. \(I\) contains at least one \(z^{\pm1}\);
3. replacing every \(z^{\pm1}\) by \(w^{\pm1}\) and freely reducing gives
   \(S\), up to cyclic rotation and inversion.

Rotate \(I\) to \(b^\varepsilon q\), where \(q\) is \(b\)-free, and set

\[
 e=\begin{cases}
 q^{-1},&\varepsilon=+1,\\
 q,&\varepsilon=-1.
 \end{cases}
\]

Then the proposed theorem is

\[
 \langle a,b\mid R,S\rangle
 \sim_{\mathrm{st}}
 \langle a,z\mid R[b\mapsto e],\ (z^{-1}w)[b\mapsto e]\rangle.
\]

Proof architecture:

1. use the substitution-and-removal lemma right-to-left to adjoin
   \(z^{-1}w\);
2. spell \(S\) as the freely equal word \(I[z\mapsto w]\);
3. replace each displayed \(w^{\pm1}\) by \(z^{\pm1}\), using one
   AC1--AC3 composite per occurrence;
4. use \(I=b^\varepsilon q\) as the defining relator for \(b\), substitute
   \(b=e\) in the two remaining relators, and remove \(b,I\);
5. relabel \(z\) as the second rank-2 generator by the already-proved stable
   ambient automorphism principle.

This is a theorem about explicit words, not an appeal to arbitrary Tietze
equivalence.

## First falsifiable lemma

The first candidate is deliberately finite:

> **Short rank-3 corridor lemma [unverified].** There is a corridor for AK(3)
> with \(1\le |w|\le4\), \(2\le |I|\le6\), at least two occurrences of
> \(z^{\pm1}\) in \(I\), and a resulting rank-2 Aut-floor at most 12.

The at-least-two condition removes the already-classified one-substitution
automorphic branches. The bounds describe the lemma being proved or refuted;
they are not presented as a search budget capable of disproving stable AC.

## Exact finite decision

The finite decision enumerates:

1. every freely reduced \(w\) over the two input generators of length 1--4;
2. both choices of eliminated generator \(b\);
3. both source relators and all cyclic rotations of each relator and inverse;
4. every freely and cyclically reduced \(I\) of length 2--6 over
   \(a^{\pm1},b^{\pm1},z^{\pm1}\), with exactly one \(b^{\pm1}\) and at least
   two \(z^{\pm1}\);
5. only identities for which the literal substitution \(z\mapsto w\)
   freely reduces to the selected source orientation.

For every identity, the code solves the isolator exactly, builds both output
relators, relabels \(z\), canonicalizes the pair, and computes its complete
Aut(\(F_2\)) floor using the existing Whitehead implementation. The certificate
hashes the ordered trace of all enumerated candidates and records every
accepted identity and distinct output orbit.

The local AC-search cap of 1,000 nodes is irrelevant here: this is a finite
word-equation enumeration, not an AC graph search. No solver, runner, notebook,
or existing result file is modified.

## Independent verification

The certificate verifier does not trust recorded output words. For every
accepted corridor it independently:

1. free-reduces \(I[z\mapsto w]\) and matches it against the named source
   orientation;
2. checks the exact-one-\(b\) and at-least-two-\(z\) gates;
3. solves \(b^\varepsilon q=1\) from a fresh cyclic rotation;
4. recomputes the two output relators by substitution;
5. verifies the recorded canonical pair and Aut witness;
6. reruns the complete bounded enumeration and compares the trace digest,
   candidate count, accepted count, and orbit partition.

The hand proof of enumeration completeness remains load-bearing. The
implementation supplies a replayable finite certificate of the candidate
lemma, not a proof that no longer corridor exists.

## Proof-loop continuation

If the short corridor lemma is true, its \(\mu\le12\) output is joined to a
classical AC certificate and the complete stable chain is expanded and
independently replayed.

If it is false, the next theorem attempt is not merely a larger bound. It is
the **primitive-isolator corridor lemma**: replace the exact-one-generator
condition by a primitive word \(v(a,b)\), normalize \(v\) to a generator using
an explicit Nielsen witness, and classify corridors
\(I=zuz^{-1}v^{-1}\). This strictly enlarges the structural mechanism while
retaining a finite, proof-producing normalization test.

## Version-control discipline

Checkpoint commits are pushed to `origin/codex/proofs` at least every twenty
minutes while tracked work is in progress. No pull request, merge, or unrelated
file change is authorized.
