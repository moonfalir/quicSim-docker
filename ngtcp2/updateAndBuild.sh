#!/bin/bash

git pull

if [ "$COMMIT" ]; then 
    git checkout "$COMMIT"
fi

autoreconf -i && ./configure PKG_CONFIG_PATH=$PWD/../openssl/build/lib/pkgconfig:$PWD/../nghttp3/build/lib/pkgconfig \
 LDFLAGS="-Wl,-rpath,$PWD/../openssl/build/lib" && make -j$(nproc) check