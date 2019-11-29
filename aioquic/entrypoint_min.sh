#!/bin/bash

# The following variables are available for use:
# - ROLE contains the role of this execution context, client or server
# - SERVER_PARAMS contains user-supplied command line parameters
# - CLIENT_PARAMS contains user-supplied command line parameters

if [ "$ROLE" == "client" ]; then 
    python3 examples/http3_client.py -v $CLIENT_PARAMS
elif [ "$ROLE" == "server" ]; then
    python3 examples/http3_server.py -v $SERVER_PARAMS
fi