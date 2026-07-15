# Change of Variables (CoV)

Implementation reference for the CoV transform and its runner. **Case (i)** only: CoV is
applied **once** to the initial presentation, then the ordinary numba greedy searches the
transformed pair. (`n_cov` is an int so case (ii) — CoV *during* search — can extend the
schema later.) Code: `cov.py` (transform) + `run_cov.py` (runner). Method source:
`literature/txt/change_of_variables_stable_ac.txt` §3.1.

Codec everywhere: `1=x, -1=X, 2=y, -2=Y, 3=z, -3=Z` (capital = inverse). Constants in
`cov.py`: `X_GEN=1, Y_GEN=2, Z_GEN=3, DEFAULT_CAP=24`.

## 1. The transform — `apply_cov_once(r1, r2, z_word, iso_gen)`

Given a pair `(r1, r2)`, a candidate word `w = z_word`, and a target `iso_gen ∈ {"x","y"}`:

1. **Stabilize** — form the defining relator `Zw` (`defining_relator`, cov.py:175). Asserts
   `z = w`; presentation is now `(r1, r2, Zw)` in F₃.
2. **Substitute** — `substitute_word` (cov.py:103): one left-to-right non-overlapping pass
   replacing `w→z` and `w⁻¹→Z` in r1 and r2, then free reduction. Returns transformed
   `r1', r2'` and `n_subs` (total replacements). Linear scan: an occurrence straddling a
   stored relator's cyclic seam is not matched (sound, weaker).
3. **Isolate** — `isolate(relator, x=gen, z=Z_GEN)` (cov.py:130), `gen = X_GEN` or `Y_GEN`.
   Finds a relator with **exactly one ±gen** (on the cyclic reduction) **and ≥1 z-letter**,
   rotates gen to the front (`gen^ε·s`, s gen-free), returns `(True, expr)` where
   `expr = s⁻¹` (ε=+1) or `s` (ε=−1); `(False, ())` otherwise. Candidate order: r1′, r2′,
   then `Zw` itself when `allow_defining_iso`. The z-letter gate rejects isolators that
   would drop gen without using z (dead weight).
4. **Destabilize** — `substitute_generator(keep, gen, expr)` (cov.py:148) rewrites every
   ±gen in the two *kept* relators; the isolating relator is dropped (it became gen's
   definition). Hard `assert`: no ±gen survives.
5. **Relabel** — `relabel(word, iso_gen)` (cov.py:170) maps the survivors back to (x,y):
   x-elim `(y,z)→(x,y)`; y-elim `x` stays, `z→y`.

Returns a `CoVResult`: `.r1, .r2` (2-gen output), `.expr`, `.n_subs`, `.iso_index`,
`.iso_gen`, `.cap`. `iso_index` records which relator was consumed and thus what survives:

| iso_index | consumed           | output pair             |
| --------- | ------------------ | ----------------------- |
| 0         | r1′                | (r2′, Zw) transformed   |
| 1         | r2′                | (r1′, Zw) transformed   |
| 2         | Zw (universe only) | (r1′, r2′) transformed   |

One `z_word` yields up to **two** starts — its x- and y-eliminating outputs (`iso_gen`),
tied by an exact x↔y swap symmetry (`test_xy_symmetry_oracle`). `enumerate_cov`
(cov.py:314) loops z-words × `iso_targets=("x","y")`, dedups on the output pair (x wins
ties). Legality: stabilize→AC-moves→destabilize is the stable-AC equivalence, so a greedy
solve of the output certifies the original. `path_moves` are in **transformed** coordinates.

### Worked example — golden AK(3), z = xyx, x-elim

`(xyxYXY, xxxYYYY)`: substitute `xyx→z` → r1′ `zYXY` (1 sub), r2′ unchanged. Isolate x from
`zYXY`: rotate → `XYzY`, ε=−1 → `x = YzY`. Destabilize r2′ → `(YzY)³YYYY` = `YzYYzYYzYYYYY`;
`Zxyx` → `ZYzYzY`. Relabel → **`(XyXXyXXyXXXXX, YXyXyX)`**.

## 2. The three z families

Deterministic `(length, tuple)` order in all three (this order *is* first-win / row identity).
`w ~ w⁻¹` deduped to `max(w, w⁻¹)`.

| family          | tag       | generator (cov.py)        | z-words                                                                                                                                                    |
| --------------- | --------- | ------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------- |
| naive first-win | `zf2`     | `NAIVE_Z_FAMILY` :82      | **62** words: every canonical **freely + cyclically** reduced (x,y)-word of length 2..4 (6+14+42). Nothing hand-picked, pure powers (xx, yyy…) included.  |
| subwords        | `sub4pxy` | `subword_candidates` :287 | every distinct cyclic subword of r1/r2 (seam included), length 2..`subword_max_len`. Count is per-presentation (~18 starts/pres on the benchmark).         |
| universe        | `uni4xy`  | `universe_candidates` :50 | **78** words: every canonical **freely** reduced (x,y)-word of length 2..`universe_max_len` (6+18+54 at n=4). Superset of zf2; need not occur in the pair. |

`zf2` vs `universe`: same recursion, zf2 additionally keeps only cyclically reduced words
(`w[0] != -w[-1]`), so 62 ⊂ 78. `zf1` (17 hand-picked mixed words) is retired; its files keep
the `zf1` tag and are never resumed by zf2 runs.

The full **zf2** list (canonical rep `max(w, w⁻¹)` per `w ~ w⁻¹` pair, first-win order):

- **len 2** (6): `Xy xx xy yX yx yy`
- **len 3** (14): `XXy Xyy xYx xxx xxy xyx xyy yXX yXy yxx yxy yyX yyx yyy`
- **len 4** (42): `XYXy XYxy XXXy XXyy XyXy Xyxy Xyyy xYYx xYXy xYxx xYxy xxYx xxxx xxxy xxyx xxyy xyXy xyxx xyxy xyyx xyyy yXYX yXYx yXXX yXXy yXyX yXyx yXyy yxYX yxYx yxxx yxxy yxyX yxyx yxyy yyXX yyXy yyxx yyxy yyyX yyyx yyyy`

**subwords vs universe (why both):** under substitution-only rules a word fires only if it
occurs in a relator ("occurs" *is* "is a subword"), so a fixed universe would reproduce the
subword runs exactly. Universe becomes a distinct experiment via `allow_defining_iso`
(`iso_index 2`): a non-occurring word isolates from `Zw` and acts as a pure Nielsen
re-coordinatisation. Overlapping (z_word) rows across the two files are a consistency check.

`xy` suffix = both isolation targets (x and y); `p` = pure powers included. Older rules
(`sub4`, `sub4p`, `uni4`, `zf1`) keep their tags and never share a resume file.

## 3. Config options (`config_cov.yaml`, loaded over `COV_DEFAULTS`)

| knob                 | default                 | what it does                                                                                                                                             |
| -------------------- | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `datasets`           | subset_10 + reach_1     | benchmark CSVs to run (each row = one presentation).                                                                                                     |
| `budgets`            | `[100, 1000]`           | node budgets per row. Local hard cap = 1000; production (50000) is Colab-only.                                                                           |
| `mode`               | `cov`                   | `cov` = transform each start; `baseline` = identity transform (same rows/budgets, comparison file).                                                      |
| `experiment_length`  | `false`                 | `true` = **the sweep**: run greedy from *every* valid CoV start + one control row (`z_word: null`) per presentation.                                     |
| `z_source`           | `subwords`              | sweep family: `subwords` (`sub{K}pxy`) or `universe` (`uni{n}xy`, defining-relator isolation on).                                                        |
| `subword_max_len`    | `4`                     | K for the subword family (z lengths 2..K). Only identity knob of that family.                                                                            |
| `universe_max_len`   | `4`                     | n for the universe family (78 words at 4; grows ~3× per +1).                                                                                             |
| `max_relator_length` | `24`                    | base per-relator cap (ms640 layout). Control/baseline rows run at exactly this.                                                                          |
| `cap_headroom`       | `16`                    | slack above the longest transformed relator. A cov row runs at `cap = max(24, longest+16)` (`max_relator_length_cap`). A relator pinned at the cap can never grow over the hump. |
| `reject_len`         | `239`                   | **structural ceiling only** (fast-solver relator cap 255 − headroom 16). NOT a length prior — long starts hold some solves (629, 539). Changing it bumps the family. |
| `cyclic_reduce`      | `true`                  | cyclically reduce output relators before search.                                                                                                        |
| `high_speedup`       | `true` (yaml)           | route searches through the compact fast solver; re-solve solved rows with the normal solver for their path. **Result-neutral** → not in the filename, resumes across modes. ~2.9× measured. |
| `out_dir`            | `results/stable_ac/cov` | output namespace (never `greedy_baseline/` or `benchmark/`).                                                                                             |
| `resume`             | `true`                  | skip rows already present in the target jsonl.                                                                                                           |

`z_family` is **not** a yaml knob — it lives only in `cov.Z_FAMILY_TAG`; a yaml copy once
shadowed a tag bump (`test_shipped_yaml_cannot_shadow_the_family_tag`).

## 4. Rejection gates

A z candidate is dropped when:

| gate                                | reason                                     |
| ----------------------------------- | ------------------------------------------ |
| `len(w) < 2` after free reduction   | z = x is a rename, not a CoV.              |
| no occurrence AND not universe mode | substitution has nothing to act on.        |
| no relator isolates (per target)    | can't eliminate that generator.            |
| empty relator after destabilization | degenerate presentation.                   |
| any output relator > `reject_len`   | exceeds the packed fast-solver's 255 cap.  |

## 5. The sweep & post-hoc selectors

`experiment_length: true` runs greedy from every valid CoV start plus a per-presentation
control (`z_word: null`, cap 24). Rows keyed `(pres_id, z_word, iso_gen)`, fsynced on write.
Because budget B is the first B pops of any longer search (budget-invariance), one 50k sweep
file yields, with no new runs: solve rate / nodes / path at any budget ≤ 50k; **argmin-length**
selector (greedy from the shortest start); **top-k beam**; the **oracle** (best start per
presentation); and the baseline (control rows). `iso_index`/`n_subs` split occurrence-driven
shrinking (n_subs ≥ 1) from pure re-coordinatisation (iso_index 2, n_subs 0).

## 6. Row schema & filename identity

Greedy schema (`_build_row`) + cov extras. Base fields: `min_relator[_length]`,
`max_relator[_length]`, `max_relator_expanded[_length]`, `nodes_explored`, `solved`,
`path_length`, `path_moves` (transformed coords). Cov extras: `mode` · `z_word` (null =
control) · `n_cov` · `cov_applicable` · `iso_index` (0/1/2) · `iso_gen` (x/y; null = control)
· `n_subs` · `r1_orig`/`r2_orig` · `start_total_length_orig`/`_cov` · `max_relator_length_cap`
· `source` (CSV) · `git_commit` (provenance only).

**Filename = resume identity** (date-less, every result-changing knob and nothing else):
`covsweep_{budget}_{n}_{fam}_mrl24_cyc_{tag}_`, `fam ∈ {sub4pxy, uni4xy}`; plus `cov_...`
(zf2) and `covbase_...` (identity) for the non-sweep modes. `high_speedup` and `git_commit`
are excluded (result-neutral).

## 7. Running it

Local proof (≤ 1000 nodes — repo hard cap):

```bash
.venv/bin/python3 -m pytest experiments/stable_ac -q
.venv/bin/python3 -m experiments.stable_ac.cov.run_cov \
    --experiment-length --budget 100 1000                       # subword sweep
.venv/bin/python3 -m experiments.stable_ac.cov.run_cov \
    --experiment-length --z-source universe --budget 100 1000   # universe sweep
.venv/bin/python3 -m experiments.stable_ac.verify_results results/stable_ac/cov
```

Production (Colab, `cov_baseline.ipynb` — re-open from GitHub after any push; edit only the
CONFIG cell). Both runs: `BUDGET=[50000]`, `MODE="cov"`, `EXPERIMENT_LENGTH=True`,
`DATASETS=[benchmark_subset_60.csv, reach_tier_6.csv]`.

|            | Colab A (subwords)              | Colab B (universe)                        |
| ---------- | ------------------------------- | ----------------------------------------- |
| `Z_SOURCE` | `None`                          | `"universe"`                              |
| file       | `covsweep_50000_66_sub4pxy_...` | `covsweep_50000_66_uni4xy_...`            |
| rows       | 1,184 starts + 66 controls      | 3,615 starts (1,747 y-elim) + 66 controls |
| est. time  | ~2–3 h                          | ~6–9 h (may need one resume)              |

Resume is per-row: rerun the RUN cell, it skips every finished `(pres_id, z_word, iso_gen)`.
The jsonl lives in the ephemeral `/content` clone — copy it to Drive periodically and back
before resuming on a fresh VM.

## 8. Known limitations

- **Linear-scan substitution** misses seam-straddling occurrences (sound, weaker).
- **One-shot (case i)** only; case (ii) — CoV as a search move — is what `n_cov` anticipates.
- **Selector not shipped**: argmin-length / top-k are post-hoc derivations until a 50k sweep
  picks the winner and it becomes a `selector:` mode.
- **`path_length` is transformed-coordinates** — not directly comparable to baseline rows.
- W&B mirroring deferred until the production selector exists (jsonl is source of truth).
