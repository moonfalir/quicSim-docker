#!/bin/bash

# Set up the routing needed for the simulation
/setup.sh
./updateAndBuild.sh
# The following variables are available for use:
# - ROLE contains the role of this execution context, client or server
# - SERVER_PARAMS contains user-supplied command line parameters
# - CLIENT_PARAMS contains user-supplied command line parameters

if [ "$ROLE" == "client" ]; then
    python3 tcp_server.py --port 57831
    /wait-for-it.sh sim:57832 -s -t 30
    git rev-parse HEAD > /logs/cl_commit.txt
    ./examples/client $CLIENT_PARAMS
elif [ "$ROLE" == "server" ]; then
    python3 tcp_server.py --port 57830
    git rev-parse HEAD > /logs/sv_commit.txt
    ./examples/server $SERVER_PARAMS
fi