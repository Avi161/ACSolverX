#!/bin/bash
# EC2 user-data: is the relator-length cap an issue for the rank-3 baseline?
#
# 1. cap_exhaustion on the cap-24 results in S3: unsolved searches that stopped
#    below the budget (the cap emptied the frontier).
# 2. The cap-24 results cut to word lengths 1..MAX_LEN, summarized on their own
#    (the pool the other caps are compared on).
# 3. For each cap in CAPS: the control, every word of length 1..MAX_LEN and the
#    relator subwords at that cap (run_rank3_bf --cap), verifier, summary,
#    graph, class view, cap_exhaustion.
#
# Outputs: s3://$BUCKET/$ROOT/cap/out/ (tables), .../cap/cap<N>/results/ (raw,
# resumable). Launch with --instance-initiated-shutdown-behavior terminate.
CAPS="32 48"
BUDGET=1000
MAX_LEN=6
WORKERS=""               # empty = every online core
PRE_IDS="0,320"
PRE_MAX_LEN=3
ROOT=cov_all/rank3_bf
DEADMAN=240
BRANCH=rank3/brute-force-baseline
SHA=SET_ME
BUCKET=acsolver-u124-205558941715
export HOME=/root AWS_DEFAULT_REGION=us-east-1
mkdir -p /opt/r3
exec >> /opt/r3/run.log 2>&1
shutdown -h +$DEADMAN
B=s3://$BUCKET/$ROOT
MOD=experiments.stable_ac.rank3
OUT=/opt/r3/out
T=$(curl -s -X PUT http://169.254.169.254/latest/api/token -H 'X-aws-ec2-metadata-token-ttl-seconds: 600')
md(){ curl -s -H "X-aws-ec2-metadata-token: $T" http://169.254.169.254/latest/meta-data/$1; }
putlog(){ aws s3 cp /opt/r3/run.log $B/cap/run.log --only-show-errors; }
say(){ echo "$(date -u +%FT%TZ) == $*"; putlog; }
up(){ aws s3 sync $OUT/ $B/cap/out/ --only-show-errors; putlog; }
fail(){ say "FAIL: $*"; up; shutdown -h now; exit 1; }

echo "$(date -u +%FT%TZ) == boot $(md instance-id) $(md instance-type) $(md placement/availability-zone) life=$(md instance-life-cycle) cores=$(getconf _NPROCESSORS_ONLN)"
if ! putlog; then echo "R3: S3 WRITE FAILED, shutting down" > /dev/console; shutdown -h now; exit 1; fi

dnf install -y -q python3.12 python3.12-pip git || fail dnf
git config --system --add safe.directory '*'
cd /opt/r3
git clone -q --branch $BRANCH --single-branch https://github.com/Avi161/ACSolverX.git acsx || fail clone
cd acsx
git checkout -q $SHA || fail checkout
python3.12 -m venv /opt/r3/venv || fail venv
/opt/r3/venv/bin/pip -q install numpy==2.1.3 numba==0.63.1 pytest matplotlib \
  || /opt/r3/venv/bin/pip -q install numpy numba pytest matplotlib || fail pip
PY=/opt/r3/venv/bin/python3
export PYTHONPATH=. NUMBA_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 MPLBACKEND=Agg
N=${WORKERS:-$(getconf _NPROCESSORS_ONLN)}
say "env $($PY -c 'import sys,numpy,numba;print(sys.version.split()[0],numpy.__version__,numba.__version__)') commit=$(git rev-parse --short HEAD) workers=$N budget=$BUDGET max_len=$MAX_LEN caps=$CAPS"

$PY -m pytest tests/stable_ac/test_rank3_bf.py -q -p no:cacheprovider 2>&1 | tail -3
[ "${PIPESTATUS[0]}" -eq 0 ] || fail pytest
say "tests passed"
mkdir -p $OUT

step(){ # step <name> <command...>: run, keep the output, log the exit code
  local name=$1; shift
  "$@" > $OUT/log_${name}.txt 2>&1
  local rc=$?
  tail -c 3000 $OUT/log_${name}.txt
  say "$name exit=$rc"
  return $rc
}
post(){ # post <dir> <cap>: summary, graph, class view, exhaustion of one cap
  local d=$1 cap=$2
  step summarize_cap$cap $PY -m $MOD.summarize_rank3_bf --dir $d --budget $BUDGET --cap $cap
  step plot_cap$cap $PY -m $MOD.plot_rankn_vs_control --rank3 $d --budget $BUDGET --cap $cap
  step classes_cap$cap $PY -m $MOD.class_view --rank3 $d --budget $BUDGET --cap $cap
  step exhaustion_cap$cap $PY -m $MOD.cap_exhaustion --dir $d --out $d/cap_exhaustion_cap$cap.json
  mkdir -p $OUT/cap$cap
  cp $d/*.md $d/*.png $d/*.csv $d/*_summary.json $d/*_class_view.json $d/cap_exhaustion_cap$cap.json $OUT/cap$cap/ 2>/dev/null
  up
}

# 1. the cap-24 results as they are
mkdir -p /opt/r3/c24
for src in b1000 b10000 rankn; do
  aws s3 sync $B/$src/results/ /opt/r3/c24/ --exclude 'shards/*' --exclude '*.tmp*' --exclude '*.log' --only-show-errors
done
say "cap 24 files: $(ls /opt/r3/c24 | grep -c .)"
step exhaustion_all_cap24 $PY -m $MOD.cap_exhaustion --dir /opt/r3/c24 --out $OUT/cap_exhaustion_all_cap24.json
up

# 2. cap 24 on the comparison pool (lengths 1..MAX_LEN, no inverse words)
S24=rank3_bf_ms640_b${BUDGET}_cap24
mkdir -p /opt/r3/cap24
cp /opt/r3/c24/${S24}_control.jsonl /opt/r3/c24/${S24}_relsub.jsonl /opt/r3/cap24/ || fail cap24-copy
for n in $(seq 1 $MAX_LEN); do cp /opt/r3/c24/${S24}_L$n.npz /opt/r3/cap24/ || fail cap24-copy; done
post /opt/r3/cap24 24

# 3. the same pool at each larger cap
for CAP in $CAPS; do
  D=/opt/r3/cap$CAP
  P=$B/cap/cap$CAP
  say "cap $CAP preflight start"
  $PY -m $MOD.run_rank3_bf --budget $BUDGET --cap $CAP --workers $N --max-len $PRE_MAX_LEN \
    --inv-max-len 0 --pres "$PRE_IDS" --out-dir /opt/r3/pre$CAP || fail "preflight-run cap $CAP"
  $PY -m $MOD.verify_rank3_bf --dir /opt/r3/pre$CAP --recheck 10 || fail "preflight-verify cap $CAP"
  say "cap $CAP preflight verified"
  mkdir -p $D
  aws s3 sync $P/results/ $D/ --only-show-errors
  say "cap $CAP restored $(find $D -type f | wc -l) files from S3"
  ( while true; do sleep 120
    aws s3 sync $D/ $P/results/ --exclude '*.tmp*' --only-show-errors; putlog
    OOM=$(dmesg 2>/dev/null | grep -c -i -E 'out of memory|oom-kill')
    echo "$(date -u +%FT%TZ) mem $(free -g | awk '/Mem:/{print "used="$3"G avail="$7"G"}') py=$(pgrep -fc run_rank3_bf) oom=$OOM"
    if [ "$OOM" -gt 0 ]; then fail "oom-kill seen, pool would hang"; fi
  done ) &
  SYNC=$!
  say "cap $CAP full start"
  $PY -m $MOD.run_rank3_bf --budget $BUDGET --cap $CAP --workers $N --max-len $MAX_LEN \
    --inv-max-len 0 --out-dir $D || fail "full-run cap $CAP"
  kill $SYNC
  aws s3 sync $D/ $P/results/ --exclude '*.tmp*' --only-show-errors
  step verify_cap$CAP $PY -m $MOD.verify_rank3_bf --dir $D --recheck 20
  say "cap $CAP verify exit=$?"
  post $D $CAP
done
aws s3 ls --recursive $B/cap/out/
say "DONE"
shutdown -h now
