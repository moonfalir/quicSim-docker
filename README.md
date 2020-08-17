# QuicSim-Docker

Collection of docker containers for QUIC clients/servers for testing. There are two different network emulators available: QUIC network simulator and Containernet.

# Prerequisites

Build done on ubuntu 18.04, need at least kernel v5.3 for eBPF. Needs recent Docker version (install: https://docs.docker.com/engine/install/ubuntu/) and Docker-compose (install: https://docs.docker.com/compose/install/)

After on Debian-based Linux systems, do

```apt install python3 python3-pip git```

With framework using python3, additional packages need to be installed:

```pip3 install paramiko docker numpy```

## Build

To build QUIC network simulator, after cloning this repository use the following command:

```
git submodule update --init --recursive
```

You can build all containers with `buildAllImages.py`, change working directory to `qtest`:

```python3 buildAllImages.py```

This might take some time and might need `sudo` depending on docker priviledges.

Alternatively each implementation directory(aioquic, quant and tcpebpf) have both a `buildQNS.sh` and `buildMininet.sh` script which need to be run. For Tshark, run `buildTshark.sh` in the `wireshark` directory.

## Run tests

To run test with TCP NewReno, we configured ubuntu/debian in the following way:

```
sudo sysctl -w net.ipv4.tcp_congestion_control=reno
sudo sysctl -p
```

To start test locally, use the following command:

```python3 run.py --runs X```

* runs: the amount of times each tests will be repeated

## Running on server cluster

A small server cluster was used to run the majority of tests. Installation and configuration process is the same for the servers.

To run the script for the server cluster, use:

```python3 clusterTestControl.py --usr USERNAME --pwd PASSWORD --runs X```

* usr: username for SSH
* pwd: password for SSH
* runs: the amount of times each tests will be repeated

After the tests are finished, `scpLogs.sh` can be used to download the log files from all servers:

```./scpLogs.sh DIRECTORY USERNAME```

* DIRECTORY: directory used on all servers for the logs (represented as timestamp, printed out by previous script)
* USERNAME: username for scp (same as SSH)

The script will require to input the password for each server. After all the logs are downloaded, we can group all the metrics into one file:

```python3 groupMetrics.py DIRECTORY```

* DIRECTORY: same as used in `scpLogs.sh`
