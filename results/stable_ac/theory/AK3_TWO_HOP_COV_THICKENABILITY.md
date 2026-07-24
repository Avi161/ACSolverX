# AK(3) two-hop CoV thickenability result

Date: 2026-07-24

## Verdict

The paw-core one-loop synchronized-planarity theorem is **PROVEN**.  The
exact two-hop subword-CoV thickenability candidate is **REFUTED**.

Starting from the 34 distinct exact one-hop outputs, a second gated
subword-CoV move gives 1,724 raw paths and 1,352 distinct exact output
pairs.  The certificate checks the hypotheses of the proved Lemma-11 CoV
proposition at both hops, so all 1,352 outputs are stably AC-equivalent to
AK(3).  Every compatible Neuwirth link is certified non-spherical:

| support | outputs | spherical |
|---|---:|---:|
| \(K_4\) | 334 | 0 |
| \(K_4-e\) | 399 | 0 |
| \(C_4\) | 57 | 0 |
| \(P_4\) | 2 | 0 |
| \(K_4\) plus one loop | 164 | 0 |
| \(K_4-e\) plus one loop | 374 | 0 |
| paw plus one loop | 22 | 0 |
| **total** | **1,352** | **0** |

There is no positive requiring Regina validation.  This is a bounded null
result; AK(3) remains open.

## The new theorem

The proof is in:

```text
literature/proofs/AK3_PAW_ONE_LOOP_PLANARITY.md
```

Let \(G_0\) be a positive parallel expansion of a paw: a triangle on
\(a,b,c\) with a pendant class \(ad\).  Let

\[
p=m_{ab}+m_{ac}.
\]

Deleting the articulation \(a\) gives exactly two components.  The
cut-vertex block lemma therefore makes the triangle darts and pendant darts
complementary intervals at \(a\).  A spherical rotation is determined
uniquely by the four labeled parallel-class orders and by inserting the
pendant interval into any of the \(p\) cyclic gaps of the triangle
rotation.  These gaps include gaps inside a triangle parallel class.

If one loop is added at \(v\ne a\), then \(G_0-v\) is connected.  The loop
darts are consecutive in every spherical rotation, and they may be
inserted in either order into any of the \(q=\deg_{G_0}(v)\) core gaps.
Thus

\[
N(G)=
2pq\,m_{ab}!\,m_{ac}!\,m_{bc}!\,m_{ad}!.
\]

Enumerating those schemes, the two cyclic word phases, all
constraint-component seeds, and all global rank partitions is therefore
an exact decision procedure for the paw-plus-one-loop cases.

The theorem deliberately uses the fact that \(G_0-a\) has exactly two
components.  The corresponding block statement is false for an arbitrary
number of cut-vertex components.

## Exact certificate

Certificate:

```text
results/stable_ac/theory/ak3_two_hop_cov_thickenability.json
```

Exact counts:

| quantity | value |
|---|---:|
| distinct first-hop outputs | 34 |
| raw second-hop paths | 1,724 |
| distinct exact two-hop outputs | 1,352 |
| outputs certified stably equivalent | 1,352 |
| planar schemes exhausted | 82,776 |
| phase pairs exhausted | 10,328,938 |
| component seeds exhausted | 50,566,572 |
| closed component assignments | 18,621 |
| non-spherical outputs | 1,352 |
| unsupported outputs | 0 |
| Regina candidates | 0 |
| upstream one-hop trace SHA-256 | `d2ecadb2eb740dae256c3afec98ae69564522273313e7a129468e82086279d2d` |
| ordered two-hop trace SHA-256 | `89cb2d1a8829a040b189b55c07208ac6e5490c839c3680f98ed0928f2da330a4` |

Replay:

```bash
PYTHONHASHSEED=0 uv run --with pytest python3 -m \
  experiments.stable_ac.thickenable.two_hop_cov_thickenability_certificate \
  --verify
```

Verified output:

```text
CERTIFICATE VERIFIES: 1352 distinct two-hop stable CoV outputs,
1352 non-spherical, 0 Regina candidates
```

The verifier:

1. independently verifies the upstream one-hop certificate and trace;
2. regenerates the 1,724 exact composed paths;
3. checks the stable CoV hypotheses at each hop and deduplicates exact
   output pairs by first occurrence;
4. dispatches every support to a proved complete rotation solver;
5. exhausts every scheme, phase pair, component seed, and rank partition;
6. cross-checks the paw solver against an independent factorial census,
   including a stored witness that inserts the pendant block inside a
   parallel class;
7. independently reconstructs every positive fixture witness and checks
   Euler characteristic two; and
8. requires source hashes and complete payload equality.

## Bounded meaning

This rules out only the exact family of two sequential gated subword-CoV
moves starting at AK(3).  It does not prove a CoV-invariant obstruction,
does not cover a third hop or defining-relator CoV families, and does not
disprove stable Andrews--Curtis for AK(3).

The proof loop remains active.
