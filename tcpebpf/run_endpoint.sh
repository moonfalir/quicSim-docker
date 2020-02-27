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
    
    iperf3 $CLIENT_PARAMS
elif [ "$ROLE" == "server" ]; then
    python3 tcp_server.py --port 57830
    /wait-for-it.sh sim:57832 -s -t 30   
    #tcpdump -i eth0 -w /logs/$CURTIME.pcap &
    python3 captureAndServe.py
fi