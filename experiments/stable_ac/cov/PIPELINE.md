# Change of Variables (CoV)

Question: does starting the greedy from a change-of-variables rewrite of a presentation cost fewer nodes / a shorter path than starting from the presentation itself and does *which* z-word you pick predict that?

**Scope (deliberate).** Subword CoV only (`z_source: subwords`). **Universal CoV is an automorphism**: a z-word that does not occur can only isolate from its own defining relator, and those one-shot outputs are exactly `x ↦ yᵃx^±1yᵇ` / `y ↦ xᵃy^±1xᵇ`. Using automorphisms deliberately is a later, separate question.

## 0. The pipeline in one line

**Enumerate** every candidate z-word from a presentation (§2) → **transform** the pair once per valid `(z_word, iso_gen, iso_index)` (§1) → **search** each transformed start with the ordinary greedy at each budget, alongside an untransformed *control* start (§3) → **log** one jsonl row per start (§4) → **compare** each CoV row's `nodes_explored` / `path_length` against its control.

## 1. The move — `apply_cov_once(r1, r2, z_word, iso_gen)`

1. **Stabilize** — add the defining relator `Zw` (z = w): `(r1, r2, Zw)` in F₃.
2. **Substitute** — one left-to-right non-overlapping pass replacing `w→z`, `w⁻¹→Z` in both relators, then at most one cyclic-seam wrap on the remaining unconsumed prefix/suffix (relators are cyclic; a match straddling last→first counts), then free reduction; `n_subs` counts replacements.
3. **Isolate** — find a transformed relator with exactly one `±gen` (cyclically) and ≥1 z-letter (`gen` = the `iso_gen` target); solve it as `gen = expr` (expr gen-free).
4. **Destabilize (Lemma 11)** — rewrite every `±gen` in the two kept relators with `expr`; drop the isolating relator (it became gen's definition). Hard assert: no `±gen` survives.
5. **Relabel** — map the two survivors back to (x, y).

`iso_index` names the consumed relator (0 = r1′, 1 = r2′); the other transformed relator and `Zw` survive — so in subword mode one output is always `Zw` itself, rewritten and relabeled, which is why `|w|` drives output size. **Both** r1′ and r2′ may isolate the same target: those are two different coordinate changes, so `iso_index` is part of the row key and `cov_branches` returns them all (`apply_cov_once` keeps first-wins only for single-transform callers). One z therefore gives up to four starts — `iso_gen` × `iso_index` — with the two `iso_gen` halves tied by an exact x↔y swap symmetry (`test_xy_symmetry_oracle`).

Worked example (golden, AK(3), z = xyx, x-elim): `(xyxYXY, xxxYYYY)` → substitute: r1′ `zYXY` (1 sub) → isolate x: `x = YzY` → destabilize: `(YzYYzYYzYYYYY, ZYzYzY)` → relabel: `(XyXXyXXyXXXXX, YXyXyX)`.

## 2. The z family — subwords (`subnc2pxysb`)

Every distinct cyclic subword of r1 & r2 (seam included), at **every** length, pure powers included, `w ~ w⁻¹` deduped to `max(w, w⁻¹)`, deterministic `(length, tuple)` order (that order is the row identity). There is no `|w|` knob — the family is a pure function of the presentation. AK(3): 38 z-words → 34 valid starts + 1 control = 35 rows.

**The no-collapse gate is the only length rule.** A z is judged by what its substitution does to *every* relator, never by which relator it was read from: drop `w` if it takes some relator to fewer than 3 letters. A relator collapsed to length 2 is the two-letter isolator `z^η·a^ε` — exactly the hypothesis of the relator-minus-one factorization theorem (`literature/proofs/PROOFS.tex` §minus-one), which proves that branch is an ordinary rank-two substitution plus a signed rename. It reaches nothing the greedy could not walk to itself, so it is not a new coordinate system — the only thing a CoV is for. Collapse to ≤1 letter is the same degeneracy one step further (a primitive output solving in ~1 node).

Worked: `r1 = xyxxy`, `r2 = yxxy`, `w = yxx`. Here `|w| = 3 = |r1|-2`, a legitimate interior subword of r1 (`→ xzy`) — but `w` also occurs in r2 and takes it to `zy`, so `w` is dropped. Its outputs would have been `(yx, YYXY)` and `(X, YYx)`: primitive relators, i.e. free solves. This is why a per-relator `|w| ≤ |r|-2` bound is not sufficient — and why none is necessary: `|w| = |r|-1` collapses that relator to 2 and `|w| = |r|` collapses it to 1, so the gate strictly contains that rule. Measured over the 66-row benchmark through `enumerate_cov` itself, the gate takes 7999 rows → 6722 while keeping 469 of 473 Aut-orbits, and cuts primitive-output rows from 25 to 12. The 4 forfeited orbits *are* genuinely distinct Aut-orbits, but they are the theorem's `σ(R, S*)` with `(R,S) ~AC (R,S*)`: AC-equivalent to a relabeling of the input, so a CoV to them duplicates an ordinary-AC path rather than opening a disconnected region. (AC-equivalent is not the same as reachable within a node budget — that is the open question, not something the theorem settles.)

A candidate is also dropped when: `|w| < 2` after free reduction (a rename, not a CoV) · no occurrence · no relator isolates for that target · a relator comes back empty · any output relator > `reject_len` (239 = fast-solver cap 255 − headroom 16 — structural only, never a length prior: long starts hold some solves).

## 3. One run (`experiment_length: true` — the only mode we run)

Per presentation: one **control** row (`z_word: null`, original pair, cap 24), then one row per valid `(z_word, iso_gen, iso_index)` — every z, both elimination targets, **and every isolating branch**. When both r1′ and r2′ isolate the target they are two different coordinate changes with different outputs, so `iso_index` is part of the key, not a logged passenger: taking only the first would let candidate order pick the row (on 521, `z=yy`/`iso=y`, first-wins returns a total-30 start and discards the total-16 one), and would bias any z→outcome correlation by a branch nobody chose. Enumerating branches costs +104 rows and buys **+75 Aut-orbits** (394 → 469). Every row is searched by the ordinary greedy at each `budget`; **one jsonl file per budget**. Resume skips finished keys — a 3-field key would collide the two branches and silently lose one. A CoV row runs at `cap = max(24, longest transformed relator + 16)` (`cap_headroom`). `mode: baseline` (identity transform, `covbase_` files) exists for A/B comparison.

**Interpretation caveats (rigor):**

- A valid CoV row can still be a **pure relabel** of its input: w = a relator minus one cyclic letter with a single occurrence returns the original pair up to letter names (`test_subword_relator_minus_one_boundary`). Whether a row genuinely left the input's Aut(F₂)-orbit is decided by `aut_canon` (`equivalence_classes/lib/autcanon.py`) on the two pairs — never by `n_subs` or `iso_index`.
- One-shot only (case i): the CoV is applied to the start, never during the search. `n_cov` is an int so case (ii) — CoV as a search move — can extend the schema later.



## 4. The output row (jsonl — one JSON object per line)


| group      | fields                                                                                                                                                                                                                                                                                            |
| ---------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| identity   | `pres_id` (CSV id or name) · `z_word` (null = control) · `iso_gen` ("x"/"y"; null = control) · `iso_index` (0 = r1′, 1 = r2′; null = control) · `node_budget` · `source` (which CSV)                                                                                                                                                               |
| transform  | `mode` ("cov") · `n_cov` (0 = control, 1 = CoV) · `cov_applicable` · `n_subs` · `r1_orig`/`r2_orig` (input pair) · `r1`/`r2` (pair actually searched) · `start_total_length_orig`/`_cov` · `max_relator_length_cap` · `cyclic_reduce`                                         |
| outcome    | `solved` · `nodes_explored` · `path_length` · `min_relator_length`/`min_relator` (shortest total reached / that pair) · `max_relator_length`/`max_relator` · `max_relator_length_expanded`/`max_relator_expanded` · `time_seconds` · `path_moves` (solved rows only; **transformed** coordinates) |
| provenance | `git_commit` (never part of identity) · `family_tag` (the rule that made the row) |

| orbit | `aut_canon_orig` · `aut_canon_cov` — Aut(F₂)-orbit canonical reps of the input and of the searched pair. **Same orbit ⇔ the reps are equal**, which is the only sound test of whether a CoV changed coordinates at all. |

Why the reps and not a `same_aut_orbit` bool: the bool is their equality (derivable from the same row, like any `*_len`), while the reps also let analysis **count and group** distinct orbits. This is the field that stops the sweep lying to you — on AK(3), 30 of 34 CoV rows are the input relabeled and the whole family reaches only **2** distinct orbits, which no amount of staring at `n_subs`, `iso_index` or start length would reveal. Cost ~2 ms/row (24 ms worst), ~30 s over a 6722-row sweep — nothing beside the searches. `aut_canon` truncates at `level_cap` in principle; `test_aut_canon_cap_does_not_truncate_on_this_data` pins that it does not here (measured 0/150 on the longest outputs, rep identical at cap 50k and 400k). If that test ever fails these fields become cap-dependent approximations and must move to an analysis pass.

**Deliberately NOT stored** — recoverable from `(r1_orig, r2_orig, z_word, iso_gen, iso_index)` with no search: `expr` (~164 µs/row, ~1 s to rebuild a whole sweep) · any `*_len` (`len()` of a string already in the row, and a stored copy can drift from it).


**Filename = resume identity**: `covsweep_{budget}_{nrows}_subnc2pxysb_mrl{cap}_{cyc}_{dataset-tag}_` plus a creation-date suffix that is **not** part of the key (resume globs the prefix). Every result-changing knob is in the prefix and nothing else — `high_speedup` and `git_commit` are result-neutral and stay out. The family tag is the constant `cov.SUBWORD_FAMILY_TAG`, never rebuilt from config. Different family rules never share a file: `nc2` = the no-collapse gate, `b` = every isolating branch is its own row (pre-`b` files hold only the first branch per `(z, iso_gen)`, a strict subset), and the earlier `sub{K}pxys` files bounded `|w|` by a fixed global K instead (`s` = cyclic-seam substitution; pre-`s` `sub{K}pxy` files are a narrower transform still).

## 5. Config (`config_cov.yaml` over `COV_DEFAULTS`)


| knob                 | default                 | meaning                                                               |
| -------------------- | ----------------------- | --------------------------------------------------------------------- |
| `datasets`           | subset_10 + reach_1     | benchmark CSVs (one presentation per row)                             |
| `budgets`            | `[100, 1000]`           | node budgets; local hard cap 1000, production (50000) Colab-only      |
| *(no length knob)*   | —                       | family = every subword, gated only by no-collapse (§2)                 |
| `max_relator_length` | `24`                    | base/control cap (ms640 layout)                                       |
| `cap_headroom`       | `16`                    | slack above the longest transformed relator                           |
| `reject_len`         | `239`                   | structural ceiling (see §2); changing it bumps the family             |
| `cyclic_reduce`      | `true`                  | cyclically reduce outputs before search                               |
| `high_speedup`       | `true` (yaml)           | compact fast solver + slow re-solve for paths; result-neutral (~2.9×) |
| `out_dir`            | `results/stable_ac/cov` | output namespace                                                      |
| `resume`             | `true`                  | skip rows already in the target jsonl                                 |




## 6. Running it

Local proof (≤ 1000 nodes), then always verify certificates:

```bash
.venv/bin/python3 -m pytest experiments/stable_ac -q
.venv/bin/python3 -m experiments.stable_ac.cov.run_cov --experiment-length --budget 100 1000
.venv/bin/python3 -m experiments.stable_ac.verify_results results/stable_ac/cov
```

Production (Colab, `cov_baseline.ipynb` — re-open from GitHub after any push; edit only the CONFIG cell): `BUDGET=[50000]`, `MODE="cov"`, `EXPERIMENT_LENGTH=True`, `Z_SOURCE=None`, `DATASETS=[benchmark_subset_60.csv, reach_tier_6.csv]` → `covsweep_50000_66_subnc2pxysb_...` (6722 cov rows + 66 controls = 6788 per budget, from enumeration; re-measure after a fresh sweep). Resume is per-row: rerun the RUN cell; copy the jsonl to Drive periodically and back before resuming on a fresh VM.

## 7. Known limitations

- One-shot (case i) only; case (ii) — CoV during search — is the designed extension not yet implemented.
- Post-hoc selectors (argmin-length start, top-k beam, oracle) are derivations over a sweep file, not shipped modes; budget-invariance (budget B = first B pops) makes one 50k sweep yield every budget ≤ 50k.
- W&B mirroring deferred until a production selector exists (jsonl is source of truth).

