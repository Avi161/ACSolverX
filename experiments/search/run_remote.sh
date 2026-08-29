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
#   ./run_remote.sh tail     # follow the log
#   ./run_remote.sh report   # totals so far; safe to run mid-flight
#
# Env overrides: BUDGET MRL WORKERS ARMS OUT BRANCH REPO
set -euo pipefail
PLAN_GB=${PLAN_GB:-}; PLAN_CORES=${PLAN_CORES:-}

BRANCH=${BRANCH:-claude/ac19-leftover-solver-notebook-6yan6d}
REPO=${REPO:-https://github.com/Avi161/ACSolverX.git}
BUDGET=${BUDGET:-5000000}
MRL=${MRL:-48}
WORKERS=${WORKERS:-auto}
ARMS=${ARMS:-greedy s20_mk2}
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
  $PY -c 'import numba, numpy' 2>/dev/null || $PY -m pip -q install numba numpy
  export PYTHONPATH="$SRC"
}

plan() {
  setup
  $PY - <<'PYEOF'
import os, multiprocessing as mp
from experiments.search.run_leftovers_1m import est_gb, resolve_workers, _available_gb
from experiments.search.run_leftovers_5m import SPEC_5M, plan_memory, load_rows_5m
from experiments.search.run_leftovers_1m import HAVE_HCOMPACT

B, MRL = int(os.environ["BUDGET"]), int(os.environ["MRL"])
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
per = est_gb(B, MRL)
print(f"budget {B:,} @ cap {MRL}: {per:.1f} GB per row")
tot = 0.0
for arm in ("greedy", "s20_mk2"):
    n = len(load_rows_5m(arm)[0])   # also fails loudly on a stale clone
    w, _ = resolve_workers(arm, os.environ["WORKERS"], gb, cores, B, MRL)
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
    $PY -m experiments.search.run_leftovers_5m --arm "$a" --smoke --out-dir "$OUT"; done; }

run() {
  setup
  # setsid + nohup: the run outlives the SSH session that started it. On a
  # rented box the connection WILL drop; the job must not care.
  cat > "$OUT/_job.sh" <<JOB
#!/usr/bin/env bash
set -euo pipefail
cd "$SRC"; export PYTHONPATH="$SRC"
for a in $ARMS; do
  $PY -m experiments.search.run_leftovers_5m --arm "\$a" --budget $BUDGET \\
      --mrl $MRL --workers $WORKERS --out-dir "$OUT"
done
echo "CAMPAIGN COMPLETE \$(date -u +%FT%TZ)"
JOB
  chmod +x "$OUT/_job.sh"
  setsid nohup "$OUT/_job.sh" >>"$LOG" 2>&1 < /dev/null &
  echo "started pid $! -- log: $LOG"
  echo "results (rsync these off the box BEFORE you destroy it):"
  echo "  rsync -avz <user>@<host>:$OUT/*.jsonl ./"
}

tail_log() { tail -f "$LOG"; }

report() { setup; for a in $ARMS; do
    $PY -c "
from experiments.search.run_leftovers_5m import report_5m
report_5m('$a', '$OUT', chunks=1, chunk_index=1, budget=$BUDGET, mrl=$MRL)"; done; }

export BUDGET MRL WORKERS ARMS PLAN_GB PLAN_CORES
case "${1:-plan}" in
  plan) plan ;; smoke) smoke ;; run) run ;;
  tail) tail_log ;; report) report ;;
  *) echo "usage: $0 {plan|smoke|run|tail|report}" >&2; exit 2 ;;
esac
