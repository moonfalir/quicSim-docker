#!/bin/bash

# The following variables are available for use:
# - ROLE contains the role of this execution context, client or server
# - SERVER_PARAMS contains user-supplied command line parameters
# - CLIENT_PARAMS contains user-supplied command line parameters

if [ "$ROLE" == "client" ]; then  
    iperf3 $CLIENT_PARAMS
elif [ "$ROLE" == "server" ]; then
    #tcpdump -i server-eth0 -w /logs/$SERVER_PARAMS.pcap &
    echo "iperf3" > /logs/sv_commit.txt
    python3 captureAndServe.py
fi