# Convention: testing & independent verification (make the code strong)

> Referenced from the root `CLAUDE.md` ("Testing conventions" pointer). Kept out of `CLAUDE.md`
> so the index stays lean. Open this file before writing tests for, or claiming correctness of,
> any non-trivial algorithm — especially one whose output we present as a research finding.

The goal is **strong evidence of correctness**, not a green checkmark. A test suite the
implementer wrote alone shares the implementer's blind spots: the same wrong mental model that
produced a bug produces a test that agrees with the bug. The fixes below are the state of the
art for breaking that shared-blind-spot bias.

---

## 1. Always add an INDEPENDENT adversarial test pass (default, not optional)

For any non-trivial algorithm (search, numerics, encodings, moves/transforms, parsers, anything
where a silent bug **corrupts** rather than merely degrades results):

1. Get **your own** suite green first (fast iteration).
2. Then launch a **separate subagent** to author an independent suite in a **separate test file**
   (e.g. `tests/<thing>_independent_test.py`). It must:
   - know the **problem/spec and the public API (the contract)** — function names, inputs/outputs,
     invariants — but be **forbidden from reading or mirroring the implementation's internal logic**.
     Treat the module under test as a **black box**.
   - **not read your test file** (it would inherit your framing and blind spots).
   - **build its own oracle from first principles / the math / an independent reference** — not from
     the code under test.
   - be **adversarial**: its job is to find a real bug or produce strong independent evidence, not to
     confirm. Tell it so explicitly.
3. Reconcile every discrepancy honestly (see §5).

This is **N-version / differential** verification: two independent derivations of "what the answer
should be" agreeing is far stronger evidence than one derivation checking itself.

## 2. The BIAS LEAK — the mistake to avoid (learned the hard way)

> When you hand the independent agent a **design/algorithm choice** ("the move set is unordered-pairs
> with dual-slot emission", "canonical form sorts by (len,lex)"), it will **confirm that choice**, not
> check it. You have leaked the very thing you needed independence on. Its "all passed" then certifies
> the *primitives and the plumbing*, **not** the design decision.

Rules to prevent the leak:
- Give the agent the **contract** (what must hold), never the **mechanism** (how you did it).
- If a design choice is load-bearing (e.g. which move set / which normalization), do **not** state
  your choice — instead point the agent at an **independent source of truth** for it (a second
  reference implementation, the paper/lemma, the production system) and have it derive the oracle
  there. Then **triangulate**: a choice confirmed by ≥2 independent sources that agree is trustworthy.
- Explicitly list what NOT to look at (your test file, the module's internals).

## 3. Techniques (pick what the problem admits; combine them)

- **Differential testing** — compare against a known-good independent reference implementation on
  the same inputs; assert **representation-independent** outputs match (e.g. the *solved set*, not
  node counts or which canonical representative — those legitimately differ across implementations).
  This is the strongest check when a reference exists.
- **Metamorphic testing** — when there's no full oracle, assert relations that must hold:
  idempotence (`reduce(reduce(x)) == reduce(x)`), invariances (`canonical` unchanged under rotation
  and inversion), round-trips (`decode(encode(x)) == x`), monotonicities, commuting diagrams.
- **Property-based testing** — random inputs + invariants, with shrinking (Hypothesis if available;
  otherwise a seeded RNG loop). Cover edge cases explicitly (empty, singleton, full-cancellation,
  wrap-around, degenerate/equal inputs) — random rarely hits them.
- **Independent replay / re-derivation** — re-implement the *checker* from scratch; do **not** reuse
  the code's own verifier. (Trap: a `verify_path` that calls the same `get_neighbors` as the solver
  shares its move-generation blind spot and cannot catch a move-gen bug — see §4.)
- **Brute-force reference** — an obviously-correct O(n²) version to validate a clever O(n) one
  (e.g. materialize-and-check vs an index-arithmetic fast-reject). Slowness is a virtue here.
- **Gold gate** — the production/ground-truth executor (here: the JAX env `check_paths` / `s_move`).
  When it can't run yet (missing dep, deferred bridge), **read its source** and check your logic
  against it statically, and **say the executable gold check is deferred** — don't let "unit tests
  pass" masquerade as "gold-checked".

## 4. Know which checks are actually INDEPENDENT (verification ladder)

Rank each check by what it can catch, and don't overclaim:
- **Self-consistent** (shares code paths with the thing it checks) → catches typos/plumbing, **not**
  the shared logic. A solver's own path-verifier that reuses the solver's move generator is here.
- **Independent within the module** (different code, same author/mental model) → catches
  implementation bugs, **not** a wrong design choice.
- **Cross-implementation / cross-source** (reference impl, production system, paper) → catches design
  choices too. Aim for this for anything you'll present as a finding.
Write down, per claim, which rung it sits on. A headline result needs the top rung (or an explicit
"gold check deferred" caveat).

## 5. Reconcile discrepancies honestly

- An independent oracle can itself be wrong. On a mismatch, **hand-verify the tiny case** before
  blaming either side.
- If the reference is buggy (it happens — e.g. a reference `reduce` that reads past the array end on
  full cancellation), **document the reference bug**, make your comparison robust to it (compare only
  the well-defined cases), and prefer the *correct* behavior in your implementation.
- Never silently switch sides. If your evidence and the oracle disagree, surface the conflict
  (advisor / the user) with the specific inputs, not a vibe.

## 6. Process checklist (copy into the task)

- [ ] Own suite green (unit + edge cases + the one discriminating end-to-end check).
- [ ] Independent adversarial subagent ran on a **separate** file, spec-only, black-box, told not to
      read the impl internals or your tests.
- [ ] Load-bearing design choices oracle'd from an **independent source**, triangulated ≥2 ways.
- [ ] Every claim tagged with its ladder rung; gold gate run or its deferral stated.
- [ ] Discrepancies reconciled by hand; reference bugs documented.
- [ ] Result persistence, if any, verified by an independent **reload → replay** (on-disk artifact,
      not just the in-memory object).
