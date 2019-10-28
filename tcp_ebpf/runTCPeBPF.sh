#!/bin/bash

docker run -it --rm --privileged -v /sys/kernel/debug:/sys/kernel/debug:ro -v "$PWD/bccscripts":/scripts tcpebpf