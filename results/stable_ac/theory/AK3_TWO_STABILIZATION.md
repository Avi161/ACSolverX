# AK(3) immediate two-stabilization result

Date: 2026-07-24

## Verdict

The triangular two-removal theorem is **PROVEN**. Its first finite AK(3)
candidate is **REFUTED**.

The exact candidate allowed:

- two nonempty freely reduced defining words \(w_z,w_t\), each of length at
  most two;
- a freely/cyclically reduced braid template of length at most six;
- exactly one occurrence of the first eliminated generator \(y^{\pm1}\);
- both new generators \(z,t\) in the template;
- an immediate second relator with exactly one \(x^{\pm1}\);
- two successive Lemma-11 removals;
- a final rank-two output of Aut-floor at most 12.

The complete certificate found minimum floor 13, so no output reaches the
classical length-at-most-12 bar.

This refutes only the stated finite immediate-removal lemma. It is not a
stable-AC obstruction.

## Exact census

| quantity | value |
|---|---:|
| defining words | 16 |
| ordered defining-word pairs | 256 |
| structural templates | 43,296 |
| literal word/template cases | 11,083,776 |
| accepted braid identities | 31,232 |
| distinct rank-3 tuples after removing \(y\) | 3,224 |
| immediate triangular certificates | 18,528 |
| distinct raw rank-2 outputs | 352 |
| canonical rank-2 outputs | 96 |
| output Aut-orbits | 9 |
| minimum output floor | 13 |
| trace SHA-256 | `898bac80772fcc19e0f321a9970e1da1701b91a768788ba1d85bcbffe1fdaa1b` |

The raw-output floor distribution is:

| floor | outputs |
|---:|---:|
| 13 | 64 |
| 14 | 128 |
| 16 | 16 |
| 23 | 16 |
| 24 | 40 |
| 25 | 16 |
| 27 | 16 |
| 28 | 40 |
| 43 | 16 |

All 64 minimum outputs have the same complete Whitehead representative:

```text
YXYxyx | YYYYxxx
```

which is AK(3)'s own Aut(\(F_2\))-orbit. Thus the minimum certificates loop
back to AK(3) under a change of basis; they do not reach orbit-2 or the
standard presentation.

## The theorem

The proof is in:

```text
literature/proofs/AK3_TWO_STABILIZATION.md
```

Given

\[
 P=\langle x,y\mid R,S\rangle,
\]

adjoin

\[
 z^{-1}w_z,\qquad t^{-1}w_t.
\]

If a simultaneous template \(I_y\) expands literally to one source relator
and contains one \(y^{\pm1}\), defining-relator substitutions turn that source
into \(I_y\). Lemma 11 removes \(y\), leaving three relators over \(x,z,t\).
If one already contains one \(x^{\pm1}\), a second Lemma-11 application
removes \(x\). The two survivors form a balanced presentation on \(z,t\).

Every step is a stable-AC composite; no arbitrary Tietze move is used.

## Order and reduction audits

Two pre-certificate errors were caught and quarantined:

1. For \(w_z=xy,w_t=yx\), the valid braid factorization is
   \[
   (xy)x\,y^{-1}(yx)^{-1}=xyxYXY.
   \]
   The invalid order
   \[
   (xy)x(yx)^{-1}y^{-1}
   \]
   freely reduces to `xY`. A nine-move rank-3 solve derived from the invalid
   spelling is not connected to AK(3) and appears nowhere in the certificate.
2. Substituting \(y^{-1}=x^{-1}z^{-1}t\) in \(x^3y^{-4}\) cancels one
   boundary `xX`. The exact reduced relator is
   `xxZtXZtXZtXZt`, not the unreduced `xxxXZtXZtXZtXZt`.

Both identities are pinned in tests and rechecked before every census row is
accepted.

## Replay

Certificate:

```text
results/stable_ac/theory/ak3_two_stabilization.json
```

Replay:

```bash
PYTHONHASHSEED=0 .venv/bin/python3 -m \
  experiments.stable_ac.rank3_compression.two_stabilization_certificate \
  --verify
```

Verified output:

```text
CERTIFICATE VERIFIES: 256 word pairs, 352 outputs,
minimum 13, lemma REFUTED
```

The verifier:

1. re-expands every stored braid template;
2. resolves both isolators independently;
3. recomputes the rank-3 and rank-2 relators;
4. verifies every Aut witness;
5. reruns all 11,083,776 cases and compares the entire derived payload.

Focused regressions passed:

```text
108 passed
```

covering all three new corridor certificates plus the existing CoV and AK(3)
certificates.

## Scope

What is proved:

- the general immediate triangular two-removal theorem;
- completeness of the finite defining-word/template census;
- every endpoint in the certificate is stably equivalent to AK(3);
- no endpoint in this class has floor at most 12.

What remains open:

- an additional AC move before the second removal;
- longer words/templates;
- nontriangular dependencies;
- three or more stabilizations;
- stable triviality or nontriviality of AK(3).

AK(3) therefore remains open.

## Next proof attempt

The next mechanism permits exactly one AC edge after the first removal.

### One-edge second-stage compression theorem [unverified]

After the \(y\)-removal, let the rank-3 tuple be

\[
 (A,B,C)\subset F(x,z,t).
\]

Choose distinct indices \(i,j\), a sign \(\delta\in\{\pm1\}\), and cyclic
rotations of \(A_i\) and \(A_j^\delta\). Replace

\[
 A_i\longmapsto
 \overline{\operatorname{rot}(A_i)\,
 \operatorname{rot}(A_j^\delta)}.
\]

Up to conjugating the tuple, this is a Definition-2.1 AC move: multiplication
of one relator by a conjugate of another. If any relator in the resulting
triple contains exactly one \(x^{\pm1}\), Lemma 11 removes \(x\) and produces
a rank-two output.

The next finite candidate keeps the already-certified defining-word/template
bounds and exhausts this single AC edge for each of the 3,224 distinct
rank-3 tuples. It is strictly broader than immediate removal but is not a
deeper graph search. A hit at floor at most 12 would supply a concrete stable
proof candidate; a null would refute only the one-edge candidate.

The main proof loop remains active.
