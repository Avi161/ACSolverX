# MMS02 Sequential Donor Factorization SDD Report

## Status

`DONE_WITH_CONCERNS`

The exact proof artifacts are complete and independently replay. The only
handoff concern is an unrelated untracked file,
`docs/AK3_PROMISE_LEDGER.md`, already present in the worktree during the final
scope audit. It was not read, modified, staged, or committed by this task.

## Design implemented

The checkpoint contains three independent proof objects under the literal
free-group convention uppercase=inverse and
`[s,t]=s t s^-1 t^-1`:

1. the separate nine-action 1-based triangular transcript
   `(r,q,v)->(x,y,z)`;
2. the S1 donor branch `(r,q,v)->(A,q,v)` with eight macros; and
3. the S2 donor branch `(r,q,v)->(r,B,v)` with two macros.

The two donor branches start from the same literal tuple and do not concatenate.
Every positive donor macro expands to conjugate donor, right-multiply target,
and inverse-conjugate donor to restore it. Every negative macro additionally
inverts the donor before conjugation and again after inverse conjugation.
Every action and macro stores exact before/after row tuples and 1-based row
indices.

The implementation consists only of these new proof artifacts:

- `.scratch/mms02_sequential_donor_factorization_certificate.py`
- `.scratch/verify_mms02_sequential_donor_factorization.py`
- `.scratch/test_mms02_sequential_donor_factorization.py`
- `.scratch/mms02_sequential_donor_factorization_certificate.json`

No existing solver, runner, notebook, proof guard, or proof checker was changed.
The project `AGENTS.md` has one required lesson recording that these explicitly
authorized `.scratch/` proof artifacts must be force-added by exact path because
the directory is ignored.

## RED evidence

The focused tests were created before the generator, verifier, or canonical
JSON. The first guarded invocation did not reach pytest because `uv` attempted
to use the sandboxed home cache. The already documented worktree rule was then
applied by setting `UV_CACHE_DIR=.scratch/uv-cache` inside the guarded child.

The resulting guarded RED run reached pytest and reported:

```text
1 failed, 8 errors in 0.07s
```

The failure and every setup error identified the same intended missing feature:

```text
missing implementation artifact: mms02_sequential_donor_factorization_certificate.py
```

No production proof code or certificate existed during that run.

## GREEN and replay evidence

Before any JSON was written, guarded generator check-only replay returned exit
zero with:

```json
{"branch_endpoints":{"S1":["xzYXyxZXYxyZ","Xy","Xyz"],"S2":["xyxZXY","XyxZXYXyxzXYxy","Xyz"]},"branch_macros":{"S1":8,"S2":2},"total_primitives":49,"transcript_actions":9,"transcript_endpoint":["x","y","z"]}
```

Only after that pass, the guarded generator wrote the canonical JSON. The
separately implemented verifier, which does not import generator code, consumed
that literal file and returned the same exit-zero summary. The guarded focused
suite then reported:

```text
9 passed in 0.06s
```

The tests include mutations of pinned letter case, 1-based row indices, negative
donor restoration, S1/S2 branch starts, triangular-transcript conflation, and
both quotient defects. Each mutation is rejected by the independent verifier.

After the only Ruff-requested import-order cleanup, fresh independent replay
again returned the exact summary above and focused pytest again reported
`9 passed in 0.06s`. Guarded Ruff reported `All checks passed!`. A separate
guarded `python3 -m py_compile` invocation returned exit zero for the generator,
verifier, and focused test.

## Exact action counts

| Proof object | Macros/actions | Multiplications | Conjugations | Inversions | Primitive total |
|---|---:|---:|---:|---:|---:|
| Triangular transcript | 9 actions | 3 | 4 | 2 | 9 |
| S1 | 8 macros | 8 | 16 | 8 | 32 |
| S2 | 2 macros | 2 | 4 | 2 | 8 |
| Combined independent objects | 10 macros + 9 actions | 13 | 24 | 12 | 49 |

The exact triangular transcript is:

```text
I3, M32, I3, C_yx(3), M13, C_XY(3), C_Yx(1), M21, C_Xy(1)
```

S1 binds the ordered macro specifications:

```text
(1,2,x,+1), (1,2,xx,-1), (1,3,xx,+1), (1,2,x,-1),
(1,2,zY,+1), (1,3,zYx,-1), (1,2,zYx,+1), (1,2,zY,-1)
```

S2 binds:

```text
(2,1,YX,+1), (2,1,YXX,-1)
```

Every macro's stored donor-after word equals its donor-before word, and the
independent verifier recomputes that equality from the primitive ledger.

## Exact quotient gates

The named substitution `v=Xyz=1` gives `z=Yx` and `Z=Xy`. Literal substitution
and free reduction give:

```text
A_bar = xYxYXyyXYxyXy
D_bar = YXyyXYxyxY
B_bar = XyyXYXyxYYxy
K_bar = YxYXyxYYxyXyyyXY
```

The exact named quotient presentations and stored defect words are:

```text
Q_A = <x,y | xYxYXyyXYxyXy>, defect delta_D = YXyyXYxyxY
Q_B = <x,y | XyyXYXyxYYxy>,   defect delta_K = YxYXyxYYxyXyyyXY
```

Both gate statuses are stored as `undecided`.

## Artifact and process audit

- Canonical JSON size: 28,419 bytes.
- Canonical JSON SHA-256:
  `829f89a191cfe9cfeb1c86d194c1ec3e29a05941277206c1c091ab0152bfbbff`.
- Canonical JSON ends in exactly one newline.
- `.scratch/process-guard/active.json` is absent after the guarded commands.
- A narrowly approved read-only process scan stripped executable paths and
  matched exact lowercase basenames only. It returned zero matches for
  `python`, `python3`, `pytest`, `uv`, `numba`, and `run_proof_guarded.py`.
- `git diff --check` returned no whitespace errors.
- The implementation commit contains only the four named `.scratch/` proof
  artifacts. The design commit contains only the required design and plan. The
  RED commit contains only the test and the required `AGENTS.md` lesson.
- No push was performed.

## Commits

- `9e9b4e2` — design specification and implementation plan.
- `922c96b` — strict RED tests and the verified ignored-`.scratch/` lesson.
- `b124d0c` — generator, independent verifier, canonical JSON, and final test formatting.

The report commit SHA is intentionally supplied in the final handoff because a
commit cannot contain its own SHA.

## Concerns

- The unrelated untracked `docs/AK3_PROMISE_LEDGER.md` remains in the worktree
  and is intentionally excluded from this task.
- Ruff was not initially cached and the sandboxed fetch failed. A narrowly
  approved guarded download populated the project-local cache; the subsequent
  required Ruff pass was local and successful.

Neither concern affects the replayed proof artifacts.

## Explicit nonclaims

- S1 and S2 are separate branches and do not prove a path to `(A,B,v)`.
- The full sequential donor factorization needed to combine them is equivalent
  to the open MMS02 bridge; it is not supplied here and the bridge remains open.
- The nine-action triangular transcript is separate from both donor branches.
- No normal-closure factorization, membership, or nonmembership result is
  claimed for `D mod <<A,v>>` or `K mod <<B,v>>`.
- No finite quotient or homomorphism is claimed.
- No finite-group enumeration, heuristic search, or bounded search was run.
