# Adversarial verification record

Verbatim scripts and raw outputs of the two independent reviewers who were
asked to refute `capbfs.py` / `capbfs_reference.py` / `verify_path.py` before
the module was committed. Nothing here is imported by the module or its test
suite; it is kept so the claims in README section 6 can be re-run.

Every script was run from its own directory with the module directory on
`sys.path` (the `sys.path.insert(0, '/home/user/ACSolverX/research/ac_cap_closure_20260912')`
line at the top of each file; adjust it if the checkout lives elsewhere).
Some scripts `exec` a slice of a sibling (`overflow.py`), so run them in place.

## `model/` — attack on the mathematical model

`indep.py` is the independent formulation everything else in this directory
compares against: strings over `xXyY`, moves `r_i · (u r_j^e u^-1)` over all
freely reduced conjugators `u` up to a length bound (no rotations, no
connector bound), canonical form under the letter order `y < Y < x < X`.

| script | what it checks | output |
|---|---|---|
| `cmp_nb.py`, `bigcap.py`, `invcheck.py` | module neighbour sets == brute-force sets (caps 5–14, saturation in `\|u\|`, `r_i^-1` representative adds nothing) | stdout |
| `cmp_bfs.py` | full BFS state sets brute == reference == fast at caps 5–7 | stdout |
| `subseteq.py`, `subseteq2.py`, `subseteq3.py` | every model move has a cap-respecting elementary AC realisation (all class pairs of length ≤ 7 at caps 4–8; 400 random states at caps 4–12) | stdout |
| `canoncheck.py` | canonicalisation is a complete invariant, identical across engines and orders | stdout |
| `ak3_11.py` | AK(3) at caps 9–12 re-derived by the pure-Python reference | `ak3_11.out`, `ak3_12.out` |
| `degenerate.py` | degenerate starts (`{x,x}`, `{xy,xy}`, …) agree across engines | stdout |
| `overflow.py`, `overflow2.py`, `overflow3.py`, `threshold.py`, `spurious.py`, `reach17.py`, `realstate17.py`, `dbg17.py`, `dbg17b.py`, `endtoend17.py`, `childsets.py`, `probe.py`, `ballcheck.py` | the int64 packing defect: threshold at 33 letters, missed/spurious counts at cap 31, a state visited at cap 17 with dropped rotations, child sets still equal to the reference on 248 overflow-regime states | stdout, `kernel_all.txt` |
| `capbfs_dbg.py` | instrumented copy of the kernel used for the rotation-drop diagnosis (not the shipped engine) | — |
| `refcerts.jsonl`, `cert.json`, `t.json` | certificates produced by the *reference* engine and the tampering inputs fed to `verify_path.py` | — |
| `pytest.out` | the module's own suite as it stood when reviewed (57 tests) | — |

## `code/` — attack on the implementation

The code reviewer's scripts are in `code/` (see the README there): an
independent rediscovery of the packing defect and its exact threshold, a
worst-case stress of the patched cap-16 boundary, fast-vs-reference
differentials at caps 10–16, and the reproductions of the three small defects
fixed in section 6.3 (`max_states <= 0`, `frontier_size_at_stop`, the batch
exit status).

The defect these scripts found is fixed in the shipped module (`MAX_CAP = 16`,
test (g)); the scripts were written against the pre-fix engine, so the
`cap > 16` probes will now raise `ValueError` from `bfs` (the ones that call
the packed helpers directly still run).
