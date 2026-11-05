#!/bin/bash
# User-data for the full-CoV CoV-gate run: the box runs the whole job by itself and powers off (terminating, since
# launch.sh sets instance-initiated-shutdown-behavior terminate) when it ends, so no SSM command or terminate call
# is needed from outside. Resumable: rows already in s3://$BUCKET/$RUN/out are skipped, so a relaunched box (after a
# spot reclaim) continues. Fill __BUCKET__, __RUN__, __HOURS__, __P1__ (workers at 1e5), __P2__ (workers at 1e6),
# __MEM__ (GB per 1e6 search), __ENGINE__ (python or numba) with sed. No secrets: the box uses its instance role.
BUCKET=__BUCKET__ RUN=__RUN__
shutdown -h +$((__HOURS__ * 60)) "max lifetime reached"
mkdir -p /opt/job/out && cd /opt/job
exec >> /opt/job/run.log 2>&1
echo "boot $(date -u +%FT%TZ) $(nproc) cores $(free -g | awk '/Mem/{print $2}') GB"
sync_out() { aws s3 sync /opt/job/out "s3://$BUCKET/$RUN/out" --only-show-errors; aws s3 cp /opt/job/run.log "s3://$BUCKET/$RUN/run.log" --only-show-errors; }
dnf install -y -q python3.11 python3.11-pip >/dev/null
python3.11 -m pip install -q numba==0.63.1 numpy==2.1.3 || { echo "pip failed, powering off"; sync_out; shutdown -h now; exit 1; }
# Without S3 the run can save nothing: power off at once rather than idle until the timer.
if ! { aws s3 cp "s3://$BUCKET/$RUN/code.tgz" . --only-show-errors && tar xzf code.tgz \
       && echo "$(date -u +%FT%TZ)" > out/BOOT && aws s3 cp out/BOOT "s3://$BUCKET/$RUN/out/BOOT" --only-show-errors; }; then
  echo "S3 unreachable, powering off"; shutdown -h now; exit 1
fi
aws s3 sync "s3://$BUCKET/$RUN/out" out --only-show-errors || true
rm -f out/EXIT
( while :; do sleep 60; sync_out; done ) &
( while :; do
    T=$(curl -s -X PUT http://169.254.169.254/latest/api/token -H 'X-aws-ec2-metadata-token-ttl-seconds: 60')
    if curl -sf -H "X-aws-ec2-metadata-token: $T" http://169.254.169.254/latest/meta-data/spot/instance-action >/dev/null; then
      echo "SPOT RECLAIM WARNING $(date -u +%FT%TZ)"; sync_out; exit
    fi; sleep 5; done ) &
export HOME=/root NUMBA_NUM_THREADS=1 OMP_NUM_THREADS=1 NUMBA_CACHE_DIR=/opt/job/nbcache PYTHONPATH=/opt/job
python3.11 benchmark/ryan/run_full.py --out out/p1e5 --budget 100000 --workers __P1__ --engine __ENGINE__ \
  && python3.11 benchmark/ryan/run_full.py --out out/p1e6 --budget 1000000 --only-unsolved-from out/p1e5 \
       --workers __P2__ --mem-gb __MEM__ --engine __ENGINE__
echo $? > out/EXIT
echo "done $(date -u +%FT%TZ) exit $(cat out/EXIT)"
sync_out
shutdown -h now "job finished"
