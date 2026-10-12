#!/bin/bash
# EC2 user-data for one autonomous run_cov_all box (this is what ran the budget
# 100,000 sweep). The box clones the branch at $SHA, runs the tests, a pre-flight
# on $PRE_IDS, the full sweep, the verifier and the summarizer, syncs $BASE* to
# s3://$BUCKET/$PREFIX/ every minute, and shuts down; launch it with
# --instance-initiated-shutdown-behavior terminate so shutdown ends the spend.
# Relaunching with the same PREFIX resumes from the rows already in S3.
#
#   aws ec2 run-instances --image-id <AL2023 x86_64 AMI> --instance-type r7i.24xlarge \
#     --iam-instance-profile Name=<profile with S3 write to $BUCKET> --subnet-id <subnet> \
#     --instance-initiated-shutdown-behavior terminate \
#     --instance-market-options 'MarketType=spot,SpotOptions={SpotInstanceType=one-time,InstanceInterruptionBehavior=terminate}' \
#     --user-data file://experiments/stable_ac/cov/run/aws_cov_all_box.sh \
#     --block-device-mappings 'DeviceName=/dev/xvda,Ebs={VolumeSize=30,VolumeType=gp3,DeleteOnTermination=true}'
#
# WORKERS is a memory decision, not a core count: at budget 100,000 the
# path-recording greedy peaked at about 5.8 GB per worker, and a pool worker the
# kernel kills hangs the run (192 workers in 384 GB did exactly that). The sync
# loop logs memory every minute and fails fast on an OOM kill.
# DEADMAN (minutes) shuts the box down whatever happens.
BUDGET=100000
PRE_IDS="444,452"        # two small presentations, 240 rows, for the pre-flight
FULL_PRES=""             # empty = all of data/ms640_solved.txt
PATH_SAMPLE=0.02
BATCH=20
WORKERS=96
PREFIX=cov_all/b100000
BASE=cov_all_suballpxyb8_ms640_b100000
EXPECT_PRE=240
EXPECT_FULL=114682
DEADMAN=240
SHA=f2ffd98
BUCKET=CHANGE_ME
# ---- CoV all-subsets sweep box: bootstrap, run, sync to S3, shut down (= terminate) ----
export HOME=/root AWS_DEFAULT_REGION=us-east-1
mkdir -p /opt/cov
exec >> /opt/cov/run.log 2>&1
shutdown -h +$DEADMAN
B=s3://$BUCKET/$PREFIX
RD=results/stable_ac/cov_all
MOD=experiments.stable_ac.cov
T=$(curl -s -X PUT http://169.254.169.254/latest/api/token -H 'X-aws-ec2-metadata-token-ttl-seconds: 600')
md(){ curl -s -H "X-aws-ec2-metadata-token: $T" http://169.254.169.254/latest/meta-data/$1; }
putlog(){ aws s3 cp /opt/cov/run.log $B/run.log --only-show-errors; }
say(){ echo "$(date -u +%FT%TZ) == $*"; putlog; }
push(){ aws s3 sync /opt/cov/acsx/$RD/ $B/results/ --exclude '*' --include "$BASE*" --only-show-errors; putlog; }
fail(){ say "FAIL: $*"; [ -d /opt/cov/acsx/$RD ] && push; shutdown -h now; exit 1; }

echo "$(date -u +%FT%TZ) == boot $(md instance-id) $(md instance-type) $(md placement/availability-zone) life=$(md instance-life-cycle) cores=$(getconf _NPROCESSORS_ONLN)"
if ! putlog; then echo "COV: S3 WRITE FAILED, shutting down" > /dev/console; shutdown -h now; exit 1; fi

dnf install -y -q python3.12 python3.12-pip git || fail dnf
git config --system --add safe.directory '*'
cd /opt/cov
git clone -q --branch cov/all-subsets-sweep --single-branch https://github.com/Avi161/ACSolverX.git acsx || fail clone
cd acsx
git checkout -q $SHA || fail checkout
python3.12 -m venv /opt/cov/venv || fail venv
/opt/cov/venv/bin/pip -q install numpy==2.1.3 numba==0.63.1 pytest \
  || /opt/cov/venv/bin/pip -q install numpy numba pytest || fail pip
PY=/opt/cov/venv/bin/python3
export PYTHONPATH=. NUMBA_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1
N=${WORKERS:-$(getconf _NPROCESSORS_ONLN)}
say "env $($PY -c 'import sys,numpy,numba;print(sys.version.split()[0],numpy.__version__,numba.__version__)') commit=$(git rev-parse --short HEAD) workers=$N budget=$BUDGET"

$PY -m pytest tests/stable_ac/test_cov_all.py -q -p no:cacheprovider 2>&1 | tail -3
[ "${PIPESTATUS[0]}" -eq 0 ] || fail pytest
say "tests passed"

mkdir -p $RD /opt/cov/pre
OUT=$RD/$BASE.jsonl
PRE=/opt/cov/pre/${BASE}_preflight.jsonl
aws s3 sync $B/results/ $RD/ --exclude '*' --include "$BASE.jsonl" --include "$BASE.log" --only-show-errors
say "restored $( [ -f $OUT ] && wc -l < $OUT || echo 0) rows from S3"
( while true; do sleep 60; push
  OOM=$(dmesg 2>/dev/null | grep -c -i -E 'out of memory|oom-kill')
  echo "$(date -u +%FT%TZ) mem $(free -g | awk '/Mem:/{print "used="$3"G avail="$7"G"}') py=$(pgrep -fc run_cov_all) oom=$OOM"
  # a killed pool worker loses its chunk and the pool then waits forever
  if [ "$OOM" -gt 0 ]; then fail "oom-kill seen, pool would hang"; fi
done ) &
SYNC=$!

say "preflight start"
$PY -m $MOD.run.run_cov_all --budget $BUDGET --workers $N --path-sample $PATH_SAMPLE ${BATCH:+--batch $BATCH} --pres "$PRE_IDS" --out $OUT || fail preflight-run
NPRE=$($PY -c "
import sys,json
keep=set(map(int,sys.argv[2].split(',')));n=0
with open(sys.argv[3],'w') as o:
    for ln in open(sys.argv[1]):
        if ln.strip() and json.loads(ln)['pres_id'] in keep:
            o.write(ln); n+=1
print(n)" $OUT "$PRE_IDS" $PRE)
say "preflight rows=$NPRE expect=${EXPECT_PRE:-any}"
[ -z "$EXPECT_PRE" ] || [ "$NPRE" -eq "$EXPECT_PRE" ] || fail "preflight row count"
$PY -m $MOD.verify.verify_cov_all $PRE --counts --path-sample $PATH_SAMPLE || fail preflight-verify
$PY -m $MOD.run.summarize_cov_all $PRE || fail preflight-summarize
aws s3 sync /opt/cov/pre/ $B/preflight/ --only-show-errors
say "preflight verified"

say "full start"
ARGS=""; DS="--dataset data/ms640_solved.txt"
if [ -n "$FULL_PRES" ]; then ARGS="--pres $FULL_PRES"; DS=""; fi
$PY -m $MOD.run.run_cov_all --budget $BUDGET --workers $N --path-sample $PATH_SAMPLE ${BATCH:+--batch $BATCH} $ARGS --out $OUT || fail full-run
ROWS=$(wc -l < $OUT)
say "full rows=$ROWS expect=${EXPECT_FULL:-any}"
push
[ -z "$EXPECT_FULL" ] || [ "$ROWS" -eq "$EXPECT_FULL" ] || fail "full row count"
$PY -m $MOD.verify.verify_cov_all $OUT --counts $DS --path-sample $PATH_SAMPLE
V=$?
say "verify exit=$V"
$PY -m $MOD.run.summarize_cov_all $OUT || say "summarize failed"
gzip -9 -k -f $OUT
kill $SYNC
push
aws s3 ls --recursive $B/
say "DONE verify=$V"
shutdown -h now
