# AK(3) primitive-basis corridor result

Date: 2026-07-24

## Verdict

The primitive-basis short-corridor lemma is **REFUTED**.

The exact statement tested was:

> There is an automorphism \(\phi\in\operatorname{Aut}(F_2)\) with
> \(|\phi(x)|+|\phi(y)|\le4\) such that \(\phi(\mathrm{AK}(3))\) admits a
> hidden corridor with \(1\le|w|\le4\), \(2\le|I|\le6\), at least two
> \(z^{\pm1}\)-occurrences, exactly one isolated basis letter, and output
> Aut-floor at most 12.

The complete verified result is:

| quantity | value |
|---|---:|
| reduced ordered basis pairs | 200 |
| signed/cyclic quotient classes | 9 |
| class sizes | `16,16,16,16,24,24,24,24,40` |
| global minimum output floor | 14 |
| partition SHA-256 | `b3b617847055196fde09853fd1b7ea7bb7f6c94cb2a88e8c5866b5ae6f81309d` |

Every one of the 200 basis pairs carries a strict Nielsen-reduction witness
ending at two distinct signed generators. The verifier replays every witness,
reconstructs the transformed AK(3) pair and symmetry key, then reruns the
complete corridor decision on every quotient class.

This refutes only the finite primitive-basis lemma. It is not an invariant and
does not imply that AK(3) is stably nontrivial.

## Class certificate

| # | transformed-pair key | bases | accepted corridors | minimum | trace SHA-256 |
|---:|---|---:|---:|---:|---|
| 1 | `YXXYx \| YYYYXYXYXYX` | 16 | 952 | 14 | `9177d7c51bbdefd0c0482b075ded07ace8f60a9e0a15edbeb89360325e269d00` |
| 2 | `YXXYx \| YYYYYXYXYX` | 16 | 1,056 | 14 | `681635d95329cc2fab6119dbceec0ff530fe926d52e23d36acf61852d86c55b1` |
| 3 | `YXYXYx \| YYYYYXYYXYYXYYX` | 24 | 1,904 | 14 | `13f6b0c47c03e4367134620070cce3f179191bdb9efd1202bd993130c6f07d33` |
| 4 | `YXYXYx \| YYYYYYXYYXYYX` | 24 | 1,904 | 14 | `13f6b0c47c03e4367134620070cce3f179191bdb9efd1202bd993130c6f07d33` |
| 5 | `YXYxyx \| YYYYxxx` | 40 | 2,128 | 14 | `3729170b9ed945cbc79b98b85c794c39a70b19122693c8f42662434e0fe7d442` |
| 6 | `YXyXYxx \| YXXXYxYx` | 16 | 768 | 14 | `985f976f4fdad1e202d8bbc19b334ee1ab6e7a5061f1cb0d3d26f95abc7e2f90` |
| 7 | `YXyXYxx \| YXXYxYxYx` | 16 | 624 | 14 | `d08469a73badcd9608b17c92ed64985b0a9a55f7bdf7c830a71608b69d73fafa` |
| 8 | `YXyXYxxx \| YXXYxxYxx` | 24 | 636 | 14 | `5d5e8be4137405b0e04e54c9af1d7b6964843b1a22e842cbdcf4ce3b72ac2ebe` |
| 9 | `YXyXYxxx \| YXYxxYxxYxx` | 24 | 680 | 14 | `402264521e74d948a2a5d342325dee6b8ca98ffa261b5b65e4376b749030a42b` |

Each class enumerates 2,851,840 structurally admissible
word/template/source/isolation tuples. Equal traces in classes 3 and 4 are
allowed: their relator occurrence patterns induce the same accept/reject
trace even though their transformed-pair keys differ. Their outputs and Aut
witnesses are still recomputed separately.

## Proof foundation

The load-bearing proof is
`literature/proofs/AK3_PRIMITIVE_BASIS_CORRIDORS.md`.

It proves:

1. strict rank-two Nielsen reduction accepts exactly the basis pairs;
2. direct word-pair enumeration is complete under the image-length bound;
3. signed generator permutations, relator order, rotation, and inversion give
   bijections of corridor data and preserve output Aut-floor;
4. one corridor census per quotient key is therefore complete.

Before implementation, the strict reducer was compared with the repository's
independent classical Nielsen reducer on every word pair under the bound:
200 acceptances and zero disagreements.

## Replay

The certificate is:

```text
results/stable_ac/theory/ak3_primitive_basis_corridors.json
```

Replay:

```bash
PYTHONHASHSEED=0 .venv/bin/python3 -m \
  experiments.stable_ac.rank3_compression.primitive_certificate --verify
```

Verified output:

```text
CERTIFICATE VERIFIES: 200 bases, 9 classes, minimum 14, lemma REFUTED
```

Focused regression result:

```text
101 passed
```

covering the primitive-basis certificate, the original rank-3 corridor
certificate, existing CoV behavior, and the AK(3) certificates.

## What changed mathematically

The first hidden corridor proved:

\[
\mathrm{AK}(3)\sim_{\mathrm{st}}
\langle x,y\mid \texttt{xxxyXXXXY},\texttt{YxyxY}\rangle,
\]

whose floor is 14. The primitive-basis census proves that this failure is not
an artifact of choosing only the original or Aut-minimal basis within the
complete total-image-length-four ball. Every basis class still bottoms out at
14.

This is stronger than the first bounded result, but it remains finite. Longer
bases and longer one-stabilization corridors remain open.

## Next proof mechanism

The next attempt changes the stable rank rather than increasing either bound.

### Two-stabilization simultaneous-isolator theorem [unverified]

Start with

\[
 P=\langle x,y\mid R,S\rangle.
\]

Adjoin two defining generators:

\[
 D_z=z^{-1}w_1(x,y),\qquad
 D_t=t^{-1}w_2(x,y).
\]

Use the two defining relators to compress freely expanded spellings of
\(R,S\) to templates \(I_1,I_2\). Require:

1. \(I_1\) contains exactly one \(y^{\pm1}\), so it gives
   \(y=e_y(x,z,t)\);
2. after substituting \(y=e_y\), the second template contains exactly one
   \(x^{\pm1}\), so it gives \(x=e_x(z,t)\).

Two successive substitution-and-removal applications delete
\((y,I_1)\) and then \((x,I_2)\). The surviving defining relators become a
balanced presentation on \(z,t\), which is relabelled to rank two.

The proposed theorem must prove that this triangular dependency condition is
necessary and sufficient for this exact two-removal corridor. Its first AK(3)
candidate should use the braid conjugator \(w_1=xy\) from the proven
rank-3 transform and choose \(w_2\) from the power relator so both source
relations participate. This is a new stable mechanism, not a larger search
radius.

AK(3) remains open, so the main proof loop remains active.
