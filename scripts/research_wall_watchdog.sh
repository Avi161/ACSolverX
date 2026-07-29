#!/usr/bin/env bash
# Keep scale10k / ak3 / more_mini alive until wall_end; then finalize Colab handoff.
set -euo pipefail
cd /workspace/.worktrees/heur-12h
WALL_END="2026-07-29T16:12:20+00:00"
LOG=results/heuristic_search/scale10k/watchdog.log
mkdir -p results/heuristic_search/scale10k

tmux_run() {
  local sess="$1" cmd="$2"
  tmux -f /exec-daemon/tmux.portal.conf has-session -t "=$sess" 2>/dev/null \
    || tmux -f /exec-daemon/tmux.portal.conf new-session -d -s "$sess" -c "$PWD" -- "${SHELL:-bash}" -l
  # only start if no matching python already
  if ! pgrep -f "$3" >/dev/null 2>&1; then
    echo "$(date -u +%H:%M:%S) restart $sess" | tee -a "$LOG"
    tmux -f /exec-daemon/tmux.portal.conf send-keys -t "$sess:0.0" "$cmd" C-m
  fi
}

while true; do
  NOW_EPOCH=$(date -u +%s)
  WALL_EPOCH=$(date -u -d "$WALL_END" +%s 2>/dev/null || python3 -c "from datetime import datetime,timezone; print(int(datetime.fromisoformat('$WALL_END'.replace('+00:00','+00:00')).timestamp()))")
  REMAIN=$((WALL_EPOCH - NOW_EPOCH))
  echo "$(date -u +%H:%M:%S) watchdog remain=${REMAIN}s" >> "$LOG"

  if (( REMAIN <= 0 )); then
    echo "$(date -u +%H:%M:%S) WALL HIT — finalize Colab" | tee -a "$LOG"
    python3 -m experiments.heuristic_search.runners.finalize_colab_handoff \
      2>&1 | tee -a results/heuristic_search/scale10k/finalize.log || true
    break
  fi

  tmux_run scale10k-research \
    'python3 -m experiments.heuristic_search.runners.research_scale10k 2>&1 | tee -a results/heuristic_search/scale10k/run.log' \
    'research_scale10k'

  tmux_run ak3-proofs-inspired \
    'python3 -m experiments.heuristic_search.runners.research_ak3_proofs_inspired 2>&1 | tee -a results/heuristic_search/ak3_proofs_inspired/run.log' \
    'research_ak3_proofs_inspired'

  tmux_run more-mini \
    'python3 -m experiments.heuristic_search.runners.research_more_mini 2>&1 | tee -a results/heuristic_search/more_mini/run.log' \
    'research_more_mini'

  # campaign optional — leave if alive, do not restart if user stopped
  sleep 180
done
echo "$(date -u +%H:%M:%S) watchdog exit" | tee -a "$LOG"
