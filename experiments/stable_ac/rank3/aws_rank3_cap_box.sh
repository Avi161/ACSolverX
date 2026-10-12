#!/bin/bash
# EC2 user-data: is the relator-length cap an issue for the rank-3 baseline?
# Second cap box. The first one (this file at commit c1b2148) counted the
# cap-24 searches that the cap ended early and reran budget 1,000 (control,
# relator subwords, words of length 1..6) at caps 32 and 48; its raw results
# are in s3://$BUCKET/$ROOT/cap/cap32|cap48/results/.
#
# This box:
# 1. cuts the cap-24 results of each budget to the comparison pool (control,
#    relator subwords, words of length 1..maxlen) and compares the caps the
#    first box ran with it, search by search (cap_compare);
# 2. runs each job in JOBS (budget:cap): preflight, the same pool at that cap
#    (run_rank3_bf --cap), verifier, and the comparison again;
# 3. summary, graph, class view and cap_exhaustion for every (budget, cap).
#
# Outputs: s3://$BUCKET/$ROOT/cap/final/ (tables), .../cap/b<B>_cap<C>/results/
# (raw, resumable). Launch with --instance-initiated-shutdown-behavior terminate.
JOBS="10000:32 1000:20 10000:48"
DONE_B1000="32 48"       # caps the first box ran at budget 1,000
maxlen(){ case $1 in 1000) echo 6;; 10000) echo 4;; *) echo 3;; esac; }
WORKERS=""               # empty = every online core
PRE_IDS="0,320"
PRE_MAX_LEN=3
ROOT=cov_all/rank3_bf
DEADMAN=180
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
putlog(){ aws s3 cp /opt/r3/run.log $B/cap/run2.log --only-show-errors; }
say(){ echo "$(date -u +%FT%TZ) == $*"; putlog; }
up(){ aws s3 sync $OUT/ $B/cap/final/ --only-show-errors; putlog; }
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
say "env $($PY -c 'import sys,numpy,numba;print(sys.version.split()[0],numpy.__version__,numba.__version__)') commit=$(git rev-parse --short HEAD) workers=$N jobs=$JOBS"

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
post(){ # post <budget> <cap>: summary, graph, class view, exhaustion of one run
  local b=$1 cap=$2 t=b${1}_cap${2}
  local d=/opt/r3/$t
  step summarize_$t $PY -m $MOD.summarize_rank3_bf --dir $d --budget $b --cap $cap
  step plot_$t $PY -m $MOD.plot_rankn_vs_control --rank3 $d --budget $b --cap $cap
  step classes_$t $PY -m $MOD.class_view --rank3 $d --budget $b --cap $cap
  step exhaustion_$t $PY -m $MOD.cap_exhaustion --dir $d --out $d/cap_exhaustion_$t.json
  mkdir -p $OUT/$t
  cp $d/*.md $d/*.png $d/*.csv $d/*_summary.json $d/*_class_view.json $d/cap_exhaustion_$t.json $OUT/$t/ 2>/dev/null
  up
}
compare(){ # compare <budget>: every finished cap of that budget against cap 24
  local b=$1 others="" d
  for d in /opt/r3/b${b}_cap*; do
    [ "$d" = /opt/r3/b${b}_cap24 ] && continue
    ls $d/rank3_bf_ms640_b${b}_cap*_relsub.jsonl > /dev/null 2>&1 || continue
    others="$others --other $d"
  done
  [ -n "$others" ] || return 0
  step compare_b$b $PY -m $MOD.cap_compare --base /opt/r3/b${b}_cap24 $others \
    --budget $b --out $OUT/cap_compare_b$b.json
  up
}

# 1. cap 24 cut to the comparison pool of each budget, and the caps already run
for b in 1000 10000; do
  d=/opt/r3/b${b}_cap24
  s=rank3_bf_ms640_b${b}_cap24
  mkdir -p $d
  for f in ${s}_control.jsonl ${s}_relsub.jsonl $(for n in $(seq 1 $(maxlen $b)); do echo ${s}_L$n.npz; done); do
    aws s3 cp $B/b$b/results/$f $d/$f --only-show-errors || fail "cap 24 $f"
  done
  post $b 24
done
for c in $DONE_B1000; do
  mkdir -p /opt/r3/b1000_cap$c
  aws s3 sync $B/cap/cap$c/results/ /opt/r3/b1000_cap$c/ --exclude 'shards/*' \
    --exclude '*.tmp*' --exclude '*.log' --only-show-errors || fail "restore cap $c"
  post 1000 $c
done
compare 1000

# 2. the same pool at each (budget, cap) of JOBS
for J in $JOBS; do
  BUDGET=${J%%:*}
  CAP=${J##*:}
  TAG=b${BUDGET}_cap${CAP}
  D=/opt/r3/$TAG
  P=$B/cap/$TAG
  say "$TAG preflight start"
  $PY -m $MOD.run_rank3_bf --budget $BUDGET --cap $CAP --workers $N --max-len $PRE_MAX_LEN \
    --inv-max-len 0 --pres "$PRE_IDS" --out-dir /opt/r3/pre_$TAG || fail "preflight-run $TAG"
  $PY -m $MOD.verify_rank3_bf --dir /opt/r3/pre_$TAG --recheck 10 || fail "preflight-verify $TAG"
  say "$TAG preflight verified"
  mkdir -p $D
  aws s3 sync $P/results/ $D/ --only-show-errors
  say "$TAG restored $(find $D -type f | wc -l) files from S3"
  ( while true; do sleep 120
    aws s3 sync $D/ $P/results/ --exclude '*.tmp*' --only-show-errors; putlog
    OOM=$(dmesg 2>/dev/null | grep -c -i -E 'out of memory|oom-kill')
    echo "$(date -u +%FT%TZ) mem $(free -g | awk '/Mem:/{print "used="$3"G avail="$7"G"}') py=$(pgrep -fc run_rank3_bf) oom=$OOM"
    if [ "$OOM" -gt 0 ]; then fail "oom-kill seen, pool would hang"; fi
  done ) &
  SYNC=$!
  say "$TAG full start"
  $PY -m $MOD.run_rank3_bf --budget $BUDGET --cap $CAP --workers $N --max-len $(maxlen $BUDGET) \
    --inv-max-len 0 --out-dir $D || fail "full-run $TAG"
  kill $SYNC
  aws s3 sync $D/ $P/results/ --exclude '*.tmp*' --only-show-errors
  step verify_$TAG $PY -m $MOD.verify_rank3_bf --dir $D --recheck 20
  post $BUDGET $CAP
  compare $BUDGET
done
aws s3 ls --recursive $B/cap/final/
say "DONE"
shutdown -h now
