# [2026-07-29] Scout small, then scale only the winner [WORKS]

A long wall-clock campaign at a huge node budget is the wrong default for heuristic
comparisons. Agent-local searches are already capped at `node_budget ≤ 1,000`
([`local-run-budget-cap.md`](local-run-budget-cap.md)); within that, prefer **short
scouts** that compare many arms quickly, then raise budget only for the arm that
won the scout.

Why this works here:

- A search at budget `B` is exactly the first `B` pops of any longer search, so a
  small-budget ranking is a prefix of the large-budget run — not a different
  experiment. Scaling the winner buys depth on a known ordering; it does not
  invent a new ranking that a scout could not have seen.
- Long multi-hour agent runs at the local ceiling still burn wall time on losers
  and invite overfitting / under-powered nulls (see campaign-12h: advisor blocked
  fitting; the useful signal was already visible at budget 1k on short arms).
- Production depth (`10^4`–`10^6`) belongs on Colab multi-CPU, via a CONFIG /
  SETUP / RUN notebook that resumes from jsonl — not on the agent host.

**Rule:** for any new ordering / feature / weight idea: (1) scout ≤1k nodes,
small presentation subsets, short wall; (2) pick the winner on a pre-registered
denominator; (3) only then write or bump a Colab notebook budget for that winner;
(4) never start with a huge-budget marathon "to be sure."

**Trap:** quoting a large-budget win without the scout ranking (or without saying
the control had dynamic range) hides that the expensive run was unnecessary, or
that the null was dead at the scout stage already.
