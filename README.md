# QuicSim-Docker

Collection of docker containers for QUIC clients/servers for testing. There are two different network emulators available: QUIC network simulator and Containernet.

## Build

To build QUIC network simulator first clone with the following command:

```
git submodule update --init --recursive
```

The rest of the build instruction are available on https://github.com/moonfalir/quic-network-simulator.

## Build containers & run tests
Build scripts are available in the QUIC implementation directories (e.g. quant), with example run scripts to start a test. 