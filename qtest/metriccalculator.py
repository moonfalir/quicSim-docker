import os, json

class MetricCalculator():
    _metricsperfile = []
    _json_columns = ['name', 'sim', 'avg_goodput', 'avg_throughput', 'avg_rtt', 'avg_cwnd']
    
    def calculateMetrics(self, logdir: str, tcpdumpfiles: list, qlogfile: str, istcpdump: bool, isquic: bool, sim: str, run: int):
        split_dir = logdir.split("/")
        name = split_dir[len(split_dir) - 3] + "/" + split_dir[len(split_dir) - 2]
        totals = {
            "rtt_amount": 0,
            "tp_time": 0,
            "gp_time": 0,
            "cwnd_amount": 0,
            "unacked_packets": {}
        }
        run_avgs = {
            "avg_goodput": 0.0,
            "avg_throughput": 0.0,
            "avg_rtt": 0.0,
            "avg_cwnd": 0.0
        }
        for file in tcpdumpfiles:
            serverside = "server" in file
            totals, run_avgs = self.getTcpDumpMetrics(file, isquic, serverside, run_avgs, totals)
        if qlogfile != "":
            run_avgs = self.getAvgCWND(qlogfile, run_avgs, totals)

        #print(self._metricsperfile)
        #print(totals)
        try:
            run_avgs["avg_throughput"] /= 125.0
            run_avgs["avg_throughput"] /= totals["tp_time"]
            run_avgs["avg_goodput"] /= 125.0
            run_avgs["avg_goodput"] /= totals["gp_time"]
            run_avgs["avg_rtt"] /= totals["rtt_amount"]
            run_avgs["avg_cwnd"] /= totals["cwnd_amount"]
        except ZeroDivisionError as z:
            print()
        if run == 0:
            self._metricsperfile.append({
                "name": name,
                "sim": sim,
                "avg_goodput": 0.0,
                "avg_throughput": 0.0,
                "avg_rtt": 0.0,
                "avg_cwnd": 0.0,
                "runs": []
            })
            id = len(self._metricsperfile) - 1
        else:
            id = next((index for (index, d) in enumerate(self._metricsperfile) if d["name"] == name and d["sim"] == sim), None)
        
        self._metricsperfile[id]["avg_goodput"] += run_avgs["avg_goodput"]
        self._metricsperfile[id]["avg_throughput"] += run_avgs["avg_throughput"]
        self._metricsperfile[id]["avg_rtt"] += run_avgs["avg_rtt"]
        self._metricsperfile[id]["avg_cwnd"] += run_avgs["avg_cwnd"]
        self._metricsperfile[id]["runs"].append(run_avgs)
        #print(self._metricsperfile)

    def getAvgCWND(self, file: str, run_avgs: dict, totals: dict):
        data = ""
        with open(file, "r") as qlog_file:
            data = qlog_file.read()

        qlog = json.loads(data)
        events = qlog["traces"][0]["events"]
        event_fields = [x.lower() for x in qlog["traces"][0]["event_fields"]]
        try:
            event_type_id = event_fields.index("event_type")
        except ValueError as e:
            event_type_id = event_fields.index("event")
        data_id = event_fields.index("data")

        prev_cwnd = -1.0

        for event in events:
            if event[event_type_id] == "metrics_updated" and "cwnd" in event[data_id]:
                cur_cwnd = float(event[data_id]["cwnd"])
                if cur_cwnd != prev_cwnd:
                    run_avgs["avg_cwnd"] += cur_cwnd
                    totals["cwnd_amount"] += 1
                    prev_cwnd = cur_cwnd

        return run_avgs
    


    def getTcpDumpMetrics(self, file: str, isquic: bool, serverside: bool, run_avgs: dict, totals: dict):
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
                totals, run_avgs = self.processQuicPacket(packet, serverside, run_avgs, totals, isserver)
            else:
                totals, run_avgs = self.processTcpPacket(packet, serverside, run_avgs, totals, isserver)
        return totals, run_avgs

    def getServerIp(self, packet: dict, isquic: bool):
        if isquic:
            if packet['_source']['layers']['quic']['quic.header_form'] == "1" and packet['_source']['layers']['quic']['quic.long.packet_type'] == "0":
                return packet['_source']['layers']['ip']['ip.dst']
            else:
                return ""
        else:
            if packet['_source']['layers']['tcp']['tcp.flags_tree']['tcp.flags.syn'] == "1" and packet['_source']['layers']['tcp']['tcp.flags_tree']['tcp.flags.ack'] == "1":
                return packet['_source']['layers']['ip']['ip.dst']
            else:
                return ""
    
    def checkPacketSendByServer(self, packet: dict, serverip: str):
        return serverip == packet["_source"]["layers"]["ip"]["ip.src"]

    def processQuicPacket(self, packet: dict, serverside: bool, run_avgs: dict, totals: dict, isserver: bool):
        if serverside:
            if isserver:
                try:
                    bytes_amount = float(packet['_source']['layers']["frame"]["frame.len"])
                    timestamp = float(packet['_source']['layers']['frame']['frame.time_relative'])
                    totals, run_avgs = self.addThroughputBytes(run_avgs, bytes_amount, totals, timestamp)
                except KeyError as e:
                    print()
            #find RTT
            totals, run_avgs = self.trackRTTValuesQUIC(packet, run_avgs, totals, isserver)
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
                    totals, run_avgs = self.addGoodputBytes(run_avgs, bytes_amount, totals, timestamp)
                except KeyError as e:
                    print()
                except TypeError as t:
                    print()

        return totals, run_avgs

    def processTcpPacket(self, packet: dict, serverside: bool, run_avgs: dict, totals: dict, isserver: bool):
        if serverside:
            if isserver:
                try:
                    bytes_amount = float(packet['_source']['layers']["frame"]["frame.len"])
                    timestamp = float(packet['_source']['layers']['frame']['frame.time_relative'])
                    totals, run_avgs = self.addThroughputBytes(run_avgs, bytes_amount, totals, timestamp)
                except KeyError as e:
                    print()
            #find RTT
            totals, run_avgs = self.trackRTTValuesTCP(packet, run_avgs, totals, isserver)
            #count retransmission
        else:
            if isserver:
                try:
                    bytes_amount = float(packet['_source']['layers']["tcp"]["tcp.len"])
                    timestamp = float(packet['_source']['layers']['frame']['frame.time_relative'])
                    totals, run_avgs = self.addGoodputBytes(run_avgs, bytes_amount, totals, timestamp)
                except KeyError as e:
                    print()

        return totals, run_avgs
    def trackRTTValuesQUIC(self, packet: dict, run_avgs: dict, totals: dict, isserver: bool):
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
                    ackranges = self.getAckRangesQUIC(ackframe, ackranges, first_range)
                    for index, pn_timestamp in totals["unacked_packets"].items():
                        if self.isAcked(ackranges, index, True):
                            run_avgs["avg_rtt"] += (ack_timestamp - pn_timestamp)
                            totals["rtt_amount"] += 1
                            acked_packets.append(index)
                    for acked_packet in acked_packets:
                        del totals["unacked_packets"][acked_packet]
            except TypeError as t:
                print(t)
            except KeyError as e:
                print(e)
        return totals, run_avgs

    def trackRTTValuesTCP(self, packet: dict, run_avgs: dict, totals: dict, isserver: bool):
        if isserver:
            try: 
                pn = int(packet['_source']['layers']["tcp"]["tcp.seq"])
                timestamp = float(packet['_source']['layers']['frame']['frame.time_relative']) * 1000
                totals["unacked_packets"][pn] = timestamp
            except TypeError as t:
                print(t)
            except KeyError as e:
                print(e)
        else:
            try:
                tcppacket = packet['_source']['layers']["tcp"] 
                ack_timestamp = float(packet['_source']['layers']['frame']['frame.time_relative']) * 1000
                large_ack = int(tcppacket['tcp.ack'])
                acked_packets = []
                ackranges = [{
                    "high_ack": large_ack,
                    "low_ack": 0
                }]
                ackranges = self.getAckRangesTCP(tcppacket, ackranges)
                for index, pn_timestamp in totals["unacked_packets"].items():
                    if self.isAcked(ackranges, index, False):
                        run_avgs["avg_rtt"] += (ack_timestamp - pn_timestamp)
                        totals["rtt_amount"] += 1
                        acked_packets.append(index)
                for acked_packet in acked_packets:
                    del totals["unacked_packets"][acked_packet]
            except TypeError as t:
                print(t)
            except KeyError as e:
                print(e)
        return totals, run_avgs

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
    
    def getAckRangesTCP(self, tcppacket: dict, ackranges: list):
        if "tcp.options.sack_tree" in tcppacket['tcp.options_tree']:
            sack = tcppacket['tcp.options_tree']['tcp.options.sack_tree']
            left_egdes = sack['tcp.options.sack_le']
            right_edges = sack['tcp.options.sack_re']
            if isinstance(left_egdes, list):
                for index, gap in enumerate(left_egdes):
                    large_ack = int(right_edges[index])
                    low_ack = int(left_egdes[index])
                    ackranges.append({
                        "high_ack": large_ack,
                        "low_ack": low_ack
                    })
            else:
                large_ack = int(right_edges)
                low_ack = int(left_egdes)
                ackranges.append({
                    "high_ack": large_ack,
                    "low_ack": low_ack
                })

        return ackranges

    def getAckRangesQUIC(self, ackframe: dict, ackranges: list, large_ack: int):
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
    
    def isAcked(self, ackranges: list, pn: int, isquic: bool):
        acked = False
        if isquic:
            for ackrange in ackranges:
                if pn >= ackrange['low_ack'] and pn <= ackrange['high_ack']:
                    acked = True
                    break
        else:
            for ackrange in ackranges:
                if pn >= ackrange['low_ack'] and pn < ackrange['high_ack']:
                    acked = True
                    break
        return acked

    def addThroughputBytes(self, run_avgs: dict, bytes_amount: float, totals: dict, timestamp: float):
        run_avgs["avg_throughput"] += bytes_amount
        totals["tp_time"] = timestamp
        return totals, run_avgs
    
    def addGoodputBytes(self, run_avgs: dict, bytes_amount: float, totals: dict, timestamp: float):
        run_avgs["avg_goodput"] += bytes_amount
        totals["gp_time"] = timestamp
        return totals, run_avgs
    
    def saveMetrics(self, outputdir: str):
        #TODO avgs for all runs
        for id in range(0, len(self._metricsperfile)):
            self._metricsperfile[id]["avg_goodput"] /= len(self._metricsperfile[id]["runs"])
            self._metricsperfile[id]["avg_throughput"] /= len(self._metricsperfile[id]["runs"])
            self._metricsperfile[id]["avg_rtt"] /= len(self._metricsperfile[id]["runs"])
            self._metricsperfile[id]["avg_cwnd"] /= len(self._metricsperfile[id]["runs"])
        with open(outputdir + "/metrics.json", mode='w') as metrics_file:
            json.dump(self._metricsperfile, metrics_file)