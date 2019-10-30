#!/usr/bin/python

from __future__ import print_function
from bcc import BPF
from socket import inet_ntop, AF_INET
from struct import pack
import time as ti
import json
import ctypes

# initialize BPF
b = BPF(src_file="ebpf_probes.c")
b.attach_kprobe(event="tcp_rcv_established", fn_name="trace_rcv_established")
qlog = {
	"qlog_version": "draft-01",
	"traces": [
		{
			"common_fields": {
				"reference_time": -1
			},
			"event_fields": [
				"relative_time",
				"category",
				"event_type",
				"data"
			],
			"events": [],
			"vantage_point": {
				"name": "iperf",
				"type": "server"
			}
		},
		{
			"common_fields": {
				"reference_time": -1
			},
			"event_fields": [
				"relative_time",
				"category",
				"event_type",
				"data"
			],
			"events": [],
			"vantage_point": {
				"name": "iperf",
				"type": "client"
			}
		}
	]
}

with open('/proc/uptime', 'r') as f:
	uptime_s = float(f.readline().split()[0])
	start_time = ti.time() - uptime_s

reference_time_c = -1
reference_time_s = -1

def print_tcp_event(cpu, data, size):
	event = b["tcp_events"].event(data)
	sender = inet_ntop(AF_INET, pack('I', event.saddr)) + ":" + str(event.sport)
	receiver = inet_ntop(AF_INET, pack('I', event.daddr)) + ":" + str(event.dport)
	if sender.__contains__("10.0.0.252"):
		global reference_time_s
		if reference_time_s == -1:
			reference_time_s = start_time + (ctypes.c_float(event.timestamp).value / 1000000000)
			qlog["traces"][0]["common_fields"]["reference_time"] = reference_time_s
		time = reference_time_s - (start_time + (ctypes.c_float(event.timestamp).value / 1000000000))
		output_arr = []
		output_arr.append("%.6f" % (abs(time)))
		output_arr.append("recovery")
		output_arr.append("metrics_updated")
		output_arr.append(
			{
				"bytes_in_flight": event.bytes_sent - event.bytes_acked, 
				"cwnd": event.snd_cwnd,
				"sender": inet_ntop(AF_INET, pack('I', event.saddr)) + ":" + str(event.sport),
				"receiver": inet_ntop(AF_INET, pack('I', event.daddr)) + ":" + str(event.dport)
			}
		)
		qlog["traces"][0]["events"].append(output_arr)
	if sender.__contains__("10.0.0.251"):
		global reference_time_c
		if reference_time_c == -1:
			reference_time_c = start_time + (ctypes.c_float(event.timestamp).value / 1000000000)
			qlog["traces"][1]["common_fields"]["reference_time"] = reference_time_c
		time = reference_time_c - (start_time + (ctypes.c_float(event.timestamp).value / 1000000000))
		output_arr = []
		output_arr.append("%.6f" % (abs(time) * 1000))
		output_arr.append("recovery")
		output_arr.append("metrics_updated")
		output_arr.append(
			{
				"bytes_in_flight": event.bytes_sent - event.bytes_acked, 
				"cwnd": event.snd_cwnd,
				"sender": inet_ntop(AF_INET, pack('I', event.saddr)) + ":" + str(event.sport),
				"receiver": inet_ntop(AF_INET, pack('I', event.daddr)) + ":" + str(event.dport)
			}
		)
		qlog["traces"][1]["events"].append(output_arr)
print("Tracing tcp events ... Hit Ctrl-C to end")

# header
print("Output network information ...")

b["tcp_events"].open_perf_buffer(print_tcp_event)
while 1:
    try:
        b.perf_buffer_poll()
    except KeyboardInterrupt:
		with open('/scripts/' + str(ti.time()) + '.qlog', 'w') as f:
			f.write(json.dumps(qlog))
		exit()