#!/bin/bash

docker run -it --rm --privileged -v /sys/kernel/debug:/sys/kernel/debug:rw -v "$PWD/bccscripts":/scripts -v "$PWD/logs":/logs tcpebpf-obs