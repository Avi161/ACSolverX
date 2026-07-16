# Change of Variables (CoV)

**What we do.** One move — the Lemma-11 substitution-and-removal ("change of variables",
`literature/txt/change_of_variables_stable_ac.txt` §3.1; Lemma 11 = arXiv:2408.15332) —
applied **once** to a presentation, using only words that **occur in its relators**. The
ordinary numba greedy then searches each transformed pair next to an untransformed
control. The question: does a single occurrence-based CoV let greedy solve, or descend
below, what the control cannot?

**Legality.** Stabilize (z = w) → AC moves → Lemma-11 destabilize is a stable-AC
equivalence: the output is stably AC-equivalent to the input, so a greedy solve of the
output certifies the input **stably** AC-trivial. `path_moves` are in transformed
coordinates.

**Scope (deliberate).** Subword CoV only (`z_source: subwords`). **Universe mode is
parked**: a z-word that does not occur can only isolate from its own defining relator,
and those one-shot outputs are exactly the automorphisms `x ↦ yᵃx^±1yᵇ` /
`y ↦ xᵃy^±1xᵇ` — a re-coordinatisation of the same problem, not new stable-AC content.
Likewise parked: the fixed zf1/zf2 families and the AK(3) universal-move study
(`ak_3_universal_test/` — its results stand in its RESULTS.md). Code and old result
files remain; nothing new runs them. How to use automorphisms deliberately is a later,
separate question.

Codec everywhere: `1=x, -1=X, 2=y, -2=Y, 3=z, -3=Z` (capital = inverse).
Code: `cov.py` (transform) + `run_cov.py` (runner).

## 1. The move — `apply_cov_once(r1, r2, z_word, iso_gen)`

1. **Stabilize** — add the defining relator `Zw` (z = w): `(r1, r2, Zw)` in F₃.
2. **Substitute** — one left-to-right non-overlapping pass replacing `w→z`, `w⁻¹→Z` in
   both relators, then free reduction; `n_subs` counts replacements. (Linear scan: an
   occurrence straddling the stored cyclic seam is not matched — sound, weaker.)
3. **Isolate** — find a transformed relator with exactly one `±gen` (cyclically) and ≥1
   z-letter (`gen` = the `iso_gen` target); solve it as `gen = expr` (expr gen-free).
4. **Destabilize (Lemma 11)** — rewrite every `±gen` in the two kept relators with
   `expr`; drop the isolating relator (it became gen's definition). Hard assert: no
   `±gen` survives.
5. **Relabel** — map the two survivors back to (x, y).

`iso_index` records the consumed relator (0 = r1′, 1 = r2′); the other transformed
relator and `Zw` survive. One z gives up to two starts (`iso_gen` = "x"/"y"), tied by an
exact x↔y swap symmetry (`test_xy_symmetry_oracle`).

Worked example (golden, AK(3), z = xyx, x-elim): `(xyxYXY, xxxYYYY)` → substitute:
r1′ `zYXY` (1 sub) → isolate x: `x = YzY` → destabilize: `(YzYYzYYzYYYYY, ZYzYzY)` →
relabel: `(XyXXyXXyXXXXX, YXyXyX)`.

## 2. The z family — subwords (`sub4pxy`)

Every distinct cyclic subword of r1/r2 (seam included), length 2..`subword_max_len`
(= 4), pure powers included, `w ~ w⁻¹` deduped to `max(w, w⁻¹)`, deterministic
`(length, tuple)` order (that order is the row identity). ~18 starts per presentation
on the benchmark.

A candidate is dropped when: `|w| < 2` after free reduction (a rename, not a CoV) · no
occurrence · no relator isolates for that target · a relator comes back empty · any
output relator > `reject_len` (239 = fast-solver cap 255 − headroom 16 — structural
only, never a length prior: long starts hold some solves).

## 3. One run (`experiment_length: true` — the only mode we run)

Per presentation: one **control** row (`z_word: null`, original pair, cap 24), then one
row per valid `(z_word, iso_gen)`. Every row is searched by the ordinary greedy at each
`budget`; **one jsonl file per budget**. Row key = `(pres_id, z_word, iso_gen)`; resume
skips finished keys. A CoV row runs at `cap = max(24, longest transformed relator + 16)`
(`cap_headroom`). `mode: baseline` (identity transform, `covbase_` files) exists for A/B
comparison.

**Interpretation caveats (rigor):**

- A valid CoV row can still be a **pure relabel** of its input: w = a relator minus one
  cyclic letter with a single occurrence returns the original pair up to letter names
  (`test_subword_relator_minus_one_boundary`). Whether a row genuinely left the input's
  Aut(F₂)-orbit is decided by `aut_canon` (`equivalence_classes/lib/autcanon.py`) on the
  two pairs — never by `n_subs` or `iso_index`.
- One-shot only (case i): the CoV is applied to the start, never during the search.
  `n_cov` is an int so case (ii) — CoV as a search move — can extend the schema later.

## 4. The output row (jsonl — one JSON object per line)

| group | fields |
|---|---|
| identity | `pres_id` (CSV id or name) · `z_word` (null = control) · `iso_gen` ("x"/"y"; null = control) · `node_budget` · `source` (which CSV) |
| transform | `mode` ("cov") · `n_cov` (0 = control, 1 = CoV) · `cov_applicable` · `iso_index` (0/1) · `n_subs` · `r1_orig`/`r2_orig` (input pair) · `r1`/`r2` (pair actually searched) · `start_total_length_orig`/`_cov` · `max_relator_length_cap` · `cyclic_reduce` |
| outcome | `solved` · `nodes_explored` · `path_length` · `min_relator_length`/`min_relator` (shortest total reached / that pair) · `max_relator_length`/`max_relator` · `max_relator_length_expanded`/`max_relator_expanded` · `time_seconds` · `path_moves` (solved rows only; **transformed** coordinates) |
| provenance | `git_commit` (never part of identity) |

**Filename = resume identity**: `covsweep_{budget}_{nrows}_sub{K}pxy_mrl{cap}_{cyc}_{dataset-tag}_`
plus a creation-date suffix that is **not** part of the key (resume globs the prefix).
Every result-changing knob is in the prefix and nothing else — `high_speedup` and
`git_commit` are result-neutral and stay out. Different family rules never share a file.

## 5. Config (`config_cov.yaml` over `COV_DEFAULTS`)

| knob | default | meaning |
|---|---|---|
| `datasets` | subset_10 + reach_1 | benchmark CSVs (one presentation per row) |
| `budgets` | `[100, 1000]` | node budgets; local hard cap 1000, production (50000) Colab-only |
| `subword_max_len` | `4` | K — the family's only identity knob |
| `max_relator_length` | `24` | base/control cap (ms640 layout) |
| `cap_headroom` | `16` | slack above the longest transformed relator |
| `reject_len` | `239` | structural ceiling (see §2); changing it bumps the family |
| `cyclic_reduce` | `true` | cyclically reduce outputs before search |
| `high_speedup` | `true` (yaml) | compact fast solver + slow re-solve for paths; result-neutral (~2.9×) |
| `out_dir` | `results/stable_ac/cov` | output namespace |
| `resume` | `true` | skip rows already in the target jsonl |

## 6. Running it

Local proof (≤ 1000 nodes — repo hard cap), then always verify certificates:

```bash
.venv/bin/python3 -m pytest experiments/stable_ac -q
.venv/bin/python3 -m experiments.stable_ac.cov.run_cov --experiment-length --budget 100 1000
.venv/bin/python3 -m experiments.stable_ac.verify_results results/stable_ac/cov
```

Production (Colab, `cov_baseline.ipynb` — re-open from GitHub after any push; edit only
the CONFIG cell): `BUDGET=[50000]`, `MODE="cov"`, `EXPERIMENT_LENGTH=True`, `Z_SOURCE=None`,
`DATASETS=[benchmark_subset_60.csv, reach_tier_6.csv]` → `covsweep_50000_66_sub4pxy_...`
(1,184 starts + 66 controls, ~2–3 h). Resume is per-row: rerun the RUN cell; copy the
jsonl to Drive periodically and back before resuming on a fresh VM.

## 7. Known limitations

- Linear-scan substitution misses seam-straddling occurrences (sound, weaker).
- One-shot (case i) only; case (ii) — CoV during search — is the designed extension.
- Post-hoc selectors (argmin-length start, top-k beam, oracle) are derivations over a
  sweep file, not shipped modes; budget-invariance (budget B = first B pops) makes one
  50k sweep yield every budget ≤ 50k.
- `path_length` is in transformed coordinates — not directly comparable to baseline rows.
- W&B mirroring deferred until a production selector exists (jsonl is source of truth).
