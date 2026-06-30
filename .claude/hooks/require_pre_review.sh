#!/usr/bin/env bash
# Checkpoint 1 gate (PreToolUse matcher: ExitPlanMode).
# Blocks leaving plan mode / starting implementation until a FRESH Field Advisor
# pre-review artifact exists. advisor() leaves no artifact, so we can only enforce
# the Field Advisor file + remind about advisor(). See CLAUDE.md "Dual-reviewer workflow".
set -euo pipefail

PROJ="${CLAUDE_PROJECT_DIR:-$(pwd)}"
PRE="$PROJ/tmp/field_advisor_pre.md"
MAX_AGE_MIN="${FIELD_ADVISOR_PRE_MAX_AGE_MIN:-120}"

block() {
  # exit 2 + stderr => PreToolUse deny; message is shown to Claude.
  echo "$1" >&2
  exit 2
}

[ -s "$PRE" ] || block "Dual-reviewer Checkpoint 1 NOT satisfied: missing $PRE.
Before exiting plan mode, review the plan with BOTH advisor() AND the Field Advisor
(warm-pre, which writes tmp/field_advisor_pre.md). See CLAUDE.md 'Dual-reviewer workflow'.
To bypass for a genuinely trivial edit, set FIELD_ADVISOR_PRE_MAX_AGE_MIN=0 is NOT enough —
run the review or touch the file deliberately."

# Freshness: a stale pre-review from a previous task must not pass.
now=$(date +%s)
mtime=$(stat -f %m "$PRE" 2>/dev/null || stat -c %Y "$PRE" 2>/dev/null || echo 0)
age_min=$(( (now - mtime) / 60 ))
if [ "$age_min" -gt "$MAX_AGE_MIN" ]; then
  block "Dual-reviewer Checkpoint 1: $PRE is stale (${age_min} min old, limit ${MAX_AGE_MIN}).
Re-run the Field Advisor (warm-pre) on the CURRENT plan + advisor() before exiting plan mode."
fi

# Reminder (non-blocking): advisor() cannot be detected from a hook.
echo "Checkpoint 1 pre-review present (${age_min} min old). Confirm advisor() was also run on this plan." >&2
exit 0
