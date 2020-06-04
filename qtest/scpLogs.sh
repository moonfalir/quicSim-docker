#!/bin/bash

if [ $# -eq 0 ]
  then
    echo "No arguments supplied"
    exit 1
fi

echo "Retrieving logs from 172.19.13.222"

scp -r $2@172.19.13.222:./quicSim-docker/qtest/logs/$1 ./logs

echo "Retrieving logs from 172.19.13.223"

scp -r $2@172.19.13.223:./quicSim-docker/qtest/logs/$1 ./logs

echo "Retrieving logs from 172.19.13.224"

scp -r $2@172.19.13.224:./quicSim-docker/qtest/logs/$1 ./logs

echo "Retrieving logs from 172.19.13.225"

scp -r $2@172.19.13.225:./quicSim-docker/qtest/logs/$1 ./logs

echo "Retrieving logs from 172.19.13.226"

scp -r $2@172.19.13.226:./quicSim-docker/qtest/logs/$1 ./logs

echo "Retrieving logs from 172.19.13.227"

scp -r $2@172.19.13.227:./quicSim-docker/qtest/logs/$1 ./logs