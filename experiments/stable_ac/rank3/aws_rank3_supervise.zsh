#!/bin/zsh
# aws_rank3_supervise.zsh <dir with ud_armA.sh ud_armB.sh ud_armC.sh ud_armF.sh>
#
# Relaunches the boxes of the rank-3 counted rerun without anyone watching. Runs on the launching
# machine (it only polls and launches). The instance ids below are those of the run of 13 Oct 2026:
# put in the ids of the boxes you have just launched. ud_armA/B/C.sh come from
# aws_rank3_split_helpers.py, ud_armF.sh is aws_rank3_arm_main_box.sh.
# Lesson: experiments/lessons/relaunch-spot-boxes-automatically.md
export AWS_PROFILE=acsolver AWS_DEFAULT_REGION=us-east-1 AWS_PAGER=""
W=$1
B=s3://acsolver-u124-205558941715/cov_all/rank3_bf
typeset -A ID Z NREL FIN
ID=(A i-0143da6774f340b33 B i-0c032cd6441f7fc34 C i-052a556523db34d45)
# zones to try on a relaunch, in order (1c reclaimed three ARM spot boxes on 12 Oct, so it is left out)
Z=(A "subnet-0183b57981cfdf0a4 subnet-009f4c8badc8a5e28 subnet-0b499315f8992c89a subnet-0e24b1b3986561ff9"
   B "subnet-009f4c8badc8a5e28 subnet-0e24b1b3986561ff9 subnet-0b499315f8992c89a subnet-0183b57981cfdf0a4"
   C "subnet-0e24b1b3986561ff9 subnet-0183b57981cfdf0a4 subnet-0b499315f8992c89a subnet-009f4c8badc8a5e28")
NREL=(A 0 B 0 C 0)
FIN=(A 0 B 0 C 0)
now(){ date -u +%H:%M:%S; }
launch(){ # launch <group> <subnet>
  aws ec2 run-instances --image-id ami-0cded71ff6ab7f608 --instance-type c8g.16xlarge \
    --iam-instance-profile Name=acsolver-ec2 --subnet-id $2 --security-group-ids sg-0181416e25f45694b \
    --instance-initiated-shutdown-behavior terminate \
    --instance-market-options 'MarketType=spot,SpotOptions={SpotInstanceType=one-time,InstanceInterruptionBehavior=terminate}' \
    --user-data file://$W/ud_arm$1.sh \
    --block-device-mappings 'DeviceName=/dev/xvda,Ebs={VolumeSize=30,VolumeType=gp3,DeleteOnTermination=true}' \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=rank3-bf-counted-arm-helper-$1},{Key=Project,Value=cov-all-subsets}]" \
      'ResourceType=volume,Tags=[{Key=Project,Value=cov-all-subsets}]' \
      'ResourceType=spot-instances-request,Tags=[{Key=Project,Value=cov-all-subsets}]' \
    --query 'Instances[0].InstanceId' --output text 2>&1 | tail -1
}
MAIN=i-01387ad2eb2241564
MREL=0
launch_main(){ # launch_main <subnet>: on demand
  aws ec2 run-instances --image-id ami-0cded71ff6ab7f608 --instance-type c8g.24xlarge \
    --iam-instance-profile Name=acsolver-ec2 --subnet-id $1 --security-group-ids sg-0181416e25f45694b \
    --instance-initiated-shutdown-behavior terminate \
    --user-data file://$W/ud_armF.sh \
    --block-device-mappings 'DeviceName=/dev/xvda,Ebs={VolumeSize=30,VolumeType=gp3,DeleteOnTermination=true}' \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=rank3-bf-counted-arm},{Key=Project,Value=cov-all-subsets}]' \
      'ResourceType=volume,Tags=[{Key=Project,Value=cov-all-subsets}]' \
    --query 'Instances[0].InstanceId' --output text 2>&1 | tail -1
}
while true; do
  main=$(aws s3 cp $B/cap/counted/run_arm.log - 2>/dev/null)
  hit=$(echo "$main" | grep -E 'merged L10:|== DONE|FAIL|WARNING' | tail -1 | cut -c1-200)
  if [ -n "$hit" ]; then echo "$(now) MAIN: $hit"; exit 0; fi
  # the on-demand main box is not reclaimed by AWS; if it is gone without DONE or FAIL, start it again
  mst=$(aws ec2 describe-instances --instance-ids $MAIN --query 'Reservations[0].Instances[0].State.Name' --output text 2>/dev/null)
  case "$mst" in
    terminated|shutting-down)
      if [ "$MREL" -ge 2 ]; then echo "$(now) MAIN gone 3 times, giving up"; exit 1; fi
      aws s3 cp $B/cap/counted/run_arm.log $B/cap/counted/run_arm_until_$(date -u +%H%M).log --only-show-errors
      new=""
      for sn in subnet-0183b57981cfdf0a4 subnet-009f4c8badc8a5e28 subnet-0e24b1b3986561ff9 subnet-0b499315f8992c89a; do
        out=$(launch_main $sn)
        if [[ "$out" == i-* ]]; then new=$out; break; fi
      done
      if [ -z "$new" ]; then echo "$(now) MAIN gone, NO CAPACITY: $out"; exit 1; fi
      MREL=$((MREL+1)); echo "$(now) MAIN GONE $MAIN -> RELAUNCHED $new in $sn (relaunch $MREL)"; MAIN=$new
      ;;
  esac
  for g in A B C; do
    [ "$FIN[$g]" = 1 ] && continue
    log=$(aws s3 cp $B/cap/counted/run_arm$g.log - 2>/dev/null)
    if echo "$log" | grep -q 'HELPER DONE'; then FIN[$g]=1; echo "$(now) $g HELPER DONE"; continue; fi
    if echo "$log" | grep -q 'FAIL'; then echo "$(now) $g FAIL: $(echo "$log" | grep FAIL | tail -1 | cut -c1-200)"; exit 1; fi
    st=$(aws ec2 describe-instances --instance-ids $ID[$g] --query 'Reservations[0].Instances[0].[State.Name,StateReason.Code]' --output text 2>/dev/null)
    case "$st" in
      terminated*|shutting-down*)
        if [[ "$st" != *Server.SpotInstanceTermination* ]]; then echo "$(now) $g GONE $ID[$g]: $st"; exit 1; fi
        if [ "$NREL[$g]" -ge 3 ]; then echo "$(now) $g reclaimed 4 times, giving up"; exit 1; fi
        aws s3 cp $B/cap/counted/run_arm$g.log $B/cap/counted/run_arm${g}_until_$(date -u +%H%M).log --only-show-errors
        zones=(${=Z[$g]})
        new=""
        for sn in $zones; do
          out=$(launch $g $sn)
          if [[ "$out" == i-* ]]; then new=$out; break; fi
        done
        if [ -z "$new" ]; then echo "$(now) $g reclaimed, NO CAPACITY: $out"; exit 1; fi
        NREL[$g]=$((NREL[$g]+1))
        echo "$(now) $g RECLAIMED $ID[$g] -> RELAUNCHED $new in $sn (relaunch $NREL[$g])"
        ID[$g]=$new
        Z[$g]="$zones[2,-1] $zones[1]"
        ;;
    esac
  done
  if [ "$FIN[A]$FIN[B]$FIN[C]" = 111 ]; then echo "$(now) ALL HELPERS DONE"; exit 0; fi
  sleep 60
done
