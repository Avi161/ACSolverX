# [2026-07-29] Colab live-run hotfixes are .py-only — never touch the open notebook [WORKS]

**User contract (bench60 @1M and every later Colab campaign):** while the user has sessions
running, do **not** edit the `.ipynb`. If heartbeat, `nodes_explored/s`, ETA, mirror,
resume, worker count, or any runner bug needs a fix — change only importable modules
under `experiments/` (e.g. `heuristic_search/runners/run_ab.py`, `run_s24_scale.py`),
commit + push to the notebook's `BRANCH`. The user Runtime → Restart → Run All; SETUP's
`UPDATE_REPO` (`git reset --hard`) + `sys.modules` purge loads the new `.py`. Drive
jsonl resume continues. Editing the notebook forces re-open from GitHub in every parallel
session and wastes wall time.

Touch the `.ipynb` only when a new CONFIG knob is unavoidable — and say so explicitly so
the user re-opens from GitHub.
