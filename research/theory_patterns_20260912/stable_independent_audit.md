# Independent stable-AC proof and witness audit

Status: **PASS for the stated trivial-group scope**, with a rank-bound
clarification below. No defect was found in the stored algebraic endpoints.
The stable records are **theorem-backed stable composites**, not expanded
elementary stable-AC certificates. The two unbounded fixed-donor exclusions
also pass this proof review; they are not obstructions to arbitrary AC moves.

The audit checks `STABLE_CERTIFICATE_CONVENTIONS.md`, the coupled-power
theory note, and its special-power, general-power, and literal-word scripts
and saved records. `stable_independent_audit.json` pins their SHA-256 hashes
and the exact `aca_124_best.csv` hash. The verifier is
`check_stable_independent.py`; it writes only the independent audit JSON.
Source changes during a run cause failure.

## Stable defining-generator construction

Let the original tuple normally generate the free group on its generators.
For any old word w, the definition of normal closure supplies a finite
identity `w=F1 ... Fk`, where each Fj is a conjugate of a signed old relator.
After adjoining the strict pair `(z,z)`, invert its relator and append these
factors. To append `c^-1 R_i^epsilon c`, temporarily invert/conjugate the
old donor, multiply the new relator on the right, and undo the donor's unary
operations. Old relators remain exactly unchanged, and the new one becomes
`D=z^-1 w`. Every conjugating word is finite and uses only old generators.

This does not presuppose an AC trivialization of the original tuple.
Existence of the normal-product identity follows from group triviality, not
from the AC conjecture. A fair enumeration by total expression size would
eventually find it, but no such identity has been generated for the U124
records in these files. The argument supplies neither a practical running
time nor a bound on the elementary move count or maximum word length.

For literal compression, the recipient error is exact:
`(P w Q)^-1(P z Q)=Q^-1 w^-1 z Q=Q^-1 D^-1 Q`.
For an inverse block, `w z^-1=z D z^-1` gives the corresponding source
factor. Repeated block substitutions therefore use ordinary donor-restored
operations. If a template is only freely equal after expansion, substitute
its z letters by w in the reverse direction and reverse the resulting
ordinary certificate. This handles hidden free cancellations without treating
quotient equality as a certificate.

For deletion, orient the unique-occurrence relator to `a^-1 e`, with e free
of a, and use it to remove a from every other relator. The presentation
defined by the remaining a-free relators is isomorphic to the current group,
so it is trivial. Its relators consequently normally generate the free group
on the surviving generators. Express e as a finite product of their signed
conjugates, append its inverse product to `a^-1 e`, and invert the result.
Now the literal relator a is the only occurrence of a in the presentation,
so strict destabilization is legal. The new normal-product factors do not
involve a; no circular assumption about the deleted generator is needed.

Thus the defining-word introduction, substitution, and elimination mechanism
is a valid stable-AC composite. The needed hypothesis is normal generation
of the relevant words; known triviality is a sufficient uniform hypothesis.
Unimodular abelianization alone does not supply it. For the original MS
family the trivial-group hypothesis is confirmed directly by Miller–Schupp,
Corollary 3, with Theorem 1 and Lemma 2 providing its proof. The cited PDF
host timed out during this audit; the same primary paper was read in
[Schupp's uploaded full text](https://www.researchgate.net/publication/228568872_Some_presentations_of_the_trivial_group).
The audit relies on the supplied equivalence provenance to transfer this
hypothesis from the MS family to the exact retained U124 inputs; it does not
replay the older census-equivalence archive.

## Ambient automorphisms and the rank clarification

The direction of the Nielsen example is correct. To apply `a -> a b` to
each relator, introduce `z=a b^-1`, solve this relation for `a=z b`,
substitute in the old relators, eliminate a, and label the surviving z as a.
The result is the desired forward image, not its inverse. Left multiplication,
inversion, and generator exchange follow by the corresponding elementary
Nielsen changes. A finite Nielsen decomposition proves the claim for every
free-group automorphism in this trivial-group scope.

All eight elementary ambient maps actually used in the saved descent traces
have explicit inverse maps in the independent checker. Both compositions
are checked to be the literal basis `(x,y)`, and each recorded before/after
pair is independently substituted and cyclically normalized. Relator
inversions, rotations, and order changes in that normalization have ordinary
AC realizations; they are not being charged as zero-cost elementary moves.

**Clarification to the author's caution about rank:** this construction does
give a peak-rank bound. A rank-two isolator corridor requires one fresh
generator, reaches rank three, and returns to rank two. Normal-product
expansion changes relators using the generators already present and never
introduces another generator. Sequential elementary Nielsen realizations
likewise need only one temporary generator at a time. Thus these composites
have a finite realization of rank at most three, up to the stated harmless
generator labeling. Its elementary move count and peak total relator length
remain unknown. The sentence in the audited theory snapshot saying that a
peak-rank bound requires the missing normal-product ledger is unnecessarily
weak and should be corrected; it is not a failure of the equivalence proof.

## Exact endpoint checks

An independent signed-integer free-group reducer checks all expansions,
unique-letter isolation, recovered words, substitution into the defining
relator and companion, surviving-generator labels, and total lengths.

For each literal-word witness it verifies:

1. The saved cyclic prefix and cut give the saved source orientation.
2. Expanding z to the defining word gives exactly that source, and expanding
   the compressed companion gives its exact original relator.
3. The isolator has one occurrence of the eliminated generator with the
   saved sign; substituting the recovered word makes the isolator freely empty.
4. Substitution into `z^-1 w` and the compressed companion gives the two saved
   rank-two endpoint words, before any ambient descent.
5. Each displayed rank-three state retains all three relators. Their summed
   freely reduced lengths reproduce the recorded boundary maximum.

The pure-power witnesses receive the analogous checks, including every signed
division identity `e=dq+r`, its selected order, and each saved individual
run replacement. The special consecutive-BS formulas are checked as actual
isolator expansions, including the hidden negative-power cancellation in
the second definition.

The verifier independently checks all stored best witnesses and replays the
declared template enumeration to check every evaluated endpoint:

| Mechanism | Stored best witnesses | Reconstructed endpoints |
|---|---:|---:|
| Two special BS power definitions | 49 | 200 |
| General literal pure-power isolators | 115 | 969 |
| Literal defining words of lengths 2–6 | 124 | 1,483 |

The endpoint reconstruction reuses the author's finite template enumerators
and companion-choice generator. Word algebra, isolation, expansions, lengths,
and recorded ambient maps are checked independently. This establishes the
reported outcomes for the declared enumeration, not completeness over all
possible compression templates. All per-row endpoint counts and best lengths
match the saved records. No reconstructed endpoint supplies a strict gain.

The saved literal-word JSON contains only each row's best full witness,
not 1,483 complete records. The independent audit therefore reconstructs
the full declared enumeration and records per-row counts and hashes of the
verified endpoint/length records. No row limit is hit. Internal decomposition
truncation remains an admitted limitation of the author algorithm.

The rank-three boundary lengths are maxima of selected displayed states.
They do not bound the words encountered while adding the defining generator,
restoring substitution donors, or deleting the isolated generator. The
theorem-backed rank-three bound and the unknown elementary word-length peak
must remain separate in the final table.

## Unbounded exclusion review

The synchronized reciprocal-power rectangle argument is valid under its
nonzero, coprime, absolute-value-at-least-two hypotheses. A height B corridor
through `t^-1 a^m t=a^n` requires an incoming exponent divisible by
`|m|^B` for B>0, or by `|n|^(-B)` for B<0. Coprimality proves necessity
inductively: outgoing factors cannot supply any of the next required incoming
factors. Repeating the same argument for the reciprocal corridor gives
`|A|>=2^|B|` and `|B|>=2^|A|`, which contradict each other. The proof is
unbounded, but it forbids only those two complete single-source transports.
It does not forbid arbitrary interleaved diagrams or donor changes.

The torus fixed-donor primitive-image exclusion also passes. With
`u=a t^k` and N=2k+1, the companion becomes `u^2 t^-N` up to a verified
conjugation. The explicit inverse substitution is `a=u t^-k`. In
`C2*C_N`, the other relator has 2m+1 u-syllables, separated by the stated
nonzero residues. In particular the last cyclic boundary contributes -1
modulo N; omitting it would change the proof.

An ambient primitive with the same image up to conjugacy must have exponent
vector `(h,j)` satisfying `2h+Nj=1`. Thus j is odd and nonzero, h and j
have opposite signs, and `k<=|h|/|j|<=k+1`. The needed external theorem is
the signed Christoffel classification of primitive conjugacy classes,
explicitly stated in
[Kassel–Reutenauer, Corollary 3.3(b)](https://arxiv.org/pdf/math/0507219).
The uniform-sign property is also supported by
[Gilman–Keen, Section 5](https://arxiv.org/html/0802.2731).

Consequently a primitive candidate has |j| u letters and t runs of lengths
k or k+1. Its projection suffers no syllable cancellation, so its t residues
belong to `{k,k+1}`. The actual relator contains residues 1 and 2k; for k>=2
these exclude conjugacy in the free product. Conjugate cyclically reduced
free-product words of syllable length at least two agree up to cyclic
rotation, which is exactly the invariant used here.

For k=1, equality of u-syllable counts forces `|j|=2m+1`. The two candidate
exponent vectors in the note are correct. A Christoffel run sequence can be
written as differences of consecutive floor values. Every window sum
telescopes, so equal-length cyclic windows have sums differing by at most
one. After subtracting the common shorter run length, this proves the
required binary balance directly. The actual circular sequence has one block
of each run value, with both block lengths at least two when m>=2. It has
length-two windows containing zero versus two longer runs and is unbalanced.
For the negative t orientation, raw residue 2 corresponds to run length 1;
this conversion explains the note's counts of m+1 ones and m twos. For the
other orientation the binary sequence is complemented. Both fail balance.

The independent checker reproduces all 42 stored torus coordinate and
projection cases, including both necessary primitive candidates. Only
`(m,k)=(1,1)` has a matching projection; a matching projection alone does
not prove a primitive lift. The unbounded proof, rather than these finite
cases, supports exclusion for `m>=1,k>=2` and for `k=1,m>=2`.

Recipient inversion creates no gap: if the inverse class had a primitive
lift, its inverse would be a primitive lift of the original class. The
exclusion assumes the torus donor is retained and permits recipient
conjugation and multiplication by its signed conjugates. Stable generator
changes or changing the donor are outside this fixed-donor statement.

## Remaining limitations

No U124 trivialization, strict length improvement, expanded normal-product
ledger, useful elementary move bound, or elementary peak-length bound is
produced by this audit. The known-trivial-input premise and the cited
rank-two primitive classification remain mathematical inputs. The supplied
unbounded arguments have been reviewed, not formalized in a proof assistant.

The complete script run checks 2,652 reconstructed stable endpoints, 288
stored best witnesses, and 42 torus projection cases in approximately 2.42
CPU seconds. It performs no presentation search and no JIT compilation.
Audited source hashes and exact machine outcomes are in the JSON artifact.
