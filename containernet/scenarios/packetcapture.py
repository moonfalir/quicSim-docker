import subprocess

class PacketCapture:
    _clientint = "s1-eth2"
    _serverint = "s2-eth2"

    _clientcapture = None
    _servercapture = None

    def startCapture(self):
        self._clientcapture = subprocess.Popen(["tcpdump", "-i", self._clientint, "-w",  "/logs/trace_node_clients.pcap"])
        self._servercapture = subprocess.Popen(["tcpdump", "-i", self._serverint, "-w",  "/logs/trace_node_servers.pcap"])

    def stopCapture(self):
        self._clientcapture.terminate()
        self._servercapture.terminate()