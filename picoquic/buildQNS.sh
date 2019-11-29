#!/bin/bash

CLIENT=picoquic \
SERVER=picoquic \
docker-compose -f ../quic-network-simulator/docker-compose.yml build