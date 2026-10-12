#!/bin/bash
# EC2 user-data: verify, summarize and plot the rank-3/4/5 sweeps from S3, then
# shut down. No search of its own beyond the verifier's reference re-checks and
# the independent checks in indep/.
#
# Pass "preview" runs at once on whatever is merged in S3. Pass "final" runs
# when both sweep boxes have logged DONE, or at WAIT_UNTIL (UTC epoch) on
# whatever is merged by then. Outputs: s3://$BUCKET/$ROOT/post/<pass>/.
ROOT=cov_all/rank3_bf
DEADMAN=1020
WAIT_UNTIL=0             # UTC epoch seconds; 0 = preview pass only
INDEP_MIN=40             # wall-clock box of the independent search check
BRANCH=rank3/brute-force-baseline
SHA=SET_ME
BUCKET=acsolver-u124-205558941715
export HOME=/root AWS_DEFAULT_REGION=us-east-1
mkdir -p /opt/r3
exec >> /opt/r3/run.log 2>&1
shutdown -h +$DEADMAN
B=s3://$BUCKET/$ROOT
RD=results/stable_ac/rank3_bf
MOD=experiments.stable_ac.rank3
IND=experiments/stable_ac/rank3/indep
T=$(curl -s -X PUT http://169.254.169.254/latest/api/token -H 'X-aws-ec2-metadata-token-ttl-seconds: 600')
md(){ curl -s -H "X-aws-ec2-metadata-token: $T" http://169.254.169.254/latest/meta-data/$1; }
putlog(){ aws s3 cp /opt/r3/run.log $B/post/run.log --only-show-errors; }
say(){ echo "$(date -u +%FT%TZ) == $*"; putlog; }
fail(){ say "FAIL: $*"; shutdown -h now; exit 1; }

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
say "env $($PY -c 'import sys,numpy,numba,matplotlib;print(sys.version.split()[0],numpy.__version__,numba.__version__,matplotlib.__version__)') commit=$(git rev-parse --short HEAD)"

$PY -m pytest tests/stable_ac/test_rank3_bf.py tests/stable_ac/test_rankn_class_view.py -q -p no:cacheprovider 2>&1 | tail -15
say "tests exit=${PIPESTATUS[0]}"

COV=results/stable_ac/cov_all/cov_all_suballpxyb8_ms640_b100000.jsonl.gz
CTRL=results/stable_ac/cov_all/cov_all_suballpxyb8_ms640_b10000.jsonl.gz

step(){ # step <name> <command...>: run, log the exit code, never stop the pass
  local name=$1; shift
  echo "$(date -u +%FT%TZ) -- $name"
  "$@" > /opt/r3/step.out 2>&1
  local rc=$?
  tail -c 6000 /opt/r3/step.out
  cp /opt/r3/step.out "$RD/post_${name}.txt"
  say "$name exit=$rc"
}

pass(){
  local tag=$1
  say "pass $tag start"
  rm -rf $RD && mkdir -p $RD
  for src in b1000 b10000 rankn; do
    aws s3 sync $B/$src/results/ $RD/ --exclude 'shards/*' --exclude '*.tmp*' --exclude '*.log' --only-show-errors
  done
  say "files: $(ls $RD | grep -c .) ($(ls $RD | grep -E '_L[0-9]+\.npz$|_r[45]\.npz$' | tr '\n' ' '))"
  for bud in 1000 10000; do
    [ -f $RD/rank3_bf_ms640_b${bud}_cap24_L1.npz ] || continue
    step plot_b$bud $PY -m $MOD.plot_rankn_vs_control --rank3 $RD --budget $bud
    step plot_b${bud}_L1-4 $PY -m $MOD.plot_rankn_vs_control --rank3 $RD --budget $bud --lengths 1-4
    step summarize_b$bud $PY -m $MOD.summarize_rank3_bf --dir $RD --budget $bud --cov $COV
    step classes_b$bud $PY -m $MOD.class_view --rank3 $RD --budget $bud
  done
  for r in 4 5; do
    [ -f $RD/rankn_bf_ms640_b1000_cap24_r$r.npz ] || continue
    step plot_r$r $PY -m $MOD.plot_rankn_vs_control --rankn $RD/rankn_bf_ms640_b1000_cap24_r$r.npz
    step classes_r$r $PY -m $MOD.class_view --rankn $RD/rankn_bf_ms640_b1000_cap24_r$r.npz
  done
  up(){ aws s3 sync $RD/ $B/post/$tag/ --exclude '*' --include '*.md' --include '*.png' --include '*.csv' \
    --include '*_summary.json' --include '*_class_view.json' --include 'indep_*.json' --include 'post_*.txt' --include 'checks_reference.json' --only-show-errors; }
  up
  step verify $PY -m $MOD.verify_rank3_bf --dir $RD --recheck 30 --cov-control $CTRL
  up
  # independent checks: written blind, no repo imports (-I drops PYTHONPATH)
  say "indep: $(ls $IND/indep_*.py 2>/dev/null | tr '\n' ' ')"
  for s in $(ls $IND/indep_*.py 2>/dev/null | grep -v _search) $IND/indep_search.py; do
    [ -f "$s" ] || continue
    n=$(basename $s .py)
    step $n timeout -k 60 $((INDEP_MIN * 60 + 900)) $PY -I -u $s $RD data/ms640_solved.txt $RD/$n.json $(getconf _NPROCESSORS_ONLN) $INDEP_MIN
    up
  done
  aws s3 ls $B/post/$tag/
  say "pass $tag done"
}

pass preview

if [ "$WAIT_UNTIL" -gt 0 ]; then
  say "waiting for both sweep boxes (until $(date -u -d @$WAIT_UNTIL +%FT%TZ))"
  ended(){ aws s3 cp $B/$1/run.log - 2>/dev/null | grep -qE '== DONE verify=|== FAIL'; }
  while [ "$(date +%s)" -lt "$WAIT_UNTIL" ]; do
    ended b1000 && ended b10000 && break
    sleep 300
  done
  sleep 180      # let the other boxes' last sync land
  pass final
fi
say "DONE"
shutdown -h now
