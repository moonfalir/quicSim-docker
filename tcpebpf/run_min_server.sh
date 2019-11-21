#!/bin/bash

tcpdump -i server-eth0 -w /logs/test.pcap &

sleep 2

iperf -s &