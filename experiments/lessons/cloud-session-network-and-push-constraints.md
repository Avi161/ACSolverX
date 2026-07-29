# Cloud session: scholarly hosts are proxy-blocked; push can 403 — mirror and notify

2026-07-29, fable line (branch claude/ac-stable-ac-conjecture-ijfzgz).

- [TRAP] The cloud egress proxy returns CONNECT 403 for every scholarly host tried
  (arxiv.org and mirrors, ar5iv, Semantic Scholar, publisher sites, even Wikipedia), and
  WebFetch 403s on ALL urls including example.com. Only WebSearch (indexed snippets) and
  git-over-HTTPS to github.com work. Never claim a paper "cannot be verified" without
  trying a GitHub mirror of its sources first.
- [WORKS] Paper LaTeX is often on GitHub: the Shehper et al. AC paper's full source lives
  at github.com/ammedmar/ac_paper (coauthor's repo) and the AC-Solver code at
  github.com/shehper/AC-Solver — `git clone` through the proxy works and yields verbatim
  appendix text that WebSearch snippets garble. Clone to scratch, quote from source.
- [TRAP] `git push` to origin can be denied (403 "Permission … denied to <owner>" at
  receive-pack) while fetch works, and the GitHub API write path can be denied
  simultaneously ("Resource not accessible by integration"). This is a credential/App
  permission state, not transient: after 4 backoff retries, notify the user by push
  notification, keep committing locally every cycle, and retry the push once per cycle.
  Log the blockage in the day log so the eventual push carries the history.
- [WORKS] Log-heading timestamps must be MEASURED (`date -u` at commit time), never
  estimated from felt elapsed time — two early headings this session ran ~30 min ahead of
  reality and needed a correction note.
