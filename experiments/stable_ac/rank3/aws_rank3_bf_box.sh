#!/bin/bash
# EC2 user-data for one autonomous run_rank3_bf box. The box clones $BRANCH at
# $SHA, runs the rank-3 tests, a pre-flight on $PRE_IDS (run + verify), the full
# sweep, the verifier, syncs the results directory to s3://$BUCKET/$PREFIX/
# every two minutes and shuts down; launch it with
# --instance-initiated-shutdown-behavior terminate so shutdown ends the spend.
# Relaunching with the same PREFIX resumes from the shards already in S3.
#
#   aws ec2 run-instances --image-id <AL2023 x86_64 AMI> --instance-type c7a.48xlarge \
#     --iam-instance-profile Name=<profile with S3 write to $BUCKET> --subnet-id <subnet> \
#     --instance-initiated-shutdown-behavior terminate \
#     --instance-market-options 'MarketType=spot,SpotOptions={SpotInstanceType=one-time,InstanceInterruptionBehavior=terminate}' \
#     --user-data file://experiments/stable_ac/rank3/aws_rank3_bf_box.sh \
#     --block-device-mappings 'DeviceName=/dev/xvda,Ebs={VolumeSize=30,VolumeType=gp3,DeleteOnTermination=true}'
#
# At budget 1,000 a search needs a few MB, so WORKERS can be every core. At
# 10,000 leave headroom: a pool worker the kernel kills hangs the run, and the
# sync loop fails fast on an OOM kill. DEADMAN (minutes) shuts the box down
# whatever happens.
BUDGET=1000
MAX_LEN=10
INV_MAX_LEN=6
WORKERS=""               # empty = every online core
EXTRA=""                 # extra run_rank3_bf arguments, e.g. "--pres 0,1,2 --no-sub"
PRE_IDS="0,320"
PRE_MAX_LEN=4
PREFIX=cov_all/rank3_bf/b1000
DEADMAN=720
BRANCH=rank3/brute-force-baseline
SHA=CHANGE_ME
BUCKET=CHANGE_ME
# ---- rank-3 brute-force box: bootstrap, run, sync to S3, shut down (= terminate) ----
export HOME=/root AWS_DEFAULT_REGION=us-east-1
mkdir -p /opt/r3
exec >> /opt/r3/run.log 2>&1
shutdown -h +$DEADMAN
B=s3://$BUCKET/$PREFIX
RD=results/stable_ac/rank3_bf
MOD=experiments.stable_ac.rank3
T=$(curl -s -X PUT http://169.254.169.254/latest/api/token -H 'X-aws-ec2-metadata-token-ttl-seconds: 600')
md(){ curl -s -H "X-aws-ec2-metadata-token: $T" http://169.254.169.254/latest/meta-data/$1; }
putlog(){ aws s3 cp /opt/r3/run.log $B/run.log --only-show-errors; }
say(){ echo "$(date -u +%FT%TZ) == $*"; putlog; }
push(){ aws s3 sync /opt/r3/acsx/$RD/ $B/results/ --exclude '*.tmp*' --only-show-errors; putlog; }
fail(){ say "FAIL: $*"; [ -d /opt/r3/acsx/$RD ] && push; shutdown -h now; exit 1; }

echo "$(date -u +%FT%TZ) == boot $(md instance-id) $(md instance-type) $(md placement/availability-zone) life=$(md instance-life-cycle) cores=$(getconf _NPROCESSORS_ONLN)"
if ! putlog; then echo "R3: S3 WRITE FAILED, shutting down" > /dev/console; shutdown -h now; exit 1; fi

dnf install -y -q python3.12 python3.12-pip git || fail dnf
git config --system --add safe.directory '*'
cd /opt/r3
git clone -q --branch $BRANCH --single-branch https://github.com/Avi161/ACSolverX.git acsx || fail clone
cd acsx
git checkout -q $SHA || fail checkout
python3.12 -m venv /opt/r3/venv || fail venv
/opt/r3/venv/bin/pip -q install numpy==2.1.3 numba==0.63.1 pytest \
  || /opt/r3/venv/bin/pip -q install numpy numba pytest || fail pip
PY=/opt/r3/venv/bin/python3
export PYTHONPATH=. NUMBA_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1
N=${WORKERS:-$(getconf _NPROCESSORS_ONLN)}
say "env $($PY -c 'import sys,numpy,numba;print(sys.version.split()[0],numpy.__version__,numba.__version__)') commit=$(git rev-parse --short HEAD) workers=$N budget=$BUDGET max_len=$MAX_LEN"

$PY -m pytest tests/stable_ac/test_rank3_bf.py -q -p no:cacheprovider 2>&1 | tail -3
[ "${PIPESTATUS[0]}" -eq 0 ] || fail pytest
say "tests passed"

CTRL=results/stable_ac/cov_all/cov_all_suballpxyb8_ms640_b10000.jsonl.gz
say "preflight start"
$PY -m $MOD.run_rank3_bf --budget $BUDGET --workers $N --max-len $PRE_MAX_LEN \
  --inv-max-len 2 --pres "$PRE_IDS" --out-dir /opt/r3/pre || fail preflight-run
$PY -m $MOD.verify_rank3_bf --dir /opt/r3/pre --recheck 10 --cov-control $CTRL || fail preflight-verify
aws s3 sync /opt/r3/pre/ $B/preflight/ --only-show-errors
say "preflight verified"

mkdir -p $RD
aws s3 sync $B/results/ $RD/ --only-show-errors
say "restored $(find $RD -type f | wc -l) files from S3"
( while true; do sleep 120; push
  OOM=$(dmesg 2>/dev/null | grep -c -i -E 'out of memory|oom-kill')
  echo "$(date -u +%FT%TZ) mem $(free -g | awk '/Mem:/{print "used="$3"G avail="$7"G"}') py=$(pgrep -fc run_rank3_bf) oom=$OOM"
  # a killed pool worker loses its task and the pool then waits forever
  if [ "$OOM" -gt 0 ]; then fail "oom-kill seen, pool would hang"; fi
done ) &
SYNC=$!

say "full start"
$PY -m $MOD.run_rank3_bf --budget $BUDGET --workers $N --max-len $MAX_LEN \
  --inv-max-len $INV_MAX_LEN $EXTRA || fail full-run
push
$PY -m $MOD.verify_rank3_bf --dir $RD --recheck 20 --cov-control $CTRL
V=$?
say "verify exit=$V"
kill $SYNC
push
aws s3 ls --recursive $B/results/ | grep -v shards/
say "DONE verify=$V"
shutdown -h now
