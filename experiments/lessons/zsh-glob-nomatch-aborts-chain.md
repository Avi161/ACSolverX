# [2026-07-08] zsh glob nomatch aborts a command chain [TRAP]
`rm -f results/*.jsonl && python …` — when the glob matches nothing, zsh errors on the glob and `&&` short-circuits, so the Python step silently never ran. **Rule:** use `find results -type f -delete` (or guard with `setopt null_glob`) instead of bare globs in `rm`.
