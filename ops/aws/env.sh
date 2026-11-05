# Non-secret AWS settings for this branch's runs (keys come from the environment, never from here).
export AWS_PAGER=""
export AWS_DEFAULT_REGION=us-east-1
export PROJECT=claude-agent
export BUCKET=${BUCKET:-claude-agent-205558941715}
export BOX_SG=sg-07363655368c9d2d2          # claude-agent-no-inbound: no inbound rules
export BOX_PROFILE=${BOX_PROFILE:-claude-box}  # SSM + read/write on $BUCKET only
