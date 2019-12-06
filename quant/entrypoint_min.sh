#!/bin/bash

git pull

if [ "$COMMIT" ]; then 
    git checkout "$COMMIT"
fi

cmake .. && make

# The following variables are available for use:
# - ROLE contains the role of this execution context, client or server
# - SERVER_PARAMS contains user-supplied command line parameters
# - CLIENT_PARAMS contains user-supplied command line parameters

if [ "$ROLE" == "client" ]; then 
    # Change interface name so quant can bind to it
    git rev-parse HEAD > /logs/cl_commit.txt
    ifconfig client-eth0 down  
    ip link set client-eth0 name eth1  
    ifconfig eth1 up
    ./bin/client $CLIENT_PARAMS
    sleep 3
elif [ "$ROLE" == "server" ]; then
    git rev-parse HEAD > /logs/sv_commit.txt
    ifconfig server-eth0 down  
    ip link set server-eth0 name eth1
    ifconfig eth1 up
    ./bin/server $SERVER_PARAMS
fi