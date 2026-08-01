# Experiments and certificates

Scout first: use short runs, the local node cap of 1,000, and small presentation subsets. Compare candidate arms on a pre-registered denominator, confirm that the control has dynamic range, then scale only the winner. A search at budget `B` is the first `B` pops of a longer search; do not burn a large local budget merely to be sure. Put production-scale work in a Colab CONFIG/SETUP/RUN notebook and preserve resumable JSONL results.

Treat ceilings, budgets, and all result-affecting knobs as distinct. Record what evidence varied, maintain resume identity, and never let a verifier share the search canonicalisation it is supposed to check. Persist computed rows before enrichment; write locally and mirror whole files rather than appending to Drive.

During a live Colab session, hotfix only importable `experiments/**/*.py` on the notebook branch for heartbeat, pops/s, ETA, mirror, or resume fixes. Do not edit the open notebook except to add a new CONFIG knob. Restart then Run All must reload modules and continue the Drive JSONL contract.
