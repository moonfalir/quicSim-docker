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
    ./picoquicdemo $CLIENT_PARAMS
    ./picolog_t -f qlog /logs/clientpico_qns.log > /logs/clientpico_qns.qlog 
    rm /logs/clientpico_qns.log
    sleep 3
elif [ "$ROLE" == "server" ]; then
    git rev-parse HEAD > /logs/sv_commit.txt
    ./picoquicdemo $SERVER_PARAMS
    ./picolog_t -f qlog /logs/serverpico_qns.log > /logs/serverpico_qns.qlog
    rm /logs/serverpico_qns.log
    sleep 3
fi