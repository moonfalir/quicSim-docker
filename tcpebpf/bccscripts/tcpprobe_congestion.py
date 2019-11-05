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
#b.attach_kprobe(event="tcp_rcv_established", fn_name="trace_rcv_established")
b.attach_kprobe(event="bictcp_state", fn_name="trace_cubictcp_state")
b.attach_kretprobe(event="bictcp_recalc_ssthresh", fn_name="trace_recalc_ssthresh")
b.attach_kprobe(event="bictcp_cwnd_event", fn_name="trace_cwnd_event")
b.attach_kprobe(event="tcp_cong_avoid_ai", fn_name="trace_cong_avoid")
b.attach_kretprobe(event="tcp_slow_start", fn_name="trace_slow_start")
b.attach_kprobe(event="tcp_enter_loss", fn_name="trace_enter_loss")
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

ca_states = {}
ca_states[0] = "TCP_CA_Open"
ca_states[1] = "TCP_CA_Disorder"
ca_states[2] = "TCP_CA_CWR"
ca_states[3] = "TCP_CA_Recovery"
ca_states[4] = "TCP_CA_Loss"

cwnd_event_types = {}
cwnd_event_types[0] = "CA_EVENT_TX_START"
cwnd_event_types[1] = "CA_EVENT_CWND_RESTART"
cwnd_event_types[2] = "CA_EVENT_COMPLETE_CWR"
cwnd_event_types[3] = "CA_EVENT_LOSS"
cwnd_event_types[4] = "CA_EVENT_ECN_NO_CE"
cwnd_event_types[5] = "CA_EVENT_ECN_IS_CE"

with open('/proc/uptime', 'r') as f:
	uptime_s = float(f.readline().split()[0])
	start_time = ti.time() - uptime_s

reference_time_c = -1
reference_time_s = -1

def print_tcp_event(cpu, data, size):
	event = b["tcp_events"].event(data)
	sender = inet_ntop(AF_INET, pack('I', event.saddr))
	if sender.__contains__("10.0.0.252") or sender.__contains__("193.167.0.100"):
		global reference_time_s
		if reference_time_s == -1:
			reference_time_s = start_time + (ctypes.c_float(event.timestamp).value / 1000000000)
			qlog["traces"][0]["common_fields"]["reference_time"] = reference_time_s
		time = reference_time_s - (start_time + (ctypes.c_float(event.timestamp).value / 1000000000))
		output_arr = []
		output_arr.append("%.6f" % (abs(time) * 1000))
		output_arr.append("recovery")
		output_arr.append("metrics_updated")
		output_arr.append(
			{
				"bytes_in_flight": event.bytes_sent - event.bytes_acked, 
				"cwnd": event.snd_cwnd
			}
		)
		qlog["traces"][0]["events"].append(output_arr)
	if sender.__contains__("10.0.0.251") or sender.__contains__("193.167.100.100"):
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
				"cwnd": event.snd_cwnd
			}
		)
		qlog["traces"][1]["events"].append(output_arr)

def print_ca_state(cpu, data, size):
	global ca_states
	event = b["ca_state"].event(data)
	sender = inet_ntop(AF_INET, pack('I', event.saddr))
	if sender.__contains__("10.0.0.252") or sender.__contains__("193.167.0.100"):
		global reference_time_s
		if reference_time_s == -1:
			reference_time_s = start_time + (ctypes.c_float(event.timestamp).value / 1000000000)
			qlog["traces"][0]["common_fields"]["reference_time"] = reference_time_s
		time = reference_time_s - (start_time + (ctypes.c_float(event.timestamp).value / 1000000000))
		output_arr = []
		output_arr.append("%.6f" % (abs(time) * 1000))
		output_arr.append("recovery")
		output_arr.append("metrics_updated")
		output_arr.append(
			{
				"ca_state": ca_states[event.new_state]
			}
		)
		qlog["traces"][0]["events"].append(output_arr)
	if sender.__contains__("10.0.0.251") or sender.__contains__("193.167.100.100"):
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
				"ca_state": ca_states[event.new_state]
			}
		)
		qlog["traces"][1]["events"].append(output_arr)

def print_ssthresh_event(cpu, data, size):
	event = b["ssthresh_event"].event(data)
	sender = inet_ntop(AF_INET, pack('I', event.saddr))
	if sender.__contains__("10.0.0.252") or sender.__contains__("193.167.0.100"):
		global reference_time_s
		if reference_time_s == -1:
			reference_time_s = start_time + (ctypes.c_float(event.timestamp).value / 1000000000)
			qlog["traces"][0]["common_fields"]["reference_time"] = reference_time_s
		time = reference_time_s - (start_time + (ctypes.c_float(event.timestamp).value / 1000000000))
		output_arr = []
		output_arr.append("%.6f" % (abs(time) * 1000))
		output_arr.append("recovery")
		output_arr.append("metrics_updated")
		output_arr.append(
			{
				"ssthresh": str(event.ssthresh)
			}
		)
		qlog["traces"][0]["events"].append(output_arr)
	if sender.__contains__("10.0.0.251") or sender.__contains__("193.167.100.100"):
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
				"ssthresh": str(event.ssthresh)
			}
		)
		qlog["traces"][1]["events"].append(output_arr)

def print_cwnd_event(cpu, data, size):
	global cwnd_event_types
	event = b["cwnd_event"].event(data)
	sender = inet_ntop(AF_INET, pack('I', event.saddr))
	if sender.__contains__("10.0.0.252") or sender.__contains__("193.167.0.100"):
		global reference_time_s
		if reference_time_s == -1:
			reference_time_s = start_time + (ctypes.c_float(event.timestamp).value / 1000000000)
			qlog["traces"][0]["common_fields"]["reference_time"] = reference_time_s
		time = reference_time_s - (start_time + (ctypes.c_float(event.timestamp).value / 1000000000))
		output_arr = []
		output_arr.append("%.6f" % (abs(time) * 1000))
		output_arr.append("recovery")
		output_arr.append("metrics_updated")
		output_arr.append(
			{
				"cwnd_event": cwnd_event_types[event.event_type]
			}
		)
		qlog["traces"][0]["events"].append(output_arr)
	if sender.__contains__("10.0.0.251") or sender.__contains__("193.167.100.100"):
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
				"cwnd_event": cwnd_event_types[event.event_type]
			}
		)
		qlog["traces"][1]["events"].append(output_arr)

def print_cwnd_change(cpu, data, size):
	event = b["cwnd_change"].event(data)
	sender = inet_ntop(AF_INET, pack('I', event.saddr))
	if sender.__contains__("10.0.0.252") or sender.__contains__("193.167.0.100"):
		global reference_time_s
		if reference_time_s == -1:
			reference_time_s = start_time + (ctypes.c_float(event.timestamp).value / 1000000000)
			qlog["traces"][0]["common_fields"]["reference_time"] = reference_time_s
		time = reference_time_s - (start_time + (ctypes.c_float(event.timestamp).value / 1000000000))
		output_arr = []
		output_arr.append("%.6f" % (abs(time) * 1000))
		output_arr.append("recovery")
		output_arr.append("metrics_updated")
		output_arr.append(
			{
				"cwnd": str(event.snd_cwnd),
				"packets_in_flight": str(event.pkts_in_flight)
			}
		)
		qlog["traces"][0]["events"].append(output_arr)
	if sender.__contains__("10.0.0.251") or sender.__contains__("193.167.100.100"):
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
				"cwnd": str(event.snd_cwnd),
				"packets_in_flight": str(event.pkts_in_flight)
			}
		)
		qlog["traces"][1]["events"].append(output_arr)


def print_loss_event(cpu, data, size):
	event = b["loss_event"].event(data)
	sender = inet_ntop(AF_INET, pack('I', event.saddr))
	if sender.__contains__("10.0.0.252") or sender.__contains__("193.167.0.100"):
		global reference_time_s
		if reference_time_s == -1:
			reference_time_s = start_time + (ctypes.c_float(event.timestamp).value / 1000000000)
			qlog["traces"][0]["common_fields"]["reference_time"] = reference_time_s
		time = reference_time_s - (start_time + (ctypes.c_float(event.timestamp).value / 1000000000))
		output_arr = []
		output_arr.append("%.6f" % (abs(time) * 1000))
		output_arr.append("recovery")
		output_arr.append("packet_lost")
		output_arr.append(
			{
				"seq_lost": str(event.loss_seq)
			}
		)
		qlog["traces"][0]["events"].append(output_arr)
	if sender.__contains__("10.0.0.251") or sender.__contains__("193.167.100.100"):
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
				"seq_lost": str(event.loss_seq)
			}
		)
		qlog["traces"][1]["events"].append(output_arr)

print("Tracing tcp events ... Hit Ctrl-C to end")

# header
print("Output network information ...")

b["tcp_events"].open_perf_buffer(print_tcp_event)
b["ca_state"].open_perf_buffer(print_ca_state)
b["ssthresh_event"].open_perf_buffer(print_ssthresh_event)
b["cwnd_event"].open_perf_buffer(print_cwnd_event)
b["cwnd_change"].open_perf_buffer(print_cwnd_change)
b["loss_event"].open_perf_buffer(print_loss_event)
while 1:
    try:
        b.perf_buffer_poll()
    except KeyboardInterrupt:
		with open('/scripts/' + str(ti.time()) + '.qlog', 'w') as f:
			f.write(json.dumps(qlog))
		exit()