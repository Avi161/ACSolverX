# Two traps that cost real work: duplicate writers, and reading a bound backwards

2026-07-29, fable line, post-restart segment.

- [TRAP] A resumed subagent can relaunch the job it was already running. Two processes
  then execute the same module with the same DEFAULT output paths, each opening the
  artifact with truncation, and the committed file is an interleaving of both — the
  first symptom was a `.gz` that raised `EOFError: Compressed file ended before the
  end-of-stream marker`. Diagnose with `ps -eo pid,etimes,time,pcpu,args` and compare
  ELAPSED against the run you launched: two entries for one module means two writers.
  Kill both (the artifact is already suspect), delete the outputs, relaunch exactly
  one. Prevention: give every launch an explicit, distinct `--out` path, and never
  resume an agent whose work you have taken over — stop it.
- [TRAP] A heuristic search over rotation systems yields an UPPER bound on gamma_N (a
  witness proves the minimum is no worse than what was found). It is silently tempting
  to read a histogram of such values as "the class sits high", and then to feed that
  into a distance corollary that needs a LOWER bound — inverting the inequality twice
  without noticing. Guard: for every reported quantity write down which tool bounds it
  from which side (exhaustive solver: gamma_N >= 1; heuristic witness: gamma_N <= k;
  exact census: equality), and never combine them in the direction neither supports.
- [TRAP] A weaker search reports HIGHER values, so "the obstruction grows with input
  size" and "my search degrades with input size" produce the identical shape. Any claim
  about a trend in a heuristically-measured quantity needs a calibration control at the
  large end — exact values on the largest instances still affordable — before the trend
  is attributed to the object rather than the instrument.
- [WORKS] Pinning a value from two sides with two different tools: the exhaustive
  solver certifies gamma_N >= 1 and a single hill-climbed rotation, re-verified
  exactly, certifies gamma_N <= 1. Neither tool alone can produce the exact value at
  that word length, and together they cost ~0.1 s where the census is infeasible.
