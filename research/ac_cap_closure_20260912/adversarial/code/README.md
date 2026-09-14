# `adversarial/code/` — attack on the implementation

Verbatim scripts of the code-focused reviewer (README section 6.3). Nothing
here is imported by the module or its test suite. Each script puts the module
directory on `sys.path` with an absolute
`sys.path.insert(0, '/home/user/ACSolverX/research/ac_cap_closure_20260912')`
line; adjust it if the checkout lives elsewhere.

| script | what it checks |
|---|---|
| `probe5.py`, `probe_overflow.py`, `probe2.py`–`probe4.py` | the int64 packing defect found independently of the model reviewer: constructed and random states whose move products exceed 32 letters, fast vs reference relator by relator (run against the pre-fix engine; `bfs` now raises for `cap > 16`, the packed helpers still run) |
| `probe16.py` | the threshold pinned exactly: 0 diverging moves at `\|r_i\|+\|r_j\| = 30, 31, 32`, first divergence at 33 |
| `probe8.py`, `probe10.py` | set-level impact of the defect: 100,000 states at caps 17–26, states with diverging moves but no differing child set (the rotation-orbit masking of section 6.2) |
| `probe6.py`, `probe7.py`, `probe9.py` | supporting probes (single moves, canonical keys, kernel-vs-standalone helper composition) |
| `cap16.py` | the patched boundary, worst case not random: 400 constructed 16/16 pairs, every move concatenating exactly 32 letters, 204,800 moves compared as reduced words and as packed keys — 0 divergences |
| `diff1012.py`, `diff1316.py` | fast vs reference in the band the suite never covered: 468 `(presentation, cap)` pairs at caps 10–12; 5,815 full CLOSED components at caps 13–16 |
| `adv.py` | adversarial inputs: single-letter relators, `r1 = r2`, `r1 = r2^-1`, `cap = 1`, a cap below `\|r_1\|+\|r_2\|` |
| `budget.py` | the `frontier_size_at_stop` disagreement between the engines (fixed: both now report discovered-minus-fully-expanded) |
| `model.py` | brute-force AC2 with `\|u\| ≤ 6` against the model on eight `(state, cap)` pairs: containment never fails, equality arrives at different `\|u\|` — the §1.4 wording fix |
| `ak16.py`, `mono.py`, `thr.py` | re-derivation of the headline cap-16 component, of monotonicity at caps 9–14, and of the throughput table (wall clock, peak RSS) |
| `b.csv`, `b.jsonl` | the batch-mode exit-status reproduction (`--caps 17,10`): a refused cap used to be written as an `error` record with exit 0; it now exits 1 |
| `err.txt`, `rows.jsonl`, `out.json` | captured stderr of the single-mode `cap = 17` rejection, and the CLI/certificate round-trip outputs (`--csv` batch, `--r1/--r2` single run) that `verify_path.py` was run on |

The three defects these scripts found (`max_states <= 0` out-of-bounds write,
the `frontier_size_at_stop` mismatch, the batch exit status) are fixed in the
shipped module and pinned by tests (h), (i), (j); the packing defect is
section 6.2's, fixed by `MAX_CAP = 16` and test (g).
