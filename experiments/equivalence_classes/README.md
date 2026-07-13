# `experiments/equivalence_classes/`

Proves that the 261 "unsolved" Miller–Schupp representatives are really **126 distinct problems** —
and ships a machine-checkable certificate for every merge. The result and the evidence live in
[`results/equivalence_classes/`](../../results/equivalence_classes/).

Five subpackages, by role.

## `lib/` — the algebra. Pure, no I/O.

| module | what it is |
|---|---|
| `words.py` | F₂ word algebra in the `xXyY` alphabet: `canon_pair` (Booth's O(n) least rotation), the Miller–Schupp definition, Definition 2.1 replay, `abelian_det`. Pure Python — deliberately **independent of the numba solver**, so agreement between them is evidence rather than tautology. |
| `acmoves.py` | the two move sets — `seam` (the baseline's cancelling-seam moves) and `full` (every `(k1,k2)`) — importing the baseline's reduce/canonicalise **verbatim** |
| `autcanon.py` | Whitehead canonical form, **carrying the witnessing automorphism** `φ` |
| `autinv.py` | inverse of an automorphism of F₂ (Nielsen reduction with tracking) — turns a two-sided `Aut` merge into a single substitution |
| `relabel.py` | signed-permutation relabelling of a presentation |

## `search/` — the two searches

| module | what it is |
|---|---|
| `aut_search.py` | **the one that works**: multi-source BFS over `Aut`-classes + union-find. This produced the 126. |
| `aca_search.py` | the raw-AC multi-source search. Its *strategy* is superseded — it is the measurement proving the raw AC hump is too high to cross at any locally available budget — but its `DSU` union-find class is a **live dependency of `aut_search.py`**, which is why it lives here and not in `phases/`. |

## `pipeline/` — produces the artifacts

Run in this order; each writes into `results/equivalence_classes/`.

| module | in → out |
|---|---|
| `run_sweep.py` | the 261 reps → `sweep_<stem>.json` |
| `make_proof_book.py` | sweep JSON → `certificates.json` + `PROOFS.md` |
| `make_class_table.py` | sweep JSON → `classes_<stem>.csv` (the 126-row deliverable) |

## `verify/` — the checkers. **Nothing ships until these exit 0.**

| module | checks |
|---|---|
| `verify_certificates.py` | a sweep JSON: re-derives every merge from `data/` by pure string substitution |
| `verify_proofs.py` | **the shipped result**: reads `certificates.json` + the raw CSV and *nothing else* — no sweep, no search. Replays every move literally, re-proves every change of variables is an automorphism by Nielsen reduction, then **rebuilds the partition from the verified edges alone** and requires it to equal 126. Verifying every edge is a different claim from verifying the count. |

```bash
.venv/bin/python3 experiments/equivalence_classes/verify/verify_proofs.py
# -> ALL 135 EDGES VERIFY. The 261 presentations are 126 distinct problems.
```

## `phases/` — one-shot gates, run once each before the pipeline existed

Historical evidence, still correct, but not part of the reproduction recipe. Nothing imports them.

| module | the gate it opened |
|---|---|
| `phase0_provenance.py` | the 550 → 261 dedup was an AC-reduction; word-reversal is **not** a free symmetry |
| `phase1_moveset_check.py` | gate A: `seam` vs `full` move-set sanity |
| `phase1_preflight.py` | gate B: rediscovers the 2 known merges + throughput |
| `phase1_calibrate.py` | gate B′: calibrates `(max_total, budget)` against the one known merge. **This is the script whose output motivated switching from raw-length BFS to Aut-minimal-length BFS** — i.e. the reason `aut_search` exists and `aca_search` was demoted. |

---

## `test_equivalence.py`

Layered so a bug in one layer cannot hide a bug in another: the move sets against the baseline
solver's own `expand_node_nj`; the `Aut` canonical form against the *independently written*
`experiments/analysis/whitehead.py`; the certificates against pure string substitution and a
Nielsen-reduction basis test sharing nothing with the code that produced them. It also **mutation-tests
the verifier** — tampering with `certificates.json` seven ways and requiring each to be rejected.

It is collected by a bare `pytest` (via `testpaths`), and directly:

```bash
.venv/bin/python3 -m pytest experiments/equivalence_classes -q     # 35 passed, ~65s
```

## A note on paths

Every script here finds the repo root by **walking up** until it sees `experiments/` and `data/` —
never by counting `os.path.dirname()` levels. A dirname chain encodes the file's depth, so it silently
repoints at the wrong directory the moment the file moves, and every `results/` path below it is then
wrong without raising. Keep the walk-up if you move these files again.
