# The backward ball B(cap): an exact offline endgame table for the AC search

*Companion module:* `backward_table.py` (builder, loader, CLI) ·
`plain_search_ball.py`, `mid_search_ball.py`, `final_policy_ball.py` (the
ball-aware copies of the frozen cascade) · `tests/test_ball_policy.py` ·
tables under `tables/`.

The frozen census cascade never sees the trivial pair until it pops it. This
note describes a precomputed endgame table that lets it stop as soon as it
*generates* any state from which the trivial pair is reachable inside a length
cap, what makes that table exact, why adding it can only make the cascade
cheaper, and what it costs.

---

## 1. Definition

Write `s -> t` for "the production expansion kernel
(`experiments/heuristic_search/core/hexpand.expand_children_h`, the kernel
`plain_search_fast` and `mid_search` pop with) emits `t` as a child of `s`".
Every such child is a relator substitution

```
r_i  <-  rot_{k1}(r_i) . rot_{k2}(r_j^{jsign})        (target, jsign, k1, k2)
```

freely and cyclically reduced and canonicalised, and the kernel only emits the
products whose seam cancels.

**B(cap)** is the set of canonical pairs `s` for which there is a path

```
s = s_0 -> s_1 -> ... -> s_d = (Y, X)          with max(|r1|, |r2|) <= cap at every s_i
```

(`canon_pair('x','y') == ('Y','X')`, and it is the only canonical pair the
frozen terminal test accepts.) The table stores

```
key(s)  ->  (depth d, key(s_1), move (target, jsign, k1, k2))
```

with the trivial pair at depth 0 and `(None, None)`. Keys are
`heuristic_1k.pack` bytes -- the same bytes the searches already use as
dictionary keys -- so membership is one hash lookup and, on a hit, the rest of
the certificate is read straight out of the table by following successors.

An **automorphism-closed** table (`aut_edges=True`) uses the same definition
with one extra edge type: the four ambient Nielsen maps of
`heuristic_1k.NIELSEN` (`x->xy`, `x->xY`, `y->yx`, `y->yX`), the same edges the
`aut_edges` arm of `mid_search` generates. Those entries store `dict(t)` as
the move and emit `{'kind': 'automorphism', 'images': t}` as the certificate
step, which the mixed-certificate decoder already handles.

## 2. How it is built, and why backwards

The trivial pair has **no forward children**: every emitted child needs a
cancelling seam, and no product of rotations of `x` and `y^{\pm1}` cancels. So
the ball cannot be grown forwards from `(Y, X)`, and the BFS runs backwards.

Predecessors are enumerated with the **full** product set -- both targets, both
signs, every rotation `k1` of the target relator and every rotation `k2` of the
signed partner, **with no seam condition** -- because the inverse of an engine
move is again a product of that shape but not one the kernel would emit from
this end. Each candidate is canonicalised (`canonical_pair_nj`'s rule,
computed on the packed 2-bit words `hexpand` uses) and dropped unless both
relators are nonempty and no longer than `cap`.

Every surviving candidate is then **forward-verified**: the kernel is run on
the candidate exactly as a search would run it (`cap=None` semantics, i.e.
expansion cap = the candidate's total length -- which never filters anything,
since a cancelling seam makes the new relator at least two symbols shorter than
the pair's total length), and the candidate is admitted only if the successor
is literally among the children the kernel emits. The kernel's own move is
what gets stored.

The candidate enumeration, the free/cyclic reduction and the canonical form are
`@njit` (`_candidates`), as is the verification (`_forward_move`); dedup and the
BFS bookkeeping are Python. The frontier is processed in sorted key order and
each state's candidates in `(target, jsign, k1, k2)` order, so the table is a
pure function of `cap`, `aut_edges` and the kernel sources -- rebuilding
reproduces the pickle byte for byte.

## 3. Exactness

Three separate claims, checked three separate ways.

**(a) Every stored edge is a real engine move.** It was forward-verified with
the kernel at build time, and `check_replay` re-derives *every* entry a second
time with the pure-Python `words.replay_move` (`words.apply_pair` for an
automorphism entry) -- a different implementation on a different data type --
requiring `replay(unpack(key), move) == unpack(successor)` exactly, and the
successor's depth to be one less. All six shipped tables are replay-checked in
full at build time and the result is recorded in the manifest
(`checks.replay_all_entries`); `tests/test_ball_policy.py` re-runs it. Every
solve produced through a ball hit is then checked a *third* time end to end by
the harness, which decodes the mixed certificate with `decode_elementary` and
independently replays it with `replay_elementary`.

**(b) The ball as a set is exact.** `bruteforce_ball(cap)` computes the true
backward ball the honest way: enumerate *every* canonical pair with both
relators of length `<= cap`, expand each with the kernel, reverse all the edges
and BFS from the trivial pair. No predecessor enumeration is involved. It
agrees with `build(cap)` key for key:

| cap | canonical relators | canonical pairs in the universe | brute-force ball | `build(cap)` | equal |
|---|---|---|---|---|---|
| 6 | 117 | 6,903 | 317 | 317 | yes |
| 7 | 275 | 37,950 | 2,333 | 2,333 | yes |
| 8 | 693 | 240,471 | 6,069 | 6,069 | yes |

The universe grows about 6x per +1 cap, so this ground truth stops being
affordable above cap 8; the cap-6 case runs in the test suite. Since the ball
*set* is what decides whether a search hits, this is the claim the policies
rest on. (The forward verification does bite: at cap 8, 16 of the 6,084
proposed neighbours are not children the kernel emits and are rejected. They
happen to be states the BFS reaches by another route, which is why the set is
the same either way -- but without the check there is no verified move and
hence no replayable tail.)

**(c) `depth` is an upper bound, not a geodesic.** The predecessor enumeration
finds every state but not every edge: an edge whose product is a rotation of a
*conjugate* of the successor's relator (the case the kernel's cut-shift skip
describes) is not of the enumerated shape, so a state can enter the BFS one or
two layers after its true backward distance. Brute force puts the true
eccentricity at 6 / 9 / 14 for caps 6 / 7 / 8 where the builder reports
7 / 10 / 15. Nothing depends on the number being minimal: the stored tail is a
valid path of exactly that length, and `ball_depth` is reported, never charged.
It is an upper bound and is documented as one.

**Cross-check against the prototype.** With `verify=True` and `aut_edges=False`
the builder reproduces the discovery prototype's cap-8 pickle exactly -- same
6,069 keys, same depths, same per-layer counts
(4, 8, 40, 572, 1188, 1484, 1104, 656, 404, 272, 80, 144, 56, 40, 16) -- and
the same cap-10 size (101,885) and closing layer (33). The stored successor and
move can differ, because the prototype iterates a Python `set` of candidates
(hash-order dependent) while this builder iterates them in kernel order; both
are valid kernel edges and both replay.

## 4. Sizes, depths and build times

One thread (`NUMBA_NUM_THREADS=OMP_NUM_THREADS=OPENBLAS_NUM_THREADS=1`), the
numba kernels warmed before timing, on a 4-core box that was also running other
screens -- read the wall seconds as indicative.

| table | cap | aut-closed | states | of which automorphism edges | max depth | candidates enumerated | kernel verifications | build wall | pickle |
|---|---|---|---|---|---|---|---|---|---|
| `ball_cap08.pkl` | 8 | no | 6,069 | -- | 15 | 112,540 | 6,084 | 0.4 s | 230 KB |
| `ball_cap10.pkl` | 10 | no | 101,885 | -- | 32 | 2,116,724 | 102,033 | 9.7 s | 4.2 MB |
| `ball_cap12.pkl` | 12 | no | 1,165,797 | -- | 56 | 27,326,164 | 1,167,275 | 151.5 s | 51 MB |
| `ball_cap08_aut.pkl` | 8 | yes | 7,613 | 1,741 | 16 | 169,932 | 5,903 | 2.3 s | 290 KB |
| `ball_cap10_aut.pkl` | 10 | yes | 127,873 | 30,857 | 34 | 3,100,892 | 97,213 | 44.8 s | 5.2 MB |
| `ball_cap12_aut.pkl` | 12 | yes | 1,488,649 | 356,571 | 47 | 39,859,796 | 1,133,393 | 625.0 s | 66 MB |

Growth is about **17x per +2 cap** from 8 to 10 and about **11x** from 10 to 12
(16.8x and 11.4x plain; 16.8x and 11.6x automorphism-closed). Cap 14 would be
somewhere around 10-15 million states and a gigabyte of pickle; the cap is the
knob, and it is the only knob.

For comparison, the pure-Python prototype built cap 8 in 19.3 s and cap 10 in
about 11 minutes; the numba builder is ~45x and ~65x faster, which is what makes
cap 12 (and the automorphism closure on top of it) reachable at all.

## 5. Manifest, loader, CLI

`save(table, path, ...)` writes the pickle atomically (temp file + `os.replace`)
and a sibling `<stem>.manifest.json` carrying: `cap`, `aut_edges`, `size`,
`automorphism_entries`, the full `depth_histogram`, `max_depth`,
`build_wall_seconds`, `candidates_enumerated`, `forward_verifications`, the
per-layer `levels`, the **sha256 of the pickle bytes**, the git HEAD, and the
sha256 of every source the contents depend on -- `hexpand.py`, `hfast.py`,
`greedy_baseline.py`, `words.py`, `heuristic_1k.py` and `backward_table.py`
itself -- plus the `checks` that were run.

`load(path)` recomputes the sha256 and refuses the table if it does not match
the manifest.

**Determinism is checked, not asserted.** All six tables were rebuilt from
scratch after every source edit and every pickle came out **byte-identical** to
the first build (same sha256), which is what makes the manifest's source hashes
meaningful: the same sources at the same cap give the same table.

```
PYTHONPATH=. python3 -m research.residual_20260909.backward_table \
    --cap 10 [--aut-edges] --out research/residual_20260909/tables/ball_cap10.pkl
```

The CLI replay-checks every entry before saving and fails loudly if any entry
does not replay.

## 6. The ball terminal in the cascade, and how it is charged

`plain_search_ball.py`, `mid_search_ball.py` and `final_policy_ball.py` are
copies of `plain_search_fast.py`, `mid_search.py` and
`final_policy.py` + `root_router.py`. The frozen modules are untouched and
remain the comparison implementation. The table is installed with
`set_table(table)` or passed as `table=`.

A lookup happens at **every** place a state is created:

| where | module |
|---|---|
| the canonical root of the policy | `final_policy_ball.search` |
| every donor-transport state (after each accepted basis map) | `final_policy_ball.search` |
| every substitution child | `plain_search_ball`, `mid_search_ball` |
| every `aut_edges` automorphism child | `plain_search_ball`, `mid_search_ball` |
| every commutator / full-splice child | `mid_search_ball` |
| every macro-admitted partial state (`admit_partial`) | `mid_search_ball` |
| everything inside the bounded BS-escape continuation | `mid_search_ball` (the recursive call inherits the table) |

The pre-existing terminal test -- pop a state, see `('Y','X')`, stop -- is left
exactly as it was.

**Accounting.** `nodes_explored` keeps its frozen meaning to the unit: pops,
plus the same macro charges (`collapse_bs` rewrites, two-block moves,
`primitive_complete` work, escape-continuation nodes, donor image evaluations
and accepted maps). **A ball lookup is never charged.** It is counted instead
in three new reported keys:

* `ball_lookups` -- how many membership tests were made,
* `ball_hit` -- whether one hit,
* `ball_depth` -- the stored depth of the state that hit (0 when none did),
* `ball_stage` -- which stage the hit happened in (`root`, `donor_transport`,
  `donor_terminal`, `plain`, `incumbent`), for per-row diagnosis.

That is the honest convention: the lookup is a hash probe against a table that
was computed offline, and pricing it as a search node would misstate both
directions (it is far cheaper than a pop, and its real cost was paid once, in
section 4, not per row).

## 7. Why the ball cascade dominates the frozen cascade

**Claim.** With `force_arm=None`, `certified_overrun=False`,
`use_stable_power=False` and `use_bs_demote=False` -- the settings the
`frozen_ball08/10/12`, `frozen_ball10aut/12aut` and `K1` policies use -- for
every row the frozen cascade solves at N units, the ball cascade solves it at
<= N units, and it never loses a row.

**Proof sketch, in lockstep.** Run the two cascades side by side on the same
row with the same budget.

1. *Nothing but the lookups is different.* The stage order, the stage caps, the
   donor gates, the heap orderings, the `parent` de-duplication, the expansion
   caps and every `nodes` charge are the frozen code verbatim -- the diff
   against `plain_search_fast.py` and `mid_search.py` is exactly the lookup
   sites, the counters, and the tail splice. A lookup charges nothing, pushes
   nothing, pops nothing and reorders nothing. So the two runs agree
   instruction for instruction until the first hit.
2. *A hit ends the run immediately, with the counter where it is.* Both
   `nodes` (inside a search) and `charged` (in the cascade) are nondecreasing
   along an execution, and the frozen run can only return at the same point or
   later. So the ball run's total is `<=` the frozen run's.
3. *The frozen terminal is a special case of a hit.* `('Y','X')` is in the
   table at depth 0, and it is the only canonical pair the frozen terminal test
   accepts. The frozen code recognises it when it is **popped**; the ball code
   recognises it when it is **generated**, which is strictly earlier in the
   same execution. So every frozen solve has a matching ball hit no later.
4. *Finishing earlier never starves a later stage.* The later stages' budgets
   are `limit - charged`, `min(plain_prefix, budget - charged)` and
   `budget - charged - plain_charges`; all are monotone decreasing in the
   earlier stages' charges, which the ball can only lower.
5. *A hit is a genuine solve.* Section 3(a).

This is checked, not just argued: `tests/test_ball_policy.py` runs the frozen
and cap-8 ball cascades on the 12-row smoke panel and asserts
`nodes_ball <= nodes_frozen` on every row plus a full decode-and-replay of every
ball certificate; and with `table={}` (every lookup made, none able to hit) the
ball cascade reproduces the frozen cascade *bit for bit* -- same solved flags,
same `nodes_explored`, same routes, same `states` and `steps`.

The measured regression check is the same statement on 60 rows: see section 8.

**What is NOT covered by the claim.** Four options deliberately step outside it,
and none of them is on in a `frozen_ball*` name:

* `certified_overrun=True` -- when `DONOR_NORMALIZED_BS.inspect` reports
  `bs_preflight` status `accept` at a donor endpoint, `consecutive_bs.collapse`
  is a compiler that is guaranteed to reach a solve; only its rewrite count is
  unknown in advance, and that count is charged against the 250-unit stage-1
  cap. `ac19_109` (`('YXXyx','YYYYYYYYXyyyyyyyx')`) is the worked example:
  preflight accepts with 7 pinches and base exponent 127, the collapse needs
  **256** rewrites, stage 1 had 246 units left, so the frozen cascade drops a
  certificate it had already proved and then spends its 750 plain units failing.
  With the option on, the collapse runs on the endpoint state with
  `budget=min(10000, budget-charged)` -- the remaining **row** allowance rather
  than the remaining **stage** allowance -- before the stage-1 terminal
  subsearch, and its `rewrites` are charged in full whether it succeeds or
  fails. Measured: `ac19_109` is solved at **260 units**, `policy_route`
  `strict_donor`, `winner` `certified_overrun`, certificate decoded (19,605
  elementary moves) and independently replayed. A *failed* overrun would burn
  units the frozen cascade does not, so the dominance guarantee does not extend
  to it.
* `use_stable_power=True` -- passes `use_stable_power=True` into every
  `mid_search_ball.mixed_search` of the cascade. **Withdrawn from the candidate
  set:** on regression60 it lost `ac19_28267`, which `frozen` and `K1` both
  solve at exactly 973 units, because the gate's charged failed attempts pushed
  the row past 1,000. The option remains available; no shipped candidate uses
  it.
* `use_bs_demote=True` -- the `bs_demote_gate` root macro as stage 0.
  `recognize`/`demotable` are pure recognition and charge nothing, so a row the
  gate does not fire on costs exactly zero; `complete` is entered only on a
  demotable label, predicts its whole cost before the first move and refuses
  inside 2 units when that cost does not fit. It fires only on stalled
  consecutive-BS roots, which the frozen cascade never closes at the root, but a
  refusal would still cost up to 2 units, so it is kept out of the
  dominance-carrying names. It is a no-op on dev and regression60 (no row is
  demotable) and is on in `K2'`..`K5'`.
* `force_arm='s20' | 'aut_edges'` -- overrides `root_router`'s routing feature
  for stage 3. This reorders the search, so nothing is guaranteed.

## 8. Measurements

Serial, one thread, harness warmup on, budget 1,000 units per row, every solve
decoded with `decode_elementary` and independently replayed with
`replay_elementary` (`verified` below counts rows that passed that replay).
Tags are under `screens/`.

### regression60 -- the hard constraint

The panel carries the census's own per-row `nodes_explored`; the requirement is
60/60 solved and verified with **no row above its census cost**.

| tag | solved | verified | total units | census units | rows strictly cheaper | rows over census | wall |
|---|---|---|---|---|---|---|---|
| `reg60_frozen_ball08_1000` | 60 | 60 | 56,480 | 57,166 | 37 | **0** | 17.7 s |
| `reg60_frozen_ball10_1000` | 60 | 60 | 54,044 | 57,166 | 47 | **0** | 16.4 s |
| `reg60_frozen_ball12_1000` | 60 | 60 | 26,607 | 57,166 | 55 | **0** | 9.8 s |
| `reg60_frozen_ball10aut_1000` | 60 | 60 | 22,176 | 57,166 | 56 | **0** | 7.1 s |
| `reg60_frozen_ball12aut_1000` | 60 | 60 | 6,733 | 57,166 | 58 | **0** | 2.4 s |

### dev (102 rows) -- what the table buys

`frozen` itself solves **0/102** here; that is what the residual panel is.

| tag | solved | verified | total units | wall |
|---|---|---|---|---|
| `dev_frozen_1000` (reference) | 0 | 0 | 102,000 | 34.7 s |
| `dev_frozen_ball08_1000` | 6 | 6 | 101,716 | 35.9 s |
| `dev_frozen_ball10_1000` | 24 | 24 | 100,071 | 38.5 s |
| `dev_frozen_ball12_1000` | 71 | 71 | 71,085 | 27.3 s |
| `dev_frozen_ball10aut_1000` | 78 | 78 | 34,872 | 14.6 s |
| `dev_frozen_ball12aut_1000` | 91 | 91 | 15,221 | 7.2 s |
| `dev_aut_edges_ball10_1000` | 86 | 86 | 34,441 | 29.0 s |

Two things to read off. First, the **automorphism closure matters more than
the cap**: the cap-10 automorphism-closed table (127,873 states) beats the
cap-12 substitution-only table (1,165,797 states) 78 to 71 while being an order
of magnitude smaller. Second, `aut_edges_ball10` -- the generator-move arm run
alone with the plain cap-10 table -- reaches 86/102, so most of the value is in
letting the *search* take automorphism edges, and the automorphism-closed table
is the cheap way to get the same reach out of the frozen allocation.

### The pre-registered candidate cascades (NOTES.md section "Pre-registered candidate cascades")

`K0` is `frozen`. `K1` is the pure ball cascade: the frozen allocation
(donor 250 / plain 872 / routed rest) plus the ball terminal and nothing else,
so it is the one candidate the section-7 dominance guarantee covers.
`K2'`..`K5'` add the certified consecutive-BS overrun and the free BS-DEMOTE
root macro and reallocate the stages; the stable-power gate that the original
K2..K5 carried has been **withdrawn** (it lost `ac19_28267` on regression60).

| id | stage 0 | stage 1 (strict donor) | stage 2 (plain S20) | stage 3 (incumbent) |
|---|---|---|---|---|
| K1 | -- | 250 + ball | 872 + ball | rest, routed + ball |
| K2' | BS-DEMOTE | 250 + ball + overrun | 872 + ball | rest, routed + ball |
| K3' | BS-DEMOTE | 250 + ball + overrun | 300 + ball | rest, routed + ball |
| K4' | BS-DEMOTE | 250 + ball + overrun | none | rest, routed + ball |
| K5' | BS-DEMOTE | 250 + ball + overrun | none | rest, forced generator arm + ball |

Each was run once on dev and once on regression60 at 1,000 units, on both
automorphism-closed tables. `over census` counts regression60 rows charged more
than the published census spent on them; it must be zero.

| candidate | table | dev solved | dev verified | dev units | dev wall | reg60 solved | reg60 verified | reg60 units | over census | reg60 wall |
|---|---|---|---|---|---|---|---|---|---|---|
| K1 | cap-10 aut | 78/102 | 78 | 34,872 | 14.7 s | 60/60 | 60 | 22,176 | 0 | 6.5 s |
| K2' | cap-10 aut | 79/102 | 79 | 34,132 | 13.7 s | 60/60 | 60 | 22,176 | 0 | 7.4 s |
| K3' | cap-10 aut | 92/102 | 92 | 26,375 | 15.9 s | 60/60 | 60 | 9,490 | 0 | 3.0 s |
| K4' | cap-10 aut | 92/102 | 92 | 20,019 | 17.5 s | 60/60 | 60 | 1,970 | 0 | 0.5 s |
| K5' | cap-10 aut | 92/102 | 92 | 19,850 | 16.5 s | 60/60 | 60 | 1,970 | 0 | 0.6 s |
| K1 | cap-12 aut | 91/102 | 91 | 15,221 | 6.2 s | 60/60 | 60 | 6,733 | 0 | 2.6 s |
| K2' | cap-12 aut | 92/102 | 92 | 14,481 | 6.3 s | 60/60 | 60 | 6,733 | 0 | 2.2 s |
| **K3'** | **cap-12 aut** | **94/102** | **94** | **11,771** | **8.5 s** | **60/60** | **60** | **3,065** | **0** | **1.0 s** |
| K4' | cap-12 aut | 92/102 | 92 | 13,031 | 13.2 s | 60/60 | 60 | 740 | 0 | 0.2 s |
| K5' | cap-12 aut | 92/102 | 92 | 13,028 | 13.2 s | 60/60 | 60 | 740 | 0 | 0.2 s |

Best on dev is **K3' on the cap-12 automorphism-closed table, 94/102**, all 94
decoded and independently replayed, 60/60 on regression60 with no row over its
census cost. The eight dev rows it does not close are

```
ac19_11753  ac19_18413  ac19_38222  ac19_45684
ac19_49255  ac19_54337  ac19_60781  ac19_62145
```

(the six in **every** candidate's unsolved list, on both tables, are
`ac19_38222`, `ac19_45684`, `ac19_49255`, `ac19_54337`, `ac19_60781`,
`ac19_62145` -- the residual core.) None of this is a selection: val.csv and
test.csv were not opened, and the selection rule in NOTES.md still runs on
val.csv.

Where the hits happen, from the per-row `ball_stage` field (K3' / cap-12 aut,
dev): 66 at the canonical **root** -- the row is already inside the ball before
a single unit is charged -- 1 during donor transport, 20 in the plain S20
stage, 4 in the incumbent restart. That distribution is the whole story of the
table: at cap 12 with the automorphism closure, two thirds of the residual dev
panel is endgame.

The BS-DEMOTE stage-0 macro is a measured **no-op on both panels**: zero rows
recognised, zero demotable, zero units charged on all 102 dev and all 60
regression60 rows. It is carried for the residual rows outside these panels
that it certifies; it costs those panels nothing, exactly as its contract says.


## 10. Compact mode: the cap-14 table

At cap 12 the automorphism-closed ball is 1.49M states and a 69 MB pickle that
inflates to roughly 600 MB of Python objects once loaded. At cap 14 it is an
order of magnitude larger again, and the dict-of-`bytes` representation would
need several gigabytes **per worker**. Compact mode stores the same ball in
four numpy columns and never creates a Python object per state.

### The packing

A canonical pair is `(r1, r2)` with `la = len(r1)`, `lb = len(r2)`, both in
`1..15`, and at cap <= 14 also `la + lb <= 28`. Each symbol is one of the four
engine codes `X=1, Y=2, x=3, y=4`, so `code - 1` is exactly two bits. One
uint64 holds the pair:

```
bits 63..60   la                       (4 bits, 1..15)
bits 59..56   lb                       (4 bits, 1..15)
bits 55..0    2 bits per symbol, code-1, little-endian:
              symbol t of r1 at bits 2t, symbol t of r2 at bits 2*(la+t)
```

`2*(la+lb) <= 56` payload bits, so nothing collides with the two length
nibbles. It is a **bijection** on canonical pairs with relators of length
1..15: the lengths are stored outside the payload and every symbol has its own
field, so `_unpack_u64` inverts it and returns the identical
`heuristic_1k.pack` bytes the dict tables use (`test_compact_packing_is_a_bijection`
round-trips a real ball and checks that an over-long pair packs to the reserved
value `0`). `0` is never a valid word (`la >= 1` forces a nonzero high nibble),
which is what lets it double as the empty slot of the build's hash set.

The move is one int32:

```
-1                  no move (the trivial pair)
-2                  substitution, not yet verified (build-time only)
byte0 = 1 or 2      substitution: target; byte1 = 1 for jsign +1, 2 for -1;
                    byte2 = k1; byte3 = k2
byte0 = 0           RESERVED for the four Nielsen automorphism steps;
                    byte1 is the index into heuristic_1k.NIELSEN
```

Every field is at most 14 at cap 14, so the value stays far below 2**31.

### The build

Same ball, same enumeration, same forward verification -- only the bookkeeping
changes. Candidate generation, the Nielsen images, the free/cyclic reduction,
the canonical form and the packing are all `@njit` and write packed uint64s
straight into a preallocated buffer. Per level the frontier is walked in
**chunks** sized so the candidate buffer can never overflow (`_level_chunk`
returns how many states it consumed), which is what bounds peak memory no
matter how wide a level gets. Per chunk: `_hs_missing` against a numba
open-addressing hash set drops what is already known, `np.unique(..., return_index=True)`
dedups keeping the first proposal, and `_verify_many` runs the production
kernel on every remaining candidate in **one** numba call instead of one call
per candidate. A candidate whose first proposal fails verification is retried
against its other proposals at the same level, exactly as the dict builder
does, so the ball and the depths come out identical.

Checked, not asserted: at caps 8 and 10 (plain and automorphism-closed) and at
cap 12 automorphism-closed, `build_compact` is **key-for-key and depth-for-depth
identical** to `build`. The stored *successor* agrees on 73% of the cap-12
entries and differs on the rest, because the frontier is ordered by packed key
here and by raw byte key there; both are kernel edges, both replay, and both
give the same certificate length distribution.

### `CompactTable`

`CompactTable` satisfies the same mapping protocol the cascade already uses --
`key in table`, `table[key]`, `table.get(key)`, `len(table)`, with `key` the
same `pack` bytes and `table[key] == (depth, successor_key_bytes, move)` -- so
`plain_search_ball`, `mid_search_ball` and `final_policy_ball` are unchanged.
`backward_table.tail` dispatches to `CompactTable.tail`, an index-walking fast
path that never re-hashes. Lookup is `_find_bytes`: one numba call that takes
the `bytes` object directly (numba reads it as a read-only uint8 buffer), packs
it and binary-searches the sorted uint64 column, with no Python-level work in
between.

Persistence is `.npz` plus a `<name>.npz.manifest.json` (the suffix is part of
the manifest name so a `.pkl` and a `.npz` of the same ball can coexist without
one clobbering the other's manifest), carrying the sha256 of the `.npz`, the
cap, the size, the depth histogram, the build wall seconds, peak RSS, and the
replay check. `load` refuses a file whose sha256 does not match.

MEASUREMENT_COMPACT_PLACEHOLDER

## 11. Caveats

* **The table is an offline precomputation and its cost is outside the
  per-row 1,000-unit allowance.** Section 4 is the price: 0.4 s to 10.5 minutes
  of single-threaded build, 230 KB to 66 MB of pickle, plus a few hundred MB of
  process memory to hold the largest table. None of that is charged to any row,
  and it should not be: it is paid once for the whole campaign. But a
  comparison against the frozen policy's per-row numbers is a comparison of
  *search* work only, and any claim of the form "policy X solves N rows in
  1,000 units" carries this table as a silent premise.
* **The cap is the knob, and it is exponential.** ~17x more states per +2 cap
  from 8 to 10, ~11x from 10 to 12. Every doubling of reach costs an order of
  magnitude of memory. There is no free lunch hiding here: the table is a
  memoised endgame, and endgames get big.
* **`depth` is an upper bound**, per section 3(c). Tails are valid, not
  necessarily shortest.
* **Set-exactness is proved by brute force only up to cap 8.** Above that the
  universe is too large to enumerate; the same algorithm is used, and every
  individual entry is still forward-verified and replayed, so soundness is
  machine-checked at every cap -- it is completeness at cap 10 and 12 that
  rests on the algorithm being the same one that is provably complete at
  caps 6-8.
* **The wall-clock numbers were taken on a shared 4-core box** with other
  screens running. Unit counts are exact and reproducible; seconds are not.
