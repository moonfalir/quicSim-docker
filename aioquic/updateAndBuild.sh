#!/bin/bash

git pull

if [ "$COMMIT" ]; then 
    git checkout "$COMMIT"
fi