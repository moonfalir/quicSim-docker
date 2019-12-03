#!/bin/bash

# Set up the routing needed for the simulation
/setup.sh

git pull

if [ "$COMMIT" ]; then 
    git checkout "$COMMIT"
fi

cmake . && make

# The following variables are available for use:
# - ROLE contains the role of this execution context, client or server
# - SERVER_PARAMS contains user-supplied command line parameters
# - CLIENT_PARAMS contains user-supplied command line parameters

if [ "$ROLE" == "client" ]; then
    /wait-for-it.sh sim:57832 -s -t 30    
    ./picoquicdemo $CLIENT_PARAMS
    ./picolog_t -f qlog /logs/clientpico_qns.log > /logs/clientpico_qns.qlog 
    sleep 3
elif [ "$ROLE" == "server" ]; then
    ./picoquicdemo $SERVER_PARAMS
    ./picolog_t -f qlog /logs/serverpico_qns.log > /logs/serverpico_qns.qlog
    sleep 3
fi