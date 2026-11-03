#!/bin/bash
# usage: ssm-run.sh <instance-id> <local-script> [timeout-s]   (short commands only; long jobs run detached)
set -euo pipefail
source "$(dirname "$0")/env.sh"
IID=$1 FILE=$2 TO=${3:-900}
B64=$(base64 < "$FILE" | tr -d '\n')
P=$(mktemp)
jq -n --arg c "echo $B64 | base64 -d > /root/ssm-job.sh && HOME=/root AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION bash /root/ssm-job.sh" \
  --arg t "$TO" '{commands:[$c],executionTimeout:[$t]}' > "$P"
CID=$(aws ssm send-command --instance-ids "$IID" --document-name AWS-RunShellScript --parameters "file://$P" --query Command.CommandId --output text)
while :; do
  ST=$(aws ssm get-command-invocation --command-id "$CID" --instance-id "$IID" --query Status --output text 2>/dev/null || echo Pending)
  case $ST in Success|Failed|Cancelled|TimedOut) break;; esac; sleep 3
done
aws ssm get-command-invocation --command-id "$CID" --instance-id "$IID" --query '[StandardOutputContent,StandardErrorContent]' --output text
echo "STATUS $ST" >&2; [ "$ST" = Success ]
