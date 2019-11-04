#!/bin/bash

# Set up the routing needed for the simulation
/setup.sh

git pull && autoreconf -i && ./configure PKG_CONFIG_PATH=$PWD/../openssl/build/lib/pkgconfig:$PWD/../nghttp3/build/lib/pkgconfig \
 LDFLAGS="-Wl,-rpath,$PWD/../openssl/build/lib" && make -j$(nproc) check

# The following variables are available for use:
# - ROLE contains the role of this execution context, client or server
# - SERVER_PARAMS contains user-supplied command line parameters
# - CLIENT_PARAMS contains user-supplied command line parameters

if [ "$ROLE" == "client" ]; then
    /wait-for-it.sh sim:57832 -s -t 30
    ./examples/client $CLIENT_PARAMS
elif [ "$ROLE" == "server" ]; then
    ./examples/server $SERVER_PARAMS
fi