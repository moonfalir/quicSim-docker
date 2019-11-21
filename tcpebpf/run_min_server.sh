#!/bin/bash

tcpdump -i server-eth0 -w /logs/test.pcap &

iperf -s &