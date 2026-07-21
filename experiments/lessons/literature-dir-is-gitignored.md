# [2026-07-21] `literature/` is gitignored — theory written there never reaches the remote [TRAP]

Commit `4cfa57d` was made with `git add literature/proofs/STABLE_AC_NEW.tex literature/proofs/STABLE_AC_NEW.pdf …` plus several other paths. The commit succeeded and was pushed — but the two literature paths were silently skipped: `.gitignore` line 16 ignores the whole `literature/` directory, and `git add` of an ignored path only *warns* (a warning that scrolls past in a multi-path add) while the commit proceeds with whatever else was staged. The night's two new theorem sections existed only on local disk while the push message claimed they were shipped.

Root cause: the ignore is deliberate (the directory holds downloaded papers/PDFs), but it also swallows the project's OWN proof documents (`PROOFS.tex`, `STABLE_AC_NEW.tex`), which every doc cross-references as if they were shared artifacts.

Fixed by: committed markdown summaries of any theory result under `results/stable_ac/theory/` (`THEORY_NIGHT_2026_07_21.md`, `OBSTRUCTION_BARRIER.md`), with the .tex as the local-only formal companion.

**Rule:** anything under `literature/` is local-only — never claim a result is committed/pushed because a `.tex` there was edited. A shareable result needs a summary in a committed home (`results/stable_ac/theory/`). And after any multi-path `git add`, verify the commit actually contains the load-bearing file (`git show --stat`) before reporting it shipped.
