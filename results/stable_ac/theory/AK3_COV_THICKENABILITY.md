# AK(3) one-hop CoV thickenability result

Date: 2026-07-24

## Verdict

The one-loop synchronized-planarity theorem is **PROVEN**.  The exact
one-hop subword-CoV thickenability candidate is **REFUTED**.

The complete no-collapse subword family for AK(3) contains 38 candidate
words and produces 34 distinct exact presentation pairs.  Every transform
satisfies the hypotheses of the proved Lemma-11 CoV proposition, so every
output is stably AC-equivalent to AK(3).  All 34 compatible Neuwirth links
are certified non-spherical:

| support | outputs | spherical |
|---|---:|---:|
| \(K_4\) | 15 | 0 |
| \(K_4-e\) | 9 | 0 |
| \(K_4\) plus one loop | 2 | 0 |
| \(K_4-e\) plus one loop | 8 | 0 |
| **total** | **34** | **0** |

There is no positive requiring Regina validation.  AK(3) remains open.

## The new theorem

The proof is in:

```text
literature/proofs/AK3_ONE_LOOP_SYNCHRONIZED_PLANARITY.md
```

Let \(G\) have exactly one loop edge \(\ell\) at a vertex \(v\), and suppose
deleting \(\ell\) gives a positive parallel expansion \(G_0\) of \(K_4\) or
\(K_4-e\).  Since \(G_0-v\) is connected, the Jordan curve represented by
\(\ell\) puts every nonloop edge on one side.  Therefore the two loop darts
must be consecutive in every spherical rotation.

Conversely, insert the two loop darts consecutively in any angular gap of
any spherical core rotation.  This is a bijection.  If
\(d=\deg_{G_0}(v)\), then

\[
N(G)=2d\,N(G_0).
\]

The exact signed-rank system is obtained by taking every proved core scheme,
every one of the \(d\) insertion gaps, both loop-dart orders, and the
existing two cyclic phases.  The loop edge has fixed rank zero; all other
parallel classes retain their all-different ranks.  The prior propagation
proof applies because it requires injective partitioning slot maps, not
loopless \(A\)-edges.

## Exact certificate

Certificate:

```text
results/stable_ac/theory/ak3_cov_thickenability.json
```

Exact counts:

| quantity | value |
|---|---:|
| candidate subwords | 38 |
| distinct exact CoV outputs | 34 |
| outputs certified stably equivalent | 34 |
| planar schemes exhausted | 1,419 |
| phase pairs exhausted | 139,804 |
| component seeds exhausted | 553,571 |
| non-spherical outputs | 34 |
| unsupported outputs | 0 |
| Regina candidates | 0 |
| ordered trace SHA-256 | `d2ecadb2eb740dae256c3afec98ae69564522273313e7a129468e82086279d2d` |

Replay:

```bash
PYTHONHASHSEED=0 uv run --with pytest python3 -m \
  experiments.stable_ac.thickenable.cov_thickenability_certificate \
  --verify
```

Verified output:

```text
CERTIFICATE VERIFIES: 34 stable CoV outputs,
34 non-spherical, 0 Regina candidates
```

The verifier:

1. regenerates the exact 38-word gated subword family;
2. reruns every transform and requires all 34 Lemma-11 hypotheses;
3. checks output distinctness and retains the exact rank-three intermediate
   for each stable move;
4. dispatches every loopless support to the proved \(K_4/K_4-e\) solver;
5. dispatches every remaining support to the complete one-loop solver;
6. exhausts every scheme, phase, component seed, and rank partition;
7. agrees with an independent factorial census on one spherical and one
   non-spherical one-loop fixture; and
8. requires source hashes and complete payload equality.

## Bounded meaning

This is the first direct thickenability decision over every output of an
exact targeted Lemma-11 stable-move family from AK(3).  It rules out that
one-hop family only.  It does not say thickenability is invariant under CoV,
does not cover two composed CoVs or universe-family defining-relator
branches, and is not a stable-AC obstruction.

The proof loop remains active.
