#!/bin/bash
# User-data of the Elliot full-CoV box (no secrets). launch_spot.py fills __COMMIT__, __RUN__, __BUCKET__, __END__.
# A persistent spot request relaunches the box after a reclaim; a new box pulls the saved results from S3 and resumes
# (each stage skips the rows already written). The box powers off at __END__ (UTC), after the request has expired.
exec >> /var/log/job-boot.log 2>&1
set -u
COMMIT=__COMMIT__ RUN=__RUN__ BUCKET=__BUCKET__ END=__END__
MIN=$(( ($(date -u -d "$END" +%s) - $(date -u +%s)) / 60 ))
shutdown -h +$(( MIN > 1 ? MIN : 1 )) "end of run window"
dnf install -y -q python3.12 python3.12-pip git
python3.12 -m pip install -q numba==0.63.1 numpy==2.1.3
mkdir -p /opt/job/out && cd /opt/job
git clone -q https://github.com/Avi161/ACSolverX repo && git -C repo checkout -q "$COMMIT"
aws s3 sync "s3://$BUCKET/$RUN/out" out --only-show-errors
cat > sync.sh <<S
#!/bin/bash
while :; do aws s3 sync /opt/job/out s3://$BUCKET/$RUN/out --only-show-errors; sleep 60; done
S
cat > stages.sh <<'S'
#!/bin/bash
# budget workers mem-cap-GB: each stage searches only the rows the one before left unsolved
cd /opt/job/repo
PREV=""
while read -r B W M; do
  python3.12 -m benchmark.elliot.fullcov.run_fullcov --budget "$B" --out "/opt/job/out/b$B" --workers "$W" \
    --mem-gb "$M" ${PREV:+--from "$PREV"} >> "/opt/job/out/run_b$B.log" 2>&1 || exit 1
  PREV="/opt/job/out/b$B"
done <<E
1000 190 0
10000 190 0
100000 110 3
1000000 11 32
10000000 2 180
E
touch /opt/job/out/DONE
S
systemd-run --unit=job-sync bash /opt/job/sync.sh
systemd-run --unit=job --setenv=HOME=/root --setenv=NUMBA_NUM_THREADS=1 --setenv=OMP_NUM_THREADS=1 \
  --setenv=NUMBA_CACHE_DIR=/opt/job/nbcache bash /opt/job/stages.sh
echo "started $(date -u +%FT%TZ)"
