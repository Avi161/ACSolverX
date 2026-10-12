#!/bin/bash
# EC2 user-data: run tests/stable_ac at one commit and shut down (= terminate).
# The files of FIRST run side by side, the rest of the directory as one more
# job. Log: s3://$BUCKET/$ROOT/tests/<sha>.log, ends with "== DONE fails=<n>".
# Launch with --instance-initiated-shutdown-behavior terminate.
FIRST="test_solvern_fast test_solvern test_rank3_bf test_rankn_class_view test_run_nocov"
ROOT=cov_all/rank3_bf
DEADMAN=90
BRANCH=rank3/brute-force-baseline
SHA=SET_ME
BUCKET=acsolver-u124-205558941715
export HOME=/root AWS_DEFAULT_REGION=us-east-1
mkdir -p /opt/r3
exec >> /opt/r3/run.log 2>&1
shutdown -h +$DEADMAN
LOG=s3://$BUCKET/$ROOT/tests/${SHA:0:7}.log
putlog(){ aws s3 cp /opt/r3/run.log $LOG --only-show-errors; }
say(){ echo "$(date -u +%FT%TZ) == $*"; putlog; }
fail(){ say "FAIL: $*"; shutdown -h now; exit 1; }

echo "$(date -u +%FT%TZ) == boot cores=$(getconf _NPROCESSORS_ONLN)"
if ! putlog; then echo "R3: S3 WRITE FAILED, shutting down" > /dev/console; shutdown -h now; exit 1; fi
dnf install -y -q python3.12 python3.12-pip git || fail dnf
git config --system --add safe.directory '*'
cd /opt/r3
git clone -q --branch $BRANCH --single-branch https://github.com/Avi161/ACSolverX.git acsx || fail clone
cd acsx
git checkout -q $SHA || fail checkout
python3.12 -m venv /opt/r3/venv || fail venv
/opt/r3/venv/bin/pip -q install numpy==2.1.3 numba==0.63.1 pytest matplotlib pyyaml \
  || /opt/r3/venv/bin/pip -q install numpy numba pytest matplotlib pyyaml || fail pip
PY=/opt/r3/venv/bin/python3
export PYTHONPATH=. NUMBA_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 MPLBACKEND=Agg
say "env commit=$(git rev-parse --short HEAD)"
# compile once, so the jobs below do not all write the numba cache at once
$PY -c "
from experiments.stable_ac.solvern import Pres, search_n
from experiments.stable_ac.solvern_fast import search_n_fast
p = Pres(3, ((1, 2), (1, -2), (-3, 1)))
print(search_n(p, 10, cap=24) == search_n_fast(p, 10, cap=24))" || fail warmup

REST=$(ls tests/stable_ac/test_*.py | grep -v -E "/($(echo $FIRST | tr ' ' '|'))\.py$" | tr '\n' ' ')
job(){ # job <name> <files...>
  local name=$1; shift
  $PY -m pytest "$@" -q -p no:cacheprovider --basetemp=/opt/r3/tmp_$name > /opt/r3/t_$name.log 2>&1
  echo $? > /opt/r3/t_$name.rc
}
for t in $FIRST; do job $t tests/stable_ac/$t.py & done
job rest $REST &
( while true; do sleep 60; putlog; done ) &
BEAT=$!
wait $(jobs -p | grep -v -x $BEAT)
kill $BEAT
FAILS=0
for t in $FIRST rest; do
  rc=$(cat /opt/r3/t_$t.rc)
  [ "$rc" -eq 0 ] || FAILS=$((FAILS + 1))
  echo "---- $t exit=$rc"
  if [ "$rc" -eq 0 ]; then tail -3 /opt/r3/t_$t.log; else tail -c 12000 /opt/r3/t_$t.log; fi
done
say "DONE fails=$FAILS"
shutdown -h now
