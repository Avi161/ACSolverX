#!/bin/bash
# Runs on the box via ssm-run.sh. Fill BUCKET, RUN, ARGS (sed) before sending.
set -eu
BUCKET=__BUCKET__ RUN=__RUN__ ARGS="__ARGS__"
dnf install -y -q python3.11 python3.11-pip >/dev/null
python3.11 -m pip install -q numba==0.63.1 numpy==2.1.3
mkdir -p /opt/job && cd /opt/job
aws s3 cp "s3://$BUCKET/$RUN/code.tgz" . --only-show-errors && tar xzf code.tgz
mkdir -p out
cat > /opt/job/sync.sh <<S
#!/bin/bash
while :; do aws s3 sync /opt/job/out s3://$BUCKET/$RUN/out --only-show-errors
  aws s3 cp /opt/job/run.log s3://$BUCKET/$RUN/run.log --only-show-errors; sleep 60; done
S
cat > /opt/job/spotwatch.sh <<S
#!/bin/bash
while :; do
  T=\$(curl -s -X PUT http://169.254.169.254/latest/api/token -H 'X-aws-ec2-metadata-token-ttl-seconds: 60')
  if curl -sf -H "X-aws-ec2-metadata-token: \$T" http://169.254.169.254/latest/meta-data/spot/instance-action >/dev/null; then
    echo "SPOT RECLAIM WARNING" >> /opt/job/run.log
    aws s3 sync /opt/job/out s3://$BUCKET/$RUN/out --only-show-errors
    aws s3 cp /opt/job/run.log s3://$BUCKET/$RUN/run.log --only-show-errors; exit
  fi; sleep 5; done
S
systemd-run --unit=job-sync bash /opt/job/sync.sh
systemd-run --unit=job-spotwatch bash /opt/job/spotwatch.sh
systemd-run --unit=job --working-directory=/opt/job --setenv=HOME=/root --setenv=NUMBA_NUM_THREADS=1 \
  --setenv=NUMBA_CACHE_DIR=/opt/job/nbcache \
  bash -c "python3.11 benchmark/ryan/run_all.py --out out \$ARGS >> /opt/job/run.log 2>&1; echo \$? > /opt/job/out/EXIT"
echo started; nproc; free -g | head -2
