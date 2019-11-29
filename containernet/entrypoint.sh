#! /bin/bash -e

# start OVS
service openvswitch-switch start

# update containernet
git pull && python setup.py install

# check if docker socket is mounted
if [ ! -S /var/run/docker.sock ]; then
    echo 'Error: the Docker socket file "/var/run/docker.sock" was not found. It should be mounted as a volume.'
    exit 1
fi

# Copy custom controllers to pox directory
cp -a /containernet/poxcontrollers/. /pox/pox/forwarding/

echo "Welcome to Containernet running within a Docker container ..."

if [[ $# -eq 0 ]]; then
    python ./scenarios/containernet.py $SCENARIO
else
    exec $*
fi
