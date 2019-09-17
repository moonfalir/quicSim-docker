#!/bin/bash

CLIENT=quanttest \
SERVER=quanttest \
docker-compose -f ../quic-network-simulator/docker-compose.yml build