#!/bin/bash

# Set up the routing needed for the simulation
/setup.sh

# The following variables are available for use:
# - ROLE contains the role of this execution context, client or server
# - SERVER_PARAMS contains user-supplied command line parameters
# - CLIENT_PARAMS contains user-supplied command line parameters
if [ "$ROLE" == "client" ]; then
    /wait-for-it.sh sim:57832 -s -t 30  
    git rev-parse HEAD > /logs/cl_commit.txt  
    python3 examples/http3_client.py -v $CLIENT_PARAMS
elif [ "$ROLE" == "server" ]; then
    git rev-parse HEAD > /logs/sv_commit.txt
    python3 examples/http3_server.py -v $SERVER_PARAMS
fi