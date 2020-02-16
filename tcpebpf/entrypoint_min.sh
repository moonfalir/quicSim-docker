#!/bin/bash

# The following variables are available for use:
# - ROLE contains the role of this execution context, client or server
# - SERVER_PARAMS contains user-supplied command line parameters
# - CLIENT_PARAMS contains user-supplied command line parameters

if [ "$ROLE" == "client" ]; then 
    #python /bccscripts/tcpprobe_congestion.py $CLIENT_PARAMS &
    #EBPF_PID=$!

    #sleep 2

    python3 /simple_socket/h0_client.py $CLIENT_PARAMS 

    #wait $EBPF_PID
elif [ "$ROLE" == "server" ]; then
    #tcpdump -i server-eth0 -w /logs/$SERVER_PARAMS.pcap &

    python3 /simple_socket/h0_server.py $SERVER_PARAMS
fi