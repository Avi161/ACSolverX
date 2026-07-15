# PIPELINE.md — one-shot Change of Variables (Branch B)

What this pipeline does, why it exists, how every piece works, and how to run the two
production experiments. Source of the method: `literature/txt/change_of_variables_stable_ac.txt`
§3.1 (the 4-pager). Code: `cov.py` (transform) + `run_cov.py` (runner) in this directory.

---

## 1. Why: search cost is not an invariant

The greedy baseline leaves 12 ms640 presentations unsolved at 50k nodes — yet 10 of those 12
have an **orbit-mate under Aut(F₂) that the same greedy solves easily**. Whether a presentation
is stably AC-trivial is invariant under a change of variables; whether *our greedy can find the
path* is not. The same mountain looks different on a different map.

A change of variables (CoV) re-coordinatises the presentation before searching: pick a word
`w(x,y)`, introduce `z = w`, eliminate one old generator, and land in a fresh 2-generator
coordinate system. If the original start sits in a bad valley of the two-hump landscape, the
transformed start may sit somewhere the hump is lower — a "wormhole" past the barrier.

This pipeline is **case (i)** only: CoV applied **once, to the initial presentation**, then the
ordinary numba greedy runs on the transformed pair. (`n_cov` is an int so case (ii) — CoV moves
*during* search — can extend it later without a schema change.)

## 2. The transform, step by step

Alphabet codec everywhere: `1=x, -1=X, 2=y, -2=Y, 3=z, -3=Z` (capital = inverse).

Given `(r1, r2)` and a candidate `z = w(x,y)`:

1. **Stabilize** — add generator `z` and defining relator `Z·w` (asserts z = w).
   Presentation is now `(r1, r2, Zw)` in F₃. This is the stable-AC stabilization move.
2. **Substitute** — replace occurrences of `w → z` and `w⁻¹ → Z` in r1 and r2
   (`substitute_word`: one left-to-right pass, non-overlapping, then free reduction).
   Every substitution is an AC-move using the defining relator, so this stays in the
   stable AC class. *Limitation:* the scan is linear, so an occurrence straddling the
   cyclic seam of a stored relator is not matched — sound, just less powerful.
3. **Isolate x — or y** (`iso_gen`) — the stabilized presentation ⟨x,y,z | …⟩ has three
   generators, and destabilizing back to two may eliminate **either** old one. Find a relator
   containing **exactly one ±g** (g = x or y, counted on the cyclic reduction) **and at least
   one z-letter**. Rotate the g to the front: `g^ε·s` with s g-free. Then `g·s = 1 → g = s⁻¹`
   and `g⁻¹·s = 1 → g = s`. The z-letter requirement exists because a z-free isolator would
   eliminate g without ever using z — z would be dead weight.
4. **Destabilize** — rewrite every ±g in the two *kept* relators as `expr` / `expr⁻¹`
   (`substitute_generator`), then drop the isolating relator together with the generator g.
   The isolator is consumed: it *became* the definition of g.
5. **Relabel** — the survivors mention only the other old generator and z; map them back to
   (x, y): after x-elimination `(y,z) → (x,y)`, after y-elimination `x` stays and `z → y`.
   Output: a 2-generator pair the unmodified greedy can search.

One z word can therefore yield **two different coordinate systems** — its x-eliminating and
y-eliminating starts (row field `iso_gen`; both are searched in the sweep). The two targets
are tied by an exact symmetry: eliminating y on P with z=w equals eliminating x on the
generator-swapped presentation with the swapped word (`test_xy_symmetry_oracle` pins this on
every benchmark row — an independent check of the whole y path).

Which relator is isolated decides what survives (`iso_index` in every result row):

| iso_index | isolated (consumed)            | output pair                        |
| --------- | ------------------------------ | ---------------------------------- |
| 0         | r1′                            | (r2′ transformed, Zw transformed)  |
| 1         | r2′                            | (r1′ transformed, Zw transformed)  |
| 2         | Zw itself (universe mode only) | (r1′ transformed, r2′ transformed) |

### Worked example A — the paper's golden, AK(3) with z = xyx

AK(3) = `(xyxYXY, xxxYYYY)`.

- Substitute `xyx → z`: r1 = **xyx**YXY → `zYXY` (1 sub); r2 untouched.
- Isolate from r1′ = `zYXY`: one X, rotate → `XYzY`, ε = −1 → **x = YzY**.
- Destabilize: r2 = xxxYYYY → `(YzY)³YYYY` = `YzYYzYYzYYYYY` (13);
  defining relator `Zxyx` → `Z·YzY·y·YzY` → `ZYzYzY` (6, one Yy cancellation).
- Relabel: **`(XyXXyXXyXXXXX, YXyXyX)`**. Same group, new coordinates.

### Worked example B — why order used to matter, z = xy on AK(3)

`xy` occurs at position 0 of r1 AND `YX = (xy)⁻¹` at position 3 — two substitutions at once:
r1 → `zxZY`, leaving a single x. Isolate → `x = Zyz`; destabilize r2 → `ZyyyzYYYY` (9),
defining `Zxy` → `ZZyzy` (5); relabel → `(YxxxyXXXX, YYxyx)` — total length 14 vs the
original 13, and empirically the start the greedy likes best on AK(3).

### Worked example C — a word that occurs NOWHERE, z = xyy (universe mode)

`xyy` has no occurrence in AK(3) and no inverse occurrence. Substitution does nothing
(`n_subs = 0`). But the **defining relator** `Zxyy` contains exactly one x — so isolate from
*it*: `x = zYY`. That is just solving `z = x·yy` for x: an **elementary Nielsen automorphism**
of F₂. Rewrite both relators:

- r1 = xyxYXY → `zYzYZY` → relabel → `yXyXYX` (6)
- r2 = xxxYYYY → `(zYY)³YYYY` → relabel → `yXXyXXyXXXXXX` (13)

No occurrence needed, ever. This is the mathematically complete form of "try any w": every
w with exactly one ±x defines a valid re-coordinatisation of the whole presentation.

### Worked example D — eliminating y instead, z = yxx (universe mode)

`yxx` occurs nowhere in AK(3) and carries TWO x — no x-isolation exists even from the
defining relator. But it has exactly **one y**, so isolate y from `Zyxx`: rotate →
`y·xxZ`, ε = +1 → **y = zXX** (the y-Nielsen move y ↦ zx⁻²). Rewrite both relators and
relabel (x stays, z → y):

- r1 = xyxYXY → `xzxZxZ` → relabel → `xyxYxY` (6)
- r2 = xxxYYYY → `xxxxxZxxZxxZxxZ` → relabel → `xxxxxYxxYxxYxxY` (15), cap 31

Without y-elimination this word — and every re-coordinatisation of y — was silently
rejected: literally half the elementary Nielsen moves were missing from universe mode.

## 3. Why it's legal, and how we check it

Stabilize → AC-moves → destabilize is exactly the stable-AC equivalence: the output pair is
stably AC-trivial **iff** the input pair is. So a greedy solve of the transformed pair is a
certificate for the original (the full stable-AC path = CoV bookkeeping + the greedy's moves;
note the greedy's `path_moves` are in *transformed* coordinates).

Checks in force:

- **Abelianization invariant**: |det| of the exponent-sum matrix is preserved at all three
  stages (original 2×2 → intermediate 3×3 → output 2×2). Tested on every candidate on the
  local benchmark rows, including a |det| = 4 example so the test is never a vacuous 1 == 1.
- **No-x assert**: after destabilization no ±x may survive (hard `assert`).
- **Independent replay**: `experiments/stable_ac/verify_results.py` re-runs every solved row's
  path through the pure-Python spec (never the solver). All 750 solved 10k rows verify.

## 4. Rejection gates (what makes a candidate invalid)

A z candidate is rejected when:

| gate                                     | reason                                                                                      |
| ---------------------------------------- | ------------------------------------------------------------------------------------------- |
| `len(w) < 2` after free reduction        | z = x is a rename, not a CoV                                                                 |
| no occurrence AND not universe mode      | substitution mode has nothing to act on                                                      |
| no relator isolates (per target)         | can't eliminate that generator                                                               |
| empty relator after destabilization      | degenerate presentation                                                                      |
| any output relator > `reject_len = 239`  | **structural only**: the packed fast solver caps relators at 255 and a row runs at cap = longest + 16 |

`reject_len` is deliberately NOT a length prior. It used to be 48; that was an empirical
prejudice, and the sweep's own evidence contradicts it — some presentations solve *only*
from long transformed starts (629 at length 33, 539 via z=Xyy). Long starts stay in;
only physics (the 255-relator cap of the fast solver) rejects. Changing `reject_len`
changes the family, so it requires a sweep-tag bump.

**Cap policy**: a cov row runs at `cap = max(24, longest transformed relator + 16)`. The +16
headroom is mandatory — a relator already pinned at the cap can never lengthen over the hump,
so a tight cap silently strangles the search (the repo's ceiling-vs-budget lesson). Control and
baseline rows run at exactly 24 (the ms640 layout). The per-row cap is recorded as
`max_relator_length_cap`; it is derived deterministically from the input, so it stays out of
the filename.

## 5. The three z families (and what killed the first)

1. **zf2** (first-win, `NAIVE_Z_FAMILY`, `change_of_variables`) — every canonical word of
   length 2..4 that survives free and cyclic reduction (62 words), deterministic
   (length, tuple) order, **nothing hand-picked and nothing excluded** — pure powers
   (xx, yyy, …) are candidates like any other word. Supersedes **zf1** (17 hand-picked
   mixed-only words with xy pinned early — z = xy won 65/65 applicable rows, an ordering
   artifact; its exclusions were a prejudice). zf1 files keep their tag; the `mode: cov`
   non-sweep path now writes `cov_..._zf2_...`.
2. **subwords, tag `sub{K}pxy`** — z = every distinct cyclic subword of the presentation's
   own relators, length 2..K (default 4), seam included, `w ~ w⁻¹` deduped to `max(w, w⁻¹)`,
   pure powers included (p), **each z tried eliminating x AND y** (xy). ~18
   starts/presentation on the 66-row benchmark (1,184 total; the x-only sub4p rule
   yields 1,004).
3. **universe, tag `uni{n}xy`** — z = **every** freely reduced (x,y)-word of length 2..n
   (78 canonical words at n = 4), with defining-relator isolation allowed (`iso_index 2`)
   for both targets: x-Nielsen (one ±x) and y-Nielsen (one ±y) moves. 3,615 starts on the
   66-row benchmark — the x-only uni4 rule yields 1,868; the y axis nearly doubles it.

(Counts measured on the current 66-row benchmark — `benchmark_subset_60` + `reach_tier_6`
as regenerated 2026-07-15 with Aut-class-deduped picks.)

**The collapse insight (why universe mode needed new mechanics):** under substitution-only
rules, a fixed universe of all words ≤ n produces *exactly* the same runs as the subword
family — a word can only fire if it occurs in a relator, and "occurs in a relator" *is*
"is a subword". The universe family only becomes a genuinely different experiment because
iso_index 2 lets non-occurring words act as pure Nielsen re-coordinatisations. Shared words
transform identically in both modes (the defining-relator branch is tried last), so
overlapping rows across the two files double as a consistency check.

### What universe mode can — and cannot — reach (one-shot)

The pure-Nielsen branch (iso_index 2) eliminating x accepts exactly the w with **one ±x
letter** — and a freely reduced word with one x-letter is forced into `w = y^a x^±1 y^b`
(a, b ∈ ℤ; w may mix letters — yx, Yxyy — but carries only one letter of the *eliminated*
generator). The substituted expression is correspondingly a power of the kept generator on
each side of exactly one ±z (`test_universe_iso2_expr_is_nielsen_shaped`). Three facts:

1. **Within its slice the gate is complete — a theorem, not a filter.** (y, w) is a free
   basis of F₂ **iff** w = y^a x^±1 y^b: Nielsen moves on the pair {y, w} can only strip
   y-powers off w, a Nielsen-reduced pair is a free basis of the subgroup it generates, and
   that subgroup is all of F₂ only when w reduces to a single x^±1. So "exactly one ±x" is
   precisely the condition for z = w to define a change of variables keeping y — a w with
   two or more x-letters gives no basis, hence no CoV exists there to miss.
2. **One shot is NOT all of Aut(F₂) — not a superset of all CoVs.** Every one-shot output
   basis keeps an original generator: (y, w) or (x, w). A basis containing neither — e.g.
   (xy, xyy), where old y = A⁻¹B and old x = AB⁻¹A — is unreachable in one application,
   and `universe_max_len` truncates the reachable slice further.
3. **Composition closes the gap.** Aut(F₂) = ⟨swap, x ↦ x⁻¹, x ↦ xy⟩ (Nielsen), and each
   generator is ≤ 2 universe moves with |w| = 2: basis (x, xy) is one move (w = xy,
   y-elim); (y, yx) then (u, u⁻¹v) is the swap; (x, xy⁻¹) then (u, u⁻¹v) is (x, y⁻¹).
   Iterated CoV — case (ii), or re-running the sweep on transformed outputs — therefore
   reaches *every* change of variables; one shot cannot.

Mixed words with many x- and y-letters still act — through occurrences (iso_index 0/1).
That isolation consumes a *transformed relator*, i.e. it uses r = 1 in the group: a
stable-AC transformation, not an automorphism of F₂ at all (its expr can even carry two
z-letters — zxZ in the z = xy golden). Universe mode is exactly {subword-fired,
relator-mediated transforms} ∪ {the elementary-Nielsen slice}.

### Degeneracy at the top of the subword range

w = a relator minus one (cyclic) letter shortens that relator to `z·g`, so isolating from
it gives `g = z^±1` — the coordinate change is a pure re-lettering. If that was w's **only**
occurrence, the output is the *original pair* back, up to relator order, rotation and letter
names — a redundant ~control row (it may still run at a wider cap, longest+16 vs 24). But
when w **also fires elsewhere**, the same boundary word does real work: on
`(YYYYYYYXyyyyyyx, YYX)` (pres 496), z = YY compresses 18 letters to 10 by substituting the
relation x = y⁻² into r1. Census on the current benchmark: 16 of 1,184 sub4pxy starts have
`expr = z^±1` — 12 fully trivial, 4 working. With K = 4 only relators of length ≤ 5 produce
them; raising K adds a handful per presentation. Per the empiricism rule none are filtered
(`test_subword_relator_minus_one_boundary`).

## 6. The sweep (experiment_length: true) — one file answers everything

Per presentation, the sweep runs the greedy from **every valid CoV start** plus one **no-CoV
control row** (`z_word: null`, cap 24). Rows are keyed `(pres_id, z_word, iso_gen)` — one z
can contribute both an x- and a y-eliminating start; every row is fsynced on write, so resume
never re-searches a finished row.

Because a search at budget B is exactly the first B pops of any longer search
(budget-invariance), one 50k sweep file yields, **post-hoc, with no new runs**:

- solve rate / nodes / path length at *any* budget ≤ 50k,
- the **argmin-length selector** (greedy from the shortest transformed start),
- **top-k beam** (k shortest starts, cumulative nodes),
- the **oracle** (best start per presentation — the selector ceiling),
- the baseline comparison (the control rows *are* the baseline at the same budget).

### The two production questions

- **Q1 (universe run)**: *is any word shape good in general?* The uni family is identical for
  every presentation, so group rows by `z_word` across the whole benchmark and ask which words
  beat their control repeatedly. `iso_index`/`n_subs` split occurrence-driven shrinking
  (n_subs ≥ 1) from pure re-coordinatisation (iso_index 2, n_subs 0).
- **Q2 (subword run)**: *what length and kind of relator-subset works best?* Rows carry
  `z_word`, `n_subs`, `iso_index`, `r1_orig`/`r2_orig`, `start_total_length_orig/cov` — length
  bins, which relator z came from, and x/y composition are all derivable.

## 7. What we know so far (10k nodes, 66-row benchmark — pre-2026-07-15 subsets, old sub4 family)

| method                  | solved | med. nodes (solved) | med. path (solved) |
| ----------------------- | ------ | ------------------- | ------------------ |
| baseline (no CoV)       | 40/66  | 175                 | 24                 |
| zf1 first-win           | 45/66  | 188                 | 26                 |
| subword argmin-length   | 47/66  | 121                 | 28                 |
| top-6 beam (cumulative) | 48/66  | 143                 | 28                 |
| oracle best start       | 49/66  | 38                  | 21                 |

- **9 presentations solve ONLY via CoV** (568, 583, 588, 603, 605, 610, 633, 634, 635);
  **zero** solve only via baseline. CoV strictly dominates.
- **Depth beats width**: splitting the same total budget over 6 starts (1,666 each) drops to
  38/66 — worse than the plain baseline. Run selectors at full budget.
- **Shorter transformed starts solve more** (≈80% below length 20, ≈20% past 35) — but the
  exceptions are the point: presentation 629's only solving start is z = xy at transformed
  length 33; 539's is z = Xyy. Pure argmin misses them; top-k covers them.
- Oracle-best z words are diverse (XYxy, Xyyy, yyx, Xy, Xyy, xyX, xyy, Xyx …) — no single
  magic word; the *family + selector* is the method.
- Reach tier: 0/6 solved by anything. 25_17 and 25_1 exhausted their whole reachable space
  below budget (672 / 4,891 nodes) — for them the **cap**, not the budget, binds.

## 8. Row schema (jsonl)

Greedy schema (`_build_row`) + cov extras. Every row has `min_relator`, `min_relator_length`,
`max_relator`, `max_relator_length`, `max_relator_expanded`, `max_relator_length_expanded`,
`nodes_explored`, `solved`, `path_length`, `path_moves` (transformed coordinates), plus:

`mode` (cov/baseline) · `z_word` (null = control) · `n_cov` · `cov_applicable` · `iso_index`
(0/1/2, §2) · `iso_gen` (x/y — which generator the destabilization eliminated; null = control)
· `n_subs` · `r1_orig`/`r2_orig` · `start_total_length_orig` / `start_total_length_cov` ·
`max_relator_length_cap` · `source` (which CSV) · `git_commit` (provenance only, never
identity).

**Filename = resume identity** (date-less prefix; every result-changing knob, nothing else):
`covsweep_{budget}_{n}_{fam}_mrl24_cyc_{tag}_` with fam ∈ {`sub4pxy`, `uni4xy`} — plus
`cov_...` (zf2) and `covbase_...` (identity transform) for the non-sweep modes. Older family
rules (`sub4`, `sub4p`, `uni4`, `zf1`) keep their tags and never share a resume file.

## 9. Running it

Local proof (≤ 1000 nodes — the repo hard cap):

```bash
.venv/bin/python3 -m pytest experiments/stable_ac -q            # 58 tests
.venv/bin/python3 -m experiments.stable_ac.cov.run_cov \
    --experiment-length --budget 100 1000                       # subword sweep, 11 rows
.venv/bin/python3 -m experiments.stable_ac.cov.run_cov \
    --experiment-length --z-source universe --budget 100 1000   # universe sweep
```

**high_speedup** (yaml: on in production, off in `COV_DEFAULTS`; CLI `--high-speedup`):
routes every search through `run_baseline`'s compact fast solver — same pop order, and a
solved search is re-solved by the normal solver so the written row is identical (0
contractual mismatches over 420 row pairs; only the min/max relator display strings can
differ, the documented set-tiebreak). Measured **2.9×** wall on the 11-row double-budget
sweep locally; bigger budgets amortize the JIT warm-up further. Result-neutral → outside
the filename identity, so files written in either mode resume each other — flipping the
knob mid-campaign is safe.

Production (Colab, `cov_baseline.ipynb` — re-open from GitHub after any push; edit only the
CONFIG cell). Both runs: `BUDGET = [50000]`, `MODE = "cov"`, `EXPERIMENT_LENGTH = True`,
`DATASETS = [".../benchmark_subset_60.csv", ".../reach_tier_6.csv"]`.

|            | Colab A (Q2)                   | Colab B (Q1)                                      |
| ---------- | ------------------------------ | ------------------------------------------------- |
| `Z_SOURCE` | `None` (subwords)              | `"universe"`                                      |
| file       | `covsweep_50000_66_sub4pxy_...`| `covsweep_50000_66_uni4xy_...`                    |
| rows       | 1,184 starts + 66 controls     | 3,615 starts (1,747 y-eliminating) + 66 controls  |
| est. time  | ~2–3 h (fast solver)           | ~6–9 h (fast solver; may need one resume)         |

Resume is per-row: on disconnect, rerun the RUN cell — it skips every finished
`(pres_id, z_word, iso_gen)`. The jsonl lives in the ephemeral `/content` clone, so
periodically copy it to Drive and copy it back before resuming on a fresh VM. Verify before
believing numbers:

```bash
.venv/bin/python3 -m experiments.stable_ac.verify_results results/stable_ac/cov
```

## 10. Known limitations / next rungs

- **Linear-scan substitution** misses seam-straddling occurrences (sound, weaker).
- **One-shot (case i)**: CoV happens once, before the search. Case (ii) — CoV as a move
  *during* search — is the larger design this schema (`n_cov`) anticipates.
- **Selector not shipped**: argmin-length / top-k are post-hoc derivations today; once the 50k
  sweeps pick the winner, it becomes a `selector:` production mode.
- **Path lengths are transformed-coordinates**: comparing `path_length` against baseline rows
  ignores the constant CoV move overhead of a full stable-AC certificate.
- W&B mirroring is deferred until the production selector exists (jsonl is source of truth).
