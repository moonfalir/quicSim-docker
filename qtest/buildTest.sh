#!/bin/bash

docker-compose -f ../containernet/docker-compose.yml build

CLIENT=aioquic \
SERVER=ngtcp2 \
docker-compose -f ../quic-network-simulator/docker-compose.yml build

CLIENT=picoquic \
SERVER=quant \
docker-compose -f ../quic-network-simulator/docker-compose.yml build