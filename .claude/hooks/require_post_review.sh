#!/usr/bin/env bash
# Checkpoint 2 gate (Stop hook).
# When there are uncommitted IMPLEMENTATION changes (anything outside the scratch
# dirs tmp/ and .research_executor/) but no FRESH Field Advisor post-review artifact,
# block stopping once and tell Claude to run advisor() + Field Advisor (post).
# Blocks at most once per stop-cycle (respects stop_hook_active) to avoid loops.
set -euo pipefail

PROJ="${CLAUDE_PROJECT_DIR:-$(pwd)}"
POST="$PROJ/tmp/field_advisor_post.md"

# Read stdin; if we're already in a stop-hook continuation, do not re-block (loop guard).
input="$(cat 2>/dev/null || true)"
if printf '%s' "$input" | grep -q '"stop_hook_active"[[:space:]]*:[[:space:]]*true'; then
  exit 0
fi

cd "$PROJ" 2>/dev/null || exit 0
command -v git >/dev/null 2>&1 || exit 0
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || exit 0

# Implementation changes = porcelain entries whose path is NOT under tmp/ or .research_executor/.
changed="$(git status --porcelain 2>/dev/null \
  | sed 's/^...//' \
  | sed 's/.* -> //' \
  | grep -vE '^(tmp/|\.research_executor/)' || true)"

[ -n "$changed" ] || exit 0   # nothing to review (clean or scratch-only) -> allow stop.

# Newest mtime among changed files.
newest=0
while IFS= read -r f; do
  [ -e "$f" ] || continue
  m=$(stat -f %m "$f" 2>/dev/null || stat -c %Y "$f" 2>/dev/null || echo 0)
  [ "$m" -gt "$newest" ] && newest=$m
done <<< "$changed"

post_m=0
[ -s "$POST" ] && post_m=$(stat -f %m "$POST" 2>/dev/null || stat -c %Y "$POST" 2>/dev/null || echo 0)

if [ "$post_m" -ge "$newest" ] && [ "$post_m" -gt 0 ]; then
  exit 0   # post-review is fresh (at least as new as the latest change) -> allow stop.
fi

echo "Dual-reviewer Checkpoint 2 NOT satisfied: uncommitted implementation changes exist but
$POST is missing or stale. Before finishing, review the produced artifacts with advisor()
FIRST, then the Field Advisor (post, which writes tmp/field_advisor_post.md), and address what
they surface. See CLAUDE.md 'Dual-reviewer workflow'. (Trivial/mechanical edits are exempt —
if this is one, commit the change or write tmp/field_advisor_post.md to clear the gate.)" >&2
exit 2
