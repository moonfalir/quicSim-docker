#!/bin/bash

# The following variables are available for use:
# - ROLE contains the role of this execution context, client or server
# - SERVER_PARAMS contains user-supplied command line parameters
# - CLIENT_PARAMS contains user-supplied command line parameters

if [ "$ROLE" == "client" ]; then 
    ./examples/client $CLIENT_PARAMS
elif [ "$ROLE" == "server" ]; then
    ./examples/server $SERVER_PARAMS
fi