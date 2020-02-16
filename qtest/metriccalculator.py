import os, json, csv

class MetricCalculator():
    _metricsperfile = []
    _csv_columns = ['name', 'sim', 'avg_goodput', 'avg_throughput', 'avg_rtt', 'avg_cwnd']
    
    def calculateMetrics(self, logdir: str, tcpdumpfiles: list, qlogfile: str, istcpdump: bool, isquic: bool, sim: str):
        split_dir = logdir.split("/")
        name = split_dir[len(split_dir) - 3] + "/" + split_dir[len(split_dir) - 2] + "/" + split_dir[len(split_dir) - 1]
        self._metricsperfile.append({
            "name": name,
            "sim": sim,
            "avg_goodput": 0.0,
            "avg_throughput": 0.0,
            "avg_rtt": 0.0,
            "avg_cwnd": 0.0
        })
        id = len(self._metricsperfile) - 1
        totals = {
            "rtt_amount": 0,
            "tp_time": 0,
            "gp_time": 0,
            "cwnd_amount": 0,
            "unacked_packets": {}
        }
        for file in tcpdumpfiles:
            serverside = "server" in file
            totals = self.getTcpDumpMetrics(file, isquic, serverside, id, totals)
        if qlogfile != "":
            self.getAvgCWND(qlogfile, id, totals)

        #print(self._metricsperfile)
        #print(totals)
        try:
            self._metricsperfile[id]["avg_throughput"] /= 125.0
            self._metricsperfile[id]["avg_throughput"] /= totals["tp_time"]
            self._metricsperfile[id]["avg_goodput"] /= 125.0
            self._metricsperfile[id]["avg_goodput"] /= totals["gp_time"]
            self._metricsperfile[id]["avg_rtt"] /= totals["rtt_amount"]
            self._metricsperfile[id]["avg_cwnd"] /= totals["cwnd_amount"]
        except ZeroDivisionError as z:
            print()
        #print(self._metricsperfile)

    def getAvgCWND(self, file: str, id: int, totals: dict):
        data = ""
        with open(file, "r") as qlog_file:
            data = qlog_file.read()

        qlog = json.loads(data)
        events = qlog["traces"][0]["events"]
        event_fields = [x.lower() for x in qlog["traces"][0]["event_fields"]]
        event_type_id = event_fields.index("event_type")
        data_id = event_fields.index("data")

        prev_cwnd = -1.0

        for event in events:
            if event[event_type_id] == "metrics_updated" and "cwnd" in event[data_id]:
                cur_cwnd = float(event[data_id]["cwnd"])
                if cur_cwnd != prev_cwnd:
                    self._metricsperfile[id]["avg_cwnd"] += cur_cwnd
                    totals["cwnd_amount"] += 1
                    prev_cwnd = cur_cwnd

        return totals
    


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
                totals = self.processTcpPacket(packet, serverside, id, totals, isserver)
        return totals

    def getServerIp(self, packet: dict, isquic: bool):
        if isquic:
            if packet['_source']['layers']['quic']['quic.header_form'] == "1" and packet['_source']['layers']['quic']['quic.long.packet_type'] == "0":
                return packet['_source']['layers']['ip']['ip.dst']
            else:
                return ""
        else:
            if packet['_source']['layers']['tcp']['tcp.flags_tree']['tcp.flags.syn'] == "1" and packet['_source']['layers']['tcp']['tcp.flags_tree']['tcp.flags.ack'] == "0":
                return packet['_source']['layers']['ip']['ip.dst']
            else:
                return ""
    
    def checkPacketSendByServer(self, packet: dict, serverip: str):
        return serverip == packet["_source"]["layers"]["ip"]["ip.src"]

    def processQuicPacket(self, packet: dict, serverside: bool, id: int, totals: dict, isserver: bool):
        if serverside:
            if isserver:
                try:
                    bytes_amount = float(packet['_source']['layers']["frame"]["frame.len"])
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
                                if "quic.stream_data" in frame:
                                    data = frame["quic.stream_data"].replace(':', '')
                                    bytes_amount = len(data) / 2
                    else:
                        if "quic.stream.length" in frames:
                                bytes_amount += float(frames['quic.stream.length'])
                        else:
                            if "quic.stream_data" in frames:
                                data = frames["quic.stream_data"].replace(':', '')
                                bytes_amount = len(data) / 2
                    timestamp = float(packet['_source']['layers']['frame']['frame.time_relative'])
                    totals = self.addGoodputBytes(id, bytes_amount, totals, timestamp)
                except KeyError as e:
                    print()
                except TypeError as t:
                    print()

        return totals

    def processTcpPacket(self, packet: dict, serverside: bool, id: int, totals: dict, isserver: bool):
        if serverside:
            if isserver:
                try:
                    bytes_amount = float(packet['_source']['layers']["frame"]["frame.len"])
                    timestamp = float(packet['_source']['layers']['frame']['frame.time_relative'])
                    totals = self.addThroughputBytes(id, bytes_amount, totals, timestamp)
                except KeyError as e:
                    print()
            #find RTT
            #totals = self.trackRTTValues(packet, id, totals, isserver)
            #count retransmission

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
                    ackranges = [{
                        "high_ack": large_ack,
                        "low_ack": first_range
                    }]
                    ackranges = self.getAckRanges(ackframe, ackranges, first_range)
                    for index, pn_timestamp in totals["unacked_packets"].items():
                        if self.isAcked(ackranges, index):
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
    
    def getAckRanges(self, ackframe: dict, ackranges: list, large_ack: int):
        if "quic.ack.gap" in ackframe:
            ack_gaps = ackframe["quic.ack.gap"]
            range_lengths = ackframe["quic.ack.ack_range"]
            if isinstance(ack_gaps, list):
                for index, gap in enumerate(ack_gaps):
                    gap = int(gap) + 2
                    large_ack -= gap
                    range_length = int(range_lengths[index])
                    low_ack = large_ack - range_length
                    ackranges.append({
                        "high_ack": large_ack,
                        "low_ack": low_ack
                    })
                    large_ack = low_ack
            else:
                gap = int(ack_gaps) + 2
                large_ack -= gap
                range_length = int(range_lengths)
                low_ack = large_ack - range_length
                ackranges.append({
                    "high_ack": large_ack,
                    "low_ack": low_ack
                })

        return ackranges
    
    def isAcked(self, ackranges: list, pn: int):
        acked = False
        for ackrange in ackranges:
            if pn >= ackrange['low_ack'] and pn <= ackrange['high_ack']:
                acked = True
                break
        return acked

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
    
    def saveMetrics(self, outputdir: str):
        with open(outputdir + "/metrics.csv", mode='w') as metrics_file:
            metrics_writer = csv.DictWriter(metrics_file, delimiter=",", fieldnames=self._csv_columns)
            metrics_writer.writeheader()
            metrics_writer.writerows(self._metricsperfile)