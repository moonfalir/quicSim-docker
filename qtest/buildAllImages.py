import docker
dockercl = docker.from_env()


dockercl.images.build(path="../quic-network-simulator/endpoint", tag="quic-network-simulator-endpoint")
dockercl.images.build(path="../quic-network-simulator/sim", tag="sim")

dockercl.images.build(path="../containernet", tag="containernet")

dockercl.images.build(path="../quant", tag="quant")
dockercl.images.build(path="../aioquic", tag="aioquic")
dockercl.images.build(path="../tcpebpf", tag="tcpebpf")