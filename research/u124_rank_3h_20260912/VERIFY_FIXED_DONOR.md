# Fixed-donor exclusions: PASS within the stated metric

For the shear x→y^p x y^q, the BS donor x^-1 y^m x y^-n is conjugated by
y^q. The cyclic gap following signs s_i,s_(i+1) changes by
`(p+q)*(s_i+s_(i+1))/2`. The flow matrix satisfies
`M*1=(m-n)*((s_i+s_(i+1))/2)`. Thus when |m-n|=1, constant integer flow
`q_i=(p+q)/(m-n)` reproduces every such shift at the expanded cyclic-word
level. Twenty-four signed free-word controls verify this, including the wrap
gap and both consecutive orientations. For nonconsecutive exponents this
argument requires m-n to divide p+q. `verification_stable_shear.json` records
the controls and that limitation.

The stronger short-companion deduction is also valid. The source establishes
stable-length invariance and, for positive cyclic stable length, the Collins
criterion: conjugate cyclically reduced forms differ through cyclic permutation
and associated-subgroup conjugation. Its normal-form transfer equations give
the corresponding subgroup powers along each stable edge.
See [Borovik, Myasnikov and Remeslennikov, Section2.2, Theorem3.9 and Lemma4.3](https://eprints.maths.manchester.ac.uk/991/1/OmskVestnik.pdf).

In the cyclic exponent formulation, those integer edge transfers contribute
`e_i'=e_i-B_i q_i+A_(i+1) q_(i+1)`. The seam variable represents the
associated-subgroup conjugator, rather than imposing a zero seam. Cutting at
a different stable edge only reindexes this system and its summed coin cost.
An outer base conjugation can be removed at the cyclic cut. Thus the recorded
cyclic flow family covers the same-stable-length conjugacy competitors.

Now take a shortest cyclic spelling V of a companion with cyclic Britton
stable length t>=3, stable exponent±1, and packed power cost C0<=3. Let T be
V's number of stable letters. Conjugacy invariance gives T>=t; the stable
exponent gives the same odd parity. If T>t, then T>=t+2. Both signs occur,
forcing at least two nonempty intervening power-token gaps in a freely cyclically
reduced spelling. Consequently |V|>=T+2>=t+4, already longer than t+C0.
Therefore T=t. Expanding helpers cannot introduce a removable cyclic Britton
pair, because that would reduce conjugacy stable length below t. The same-t
flow classification applies, and exact power repacking never raises cost.
A completed negative flow search below C0 therefore proves that the current
companion is shortest in its conjugacy class for this fixed generating metric.

This is an audited deduction, not a verbatim result in the cited paper.
For larger power cost the extra-pair lower bound is insufficient. General BS
geodesics require more than ordinary Britton reduction, consistent with
[Diekert and Laun, Section3](https://arxiv.org/pdf/0907.5114).

Read-only checks reconstruct the root definition, expanded BS donor and
companion from every saved exact tuple in `flow_exact_diagnostic.json`.
All124 IDs match the pinned baseline. The33 recognized cases have stable
length5 and exponent±1, no cyclic pinch, completed negative searches at the
correct cost ceiling, and independently reconstructed rational bounds. Two
have power cost2 and31 have power cost3. Their actual target lengths equal
stable length plus exact packed cost. `verification_fixed_donor.json` records
these checks; no flow or census search was rerun.

This excludes shortening that one target by products with its two fixed
donors, target conjugations and inversions in the fixed alphabet, regardless
of intermediate length. Changing a donor, metric, helper system or other
relator leaves the hypothesis. It proves no global AC obstruction.
