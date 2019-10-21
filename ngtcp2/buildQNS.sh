#!/bin/bash

CLIENT=ngtcp2 \
SERVER=ngtcp2 \
docker-compose -f ../quic-network-simulator/docker-compose.yml build