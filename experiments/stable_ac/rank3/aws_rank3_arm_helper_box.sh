#!/bin/bash
# EC2 user-data: the whole rank-3 baseline again, every search with its cap
# counters (run_rank3_bf.CAP_DOC). Same searches as the stored cap-24 results,
# so every array is also compared with the committed one.
#
# A. pool (control, relator subwords, short words): budget 1,000 (lengths 1..6)
#    and budget 10,000 (lengths 1..4). Then, before anything long: verifier,
#    "same as the stored run", and the counters against the earlier runs at
#    caps 32 and 48, which are only read: a search with no bind at cap 24 must
#    be identical there (cap_compare). No search is run at another cap.
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
DEADMAN=1020
BRANCH=rank3/brute-force-baseline
SHA=64b41ff72e1bfd165fd42199dfd7b3cd01d4c791
REV=faa88318702383fb37144d82dcb8af60fa92fec7   # the same code + run_rank3_bf --reverse --no-merge
BUCKET=acsolver-u124-205558941715
export HOME=/root AWS_DEFAULT_REGION=us-east-1
mkdir -p /opt/r3
exec >> /opt/r3/run.log 2>&1
shutdown -h +$DEADMAN
B=s3://$BUCKET/$ROOT
MOD=experiments.stable_ac.rank3
OUT=/opt/r3/out
RUNS="b1000_cap24"
SH=shards/rank3_bf_ms640_b1000_cap24
T=$(curl -s -X PUT http://169.254.169.254/latest/api/token -H 'X-aws-ec2-metadata-token-ttl-seconds: 600')
md(){ curl -s -H "X-aws-ec2-metadata-token: $T" http://169.254.169.254/latest/meta-data/$1; }
putlog(){ aws s3 cp /opt/r3/run.log $B/$P/run_arm2.log --only-show-errors; }
say(){ echo "$(date -u +%FT%TZ) == $*"; putlog; }
push(){ # this box writes shards and its own log, nothing else
  [ -d /opt/r3/b1000_cap24/$SH ] && aws s3 sync /opt/r3/b1000_cap24/$SH/ $B/$P/b1000_cap24/results/$SH/ \
    --exclude '*.tmp*' --exclude '*.npz.*' --only-show-errors
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
git worktree add -q --detach /opt/r3/rev $REV || fail "worktree $REV"
( cd /opt/r3/rev && $PY -m pytest tests/stable_ac/test_rank3_bf.py -q -p no:cacheprovider 2>&1 | tail -3
  exit ${PIPESTATUS[0]} ) || fail "pytest at $REV"
say "tests passed at $(git -C /opt/r3/rev rev-parse --short HEAD) (--reverse --no-merge)"

OLD=results/stable_ac/rank3_bf       # the committed cap-24 results, no counters
CTRL=results/stable_ac/cov_all/cov_all_suballpxyb8_ms640_b10000.jsonl.gz
D1=/opt/r3/b1000_cap24
D10=/opt/r3/b10000_cap24
DN=/opt/r3/rankn
mkdir -p $OUT $DN
for r in $RUNS; do
  mkdir -p /opt/r3/$r
  aws s3 sync $B/$P/$r/results/ /opt/r3/$r/ --only-show-errors
  say "$r: restored $(find /opt/r3/$r -type f | wc -l) files from S3"
done
heal(){ # heal <dir>: a merged length whose companion files are missing (a box
  # killed during an upload) is merged again from its shards by the next run3
  local f b x
  for f in $1/*_L*.npz; do
    [ -f $f ] || continue
    case $f in *_capcount.npz) continue;; esac
    b=${f%.npz}
    for x in _capcount.npz _sample.jsonl _sample_paths.jsonl; do
      [ -s $b$x ] || { say "incomplete merge, merging again: $f (no $x)"; rm -f $f; break; }
    done
  done
}
[ -f $D1/rank3_bf_ms640_b1000_cap24_L8.npz ] || fail "b1000 restore incomplete"
heal $D1
bg_sync(){ ( while true; do sleep 120; push
  OOM=$(dmesg 2>/dev/null | grep -c -i -E 'out of memory|oom-kill')
  echo "$(date -u +%FT%TZ) mem $(free -g | awk '/Mem:/{print "used="$3"G avail="$7"G"}') py=$(pgrep -fc 'run_rank3_bf|rankn_') oom=$OOM"
  # a killed pool worker loses its task and the pool then waits forever
  if [ "$OOM" -gt 0 ]; then fail "oom-kill seen, pool would hang"; fi
done ) &
  SYNC=$!
}
bg_sync

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

# ---- A. preflight on this machine ----
say "preflight start"
$PY -m $MOD.run_rank3_bf --budget 1000 --workers $N --max-len 3 --inv-max-len 2 \
  --pres 0,320 --out-dir /opt/r3/pre || fail preflight-run
$PY -m $MOD.verify_rank3_bf --dir /opt/r3/pre --recheck 10 --cov-control $CTRL || fail preflight-verify
$PY -m $MOD.rankn_bf /opt/r3/pre_rankn $N 0,320 || fail preflight-rankn
say "preflight verified"

# ---- B, on the helper box ----
# The main ARM box (log run_arm.log) runs budget 1,000 lengths 9 and 10 from the
# slow end and merges them. This box runs the same lengths from the fast end
# and writes shards only (--reverse --no-merge). Each box copies the other's
# finished shards from S3 and skips those tasks when it picks them, so the two
# meet once per length. If this box dies nothing is lost but its running tasks.
mkdir -p $D1/$SH/L9 $D1/$SH/L10
( while true; do
    for n in 9 10; do
      aws s3 sync $B/$P/b1000_cap24/results/$SH/L$n/ $D1/$SH/L$n/ --only-show-errors
    done
    sleep 45
  done ) &
PULL=$!
say "helper start: lengths 9 and 10 from the fast end, shards only"
( cd /opt/r3/rev && $PY -m $MOD.run_rank3_bf --budget 1000 --cap 24 --workers $N \
    --min-len 9 --max-len 10 --no-sub --reverse --no-merge --out-dir $D1 ) || fail "helper run"
kill $PULL $SYNC; wait $PULL 2>/dev/null; pkill -f "results/$SH/"
push
say "HELPER DONE"
shutdown -h now
