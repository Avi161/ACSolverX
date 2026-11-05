"""Run a short shell script on a box over SSM and print its output (boto3; output is cut at ~24,000 characters).

    python ops/aws/ssm_run.py <instance-id> <script-file | -c 'commands'> [timeout-s]
"""
import sys
import time

import boto3


def run(iid, script, timeout=600):
    ssm = boto3.client("ssm")
    cid = ssm.send_command(InstanceIds=[iid], DocumentName="AWS-RunShellScript",
                           Parameters={"commands": [script], "executionTimeout": [str(timeout)]})["Command"]["CommandId"]
    while True:
        time.sleep(2)
        try:
            r = ssm.get_command_invocation(CommandId=cid, InstanceId=iid)
        except ssm.exceptions.InvocationDoesNotExist:
            continue
        if r["Status"] in ("Success", "Failed", "Cancelled", "TimedOut"):
            return r["Status"], r["StandardOutputContent"], r["StandardErrorContent"]


if __name__ == "__main__":
    iid, arg = sys.argv[1], sys.argv[2]
    script = sys.argv[3] if arg == "-c" else open(arg).read()
    timeout = int(sys.argv[4] if arg == "-c" and len(sys.argv) > 4 else (sys.argv[3] if arg != "-c" and len(sys.argv) > 3 else 600))
    st, out, err = run(iid, "export HOME=/root\n" + script, timeout)
    print(out, end="")
    if err:
        print(err, end="", file=sys.stderr)
    print("STATUS", st, file=sys.stderr)
    sys.exit(st != "Success")
