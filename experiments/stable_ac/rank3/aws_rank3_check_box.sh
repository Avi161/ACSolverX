#!/bin/bash
# EC2 user-data: check the rank-3 results committed at one commit and shut down
# (= terminate). Side by side: tests/stable_ac; the verifier on
# results/stable_ac/rank3_bf; every search and every array against the results
# stored at OLD (the same run before the cap counters); the counter table.
# Log: s3://$BUCKET/$ROOT/checks/<sha>.log, ends with "== DONE fails=<n>";
# tables beside it under checks/<sha>/.
# Launch with --instance-initiated-shutdown-behavior terminate.
FIRST="test_solvern_fast test_solvern test_rank3_bf test_rankn_class_view test_run_nocov"
ROOT=cov_all/rank3_bf
DEADMAN=120
BRANCH=rank3/brute-force-baseline
SHA=SET_ME
OLD=64b41ff
RECHECK=10
BUCKET=acsolver-u124-205558941715
export HOME=/root AWS_DEFAULT_REGION=us-east-1
mkdir -p /opt/r3/out
exec >> /opt/r3/run.log 2>&1
shutdown -h +$DEADMAN
LOG=s3://$BUCKET/$ROOT/checks/${SHA:0:7}.log
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
say "env commit=$(git rev-parse --short HEAD) old=$OLD"
# compile once, so the jobs below do not all write the numba cache at once
$PY -c "
from experiments.stable_ac.solvern import Pres, search_n
from experiments.stable_ac.solvern_fast import search_n_fast
p = Pres(3, ((1, 2), (1, -2), (-3, 1)))
print(search_n(p, 10, cap=24) == search_n_fast(p, 10, cap=24))" || fail warmup

MOD=experiments.stable_ac.rank3
R=results/stable_ac/rank3_bf
CTRL=results/stable_ac/cov_all/cov_all_suballpxyb8_ms640_b10000.jsonl.gz
# copies: the verifier unpacks beside the files, and the tests scan results/
NEW=/opt/r3/new
cp -r $R $NEW || fail "copy results"
mkdir -p /opt/r3/old
git archive $OLD $R | tar -x -C /opt/r3/old || fail "results at $OLD"
O=/opt/r3/old/$R

same_arrays(){ # same_arrays <old_dir> <new_dir>: every array of every old npz
  $PY - "$@" <<'EOF'
import glob, os, sys
import numpy as np
old, new = sys.argv[1:3]
bad = n = 0
for po in sorted(glob.glob(os.path.join(old, "*.npz"))):
    name = os.path.basename(po)
    pn = os.path.join(new, name)
    if not os.path.exists(pn):
        print("MISSING", name)
        bad += 1
        continue
    with np.load(po) as a, np.load(pn) as b:
        for k in ("nodes", "path_len", "min_total", "base", "null", "pres_ids",
                  "words", "combos"):
            if k in a.files:
                n += 1
                if (k not in b.files or a[k].shape != b[k].shape
                        or not (a[k] == b[k]).all()):
                    print("DIFFERENT", name, k)
                    bad += 1
    print("compared", name)
print(f"{n} arrays compared with the stored run, {bad} problems")
sys.exit(1 if bad or not n else 0)
EOF
}
job(){ # job <name> <command...>
  local name=$1; shift
  "$@" > /opt/r3/out/log_$name.txt 2>&1
  echo $? > /opt/r3/t_$name.rc
}
tests(){ $PY -m pytest "$@" -q -p no:cacheprovider --basetemp=/opt/r3/tmp_$BASHPID; }
REST=$(ls tests/stable_ac/test_*.py | grep -v -E "/($(echo $FIRST | tr ' ' '|'))\.py$" | tr '\n' ' ')
JOBS="$FIRST rest verify same_b1000 same_b10000 arrays counters"
for t in $FIRST; do job $t tests tests/stable_ac/$t.py & done
job rest tests $REST &
job verify $PY -m $MOD.verify_rank3_bf --dir $NEW --recheck $RECHECK --cov-control $CTRL &
job same_b1000 $PY -m $MOD.cap_compare --must-match --base $NEW --other $O --budget 1000 \
  --out /opt/r3/out/same_b1000.json &
job same_b10000 $PY -m $MOD.cap_compare --must-match --base $NEW --other $O --budget 10000 \
  --out /opt/r3/out/same_b10000.json &
job arrays same_arrays $O $NEW &
job counters $PY -m $MOD.cap_exhaustion --dir $NEW --out /opt/r3/out/cap_counters_committed.json &
( while true; do sleep 60; putlog; done ) &
BEAT=$!
wait $(jobs -p | grep -v -x $BEAT)
kill $BEAT
FAILS=0
for t in $JOBS; do
  rc=$(cat /opt/r3/t_$t.rc)
  [ "$rc" -eq 0 ] || FAILS=$((FAILS + 1))
  echo "---- $t exit=$rc"
  if [ "$rc" -eq 0 ]; then tail -4 /opt/r3/out/log_$t.txt; else tail -c 12000 /opt/r3/out/log_$t.txt; fi
done
aws s3 sync /opt/r3/out/ s3://$BUCKET/$ROOT/checks/${SHA:0:7}/ --only-show-errors
say "DONE fails=$FAILS"
shutdown -h now
