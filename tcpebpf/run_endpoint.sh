#!/bin/bash

# Set up the routing needed for the simulation
/setup.sh

# The following variables are available for use:
# - ROLE contains the role of this execution context, client or server
# - SERVER_PARAMS contains user-supplied command line parameters
# - CLIENT_PARAMS contains user-supplied command line parameters
# - CURTIME contains the timestamp of the start of the simulation

if [ "$ROLE" == "client" ]; then
    python3 tcp_server.py --port 57831
    /wait-for-it.sh sim:57832 -s -t 30    
    #python /bccscripts/tcpprobe_congestion.py $CURTIME &
    #EBPF_PID=$!

    #sleep 2

    python3 /simple_socket/h0_client.py $CLIENT_PARAMS

    #wait $EBPF_PID
elif [ "$ROLE" == "server" ]; then
    python3 tcp_server.py --port 57830
    #tcpdump -i eth0 -w /logs/$CURTIME.pcap &

    python3 /simple_socket/h0_server.py $SERVER_PARAMS
fi