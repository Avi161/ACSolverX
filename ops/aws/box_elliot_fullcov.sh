#!/bin/bash
# User-data of the Elliot full-CoV box (no secrets). launch_spot.py fills __COMMIT__, __RUN__, __BUCKET__, __END__.
# It installs /opt/job/boot.sh as a service that runs on every boot: a spot reclaim stops the box, the persistent
# request starts it again, and the stages resume from the rows already written (also copied to S3 every minute).
mkdir -p /opt/job
cat > /opt/job/boot.sh <<'B'
#!/bin/bash
exec >> /var/log/job-boot.log 2>&1
set -u
COMMIT=__COMMIT__ RUN=__RUN__ BUCKET=__BUCKET__ END=__END__
echo "boot $(date -u +%FT%TZ)"
MIN=$(( ($(date -u -d "$END" +%s) - $(date -u +%s)) / 60 ))
shutdown -h +$(( MIN > 1 ? MIN : 1 )) "end of run window"
cd /opt/job
command -v python3.12 >/dev/null || dnf install -y -q python3.12 python3.12-pip git
python3.12 -c "import numba" 2>/dev/null || python3.12 -m pip install -q numba==0.63.1 numpy==2.1.3
[ -d repo ] || { git clone -q https://github.com/Avi161/ACSolverX repo && git -C repo checkout -q "$COMMIT"; }
mkdir -p out
[ -n "$(ls out)" ] || aws s3 sync "s3://$BUCKET/$RUN/out" out --only-show-errors
[ -f out/DONE ] && exit 0
( while :; do aws s3 sync /opt/job/out "s3://$BUCKET/$RUN/out" --only-show-errors; sleep 60; done ) &
cd repo
export HOME=/root NUMBA_NUM_THREADS=1 OMP_NUM_THREADS=1 NUMBA_CACHE_DIR=/opt/job/nbcache
PREV=""
# budget workers mem-cap-GB: each stage searches only the rows the stage before left unsolved
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
aws s3 sync /opt/job/out "s3://$BUCKET/$RUN/out" --only-show-errors
B
chmod +x /opt/job/boot.sh
cat > /etc/systemd/system/elliotjob.service <<'U'
[Unit]
After=network-online.target
Wants=network-online.target
[Service]
Type=simple
ExecStart=/opt/job/boot.sh
[Install]
WantedBy=multi-user.target
U
systemctl daemon-reload
systemctl enable --now elliotjob.service
