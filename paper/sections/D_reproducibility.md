# Reproducibility and Artifact Details {#app:repro}

## Data and artifacts

- **MS(1190) dataset.** The $640$-presentation known-solvable prefix used throughout \ref{sec:methods}, drawn from the Miller–Schupp benchmark \cite{miller1999ms}.
- **Consolidated candidate/trial archives.** JSONL.gz streams with one record per (presentation, arm/word/candidate, budget) triple and full per-record provenance — source form, generator and relator words, node count, floor reached, solved flag.
- **Certificates.** JSON, schema of \ref{app:certs}.

All of the above, together with the two acx-cert-v1 verifiers, are released on acceptance. The source MS(1190)/AC-benchmark datasets this campaign builds on are released under a data license (CC BY 4.0) by \cite{fagan2026twohump}; the campaign's own derived artifacts — word bank, quotient archive, certificates — will be released under the same terms.

## Per-campaign recipe

Six campaigns, each an independent, resumable, append-only JSONL stream keyed by (dataset, idx-or-form, word-or-arm, budget):

1. **Baseline reproduction** (cap-semantics check, \ref{sec:methods}). Entry: `run_greedy.py`. Parameters: `--cap {sum,per_relator} --budget {1e5,1e6} --workers N`. Output: one stream per (cap, budget) tier, one record per presentation index, distinguishing the per-relator cap ($L=24$) from the original sum cap.
2. **Naive $z=w$ arms** (Table \ref{tab:arms}). Entry: `run_greedy_sweep.py`. Parameters: arm $\in\{$baseline$,r_1,r_2,x,y\}$, budget $5\times10^5$, two-phase light/heavy worker scheduling so cheap instances finish first and memory-heavy ones run at low parallelism. Output: one stream per arm, records keyed by (dataset, idx, arm, budget) so arms merge directly for the subset/union comparison of \ref{sec:results}.
3. **AK(3) word bank** (Table \ref{tab:wordbank}). Entry: `run_ak3_wormhole.py`. Parameters: form $\in\{$textbook, rep$\}$, the 97-word bank, a two-tier budget ($10^5$-node screen, escalate every unsolved word to $10^6$), per-relator cap $L=24$. Output: one stream per (form, budget), named by the pattern `ak3_<form>_<budget>.jsonl`, keyed by word name.
4. **Hard-target controls** (Figure \ref{fig:hard_ties}). Entry: `run_hard_wormhole.py`. Parameters: MS(1190) indices $\{625,610\}$, target-specific word banks (the `relhalf` family re-derived from each target's own relators), $10^5$-node screen. Output: one stream per target index, keyed by word name.
5. **Five-lane campaign** (Table \ref{tab:lanes}). Entries: `plateau_elim.py` (Lane D's harvest/merge/solve phases), with `harvest_fast.py` as its numba-accelerated, byte-identical hot path; `stable_solver.py` (Lane B); `floor_census.py` (the two-floor census); `resolve_hi_l.py` (cap-gap re-solve of the shortest candidates at a raised per-relator cap); `collect_results.py`, which consolidates every box's streams into one archive plus a manifest. Parameters vary by phase: harvest budgets up to $\sim\!5\times10^5$ per combination, solve budgets $2.5\times10^4$–$2\times10^5$, `resolve_hi_l.py` at cap $L=40$. Output: per-combination candidate streams, a global merged-candidate stream, a solve-attempt stream, and certificate JSON files — keyed by (form, word) for harvest and by candidate canonical key for merge/solve.
6. **Cap control** (\ref{app:cap}). Entries: `run_captest.py` (positive-control gate, the search-cap arm, and the harvest-cap arm) and `solve_stratified.py` (the stratified-solve arm). Parameters: gate at $5\times10^4$ nodes; search arm at $\max\_len\in\{24,48\}$, $10^5$ nodes; harvest arm at per-relator cap $48$, total-length cap $40$, $6\times10^4$ nodes; stratified solve at $100$ candidates per length bucket $25$–$40$ plus $200$ short controls, $\max\_len=60$, budget $8\times10^4$ ($4\times10^4$ for the longest-tail bucket). Output: isolated JSONL streams, kept entirely separate from the main campaign's directories.

Every stream is append-only, one JSON record per line, flushed (and fsynced on cloud/networked mounts) after each write. A re-run of a finished sweep re-reads existing ids and exits as a no-op; a killed run resumes from the last complete line, discarding at most one in-flight record.

## Determinism and verification

The per-node hot paths — neighbor generation, canonicalization, Lemma-11 elimination — are numba-jitted. Every jitted path is held byte-identical to a pure-Python reference implementation via differential tests on real visited sets, with $0$ mismatches across the tested combinations. Every claimed solve is replayed through an independent path verifier before it is counted (Table \ref{tab:certs}, \ref{app:certs}), and every printed number in the paper is re-derived by an independent recomputation script run directly against the raw JSONL/gz streams, not against any intermediate digest.

## Compute

Development and calibration ran on a single consumer laptop ($16$ GB RAM); the five-lane escalation additionally used cloud CPU boxes (up to $8$ vCPU, up to $50$ GB RAM); the RL beam probe (Lane E) ran as CPU-only inference throughout. Per-attempt node budgets ranged from $2.5\times10^4$ to $10^6$; a greedy run's visited set carries roughly $40\times$ its node budget in entries, which is the binding memory constraint at the higher budgets. Total wall-clock across the full campaign was approximately one week.
