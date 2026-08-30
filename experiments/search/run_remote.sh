#!/usr/bin/env bash
# Run the AC19 leftover campaign on a rented high-RAM CPU box (vast.ai, Hetzner,
# bare metal -- anything with SSH). Colab's constraint was RAM per row: at 5M
# nodes hcompact reserves ~34.7 GB for ONE row on ONE core, so a 51 GB Colab
# runs a single row at a time. A big-RAM box runs N of them, and N is what you
# are actually buying.
#
#   ./run_remote.sh plan     # what THIS box would do -- run before you rent
#   PLAN_GB=512 PLAN_CORES=64 ./run_remote.sh plan   # price an offer first
#   ./run_remote.sh smoke    # 2 rows x 2,000 nodes; proves the pipeline
#   ./run_remote.sh run      # the campaign, detached (survives an SSH drop)
#   ./run_remote.sh install-service   # ... and survives a Spot preemption
#   ./run_remote.sh tail     # follow the log
#   ./run_remote.sh report   # totals so far; safe to run mid-flight
#
# Env overrides: CAMPAIGN BUDGET MRL WORKERS ARMS OUT BRANCH REPO
set -euo pipefail
PLAN_GB=${PLAN_GB:-}; PLAN_CORES=${PLAN_CORES:-}

BRANCH=${BRANCH:-claude/ac19-leftover-solver-notebook-6yan6d}
REPO=${REPO:-https://github.com/Avi161/ACSolverX.git}
# One env var selects the whole campaign: budget, arm list, row lists and
# output filenames all follow from it (explicit BUDGET/ARMS still win).
# Without this, pre-staging u124 meant hand-assembling four flags that had
# to agree -- and a missed one ran the WRONG CAMPAIGN's rows at 10M.
CAMPAIGN=${CAMPAIGN:-ac19}
case "$CAMPAIGN" in
  ac19) BUDGET=${BUDGET:-5000000};  ARMS=${ARMS:-greedy s20_mk2} ;;
  u124) BUDGET=${BUDGET:-10000000}; ARMS=${ARMS:-s20_mk2} ;;
  *) echo "STOP: unknown CAMPAIGN='$CAMPAIGN' (ac19|u124)" >&2; exit 2 ;;
esac
MRL=${MRL:-64}
WORKERS=${WORKERS:-auto}
OUT=${OUT:-$HOME/leftovers_5m}
SRC=${SRC:-$HOME/ACSolverX}
LOG="$OUT/run.log"
PY=${PY:-python3}

have_repo() { [ -d "$SRC/experiments/search" ]; }

setup() {
  mkdir -p "$OUT"
  if ! have_repo; then
    command -v git >/dev/null || { apt-get update -qq && apt-get install -y -qq git; }
    git clone --branch "$BRANCH" --depth 1 "$REPO" "$SRC"
  fi
  cd "$SRC"
  # numba + numpy are the only runtime deps of the search. requirements.txt
  # pulls the JAX/PPO stack, which this campaign never imports -- skip it.
  # Debian 12 / Ubuntu 24 mark the system Python "externally managed" (PEP 668)
  # and refuse a plain pip install, which is exactly what a fresh GCE image is.
  if ! $PY -c 'import numba, numpy' 2>/dev/null; then
    $PY -m pip -q install numba numpy 2>/dev/null       || $PY -m pip -q install --break-system-packages numba numpy       || { sudo apt-get update -qq && sudo apt-get install -y -qq python3-pip            && $PY -m pip -q install --break-system-packages numba numpy; }
    $PY -c 'import numba, numpy' || { echo "STOP: numba unavailable"; exit 1; }
  fi
  export PYTHONPATH="$SRC"
}

plan() {
  setup
  $PY - <<'PYEOF'
import os, multiprocessing as mp
from experiments.search.run_leftovers_1m import est_gb, resolve_workers, _available_gb
from experiments.search.run_leftovers_5m import (
    SPEC_5M, plan_memory, load_rows_5m, TRACK_PATH)
from experiments.search.run_leftovers_1m import HAVE_HCOMPACT

B, MRL = int(os.environ["BUDGET"]), int(os.environ["MRL"])
CAMPAIGN = os.environ.get("CAMPAIGN", "ac19")
ARMS = os.environ.get("ARMS", "greedy s20_mk2").split()
# PLAN_GB/PLAN_CORES price an offer you have NOT rented yet -- the whole
# point on a spot market is choosing the box before paying for it.
gb = float(os.environ.get("PLAN_GB") or _available_gb())
cores = int(os.environ.get("PLAN_CORES") or mp.cpu_count())
where = "offer" if os.environ.get("PLAN_GB") else "this box"
print(f"{where:<15}: {cores} cores, {gb:.0f} GB RAM")
print(f"engine         : hcompact={HAVE_HCOMPACT}")
if not HAVE_HCOMPACT:
    raise SystemExit("STOP: hcompact missing -- the Python fallback at this "
                     "budget is a hundreds-of-GB code path, not a slow one.")
per = est_gb(B, MRL, track_path=TRACK_PATH)
print(f"budget {B:,} @ cap {MRL}: {per:.1f} GB per row"
      f"{' (paths captured)' if TRACK_PATH else ''}")
tot = 0.0
for arm in ARMS:
    n = len(load_rows_5m(arm, campaign=CAMPAIGN)[0])   # fails loudly on a stale clone
    w, _ = resolve_workers(arm, os.environ["WORKERS"], gb, cores, B, MRL,
                           track_path=TRACK_PATH)
    rate = 708 if arm == "greedy" else 846          # measured at 1M, this engine
    h = n * (B / rate) / 3600 / max(w, 1)
    tot += h
    print(f"  {arm:<8} {n:>3} rows, {w:>2} workers -> {h:5.1f} h  (worst case)")
print(f"total wall clock: {tot:.1f} h if every row runs the full budget")
lim, res = plan_memory(B, MRL, available_gb=gb, log=lambda *a: None)
if res is not None:
    from experiments.search.greedy_compact import est_states, _RESERVE_SLACK
    default = int(est_states(B) * _RESERVE_SLACK) + 4 * (MRL + 1) ** 2
    tag = "full" if res >= default else f"CLIPPED from {default:,} -- box is small"
    print(f"reserve_states  : {res:,} ({tag})")
PYEOF
}

smoke() { setup; for a in $ARMS; do
    $PY -m experiments.search.run_leftovers_5m --arm "$a" --campaign "$CAMPAIGN" \
        --smoke --out-dir "$OUT"; done; }

write_job() {
  cat > "$OUT/_job.sh" <<JOB
#!/usr/bin/env bash
set -euo pipefail
cd "$SRC"; export PYTHONPATH="$SRC"
# stdout goes to a log FILE under both systemd and nohup, so Python
# block-buffers it: heartbeats fire every 60s but the log freezes for ~27 min
# at a time, and tail -f shows nothing -- "a quiet hour is indistinguishable
# from a hung session". Unbuffered fixes the log, not the run.
export PYTHONUNBUFFERED=1
for a in $ARMS; do
  # --chunks 1 --chunk-index 1 is the SINGLE-BOX convention: stride_chunk(rows,
  # 1, 1) is rows[0::1], i.e. all of them, into one untagged jsonl -- which is
  # what the report subcommand already reads. Without it the runner falls back
  # to the arm's default chunk count (4 for greedy) and silently runs 22 of 88
  # rows, then prints CAMPAIGN COMPLETE. The 4-way split is for four Colabs.
  # NOTE: this heredoc is unquoted so \$BUDGET interpolates -- never put a
  # backtick or \$( ) in it, they execute HERE and splice output into the job.
  $PY -m experiments.search.run_leftovers_5m --arm "\$a" --campaign $CAMPAIGN \\
      --budget $BUDGET --mrl $MRL --workers $WORKERS \\
      --chunks 1 --chunk-index 1 --out-dir "$OUT"
done
echo "CAMPAIGN COMPLETE \$(date -u +%FT%TZ)"
# Best-effort beacon into Cloud Logging so an alert policy can email the
# owner at completion even if no session is watching. Harmless where
# gcloud or the logWriter role is absent. (Heredoc rule: no backticks, no
# unescaped command substitution.)
command -v gcloud >/dev/null 2>&1 && gcloud logging write ac19-campaign \\
    "CAMPAIGN COMPLETE $CAMPAIGN" --severity=NOTICE 2>/dev/null || true
JOB
  chmod +x "$OUT/_job.sh"
}

run() {
  setup; write_job
  # setsid + nohup: the run outlives the SSH session that started it. On a
  # rented box the connection WILL drop; the job must not care.
  setsid nohup "$OUT/_job.sh" >>"$LOG" 2>&1 < /dev/null &
  echo "started pid $! -- log: $LOG"
  echo "results (rsync these off the box BEFORE you destroy it):"
  echo "  rsync -avz <user>@<host>:$OUT/*.jsonl ./"
}

# A Spot VM WILL be preempted during a 14 h run. With
# --instance-termination-action=STOP the disk survives, so the whole recovery
# is "boot again": this unit restarts the campaign and RESUME skips every row
# already on disk. Nothing to babysit.
install_service() {
  setup; write_job
  sudo tee /etc/systemd/system/ac19.service >/dev/null <<UNIT
[Unit]
Description=AC19 leftover campaign
After=network-online.target

[Service]
Type=simple
User=$(id -un)
Environment=PYTHONUNBUFFERED=1
ExecStart=$OUT/_job.sh
StandardOutput=append:$LOG
StandardError=append:$LOG
Restart=on-failure
RestartSec=30

[Install]
WantedBy=multi-user.target
UNIT
  sudo systemctl daemon-reload
  sudo systemctl enable --now ac19.service
  echo "ac19.service enabled -- survives reboot AND Spot preemption."
  echo "  status: systemctl status ac19  |  log: $LOG"
}

# Write the job script and print its path, starting nothing. Exists so the
# generated file can be syntax-checked -- a heredoc that silently executes
# something at generation time produces a job that dies on its first line.
job_only() { setup; write_job; echo "$OUT/_job.sh"; }

tail_log() { tail -f "$LOG"; }

report() { setup; for a in $ARMS; do
    $PY -c "
from experiments.search.run_leftovers_5m import report_5m
report_5m('$a', '$OUT', chunks=1, chunk_index=1, budget=$BUDGET, mrl=$MRL,
          campaign='$CAMPAIGN')"; done; }

# Assert the generated job and the installed unit agree with THIS config.
# Read-only: never patches, never starts or stops anything -- a boot-time
# self-heal script calls this and decides what to do with a failure (the
# convention: an unparseable job means do NOT start the unit). Campaign
# flags are derived from the same variables that wrote the job, so the
# checks can never rot against a new campaign the way a hardcoded
# "--mrl 64" list would. UNIT_FILE is overridable for tests.
UNIT_FILE=${UNIT_FILE:-/etc/systemd/system/ac19.service}
verify() {
  local job="$OUT/_job.sh" fail=0
  chk() { if [ "$1" = 0 ]; then echo "verify: PASS -- $2";
          else echo "verify: FAIL -- $2"; fail=1; fi; }
  if [ ! -f "$job" ]; then
    chk 1 "job exists: $job"
  else
    if bash -n "$job" 2>/dev/null; then chk 0 "job parses"; else chk 1 "job parses"; fi
    if grep -q 'PYTHONUNBUFFERED=1' "$job"; then chk 0 "job exports PYTHONUNBUFFERED"; else chk 1 "job exports PYTHONUNBUFFERED"; fi
    for flag in "--campaign $CAMPAIGN" "--budget $BUDGET" "--mrl $MRL" \
                "--chunks 1 --chunk-index 1"; do
      if grep -q -- "$flag" "$job"; then chk 0 "job carries $flag"; else chk 1 "job carries $flag"; fi
    done
    if grep -q '`' "$job"; then chk 1 "no backticks in job"; else chk 0 "no backticks in job"; fi
    # $( ) may appear in comments (the heredoc warning mentions it) and in
    # the one CAMPAIGN COMPLETE date line; anywhere else is a splice.
    splices=$(grep '\$(' "$job" | grep -v '^[[:space:]]*#' \
              | grep -vc 'CAMPAIGN COMPLETE' || true)
    if [ "${splices:-0}" = 0 ]; then chk 0 "no spliced command output"; else chk 1 "no spliced command output"; fi
  fi
  if [ -f "$UNIT_FILE" ]; then
    if grep -q 'Environment=PYTHONUNBUFFERED=1' "$UNIT_FILE"; then chk 0 "unit sets PYTHONUNBUFFERED"; else chk 1 "unit sets PYTHONUNBUFFERED"; fi
    if grep -q "ExecStart=$job" "$UNIT_FILE"; then chk 0 "unit runs this job"; else chk 1 "unit runs this job"; fi
  else
    echo "verify: WARN -- unit not installed at $UNIT_FILE"
  fi
  if PYTHONPATH="$SRC" $PY -c 'from experiments.heuristic_search.core import hcompact' 2>/dev/null; then
    chk 0 "hcompact engine imports"
  else
    chk 1 "hcompact engine imports (python fallback would be silent and wrong)"
  fi
  return $fail
}

export BUDGET MRL WORKERS ARMS CAMPAIGN PLAN_GB PLAN_CORES
case "${1:-plan}" in
  plan) plan ;; smoke) smoke ;; run) run ;;
  install-service) install_service ;;
  job) job_only ;;
  verify) verify ;;
  tail) tail_log ;; report) report ;;
  *) echo "usage: $0 {plan|smoke|run|install-service|job|verify|tail|report}" >&2; exit 2 ;;
esac
