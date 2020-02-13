import os, json

class MetricCalculator():
    _metricsperfile = []
    
    def calculateMetrics(self, name: str, files: list, istcpdump: bool, isquic: bool):
        print("calculate metrics of 1 connection")
        self._metricsperfile.append({
            "name": name,
            "avg_goodput": 0.0,
            "avg_throughput": 0.0,
            "avg_rtt": 0.0
        })
        id = len(self._metricsperfile) - 1
        totals = {
            "rtt_amount": 0,
            "tp_time": 0,
            "gp_time": 0,
            "unacked_packets": {}
        }
        for file in files:
            serverside = "server" in file
            totals = self.getTcpDumpMetrics(file, isquic, serverside, id, totals)

        print(self._metricsperfile)
        #print(totals)
        self._metricsperfile[id]["avg_throughput"] /= 125.0
        self._metricsperfile[id]["avg_throughput"] /= totals["tp_time"]
        self._metricsperfile[id]["avg_goodput"] /= 125.0
        self._metricsperfile[id]["avg_goodput"] /= totals["gp_time"]
        self._metricsperfile[id]["avg_rtt"] /= totals["rtt_amount"]
        print(self._metricsperfile)

    def getTcpDumpMetrics(self, file: str, isquic: bool, serverside: bool, id: int, totals: dict):
        data = ""
        with open(file, "r") as tcpdump_file:
            data = tcpdump_file.read()

        packets = json.loads(data)
        serverip = ""
        for packet in packets:
            if "quic" not in packet['_source']['layers'] and isquic:
                continue

            if "tcp" not in packet['_source']['layers'] and not isquic:
                continue
            
            if serverip == "":
                serverip = self.getServerIp(packet, isquic)
            
            isserver = self.checkPacketSendByServer(packet, serverip)

            if isquic:
                totals = self.processQuicPacket(packet, serverside, id, totals, isserver)
            else:
                print("tcp")
        return totals

    def getServerIp(self, packet: dict, isquic: bool):
        if isquic:
            if packet['_source']['layers']['quic']['quic.header_form'] == "1" and packet['_source']['layers']['quic']['quic.long.packet_type'] == "0":
                return packet['_source']['layers']['ip']['ip.dst']
            else:
                return ""
        else:
            return ""
    
    def checkPacketSendByServer(self, packet: dict, serverip: str):
        return serverip == packet["_source"]["layers"]["ip"]["ip.src"]

    def processQuicPacket(self, packet: dict, serverside: bool, id: int, totals: dict, isserver: bool):
        if serverside:
            if isserver:
                try:
                    bytes_amount = float(packet['_source']['layers']["udp"]["udp.length"])
                    timestamp = float(packet['_source']['layers']['frame']['frame.time_relative'])
                    totals = self.addThroughputBytes(id, bytes_amount, totals, timestamp)
                except KeyError as e:
                    print()
            #find RTT
            totals = self.trackRTTValues(packet, id, totals, isserver)
            #count retransmission
        else:
            if isserver:
                try:
                    frames = packet['_source']['layers']["quic"]["quic.frame"]
                    bytes_amount = 0
                    if isinstance(frames, list):
                        for frame in frames:
                            if "quic.stream.length" in frame:
                                bytes_amount += float(frame['quic.stream.length'])
                    else:
                        if "quic.stream.length" in frames:
                                bytes_amount += float(frames['quic.stream.length'])
                    timestamp = float(packet['_source']['layers']['frame']['frame.time_relative'])
                    totals = self.addGoodputBytes(id, bytes_amount, totals, timestamp)
                except KeyError as e:
                    print()
                except TypeError as t:
                    print()

        return totals

    def trackRTTValues(self, packet: dict, id: int, totals: dict, isserver: bool):
        if isserver:
            try: 
                if "quic.short" in packet['_source']['layers']["quic"]:
                    pn = int(packet['_source']['layers']["quic"]["quic.short"]["quic.packet_number"])
                else:
                    pn = int(packet['_source']['layers']["quic"]["quic.packet_number"])
                timestamp = float(packet['_source']['layers']['frame']['frame.time_relative']) * 1000
                totals["unacked_packets"][pn] = timestamp
            except TypeError as t:
                print(t)
            except KeyError as e:
                print(e)
        else:
            try:
                ackframe = self.getAckFrame(packet)
                if ackframe:
                    ack_timestamp = float(packet['_source']['layers']['frame']['frame.time_relative']) * 1000
                    large_ack = int(ackframe['quic.ack.largest_acknowledged'])
                    first_range = large_ack - int(ackframe['quic.ack.first_ack_range'])
                    acked_packets = []
                    for index, pn_timestamp in totals["unacked_packets"].items():
                        if index >= first_range and index <= large_ack:
                            self._metricsperfile[id]["avg_rtt"] += (ack_timestamp - pn_timestamp)
                            totals["rtt_amount"] += 1
                            acked_packets.append(index)
                    for acked_packet in acked_packets:
                        del totals["unacked_packets"][acked_packet]
            except TypeError as t:
                print(t)
            except KeyError as e:
                print(e)
        return totals

    def getAckFrame(self, packet: dict):
        frames = packet['_source']['layers']["quic"]["quic.frame"]
        ackframe = None
        if isinstance(frames, list):
            for frame in frames:
                if frame["quic.frame_type"] == "2":
                    ackframe = frame
                    break
        else:
            if frames["quic.frame_type"] == "2":
                    ackframe = frames
        return ackframe

    def addThroughputBytes(self, id: int, bytes_amount: float, totals: dict, timestamp: float):
        self._metricsperfile[id]["avg_throughput"] += bytes_amount
        totals["tp_time"] = timestamp
        return totals
    
    def addGoodputBytes(self, id: int, bytes_amount: float, totals: dict, timestamp: float):
        self._metricsperfile[id]["avg_goodput"] += bytes_amount
        totals["gp_time"] = timestamp
        return totals
    
    def countThroughput(self, bytes: int, timestamp: float):
        print("bytes")
    
    def getMetrics(self):
        print("return calculated metrics")