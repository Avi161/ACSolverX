# Are the Aut(F₂)-minimal censuses of AC19 and AC1M the same set?

Question (2026-09-14): AC1M (`data/AC1M.txt.gz`, 1,136,154 presentations, total length
6–30, relators of at most 25 letters) is believed to be built by applying automorphisms to
AC19 (`data/AC19.txt`, 140,535 presentations of length ≤ 19).  If so, the two files should
have the same set of Aut(F₂)-orbits and therefore the same Aut-minimal representatives.

**Answer: close, but not the same set.**  Every AC1M row does lie in an orbit whose
Aut-minimal total length is ≤ 19 (the largest minimal length over all 1,136,154 rows is
19), which is what "automorphic images of length-≤ 19 presentations" predicts.  But the
orbit sets differ in both directions: 99.8 % of AC19's orbits occur in AC1M, and 93.2 %
of AC1M's orbits occur in AC19.

| census | rows | Aut-orbits (= Aut-minimal reps) | orbit size mean / max | singletons |
|---|---:|---:|---|---:|
| `AC19.txt` | 140,535 | **66,561** | 2.11 / 199 | 42,302 |
| `AC19_extended.txt` (634 MS-640 rows + AC19 + 15,888 rows of length 20–33) | 156,762 | **72,779** (identical to the shipped `data/AC19_extended_aut_min.csv`, same member lists) | 2.15 / 200 | — |
| `AC1M.txt.gz` | 1,136,154 | **71,283** | 15.9 / 454 | 0 (every orbit has ≥ 4 members) |

| relation | orbits | rows |
|---|---:|---:|
| in AC19 and in AC1M | 66,444 (99.82 % of AC19's, 93.21 % of AC1M's) | 1,085,695 AC1M rows (95.56 %) |
| in AC19 only | **117** | 378 AC19 rows, lengths 3–19 (68 of the 117 minimal reps have a one-letter relator; the trivial `(Y, X)` is one of them) |
| in AC1M only | **4,839** | 50,459 AC1M rows (4.44 %); minimal reps of length 15–19 (3,983 of them of length 19, after `AC19_extended` is also excluded: 4,672 orbits, lengths 15: 2, 16: 17, 17: 196, 18: 474, 19: 3,983) |
| in AC19_extended and in AC1M | 66,611 | 1,087,594 AC1M rows (95.73 %) |
| in AC19_extended only | 6,168 | 6,029 of them come only from the length > 19 tail of the extended file, 20 only from the 634 MS rows, 104 only from length-≤ 19 rows |

Literal overlap (presentations equal up to rotation, inversion and relator order, no
automorphism): 73,739 AC1M rows are AC19 rows, and 56,692 of the 140,535 AC19 rows occur
verbatim in AC1M; AC1M holds 943,083 distinct presentations.

So AC1M is consistent with "orbits of length-≤ 19 presentations under Aut(F₂)", but its
source pool was not exactly `AC19.txt`: 4,839 of its orbits (all with minimal length
15–19) have no member in AC19 at all, and 117 AC19 orbits, mostly very short ones, have no
member in AC1M.  The repository does not document how AC1M was generated
(`README.md` only calls it "a larger set"), so this is an observation about the files,
not about the generator.  For the solver campaigns on this branch the practical
consequence is: solving the 72,779-row AC19 census does not by itself cover 4,672
AC1M orbits (50,459 rows), and the AC1M census is a different benchmark of 71,283 orbits.

## Method

`autmin_census.py` canonicalises every row with `autcanon_fast.aut_min`
(`experiments/stable_ac/cov/ladder/autcanon_fast.py`, brought over from the branch
`claude/abelianized-exponents-verify-1i6muh` where the shipped AC19 census was built): Whitehead
peak reduction to the orbit's minimal total length, then the lex-min of the BFS-closed
minimal level set — a complete invariant of the Aut(F₂)-orbit (Whitehead's theorem), so two
rows get the same representative exactly when they are automorphic.  No level set exceeded
the 50,000-node cap on any of the 1,433,451 rows.  Letters 1/-1/2/-2 are read as x/X/y/Y
(the convention that reproduces the shipped census).

Validation:

- recomputing `AC19_extended.txt` gives exactly the shipped 72,779 representatives with
  identical member lists (`compare.json`, `shipped_vs_recomputed`);
- `crosscheck.py`: on 2,000 random AC1M rows and 1,000 random AC19_extended rows the fast
  canonicaliser agrees with the pure-Python `autcanon.aut_canon` (which also returns a
  witnessing automorphism, checked by substitution): 0 mismatches, 0 witness failures
  (`records/crosscheck.json`).

Records: `records/AC19_aut_min.csv.gz`, `records/AC19_extended_aut_min_recomputed.csv.gz`,
`records/AC1M_aut_min.csv.gz` (schema `name,r1,r2,n_members,members`, members are 0-based
line indices into the source file), the `*.summary.json` files (minimal-length histograms)
and `records/compare.json`.  Wall clock on the 4-core container: 23 s, 22 s and 154 s.

```bash
S=research/ac1m_autmin_20260914/autmin_census.py; R=research/ac1m_autmin_20260914/records
python3 $S data/AC19_extended.txt --prefix ac19x --out $R/AC19_extended_aut_min_recomputed.csv.gz
python3 $S data/AC19.txt --prefix ac19 --out $R/AC19_aut_min.csv.gz
python3 $S data/AC1M.txt.gz --prefix ac1m --out $R/AC1M_aut_min.csv.gz
python3 research/ac1m_autmin_20260914/compare.py
python3 research/ac1m_autmin_20260914/crosscheck.py --ac1m 2000 --ext 1000 --seed 1
```
