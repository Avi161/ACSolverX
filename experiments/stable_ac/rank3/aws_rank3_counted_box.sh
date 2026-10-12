#!/bin/bash
# EC2 user-data: the whole rank-3 baseline again, every search with its cap
# counters (run_rank3_bf.CAP_DOC). Same searches as the stored cap-24 results,
# so every array is also compared with the committed one.
#
# A. pool (control, relator subwords, short words): budget 1,000 at cap 20 and
#    cap 24 (lengths 1..6), budget 10,000 at cap 24 (lengths 1..4). Then, before
#    anything long: verifier, "same as the stored run" at the same cap, and the
#    test of the counters themselves: a search with no bind at the smaller cap
#    must be identical at every larger cap that was run (cap_compare).
# B. the rest: budget 1,000 lengths 7, 8 and inverse words 1..6; budget 10,000
#    lengths 5..7; ranks 4 and 5; budget 1,000 lengths 9, 10.
# C. verifier, comparison with the stored results, counter tables, reference
#    re-runs.
#
# Everything is written under s3://$BUCKET/$ROOT/$P/ and resumes from there.
# Launch with --instance-initiated-shutdown-behavior terminate.
ROOT=cov_all/rank3_bf
P=cap/counted
WORKERS=""               # empty = every online core
DEADMAN=780
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
RUNS="b1000_cap20 b1000_cap24 b10000_cap24 rankn"
T=$(curl -s -X PUT http://169.254.169.254/latest/api/token -H 'X-aws-ec2-metadata-token-ttl-seconds: 600')
md(){ curl -s -H "X-aws-ec2-metadata-token: $T" http://169.254.169.254/latest/meta-data/$1; }
putlog(){ aws s3 cp /opt/r3/run.log $B/$P/run.log --only-show-errors; }
say(){ echo "$(date -u +%FT%TZ) == $*"; putlog; }
push(){
  for r in $RUNS; do
    [ -d /opt/r3/$r ] && aws s3 sync /opt/r3/$r/ $B/$P/$r/results/ --exclude '*.tmp*' --only-show-errors
  done
  aws s3 sync $OUT/ $B/$P/final/ --only-show-errors
  putlog
}
fail(){ say "FAIL: $*"; push; shutdown -h now; exit 1; }

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
say "env $($PY -c 'import sys,numpy,numba;print(sys.version.split()[0],numpy.__version__,numba.__version__)') commit=$(git rev-parse --short HEAD) workers=$N"

$PY -m pytest tests/stable_ac/test_rank3_bf.py -q -p no:cacheprovider 2>&1 | tail -3
[ "${PIPESTATUS[0]}" -eq 0 ] || fail pytest
say "tests passed"

OLD=results/stable_ac/rank3_bf       # the committed cap-24 results, no counters
CTRL=results/stable_ac/cov_all/cov_all_suballpxyb8_ms640_b10000.jsonl.gz
D20=/opt/r3/b1000_cap20
D1=/opt/r3/b1000_cap24
D10=/opt/r3/b10000_cap24
DN=/opt/r3/rankn
mkdir -p $OUT $DN
for r in $RUNS; do
  mkdir -p /opt/r3/$r
  aws s3 sync $B/$P/$r/results/ /opt/r3/$r/ --only-show-errors
  say "$r: restored $(find /opt/r3/$r -type f | wc -l) files from S3"
done
( while true; do sleep 120; push
  OOM=$(dmesg 2>/dev/null | grep -c -i -E 'out of memory|oom-kill')
  echo "$(date -u +%FT%TZ) mem $(free -g | awk '/Mem:/{print "used="$3"G avail="$7"G"}') py=$(pgrep -fc 'run_rank3_bf|rankn_') oom=$OOM"
  # a killed pool worker loses its task and the pool then waits forever
  if [ "$OOM" -gt 0 ]; then fail "oom-kill seen, pool would hang"; fi
done ) &
SYNC=$!

step(){ # step <name> <command...>: run, keep the output, log the exit code
  local name=$1; shift
  "$@" > $OUT/log_${name}.txt 2>&1
  local rc=$?
  tail -c 3000 $OUT/log_${name}.txt
  say "$name exit=$rc"
  return $rc
}
run3(){ # run3 <budget> <cap> <dir> <max_len> <inv_max_len>
  say "run b$1 cap$2 lengths<=$4 inverse<=$5 start"
  $PY -m $MOD.run_rank3_bf --budget $1 --cap $2 --workers $N --max-len $4 \
    --inv-max-len $5 --out-dir $3 || fail "run b$1 cap$2 lengths<=$4"
  push
}
same_arrays(){ # same_arrays <old_dir> <new_dir> <glob> <all|some>
  $PY - "$@" <<'EOF'
import glob, os, sys
import numpy as np
old, new, pattern, mode = sys.argv[1:5]
bad = n = 0
for po in sorted(glob.glob(os.path.join(old, pattern))):
    name = os.path.basename(po)
    pn = os.path.join(new, name)
    if not os.path.exists(pn):
        if mode == "all":
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
old_cap(){ # old_cap <s3 prefix under cap/> <local name>: an earlier run without counters
  mkdir -p /opt/r3/old/$2
  aws s3 sync $B/cap/$1/results/ /opt/r3/old/$2/ --exclude 'shards/*' --exclude '*.tmp*' \
    --exclude '*.log' --only-show-errors
  ls /opt/r3/old/$2/*_relsub.jsonl > /dev/null 2>&1 && echo "--other /opt/r3/old/$2"
}
tables(){ # tables <name> <dir>: exhaustion and counter tables of one run
  step exhaustion_$1 $PY -m $MOD.cap_exhaustion --dir $2 --out $OUT/cap_counters_$1.json
}

# ---- A. the pool, and the checks that gate the long part ----
say "preflight start"
$PY -m $MOD.run_rank3_bf --budget 1000 --workers $N --max-len 3 --inv-max-len 2 \
  --pres 0,320 --out-dir /opt/r3/pre || fail preflight-run
$PY -m $MOD.verify_rank3_bf --dir /opt/r3/pre --recheck 10 --cov-control $CTRL || fail preflight-verify
$PY -m $MOD.rankn_bf /opt/r3/pre_rankn $N 0,320 || fail preflight-rankn
say "preflight verified"

run3 1000 20 $D20 6 0
run3 1000 24 $D1 6 0
run3 10000 24 $D10 4 0
step verify_pool_b1000_cap20 $PY -m $MOD.verify_rank3_bf --dir $D20 --recheck 5 || fail "verify pool cap 20"
step verify_pool_b1000_cap24 $PY -m $MOD.verify_rank3_bf --dir $D1 --recheck 5 --cov-control $CTRL || fail "verify pool b1000"
step verify_pool_b10000_cap24 $PY -m $MOD.verify_rank3_bf --dir $D10 --recheck 5 --cov-control $CTRL || fail "verify pool b10000"
ls -l $D20/*_capcount.npz $D1/*_capcount.npz $D10/*_capcount.npz $D1/*_L[0-9].npz
for d in $D20 $D1 $D10; do grep -h merged $d/*.log; done

# the same searches as the stored runs
step same_pool_b1000 $PY -m $MOD.cap_compare --must-match --base $D1 --other $OLD --budget 1000 \
  --out $OUT/same_pool_b1000.json || fail "pool b1000 differs from the stored run"
step same_pool_b10000 $PY -m $MOD.cap_compare --must-match --base $D10 --other $OLD --budget 10000 \
  --out $OUT/same_pool_b10000.json || fail "pool b10000 differs from the stored run"
O20=$(old_cap b1000_cap20 b1000_cap20)
O32=$(old_cap cap32 b1000_cap32)
O48=$(old_cap cap48 b1000_cap48)
T32=$(old_cap b10000_cap32 b10000_cap32)
T48=$(old_cap b10000_cap48 b10000_cap48)
say "earlier runs found: $O20 $O32 $O48 $T32 $T48"
if [ -n "$O20" ]; then
  step same_pool_b1000_cap20 $PY -m $MOD.cap_compare --must-match --base $D20 $O20 --budget 1000 \
    --out $OUT/same_pool_b1000_cap20.json || fail "pool cap 20 differs from the earlier run"
fi
# no bind at the smaller cap => identical at the larger cap
step bind_b1000_cap20 $PY -m $MOD.cap_compare --base $D20 --other $D1 $O32 $O48 --budget 1000 \
  --out $OUT/cap_bind_b1000_cap20.json || fail "cap 20: a search with no bind differs at a larger cap"
if [ -n "$O32$O48" ]; then
  step bind_b1000_cap24 $PY -m $MOD.cap_compare --base $D1 $O32 $O48 --budget 1000 \
    --out $OUT/cap_bind_b1000_cap24.json || fail "cap 24: a search with no bind differs at a larger cap"
fi
if [ -n "$T32$T48" ]; then
  step bind_b10000_cap24 $PY -m $MOD.cap_compare --base $D10 $T32 $T48 --budget 10000 \
    --out $OUT/cap_bind_b10000_cap24.json || fail "cap 24, b10000: a search with no bind differs at a larger cap"
fi
tables pool_b1000_cap20 $D20
tables pool_b1000_cap24 $D1
tables pool_b10000_cap24 $D10
push
say "POOL DONE"

# ---- B. the rest ----
run3 1000 24 $D1 8 6
run3 10000 24 $D10 7 0
say "rank 4/5 start"
$PY -m $MOD.rankn_bf $DN $N
say "rank 4/5 exit=$?"
push
run3 1000 24 $D1 10 6

# ---- C. checks on the complete runs ----
kill $SYNC
push
step verify_b1000 $PY -m $MOD.verify_rank3_bf --dir $D1 --recheck 20 --cov-control $CTRL
V1=$?
step verify_b10000 $PY -m $MOD.verify_rank3_bf --dir $D10 --recheck 20 --cov-control $CTRL
V10=$?
step same_b1000 $PY -m $MOD.cap_compare --must-match --base $D1 --other $OLD --budget 1000 --out $OUT/same_b1000.json
S1=$?
step same_b10000 $PY -m $MOD.cap_compare --must-match --base $D10 --other $OLD --budget 10000 --out $OUT/same_b10000.json
S10=$?
step same_arrays_b1000 same_arrays $OLD $D1 'rank3_bf_ms640_b1000_cap24_L*.npz' all
A1=$?
step same_arrays_b10000 same_arrays $OLD $D10 'rank3_bf_ms640_b10000_cap24_L*.npz' all
A10=$?
step same_arrays_rankn same_arrays $OLD $DN 'rankn_bf_*.npz' all
AN=$?
if [ -n "$O32$O48" ]; then
  step bind_b1000_cap24 $PY -m $MOD.cap_compare --base $D1 $O32 $O48 --budget 1000 --out $OUT/cap_bind_b1000_cap24.json
fi
if [ -n "$T32$T48" ]; then
  step bind_b10000_cap24 $PY -m $MOD.cap_compare --base $D10 $T32 $T48 --budget 10000 --out $OUT/cap_bind_b10000_cap24.json
fi
tables b1000_cap24 $D1
tables b10000_cap24 $D10
tables rankn $DN
cp $DN/*_summary.json $OUT/ 2>/dev/null
push
step reference $PY -m $MOD.rankn_checks $D1 $DN $OUT/checks_reference.json $N 20
RC=$?
push
aws s3 ls --recursive $B/$P/ | grep -v shards/ | awk '{print $3, $4}'
say "DONE verify=$V1,$V10 same=$S1,$S10 arrays=$A1,$A10,$AN reference=$RC"
shutdown -h now
