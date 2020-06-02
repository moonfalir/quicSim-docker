import docker
dockercl = docker.from_env()


print("build QNS endpoint")
dockercl.images.build(path="../quic-network-simulator/endpoint", tag="quic-network-simulator-endpoint")
print("build QNS sim")
dockercl.images.build(path="../quic-network-simulator/sim", tag="sim")
print("build wireshark")
dockercl.images.build(path="../wireshark", tag="qtest-tshark")

print("build MIN sim")
dockercl.images.build(path="../containernet", tag="containernet")

print("build Quant")
dockercl.images.build(path="../quant", tag="quant")
print("build Aioquic")
dockercl.images.build(path="../aioquic", tag="aioquic")
print("build Tcp eBPF")
dockercl.images.build(path="../tcpebpf", tag="tcpebpf")