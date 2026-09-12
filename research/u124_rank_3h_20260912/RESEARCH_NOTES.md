# Arbitrary-rank stable AC shortening on U124

Three-hour research continuation: 2026-09-12, 12:59:28–15:59:28 UTC. Branch: `codex/theory-patterns-3h`. This note is a checkpoint; the exact current counts and source pointers are in [CURRENT.json](CURRENT.json).

**Current result: 0/124 trivializations, 18 further shortened rows, total length 2180 → 2162.** The saved rank-two inputs total 2356; the older archival inputs total 2446. These are distinct baselines. All defining relators count. Eighty-nine rows are shorter than the saved rank-two inputs; the new gains improve existing shortened rows, rather than increasing that89-row coverage.

No AC counterexample has been proved. Bounded failures, fixed-donor geodesicity and endpoint rank bounds below do not establish one.

- [All124-row table](CURRENT.md) and [CSV with witness pointers](CURRENT.csv).
- [Full saved-rank-two-to-endpoint composite paths](verification/export/all124_stable_composite.jsonl); consult its [manifest](verification/export/manifest.json) for the exported checkpoint.
- [Executed experiments and measured costs](EXPERIMENT_INDEX.md).
- [Exchange and collection proofs](EXCHANGE_THEORY.md), [root/flow/torus proofs](theory_relators.md), and [rank-length theorem](RANK_LENGTH_BOUND.md).

## Latest objective: retain high rank and shorten individual relators

The user explicitly prefers retaining a higher-rank state when its individual relators become simpler, even if total length grows. The minimum-total table above remains a separate historical objective. It must not be used to discard the new short-relator states.

[Retained high-rank table for all124](HIGH_RANK_TRIANGLES.md), [CSV](HIGH_RANK_TRIANGLES.csv), and [exact words and witnesses](HIGH_RANK_TRIANGLES.json): every relator has length at most3, ranks7–12, combined total3444. Shared binary definitions achieve this in0.12465 CPU seconds; no automatic destabilization occurs. Triangularization is universal, so these124 representations do not constitute new solves. [Full retained-rank composite paths](verification/export/all124_retained_high_rank.jsonl) independently replay from the saved rank-two inputs; [their manifest](verification/export/retained_high_rank_manifest.json) pins the sources. The811 new defining steps are all retained, with no removal in this suffix.

A sharper terminal theorem is constructive: a balanced trivial presentation with all relators of length at most2 is a signed-edge forest with one singleton per component. Propagating each singleton along its tree gives an ordinary AC trivialization at unchanged rank without increasing any relator length. Conversely, if every relator has length exactly2 and rank is positive, mapping every generator to the nonidentity element of C2 gives a nontrivial quotient. See the full proof and compiler in [theory_relators.md](theory_relators.md) and [theory_short_relators.py](theory_short_relators.py).

A new rank-preserving triangle flip maps `(Zab,zcd)` to `(Zbc,azd)` when z occurs only in these two triangles. It is the explicit ambient automorphism `z -> a z C`, inverse `z -> A z c`, with row conjugations. Uppercase denotes inversion. If c=B, it exposes singleton Z. Endpoints retain maximum relator length3; the two Nielsen factors can transiently produce length4. A known-trivial rank11 control retains rank11 and shortens total15→13. The subsequent [all124 bounded test](HIGH_RANK_FLIPS.json) used at most1,000 algebraic units per row (117,984 total), taking36.82 CPU seconds and36.92 search wall seconds. It found0 further objective improvements; all ranks and endpoints remain unchanged. This move alone is not claimed to solve all triangles.

## Further reductions in this continuation

| ID | Phase start | Best total | Rank | First successful mechanism |
|---|---:|---:|---:|---|
| aca_5 | 18 | 17 | 3 | Coupled commutator aliases |
| aca_43 | 17 | 16 | 3 | Exact commutator collection |
| aca_44 | 17 | 16 | 3 | One-helper commutator prefix |
| aca_56 | 18 | 17 | 3 | One-helper commutator prefix |
| aca_67 | 19 | 18 | 3 | Exact commutator collection |
| aca_72 | 17 | 16 | 3 | Growing donor move, then Whitehead descent |
| aca_75 | 19 | 18 | 3 | Neutral donor rewrites |
| aca_79 | 18 | 17 | 3 | Iterated commutator collection through rank five |
| aca_80 | 17 | 16 | 3 | Growing donor move, then Whitehead descent |
| aca_83 | 20 | 19 | 3 | Neutral donor rewrites |
| aca_84 | 20 | 19 | 3 | Neutral donor rewrites |
| aca_87 | 19 | 18 | 3 | Exact commutator collection |
| aca_88 | 18 | 17 | 3 | Exact commutator collection |
| aca_95 | 18 | 17 | 3 | Cancellation-aware defining template |
| aca_99 | 18 | 17 | 3 | A neutral basis change followed by recompression |
| aca_101 | 21 | 20 | 3 | Root denomination change |
| aca_106 | 20 | 19 | 3 | Exact commutator collection |
| aca_111 | 21 | 20 | 3 | Growing donor move, then Whitehead descent |

The additional rank-four-to-three change for `aca_109` preserves length20. For `aca_111`, the current path now reduces both rank and length. All best endpoints currently have rank two or three.

## Work and certificate scope

Each newly generated presentation probe is serial and uses at most1,000 named algebraic work units per row. These count such operations as exact donor matches, dictionary checks and minimum cuts; they are **not** interchangeable with heap pops or elementary AC moves. Imported seed-discovery costs are historical and excluded. The experiment index reports search CPU and wall time separately, excluding verification, cooldown and initialization. Two separate small S20 continuations are recorded in `primitive_search_results_corrected.json`.

Every accepted transition has exact signed-integer words and a replayed ordinary or stable-composite witness. The full exported chains begin at the saved rank-two inputs; they are not merely suffixes from an unexplained seed. Lemma11 additions/removals use the known-trivial-group lineage. Their existential normal-product realizations have **not all been expanded into individual elementary stabilized moves**. Ordinary retained-donor factors are explicit.

## Retained-donor substitutions

Let `(R1,...,Rr)` be the relator tuple, with rankr equal to its number of
generators and relators. Uppercase letters denote inverses. Let D be a
retained donor distinct from the target R. Suppose a signed cyclic rotation
of D is S=A B and R=P A Q. The exact replacement is

    P A Q  ->  P B^-1 Q.

If S=t^-1 D^epsilon t, where epsilon is1 or−1 and t is the chosen prefix,
the right multiplication correction is

    c^-1 D^(-epsilon) c,       c=t A Q.

Indeed A^-1 S^-1 A=A^-1 B^-1. Multiplication gives the new target by free
reduction. The donor can be inverted/conjugated, multiplied into the target,
and restored using ordinary AC moves. For a target crossing its cyclic seam,
the target-frame prefix is included in c; `plateau.py` checks the complete
word identity before admitting an edge. The independent auditor checks it
again with separate word routines.

Length-neutral replacements are retained because a later replacement or
basis change may decrease length. `completion.py` also builds short products
of conjugates of several retained donors. Its critical-overlap construction
is a bounded version of classical completion, not a universal new theorem.
Each derived rule retains its full normal-product ledger. The current pilot
does not add a gain beyond its imported seeds.

## Defining templates that permit cancellation

Choose words w_j in the old generators and fresh helpers z_j. Add all
defining relators z_j^-1 w_j. For each original relator choose a template T_i
in old letters and the helpers such that expanding every z_j to w_j gives
an explicitly recorded conjugate or inverse of the original relator.
All defining relators remain in the length count.

This is a valid stable AC composite on these known trivial-group inputs:
apply Lemma11 in reverse to the expanded presentation. For several
definitions the helpers can be eliminated one at a time; the original
rank-independent definitions involve only old generators. Exact template
expansion, row orientations, normalization and completeness of the retained
relator list are independently checked. Unimodular abelianization alone is
not the hypothesis establishing group triviality.

The prefix-graph implementation finds a short template by graph paths whose
labels expand to the desired old word. Such a path can use helper words
that cancel across their boundaries, so it is more general than literal
substring replacement. The weighted-automaton version has a stronger
fixed-dictionary, fixed-orientation geodesic guarantee when its saturation
and query both finish. A truncated query returns only a verified candidate.
See `EXCHANGE_THEORY.md` for the exact proof and its scope.

For aca95, begin at the saved rank2 source of length19:

    (YYXXXyxx, YYxyxyXYxyX).

Define z=xyXY. The first implementation finds

    (ZZYXy, ZYZXXyxY, ZxyXY),       total18.

The whole-tuple map fixing x,y and sending z to zY then gives

    (ZZXXyx, ZYXyyZy, ZxyX),        total17.

Its inverse fixes x,y and sends z to zy. The alternate length18 literal
compression with this same defining word is whole-Aut-minimal; using a
different freely equal template is what exposes this descent. The saved
phase baseline for this row was already18, so the new gain is one letter.

## Root helpers and cyclic exponent flows

A retained defining relation z=y^k changes the cost of spelling y^e to

    c_k(e) = min { |a|+|b| : a+k*b=e }.

Here k and e are signed integers; a counts y letters and b counts z
letters. A second retained donor may encode x^-1 y^m x=y^n after expanding
z. Exact normal products implement power collection and simultaneous
transfers across several stable letters x or X. The dynamic program
optimizes the sum of the block costs. The signed and cyclic frame
conventions are proved in `theory_relators.md`.

For a cyclically Britton-reduced input, no integer flow creates its first
stable-letter cancellation: at an adjacent opposite-sign pair, the middle
exponent changes by a multiple of the same relevant BS exponent. Divisibility
at that boundary is invariant. Existing pinches are handled first.

The exact flow code derives a sufficient finite box using a rational inverse
of the cyclic transfer matrix and a total-cost bound. In
`flow_exact_diagnostic.json`, all33 matching current flow cases finish this
complete bounded computation, and none admits strict shortening in this
fixed-root, fixed-donor flow family. Forty-three rows have a pure-power root
definition; only33 have the second recognized BS donor. These are restricted
family exclusions, not obstructions to arbitrary AC or stable AC moves.

Changing the helper escapes that restriction. The ambient map

    z -> y^(k-l) z

fixes the other generators and sends z=y^k to z=y^l. Its inverse sends
z to y^(l-k)z. For aca101, k=7 and l=4 give the complete path

    (ZXzxY, Zyyyyyyy, YXXXYxYx)              total21
    (ZYYYXyyyzxY, Zyyyy, YXXXYxYx)           total24
    (ZZXYzzx, Zyyyy, YXXXYxYx)               total20.

The first transition is the invertible basis map; the second is an ordinary
retained-donor cyclic repacking. All three defining/ordinary relators are
counted. `verification_root_metric_pilot.json` replays the exact path.

## Exact commutator collection and coupled aliases

For two old words `u,v`, write `[u,v]=u v u^-1 v^-1`. A retained helper
`c=[u,v]` gives the free-word identity

    u v u^-1 = c v.

Repeated collection introduces the necessary higher commutator helpers and
retains every definition. No commutator is discarded as if the group were
nilpotent. Each generated template expands exactly to the original word.
The expansion can grow quickly, so the implementation prices the complete
proposed collection before allocating it. A useful prefix of the collection
is itself a valid defining-template transition.

The all-row spelling problem is coupled: a shorter spelling of one relator
can block a useful whole-tuple basis change. For `aca_5`, use the definition
`c=[x,Y]`, where uppercase denotes inverse. The shortest independent choice
from the implemented finite row-alias catalogs has total21, including the
definition. A complete Whitehead pass proves that particular tuple is
whole-Aut-minimal. Another choice in the same catalogs has total22, but two
Whitehead moves give22→19→17. Thus the extra template letter exposes five
letters of descent. This comparison is saved in `exchange_aca5_worked_path.json`;
it does not claim the catalogs exhaust every possible equivalent spelling.

For `aca_79`, the successful path from the phase incumbent has

    ranks:   3, 4, 5, 4, 4, 4, 4, 4, 3, 4, 3, 3, 3, 3
    lengths:18,22,26,37,27,24,22,21,19,20,26,20,18,17.

The path reaches rank five at length26; its largest length37 occurs at rank
four. This is an actual useful higher-rank detour, not a comparison between
unrelated presentations. `verification_collector_gains.json` independently
replays it. Higher-rank Schreier and commutator constructions were also
verified and screened; the current saved U124 screens reach rank22, without
an additional winning endpoint attributable to those larger detours.

## Central consequences without replacing the donor

Let `h,z` be generators, let `d,k,a` be integers, and put

    w = h^d z^a,       D = z^-1 w^k.

The following identity holds in the free group:

    z^-1 h^d z h^-d = D w D^-1 w^-1.

It therefore supplies an explicit two-factor retained-donor correction for
commuting central powers through `z`. The donor `D` stays in the tuple.
The current central-pinch compiler gives positive controlled examples but
no additional U124 gain in its33-row applicable panel. A power consequence
alone must not silently replace `D`: implication is weaker than an AC-equivalent
replacement. The complete algebra and signed controls are in `theory_relators.md`
and `verification_central.json`.

## Endpoint rank and intermediate rank

If a normalized balanced unimodular tuple of rank `r` admits no nonincreasing
one-occurrence substitution/removal, its total length satisfies `L >= 4r`.
The proof combines the occurrence bound with independence of short exponent
rows modulo two; see [RANK_LENGTH_BOUND.md](RANK_LENGTH_BOUND.md). At rank
three a separate finite case proof improves this to `L >= 13`.
Both proofs were independently audited in `VERIFY_LOW_LENGTH.md`.

This explains why raising rank does not automatically keep decreasing the
final total. A fully simplified rank-six endpoint costs at least24 letters;
a rank-eleven endpoint costs at least44. Our incumbents have length at most21,
so a strictly better endpoint can be reduced to rank at most five. The theorem
places **no bound on the intermediate rank of a successful path**. Higher
ranks remain allowed as temporary workspaces.

## Restricted negative results

The fixed-root corridor computation completes all33 recognized BS cases and
finds no descent. The stronger fixed-donor argument in `VERIFY_FIXED_DONOR.md`
shows why those companion words are already geodesic while the two donors
and root metric stay fixed. It says nothing against changing donors, changing
the metric, or arbitrary AC/stable AC moves.

Schreier dictionaries, multiple root denominations, stable-letter helpers,
conjugate bridges, donor commutators and critical-overlap completion all have
explicit positive controls. Their particular saved screens have not added
coverage beyond imported incumbents unless the experiment index says so.
These finite failures are preserved as data, not promoted to general obstructions.

## Reproduction

From this worktree, using the parent checkout's Python environment:

```sh
/Users/avigyapaudel/Documents/surf/ACSolverX/.venv/bin/python -B research/u124_rank_3h_20260912/refresh_results.py
```

This replays saved records, verifies imported seed hashes, and regenerates the
current table and incremental experiment index without presentation search.
`frontier.py` is the shared bounded runner for separately named probe modules;
its arguments record exact input IDs, imported seed files, budget and module.
The exporter and its independent replay checks are documented in
`VERIFY_FULL_EXPORT.md`. Existing frozen census files remain unchanged.
