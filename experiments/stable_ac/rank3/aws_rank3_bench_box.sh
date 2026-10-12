#!/bin/bash
# EC2 user-data: per-core speed of the rank-3 search on this CPU, to choose a
# machine by nodes per second per dollar (experiments/lessons/
# pick-the-cpu-by-nodes-per-dollar.md). Runs 8 fixed tasks (3,888 searches,
# budget 1,000) on 2 cores and prints per-task seconds, total core-seconds and
# a sha256 of the result arrays: the digest must be the same on every CPU. On
# ARM it then runs tests/stable_ac. A .large instance is enough.
# Log: s3://$BUCKET/$ROOT/bench/<arch>.log, ends with "== DONE".
# Launch (x86 image or the arm64 one of the same AL2023 release):
#   sed "s/^SHA=SET_ME/SHA=$(git rev-parse HEAD)/" aws_rank3_bench_box.sh > ud.sh
#   aws ec2 run-instances --instance-type c8g.large --image-id <arm64 ami> \
#     --user-data file://ud.sh --instance-initiated-shutdown-behavior terminate ...
ROOT=cov_all/rank3_bf
BRANCH=rank3/brute-force-baseline
SHA=SET_ME
BUCKET=acsolver-u124-205558941715
export HOME=/root AWS_DEFAULT_REGION=us-east-1
mkdir -p /opt/r3
exec >> /opt/r3/run.log 2>&1
shutdown -h +60
ARCH=$(uname -m)
LOG=s3://$BUCKET/$ROOT/bench/$ARCH.log
T=$(curl -s -X PUT http://169.254.169.254/latest/api/token -H 'X-aws-ec2-metadata-token-ttl-seconds: 600')
md(){ curl -s -H "X-aws-ec2-metadata-token: $T" http://169.254.169.254/latest/meta-data/$1; }
putlog(){ aws s3 cp /opt/r3/run.log $LOG --only-show-errors; }
say(){ echo "$(date -u +%FT%TZ) == $*"; putlog; }
fail(){ say "FAIL: $*"; shutdown -h now; exit 1; }
echo "$(date -u +%FT%TZ) == boot $(md instance-id) $(md instance-type) $ARCH cores=$(getconf _NPROCESSORS_ONLN)"
if ! putlog; then shutdown -h now; exit 1; fi
dnf install -y -q python3.12 python3.12-pip git || fail dnf
git config --system --add safe.directory '*'
cd /opt/r3
git clone -q --branch $BRANCH --single-branch https://github.com/Avi161/ACSolverX.git acsx || fail clone
cd acsx
git checkout -q $SHA || fail checkout
python3.12 -m venv /opt/r3/venv || fail venv
/opt/r3/venv/bin/pip -q install numpy==2.1.3 numba==0.63.1 pytest matplotlib pyyaml || fail pip
PY=/opt/r3/venv/bin/python3
export PYTHONPATH=. NUMBA_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONUNBUFFERED=1 MPLBACKEND=Agg
say "env $($PY -c 'import sys,numpy,numba;print(sys.version.split()[0],numpy.__version__,numba.__version__)') commit=$(git rev-parse --short HEAD)"
$PY - <<'EOF' || fail bench
import hashlib, os, time
from multiprocessing import get_context
import numpy as np
from experiments.stable_ac.rank3 import run_rank3_bf as R
from experiments.stable_ac.rank3 import words as W
from experiments.stable_ac.solvern_fast import search_n_fast

rows = {p: (a, b) for p, a, b in R.load_ms640("data/ms640_solved.txt")}
ids = [0, 91, 182, 273, 364, 455, 546, 639]
n, budget, cap = 6, 1000, 24
out = "/opt/r3/bench"
os.makedirs(out, exist_ok=True)
r1, r2 = rows[0]
search_n_fast(R.rank3(r1, r2, W.words_of_length(1)[0]), 10, cap=cap, cyclic=True)
tasks = []
for p in ids:
    r1, r2 = rows[p]
    tasks.append((p, r1, r2, n, 0, "fwd", budget, cap, 0.0,
                  os.path.join(out, f"p{p:04d}.npz"),
                  R.shard_ident("ms640", budget, cap, n, "fwd", 0, p, r1, r2)))
t0 = time.time()
with get_context("fork").Pool(2) as pool:
    res = pool.map(R.block_task, tasks, chunksize=1)
wall = time.time() - t0
h = hashlib.sha256()
for (p, _, _, k, s, secs), t in zip(res, tasks):
    with np.load(t[9]) as z:
        for key in ("nodes", "path_len", "min_total", "cap_dropped",
                    "cap_dropped_min_total", "cap_first_bind"):
            h.update(np.ascontiguousarray(z[key]).tobytes())
    print(f"BENCH pres={p} searches={k} solved={s} secs={secs:.1f}")
print(f"BENCH total core-seconds={sum(r[5] for r in res):.1f} wall={wall:.1f} "
      f"digest={h.hexdigest()[:16]}")
EOF
say "bench done"
if [ "$ARCH" = aarch64 ]; then
  for t in test_solvern_fast test_solvern test_rank3_bf test_rankn_class_view test_run_nocov; do
    $PY -m pytest tests/stable_ac/$t.py -q -p no:cacheprovider --basetemp=/opt/r3/tmp_$t 2>&1 | tail -3
    say "$t exit=${PIPESTATUS[0]}"
  done
  REST=$(ls tests/stable_ac/test_*.py | grep -v -E "/(test_solvern_fast|test_solvern|test_rank3_bf|test_rankn_class_view|test_run_nocov)\.py$" | tr '\n' ' ')
  $PY -m pytest $REST -q -p no:cacheprovider --basetemp=/opt/r3/tmp_rest 2>&1 | tail -15
  say "rest exit=${PIPESTATUS[0]}"
fi
say "DONE"
shutdown -h now
