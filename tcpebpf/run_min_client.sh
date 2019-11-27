#!/bin/bash

if [ $# > 0 ]
then
    CURTIME=$1
else
    CURTIME=$(date +%Y-%m-%d-%H-%M)
fi
python /bccscripts/tcpprobe_congestion.py $CURTIME &
EBPF_PID=$!

sleep 2

python3 /simple_socket/h0_client.py --ip 10.0.0.251 --port 8080 --bytes 5000000

wait $EBPF_PID