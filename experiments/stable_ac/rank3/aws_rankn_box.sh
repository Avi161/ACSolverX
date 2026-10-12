#!/bin/bash
# EC2 user-data: rank-4/5 brute-force arms + reference-solver re-checks, then shut down.
PREFIX=cov_all/rank3_bf/rankn
DEADMAN=420
BRANCH=rank3/brute-force-baseline
SHA=8b3a51d
BUCKET=acsolver-u124-205558941715
export HOME=/root AWS_DEFAULT_REGION=us-east-1
mkdir -p /opt/r3
exec >> /opt/r3/run.log 2>&1
shutdown -h +$DEADMAN
B=s3://$BUCKET/$PREFIX
OUT=/opt/r3/out
T=$(curl -s -X PUT http://169.254.169.254/latest/api/token -H 'X-aws-ec2-metadata-token-ttl-seconds: 600')
md(){ curl -s -H "X-aws-ec2-metadata-token: $T" http://169.254.169.254/latest/meta-data/$1; }
putlog(){ aws s3 cp /opt/r3/run.log $B/run.log --only-show-errors; }
say(){ echo "$(date -u +%FT%TZ) == $*"; putlog; }
push(){ aws s3 sync $OUT/ $B/results/ --exclude '*.tmp*' --only-show-errors; putlog; }
fail(){ say "FAIL: $*"; [ -d $OUT ] && push; shutdown -h now; exit 1; }

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
N=$(getconf _NPROCESSORS_ONLN)
aws s3 cp $B/code/rankn_bf.py /opt/r3/rankn_bf.py --only-show-errors || fail code
aws s3 cp $B/code/rankn_checks.py /opt/r3/rankn_checks.py --only-show-errors || fail code
say "env $($PY -c 'import sys,numpy,numba;print(sys.version.split()[0],numpy.__version__,numba.__version__)') commit=$(git rev-parse --short HEAD) workers=$N code=$(sha256sum /opt/r3/rankn_bf.py /opt/r3/rankn_checks.py | cut -c1-12 | tr '\n' ' ')"

$PY -m pytest tests/stable_ac/test_rank3_bf.py -q -p no:cacheprovider 2>&1 | tail -3
[ "${PIPESTATUS[0]}" -eq 0 ] || fail pytest
say "tests passed"

say "preflight start"
$PY /opt/r3/rankn_bf.py /opt/r3/pre $N 0,320,639 || fail preflight-run
$PY /opt/r3/rankn_checks.py /opt/r3/none /opt/r3/pre /opt/r3/pre/checks.json $N 8
PC=$?
aws s3 sync /opt/r3/pre/ $B/preflight/ --exclude 'shards/*' --only-show-errors
[ "$PC" -eq 3 ] && fail "preflight: fast solver != reference solver"
say "preflight done (checks exit=$PC)"

mkdir -p $OUT
aws s3 sync $B/results/ $OUT/ --only-show-errors
say "restored $(find $OUT -type f | wc -l) files from S3"
( while true; do sleep 120; push
  echo "$(date -u +%FT%TZ) mem $(free -g | awk '/Mem:/{print "used="$3"G avail="$7"G"}') py=$(pgrep -fc rankn_)"
done ) &
SYNC=$!

say "rank 4/5 sweep start"
$PY /opt/r3/rankn_bf.py $OUT $N
RN=$?
say "sweep exit=$RN"
push

mkdir -p /opt/r3/r3npz
aws s3 sync s3://$BUCKET/cov_all/rank3_bf/b1000/results/ /opt/r3/r3npz/ --exclude '*' --include '*_cap24_L[1-7].npz' --only-show-errors
say "rank-3 files for the reference check: $(ls /opt/r3/r3npz | tr '\n' ' ')"
$PY /opt/r3/rankn_checks.py /opt/r3/r3npz $OUT $OUT/checks_reference.json $N 110
CK=$?
kill $SYNC
push
aws s3 ls --recursive $B/results/ | grep -v shards/
say "DONE sweep=$RN checks=$CK"
shutdown -h now
