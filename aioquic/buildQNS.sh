#!/bin/bash

CLIENT=aioquic \
SERVER=aioquic \
docker-compose -f ../quic-network-simulator/docker-compose.yml build