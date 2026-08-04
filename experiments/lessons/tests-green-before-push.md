# [WORKS] Never push heuristic Colab/runner work until the related tests are green

Before any `git push` of notebook or runner changes, run the suite that
covers what you touched and wait for a green summary. A push that lands
files the user will open in Colab without that gate has already failed the
handoff — they will burn GPU/CPU time on a broken path.

For the unsolved124 × s20_mk2 census that means at least:

```bash
PYTHONPATH=. python3 -m pytest tests/heuristic_search/test_unsolved124_s20mk2.py -q
PYTHONPATH=. python3 experiments/heuristic_search/runners/mini_u124_s20mk2_mock.py
```

Do not treat "I ran them earlier this session" as enough — re-run after the
last edit, then push. Report the pass count in the handoff.
