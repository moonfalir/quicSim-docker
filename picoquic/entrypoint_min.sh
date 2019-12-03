#!/bin/bash

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
    ./picoquicdemo $CLIENT_PARAMS
    ./picolog_t -f qlog /logs/clientpico_mn.log > /logs/clientpico_mn.qlog 
    sleep 3
elif [ "$ROLE" == "server" ]; then
    ./picoquicdemo $SERVER_PARAMS
    ./picolog_t -f qlog /logs/serverpico_mn.log > /logs/serverpico_mn.qlog
    sleep 3
fi