#!/bin/bash

if [ "$COMMIT" ]; then 
    git checkout "$COMMIT"
    cmake . && make
fi