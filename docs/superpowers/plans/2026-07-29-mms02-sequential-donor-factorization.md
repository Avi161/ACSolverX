# MMS02 Sequential Donor Factorization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce an exact canonical JSON certificate and an independently implemented verifier for the MMS02 triangular transcript, the separate S1/S2 donor branches, and the two undecided rank-two quotient gates.

**Architecture:** A dependency-free generator builds typed row ledgers and validates them before canonical serialization. A separate verifier consumes literal JSON and reimplements every word and replay operation without importing generator code. Focused pytest tests mutation-check case, indices, donor restoration, branch separation, transcript separation, endpoints, and quotient strings.

**Tech Stack:** Python 3 standard library, JSON, pytest, Ruff, `scripts/run_proof_guarded.py`.

## Global Constraints

- Work only in `/Users/avigyapaudel/Documents/Obsidian Vault/surf/ACSolverX/.claude/worktrees/codex-proofs`.
- Add proof artifacts only under `.scratch/`; add only the required design, plan, and report outside `.scratch/`.
- Do not modify existing solver, runner, notebook, proof-guard, or proof-checker files.
- Use uppercase as inverse, `[s,t]=s t s^-1 t^-1`, right multiplication, and literal conjugation `w row w^-1`.
- Use 1-based row indices in every serialized action.
- Keep the nine-action triangular transcript separate from both donor branches.
- Start S1 and S2 independently from `(r,q,v)`; never concatenate them.
- Expand positive donor macros to three primitives and negative donor macros to five primitives, including both donor inversions.
- Write no canonical certificate until generator replay passes.
- Treat any failed pinned literal identity as a terminal `BLOCKED` result; never repair a target silently.
- Run every Python, pytest, check, compile, and lint command through `scripts/run_proof_guarded.py --timeout-seconds 30`, with one thread and no background work.
- Do not rerun an unchanged timeout, start search, enumerate finite groups, run a command longer than 30 seconds, spawn subagents, or push.

---

### Task 1: Pin the proof contract with failing tests

**Files:**
- Create: `.scratch/test_mms02_sequential_donor_factorization.py`

**Interfaces:**
- Consumes: literal paths for the absent generator, verifier, and canonical certificate.
- Produces: focused behavioral tests that execute the generator and verifier APIs after they exist and mutation-test the serialized proof.

- [ ] **Step 1: Write tests before implementation**

Define dynamic file loaders for
`.scratch/mms02_sequential_donor_factorization_certificate.py` and
`.scratch/verify_mms02_sequential_donor_factorization.py`. Pin the words
`A,B,u,c,C,r,q,v,h,K,D`, the nine transcript action labels and all ten expected
macro `(target,donor,conjugator,sign)` tuples. Require the canonical certificate
path to exist only for the final canonical-file test.

- [ ] **Step 2: Add exact behavior and mutation assertions**

Assert the generated object has the exact triangular ledger from the design,
S1 endpoint `(A,q,v)`, S2 endpoint `(r,B,v)`, S1/S2 macro counts 8/2,
primitive counts 32/8, and quotient presentations/defects. Deep-copy the
object and assert independent verification rejects: altered letter case, a
zero-based target, a removed donor restoration action, an S1/S2 endpoint
concatenation, replacement of the nine-action transcript with a donor branch,
and each altered quotient defect.

- [ ] **Step 3: Run guarded pytest to prove RED**

Run:

```text
python3 scripts/run_proof_guarded.py --timeout-seconds 30 -- uv run --with pytest python3 -m pytest -q .scratch/test_mms02_sequential_donor_factorization.py
```

Expected: collection or test failure because the generator/verifier and
canonical certificate do not exist. Record the exact failure in the report.

---

### Task 2: Implement and self-replay the certificate generator

**Files:**
- Create: `.scratch/mms02_sequential_donor_factorization_certificate.py`
- Test: `.scratch/test_mms02_sequential_donor_factorization.py`

**Interfaces:**
- Produces: `inverse(word: str) -> str`, `free_reduce(word: str) -> str`,
  `apply_action(rows: tuple[str,str,str], action: dict[str,object]) -> tuple[str,str,str]`,
  `build_certificate() -> dict[str,object]`,
  `validate_certificate(certificate: dict[str,object]) -> None`, and
  `main() -> int` with `--check` and `--output PATH`.
- Consumes: only pinned literals from the design; no existing proof module.

- [ ] **Step 1: Implement minimal word and primitive replay operations**

Implement case-swapped reversal, stack free reduction, literal word
substitution, commutator construction, and the three primitive actions. Reject
invalid 1-based indices, self-multiplication, unknown kinds, and malformed
conjugators before mutating a row tuple.

- [ ] **Step 2: Build the exact nine-action ledger**

Replay exactly
`I3,M32,I3,C_yx(3),M13,C_XY(3),C_Yx(1),M21,C_Xy(1)` from `(r,q,v)`, storing each
primitive before/after tuple. Require the pinned ten-state ledger and final
`(x,y,z)`.

- [ ] **Step 3: Build S1 and S2 independently**

Use the exact macro tables from the design. For each macro, expand a positive
sign to `conjugate,multiply,conjugate` and a negative sign to
`invert,conjugate,multiply,conjugate,invert`. Store before/after tuples,
target/donor indices, conjugator, sign, donor-before/donor-after, restoration
flag, freely reduced factor, and the full primitive ledger. Start both branches
from `(r,q,v)` and require exact endpoints.

- [ ] **Step 4: Bind identities, quotient gates, and counts**

Check `C=f1f2f3f4`, the eight-factor `K^-1`, the two-factor `D^-1`,
`A=rK^-1`, `B=qD^-1`, substitution `v=1 => z=Yx`, and the four exact reduced
rank-two words. Store explicit presentations, defect words, undecided status,
and nonclaims. Require transcript/S1/S2 primitive counts 9/32/8 and combined
kind counts multiplication 13, conjugation 24, inversion 12.

- [ ] **Step 5: Add canonical serialization only after in-memory replay**

Make `--check` build and validate without writing. For `--output`, call the same
validation first, then write UTF-8 JSON with `sort_keys=True`, `indent=2`, and a
single terminal newline. Do not create the canonical JSON in this task.

---

### Task 3: Implement the independent literal verifier

**Files:**
- Create: `.scratch/verify_mms02_sequential_donor_factorization.py`
- Test: `.scratch/test_mms02_sequential_donor_factorization.py`

**Interfaces:**
- Produces: independent `inverse`, `free_reduce`, `substitute`, primitive replay,
  `verify(certificate: object) -> dict[str,object]`, and CLI `main() -> int`.
- Consumes: a JSON path or a literal parsed object. It must not import the generator.

- [ ] **Step 1: Reimplement word and action semantics independently**

Use a separately written cancellation loop and explicit action dispatch. Bind
the exact top-level schema/version/keys, words, transcript action specifications,
branch macro specifications, 1-based indices, signs, and row tuple widths.

- [ ] **Step 2: Replay every serialized state**

Check each primitive `before` equals the current tuple, independently compute
its `after`, and require exact equality. For every macro, require primitive
start/end equality, exact target and donor metadata, literal conjugate factor,
donor before/after equality, and `donor_restored is True`. Require exact branch
and transcript endpoints and exact action counts.

- [ ] **Step 3: Recompute identities and quotient words**

Independently reconstruct `K,D`, the S1/S2 factor products, and the substitution
`z=Yx`. Require literal exact-case words, named presentations and defect words,
undecided gate status, and all nonclaim flags. Return a compact count/endpoint
summary only after all checks pass.

---

### Task 4: Prove GREEN and materialize the canonical certificate

**Files:**
- Create: `.scratch/mms02_sequential_donor_factorization_certificate.json`
- Verify: the generator, verifier, and focused tests.

**Interfaces:**
- Consumes: Tasks 1–3.
- Produces: one deterministic canonical JSON proof object independently accepted by the verifier.

- [ ] **Step 1: Run generator self-replay without writing**

Run:

```text
python3 scripts/run_proof_guarded.py --timeout-seconds 30 -- python3 .scratch/mms02_sequential_donor_factorization_certificate.py --check
```

Expected: exit 0 with exact transcript/S1/S2 counts and no certificate write.

- [ ] **Step 2: Generate only after replay passes**

Run the guarded generator with
`--output .scratch/mms02_sequential_donor_factorization_certificate.json`.
Expected: exit 0 after validation and one canonical JSON file.

- [ ] **Step 3: Run the independent verifier**

Run the guarded verifier on the canonical JSON. Expected summary:
`9 transcript actions, 8/2 donor macros, 49 total primitives`, endpoints
`(x,y,z)`, `(A,q,v)`, and `(r,B,v)`.

- [ ] **Step 4: Run focused pytest to prove GREEN**

Run the exact guarded pytest command from Task 1. Expected: every focused test
passes with no warnings.

---

### Task 5: Static checks, audit, report, and commit

**Files:**
- Create: `.superpowers/sdd/2026-07-29-mms02-sequential-donor-factorization/report.md`
- Verify: all new authorized files.

**Interfaces:**
- Consumes: fresh generator/verifier/test output and repository/process audits.
- Produces: evidence-backed report and local commit SHA(s), with no push.

- [ ] **Step 1: Run Ruff separately**

Run a guarded Ruff check over the three new Python files. Expected: exit 0.

- [ ] **Step 2: Run compilation separately**

Run guarded `python3 -m py_compile` over the three new Python files with
`PYTHONPYCACHEPREFIX=.scratch/pycache` supplied to the child. Expected: exit 0.

- [ ] **Step 3: Audit exact scope and process cleanup**

Require no `.scratch/process-guard/active.json`, no exact-basename
`python`, `python3`, `pytest`, `uv`, `numba`, or `run_proof_guarded.py` process
associated with the completed run, no diff whitespace errors, and no modified
pre-existing file. Inspect every new file and verify the canonical JSON has one
terminal newline.

- [ ] **Step 4: Write the report with `apply_patch`**

Record design, exact RED and GREEN commands/results, exact action/macro counts,
the four quotient words and two presentations, independent replay output,
audit evidence, commit SHAs, concerns, and explicit nonclaims. Use status
`DONE`, `DONE_WITH_CONCERNS`, or `BLOCKED` according to the evidence.

- [ ] **Step 5: Run fresh completion verification**

After the report exists, rerun the independent verifier, focused pytest, Ruff,
compile, diff check, lock audit, and exact-basename process audit. Do not reuse
earlier output for the completion claim.

- [ ] **Step 6: Commit only authorized new files**

Stage the design, plan, report, and four new `.scratch/` artifacts by exact path.
Inspect the staged name/status list and diff before committing. Commit locally,
record the final SHA in the handoff, and do not push.
