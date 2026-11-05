"""Launch one persistent spot box with a filled user-data template (boto3; no secrets anywhere).

    python ops/aws/launch_spot.py <type> <ami> <hours> <template> KEY=VALUE ...   (prints LAUNCHED <id> ...)

A reclaim stops the box (its disk is kept) and the persistent request starts it again when capacity returns, until
<hours> - 0.5 h from now; the template must resume on every boot. Its __END__ (now + <hours>) is when the box powers
off. Subnets are tried from the cheapest spot zone up. Cancel the request before terminating.
"""
import datetime as dt
import sys

import boto3

PROJECT, SG, PROFILE = "claude-agent", "sg-07363655368c9d2d2", "claude-box"


def main():
    itype, ami, hours, template, *pairs = sys.argv[1:]
    now = dt.datetime.now(dt.timezone.utc)
    end = now + dt.timedelta(hours=float(hours))
    fill = dict(p.split("=", 1) for p in pairs) | {"END": end.strftime("%Y-%m-%dT%H:%M:%SZ")}
    ud = open(template).read()
    for k, v in fill.items():
        ud = ud.replace(f"__{k}__", v)
    assert "__" not in ud.replace("__name__", ""), "unfilled placeholder"
    ec2 = boto3.client("ec2")
    prices = {p["AvailabilityZone"]: float(p["SpotPrice"]) for p in ec2.describe_spot_price_history(
        InstanceTypes=[itype], ProductDescriptions=["Linux/UNIX"], StartTime=now)["SpotPriceHistory"]}
    subnets = ec2.describe_subnets(Filters=[{"Name": "default-for-az", "Values": ["true"]}])["Subnets"]
    subnets.sort(key=lambda s: prices.get(s["AvailabilityZone"], 99))
    tags = [{"Key": "project", "Value": PROJECT}, {"Key": "owner", "Value": "agent"},
            {"Key": "expires", "Value": fill["END"]}, {"Key": "Name", "Value": f"{PROJECT}-{fill.get('RUN', 'job')}"}]
    for s in subnets:
        try:
            r = ec2.run_instances(
                ImageId=ami, InstanceType=itype, MinCount=1, MaxCount=1, SubnetId=s["SubnetId"],
                SecurityGroupIds=[SG], IamInstanceProfile={"Name": PROFILE}, UserData=ud,
                InstanceInitiatedShutdownBehavior="stop",
                MetadataOptions={"HttpTokens": "required", "HttpEndpoint": "enabled"},
                BlockDeviceMappings=[{"DeviceName": "/dev/xvda", "Ebs": {"VolumeSize": 100, "VolumeType": "gp3",
                                                                         "DeleteOnTermination": True}}],
                InstanceMarketOptions={"MarketType": "spot", "SpotOptions": {
                    "SpotInstanceType": "persistent", "InstanceInterruptionBehavior": "stop",
                    "ValidUntil": end - dt.timedelta(minutes=30)}},
                TagSpecifications=[{"ResourceType": "instance", "Tags": tags},
                                   {"ResourceType": "volume", "Tags": tags[:2]}])
            i = r["Instances"][0]
            print("LAUNCHED", i["InstanceId"], itype, s["AvailabilityZone"], prices.get(s["AvailabilityZone"]),
                  i.get("SpotInstanceRequestId"), "end", fill["END"])
            return
        except ec2.exceptions.ClientError as e:
            print(s["AvailabilityZone"], str(e)[:160], file=sys.stderr)
            if not any(t in str(e) for t in ("Capacity", "capacity", "Unsupported", "MaxSpotInstanceCount")):
                raise
    sys.exit("NO CAPACITY")


if __name__ == "__main__":
    main()
