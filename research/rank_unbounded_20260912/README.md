# Arbitrary-rank stable AC research — 2026-09-12

The new mixed screen improves eleven U124 rows by one letter each, taking the
previous sum of best lengths from **2191 to 2180**. Four further rows retain
their previous length with rank3 instead of rank4. All **124 remain unsolved**;
no new rank2 length reduction was found. There are now89 rows shorter than
their saved rank2 starts, whose aggregate length is2356. These are bounded
experimental minima, not global minima.

The implementation has **no fixed rank limit**. The final mixed and ladder
screens have **no length ceiling** either. Each screen uses at most1000
declared work units per presentation. A unit is a definition evaluation,
minimum cut, attempted removal, or AC product as specified below; it is not
one S20 heap pop and is not an equal-compute comparison with S20.

## What happened on U124

| New length gain | Previous best | New best | Retained endpoint rank |
|---|---:|---:|---:|
| aca_7 |16|15|3|
| aca_30 |17|16|3|
| aca_31 |17|16|3|
| aca_36 |16|15|3|
| aca_57 |18|17|3|
| aca_80 |18|17|3|
| aca_82 |20|19|3|
| aca_86 |20|19|3|
| aca_102 |21|20|3|
| aca_103 |21|20|3|
| aca_104 |21|20|3|

`aca_108`, `aca_112`, `aca_113`, and `aca_114` additionally reach their previous
best lengths21,21,20,20 at rank3 instead of rank4. The final retained ranks
are35 rank2,87 rank3, and2 rank4. A higher-rank intermediate can therefore be
useful even when the best endpoint is again rank3.

The complete [124-row table](ALL124.md), [CSV](all124.csv), and [JSON](all124.json)
include archival length, saved rank2 length, previous any-rank length, new
length, rank, and exact witness pointers. The
[15 new witnesses](shortening_witnesses.jsonl) cover the eleven length gains
and four same-length rank reductions.

### A real two-definition example: aca_80

Starting from its saved rank2 presentation, the following complete tuples are
recorded. Uppercase letters mean inverses.

| Operation | Rank | Total length | Tuple |
|---|---:|---:|---|
| Canonical saved rank2 input |2|19|`(YYYXyXYYYxyXX, YYXXyx)`|
| Define `z=YX`, replace three occurrences |3|19|`(ZYX, ZXXYYzyXYYY, ZyXYx)`|
| Define `u=XY`, replace three occurrences |4|19|`(UYZyUxzyy, UYzX, UXY, ZYX)`|
| Apply `x->xY, y->y, z->yzY, u->u` |4|17|`(UZUxzy, UyXY, UzX, ZYXy)`|
| Lemma11: eliminate `z` using `UzX`, so `z=ux` |3|17|`(UUxuxyUX, UYXyX, UyXY)`|

The previous incumbent had length18 at rank3. The two neutral definitions
reach a rank4 frame from which a basis change saves two letters. A subsequent
removal keeps that length with one fewer generator. This path is one reason
to retain neutral definitions and permit rank to both rise and fall.

### Actual high-rank trials

A separate ladder arm deliberately follows further definitions even when they
increase total length. It reached rank15 on118 rows and rank16 on6 rows.
That particular arm found no gain beyond the already known new `aca_36`
improvement. Representative recorded lengths were:

| Row | Rank4 | Rank6 | Rank10 | Rank11 | Rank15 | Rank16 |
|---|---:|---:|---:|---:|---:|---:|
| aca_36 |16|19|27|29|38|—|
| aca_80 |19|22|29|31|40|—|
| aca_108 |21|24|31|33|41|44|

These numbers describe this ladder's visited states, not a minimum achievable
at each rank. Other branches already give a better rank4 state for `aca_80`.
The entire path to rank16 for `aca_108`, including all16 relators of total
length44, is preserved in [observed_rank16.json](observed_rank16.json) and
independently replayed. There was no rank10/11 rejection.

## Theory

Let `m` be the length of a new defining word, and `T` its selected disjoint
occurrences in existing relators. Adding `z^-1 w` costs `m+1` letters;
each replacement saves `m-1`. The exact literal gain is

    gain = T*(m-1) - (m+1).

For example, a two-letter definition used three times is neutral, as in the
`aca_80` path. It can still expose a useful subsequent basis change.

There is no universal rank at which strict compression must stop across all
inputs. For any positive integer `k`, the trivial presentation

    ((xy)^(4^k) x, xy)

has a strict compression chain using `h1=(xy)^2` and `hj=h(j-1)^4` for
`j=2,...,k`. It ends at rank `k+2`, total length `5k+5`; every stage saves
length, with the last saving exactly one. With `k=3`, the same fixed input
has the chain `(rank,length)=(2,131)->(3,40)->(4,21)->(5,20)`.
This is a proved easy family, not a claim of a U124 solve.

For a fixed balanced trivial input of rank `r` and length `L`, each strict
rank-increasing compression decreases the nonnegative quantity `L-r` by at
least two. Without intervening length increases, there can be at most
`floor((L-r)/2)` such additions. A stronger bound applies at singleton-free
endpoints. Allowing longer intermediates removes that particular descent
bound but gives no guarantee of an eventual improvement.

[THEOREM_NOTE.md](THEOREM_NOTE.md) proves these statements, a limited
two-step bypass result for pure literal compression, and a batch-removal
criterion using acyclic generator dependencies. Its bypass result does not
apply when basis changes or AC operations intervene.

The rank-changing legality is
[Lemma11 of Shehper et al.](https://arxiv.org/abs/2408.15332), exactly the
Substitution and Removal lemma supplied by the user. A relator containing a
generator once can be oriented to `a^-1 e`; substitute `e` into every other
relator, then remove the defining row and `a`. [LEMMA11_RESEARCH.md](LEMMA11_RESEARCH.md)
gives the signed formulas and counts all surviving relators when evaluating
the resulting length. Known triviality is required; an exponent sum of one
or a unimodular matrix alone is not a primitive-word certificate.

Whole-tuple and selected-subtuple changes use the Whitehead graph minimum-cut
length formula. This is established machinery, not a new theorem of this
experiment: [Roig–Ventura–Weil, Section3.3 and Corollary3.12](https://arxiv.org/pdf/math/0608779).
The new experiment combines it with repeated definitions, ordinary AC
substitutions, and Lemma11 at arbitrary rank.

## Algorithm and measured work

`search.py` represents signed generators by nonzero integers, including IDs
above26. It enumerates cyclic substrings up to their current relator's length,
uses dynamic programming to replace disjoint occurrences of a word and its
inverse, and retains the complete new defining relator.

`mixed_search.py` starts from both the saved rank2 state and the saved any-rank
incumbent. It explores shorter complete tuples first, trying cancellation-based
ordinary AC products, Lemma11 removals (including basis changes focused on
individual relators), and promising new definitions followed by whole-tuple
Whitehead descent. Failed tests share the same1000-unit row budget. It screens
a bounded number of definitions per expanded state; it is an incomplete search
despite having no rank or length cap.

`mode=ladder` follows a promising definition at each round even when longer,
using smaller AC/removal allocations to explore substantially higher ranks.
`partial_basis.py` instead minimizes a chosen relator subtuple while applying
the resulting automorphism to the whole presentation, then removes exposed
generators. That can succeed in planted examples even when the required map
increases the whole tuple's length. On the selected17-row follow-up panel it
found no further improvement. This panel is exploratory, not a holdout.

| Screen | Rows | New length gains vs2191 baseline | Work units | CPU seconds | Search wall seconds |
|---|---:|---:|---:|---:|---:|
| Literal definitions, temporary +2 ceiling |124|0|29,462|2.518|2.528|
| Definitions and whole-tuple cuts, bounded ceiling |124|5|86,271|2.478|2.504|
| Mixed AC, definitions, cuts, Lemma11; no ceilings |124|11|124,000|2.346|2.364|
| Higher-rank ladder; no ceilings |124|1, already among11|124,000|3.692|3.703|
| Partial-basis follow-up |17|0 further|5,380|0.198|0.199|

All runs were serial pure Python, with50ms cooldown per newly run row. Pilot
results were reused in full screens. The four124-row discovery screens cost
about11 CPU seconds altogether; the17-row follow-up adds0.198 seconds. Timings
exclude cooldown, JSON output, and independent audit. They do not measure
elementary stable-certificate expansion time.

An additional observer validation replayed124,000 mixed units and1,000 ladder
units, costing approximately2.624 CPU seconds. It reproduced the original
search decisions and inspected generated intermediate macro boundaries,
including partial basis exposure that might be followed by a longer removal.
No additional length minima or rank2 gains appeared. It did expose the
same-length lower-rank witnesses retained in the final table. This replay is
additional physical work and is not counted as free reuse.

## Verification and reuse

[AUDIT.md](AUDIT.md) and [audit.json](audit.json) record independent word-level
replay, full-tuple length accounting, two-sided basis inverses, signed removals,
high-rank controls, and250 observer chains. The audit also compares minimum
cuts against exhaustive tiny partitions and checks the cut length formula
against exact transformed words. The first basis screen's executed Whitehead
source is preserved as `whitehead_first_screen.py`; its corrected completion
flag changes reporting only, not search outcomes or cost.

The saved paths are **theorem-backed stable composites**. Lemma11 supplies
finite elementary stable-AC realizability on these known trivial presentations;
its potentially long normal-product witnesses have not been emitted. Do not
label these files fully expanded elementary paths or the time in the table an
elementary-certificate conversion time.

Run scripts from this directory or use their paths from the worktree. These
commands reproduce only small validation, without a presentation campaign:

```sh
/Users/avigyapaudel/Documents/surf/ACSolverX/.venv/bin/python -B lemma11_checks.py
/Users/avigyapaudel/Documents/surf/ACSolverX/.venv/bin/python -B audit.py
```

`mixed_search.py --output <new-file.json>` runs the1000-unit mixed screen;
add `--mode ladder` for the rank ladder or `--ids aca_80` for a single row.
Existing output paths are refused. The17-row selection and full input/source
hashes are pinned in the result records. `summarize.py` regenerates only the
new tables and15-witness JSONL; it does not alter the earlier research package.

All work remains local on `codex/theory-patterns-3h`, uncommitted and unpushed.
