# ATP oracle pilot (ESCAPE_PLAN.md track T6)

Prover9 has no length-monotonicity constraint the way the greedy/CoV searches do, so it is an independent, non-monotone way to look for AC-trivializations. This is a feasibility pilot, not a production search: encode a handful of instances, run Prover9 under a hard per-instance timeout, and see what comes back.

**Any "THEOREM PROVED" from this module is a LEAD, never a solve claim** (ESCAPE_PLAN.md "Advisor reconciliation" item 1). A Prover9 proof object is a first-order refutation trace through the axioms below — it is not yet a Definition 2.1 move sequence, and turning it into one (then replaying it through `verify_results.py`, independently, twice, per the advisor's standing rule) is future work this module does not attempt.

## Files

- `encode.py` — `build_ig_problem(name, r1, r2, timeout_s)` builds the Prover9 input text for one presentation.
- `run_prover9.py` — CLI: encode + run `/opt/homebrew/bin/prover9 -f` under a per-instance timeout, classify the outcome, append one jsonl row to `results/stable_ac/atp/prover9_pilot.jsonl`, save the full Prover9 stdout (proof included, when found) under `results/stable_ac/atp/runs/<name>.{p9,out}`.
- `README.md` — this file.

## Primary source

`literature/txt/lisitsa_parametric_ac_aitp2023.txt` and `literature/txt/lisitsa_parametric_ac_simplifications_ii.txt`, read in full. The AITP 2023 abstract states the headline result (`M_n(w*)` trivialized for n=3..6 via Prover9) but not the encoding; the "…, II" extended version (section 1, lines 78–158) is where the actual first-order translations are defined, and section 2 (lines 173–236) is where the paper says which encoding produced which result.

## AC-move numbering (the AC1↔AC2 trap)

The two Lisitsa papers read here use **AC1 = invert relator, AC2 = replace `r_i` by `r_i·r_j`, AC3 = conjugate, AC4 = stabilize** (both txt files, lines 28–34 and 49–52 respectively — identical wording in both). This is consistent between the two papers actually read for this task. The advisor's warning that "Miasnikov/Lisitsa use AC1=invert, AC2=multiply" is exactly this numbering, and it is what both source files use — no renumbering was needed once the primary sources were read directly (the trap is real for anyone working from second-hand paraphrase or a different family of papers; it did not fire here because both txts were read in full and quoted verbatim below).

The actual encoded system is **not** AC1–AC4 directly, but Lisitsa's own term-rewriting formulation `ACT2` / `rACT2` over it (simplifications_ii.txt lines 88–100, 115–125), which is what gets translated into Prover9. Transcribed verbatim:

```
ACT2 (full system, dimension n=2, x/y range over the two relator slots):
  R1L  f(x, y) -> f(r(x), y))
  R1R  f(x, y) -> f(x, r(y))
  R2L  f(x, y) -> f(x . y, y)
  R2R  f(x, y) -> f(x, y . x)
  R3Li f(x, y) -> f((a_i . x) . r(a_i), y)   for a_i in A, i = 1, 2
  R3Ri f(x, y) -> f(x, (a_i . y) . r(a_i))   for a_i in A, i = 1, 2

rACT2 (reduced system used for the actual proofs; Proposition 1: rACT2 and
ACT2 have the SAME transitive closure modulo the group axioms, i.e. dropping
R1R/R3Ri loses no reachability):
  R1L  f(x, y) -> f(r(x), y))
  R2L  f(x, y) -> f(x . y, y)
  R2R  f(x, y) -> f(x, y . x)
  R3Li f(x, y) -> f((a_i . x) . r(a_i), y)   for a_i in A, i = 1, 2
```

`R1L` ~ AC1 (invert, restricted to slot 1), `R2L`/`R2R` ~ AC2 (multiply, either direction), `R3Li` ~ AC3 (conjugate by a generator, restricted to slot 1). `rACT2` drops the slot-2 mirrors (`R1R`, `R3Ri`) — Proposition 1 (proved in the paper, not re-derived here) guarantees this is lossless because the theory is taken modulo the group axioms.

## Encoding chosen: IG (implicational, ground)

The paper names four translations of `rACT2` into first-order logic (simplifications_ii.txt lines 130–158): **EG** (equational ground), **EN** (equational non-ground), **IG** (implicational ground), **IN** (implicational non-ground). Per the task's instruction to implement the one the paper reports strongest results with:

> "These trivializations were found by automated theorem proving using **IG encoding** and Prover9 prover." (simplifications_ii.txt line 177, backing Proposition 5 / Table 1 — the paper's primary reported result table: `M_n(w*)` for n=2..6, 34 to 1282 simplification steps, 0.05s to 10637s.)

IG is also the only one of the four that failed just once in the paper (n=7, line 204) and needed EN/IN as fallbacks there — out of scope for this pilot (2-generator instances only, per the task). EN's n=7 proof needed 892 hand-delemmatized macrosteps before any move sequence could even be read off (lines 217–221); IN was explored afterward as an optimization angle for a *restricted* target (lines 222–236), not reported as the paper's strongest general result. IG is implemented here, faithfully, and is the only encoding this module builds.

Transcribed IG rules (simplifications_ii.txt lines 146–152), `R` a unary "reachable" predicate:

```
I-R1L   R(f(x,y)) -> R(f(r(x),y)))
I-R2L   R(f(x,y)) -> R(f(x . y, y))
I-R2R   R(f(x,y)) -> R(f(x, y . x))
I-R3Li  R(f(x,y)) -> R(f((a_i . x) . r(a_i), y))   for a_i in A, i = 1, 2

Proposition 4: for ground t1, t2:  t1 ->*ACT2/G t2   iff   IACT2 |- R(t1) -> R(t2)
```

`encode.py:RULES` implements exactly these five ground implications (`AC_I_R1L`, `AC_I_R2L`, `AC_I_R2R`, `AC_I_R3L_a`, `AC_I_R3L_b`), each written as a Prover9 clause carrying a `# label(...)` tag naming the rule it came from (for later proof-trace reading — see "Reading a proof trace" below). `TG_AXIOMS` is the standard 5-axiom equational group theory (associativity + two-sided identity + two-sided inverse) needed for Prover9's paramodulation to freely reduce words; this is not itself part of `rACT2`, it is the background theory the paper's `TG` refers to throughout.

Goal: `R(f(a,b))`, i.e. reach the trivial presentation `<a,b|a,b>` — the paper's own chosen normal form (both txt files, e.g. simplifications_ii.txt line 60: "the trivial presentation `<x1,...,xn ; x1,...,xn>`"). No length-bounding trick is used or needed: Prover9 does not enumerate by length at all, it is a resolution/paramodulation prover working from `R(t1)` as a fact and `-R(t2)` as the denied goal, so this pilot is not a length-monotone search in the first place — that is the entire point of running it (ESCAPE_PLAN.md T6: "Prover9 has no length-monotonicity").

## Prover9 syntax notes (verified empirically against the installed 2009-11A binary)

- **Variable convention**: Prover9's default parser treats identifiers starting with `u,v,w,x,y,z` (lowercase) as **variables**, everything else as constants/functions/predicates. The paper's own rule schema uses `x,y` as the meta-variables ranging over presentation slots — kept as-is (they ARE Prover9 variables under the default convention, matching the paper's own notation). The two generators are therefore renamed `a`/`b` (the paper's own letters for its worked `M_n(w) = <a,b|...>` family) to avoid colliding with the reserved variable-letter set. Repo convention maps: `x -> a`, `y -> b`, `X -> i(a)`, `Y -> i(b)`.
- **Exit codes / output strings** (empirically confirmed, `smoke1.p9`–`smoke4_labels.p9` under the job scratch dir): exit `0` + `"THEOREM PROVED"` in stdout = proof found; exit `4` + `"exit (max_seconds)"` = Prover9's own `assign(max_seconds, ...)` fired cleanly, `"SEARCH FAILED"` printed; exit `2` = search space exhausted (`sos` empty) with no proof. `run_prover9.py` classifies on these plus a subprocess-level timeout backstop.
- **Reading a proof trace**: each derived `R(f(...))` line in the `PROOF` section cites a Prover9 inference like `[hyper(13,a,45,a)]`, where `13` is the clause number of the axiom that fired. The axiom clause numbers are stable per generated file (assumptions 1–5 clausify to clauses 12–18 in order: `AC_I_R1L`→12, `AC_I_R2L`→13, `AC_I_R2R`→14, `AC_I_R3L_a`→16 (after an internal associativity rewrite of clause 15), `AC_I_R3L_b`→18 (rewrite of 17)) — so a proof's `hyper(N,...)` chain, read against the `kept:` listing near the top of the file, is directly a trace of which AC-move fired at each step. This is the hook a future move-sequence extractor would use; it is not built here.

## Pilot design

Per the task and ESCAPE_PLAN.md T6:

1. **Sanity target** — a known-easy trivializable presentation, to catch an encoding bug before spending any timeout budget on the real instances. `ms0` = row 0 of `data/ms640_solved.txt` (`r1=YYXyx r2=Yx`, total length 7, the shortest row in the file). Decoded with `run_prover9.load_ms640_row`, using the same `1=x,-1=X,2=y,-2=Y,0=pad` codec as `experiments/run_baseline.py`.
2. **AK(3)** — `r1=xxxYYYY r2=xyxYXY`, direct to trivial, 600s timeout.
3. **Three shortest reps from `data/ms_unsolved_reps/aca_124.csv`** by `|r1|+|r2|`, 600s each.

**Timeout note**: instances 2–5 (AK(3) plus the three `aca_124` reps) were run with `--timeout-s 595`, 5 seconds under the requested 600, purely as a sandbox safety margin — the agent shell enforces a hard 600s ceiling on a single command, and a Prover9 process killed exactly at that boundary risks losing its jsonl row entirely instead of exiting cleanly. Internally `run_prover9.py` reserves a further 5s so Prover9's own `assign(max_seconds, ...)` fires before the outer subprocess-level kill (`prover9_max_seconds` field in each jsonl row = `timeout_s - 5`). The sanity target was run at `--timeout-s 60` and finished in well under a second either way.

**`aca_115` note**: one of the three shortest `aca_124` reps is `aca_115` (`r1=YXYxyx r2=YYYYxxx`, total length 13, class member `13_1`). Per ESCAPE_PLAN.md's advisor reconciliation, `aca_115` is the class believed to correspond to the still-open AK(3) presentation itself — so a "THEOREM PROVED" on `aca_115` would carry the same standing warning as one on the literal AK(3) instance: not a solve claim on its own, requires both independent replay stacks, explicit flagging, never announced on one verifier alone.

## Running it

```bash
.venv/bin/python3 -m experiments.stable_ac.atp.run_prover9 --ms640 0 --timeout-s 60
.venv/bin/python3 -m experiments.stable_ac.atp.run_prover9 --pres ak3 xxxYYYY xyxYXY --timeout-s 595
.venv/bin/python3 -m experiments.stable_ac.atp.run_prover9 --csv data/ms_unsolved_reps/aca_124.csv --csv-smallest 3 --timeout-s 595
```

Output: `results/stable_ac/atp/prover9_pilot.jsonl` (one row per instance: `name, r1, r2, encoding, timeout_s, prover9_max_seconds, status, wall_s, prover9_exit, prover9_killed, problem_file, output_file, proof_file, started_at, git_commit`), full Prover9 stdout under `results/stable_ac/atp/runs/<name>.{p9,out}`.

## Pilot results

See `results/stable_ac/atp/prover9_pilot.jsonl` for the raw rows (5 instances, all against `--timeout-s` as noted). Ran on this machine (Apple Silicon, single-threaded Prover9 per instance, 4 instances run concurrently on separate cores for instances 2-5):

| name | r1 | r2 | \|r1\|+\|r2\| | timeout_s | status | wall_s | prover9_exit | given clauses reached | notes |
|---|---|---|---|---|---|---|---|---|---|
| `ms0` (sanity) | `YYXyx` | `Yx` | 7 | 60 | **proved** | 0.047 | 0 (THEOREM PROVED) | 46-step proof, instant | sanity gate passed |
| `ak3` | `xxxYYYY` | `xyxYXY` | 13 | 595 | timeout | 595.12 | — (subprocess-killed) | 59,988 | hard-killed at the wall budget; still mid-search, weight-~82 words being generated |
| `aca_115` | `YXYxyx` | `YYYYxxx` | 13 | 595 | timeout | 595.10 | — (subprocess-killed) | 63,595 | class member `13_1`; see "aca_115 note" above |
| `aca_116` | `YYYXyyX` | `YXXXyxx` | 14 | 595 | timeout | 595.09 | — (subprocess-killed) | 66,656 | hard-killed at the wall budget |
| `aca_117` | `YYYXyyx` | `YXXXyxx` | 14 | 595 | **error (exit 3, `max_megs`)** | 555.17 | 3 | 68,729 (Given=68729, Generated=343702, Kept=79468) | Prover9's own default 500MB memory cap tripped *before* the time budget — a distinct failure mode from the other three, see below |

**Sanity gate**: `ms0` proved in 0.047s (46-step proof, `hyper()` chain traceable to `AC_I_R1L`/`AC_I_R2L`/`AC_I_R2R`/`AC_I_R3L_a`/`AC_I_R3L_b` per the "Reading a proof trace" note above) — the encoding is correct.

**AK(3) / `aca_115` / `aca_116`**: none proved within 595s. All three were still actively exploring when killed (tens of thousands of given clauses processed, `[hyper(...)]` chains still growing, no stall) — this is a genuine "ran out of time," not a dead search.

**`aca_117`**: hit Prover9's default in-process memory ceiling (`assign(max_mem, ...)`, 500 megs by default) at 555s, 40s before the wall budget would have. This is a *different* resource limit than the other three and is easy to raise (`assign(max_mem, N)` in `encode.py`, or pass more RAM on Colab) — worth flagging separately from a genuine time-out because more memory, not more time, is the lever here.

Every `.out` file (raw Prover9 stdout, proof included when found) is saved under `results/stable_ac/atp/runs/`; the `ak3`/`aca_11{5,6,7}` files are 40-50MB each (tens of thousands of derived ground terms).
