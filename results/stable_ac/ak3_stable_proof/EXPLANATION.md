# AK(3) stable-triviality campaign — implementation design

*What the pipeline actually computes, how the pieces fit, the exact configs of the five Colab
boxes, why a run takes hours, and what triggers a theorem. Assumes you know AC / stable-AC.
This is about the **code**, not the math. Companion to [`PLAN.md`](../../../experiments/stable_ac/ak3_stable_proof/PLAN.md)
and [`RESULTS.md`](../../../experiments/stable_ac/ak3_stable_proof/RESULTS.md).*

---

## 0. The object we are trying to emit

Everything in this repo exists to produce **one machine-checkable certificate**:

```
AK(3)  --stabilize(z=w)-->  S₀  --substitution*-->  S  --eliminate(Lemma 11)-->  E  --substitution*-->  ⟨x,y|x,y⟩
   (2 gens)                    (3 gens)                        (2 gens, "fresh quotient")           (trivial)
```

The bet: plain greedy dies on the 3-gen stabilization (no destabilize move → plateaus at total
length 13). But **every visited 3-gen state `S` with a generator occurring exactly once in a
relator** admits a Lemma-11 elimination `S → E`, and `E ~stAC~ AK(3)` by construction. The `E`'s
are **2-gen presentations of the trivial group that were never in anyone's search space**, and
2-gen trivial-group presentations are *empirically* often plain-greedy-easy (all 151 certified
Wirtinger catalog leaves solved). So: **mine millions of `E`'s, greedy each, and one lucky solve
back-substitutes into the full chain above.** That is Lane D. D1/D2/D3 are Lane D at scale; B and
C are two other attack shapes.

The rest of this doc is the machinery that makes that concrete and crash-safe.

---

## 1. The core solver — `NRelatorSolver` (`one_generator/greedy_nrel.py`)

Everything (harvest, solve, floor census, MITM, Lane C) is built on one best-first searcher.

- **State encoding.** A presentation is a `\x00`-joined **byte key**. Each relator is
  Booth-canonicalized (`canonical_relator` = min over cyclic rotations of the word *and* its
  inverse, under the paper letter order `Z<z<Y<y<X<x` via `_paper_lt`), then encoded with
  `_INT_TO_RANK_BYTE`. That byte map is **monotone with the paper order**, so a raw `bytes`
  compare *is* a paper-order lex compare — canonicalizing and sorting relators needs no int
  decoding. `key = b"\x00".join(_relator_bytes(canonical_relator(r)) for r in state)`, relators
  sorted by `(len, bytes)`. `0x00` is reserved as the separator (letter bytes are 1..6).
  Constants: `L = 24` (per-relator cap), `INT = int64`, `NGEN_MAX = 3`.

- **Search.** Best-first over **total relator length** — heap tuples `(total_len, depth, key)`
  (this is the GS-Sub "shrink the presentation" heuristic, not an A* cost). `max_nodes` counts
  **pops** (expansions), not pushes. `visited: key → parent_key` — **moves are not stored** (re-derived
  at retrace, to halve memory). `min_total_len` / `min_total_state` track the shortest presentation
  ever seen. **Termination:** a popped state with every relator length 1 (`all(len(r)==1)`) →
  trivial → `_retrace`.

- **Neighbours (`get_neighbors`)** — the substitution supermove, enumerated in a *fixed* order that
  the fast path must reproduce byte-for-byte: for each unordered pair `a<b`, each `c ∈ {r_b, r_b⁻¹}`,
  each rotation `i` of `r_a` and `j` of `c`, if the junction letter cancels
  (`r_a[last] == -c[first]`) emit `neighbour = reduce(roll(r_a,i) · roll(c,j))` **into slot a, then
  into slot b**; drop empties and any child relator of length ≥ `max_len`. `move = (idx, i, j,
  c_is_inv)`.

- **The numba hot path (`one_generator/expand_fast.py`).** ~60 % of a Python-path node was
  `_relator_bytes(canonical_relator(...))` + `get_neighbors`. `expand_into(key, n_gen, max_len)`
  does the whole per-node loop in one `@njit` call — decode key → replay the exact `get_neighbors`
  order → canonicalize only the changed relator → assemble each child's key + incremental total
  length — writing into preallocated module buffers (`_OUT_KEYS/_OUT_KLEN/_OUT_TL`, `MAXCHILD=8192`)
  that `solve()` iterates directly (no per-node Python list; heap + `visited` stay in Python). It
  engages only when `not track_reverts and not track_seen` (those diagnostics need per-neighbour
  move tuples). **≈5.7× on both the n=2 solve and the n=3 harvest greedy.**

- **Verification ladder.** `_retrace` walks parent pointers and re-derives each move by matching
  `get_neighbors(prev)` against the next key. `verify_path` independently replays a stored path —
  but it *shares* `get_neighbors`, so it catches search/retrace bugs, **not** a move-gen bug (the
  JAX env gold gate is N/A for n≥3, documented). `expand_fast` is gold-gated the strong way: a
  **byte-for-byte differential** vs the Python path (4000 states each for n=2 and n=3; plus a
  full-solver diff on solved / nodes / visited / min_total_len / retraced path).

---

## 2. Lemma-11 candidate generation (`ak3_stable_proof/stable_moves.py` + `harvest_fast.py`)

**`find_eliminable(state, n_gen)`** → list of `(gen, ri)` where generator `gen` occurs **exactly
once** (either sign) in relator `ri`. Enumeration is **ri-major, gen-minor** (this order is
load-bearing — `harvest_fast` mirrors it so provenance `(gen, ri)` is reproducible).

**`eliminate(state, n_gen, gen, ri, l_cap)`** — the destabilization:
1. if the sole occurrence is `-gen`, invert relator `ri` so it's `+gen`;
2. rotate `ri` so `gen` sits at index 0 → `r = [gen] + v`;
3. `gen := v⁻¹` (`sub = inverse_word(v)`), substitute into **every other** relator, `cyclic_reduce`;
4. raise `LengthCapExceeded` if any grows past `l_cap` (candidate discarded);
5. `renum`: shift every generator id `> gen` down by 1 → survivors are `1..n_gen-1`;
6. return `(new_state, n_gen-1, step)` with `step = {type:"eliminate", gen, ri, inverted, rot, sub}`
   — a JSON-ready cert record that lets a verifier redo the exact elimination.

`stabilize(state, n_gen, w)` is the inverse direction (append `z·w⁻¹`, `z = n_gen+1`);
`invert_move` is plain AC2 (used only for the certificate's sign-fix tail).

**`harvest_fast.harvest_visited(visited, l_cap, htl_cap)`** — the numba harvester. It iterates
**every canonical key in a finished greedy run's `visited` set** and, per state, runs `_harvest_key`
(an `@njit` transcription of `find_eliminable`+`eliminate` that reuses the already-jitted
`reduce_relator`/`inverse_relator`/`canonical_relator` — numba dispatchers call each other). Extra
knob vs `eliminate`: `htl_cap` drops any candidate whose two survivors sum longer than the cap.
Cross-state dedup is **first-wins**. Returns `{ck → (relA, relB, gen, ri, src_hex)}` keyed by the
destabilized 2-gen canonical key `ck`; `src_hex` is the 3-gen state that first produced it. Gold-gated
byte-for-byte against the pure-Python `eliminate`+`canonical_key` oracle (this replaced an
82%-of-runtime Python loop; ~1–2 orders of magnitude faster per combo).

---

## 3. The Lane D pipeline (`ak3_stable_proof/plateau_elim.py`)

Three phases, all **append-only JSONL + flush + fsync + atomic `os.replace`**, all resumable, under
`out_dir/laneD/`. Run as `plateau_elim.py --phase all ...`.

### harvest → `cands_<form>_<word>.jsonl`
`phase_harvest` builds the `forms × words` cross product (forms from `--forms`; words from `--words`
or the 8-name `HERO` default). Resume skip = **exact-string membership** in `set(os.listdir(laneD))`
of `cands_<form>_<word>.jsonl` or `.done` — deliberately not `os.path.exists`, because the word bank
has case-variant names (`xxx`/`XXX`) that collide on a case-insensitive FS. Warm-ups
(`gn.solve_one(...,3)` + `hf.warm()`) run **before** the `Pool(maxtasksperchild=1)` fork so children
inherit compiled numba and each combo's peak RSS is released. 90 s daemon heartbeat.

Per combo, `harvest_one` → `run_stabilized(form, w, budget)`: `stabilize_with_word` builds the 3-gen
`z·w⁻¹` presentation, **blocks the trivial-z revert state** (`null_revert_state`, so greedy can't just
undo the stabilization), runs `NRelatorSolver(n_gen=3, max_nodes=budget)`, then
`harvest_visited(solver.visited, l_cap, harvest_tl_cap)`. Record schema (note the field is `cand`,
not yet `mkey`):
```json
{"cand":"<hex 2-gen key>", "relators":[r0,r1], "total_len":N,
 "form":"textbook", "word":"xyx", "src":"<hex 3-gen source key>", "gen":G, "ri":R}
```

### merge → `merged.jsonl`
`merge_one_file` per file (`Pool(merge_workers)`), then a global fold. For each candidate:
drop if `total_len > merge_tl_cap` (24); else compute its **symmetry orbit** and
`mkey = min(orbit).hex()`; drop if the orbit meets `symmetry_keys(AK3) ∪ symmetry_keys(P25)`
(candidate is just AK3/P25 again — no progress). The **symmetry group** quotiented (`mitm.symmetry_keys`):
1. signed generator relabelings — all `2^k·k!` (= 8 for k=2) permutations × per-generator sign flips;
2. per-relator cyclic rotation, 3. per-relator inversion, 4. relator reordering — (2)–(4) are baked
into `canonical_key`. `mkey` = lexicographically smallest key over that whole orbit, so two candidates
are the same class iff their orbits intersect. Global winner per `mkey` = smallest `total_len`. Output
adds `mkey`, ranked `(total_len, mkey)` ascending (shortest-first). **Resume guard:** if `merged.jsonl`
is newer than every `cands_*.jsonl`, skip the re-merge (it's deterministic + idempotent);
`--force_merge` overrides. *(This is why a mid-solve restart re-ran merge once then stopped re-running.)*

### solve → `solve.jsonl` (+ `certs/`)
`phase_solve` resume: `done = { mkey : a solve.jsonl row exists with budget ≥ budget2 }` (a candidate
attempted at a *smaller* budget is re-attempted, not skipped). Selection: stream the already-sorted
`merged.jsonl`, skip `total_len > tl_cap` and `mkey ∈ done`, stop at `top` → i.e. **shortest top-N of
the ≤tl_cap, not-done candidates**. Each runs plain 2-gen greedy at `budget2`
(`Pool(solve_workers, maxtasksperchild=16)`), 60 s heartbeat, prints every 200. Record:
```json
{"mkey","total_len","budget","solved","nodes","min_total_len","wall_s",
 "form","word","gen","ri","src","relators":[r0,r1],
 // if solved:
 "path_states":[[[...],[...]],...], "path_verified":bool,
 // added inline by phase_solve after certifying:
 "cert_verified":bool, "cert_path":"...", "cert_errors":[...]}
```
On any `solved`, `build_chain_cert` runs **synchronously in the parent** (see §4). `--stop_on_first`
terminates the pool after the first certified solve.

---

## 4. The certificate machinery

**`build_chain_cert(solve_rec, budget)`** reconstructs the whole §0 chain, deterministically and from
scratch (so the cert depends only on `(form, word, budget)`, nothing cached):
1. `run_stabilized(form, w, budget)` again; `assert src_key in solver.visited`.
2. `sub_path = solver._retrace(src_key)` — the substitution hops `S₀ → … → S`.
3. Assemble parallel `states` (each `(relators, n_gen)`) and `steps`:
   `AK3(2)` → **stabilize** → `S₀(3)` → **substitution**×(len sub_path) → `S(3)` →
   **eliminate** (`stable_moves.eliminate` at the recorded `gen, ri`) → `E(2)` →
   **substitution**×(greedy path from `solve_rec["path_states"]`) → **invert** tail (sign-fix any
   negative length-1 relator).
4. `make_certificate(..., end_is_trivial=True)`, `verify(cert)` inline, save
   `certs/laneD_<form>_<word>_<mkey[:12]>.json`.

**`certificate.py` (acx-cert-v1).** Fields: `certificate_version:"1"`, `name`, `claim`, `start`, `end`,
`end_is_trivial`, `steps` (len T), `states` (len T+1, each `{n_gen, relators}`), `meta`. Step vocab:
`concat` (AC′1), `conjugation` (AC′2), `stabilize`, `eliminate` (Lemma 11), `relabel`, `substitution`
(the greedy composite, verified by neighbour-membership rather than fixed replay).
`concat_certificates` chains verified certs end-to-end (boundary states must match) — this is how a
**P25-start** Lane D chain composes onto the already-certified 53-move Appendix-F `P25→AK3` bridge to
yield an AK(3) claim (P25 is registered as a start form precisely for this).

**Two independent verifiers** — a solve is only "certified" if both pass:
- `verify_certificate.verify` (engine author's): global L3 invariants over every state (balanced, no
  empty relator, letters in range, `|abelianization_det| == 1` by Bareiss) + per-step recompute-and-
  compare (exact **or** canonical-key equality; `substitution` = neighbour-set membership). **Shares**
  `presentation.py` / `stable_moves.py` with the engine — run inline during `phase_solve`.
- `independent_verifier.py`: **imports nothing** from the engine — reimplements free/cyclic reduce,
  canonicalization, an integer Bareiss det, every step applier, and `substitution_matches` **from the
  spec only** (black-box). Run **out-of-band** (own CLI) before any claim ships. 19/19 existing certs
  pass both.

---

## 5. The five boxes (`ak3_stable_proof/run_lanes.py`, driven by `nb_ak3_lanes.ipynb`)

One Colab runtime per box; each streams resumable JSONL into its own Drive folder.

| Box | Engine | Forms / start | budget (harvest) | budget2 (solve) | top | tl_cap | Role |
|----|--------|---------------|-----:|-----:|-----:|-----:|------|
| **D1** | Lane D | `textbook, p25` | 500k | 50k | 12000 | 20 | Deep dig from the two classic forms. |
| **D2** | Lane D | `rep, floorF` | 500k | 50k | 12000 | 20 | Deep dig from the `rep` form **and floor F** (never swept). |
| **D3** | Lane D | `textbook, rep` + **all 95 bank words** | 200k | 25k | 10000 | 20 | Broad, shallow screen over every `z=w`. |
| **B** | **StableSolver** grid (6 rows) | AK3 / P25 | 800k / 300k | — | — | — | stabilize **and** eliminate *inside* one search, ≤4 gens. |
| **C** | dumb baselines + MITM | AK3 / P25 | 0.8–2M | — | — | — | trivial-z controls + meet-in-the-middle. |

**Worker sizing.** `auto_workers(budget) = min( 0.85·RAM / (0.6 + budget·8e-6),  2·cores )` — model
per-worker RAM as 0.6 GB baseline + ~40×-budget visited set; oversubscribe to 2×cores to hide Drive
FUSE writes; RAM-cap prevents the process-group OOM. Solve/merge workers = all cores (CPU-bound, small
records). *(`run_lanes` now passes `--merge_workers=cores`; it used to fall back to `cpu//2`.)*

**Box B — `StableSolver` (`stable_solver.py`).** The *smart* search: best-first with priority
`(total_len + gen_penalty·(n_gen − base), depth, key)` and **three move families in one search** —
`substitution` (`get_neighbors`), `stabilize` (each bank word, while `n_gen < max_gen`), and
`eliminate` (`find_eliminable`). Unlike plain greedy it *can* destabilize mid-search. `gen_penalty`
(1 or 2) sets how much an extra generator must "pay for itself" in length. Grid rows vary
`(start, budget, max_gen, gen_penalty, bank)`: 4 rows @800k on the `hero8` bank (incl. one `max_gen=4`
and one `gen_penalty=1`), 2 rows @300k on the full 95-word bank. Emits + verifies a certificate on
solve.

**Box C — controls + MITM.** *Dumb baseline* (`lane_worker` laneC): trivial-z stabilization
(`z_i = z_i`, single-letter relators stacked) at `n_gen = 3/4/5`, plain greedy, budgets 2M→0.8M
(smaller as n_gen grows). This is the "no clever word, no destabilize" control. *MITM* (`mitm.py`):
`TargetSolver` searches **outward from AK3/P25**, goal = **membership** in a target set (the
`catalog_leaves.jsonl` Wirtinger leaves, expanded to their full symmetry orbits) rather than "reach
trivial"; it also dumps its entire visited set as a gz "ball" for a future two-sided collision. The
grid wires the outward-vs-static-leaves half (`mitm_out` @2M with ball dumps); the leaf-vs-ball second
frontier (`mitm_leaf`) exists but isn't in the grid.

**Word bank (`ak3_words.build_word_bank`, 95 words).** Families
`relhalf 17 · wk 17 · wstar 5 · conj 14 · comm 6 · ms 3 · brute 33` (+ a driver-added `control` = the
form's own `r1`/`r2`). `wk` = the paper's `y⁻ᵏ·x⁻¹yxy` x-isolation family (k∈[-8,8]); `relhalf` =
relator sides + rotations + inverses (incl. Fagan's `xyxY`); `brute` = all reduced length-1..3 words.
`stabilize_with_word(flat, w)` appends `z·w⁻¹`; pinned byte-identical to the shipped `stabilize_flat`
by a differential gate.

---

## 6. Why a run takes hours (concrete)

Nothing here is I/O- or RAM-bound — it's raw CPU over enormous counts, which is why you see 100 % CPU
at low RAM (optimal, not idle):

- **harvest**: for ~190 (form,word) combos, replay greedy over 200k–500k pops; the `visited` set is
  ~40× the budget in states, and `harvest_visited` runs `find_eliminable`+`eliminate` on **every one**.
- **merge**: `symmetry_keys` (8 relabelings × canonicalization) on **every raw candidate** — D3's run
  was **41,853,063 raw → 87,939 unique**. That flood *is* the merge.
- **solve**: `top ≈ 5–12k` *independent* greedy searches, each up to `budget2` = 25k–50k pops, and
  most run to the **full** budget because they plateau (no early stop). At ~0.5–1.5 candidates/s/box
  that's ~1–3 h per box.

The hot loops are already numba'd (~5.7× solve/harvest, ~9× the merge-adjacent elim pass) and run on
all cores; the remaining wall-clock is just the size of the search.

---

## 7. The structural byproduct — two floors {AK3, F} (`floor_census.py`)

Independent of any solve: take `merged.jsonl` (`total_len ≤ 18`), run plain 2-gen greedy to its plateau
on each, read `min_total_state`, and classify by `floor_mkey = min(symmetry_keys(floor)).hex()`. Over
**1006** candidates the plateau collapses into **exactly two** classes, both at `min_total_len = 13`:
**F = ⟨x,y | y⁻²xyx⁻², y⁻³x⁻²yx⟩ (712, 71 %)** and **AK3's own floor (294)**. `certs/laneF_F_to_AK3.json`
is a **21-substitution-step** chain proving F and the AK3 floor are the same plain-AC class (so it's
"two floors," not two unrelated attractors). F is registered as `FORMS["floorF"]` and is D2's start
form — a brand-new canonical form of AK(3) to attack from.

---

## 8. What happens after the boxes finish

Watch each box's `solve.jsonl` (and B/C's `box_*.jsonl`) for a `*** SOLVED ***`. Two outcomes, both
terminal, both results:

- **Jackpot.** Any candidate greedy-solves → `build_chain_cert` auto-emits the full §0 chain →
  `verify_certificate` inline **and** `independent_verifier` out-of-band. Both pass ⇒ a rigorous,
  reproducible proof that **AK(3) is stably AC-trivial** — settling the question the 2024→2025
  retraction reopened. `concat_certificates` folds a P25-start win onto the Appendix-F bridge.

- **Expected negative.** Nothing solves at 10–40× the local budgets → the campaign closes as a
  **verified negative of unprecedented breadth**: five independent method families (388 z=w greedy
  stabilizations · 1,937 solves over 1,006 fresh Lemma-11 quotients · full StableSolver · trivial-z
  n=3/4/5 · pretrained-policy beam 0/185) **all floor at total length 13**, plus the two-floors theorem
  and F as a new form. Everything stays certificate-grade; any *future* solve still auto-certifies.

**One line:** manufacture provably-AK(3)-equivalent 2-gen quotients by the million, greedy each, and a
single solve back-substitutes into a machine-checked stable-AC trivialization of AK(3). The boxes are
five differently-shaped nets over that space; a hit is a theorem, a miss is the strongest negative on
record.

---

*Code map: solver `one_generator/greedy_nrel.py` (+ `expand_fast.py`); Lemma-11 `stable_moves.py`
(+ `harvest_fast.py`); pipeline `plateau_elim.py`; boxes `run_lanes.py` / `nb_ak3_lanes.ipynb`;
smart search `stable_solver.py`; MITM `mitm.py`; census `floor_census.py`; certs `certificate.py`,
`verify_certificate.py`, `independent_verifier.py`; words `one_generator/ak3_words.py`.*
