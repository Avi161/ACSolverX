# Replicating Ryan Zang's CoV-gate search

State of the `ryan-replication` branch, written so that someone (or an agent) starting here has the context. The
branch was cut from `elliot-replication`, so it also carries the Elliot work (`docs/ELLIOT_REPLICATION.md`).

**Goal.** Benchmark Ryan Zang's MS640 CoV-gate best-first search on MS640, bench60 and ladder100:

- source: [ryanzang04/Stable-ACSolver](https://github.com/ryanzang04/Stable-ACSolver), `scripts/ms640_cov_gates.py`
  with `scripts/greedy_search_n.py` and `envs/ac_moves.py`, commit `148a3de`, MIT licence;
- all six gates;
- on CPUs with numba, no JAX or GPU;
- exactly the same algorithm (same results), but with **no relator-length limit**, at the user's request.

**No PR, no CI.** Push to `ryan-replication` only.

## The algorithm (as in Ryan's script)

**Search.** Best-first over states (two cyclic relators, canonical form = least rotation of the word or its inverse,
order Y < y < X < x, pair sorted by (length, word)).

- **Heap order:** (total length, depth, insertion order).
- **Each pop:**
  1. Expand every substitution: slot i <- the reduced product rot(r0) * rot(r1^{+-1}), in Ryan's action order.
  2. If the gate opens, also expand every CoV move.
- **Children:** a child is dropped if it equals the parent or is already seen.
- **Nodes:** the count is pops. CoV enumeration is not charged.

**CoV move.** Pick a relator, a generator g and a cyclic window W, such that g occurs once in the rest of the
relator. Set z := W or W^-1, solve that relator for g, substitute into the other relator, and keep (other,
z * z_word^-1). This is the same construction as Elliot's single CoV, so it is always an automorphism of F2, and every
solve is an AC path via Aut. `verify_paths.py` confirms this on every CoV step (Aut-orbit check).

**Gates.** A gate decides whether CoV moves are added at a pop:

| gate | opens when |
|---|---|
| `no_short_sub` | no substitution child is shorter |
| `short_relator` | min relator length <= 3 |
| `unbalanced` | max >= 2 * min |
| `long_presentation` | total length >= 16 |
| `plateau100` | 100 pops without a new best length |
| `periodic10` | every 10th pop |

**Caps.** Ryan caps relators at 24 letters and the total at 48. It also rejects a substitution whose seam-reduced
length exceeds 24 before cyclic reduction. Our kernel keeps these as options (`--max-length 24 --max-total 48`
reproduces Ryan); **runs here use no cap**. Uncapped searches generate relators up to 84 letters.

## Files

| path | what |
|---|---|
| `benchmark/ryan/cov_gates_cpu.py` | pure-Python port (reference); `set_caps(None, None)` removes the caps |
| `benchmark/ryan/cov_gates_numba.py` | numba kernel: variable-length state arena, hash table, packed heap; caps optional, default none |
| `benchmark/ryan/check_port.py` | Python port vs Ryan's JAX code: every child, and whole searches (needs jax 0.6.0) |
| `benchmark/ryan/check_numba.py` | numba kernel vs Python port, `--uncapped` for no caps |
| `benchmark/ryan/run_all.py` | parallel driver: MS640 + ladder100, six gates, hardest rows first; `--only-unsolved-from` |
| `benchmark/ryan/summarize.py` | table; bench60 read off MS640 |
| `benchmark/ryan/verify_paths.py` | independent replay: substitutions as products of rotations, CoV steps in the Aut(F2) orbit |
| `results/ryan_1e5/` | all 4,440 searches at 10^5 pops; `README.md`, `SUMMARY_TABLE.md`, `VERIFY.json` (all pass) |
| `results/ryan_1e6/` | the 171 searches unsolved at 10^5, rerun at 10^6; `VERIFY.json` (all pass) |
| `results/ryan_full_1e6/` | merged full table to 10^6; `README.md`, `SUMMARY_TABLE.md` |
| `benchmark/ryan/merge.py` | carries rows solved at the smaller budget, replaces the unsolved ones by their rerun |
| `ops/aws/` | `env.sh`, `launch.sh`, `ssm-run.sh`, `box_ryan.sh`, `status.sh`, `ledger.md` (cost record) |

## Verification done

1. **Python port vs JAX (Ryan's code):**
   - children: 159,058 + 15,392 + 20,296 compared, 0 mismatches;
   - whole searches: 18 + 42 identical (rows 0–9, every gate);
   - the hard-row search comparison (rows 590–591) was still running at the time of writing.
2. **Numba vs Python port:**
   - capped 24/48: 48 + 24 (hard rows 590–599) + 192 (MS640 every 20th row) searches identical;
   - uncapped: 24 hard searches identical.
   - The kernel is about 22 times faster.
   - A bug found this way (the root's hash used a signed integer, so the start state could be stored twice) was fixed
     in the rewrite.
3. **Path replay:** `results/ryan_1e5/VERIFY.json` passes for every solved path.

## Results at 10^5 (no cap)

Solved at 10^3 / 10^4 / 10^5 (full metrics in `results/ryan_1e5/SUMMARY_TABLE.md`):

| gate | MS640 | bench60 | ladder100 |
|---|---|---|---|
| no_short_sub | 590 / 612 / 626 | 43 / 49 / 52 | 66 / 88 / 93 |
| short_relator | 552 / 606 / 634 | 28 / 40 / 54 | 11 / 20 / 40 |
| unbalanced | 558 / 610 / 626 | 31 / 47 / 52 | 23 / 69 / 93 |
| long_presentation | 590 / 612 / 626 | 43 / 49 / 52 | 65 / 88 / 93 |
| plateau100 | 590 / 612 / 626 | 43 / 49 / 52 | 61 / 88 / 93 |
| periodic10 | 589 / 612 / 626 | 42 / 49 / 52 | 63 / 88 / 93 |

## AWS (see ops/aws/ledger.md)

- **Account and resources:** key `claude-agent` in account 205558941715, tag `project=claude-agent`, bucket
  `claude-agent-205558941715`, instance profile `claude-box`, security group `sg-07363655368c9d2d2` (no inbound;
  created for this run).
- **The 10^5 run:** m7i.16xlarge spot, 4,440 searches in about 4 minutes with 64 workers.
- **The first 10^6 attempt failed.** 24 workers ran out of memory: a 10^6 search holds about 67M states, about 12 GB
  or more. The local watcher only looked for the EXIT file, so the dead box sat idle for about 2 hours (about $2.60
  total for that box).
- **What changed after the failure:**
  - the box now runs a unit that writes the job's final status (`out/UNIT_RESULT`), and the local watcher waits for
    it as well;
  - the rerun uses r7a.16xlarge (512 GB) with 20 workers.
- **Memory per search:** about 150 B per state; 10^6 pops make about 70M states.

## Results to 10^6 (no cap), `results/ryan_full_1e6/`

Solved at 10^3 / 10^4 / 10^5 / 10^6:

| gate | MS640 | bench60 | ladder100 |
|---|---|---|---|
| no_short_sub | 590 / 612 / 626 / 640 | 43 / 49 / 52 / 60 | 66 / 88 / 93 / 100 |
| short_relator | 552 / 606 / 634 / 640 | 28 / 40 / 54 / 60 | 11 / 20 / 40 / 60 |
| unbalanced | 558 / 610 / 626 / 640 | 31 / 47 / 52 / 60 | 23 / 69 / 93 / 100 |
| long_presentation | 590 / 612 / 626 / 640 | 43 / 49 / 52 / 60 | 65 / 88 / 93 / 100 |
| plateau100 | 590 / 612 / 626 / 640 | 43 / 49 / 52 / 60 | 61 / 88 / 93 / 100 |
| periodic10 | 589 / 612 / 626 / 640 | 42 / 49 / 52 / 60 | 63 / 88 / 93 / 100 |

Every path is verified. The 10^6 rerun ran on r7a.16xlarge spot (20 workers, 20 minutes). The total AWS cost of the
Ryan replication is about $3.25 (`ops/aws/ledger.md`). The final all-regions audit found 0 of ours left.

## Open items

- Time-weighted cost, as was done for Elliot, if wanted. CoV enumeration at gate openings is not charged in nodes.
- The paper tables. The rows per gate are long, so pick the best gate or two (`no_short_sub` / `periodic10`) for the
  main table.
- The hard-row JAX search comparison (rows 590–591) was still running locally when this was written. The child-level
  JAX comparison and all numba comparisons passed.
