# Theorems, proofs, and frequency: an audit of the AC19 completion rules

Scope: every "theorem"/completion rule that is used by, or available to, the
supermoves research tree at commit `98f719e2`, audited against the code that
implements it, and counted against the published census
`results/heuristic_search/ac19_final_policy_full_1k` (72,779 rows, 72,052
solved, 727 unsolved, 6,621,411 charged units, 39,387,241 verified elementary
moves).

Counting code: [`theorem_frequency.py`](theorem_frequency.py).
Output: [`theorem_frequency.json`](theorem_frequency.json).
Nothing under `research/supermoves_20260908/`, `results/` or `data/` was
modified, and no search was run on any row of `unsolved.csv` — the residual is
touched only by O(length) recognizers, and only aggregate counts are reported.

---

## 0. How a row was attributed to a rule

The census records `states` and `steps` for every solve but **not** the winner
label that `mid_search.complete` computed. The label is nevertheless
recoverable exactly, because the runner also stores the key `elementary_tail`,
and `mid_search.result(...)` attaches a tail **iff** the winner was
`middle_two_block` or `middle_primitive` (`terminal` and `middle_bs` never carry
one; `middle_bs_escape` inherits its inner winner's). So:

| observed | attribution |
|---|---|
| `elementary_tail` present and `two_block.solve(states[-1])` reproduces it byte for byte | **two-block** |
| `elementary_tail` present, otherwise (last state has a one-occurrence relator) | **primitive one-occurrence** |
| no tail, and some index `i` has an all-substitution suffix with `bs_gate(states[i], general=True)` non-None, `preflight(states[i])=='accept'` and `consecutive_bs.collapse(states[i]).states == states[i:]` exactly | **consecutive BS** |
| no tail, otherwise (last state is a pair of distinct single letters) | **ordinary terminal** (the search itself reached `(x,y)`) |

Validation. For all 28,035 solved `strict_donor` rows the whole of stage 1 was
re-executed faithfully (same evaluation caps, same charging, same terminal set),
which recovers `mid_search`'s own `winner` string. It agrees with the table
above on **28,035/28,035** rows (24,465 `middle_bs`, 3,564 `middle_primitive`,
5 `middle_two_block`, 1 `terminal`), with **0** state-replay mismatches. The
other two routes store no winner, so the rule is applied as stated.

Ambiguity found: **132** `plain_s20` rows (0.30 % of that route) whose greedy
path *coincides* with the deterministic BS-collapse suffix. These are resolved
by route, not by guessing: `plain_search_fast.mixed_search` has **no completion
macro of any kind**, so every one of its solves is an ordinary terminal; the
coincidence means the greedy search independently walked the same rewrite path.
No other ambiguity occurred (0 rows with a tail that matched neither rule, 0
tail-free rows whose last state was not a pair of single letters).

---

## 1. Frequency table — which rule actually closed each row

| rule (terminal) | rows closed | % of 72,052 solves | charged units | units/row | elementary moves | moves/row |
|---|---:|---:|---:|---:|---:|---:|
| **ordinary terminal** (no theorem — greedy search reached `(x,y)`) | 43,406 | 60.24 % | 3,817,181 | 87.9 | 14,772,281 | 340 |
| **consecutive BS(m,m+1) collapse** | 24,983 | 34.67 % | 1,333,697 | 53.4 | 24,115,532 | 965 |
| **primitive one-occurrence donor elimination** | 3,564 | 4.95 % | 653,851 | 183.5 | 447,758 | 126 |
| **two-block unimodular row reduction** | 99 | 0.14 % | 89,682 | 905.9 | 51,670 | 522 |
| *(unsolved residual)* | 727 | — | 727,000 | 1000.0 | — | — |

Cross-tabulated with the policy route:

| terminal \ route | strict_donor | plain_s20 | incumbent_restart |
|---|---:|---:|---:|
| ordinary terminal | 1 | 43,405 | **0** |
| consecutive BS | 24,465 | 0 | 518 |
| primitive one-occurrence | 3,564 | 0 | 0 |
| two-block | 5 | 0 | 94 |
| unsolved | 0 | 1 | 726 |

Two facts worth stating plainly:

* the single biggest closer in the census is **not a theorem at all** — 60 % of
  solves are stage 2's plain `S20_MK2` greedy search walking to `(x,y)`;
* the stage-3 incumbent closed **612** rows and **every one of them** came from
  a macro (518 BS, 94 two-block). It never once reached `(x,y)` by ordinary
  substitution. Whatever value stage 3 has, it is entirely the two macros.

Nodes distribution per terminal (charged units, whole-row totals):

| terminal | min | median | mean | p90 | max |
|---|---:|---:|---:|---:|---:|
| ordinary terminal | 5 | 29 | 87.9 | 262 | 889 |
| consecutive BS | 7 | 24 | 53.4 | 82 | 999 |
| primitive one-occurrence | 18 | 196 | 183.5 | 241 | 250 |
| two-block | 51 | 949 | 905.9 | 967 | 995 |

---

## 2. The rules, one at a time

Throughout, "ordinary AC move" means exactly what
`certificate_decoder.replay_elementary` accepts: `invert(i)`, `swap`,
`conjugate(i, by=<single letter>)`, `multiply(target, source)`. Nothing else is
in the replayed certificates.

### T1. Two-block unimodular row reduction — **proved constructive rule, enabled**

**Statement.** Let `R`, `S` be relators each of which is, up to free reduction,
cyclic rotation, inversion **and conjugation**, of the form `x^m y^n`. Write
`M = [[m,n],[p,q]]` for the exponent matrix. If `det M = ±1` then `(R,S)` is
carried to `(x,y)` by an explicit finite sequence of ordinary AC moves.

**Proof.** `primitive_patterns.md §1`: the integer row operation
`row_i <- row_i - row_j` is realized by `invert i; multiply i by j; invert i;
conjugate i by y^{-n_j}`, which restores the source row and returns the target
to two-block form; row negation is `invert i; conjugate i by y^{-n_i}`. `det = ±1`
gives `gcd(m,p)=1`, so subtractive Euclid on the first column terminates at
`(ε,0)` (up to a swap), forcing the lower-right entry to `±1`; repeated
subtraction then clears the off-diagonal entry. Quotients are emitted as
`|k|` copies of the unit macro, so no non-elementary "multiply a row by k" is
ever assumed.

**Code check.** `two_block.solve` implements exactly this: `negate`,
`subtract`, the `while matrix[1][0]` Euclid loop with a swap to keep
`matrix[0][0] >= matrix[1][0]`, then the off-diagonal clean-up. It asserts the
tracked matrix against the tracked words after every macro (`check()`), and
finally asserts `replay(pair, moves) == ['x','y']` — an independent replay from
the *original* pair. Hypotheses in code = hypotheses in prose, plus one extra
capability (see gap G3). `recognize` accepts rotations, inverses **and
conjugates**, returning the conjugator as the witness that `solve` then emits.

Empirically: over 200,000 pairs sampled from the 9,856 freely+cyclically reduced
words of length ≤ 8, `two_block.recognize`+determinant, `two_block_gate` and
`canonical_two_block_gate` agree on every canonical pair (0 disagreements); and
over **all 744** unimodular exponent matrices with entries in `[-6,6]`,
`two_block.solve` succeeds and self-replays (**744/744**, 0 failures, at most 59
elementary moves).

**Frequency.** 99 rows (0.14 %), 89,682 units, mean 906 units/row.
94 of the 99 came from the stage-3 incumbent — i.e. after ~900 units had
already been burned. In stage 1 it fires 5 times, always at donor-descent
depth 0.

### T2. Transport through an ambient free-basis automorphism — **proved, enabled, and load-bearing**

**Statement.** If `φ` is an automorphism of `F(a,b)` and a certificate carries
`(φ(R), φ(S))` to `(φ(a), φ(b))` by ordinary AC moves, then applying `φ` to
every word of that certificate carries `(R,S)` to `(a,b)`; multiplication and
inversion are literal, conjugation by `w` becomes conjugation by `φ(w)`. A
final Nielsen factorization of the basis `(φ(a), φ(b))` back to `(a,b)` — itself
ordinary AC moves — completes it. A simultaneous automorphism must **never** be
emitted as an AC move.

**Proof.** `primitive_patterns.md §2`; homomorphism, plus Nielsen generation of
`Aut(F_2)` by inversions, swaps and one-sided multiplications.

**Code check.** This is what makes the whole staged policy legitimate. Search
paths mix `{'kind':'substitution'}` and `{'kind':'automorphism'}` steps;
`certificate_decoder_compact_moves.decode_elementary` carries the inverse
cumulative automorphism, transports each later conjugator, emits explicit
canonicalization witnesses and Nielsen-reduces the terminal basis; the runner
then independently replays with `certificate_decoder.replay_elementary` and
requires literal `['x','y']`. **72,052/72,052** solves passed that second
replay, 0 errors. This is the strongest evidence in the whole tree, and it
covers every automorphism step in every route.

**Frequency.** Automorphism steps occur in 28,035 `strict_donor` rows (donor
descent; depth distribution below), in the `aut_edges` arm of stage 3, and
inside `primitive_completion`. 3,564 + 24,465 + 5 + 1 = 28,035 certified rows
contain them.

### T3. Primitive-donor elimination (exponent-sum `±1`) — **proved constructive rule, enabled in stage 1 only**

**Statement.** Let `(u,v)` be a free basis of `F(a,b)` and `W` a reduced word in
`u^{±1}, v^{±1}` whose `v`-exponent sum is `±1`. Then `(u,W)` is ordinary-AC
trivial, constructively.

**Proof.** `primitive_patterns.md §3`: write an occurrence `W = A u^ε B`; a
conjugated donor multiplication deletes it while restoring `u`. Each deletion
strictly decreases the number of `u`-letters, so the process terminates at
`v^e`; the hypothesis makes `e = ±1`. The hypothesis is also *forced*: with the
first relator primitive, the abelianized rows are `(1,0)` and `(e_u,e_v)`, so
normal generation requires `|det| = |e_v| = 1`.

**Code check — and this is where prose and code differ most.**
`primitive_completion.complete(pair, donor_word=d)`:

1. rejects unless `|abelian_det(pair)| == 1` (the forced hypothesis, 1 unit);
2. runs a **strict Nielsen descent on the donor** (`NIELSEN` images, applied to
   the whole pair by `apply_pair`, recorded as `automorphism` steps) until the
   donor is a single generator — *this*, not a basis parser, is how `(u,v)` is
   obtained;
3. deletes every donor letter from the companion, leftmost first, by
   `conjugate(source, suffix); [invert source]; multiply(target, source);
   [invert source]; conjugate(source, inverse(suffix))`;
4. normalizes the result to `['x','y']` with inversions and a swap.

So the theorem actually implemented is broader than §3/§4: *"if a strict Nielsen
descent takes the chosen donor to a generator and `|det| = 1`, the pair is
AC-trivial."* Step 3 is the §3 macro **mirrored** (conjugate by the suffix `B`
and right-multiply, giving `(A u^ε B)(B^{-1}u^{-ε}B) = AB`), not the documented
left-multiplication by `A u^{±1} A^{-1}` — see gap G4. Steps 2-4 are guarded by
asserts (`assert donor in current`, `assert current[source-1] == donor`,
`assert current == ['x','y']`), and the emitted tail is replayed by the runner.

Tightness test: over 3,000 random pairs with a one-occurrence donor of
length > 1 and `|det| = 1`, `complete` solved **3,000/3,000** — the gate
(§4 below) is exactly the right sufficient condition, never a
`no_strict_reduction` failure.

**Frequency.** 3,564 rows (4.95 %), all on the `strict_donor` route, 653,851
units (mean 183.5 — the most expensive per row after two-block).

### T4. One-occurrence donors — **proved recognizer for T3, enabled, but used only in its degenerate case**

**Statement.** A cyclically reduced word containing `a` exactly once (either
sign) has the form `b^r a^ε b^s`; after a rotation and possibly an inversion it
is `a b^{ε(r+s)}`, hence primitive with explicit complement `b`. Consequently
donors of any length are recognized uniformly; rewriting the companion in the
`(u,v) = (a b^k, b)` basis, its `v`-exponent is `exp_b(W) − k·exp_a(W)`, which
the abelianization determinant already tests.

**Code check.** The gate is `cheap_gates.one_occurrence_donor(word)`:
`word.lower().count('x') == 1 or word.lower().count('y') == 1`. Exactly the
hypothesis. But the *compiler* (T3) does not use the `a -> u v^{-k}` substitution
of §4 at all — it Nielsen-descends instead (gap G5).

**Frequency — a sharp negative result.** In **all 3,564** census uses, the donor
was *already a single generator* at the point of call
(`endpoint_min_relator_len_1|primitive_one_occurrence = 3564`): the strict-donor
Nielsen descent had already shortened one relator to `x`/`X`/`y`/`Y`, and
`primitive_completion`'s own descent loop then ran zero iterations. **The
general "one-occurrence donor of arbitrary length" recognizer of §4 never fired
in the published census.** What closed those 3,564 rows is T3 with `u` a literal
generator.

Descent depth for these rows is nevertheless nontrivial (the work is done by the
donor prepass, not by the completion): depth 0: 253, 1: 220, 2: 2,563, 3: 370,
4: 133, 5: 19, 6: 5, 7: 1.

### T5. Consecutive BS(m,m+1) collapse + Britton preflight — **proved constructive rule, enabled, the workhorse**

**Statement.** Let the donor be `b^{-1} a^m b a^{-(m+1)}` (any signed choice of
`a,b`, up to cyclic rotation, inversion and relator swap), so the quotient is
the HNN extension `BS(m, m+1) = ⟨a,b | b^{-1}a^m b = a^{n}⟩`, `n = m+1`, with
stable letter `b` and associated subgroups `⟨a^m⟩`, `⟨a^n⟩`. Let the companion
`W` have stable-letter exponent `±1`. If cyclic Britton reduction of `W`
(replace `b^{-1}a^{km}` by `a^{kn}b^{-1}` and `b a^{kn}` by `a^{km}b`) reduces
`W` to a single stable letter, then `(donor, W)` is ordinary-AC trivial and the
whole path is substitution-only.

**Proof.** Every Britton pinch is an *exact* application of the relator, so each
one is a legal relator substitution (`replay_move`); no free-group inequality is
assumed. After the pinches `W = b^{-1}a^{e}`, i.e. `b = a^{e}`; substituting into
the donor gives `a^{-e}a^{m}a^{e}a^{-n} = a^{m-n} = a^{-1}`, so the donor becomes
a generator; deleting the `|e|` remaining `a` letters from `W` leaves
`(a^{-1}, b^{-1})`, a terminal pair.

**Order-independence (needed below).** The stable-letter length of a cyclically
Britton-reduced word is a conjugacy invariant (Britton's lemma / Collins'
lemma). Each pinch removes exactly two stable letters, and `exp_b = ±1` is odd,
so *any* maximal greedy pinch schedule ends at one stable letter or at none —
accept/reject is independent of the schedule.

**Code check.** Three modules implement pieces of this, and they are consistent
where it matters:

* `cheap_gates.bs_gate(pair, general=True)` — cached donor-string table keyed by
  length, then the companion exponent test. Verified identical to
  `consecutive_bs._recognize` on every sampled BS pair (0 mismatches).
* `bs_preflight.preflight` — the abstract `(signs, powers)` Britton scan.
* `consecutive_bs.collapse` — the certified compiler on real words.

*Signed orientations:* the recognizer loops `a,b ∈ {x,X,y,Y}` with
`a.lower() != b.lower()`, i.e. all 8 ordered signed pairs, and compares under
`canon_rel` (rotation + inversion invariant); both relators are tried as donor.
Tested exhaustively for `m = 1..5` over all 8 signed orientations × all cyclic
rotations × inversion × relator swap: **1,440/1,440 recognized, 0 missed.** So
yes, `consecutive_bs` handles all signed orientations. Every canonical BS donor
string matches exactly 2 of the 8 `(a,b)` orientations, and `bs_gate`,
`_recognize` and `donor_orientations` iterate them in the same order, so they
always select the same one.

*What it deliberately does not accept* (correctly, these are different groups or
different donor lengths): `BS(1,3)`, `BS(2,4)`, `BS(2,5)`, `BS(3,5)`, `BS(2,2)`,
`BS(3,6)`, `BS(1,1)` — none recognized; and the "negative" shape
`b^{-1}a^m b a^{n}` (i.e. `b^{-1}a^m b = a^{-n}`) — not recognized.
`b^{-1}a^m b a^{-(m-1)}` **is** recognized (as `m-1`), as it must be.

*Preflight vs compiler.* Can the preflight accept something the compiler then
fails on? **Not on accept/reject grounds** — 35,029 random BS pairs, 0
disagreements, which the order-independence argument above explains. **Yes on
budget grounds**, and the preflight's own numbers cannot be used to predict the
cost: the two run *different* greedy schedules (the compiler inverts the
companion whenever `exp_b = +1`, and re-anchors at `canon_rel`'s lex-least
rotation after every rewrite, while the preflight re-anchors its abstract list
at the chosen pinch). See gap G7 for a concrete pair where the preflight
predicts 7 rewrites and the compiler needs 9. The compiler is called with
`budget = min(10000, remaining+1)`, so an accepted state whose certificate is
longer than the remaining allowance fails; no solved row was lost this way (all
24,983 BS closures succeeded), but the residual contains one row where the
theorem provably applies and the policy never asked (§5).

**Frequency.** 24,983 rows (34.67 % of solves), 1,333,697 units (mean 53.4 —
the *cheapest* rule per row closed), 24,115,532 elementary moves (61 % of all
moves in the census: BS certificates are long, ~965 moves/row).

`m` of the recognized donor at the winning state:

| m | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---:|---:|---:|---:|---:|---:|---:|
| rows | **24,599** | 358 | 20 | 3 | 1 | 1 | 1 |

### T6. Torus / amalgam donor `a^p b^q`, `gcd(p,q)=1` — **prose only; no module; not enabled**

`primitive_patterns.md §6` gives the amalgam `⟨a⟩ *_{a^p = b^{-q}} ⟨b⟩`, the
normal-form collection procedure, and the Bezout target `V = a^r b^s`. It is
explicitly conditional ("determinant one alone is not sufficient"), and it
requires a full normal-form match or a replayed rewrite trace. **There is no
implementation of it anywhere in `research/supermoves_20260908/`**, so it closes
0 census rows and cannot be counted. It is the only rule in the prose with no
code behind it.

### T7. Stable-power `Q_(k,N)` family — **recognizer + compiler, NOT enabled in the frozen policy**

`stable_power.canonical_donor_gate` recognizes donors
`a^{-2} b^{-k} a b^{k}` (5 or more letters, odd length, exactly 4 cyclic runs),
`stable_power_Q._recognize` additionally requires the companion to be *exactly*
`a^{-n} b^{k-1} a^{-1} b^{-k}` up to canonicalization, and
`stable_power.collapse` applies bounded certified pinches before the direct
`Q_(k,N)` compiler. It is a genuine proof-carrying compiler (substitution-only
path, `replay_move`-checked), but it is a **narrow template**, not a theorem
with a general hypothesis: the companion must match a one-parameter word.

`final_policy` never sets `use_stable_power`, so it closes **0** census rows.
It is nevertheless *computed and discarded* on every stage-1 admitted candidate:
`DONOR_NORMALIZED_BS.inspect` fills `stable_power_donors` and the result is
never read by `final_policy` (gap G9).

**Residual relevance: this is the one disabled rule with a real hit rate** —
its donor gate matches **69 of the 727** residual roots (9.5 %).

### T8. One-splice power family — **recognizer + compiler, NOT enabled**

`splice_power_family.canonical_family_gate` requires a donor
`a^{-h} b^{-1} a^{-1} b a^{-1} b` (3 or 6 cyclic runs) *and* a companion exactly
`a^{-(p+2)} b a^{-(h-p)} b^{-1} a^{-1} b` with `p | h`; `collapse` splices and
then hands off to `consecutive_bs`. Again a template, not a hypothesis-driven
theorem. Not enabled; closes 0 rows; matches **0 of 727** residual roots.

### T9. Stable-square donor — **hard-coded single donor, NOT enabled**

`stable_square.py` is built around the literal donor `YYXXyxx` and its 8 signed
permutations (`DONOR_TRANSFORMS`), with a `forward_pinch` that pattern-matches
`XX y^j xx`. It is a proof-carrying bridge for one specific presentation family,
not a general rule. Not enabled; 0 rows. (It is the donor of `ac19_99`, the
first row of `unsolved.csv`, which is why it exists.)

### T10. Christoffel primitive gate — **sufficient recognizer only, NOT enabled**

`christoffel_primitive_gate.recognize_canonical` decides whether a canonical
relator is a signed Christoffel/mechanical word `w(p,q)` with `gcd(p,q)=1`, and
returns the Euclidean witness `steps` that reduces `(p,q)` to a generator. It is
a *sufficient* primitivity certificate (a linear-time replacement for a
Whitehead search), and `mid_search` would use it only as an alternative gate
feeding `primitive_complete` (`use_christoffel`). It is **not enabled** by
`final_policy`, closes 0 rows, and matches **0 of 727** residual roots. Note it
is strictly a gate: it supplies no complement and no certificate by itself —
exactly the boundary `primitive_patterns.md §5` warns about.

### T11. Stalled-BS escape feature `T` and the high-core escape — **heuristic, enabled, and inert**

`mid_search.bs_escape_feature(state)` returns `s−1` where `s` is the stable-letter
count at which the Britton scan *stalled*, and only for a recognized-but-rejected
BS pair. `root_router` uses `T > 0` at the root to choose the arm, and
`mixed_search` adds `4·T` to the priority. `complete` may additionally spend up
to 300 units (at most once per search) on a bounded continuation when a rejected
core has ≥ 7 stable letters.

This is a heuristic, not a theorem — nothing about it is proof-carrying — and it
is **measurably inert**: of the 1,338 rows that reached stage 3, only 18 took the
`T`-ordered ordinary arm, and **0 of those 18 were solved**. All 612 stage-3
solves came from the `aut_edges` arm. (Whether the ≥7-stable-letter escape macro
fired is not recoverable from the saved records — the runner discards
`escape_macros`.)

### T12. Strict donor descent — **not a theorem; a normalizer, and a very effective one**

`strict_donor_route_fast.match` greedily applies whichever of the four ordered
Nielsen maps `x→xy, x→xY, y→yx, y→yX` strictly reduces the cyclic length of the
chosen donor, using exact signed-adjacency deltas (self-checked: it asserts the
predicted delta against the realized image length). It searches no
length-preserving plateau, so it is incomplete by construction. It closes no row
by itself — except one (`ordinary_terminal|strict_donor = 1`, a row driven all
the way to `(x,y)` by automorphisms alone).

Its value is as the *feeder* for T3/T5: 28,035 of 72,052 solves (38.9 %) went
through it, at a mean of 53.4 units.

### T13. Plain `S20_MK2` greedy search — **not a theorem, and the largest single closer**

Stage 2 is `L + 20·S + 2·MK` best-first over ordinary relator substitutions with
no macros and no ambient neighbours. 43,405 solves (60.2 %), 3,817,176 units
(57.6 % of the census budget), median 29 units, p90 262.

---

## 3. Route diagnostics

### 3.1 `strict_donor` (28,035 rows, all solved, 1,496,045 units, mean 53.4)

Donor descent depth (number of accepted Nielsen maps before the gate):

| depth | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| rows | 19,476 | 4,255 | 3,491 | 625 | 156 | 26 | 5 | 1 |

Which gate of `DONOR_NORMALIZED_BS.inspect` admitted the row (re-run on the
donor endpoint), and what then closed it:

| admitting gate | rows | terminal |
|---|---:|---|
| `bs_preflight accept` | 24,458 | consecutive BS |
| `one_occurrence` | 3,564 | primitive one-occurrence |
| `one_occurrence` + `bs_preflight accept` | 7 | consecutive BS |
| `two_block` | 5 | two-block |
| `two_block` + `one_occurrence` | 1 | ordinary terminal (endpoint was already `(x,y)`) |

Depth by gate: the BS gate is overwhelmingly a *depth-0* phenomenon
(19,210 of the 24,458 admitted by the BS gate alone are at depth 0 — the root
already has a BS donor), while the
one-occurrence gate is a *depth-2* phenomenon (2,563 of 3,564 at depth 2 —
two Nielsen maps shrink a relator to a generator).

### 3.2 `plain_s20` (43,406 rows, 43,405 solved)

Whole-row charged units: min 12, median 29, mean 87.9, p90 262, max 889 — the
1,000-unit budget was never binding for a solve. The stage-2 share alone
(`plain_charges`): min 3, median 13, mean 48.2, p90 123, max 872.

### 3.3 `incumbent_restart` (1,338 rows, 612 solved)

| arm (decided by `mid_search.bs_escape_feature(root) > 0`, recomputed) | rows | solved | unsolved | units (mean) |
|---|---:|---:|---:|---:|
| `aut_edges` (T = 0) | 1,320 | 612 | 708 | 976.7 |
| `s20` ordinary, `+4·T` (T > 0) | 18 | **0** | 18 | 1000.0 |

Solved stage-3 rows use 900–999 units (mean 949.7); all 726 unsolved rows are at
the 1,000 cap.

---

## 4. Strength ranking

**By coverage (rows closed).**

1. **Plain `S20_MK2` greedy search** — 43,406 (60.2 %). Not a theorem. Honest
   answer: most of AC19 at this budget does not need one.
2. **Consecutive BS(m,m+1) collapse** — 24,983 (34.7 %), i.e. 6.8× the 3,663
   rows closed by all other theorems put together. By a wide margin the
   strongest *theorem*: cheap, general in `m` and in all signed orientations,
   and it is the only rule that fires on both the stage-1 and stage-3 routes.
3. **Primitive donor elimination (T3) via one-occurrence gate** — 3,564 (5.0 %).
4. **Two-block unimodular reduction** — 99 (0.14 %).
5. Everything else — **0**: torus/amalgam (unimplemented), stable-power,
   splice-power, stable-square, Christoffel, high-core escape, `T` ordering.

**By cost (units per row closed — lower is better).**

1. **Consecutive BS: 53.4** — the cheapest closer in the census, and it is
   *cheaper than the plain search it replaces* (87.9).
2. Plain search: 87.9.
3. Primitive one-occurrence: 183.5 (capped by the 250-unit stage-1 allowance).
4. Two-block: 905.9 — 94 of its 99 rows only arrive in stage 3, so its cost is
   really the cost of the two stages that failed first.

By certificate size the ranking inverts: BS produces 61 % of all 39.4 M
elementary moves at 965 moves/row, against 126 for primitive and 340 for the
plain search. BS buys search units with certificate length.

**By residual relevance (cheap gate satisfied on a residual root but the rule
did not close the row) — aggregate counts over the 727 unsolved rows only:**

| gate | residual roots matching | notes |
|---|---:|---|
| `abelian_det = ±1` | 727 | necessary condition, universally satisfied |
| `stable_power` donor gate (**disabled rule**) | **69** | largest untapped cheap-gate hit |
| general BS donor gate | 19 | 18 preflight-**reject**, 1 preflight-**accept** |
| `two_block` gate | 0 | |
| `one_occurrence` donor | 0 | |
| `splice_power` gate | 0 | |
| Christoffel primitive | 0 | |

The single preflight-**accepting** residual root is on the `plain_s20` route,
i.e. stages 1–2 exhausted the 1,000 units and stage 3 — the only stage that
probes the *root* for a BS terminal — never ran. Its preflight reports a
certificate of roughly 136 rewrites. **That row is lost to the policy's staging,
not to the theorem.** The other 18 BS-shaped residual roots genuinely stall:
11 at 3 residual stable letters, 7 at 7.

---

## 5. Testing the belief "the BS(1,2) collapse is the strongest theorem so far"

Supported, with two caveats.

| measurement | BS(1,2) (`m=1`) | general BS(m,m+1), `m>1` |
|---|---:|---:|
| rows closed by the BS terminal | **24,599** (98.46 % of BS closures; 34.1 % of all solves) | 384 |
| solved roots already displaying such a donor | 18,838 | 963 |
| of those, closed by the BS terminal | **18,838 (100.0 %)** | 379 (39.4 %) |
| solved rows with such a state anywhere on the certified path | 40,727 | 45,417 (any `m`) |
| residual roots with such a donor | 1 (preflight **accepts**) | 18 (preflight rejects) |

* **Coverage.** BS(1,2) alone closes 24,599 rows = 34.1 % of the census, 6.7×
  the 3,663 rows closed by the two other theorems (primitive 3,564 + two-block
  99) put together.
* **Reliability.** Its root-to-solve conversion is *perfect*: every one of the
  18,838 roots with a length-5 BS donor was closed by the collapse. For `m > 1`
  the conversion collapses to 39 %, because the Britton divisibility condition
  (`powers % m == 0` / `% n == 0`) is vacuous when `m = 1` — every
  `b^{-1}a^p b` pinch is legal — and increasingly restrictive as `m` grows.
  That, not any difference in the proof, is why `m = 1` dominates.
* **Reach.** 41,930 solved rows (58.2 %) contain a preflight-*accepting* BS state
  somewhere on their certified path, including **16,947 `plain_s20` rows** which
  were closed by the greedy search only because stage 2 has no probe at all.
  The theorem is applicable far more often than it is invoked.

Caveats. (i) BS(1,2) is not stronger *as a theorem* than general
BS(m,m+1) — it is the same theorem with a hypothesis that happens to be vacuous
at `m = 1`, and the population (`AC19_extended_aut_min`, many length-5
relators) supplies it constantly. (ii) On the *residual* it is nearly exhausted:
1 accepting root out of 727, and it is lost to staging, not to mathematics.
The BS collapse is the strongest rule found **for the solved part of the
census**; it is not a lever on what remains.

---

## 6. Missing hypotheses — what would extend each rule onto the residual

Aggregates over the 727 residual roots only.

**Consecutive BS requires `n = m+1` exactly, and the positive shape.**
Relaxing it buys **nothing at the root**: of the 19 residual roots carrying a
4-run donor `b^{-1}a^{p}b a^{q}` with a unit-length stable letter, **all 19 are
already consecutive with `gcd(m,n) = 1`** — `{m,n}` is `{1,2}` once, `{2,3}`
seven times, `{5,6}` ten times, `{7,8}` once — and all 19 have companion stable
exponent `±1`. So the count of residual roots with a BS(m,n) donor having
`|m−n| ≠ 1` **or** `gcd(m,n) > 1` is **0**, and the count with the "negative"
shape `b^{-1}a^m b = a^{-n}` is also **0**. What blocks these 18 rows is the
*Britton divisibility scan*, not the consecutivity hypothesis.

**The real BS-shaped gap is the stable-letter run length.** Widening the donor
pattern from `b^{-1} … b` to `b^{-s} … b^{s}` (a `Z`-by-`Z` HNN with a
non-generator stable letter) would newly recognize, in the residual:

| stable-run `s` | 1 (currently recognized) | 2 | 3 | 4 |
|---|---:|---:|---:|---:|
| residual relators of that shape | 20 | **59** | 5 | 7 |

The `s = 2` family alone is 3× the size of everything the current BS recognizer
sees in the residual. (`stable_square.py`'s donor `YYXXyxx` is exactly an
`s = 2` instance, which is why that module exists — but it is hard-coded to one
word and disabled.)

**Two-block wants more blocks.** No residual pair is a two-block pair (0/727),
and only 10 residual roots contain a genuinely ≤2-block relator. But **293 of
727** contain a relator with exactly 4 cyclic blocks, and **30** have both
relators at ≤4 blocks. A "four-block" analogue of T1 — an exact reduction for
pairs of `a^{m}b^{n}a^{p}b^{q}` words with a unimodular invariant — is the
single largest structural family in the residual. Block profiles (sorted pair):
`(4,6)` 139, `(6,8)` 142, `(6,6)` 105, `(4,8)` 102, `(8,8)` 52, `(6,10)` 45,
`(8,10)` 42, `(4,4)` 28, `(8,12)` 16, `(4,10)` 12, `(4,12)` 10, rest ≤ 8 each.

**One-occurrence / primitive wants a plateau.** 0/727 residual roots carry a
one-occurrence relator and 0 are Christoffel-primitive, so the gate is exhausted
*at the root*. (Whether a strict donor descent reaches a one-occurrence endpoint
on any residual row is deliberately not measured here — that would be
re-executing stage 1 on `unsolved.csv`. For context, 8,559 of the 28,035 solved
`strict_donor` rows needed depth ≥ 1, so root-level absence is not proof of
endpoint-level absence.) The structural limit worth attacking is upstream:
`strict_donor_route_fast.match` follows only *strictly* cyclic-length-reducing
Nielsen maps and, by design, never searches a length-preserving Whitehead
plateau — so any residual root whose donor is Nielsen-minimal gets exactly one
gate evaluation, at the root, and it fails.

**Torus/amalgam (T6) is unimplemented.** Its hypothesis (`gcd(p,q) = 1`,
`pq ≠ 0`, two-block donor) cannot be counted against the residual until someone
writes the normal-form collector; the residual has 10 roots with a ≤2-block
relator, which is an upper bound on where it could possibly apply at the root.

**Stable-power (T7) is the cheapest thing to try next.** 69 residual roots
already satisfy its donor gate. That gate is *already computed and thrown away*
on every stage-1 candidate (gap G9), so enabling `use_stable_power` in the
mid-search terminal set costs almost nothing to evaluate — though `Q_(k,N)` also
requires the exact companion template, so 69 is an upper bound, likely a loose
one.

Residual context: total relator length 14–31, median 19; all 727 have
`|det| = 1`; 726 of 727 hit the 1,000-unit cap in stage 3.

---

## 7. Gaps found between the prose and the code

**G1 — the stage-1 one-occurrence gate does not test the determinant.**
`AC19_FULL_CENSUS_ALGORITHM.md` (Stage 1) says the route continues on "a relator
containing exactly one occurrence of one generator, **with the companion
satisfying the primitive compiler's unimodular abelianization test**".
`DONOR_NORMALIZED_BS.inspect` implements that branch as
`[i for i, word in enumerate(state) if one_occurrence_donor(word)]` — a pure
letter count, no determinant. The test happens later, inside
`primitive_completion.complete`, and a failure there costs a charged unit and
the whole tail search. *Benign here*: `|abelian_det|` is invariant under AC moves
and under `apply_pair` with a Nielsen automorphism, and every AC19 input has
`|det| = 1` (727/727 residual roots confirm), so the gate is never asked a
question it would get wrong. But the gate is weaker than documented.

**G2 — `cheap_gates` ships two different two-block gates, and the frozen policy
uses both.** `two_block_gate` freely *and cyclically* reduces before testing;
`canonical_two_block_gate` assumes its input is already reduced and rejects
anything with more than two cyclic letter-changes. `DONOR_NORMALIZED_BS.inspect`
(stage-1 admission) calls the former; `mid_search.complete` (the actual terminal)
calls the latter. Concrete divergence:

```
pair ('Yxxyy', 'x')
  two_block.recognize('Yxxyy')  = ((2, 1), 'Y')     # conjugator witness
  two_block_gate                = True
  canonical_two_block_gate      = False
  two_block.solve               = solved, 20 elementary moves, replay ['x','y']
```

Unobservable in the census — every state the policy inspects is `canon_pair`
output — but the adjacent docstrings ("True exactly when `two_block.recognize`
accepts both words with det ±1" / "Exact two-block gate") read as if the two were
interchangeable, and they are not.

**G3 — `two_block.recognize` is stronger than `primitive_patterns.md §1`.**
§1 says "Recognition should accept cyclic rotations and inverses of each block
word." The code additionally strips a conjugating prefix
(`while reduced[0] == reduced[-1].swapcase()`) and returns it as the conjugation
witness, so it accepts arbitrary *conjugates* of block words —
`recognize('Yxxyy') = ((2,1), 'Y')` above. The extra power is real and correctly
compiled, but the mid-search gate throws it away (G2).

**G4 — the emitted primitive-deletion macro is the mirror of the documented
one.** `primitive_patterns.md §3` specifies: write `W = A u^ε B`, apply
`C_(A^{-1})` to make the donor `A u A^{-1}`, invert if `ε = +1`, and
**left**-multiply. `primitive_completion.complete` deletes the same (leftmost)
occurrence but conjugates by the **suffix** `B` and **right**-multiplies:
`(A u^ε B)(B^{-1} u^{-ε} B) = AB`. Both are correct; they emit different move
lists. All 3,564 primitive certificates in the census contain the code's
version, so anyone replaying the documented contract will not reproduce the
published `elementary_tail`.

**G5 — §4's "cheap mid-search specialization" is not what runs.** §4 prescribes
rewriting the companion by the literal substitution `a → u v^{-k}, A → v^{k}U`
in the `(u,v) = (a b^k, b)` basis and then running the deletion loop.
`primitive_completion` does no such substitution: it obtains the basis by a
strict Nielsen descent on the donor, recorded as `automorphism` steps that the
certificate decoder must transport. The theorem the code proves is therefore
*broader* than §4 ("strict Nielsen descent to a generator + `|det| = 1` ⟹
AC-trivial"), with `one_occurrence_donor` as a cheap sufficient condition for
the descent to succeed (verified tight: 3,000/3,000 random one-occurrence donors
of length > 1 with `|det| = 1` solved). And measurably, §4's *general* case
never ran: in all 3,564 census uses the donor was already a single generator.

**G6 — `primitive_completion`'s default donor can pick the wrong relator.**
With `donor_word=None` it takes `min(current, key=(len, word))`, which need not
be the one-occurrence relator. Example, `|det| = 1`:

```
complete(('YXyxx','Yxxxx'))                      -> {'solved': False, 'reason': 'no_strict_reduction'}
complete(('YXyxx','Yxxxx'), donor_word='Yxxxx')  -> solved
```

`mid_search` always passes `donor_word`, so the census is unaffected; it is a
trap for direct callers and for any future policy that omits the argument.

**G7 — the preflight and the compiler run different Britton schedules, so the
preflight's cost numbers are wrong.** `bs_preflight.preflight` scans the raw
companion and re-anchors its abstract `(signs, powers)` list at the chosen
pinch; `consecutive_bs.collapse` scans `inv(companion)` whenever `exp_b = +1`
and re-anchors at `canon_rel`'s lex-least rotation after every rewrite. They
provably agree on **accept/reject** (each maximal cyclic Britton reduction
reaches the conjugacy-invariant stable-letter length; confirmed on 35,029 random
BS pairs, 0 disagreements) but not on the path. The only cost estimate the
preflight exposes, `pinches + 2 + |base_exponent|`, is exact whenever
`pinches = 0` (6,598/6,598 sampled) and **wrong in 654 of 1,584** sampled
accepting pairs with at least one pinch. Concrete:

```
pair ('YXyxx', 'YXXXyxYx')
  preflight -> accept, pinches=1, base_exponent=-4   (predicts 7 rewrites)
  collapse  -> collapsed in 9 rewrites
```

Any policy that pre-charges the compiler from the preflight will under-charge.

**G8 — `unknown` is documented as fatal and treated as permissive.**
`AC19_FULL_CENSUS_ALGORITHM.md` states "Reject and integer-growth `unknown`
results are not solves." `mid_search.complete` computes
`rejected = check['status'] == 'reject'` only, so an `unknown` falls through to
`consecutive_bs.collapse(state, budget=..., intermediate_cap=None)`. `unknown`
*is* reachable at census word lengths — with the BS(1,2) donor `YXyxx` and
companion `Y^{64} x y^{63} X` (pair length 134) the preflight returns
`{'status': 'unknown', 'scans': 8127, 'pinches': 62}` after 62 doubling pinches
overflow 63 bits. The consequence is a cost leak, not a memory hazard: each
rewrite changes a relator length by at most `n−m = 1`, so with a finite budget
the peak length is bounded by `|root| + budget` (measured: 399 rewrites, peak
512, `reason='budget'`). Still, the compiler burns the entire remaining
allowance on a state the guard already flagged as unbudgetable, and the doc says
it should not have been tried.

**G9 — the frozen policy computes a gate it never reads.**
`DONOR_NORMALIZED_BS.inspect` fills `stable_power_donors` via
`stable_power.canonical_donor_gate` on every stage-1 endpoint;
`final_policy.search` tests only `two_block`, `one_occurrence_relators` and
`bs_preflight`. The stable-power result is recorded in the attempt dict and
discarded. (Its cost is also outside the 1,000-unit budget — `inspect` returns
a `symbol_work` figure that `final_policy` stores as `gate_symbol_work` and does
**not** add to `charged`. That is consistent with the documented
`work_unit_note`, but it means the headline "1,000 heterogeneous units" excludes
`4·|pair|` symbol scans plus the Britton comparison count per inspection.)

**G10 — one documented detail of the high-core escape is stronger than the
code.** The algorithm document says a nonordinary route "may spend up to 300 of
the still-shared allowance on the bounded high-core escape continuation"; the
code additionally allows it **at most once per search** (`not escape_macros`).
Immaterial to the counts, but the escape's usage is not recoverable at all from
the published records — the runner keeps `states`/`steps` and drops
`escape_macros`, so no census-level statement about the escape can be made.

---

## 8. Reproduction

```bash
PYTHONPATH=. python3 research/residual_20260909/theorem_frequency.py
```

Streams the 74 shards line by line (`json.loads` per line), re-executes stage 1
for every solved `strict_donor` row, and writes
`research/residual_20260909/theorem_frequency.json`. Single-threaded, ~115 s,
read-only with respect to the frozen census. Optional arguments
`<shard_limit> <output_path>` restrict it for smoke tests.
