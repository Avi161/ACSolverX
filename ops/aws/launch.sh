#!/bin/bash
# usage: launch.sh <instance-type> <spot|ondemand> <max-hours> [root-gb]   (prints LAUNCHED <id> ...)
# Optional env: AMI (default: latest al2023 x86_64), NAME (Name tag), ZONES (availability zones to try, in order).
set -euo pipefail
source "$(dirname "$0")/env.sh"
TYPE=$1 MARKET=$2 HOURS=$3 ROOT_GB=${4:-60}
AMI=${AMI:-$(aws ssm get-parameter --name /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64 --query Parameter.Value --output text)}
ROOTDEV=$(aws ec2 describe-images --image-ids "$AMI" --query 'Images[0].RootDeviceName' --output text)
EXP=$(date -u -d "+$HOURS hours" +%FT%TZ)
W=$(mktemp -d)
echo "[{\"DeviceName\":\"$ROOTDEV\",\"Ebs\":{\"VolumeSize\":$ROOT_GB,\"VolumeType\":\"gp3\",\"DeleteOnTermination\":true}}]" > "$W/bdm.json"
cat > "$W/tags.json" <<J
[{"ResourceType":"instance","Tags":[{"Key":"project","Value":"$PROJECT"},{"Key":"owner","Value":"agent"},{"Key":"expires","Value":"$EXP"},{"Key":"Name","Value":"${NAME:-$PROJECT-ryan-cov-gates}"}]},
 {"ResourceType":"volume","Tags":[{"Key":"project","Value":"$PROJECT"},{"Key":"owner","Value":"agent"}]}]
J
printf '#!/bin/bash\nshutdown -h +%d "max lifetime reached"\n' $((HOURS * 60)) > "$W/ud.sh"
MKT=()
if [ "$MARKET" = spot ]; then
  echo '{"MarketType":"spot","SpotOptions":{"SpotInstanceType":"one-time","InstanceInterruptionBehavior":"terminate"}}' > "$W/mkt.json"
  MKT=(--instance-market-options "file://$W/mkt.json")
fi
SUBNETS=$(aws ec2 describe-subnets --filters Name=default-for-az,Values=true --query 'Subnets[].[AvailabilityZone,SubnetId]' --output text)
if [ -n "${ZONES:-}" ]; then
  SUBNETS=$(for Z in $ZONES; do awk -v z="$Z" '$1 == z' <<< "$SUBNETS"; done)
fi
for S in $(awk '{print $2}' <<< "$SUBNETS"); do
  if IID=$(aws ec2 run-instances --image-id "$AMI" --instance-type "$TYPE" --subnet-id "$S" \
      --security-group-ids "$BOX_SG" --iam-instance-profile Name="$BOX_PROFILE" \
      --instance-initiated-shutdown-behavior terminate --metadata-options HttpTokens=required,HttpEndpoint=enabled \
      --block-device-mappings "file://$W/bdm.json" --tag-specifications "file://$W/tags.json" \
      --user-data "file://$W/ud.sh" ${MKT[@]+"${MKT[@]}"} --query 'Instances[0].InstanceId' --output text 2>"$W/err"); then
    echo "LAUNCHED $IID $TYPE $MARKET $S expires=$EXP"; exit 0
  fi
  cat "$W/err" >&2
  grep -qE 'InsufficientInstanceCapacity|Unsupported|capacity|SpotMaxPriceTooLow' "$W/err" || exit 1
done
echo "NO CAPACITY for $TYPE ($MARKET)" >&2; exit 1
