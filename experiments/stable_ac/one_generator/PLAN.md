# Stable AC — One-Generator Change-of-Variables Pipeline (`z = w(x,y)`)

**Goal.** Stabilize a 2-generator presentation `⟨x,y | r1, r2⟩` by adding a generator `z` **defined
as a word** `z = w(x,y)` → `⟨x,y,z | r1, r2, z·w⁻¹⟩`, then run our greedy search to test whether
naming a well-chosen `w` opens trivialization paths the 2-generator search can't reach. Benchmark:
**MS(1190)** (`data/1190MS.txt`, 1190 lines). Words `w ∈ {x, y, r1, r2}` (dumbest first). **Greedy +
categorization only** — the RL/beam-on-3-generators path is deferred to Phase 4. Two headline metrics
per presentation: **path length** and **node usage**.

> The full background — the mentor's decision, why `z = r1` is non-vacuous, and why *trivial* `z`
> was dropped — is in **Background & rationale** at the end of this file. It's reference detail; the
> phases below are self-contained.

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

**Result persistence (crash-safe, resumable — a project convention; see** `CLAUDE.md`**).** Every
per-presentation sweep here (Phase 0.5 baseline, each Phase 3 `z=w` arm) writes an
**append-only** `.jsonl` — one JSON object per presentation, flushed per line — and **resumes
from the last object**: on restart it reads the stream, skips already-done `idx`, and continues.
A pre-empted or crashed cloud job then never loses finished work or recomputes it. Tiny helpers
`jsonl_done_ids(path)` / `jsonl_append(path, obj)` live in `jsonl_io.py`, reused by every sweep.
Only fully index-derived artifacts (the `paper_reference` labels) stay `.json`.

**One stream per** `(arm, node-budget)` **— the resume key must be unambiguous.** Because we run a
budget escalation (a cheap first pass, then a larger budget on the still-unsolved), a stream keyed
on `idx` **alone** cannot tell "unsolved at 100k" from "solved at 1M" — on resume the escalation
pass would either no-op or write duplicate `idx` lines that the merge then has to disambiguate.
So each sweep writes a **separate file per budget tier**: `…_100k.jsonl` and `…_1m.jsonl`, and the
larger-budget pass enumerates **only the** `idx` **left unsolved by the smaller** (which also avoids
re-solving the easy cases). The merge at report time keeps "which budget solved it" for free.
Exact budget numbers are set by the Phase 2.5 empirical calibration, not guessed.

**Execution environment (Colab × Drive) — why resumability is load-bearing, not decorative.** The
sweeps run on a **fleet of up to ~5 high-RAM Colab CPUs in parallel** (one arm per box), not this
machine. Workflow: `git clone` the repo into a Colab notebook, mount Google Drive, run the arm with
its `results/*.jsonl` written **to a Drive path**; when done (or when the session is pre-empted /
hits its time limit) the streams persist on Drive and are synced back into the repo's `results/`.
Two design consequences already baked in above: (1) the **append-only, resumable per-(arm,budget)
JSONL** is exactly what lets a killed Colab session resume with zero lost/recomputed work — this is
the primary reason for the convention; (2) high-RAM boxes absorb the `n=3` @1M memory footprint
(feedback's OOM worry), though we still key `visited` on `bytes` and log peak RSS (Phase 2). So the
single-core "CPU-weeks" figure is **not a blocker** — arms run concurrently across boxes, and any
one that won't fit a session is sharded by `idx` (Phase 2.5).

---



## Phase 0 — Categorization: per-presentation reference labels over MS(1190) (no stabilization)

Goal: per-presentation labels over all 1190, captured **before** any stabilization so
stabilization deltas are measurable — split by persistence need:

- `results/labels_1190.json` — the cheap, fully index-derived skeleton (one object per
presentation: `idx, presentation, r1_len, r2_len, ms_n, ms_w, paper_reference`). Rebuildable
in one pass, so plain JSON is fine.
- `results/greedy_reprogate_{100k,1m}.jsonl` — the n=2 **reproduction/port gate** (Phase 0.5),
run under the notebook's **sum-cap** to reproduce the paper's 634/640 and the idx-640 boundary.
- `results/greedy_baseline_{100k,1m}.jsonl` — the n=2 **cross-arm baseline** (Phase 0.5), run
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
`data/1190MS.txt`. **It does two** `n=2` **sweeps under two different length caps** — cheap, since
`n=2` is the fast case — because one run can't serve both purposes:

1. **Reproduction/port gate →** `results/greedy_reprogate_{100k,1m}.jsonl`**, notebook** `sum-cap`**.**
  GS-Sub *is* this notebook, which caps on the **sum** of relator lengths, so we reproduce the
   paper apples-to-apples under the sum-cap: a deviation from 634/640 then means "port bug," not
   "cap-semantics difference."
2. **Cross-arm baseline →** `results/greedy_baseline_{100k,1m}.jsonl`**,** `per-relator` **cap.** The
  baseline that Phase 3 compares the `z=w` arms against, run under the **same per-relator cap the
   n=3 arms use** (Phase 2/3) — so a baseline-vs-arm coverage delta reflects stabilization, not a
   cap that carves a different `(r1,r2)` region for `n=2` vs `n=3`.

Both are append-only and resumable (skip any `idx` already in *that* stream); each line:

```jsonc
{ "idx": 0, "solved": true, "path_verified": true, "nodes_explored": 812, "path_len": 13,
  "wall_time_s": 0.04, "max_len_along_path": 21, "budget_nodes": 100000, "cap": "sum" }
```

Budget escalation for **each** stream (numbers fixed by the Phase 2.5 calibration, not guessed;
nominally `max_nodes ∈ {100k, 1M}`): run the small budget over all 1190 → `…_100k.jsonl`, then the
large budget **only over the** `idx` **still unsolved** → `…_1m.jsonl` (the 6 idx-634–639 cases are
expected to appear at 1M). The `cap` field records which rule was in force. The validation gate
below reads the `reprogate` streams (paper comparison); Phase 3 reads the `baseline` streams.

**Validation gate (directional — this is the real signal):**

- **HARD-with-triage:** a greedy *solve at* `idx ≥ 640` is **quarantined, not auto-fatal**.
**Replay the returned path** (free+cyclic-reduce each step; assert it ends all-relators-length-1
— the Phase 3 re-verification machinery). **Replay passes → this is a headline result, not a
footnote.** The paper reports *never* solving any presentation outside the initial 640, so a
single reproducible solve at `idx ≥ 640` is a genuinely new, powerful finding — surface it
immediately (flag the `idx`, save its path, don't bury it in the stream). `paper_reference.solved = idx<640` is the paper's *claim*; our replay-verified measurement is allowed to beat it.
**Replay fails → it's a solver bug: stop and fix.** Only an *irreproducible* solve invalidates
the ordering assumption.
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
- **Preset baseline words** `w ∈ {x, y, r1, r2}`: `x/y` are constant, `r1/r2` read per-line from
the presentation. Across MS(1190) `max|r1|=17, max|r2|=15`, and across the 261 reps
`max|r1|=11, max|r2|=17` ⇒ every z-relator (`1+|w|`) is ≤ 18 ≤ `L=24` on **both** datasets, so
`L=24` **holds for all baseline words — no bump needed.**
- `write_stabilized_dataset(in_stem, z_spec, out_stem, ...)` — read `data/<in_stem>.txt`,
stabilize each line with `z_spec`, write `data/<out_stem>.txt` (same
one-Python-literal-list-per-line format). Produces **one file per word** for each benchmark:
`data/stabilized/1190MS_z_{x,y,r1,r2}.txt` (1190 lines) and `data/stabilized/ms_reps_unsolved_z_{x,y,r1,r2}.txt`
(261 lines), length-72 each.
- Converters `flat_to_relators(flat, n_gen, L)` ↔ `relators_to_flat(rels, n_gen, L)` so the
greedy (list-of-relators) and env (flat) formats interoperate — **n-relator-generic** (no
`//2`), mirroring the intent of `envs/utils.py::change_max_relator_length_of_presentation`.

Validation: every stabilized line has `new_n_gen*max_length` entries; the r1/r2 prefixes are
unchanged; the z-relator **decodes back to** `z = z_word` (drop the leading `z`, invert ⇒
`z_word` up to cyclic reduction); round-trip `flat_to_relators`↔`relators_to_flat` is identity.

---



## Phase 2 — n-relator greedy solver (reuse + generalize the notebook)

`greedy_nrel.py` extracts the **algorithms** from `greedy_search.ipynb` and generalizes
them from "2 bool-encoded relators" to "a tuple of `n` int-encoded relators." Reused, only
re-typed to int arrays: Booth minimal rotation (`find_minimal_rotation`), free+cyclic
reduction (`reduce_relator_nj`), inversion (`inverse_relator_nj`), canonicalization
(`canonical_relator_nj`).

> **⚠ PORTING TRAP (silent-correctness — fix first, test explicitly).** The notebook's
> rotation is `np.roll(r, 2*i)`: it rolls by `2*i` because each letter is a `(bool, bool)`
> *pair*, so one logical letter is two array slots. The int port stores **one slot per letter**,
> so it must roll by `i`, not `2*i`. Miss this and *every* rotation — hence every
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
- `get_neighbors` (the substitution move, n-relator): for **every UNORDERED pair {a, b}
(a<b, leader = a)**, each candidate `c ∈ {r_b, r_b⁻¹}`, and each cyclic rotation of `r_a` and `c`,
if the boundary letters cancel, form `neighbour = reduce(concat(rot(r_a), rot(c)))` and emit it
into **BOTH slot a (**`r_a → neighbour`**) and slot b (**`r_b → neighbour`**)** — the `r_a`-leading splice
goes into whichever relator is being modified. This is **not** the leader-only "ordered pair, replace
a" reading (that gives a *different* set and fails the n=2 oracle). It is the exact generalization of
BOTH references, which agree at n=2: the notebook `get_neighbors_nj` (leader r1, both slots) AND the
gymnax env `envs/ac_moves.py::s_move` (`neighbour = rot(r0)·rot(r1^±)` substituted into slot `i` for
`i∈{0,1}`, `r` = invert-r1). So the port's move logic is faithful-by-construction to the env's `s_move`
convention (lower-index leader, dual-slot emit, all pairs), triangulated across three independent
implementations. **With a content-bearing** `z` **(relator** `z·w⁻¹`**),** `(r_i, z)` **pairs cancel
normally** — the z-relator carries `w`'s x/y letters — so substitution acts on `z` directly. **No
seeding moves are needed** (they were only a workaround for trivial `z`, which we no longer use).
  - ⚠ **The env's shipped** `s_move` **is hardcoded to splice** `r0·r1` (`rotate_relator_k(0,…)`,
  `rotate_relator_k(1,…)`), so it structurally cannot do the `(r_i, z)` n=3 moves — confirming from
  the actual code that the **executable** JAX gold check of the n=3 move set needs Phase 4's
  generalized `s_move` (and JAX is not installed on the greedy boxes anyway). Until then the n=3 move
  logic is verified only by source-reading against the env convention + the n=2 differential oracle;
  the n=3 scheme itself has **no executable independent oracle** — state this in any n=3 coverage claim.
  - **Cheap hot-loop optimization (do this in the port):** the notebook materializes an
  `np.roll` copy + concat + reduce for *every* rotation pair before testing cancellation. Instead
  **read the two boundary letters directly** (two indexed lookups per rotation pair — the last of
  `rot(r_a)` and the first of `rot(c)`) and only build `concat+reduce` for pairs that actually
  cancel. Cancellation is sparse, so this is an order-of-magnitude constant-factor win — and it
  matters: `n=3` has **3 unordered relator pairs vs** `n=2`**'s 1** (each emitting into 2 slots), so
  per-node neighbor work is the dominant cost of the whole sweep (see Phase 2.5).
- **Visited-block (mentor's null-revert guard):** `NRelatorSolver(..., blocked_states=None)`
pre-seeds the closed/visited set with canonical state-keys that are never enqueued/expanded.
For a `z=w` run we pass the **single** null-revert state `canon(r1, r2, [z])` — the original
presentation with `z` collapsed to `z=1` — **canonicalized in the solver's own canonical form**
(sort + Booth + cyclic-reduce) so the key actually matches. This stops greedy from unwinding
`z` straight back to nothing, while leaving genuine destabilizations (progressed `r1',r2'` with
`z` removed) reachable.
- **Revert hook — label the collapse, don't just silently block it.** The blocked key
`canon(r1, r2, z=1)` is a *single fixed canonical state*, so every route that collapses `z` lands on
exactly that key (canonical form is unique — that's why one blocked state suffices). Instead of
discarding a generated neighbor that equals it, **flag it:** increment a `revert_hits` counter and
(under a `track_reverts` flag) append `(parent_key, move)` to a `revert_log`. This makes the null
revert *observable* — how many times, and from which states/moves, the search tried to unwind `z` —
so we can see whether the block is doing real work and how much effort goes into reverting.
`revert_hits` goes into the per-presentation JSONL line; the full `revert_log` is gated (diagnostic
only, off on the 1M runs alongside `track_seen`).
- **Trivial check:** `all(len(r)==1 for r in relators)` (generalizes `len(r1)==1 and len(r2)==1`; matches the env's `count_nonzero == n_gen`).
- `NRelatorSolver` class mirroring `ACRelatorSolver`: heapq best-first on total relator length
(the paper's GS default), `max_nodes`, `visited` parent-dict for path reconstruction, plus the
`blocked_states` above. Returns `(path, nodes_visited, seen)` and records **path length** and
**node usage** — the two headline metrics. (An optional `"length_tolerant"` priority remains
available but isn't required: `z=w` is content-bearing, so there's no length-increasing seed to
protect.)
- **Retrace & independent verification (step-by-step path, re-derived from scratch).** Two pieces:
  - `retrace(key)` — walk the `visited` parent-dict from a state back to the initial state and
  return the ordered path of states, **annotating each transition with the move that produced it**
  (which relator was substituted, the two rotation indices), so the route is human-readable
  step-by-step — not just a list of states. Works for any state; the point of interest is the
  solved (all-length-1) state and any `idx ≥ 640` solve.
  - `verify_path(path)` — replay the retraced path **independently of the search bookkeeping**:
  for each consecutive pair recompute `get_neighbors(state[k])` from scratch and assert
  `state[k+1]` is among them (canonical), each relator free+cyclically reduced, and the final state
  trivial. This doesn't trust `visited`/`heapq`, so it catches search bugs, and it is the
  ground-truth gate for **every reported solve** (the Phase 0.5 / Phase 3 replay check *is* this).
  Each solve's JSONL line carries `path_verified` (bool); a `False` is never counted as a solve.
  - **Persist the path — store it, don't just check-and-discard (n≥3 REQUIREMENT).** For `n≥3`
  every solve **writes its retraced path to disk**, not just the run-time `path_verified` boolean:
  a sidecar `results/paths_<arm>_<tier>.jsonl` keyed by `idx` — each line
  `{idx, name?, moves:[(rel_i, ra_rot, c_rot, c_is_inverse), …], states:[flat relator-tuples], path_len}`. This makes every solve **re-verifiable, replayable, and demonstrable to others
  offline**, and later feedable to the JAX `check_paths` gold gate — a boolean flag is proof to
  *this run*, a stored path is proof anyone can re-run. The main JSONL line keeps the scalar
  `path_verified`/`path_len`; the sidecar carries the route. (The `n=2` Phase 0.5 streams
  deliberately do **not** do this — we consciously accepted length-only there since we only need
  the solved-count + length distribution; from `n=3` on the path is a first-class, persisted
  artifact, because those `z=w` class-solves are findings we present, not just counts.)
  - **Gold-standard cross-check (real env).** `envs/utils.py::check_paths` replays a path in the
  actual gymnax env — available **now for** `n=2` **baseline solves** (the shipped 2-gen env, as in
  `scripts/check_checkpoint_paths.py`). For `n=3` `z=w` solves it needs Phase 4's generalized
  `s_move`, so until then `n=3` solves rely on the in-module `verify_path`.
- **Length cap = *per-relator*, not sum (removes an** `n=2`**-vs-**`n=3` **confound).** Cap each relator
individually at `max_len` (mirrors the env's `L=24` semantics), the **same value for every relator
in every arm**. A shared *sum*-cap would let the z-relator (up to 18 letters for `z=r1`) eat the
headroom for `r1,r2`, so the `n=3` arm would search a strictly *smaller* `(r1,r2)` subspace than
the `n=2` baseline and any "coverage regression" would be a cap artifact, not a stabilization
effect. A per-relator cap makes the `(r1,r2)` subspace identical across baseline and arms by
construction. State the rule once in the `greedy_nrel.py` docstring; record the cap per JSONL line.
*(The* `n=2` *reproduction gate in Phase 0.5 deliberately uses the notebook's native sum-cap instead
— that's port-validation, not cross-arm comparison; see Phase 0.5.)*
- **Scale/memory notes (implementation, tagged so they don't balloon the spec).** Confirmed against
`ACRelatorSolver.solve`: `visited` stores **every generated neighbor** (not just expanded nodes) —
`self.visited[key_new] = key` runs inside the neighbor loop — as a Python **string-tuple** key. At
the 1M-node, `n=3` regime that set is the memory bottleneck (~10⁷ states ⇒ ~2.5–3.5 GB just for
`visited`; 10⁸ ⇒ tens of GB). Two levers:
  - Key `visited` on compact `bytes` (int8 relators joined by a separator) instead of
  character-string tuples — ~4× smaller and hashes faster.
  - `new_seen` **is gated behind a** `track_seen` **flag, not deleted.** It's a second hash container
  (it shares the key objects with `visited`, so it doesn't double the strings, but it still costs
  the set's per-entry overhead — hundreds of MB at 10⁷) whose *only* use is the post-hoc "minimal
  element" diagnostic. So make it optional: `NRelatorSolver(..., track_seen=False)` skips it on the
  memory-critical **1M** runs; enable `track_seen=True` on the cheaper **100k** runs (and the
  calibration probes) when the minimal-element diagnostic is wanted. Default `False`.
  - Log **peak RSS** per JSONL line so the 1M runs are observable and a box OOMs visibly, not
  mysteriously.



Pre-flight (advisor-sharpened + our CLAUDE.md rule) **before any 1190 sweep**. Worded to
*discriminate* — a check that passes on a broken port is worthless:

1. **Rotation is correct (the porting trap):** assert `rotate(r, i)` on a hand-built relator
  produces the exact expected array for a few `i` — the guard against `np.roll(2*i)` vs `i`.
  Fast pinpoint; nothing else is trustworthy until it passes.
2. **Differential oracle vs** `greedy_ac` **at n=2 (THE gate).** Run `greedy_nrel(n_gen=2)` and the
  known-good `greedy_ac` on the **same ~50 presentations, including hard non-trivial solves**
  (idx ~100–600 that take thousands of nodes — *not* idx 0–4, which solve in 2–3 nodes and pass
  even with a rotation bug), same per-relator cap and budget. Assert **identical solved set** and
  **every** `greedy_nrel` **solve replays via** `verify_path`. Do **not** assert equal node counts or
  path lengths — a different int `is_less_than` ordering changes the canonical rep and heap
  tie-breaks, so those legitimately differ; only the solved *set* is representation-independent
  (tolerate a single flip on a case sitting exactly at the budget boundary; investigate any other
  disagreement). This one test catches the rotation trap, the `get_neighbors` generalization, and
  canonicalization together — the real gate, stronger than "matches the notebook."
3. Stabilize a solvable presentation with `z=x` → `n=3` solve must **still succeed** (z can be
  ignored/destabilized); assert the path replays to all-relators-length-1.
4. **z-pair neighbors are correct, not just non-empty (no independent oracle here).** The
  `(r_i, z)` move is the one piece the n=2 differential never exercises and the JAX gold check
  (Phase 4) can't yet cover, so a *wrong-but-consistent* move gives false solves `verify_path`
  can't catch (it shares `get_neighbors` with the solver). Hand-work one tiny `(r1, z=w)` example
  and assert the **specific expected neighbor set** (exact states), plus **empty** neighbors for a
  trivial `z`.
5. **Block FIRES (not just "doesn't settle").** "Search never expands the blocked state" passes
  trivially if the block is a no-op that matches nothing (e.g. blocked key canonicalized
  differently from neighbor keys). On a case constructed to attempt the revert, assert
  `revert_hits > 0` — the only thing distinguishing a working block from one that silently
  matches nothing — and that the search still never settles on `canon(r1, r2, z=1)`, incl. the
  2-step revert path `(r1, r2, z·r1⁻¹) → ([z], r2, z·r1⁻¹) → ([z], r2, r1⁻¹)` (inversion-invariant
  `canonical_relator_nj` + sorted tuple ⇒ it canonicalizes to the same single blocked key).

**Persist-loop closure (verify the *serialized* form, not just the in-memory object).**
`verify_path`'s input representation and the sidecar's stored representation must be the **same**
thing, and a sampled `deserialize → replay` must pass — otherwise `path_verified:true` certifies
an in-memory path while the on-disk artifact could be lossy. State plainly: the n=3 sidecar
enables **re-audit + demonstration now**, but **not** the JAX gold check (needs env-action
packing, Phase 4) — it is not gold-checkable yet.

**Implementation (numba granularity — saves a detour):** keep `@njit` at **single-relator**
granularity (rotate/reduce/inverse/canonical each take one int array, as the notebook does) and
run the n-relator pairing loop in **plain Python**. numba falls to object mode (or fights you) on
ragged, variable-length tuples-of-arrays, so don't pass "state = tuple of n relators" into njit.

---



## Phase 2.5 — Empirical timing calibration & budget selection (do this before the full sweeps)

**Measure the runtime so we can size the Colab runs — it is not a blocker.** A back-of-envelope
from the notebook (~10k nodes / 1.9 s single-core, `n=2`) puts one arm at ~**3 h @100k** / ~**29 h
@1M** single-core (`100k / (10k/1.9s) ≈ 19 s` × 550 unsolved; `n=3` is slower still — 6 ordered
relator pairs vs 2). That would be CPU-weeks on one core, but the **arms run in parallel on the
Colab fleet** (one arm per box; see the execution note), so the real question calibration answers
is operational: **does a given (arm, budget-tier) fit inside one Colab session**, and if not, how
to shard/multiprocess it within a box. `calibrate.py` turns the probe into that estimate.

**What to measure — throughput on the *hard* cases, not "time to solve."** Runtime is dominated by
the ~550 **unsolved** presentations: each runs to the **full node budget** (that's what "unsolved"
means), so the reusable quantity is **nodes/sec**, measured on a *budget-exhausting* case, on the
`n=3` **code path** (not the notebook's `n=2` number). Concretely:

1. **Warm up numba first** — one throwaway solve so JIT-compile time doesn't land inside the first
  measurement (it's visible as the notebook's inflated first cell). Keep dtypes fixed (int8) so
   there are no silent recompiles mid-probe.
2. **Hard sample (~5, drives the estimate):** 5 of the 261 unsolved-class reps
  (`data/ms_unsolved_reps/ms_reps_unsolved.txt` — the actual hard targets), stabilized (`z=r1`, the representative
   content-bearing arm), each run to the **candidate max budget**.
   Record wall-time and `nodes/sec`. Runtime floor ≈ `median nodes/sec` → `budget × #unsolved ÷  nodes/sec` per arm.
3. **Easy sample (~5, minor addend):** 5 *solved* presentations sampled across the difficulty range
  (early/low-idx and near-640) → the cheap solved-case time. Small next to (2), but confirms the
   easy tail is negligible.
4. **Output** → `results/calibration.jsonl` (one line per probe: `idx, arm, n_gen, budget_nodes,
  nodes_explored, solved, wall_time_s, nodes_per_sec, peak_rss_mb`) + a short printed summary:
   projected per-arm hours at each candidate budget, and the total across all arms/tiers.

**Then choose** the `{small, large}` budget tiers (the `100k / 1M` nominal, adjusted to what the
probe says is affordable) and the parallelism layout across the Colab fleet: **one arm per box**;
`multiprocessing` **across presentations within a box** (the high-RAM Colab CPUs are multi-core, and
the per-idx JSONL streams are shard-safe) to use its cores; and if a single (arm, tier) still won't
finish inside one Colab session, **shard its** `idx` **range across boxes** (each shard its own resumable
stream, merged on Drive). Record the worker count. The chosen budgets feed Phase 0.5 and Phase 3.

---



## Phase 3 — Experiment, W&B, plots

`run_experiment.py` runs the **2-gen baseline plus one arm per** `z=w` **word** over MS(1190).
**Each** `(arm, budget-tier)` **writes its own append-only, resumable** `.jsonl` —
`results/greedy_baseline_{100k,1m}.jsonl` (reused from Phase 0.5) and
`results/greedy_z_<w>_{100k,1m}.jsonl` per word — one line per presentation, skipping any `idx`
already recorded (a pre-empted cloud run resumes cleanly), and the large-budget tier enumerating
only the `idx` the small tier left unsolved. `viz.py` / the report step merges the streams by
`idx`, preferring the tier that solved it.

**Coverage target — the 261 unsolved-class representatives (**`data/ms_unsolved_reps/ms_reps_unsolved.txt`**), run first.**
The 550 unsolved MS(1190) presentations fall into **261 AC-equivalence classes**; the mentor supplied
one **minimal-form representative per class** (`data/ms_unsolved_reps/ms_reps_unsolved.csv`: `r1, r2, name`, e.g.
`13_1 = AK(3)`). Verified this session: those 261 names are an **exact bijection** with the non-`trivial`
class labels in `data/ms_unsolved_reps/ms_solved_grid.csv` (against 640 `trivial` cells), so solving the 261 reps solves
all 550 unsolved. The coverage question — *can a* `z=w` *stabilization crack a presentation classical AC
can't?* — is therefore answered on these **261**, not the raw 550: deduplicated, class-labeled, and cheap
enough to **run first** as the headline. `data/ms_unsolved_reps/ms_reps_unsolved.txt` is the loadable form (built +
round-trip-verified by `scripts/build_ms_reps.py`); `stabilize.py` also emits
`data/stabilized/ms_reps_unsolved_z_<w>.txt` per word. Streams: `results/greedy_baseline_reps_{100k,1m}.jsonl` and
`results/greedy_z_<w>_reps_{100k,1m}.jsonl` — same schema as the 1190 streams **plus a** `"name"` **field**
(the class label), resumable per `(arm, budget)`.

> **These reps are minimal canonical forms, *not* MS(1190) presentations** — 0/261 carry an MS-pattern
> relator `X y^n x Y^{n+1}` — which the metrics must respect:
>
> - **The 2-gen baseline runs on the reps too, and may legitimately solve some.** A minimal form is
> often easier for length-priority greedy than the bloated MS member, so a baseline rep-solve is **not**
> an anomaly or an ordering violation (the paper's "550 unsolved" was measured on the *MS forms*). It is
> the control, and **baseline rep-coverage is a finding in its own right** — what the canonical form
> alone buys before any stabilization. The coverage signal is `(z=w solved) − (baseline solved)` **on
> the identical rep form**, per class.
> - **A verified rep-solve establishes that AC-equivalence class is AC-trivial** (headline: *"stably
> trivialized canonical hard class* `<name>`*"*). Verify it like any solve — `verify_path` + the `n=2`
> `check_paths` gold-standard — before claiming the class. It does **not**, by itself, beat the paper's
> "never solved outside the 640" benchmark: that is a claim about the *MS forms*, and bridging rep → MS
> member needs an explicit equivalence path the CSVs don't provide. Exhibiting that MS-member→rep
> reduction is a **separate step, flagged, not assumed.**

- **Baseline: 2-gen greedy** (`n=2`, `data/1190MS.txt`) — = the **per-relator-capped**
`greedy_baseline_*.jsonl` from Phase 0.5 (**not** the sum-capped `greedy_reprogate_*.jsonl`),
so baseline and arms share the identical per-relator cap and the delta is stabilization, not caps.
- `z=w` **arms** (`n=3`), one per `w ∈ {x, y, r1, r2}`, each on its `data/stabilized/1190MS_z_<w>.txt`,
with the null-revert visited-block on → `results/greedy_z_<w>_*.jsonl`.
- **Two headline metrics per presentation, per arm:** **path length** (moves to trivialize)
and **node usage** (nodes explored). Each line also carries `solved`, `path_verified`,
`revert_hits`, `wall_time_s`, `max_len_along_path`, `peak_rss_mb`, and the budget tier that
solved it.
- **Every solved presentation also writes its full path to the sidecar**
`results/paths_<arm>_<tier>.jsonl` (Phase 2's persisted retrace, keyed by `idx`, with the class
`name`) — so each `z=w` class-solve is **replayable and demonstrable**, not just a
`path_verified:true` flag. A headline "stably trivialized class `<name>`" claim must point at a
stored, re-runnable path.
- **Path-length convention (pin one rule, cross-arm plots depend on it):** a `z=w` arm's
`path_len` is the **search path only**, and does **not** count the implicit `+1` stabilization
move (the search starts from the already-stabilized presentation). State it once; apply it to
every arm so baseline-vs-arm path-length deltas are comparable.
- Budget tiers from Phase 2.5 (nominal `max_nodes ∈ {100k, 1M}`); **per-relator** `max_len` cap
(same value every relator every arm — Phase 2), all logged so there are no silent caps.

**Pre-registered expectation —** `z∈{x,y}` **will look worse, and that's an artifact, not a verdict.**
With z-relator `z·x⁻¹`, swapping any single `x ↔ z` in `r1/r2` is **length-neutral**. Best-first on
total length exhausts each length level before growing, so `z∈{x,y}` arms will enumerate large
chunks of the `~2^(#x-occurrences)` alias orbit *at the initial length* before making progress —
inflating node usage and producing budget-exhaustion "regressions" that measure alias blowup, **not**
stabilization being bad. **We pre-register this:** interpret `z∈{x,y}` coverage regressions as
budget artifacts unless replay says otherwise. Corollary: `z=r1`**/**`z=r2` **are the arms where a real
"wormhole" signal is most likely visible** (their swaps are whole-word, not length-neutral aliases).
Optionally report a per-arm "distinct states modulo `z↦x` relabel" diagnostic to quantify the orbit.

Headline comparisons:

- **Coverage (headline — measured on the 261 class reps):** how many unsolved AC-classes does
each `z=w` arm crack that the 2-gen baseline (on the *same* rep form) does not? Signal =
`(z=w solved) − (baseline solved)` per class; baseline rep-coverage is itself reported (what the
canonical form buys pre-stabilization). Every class-solve **replay-verified** to all-length-1 and
logged with its `name` before it counts; any regressions (baseline solved, `z=w` not)? (On the
MS(1190) forms, a `z=w` solve at idx ≥ 640 is the stronger *direct* paper-benchmark claim —
Phase 0.5's replay-triage gate applies there.)
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



## Phase 3.5 — Word-choice (“wormhole”) study: which `w(x,y)` is best? (DONE — negative result)

Phase 3 fixed the four dumb words `w ∈ {x,y,r1,r2}`; the Background note flagged *“searching for the
best `w` is the next plan.”* This is that search, run as two sibling sweeps — throw ~97 candidate
words `w(x,y)` (8 families) at a target via `z=w` stabilization + n=3 greedy and ask whether a
*clever* word opens a cheaper/shorter trivialization than the dumb `z=r1`, or solves where the dumb
words fail. Word bank (`hard_words.py`/`ak3_words.py`): `relhalf` (parts of THIS target’s own
relators), `wk` (`y⁻ᵏ·x⁻¹yxy`, the AK(n) isolation family, Thm 6/7), `wstar` (Thm 3 + automorphism
images), `conj`, `comm`, `brute` (all freely-reduced words of length ≤3, includes dumb x/y), `ms`
(MS(n,w) library w-values), `control` (w=r1,r2). Two-tier, crash-safe/resumable (append+flush+fsync;
resume by `(idx, word_name, budget)`).

### Study A — AK(3) (`run_ak3_wormhole.py`, results `results/stable_ac/3_generators_w_choices/ak_3_test/`)
Two AK(3) forms (textbook `⟨x,y | xyx=yxy, x³=y⁴⟩` + rep `13_1`) × ~95 words. **Result: 0 solved.**
The search drives total relator length down to a **plateau at 13** (trivial = 3) and sticks — even the
provably-isolatable flagship theory words (Fagan’s `xyx`, `yxy`, `x³`, `y⁴`, `wk`) run the full
1,000,000 nodes and stay at length 13. AK(3) is a *negative control*: it can’t rank the families
because nothing solves.

### Study B — hard-but-solvable MS targets (`run_hard_wormhole.py`, results `.../hard_solved_test/`)
Because AK(3) gave nothing to rank, we repeated the sweep on two presentations the 2-gen greedy
**does** solve (idx 625: 77,385 n / 663 p; idx 610: 61,066 n / 307 p) — so there is a real baseline to
beat. ~97 words × {625, 610} at a **100,000-node screen** (1M full tier specified but **user-gated,
NOT run**). **Result (screen): another clean negative.** idx 625: 98 words, 4 solved; idx 610: 99
words, 2 solved — but in **both** cases the *only* solvers are relator-derived (`control` `z=r1/r2`
and `relhalf` words that are a half/inverse of `r1`), landing at the **same** node count as the `z=r1`
control (a tie, not a shortcut). **0 of ~180 generic-family (word×target) runs solved**; every
structurally-different word — including the theory-motivated `wk` family — plateaus at total length
16–18 (trivial 3). All 6 solve paths reload→replay to trivial from disk (`verify_path`).

**Takeaway (both studies).** Ordinary greedy substitution does **not** exploit a named change of
variables `z=w`: no clever word beats the dumb `z=r1`, and none solves where the dumb words fail.
Realizing a useful `z=w` is Fagan’s **Lemma-11 atomic destabilization** — a *supermove* greedy does
not perform (it can only nibble length down one substitution at a time). This is the motivation to move
to the Lemma-11 batch operation / a learned policy (Phase 4), **not** more word search. Reports
regenerated by `report_ak3.py` / `report_hard.py` (the latter’s `finding_section()` recomputes the
negative headline from the streams, so a regenerate stays honest).

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
4. **Retrain** PPO on the `z=w` stabilized data `data/stabilized/1190MS_z_<w>.txt` (`n_gen=3`); from
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
greedy path to all-length-1. Coverage is measured on the **261 minimal-form class reps** (baseline
runs on them too and may legitimately solve some — the control): a verified rep-solve establishes its
**AC class** is trivial (verified, not asserted), but is **not** by itself an MS-benchmark solve
outside the 640 (that needs a separate MS-member→rep path). `z∈{x,y}` regressions read as
pre-registered alias artifacts; no silent truncation.

---



## Reuse map (what existing code we lean on)

- `greedy_search.ipynb` — algorithms (Booth, reduce, inverse, canonical, best-first
`ACRelatorSolver`, `MS(n,w)`, `counterexamples`) generalized into `greedy_nrel.py`.
- `data/1190MS.txt` — the benchmark, loaded directly (env int format).
- `data/ms_unsolved_reps/ms_reps_unsolved.txt` — the **261 minimal-form representatives** of the unsolved
AC-equivalence classes (one per class; the headline coverage target), built + round-trip-verified
by `scripts/build_ms_reps.py` from `data/ms_unsolved_reps/ms_reps_unsolved.csv` (`r1, r2, name`; word convention
`x→1, X→-1, y→2, Y→-2`). Provenance/label map: `data/ms_unsolved_reps/ms_solved_grid.csv` (the mentor's full MS grid
— 640 `trivial` cells + the 261 class labels, verified this session to bijection with the reps).
- `ppo_checkpoints/610model/` + `scripts/check_checkpoint_paths.py` +
`beam/beam_search.py` — RL/beam labels for Phase 0, unchanged.
- `ppo_ac_s.py:362-371` — the W&B init pattern (lazy import, gated, tags/name/config) reused
for `run_experiment.py`.
- `envs/utils.py` padding/packing helpers — referenced as the spec for the n-relator
converters (not imported; kept independent to avoid touching the shipped env in this phase).

---



## Execution order

1. `jsonl_io.py` — the resumable-JSONL helpers first (every sweep below depends on them).
2. Phase 1 `stabilize.py` — write the `data/stabilized/1190MS_z_{x,y,r1,r2}.txt` datasets (+ validation).
3. Phase 2 `greedy_nrel.py` + visited-block + **5-step pre-flight (checks 0–4)** — rotation-correct
  first, then n=2, n=3 with `z=w`, content-vs-trivial, block-holds (incl. 2-step revert).

2.5. Phase 2.5 `calibrate.py` — warm up numba, probe ~5 hard (unsolved, `n=3`) + ~5 easy cases →
   `results/calibration.jsonl` + projected hours; **pick the** `{small, large}` **node budgets** and
   worker count that feed steps 4–5. (Needs the solver from step 2; must precede the full sweeps.)
3. Phase 0 `categorize.py` — build `labels_1190.json` (index-derived `paper_reference`; no
   compute; `rl_610model`/`beam_610model` null here — no JAX).
4. Phase 0.5 `categorize.py --greedy` — two `n=2` sweeps: the **sum-capped** reproduction gate
   → `results/greedy_reprogate_{100k,1m}.jsonl` (replay-triage gate at the idx-640 boundary) and
   the **per-relator-capped** cross-arm baseline → `results/greedy_baseline_{100k,1m}.jsonl`
   (metrics: **path length** + **node usage**). Both resumable, small tier over all 1190 then large
   tier over the still-unsolved.
5. Phase 3 `run_experiment.py` — **run the 261-rep coverage test first** (the cheap headline):
   baseline on `data/ms_unsolved_reps/ms_reps_unsolved.txt` + `z=w` arms on `data/stabilized/ms_reps_unsolved_z_<w>.txt`
   → `results/greedy_{baseline,z_<w>}_reps_{100k,1m}.jsonl` (class `name` per line). Then the full
   MS(1190) arms `{x,y,r1,r2}` → `results/greedy_z_<w>_{100k,1m}.jsonl` for efficiency/regression on
   the solved set and the direct idx-≥640 coverage claim. All resumable; `viz.py` + W&B.
6. `README.md` with reproduce commands. Leave Phase 4 (and the RL/beam labels) as spec.

---



## Background & rationale (extra detail)

*Reference only — the phases above are self-contained; this records the "why" behind them.*
Sources: `literature/txt/change_of_variables_stable_ac.txt`,
`literature/txt/mentor_email_stable_ac_ideas.md`, and Lucas's 2026-07-02 follow-up.

**Mentor's decision (2026-07-02) — this plan implements it.**

- **Skip trivial** `z`**.** A *trivial* stabilizer (`z = 1`) is a confirmed dead end for greedy
(see the caveat below) — so we go straight to `z = w(x,y)`.
- **Start with the dumbest words**, not clever ones: `w ∈ {x, y, r1, r2}` (4 words). Build the
*pipeline* first; searching for the *best* `w` is the next plan.
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

**Why** `z = r1` **is non-vacuous (not the trivial z we discarded).** `z = r1` is *group*-trivial
(`r1 = 1`, so `z = 1` in the group) — but the **word-level** z-relator `z·r1⁻¹` shares all of
r1's letters with r1/r2, so substitution can swap the whole word `r1 ↔ z`, a move the
2-generator presentation doesn't have. `z = x` / `z = y` likewise hand the search a named
single-generator alias. The content is in the *word*, not the group.

**Scope.** Greedy + categorization only; the RL/beam-on-3-generators path stays deferred to
**Phase 4** (large subproject — technical reasons there). Greedy (`greedy_search.ipynb`,
GS-Sub) is standalone numpy+numba (no JAX/env/checkpoint) — the fastest route to a real
signal.

**Caveat this plan is built around — why trivial** `z` **was dropped.** A substitution only fires
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