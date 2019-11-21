#!/bin/bash

python /bccscripts/tcpprobe_congestion.py &
EBPF_PID=$!

sleep 5

iperf -n 5000000 -c 10.0.0.251 5001

wait $EBPF_PID