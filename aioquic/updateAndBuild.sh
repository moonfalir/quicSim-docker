#!/bin/bash

if [ "$COMMIT" ]; then 
    git checkout "$COMMIT"
fi