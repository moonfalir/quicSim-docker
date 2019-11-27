#!/bin/bash

tcpdump -i server-eth0 -w /logs/$1.pcap &

python3 /simple_socket/h0_server.py --port 8080 &