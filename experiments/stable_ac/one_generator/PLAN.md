# Stable AC — One-Generator Change-of-Variables Pipeline (`z = w(x,y)`)

## Context

**What & why.** Lucas's Stable-AC direction, greedy first: take a balanced 2-generator
presentation `⟨x,y | r1, r2⟩` and *stabilize* it by adding a generator `z` **defined as a
word** `z = w(x,y)` → `⟨x,y,z | r1, r2, z·w⁻¹⟩`, then solve with our existing greedy search.
The scientific question: **does naming a well-chosen word `w` as a new generator open
trivialization paths the 2-generator search can't reach?** We benchmark on **MS(1190)**
(`data/1190MS.txt`, 1190 lines). Sources:
`literature/txt/change_of_variables_stable_ac.txt`,
`literature/txt/mentor_email_stable_ac_ideas.md`, and Lucas's 2026-07-02 follow-up (below).

**Mentor's decision (2026-07-02) — this plan implements it.**

- **Skip trivial `z`.** A *trivial* stabilizer (`z = 1`) is a confirmed dead end for greedy
  (see the caveat below) — so we go straight to `z = w(x,y)`.
- **Start with the dumbest words**, not clever ones. **Primary arms: `w ∈ {x, y, r1, r2}`**
  (`x⁻¹/y⁻¹` skipped as mere orientation flips of `z=x`/`z=y`). Mentor also named `r1⁻¹/r2⁻¹`;
  we keep them as **optional confirmatory arms**, run last, because they are provably
  *isomorphic* to `z=r1`/`z=r2` (see the note below) and so add no new coverage/path-length
  signal — only heap tie-break noise. Build the *pipeline* first; searching for the *best* `w`
  (the real research) is the next plan.

  **Why `r1⁻¹/r2⁻¹` are redundant (same argument that skips `x⁻¹/y⁻¹`).** The relabeling
  `z ↦ z⁻¹` is an automorphism fixing `x,y`. It maps the `z=r1` z-relator `z·r1⁻¹` to
  `z⁻¹·r1⁻¹ = (r1·z)⁻¹`, which — since relators are canonicalized up to inversion **and** cyclic
  rotation — is the same relator as `z·r1`, i.e. exactly the `z=r1⁻¹` arm. `r1,r2` are untouched
  (no `z` in them) and every operation is equivariant (substitution, free/cyclic reduction, the
  already-inversion-invariant `canonical_relator_nj`, the length priority, the blocked state), so
  the two searches are isomorphic: identical solved/unsolved and identical path lengths, differing
  only in heapq tie-break order. Running both burns ~33% of the arm compute measuring tie-break
  noise. *(Flagged for the mentor — the primary run is the 4-word set; the two inverse arms are
  a cheap confirmatory add-on, not a headline arm.)*
- **Block the null revert.** With `z = w`, greedy is tempted to unwind `z` straight back to
  `z = 1` (length-reducing). We prevent *that specific collapse* by pre-seeding the solver's
  visited/closed set with the single canonical state `(r1, r2, z=1)` — the original
  presentation with `z` thrown away. **Narrow by design:** a broad "block every `z=1` state"
  would also forbid legitimate **destabilization** (removing `z` *after* it has done work),
  which is the endgame we want reachable. The solved presentation also has a `z`-relator of
  `z`, but its `r1,r2` are reduced to single letters, so it can never equal the blocked state.
- **Two headline metrics, per presentation:** (1) **path length** (moves to trivialize) and
  (2) **node usage** (nodes explored) — tracked for the 2-gen baseline and every `z=w` arm.
- **Why later:** Lemma 11 lets us realize a `z = w(x,y)` worth *hundreds* of AC moves in one
  shot (Lucas's "wormhole") — but the moves to realize it aren't obvious. This plan is the
  on-ramp: simple `w`, measured, before complex `w`.

**Why `z = r1` is non-vacuous (not the trivial z we discarded).** `z = r1` is *group*-trivial
(`r1 = 1`, so `z = 1` in the group) — but the **word-level** z-relator `z·r1⁻¹` shares all of
r1's letters with r1/r2, so substitution can swap the whole word `r1 ↔ z`, a move the
2-generator presentation doesn't have. `z = x` / `z = y` likewise hand the search a named
single-generator alias. The content is in the *word*, not the group.

**Scope.** Greedy + categorization only; the RL/beam-on-3-generators path stays deferred to
**Phase 4** (large subproject — technical reasons there). Greedy (`greedy_search.ipynb`,
GS-Sub) is standalone numpy+numba (no JAX/env/checkpoint) — the fastest route to a real
signal.

**Caveat this plan is built around — why trivial `z` was dropped.** A substitution only fires
when the boundary letters cancel (last letter of one rotation = inverse of the first of the
other — Def 2.1). A *trivial* `z` (relator `z`, `z=1`) shares no letters with r1/r2, so
`get_neighbors` returns **nothing** for any `(r_i, z)` pair and `⟨x,y,z | r1,r2,z⟩` searches
identically to `⟨x,y | r1,r2⟩`. Seeding it back in doesn't rescue it: multiplication
`r_i→r_i·z` is immediately trimmed by length-greedy, and conjugation `z·r_i·z⁻¹` is a **cyclic
no-op** (relators are cyclic and `reduce_relator_nj` cancels `z…z⁻¹` at the seam). The only
fix is to give `z` **content** — i.e. `z = w(x,y)`, where the z-relator `z·w⁻¹` shares x/y
letters with r1/r2 so ordinary substitution swaps `w ↔ z` directly. That is exactly this
plan; **no seeding moves are needed.** (Phase 2 pre-flight keeps a one-line empirical
confirmation that `get_neighbors(r1, trivial-z)` is empty and that `get_neighbors(r1, z=w)` is
not.)

---



## Deliverable layout (all under `experiments/stable_ac/one_generator/`)

```
PLAN.md            # this document
stabilize.py       # z = w(x,y) stabilization (2-gen → 3-gen) + dataset writer, one file per w
jsonl_io.py        # crash-safe resumable JSONL helpers (jsonl_done_ids, jsonl_append) — see CLAUDE.md
greedy_nrel.py     # n-relator greedy solver (generalized from greedy_search.ipynb) + visited-block
calibrate.py       # Phase 2.5: measure nodes/sec on hard/easy probes → project runtime, pick budgets
categorize.py      # Phase 0/0.5: index-only labels skeleton (.json) + our greedy stream (.jsonl, resumable)
run_experiment.py  # driver: 2-gen baseline vs each z=w arm, writes one resumable .jsonl per arm, logs to W&B
viz.py             # matplotlib/W&B plots (reads the .jsonl streams + labels)
results/           # *.jsonl result streams + *.json labels + *.png plots (git-tracked; small)
README.md          # exact commands to reproduce
```

Encoding convention used throughout the new code = **the env's signed-int convention**
(`x→1, y→2, z→3, x⁻¹→-1, y⁻¹→-2, z⁻¹→-3, 0=pad`). This unifies the greedy code with
`data/*.txt` and lets us load MS(1190) directly and (later) cross-check against the JAX env.

**Result persistence (crash-safe, resumable — a project convention; see `CLAUDE.md`).** Every
per-presentation sweep here (Phase 0.5 baseline, each Phase 3 `z=w` arm) writes an
**append-only `.jsonl`** — one JSON object per presentation, flushed per line — and **resumes
from the last object**: on restart it reads the stream, skips already-done `idx`, and continues.
A pre-empted or crashed cloud job then never loses finished work or recomputes it. Tiny helpers
`jsonl_done_ids(path)` / `jsonl_append(path, obj)` live in `jsonl_io.py`, reused by every sweep.
Only fully index-derived artifacts (the `paper_reference` labels) stay `.json`.

**One stream per `(arm, node-budget)` — the resume key must be unambiguous.** Because we run a
budget escalation (a cheap first pass, then a larger budget on the still-unsolved), a stream keyed
on `idx` **alone** cannot tell "unsolved at 100k" from "solved at 1M" — on resume the escalation
pass would either no-op or write duplicate `idx` lines that the merge then has to disambiguate.
So each sweep writes a **separate file per budget tier**: `…_100k.jsonl` and `…_1m.jsonl`, and the
larger-budget pass enumerates **only the `idx` left unsolved by the smaller** (which also avoids
re-solving the easy cases). The merge at report time keeps "which budget solved it" for free.
Exact budget numbers are set by the Phase 2.5 empirical calibration, not guessed.

---



## Phase 0 — Categorization: per-presentation reference labels over MS(1190) (no stabilization)

Goal: per-presentation labels over all 1190, captured **before** any stabilization so
stabilization deltas are measurable — split by persistence need:

- **`results/labels_1190.json`** — the cheap, fully index-derived skeleton (one object per
  presentation: `idx, presentation, r1_len, r2_len, ms_n, ms_w, paper_reference`). Rebuildable
  in one pass, so plain JSON is fine.
- **`results/greedy_reprogate_{100k,1m}.jsonl`** — the n=2 **reproduction/port gate** (Phase 0.5),
  run under the notebook's **sum-cap** to reproduce the paper's 634/640 and the idx-640 boundary.
- **`results/greedy_baseline_{100k,1m}.jsonl`** — the n=2 **cross-arm baseline** (Phase 0.5), run
  under the **per-relator cap** — the *same* cap the n=3 `z=w` arms use, so Phase 3 baseline-vs-arm
  deltas aren't a cap artifact. Both are append-only, resumable, one line per `idx` per budget tier.

Methods stay in **separate fields/streams** (their coverage differs); the paper's *claim* and
our *measurement* are kept apart so any discrepancy is visible, not baked in.

**Cross-verified label semantics (this session).** The mentor's "first ~640 of
`AC19_extended.txt` are solved by the greedy DRT" checks out; the exact numbers are pinned to
paper Table 1 + text:

- **GS-Sub greedy** — numba, *not* the DRT policy (the RL/DRT max is 610, so "greedy DRT" =
  GS-Sub) — solves **634 @ 100K nodes** and **640 @ 1M / 10M nodes**. `1190 − 640 = 550`
  unsolved (matches the paper's "550 remaining unsolved").
- `1190MS.txt` is ordered **solved-first**: idx `0–639` = the paper's greedy-trivializable
  ("AC-trivial") set, idx `640–1189` = the 550 unsolved. (Paper: *"the first 640 environments
  are reserved for the 640 MS presentations… we never solved any presentation outside the
  initial 640."*)
- `AC19_extended.txt` (156,762 lines — the RL **training** set, *not* the benchmark) leads
  with **634** lines byte-identical to `1190MS[0:634]` (verified: exact shared prefix = 634,
  diverges at line 635). These are the *100K-node* greedy solves used as RL training seeds;
  the 6 extra (idx 634–639) trivialize only at ≥1M nodes, which is why they are not in the
  shared prefix.
- The pretrained **610model** solves **610** of the 640; never outside the 640.

**Merged view** (assembled at report time from `labels_1190.json` + the `.jsonl` streams) —
each presentation looks like:

```jsonc
{
  "idx": 0,                                  // ── from labels_1190.json (skeleton) ──
  "presentation": [ /* 48 ints, the env flat encoding */ ],
  "r1_len": 5, "r2_len": 2,
  "ms_n": 1, "ms_w": "yX",                 // MS(n,w) params recovered from r1/r2 when parseable, else null
  "paper_reference": {                       // the paper's CLAIM (no compute; from ordering + Table 1)
    "solved": true,                          //   idx < 640
    "source": "GS-Sub greedy (paper Table 1: 634@100K, 640@1M/10M)",
    "in_ac19_extended_prefix": true          //   idx < 634 (the 100K-node solves used as RL training seeds)
  },
  "greedy":       { /* our MEASUREMENT — joined from greedy_baseline_*.jsonl, else null */ },
  "rl_610model":  null,                      // { "solved": bool, "path_len": int } when JAX + checkpoint present
  "beam_610model": null                      // { "solved": bool, "path_len": int } when beam is run (optional)
}
```

Label sources:

1. **Paper reference (all 1190, no compute).** Fill `paper_reference` purely from index
   (`solved = idx<640`, `in_ac19_extended_prefix = idx<634`) using the cross-verified ordering
   above. This is the "solved/unsolved in the paper" label the task asks for. Nothing
   downstream may treat it as ground truth without the empirical `greedy` field alongside it.
2. **RL (pretrained), first 634 — gated on JAX.** Read `610model`'s
   `solve_data.solved_idx`/`path_lengths` (its first 634 entries index `1190MS[0:634]`); fill
   `rl_610model`. Reuse the exact Orbax two-stage restore in
   `scripts/check_checkpoint_paths.py` / `beam/beam_search.py:90-123`. **This env has no JAX** —
   `categorize.py` skips this gracefully (leaves `rl_610model: null`); run it later where the
   training stack lives.
3. **Beam (pretrained), all 1190 — optional, gated on JAX.** Run existing
   `python beam/beam_search.py --ckpt_path 610model --dataset 1190MS --start 0 --end 1190 --training_dataset AC19_extended --out_csv results/beam_1190.csv`;
   merge `solved`/`path_len` into `beam_610model`. Label idx ≥ 640 as clearly
   out-of-distribution. No code change — shipped pipeline.

No env/network changes in this phase.

---



## Phase 0.5 — Our own greedy run (GS-Sub, numba/CPU — runnable in this environment)

The task's "quick run ourselves … using numba on the CPU … path length until trivialization,
time taken, nodes explored." This fills the `greedy` field of the JSON and **empirically
verifies** the mentor's claim + benchmark ordering (rather than only inferring them from the
paper). numpy 2.0.2 + numba 0.60.0 are present here (JAX is not), so this phase runs now.

`categorize.py --greedy` runs `greedy_nrel.py` (Phase 2, `n_gen=2`) over every line of
`data/1190MS.txt`. **It does two `n=2` sweeps under two different length caps** — cheap, since
`n=2` is the fast case — because one run can't serve both purposes:

1. **Reproduction/port gate → `results/greedy_reprogate_{100k,1m}.jsonl`, notebook `sum-cap`.**
   GS-Sub *is* this notebook, which caps on the **sum** of relator lengths, so we reproduce the
   paper apples-to-apples under the sum-cap: a deviation from 634/640 then means "port bug," not
   "cap-semantics difference."
2. **Cross-arm baseline → `results/greedy_baseline_{100k,1m}.jsonl`, `per-relator` cap.** The
   baseline that Phase 3 compares the `z=w` arms against, run under the **same per-relator cap the
   n=3 arms use** (Phase 2/3) — so a baseline-vs-arm coverage delta reflects stabilization, not a
   cap that carves a different `(r1,r2)` region for `n=2` vs `n=3`.

Both are append-only and resumable (skip any `idx` already in *that* stream); each line:

```jsonc
{ "idx": 0, "solved": true, "nodes_explored": 812, "path_len": 13,
  "wall_time_s": 0.04, "max_len_along_path": 21, "budget_nodes": 100000, "cap": "sum" }
```

Budget escalation for **each** stream (numbers fixed by the Phase 2.5 calibration, not guessed;
nominally `max_nodes ∈ {100k, 1M}`): run the small budget over all 1190 → `…_100k.jsonl`, then the
large budget **only over the `idx` still unsolved** → `…_1m.jsonl` (the 6 idx-634–639 cases are
expected to appear at 1M). The `cap` field records which rule was in force. The validation gate
below reads the **`reprogate`** streams (paper comparison); Phase 3 reads the **`baseline`** streams.

**Validation gate (directional — this is the real signal):**

- **HARD-with-triage:** a greedy *solve at `idx ≥ 640`* is **quarantined, not auto-fatal**.
  **Replay the returned path** (free+cyclic-reduce each step; assert it ends all-relators-length-1
  — the Phase 3 re-verification machinery). **Replay passes → keep it as a genuine new solve** and
  log it (our tie-breaks/caps differ from the paper's, so a real extra solve is a small research
  finding, not automatically an ordering bug); note that `paper_reference.solved = idx<640` is the
  paper's *claim*, and our measurement is allowed to disagree. **Replay fails → it's a solver bug:
  stop and fix.** Only an *irreproducible* solve invalidates the ordering assumption.
- **SOFT:** solved count ≈ **634 @100K** and ≈ **640 @1M**, essentially all within idx < 640. Our
  numba GS-Sub may differ from the paper's by a few (tie-break/budget details) — **log deviations,
  don't assert exact equality.**

Passing this gate simultaneously (a) confirms the mentor's claim, (b) confirms the
benchmark's solved-first ordering, and (c) validates `greedy_nrel.py` at `n=2` before it is
trusted at `n=3` in Phase 3.

---



## Phase 1 — `z = w(x,y)` stabilization transform + stabilized datasets

`stabilize.py`:

- `stabilize_flat(flat, z_word, old_n_gen=2, new_n_gen=3, max_length=24)` — reshape the flat
presentation into `old_n_gen` relators and append one new relator encoding `z = z_word`: the
z-relator = `[k] ++ inverse(z_word)` (`k` = new generator id, e.g. `z=3`), free+cyclically
reduced, then padded to `max_length`; re-flatten to `new_n_gen*max_length`. `z_word` is a list
of ints over x/y (`±1,±2`). Examples: `z = r1` → z-relator `[3] ++ inverse(r1)` (length
`1+|r1|`); `z = x` → `[3,-1]` (length 2). So `[r1|r2]` (len 48) → `[r1|r2|z·w⁻¹]` (len 72).
- **Preset baseline words: primary `w ∈ {x, y, r1, r2}`** (`x⁻¹/y⁻¹` skipped as orientation
flips), plus **optional confirmatory `w ∈ {r1⁻¹, r2⁻¹}`** (isomorphic to `r1/r2` — Context note —
so generated but run last, if at all): `x/y` are constant, `r1/r2` read per-line from the
presentation. Across MS(1190) `max|r1|=17, max|r2|=15` ⇒ every z-relator is ≤ 18 ≤ `L=24`, so
**`L=24` holds for all baseline words — no bump needed.**
- `write_stabilized_dataset(in_stem, z_spec, out_stem, ...)` — read `data/<in_stem>.txt`,
stabilize each line with `z_spec`, write `data/<out_stem>.txt` (same
one-Python-literal-list-per-line format). Produces **one file per word**: primary
`data/1190MS_z_{x,y,r1,r2}.txt` and optional `data/1190MS_z_{r1inv,r2inv}.txt` (1190 lines,
length-72 each).
- Converters `flat_to_relators(flat, n_gen, L)` ↔ `relators_to_flat(rels, n_gen, L)` so the
greedy (list-of-relators) and env (flat) formats interoperate — **n-relator-generic** (no
`//2`), mirroring the intent of `envs/utils.py::change_max_relator_length_of_presentation`.

Validation: every stabilized line has `new_n_gen*max_length` entries; the r1/r2 prefixes are
unchanged; the z-relator **decodes back to `z = z_word`** (drop the leading `z`, invert ⇒
`z_word` up to cyclic reduction); round-trip `flat_to_relators`↔`relators_to_flat` is identity.

---



## Phase 2 — n-relator greedy solver (reuse + generalize the notebook)

`greedy_nrel.py` extracts the **algorithms** from `greedy_search.ipynb` and generalizes
them from "2 bool-encoded relators" to "a tuple of `n` int-encoded relators." Reused, only
re-typed to int arrays: Booth minimal rotation (`find_minimal_rotation`), free+cyclic
reduction (`reduce_relator_nj`), inversion (`inverse_relator_nj`), canonicalization
(`canonical_relator_nj`).

> **⚠ PORTING TRAP (silent-correctness — fix first, test explicitly).** The notebook's
> rotation is `np.roll(r, 2*i)`: it rolls by **`2*i`** because each letter is a `(bool, bool)`
> *pair*, so one logical letter is two array slots. The int port stores **one slot per letter**,
> so it must roll by **`i`**, not `2*i`. Miss this and *every* rotation — hence every
> substitution neighbor and every canonicalization — is silently wrong while superficial tests
> still pass (the search just explores garbage). This is the one feedback item that corrupts
> results rather than degrading them gracefully. Pre-flight check 0 (below) asserts a known
> rotation produces the exact expected array before anything else runs.

Generalized:

- **Letter encoding:** int (`±1..±n_gen`) instead of `[bool,bool]` — the bool scheme's 1
identity bit cannot name a 3rd generator. `is_inverse/is_equal/is_less_than` become
trivial int ops (`a==-b`, `a==b`, `abs`/sign order).
- **State:** `tuple` of `n` relators (was 2-tuple). `state_to_key`, `_key_to_state`,
`canonical_pair_nj` → `canonical_tuple` (canonicalize each relator, then sort the tuple
by (len, lex)).
- `get_neighbors` (the substitution move, n-relator): for **every ordered pair (a, b),
a≠b**, each candidate `c ∈ {r_b, r_b⁻¹}`, and each cyclic rotation of `r_a` and `c`, if the
boundary letters cancel, form `neighbour = concat(rot(r_a), rot(c))` and emit the state with
relator `a` replaced. (The 2-relator notebook version is the `n=2` special case.) **With a
content-bearing `z` (relator `z·w⁻¹`), `(r_i, z)` pairs cancel normally** — the z-relator
carries `w`'s x/y letters — so substitution acts on `z` directly. **No seeding moves are
needed** (they were only a workaround for trivial `z`, which we no longer use).
  - **Cheap hot-loop optimization (do this in the port):** the notebook materializes an
  `np.roll` copy + concat + reduce for *every* rotation pair before testing cancellation. Instead
  **read the two boundary letters directly** (two indexed lookups per rotation pair — the last of
  `rot(r_a)` and the first of `rot(c)`) and only build `concat+reduce` for pairs that actually
  cancel. Cancellation is sparse, so this is an order-of-magnitude constant-factor win — and it
  matters: `n=3` has **6 ordered relator pairs vs `n=2`'s 2**, so per-node neighbor work is the
  dominant cost of the whole sweep (see Phase 2.5).
- **Visited-block (mentor's null-revert guard):** `NRelatorSolver(..., blocked_states=None)`
pre-seeds the closed/visited set with canonical state-keys that are never enqueued/expanded.
For a `z=w` run we pass the **single** null-revert state `canon(r1, r2, [z])` — the original
presentation with `z` collapsed to `z=1` — **canonicalized in the solver's own canonical form**
(sort + Booth + cyclic-reduce) so the key actually matches. This stops greedy from unwinding
`z` straight back to nothing, while leaving genuine destabilizations (progressed `r1',r2'` with
`z` removed) reachable.
- **Trivial check:** `all(len(r)==1 for r in relators)` (generalizes `len(r1)==1 and len(r2)==1`; matches the env's `count_nonzero == n_gen`).
- `NRelatorSolver` class mirroring `ACRelatorSolver`: heapq best-first on total relator length
(the paper's GS default), `max_nodes`, `visited` parent-dict for path reconstruction, plus the
`blocked_states` above. Returns `(path, nodes_visited, seen)` and records **path length** and
**node usage** — the two headline metrics. (An optional `"length_tolerant"` priority remains
available but isn't required: `z=w` is content-bearing, so there's no length-increasing seed to
protect.)
- **Length cap = *per-relator*, not sum (removes an `n=2`-vs-`n=3` confound).** Cap each relator
individually at `max_len` (mirrors the env's `L=24` semantics), the **same value for every relator
in every arm**. A shared *sum*-cap would let the z-relator (up to 18 letters for `z=r1`) eat the
headroom for `r1,r2`, so the `n=3` arm would search a strictly *smaller* `(r1,r2)` subspace than
the `n=2` baseline and any "coverage regression" would be a cap artifact, not a stabilization
effect. A per-relator cap makes the `(r1,r2)` subspace identical across baseline and arms by
construction. State the rule once in the `greedy_nrel.py` docstring; record the cap per JSONL line.
*(The `n=2` reproduction gate in Phase 0.5 deliberately uses the notebook's native sum-cap instead
— that's port-validation, not cross-arm comparison; see Phase 0.5.)*
- **Scale/memory notes (implementation, tagged so they don't balloon the spec):** at the 1M-node,
`n=3` regime the generated-state set is the memory bottleneck. Key `visited` on compact **`bytes`**
(int8 relators joined by a separator), not Python string-tuples (~4× smaller, hashes faster); and
**drop `new_seen`** from the sweep path (it only feeds post-hoc "minimal element" prints — a second
full copy of the state set). Log **peak RSS** per JSONL line so the 1M runs are observable and a
cloud box OOMs visibly, not mysteriously.

Pre-flight (advisor's + our own CLAUDE.md rule) **before any 1190 sweep**:

0. **Rotation is correct (the porting trap):** assert `rotate(r, i)` on a hand-built relator
  produces the exact expected array for a few `i` — this is the guard against the `np.roll(2*i)`
  vs `np.roll(i)` bug above. Nothing else is trustworthy until this passes.
1. `n=2` on a known-solvable MS presentation (e.g. `MS(3,'YXyxy')` region) → solves,
  matching the notebook.
2. Stabilize that same presentation with `z=x` → `n=3` solve must **still succeed** (a solvable
  presentation stays solvable — `z` can be ignored or destabilized). Assert the returned path
  replays to all-relators-length-1.
3. **z fires when content-bearing / empty when trivial:** confirm `get_neighbors` emits
  neighbors for `(r1, z)` with `z=w`, and **nothing** for `(r1, z)` with a trivial `z` (the
  empirical confirmation of the caveat).
4. **Block holds — including the 2-step revert.** With the null-revert state pre-seeded, confirm
  the search never expands `canon(r1, r2, z=1)` and cannot settle there. Assert **specifically the
  2-step revert path** `(r1, r2, z·r1⁻¹) → ([z], r2, z·r1⁻¹) → ([z], r2, r1⁻¹)` is caught: because
  `canonical_relator_nj` is inversion-invariant and the tuple is sorted, that final state
  canonicalizes to *exactly* the blocked key — so a single blocked state stops both the direct
  1-step unwind and this 2-step one. (This robustness is a feature; the pre-flight must prove it,
  not assume it.)

---



## Phase 2.5 — Empirical timing calibration & budget selection (do this before the full sweeps)

**Don't guess the node budget or the total runtime — measure them.** A back-of-envelope from the
notebook (~10k nodes / 1.9 s single-core, `n=2`) already implies the full sweep is CPU-*weeks*:
`100k / (10k/1.9s) ≈ 19 s` × 550 unsolved ≈ **3 h per arm** at 100k, ~**29 h per arm** at 1M,
times ~5 arms — and `n=3` is slower still (6 ordered relator pairs vs 2 → more neighbors per node).
So before committing, `calibrate.py` runs a small probe and turns it into a real estimate.

**What to measure — throughput on the *hard* cases, not "time to solve."** Runtime is dominated by
the ~550 **unsolved** presentations: each runs to the **full node budget** (that's what "unsolved"
means), so the reusable quantity is **nodes/sec**, measured on a *budget-exhausting* case, on the
**`n=3` code path** (not the notebook's `n=2` number). Concretely:

1. **Warm up numba first** — one throwaway solve so JIT-compile time doesn't land inside the first
   measurement (it's visible as the notebook's inflated first cell). Keep dtypes fixed (int8) so
   there are no silent recompiles mid-probe.
2. **Hard sample (~5, drives the estimate):** 5 *unsolved* presentations (idx ≥ 640), stabilized
   (`z=r1`, the representative content-bearing arm), each run to the **candidate max budget**.
   Record wall-time and `nodes/sec`. Runtime floor ≈ `median nodes/sec` → `budget × #unsolved ÷
   nodes/sec` per arm.
3. **Easy sample (~5, minor addend):** 5 *solved* presentations sampled across the difficulty range
   (early/low-idx and near-640) → the cheap solved-case time. Small next to (2), but confirms the
   easy tail is negligible.
4. **Output** → `results/calibration.jsonl` (one line per probe: `idx, arm, n_gen, budget_nodes,
   nodes_explored, solved, wall_time_s, nodes_per_sec, peak_rss_mb`) + a short printed summary:
   projected per-arm hours at each candidate budget, and the total across all arms/tiers.

**Then choose** the `{small, large}` budget tiers (the `100k / 1M` nominal, adjusted to whatever
the probe says is affordable) and **whether to parallelize**: the per-idx JSONL streams are already
shard-safe, so `multiprocessing` across presentations is the obvious lever if the single-core
estimate is too slow (record the worker count). The chosen budgets feed Phase 0.5 and Phase 3.

---



## Phase 3 — Experiment, W&B, plots

`run_experiment.py` runs the **2-gen baseline plus one arm per `z=w` word** over MS(1190).
**Each `(arm, budget-tier)` writes its own append-only, resumable `.jsonl`** —
`results/greedy_baseline_{100k,1m}.jsonl` (reused from Phase 0.5) and
`results/greedy_z_<w>_{100k,1m}.jsonl` per word — one line per presentation, skipping any `idx`
already recorded (a pre-empted cloud run resumes cleanly), and the large-budget tier enumerating
only the `idx` the small tier left unsolved. `viz.py` / the report step merges the streams by
`idx`, preferring the tier that solved it.

- **Baseline: 2-gen greedy** (`n=2`, `data/1190MS.txt`) — = the **per-relator-capped**
  `greedy_baseline_*.jsonl` from Phase 0.5 (**not** the sum-capped `greedy_reprogate_*.jsonl`),
  so baseline and arms share the identical per-relator cap and the delta is stabilization, not caps.
- **Primary `z=w` arms** (`n=3`), one per `w ∈ {x, y, r1, r2}`, each on its `data/1190MS_z_<w>.txt`,
  with the null-revert visited-block on → `results/greedy_z_<w>_*.jsonl`. **Optional confirmatory
  arms** `w ∈ {r1⁻¹, r2⁻¹}` run last only if desired (isomorphic to `r1/r2` — Context note).
- **Two headline metrics per presentation, per arm:** **path length** (moves to trivialize)
  and **node usage** (nodes explored). Each line also carries `solved`, `wall_time_s`,
  `max_len_along_path`, `peak_rss_mb`, and the budget tier that solved it.
- **Path-length convention (pin one rule, cross-arm plots depend on it):** a `z=w` arm's
  `path_len` is the **search path only**, and does **not** count the implicit `+1` stabilization
  move (the search starts from the already-stabilized presentation). State it once; apply it to
  every arm so baseline-vs-arm path-length deltas are comparable.
- Budget tiers from Phase 2.5 (nominal `max_nodes ∈ {100k, 1M}`); **per-relator** `max_len` cap
  (same value every relator every arm — Phase 2), all logged so there are no silent caps.

**Pre-registered expectation — `z∈{x,y}` will look worse, and that's an artifact, not a verdict.**
With z-relator `z·x⁻¹`, swapping any single `x ↔ z` in `r1/r2` is **length-neutral**. Best-first on
total length exhausts each length level before growing, so `z∈{x,y}` arms will enumerate large
chunks of the `~2^(#x-occurrences)` alias orbit *at the initial length* before making progress —
inflating node usage and producing budget-exhaustion "regressions" that measure alias blowup, **not**
stabilization being bad. **We pre-register this:** interpret `z∈{x,y}` coverage regressions as
budget artifacts unless replay says otherwise. Corollary: **`z=r1`/`z=r2` are the arms where a real
"wormhole" signal is most likely visible** (their swaps are whole-word, not length-neutral aliases).
Optionally report a per-arm "distinct states modulo `z↦x` relabel" diagnostic to quantify the orbit.

Headline comparisons:

- **Coverage:** does any `z=w` arm solve MS presentations the 2-gen baseline can't (especially
  among the 550 unsolved)? Any regressions (baseline solved, `z=w` not, within budget)? — every
  new solve **replay-verified** to all-length-1 (Phase 0.5 machinery) before it's counted.
- **Efficiency:** for presentations both solve, does `z=w` cut **path length** or **node
  usage** vs baseline? (The "wormhole" hypothesis in miniature — even a dumb `w` might shorten
  paths.)

**W&B** (`--wandb`, project `stable-ac-onegen`, reusing the lazy-import + gated pattern from
`ppo_ac_s.py:362-371`): per-arm scalars centered on the two metrics — solved count, mean/median
**path length**, mean/median **node usage**, new-solves-vs-baseline, regressions — plus plots +
JSON uploaded as artifacts. Entity = user default (CLI-overridable); `--wandb_mode offline` ok.

`viz.py` (guided by the `dataviz` skill) produces, to `results/*.png` and W&B:

1. **Solved-count bar** — baseline vs each `z=w` (vs RL 610model within the 640-set).
2. **Node-usage distribution** — baseline vs `z=w` arms (log-scale, mirrors the paper's
  two-hump difficulty figure).
3. **Path-length distribution** — baseline vs `z=w` arms.
4. **Per-presentation scatter** — baseline vs `z=w` on node usage and on path length (points
  below the diagonal = `z=w` faster/shorter; new solves highlighted).

---



## Phase 4 — RL / beam on 3 generators (SPECIFIED, DEFERRED — do not execute now)

**Why this path is deferred, not cheap.** Exploration confirmed the whole RL stack is
hard-wired to exactly 2 relators, in a way `n_gen` alone does not fix:

- `envs/ac_moves.py::s_move` (lines 229–274) always sources relators **0 and 1**
  (`_invert(1,…)`, `rotate_relator_k(0,…)`/`(1,…)`, `_concatenate(0,1,…)`) and writes to a
  **binary** target (`lax.cond(i==0, slot 0, slot max_length)`). For `i=2` it silently
  corrupts relator 1.
- Action packing `(((k1-1)*L + (k2+j)*(-1)**j)*4) + (i*2+j)` bakes `i,j∈{0,1}` via the
  literal `*4` — duplicated in `envs/utils.py:78-96`, `wrappers.py:214-216`, `ppo_ac_s.py`,
  `beam/beam_search.py:181-188`.
- `network.py::RelativeDualRingActorCritic` is a **structural 2-relator "dual ring"**:
  `L_half=L//2` binary split, `vocab_size=5` (=`2·2+1`), pairwise cross-attention, and a
  4-way `(i,j)` action head — a 3-generator input needs vocab 7 and a tri-ring redesign,
  not a shape bump.
- `envs/utils.py::change_max_relator_length_of_presentation` uses `len//2` (assumes 2
  relators) on the data-loading path.
- The pretrained `ppo_checkpoints/610model/` has input dim 48 and 2304-action head baked
  in → **cannot run on 3-gen without a full retrain** (it was ~1e9 timesteps).

Recorded so it's turnkey later. Ordered dependencies:

1. **Env/move generalization** (`envs/ac_moves.py`, `envs/ac_s.py`, `envs/utils.py`):
  make `s_move` source an arbitrary (target `i`, source `j`) relator pair and write to
   slot `i`; generalize `change_max_relator_length_of_presentation`/
   `convert_relators_to_presentation` off `len//2`.
2. **Action packing** redesign for `i∈{0..n-1}`, `j∈{0..n-1}`, kept in sync across
  `envs/utils.py`, `wrappers.py`, `ppo_ac_s.py`, `beam/beam_search.py`.
3. **Network**: dual-ring → tri-ring (`vocab_size` 5→7, `+2`→`+3` embed shift, n-way ring
  split/attention, n-way action head).
4. **Retrain** PPO on the `z=w` stabilized data `data/1190MS_z_<w>.txt` (`n_gen=3`); from
  scratch (610model params are architecture-incompatible — no warm-start).
5. **Beam** with the new checkpoint on the stabilized MS(1190); compare to Phase 3 greedy and
  to the original 2-gen RL numbers. With a content-bearing `z` the learned policy can exploit
   the `w ↔ z` substitutions directly. Estimated weeks + GPU compute.

---



## Validation summary (how we prove each phase works)

- **Phase 0/0.5:** directional gate — an idx-≥640 solve is **replay-triaged** (replay passes ⇒
kept as a genuine new solve and logged; replay fails ⇒ solver bug, stop), and ≈634@100K /
≈640@1M within idx<640 (SOFT, log deviations). Reproduction gate runs the notebook's **sum-cap**
so a deviation reads as a port bug, not a cap-semantics difference. RL labels (when JAX present)
read back from `610model` match `scripts/check_checkpoint_paths.py` counts. JSON keeps the paper's
claim (`paper_reference`) and our measurement (`greedy`) in separate fields so any disagreement is
visible.
- **Phase 1:** stabilized lines have length `3·L`; r1/r2 prefixes unchanged; the z-relator
decodes back to `z = z_word`; round-trip `flat_to_relators`↔`relators_to_flat` is identity.
- **Phase 2:** the **5-step pre-flight** above (check 0 rotation-correct — the `np.roll(2*i)` trap;
solvable-stays-solvable; content-bearing `z` fires while trivial `z` is empty; null-revert block
holds incl. the 2-step revert; solved paths replay to trivial). Optionally cross-validate a
stabilized solved path against the JAX env once Phase 4's generalized `s_move` exists (not now).
- **Phase 2.5:** calibration probe produces a concrete nodes/sec + projected per-arm hours before
any full sweep commits; budgets/worker-count are chosen from it, not guessed.
- **Phase 3:** **path length** and **node usage** logged per presentation per arm, each with its
budget tier and **per-relator** `max_len`; new-solves-vs-baseline re-verified by replaying the
greedy path to all-length-1; `z∈{x,y}` regressions read as pre-registered alias artifacts; no
silent truncation.

---



## Reuse map (what existing code we lean on)

- `greedy_search.ipynb` — algorithms (Booth, reduce, inverse, canonical, best-first
`ACRelatorSolver`, `MS(n,w)`, `counterexamples`) generalized into `greedy_nrel.py`.
- `data/1190MS.txt` — the benchmark, loaded directly (env int format).
- `ppo_checkpoints/610model/` + `scripts/check_checkpoint_paths.py` +
`beam/beam_search.py` — RL/beam labels for Phase 0, unchanged.
- `ppo_ac_s.py:362-371` — the W&B init pattern (lazy import, gated, tags/name/config) reused
for `run_experiment.py`.
- `envs/utils.py` padding/packing helpers — referenced as the spec for the n-relator
converters (not imported; kept independent to avoid touching the shipped env in this phase).

---



## Execution order

0. `jsonl_io.py` — the resumable-JSONL helpers first (every sweep below depends on them).
1. Phase 1 `stabilize.py` — write the 4 primary `data/1190MS_z_{x,y,r1,r2}.txt` (+ the 2 optional
   `data/1190MS_z_{r1inv,r2inv}.txt`) datasets (+ validation).
2. Phase 2 `greedy_nrel.py` + visited-block + **5-step pre-flight (checks 0–4)** — rotation-correct
   first, then n=2, n=3 with `z=w`, content-vs-trivial, block-holds (incl. 2-step revert).
2.5. Phase 2.5 `calibrate.py` — warm up numba, probe ~5 hard (unsolved, `n=3`) + ~5 easy cases →
   `results/calibration.jsonl` + projected hours; **pick the `{small, large}` node budgets** and
   worker count that feed steps 4–5. (Needs the solver from step 2; must precede the full sweeps.)
3. Phase 0 `categorize.py` — build `labels_1190.json` (index-derived `paper_reference`; no
   compute; `rl_610model`/`beam_610model` null here — no JAX).
4. Phase 0.5 `categorize.py --greedy` — two `n=2` sweeps: the **sum-capped** reproduction gate
   → `results/greedy_reprogate_{100k,1m}.jsonl` (replay-triage gate at the idx-640 boundary) and
   the **per-relator-capped** cross-arm baseline → `results/greedy_baseline_{100k,1m}.jsonl`
   (metrics: **path length** + **node usage**). Both resumable, small tier over all 1190 then large
   tier over the still-unsolved.
5. Phase 3 `run_experiment.py` — primary `z=w` arms `{x,y,r1,r2}` (then optional `{r1inv,r2inv}`)
   → `results/greedy_z_<w>_{100k,1m}.jsonl` (resumable); `viz.py` + W&B.
6. `README.md` with reproduce commands. Leave Phase 4 (and the RL/beam labels) as spec.

