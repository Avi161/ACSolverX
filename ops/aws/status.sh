#!/bin/bash
systemctl is-active job; tail -n 5 /opt/job/run.log; cat /opt/job/out/EXIT 2>/dev/null; ls /opt/job/out | wc -l; free -g | head -2; uptime
