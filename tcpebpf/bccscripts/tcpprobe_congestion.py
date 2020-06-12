#!/usr/bin/python

from __future__ import print_function, division
from bcc import BPF
from socket import inet_ntop, AF_INET
from struct import pack
import time as ti
import json
import ctypes
import sys

# Initialize BPF
b = BPF(src_file="ebpf_probes.c")

# Attach trace functions to event functions as k(ret)probes
b.attach_kprobe(event="tcp_reno_cong_avoid", fn_name="trace_cong_avoid")
#b.attach_kprobe(event="tcp_slow_start", fn_name="trace_slow_start")
b.attach_kprobe(event="tcp_init_buffer_space", fn_name="trace_init_cong_control")
b.attach_kprobe(event="tcp_mark_skb_lost", fn_name="trace_mark_lost")
b.attach_kprobe(event="tcp_write_timer_handler", fn_name="trace_timeout_trigger")
b.attach_kprobe(event="tcp_rack_mark_lost", fn_name="trace_rack_timer")
b.attach_kretprobe(event="tcp_schedule_loss_probe", fn_name="trace_probe_timer")

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
		}
	]
}

# Congestion algorithm states
ca_states = {}
ca_states[0] = "TCP_CA_Open"
ca_states[1] = "TCP_CA_Disorder"
ca_states[2] = "TCP_CA_CWR"
ca_states[3] = "TCP_CA_Recovery"
ca_states[4] = "TCP_CA_Loss"

# CWND events
cwnd_event_types = {}
cwnd_event_types[0] = "CA_EVENT_TX_START"
cwnd_event_types[1] = "CA_EVENT_CWND_RESTART"
cwnd_event_types[2] = "CA_EVENT_COMPLETE_CWR"
cwnd_event_types[3] = "CA_EVENT_LOSS"
cwnd_event_types[4] = "CA_EVENT_ECN_NO_CE"
cwnd_event_types[5] = "CA_EVENT_ECN_IS_CE"

# Get timestamp of kernel boot
with open('/proc/uptime', 'r') as f:
	uptime_s = float(f.readline().split()[0])
	start_time = ti.time() - uptime_s

# Reference times for server
reference_time = -1

# Calculate time delta of event
def setTimeInfo(timestamp):
	time = 0.0
	global reference_time
	if reference_time == -1:
		reference_time = start_time + (ctypes.c_float(timestamp).value / 1000000000)
		qlog["traces"][0]["common_fields"]["reference_time"] = reference_time
	time = reference_time - (start_time + (ctypes.c_float(timestamp).value / 1000000000))
	return time

prev_met_upd_t = 0
# Log new CWND values
def print_cwnd_change(cpu, data, size):
	event = b["cwnd_change"].event(data)
	# get sender's IP
	sender = inet_ntop(AF_INET, pack('I', event.saddr))
	if sender.__contains__("10.0.0.251") or sender.__contains__("193.167.100.100"):
		global prev_met_upd_t
		output_arr = []
		output_arr.append("%.6f" % (abs(prev_met_upd_t) * 1000))
		prev_met_upd_t = setTimeInfo(event.timestamp)
		output_arr.append("recovery")
		output_arr.append("metrics_updated")
		output_arr.append(
			{
				"cwnd": str(event.snd_cwnd),
				"packets_in_flight": str(event.pkts_in_flight),
				"min_rtt": "%.2f" % (event.min_rtt / 1000),
				"smoothed_rtt": "%.2f" % (event.smoothed_rtt / 1000),
				"latest_rtt": "%.2f" % (event.latest_rtt / 1000),
				"rtt_variance": "%.2f" % (event.rttvar_us / 1000)
			}
		)
		qlog["traces"][0]["events"].append(output_arr)

# Log initial congestion control values
def print_init_cong_control(cpu, data, size):
	event = b["init_event"].event(data)
	sender = inet_ntop(AF_INET, pack('I', event.saddr))
	if sender.__contains__("10.0.0.251") or sender.__contains__("193.167.100.100"):
		time = setTimeInfo(event.timestamp)
		output_arr = []
		output_arr.append("%.6f" % (abs(time) * 1000))
		output_arr.append("transport")
		output_arr.append("parameters_set")
		output_arr.append(
			{
				"begin_of_round": str(event.round_start),
				"end_seq_round": str(event.end_seq),
				"min_rtt_curr_round": str(event.curr_rtt),
				"samples_needed_curr_rtt": str(event.sample_cnt),
				"initial_ssthresh": str(event.ssthresh),
				"deviation_rtt_ms": "%.2f" % (event.mdev_us / 1000),
				"intial_RTO": str(event.icsk_rto)
			}
		)
		qlog["traces"][0]["events"].append(output_arr)

def print_mark_lost(cpu, data, size):
	event = b["mark_lost"].event(data)
	sender = inet_ntop(AF_INET, pack('I', event.saddr))
	if sender.__contains__("10.0.0.251") or sender.__contains__("193.167.100.100"):
		time = setTimeInfo(event.timestamp)
		output_arr = []
		output_arr.append("%.6f" % (abs(time) * 1000))
		output_arr.append("recovery")
		output_arr.append("packet_lost")

		trigger = ""
		if event.loss_trigger == 1:
			trigger = "time_threshold"
		elif event.loss_trigger == 2:
			trigger = "pto_expired"
		elif event.loss_trigger == 3:
			trigger = "retrans_timer"
		output_arr.append(
			{
				"packet_number": str(event.seq),
				"trigger": trigger,
			}
		)
		if trigger != "":
			qlog["traces"][0]["events"].append(output_arr)

def print_timer_used(cpu, data, size):
	event = b["timer_calc"].event(data)
	sender = inet_ntop(AF_INET, pack('I', event.saddr))
	if sender.__contains__("10.0.0.251") or sender.__contains__("193.167.100.100"):
		time = setTimeInfo(event.timestamp)
		output_arr = []
		output_arr.append("%.6f" % (abs(time) * 1000))
		output_arr.append("recovery")

		t_type = ""
		if event.type == 1:
			t_type = "rack_timer"
		elif event.type == 2:
			t_type = "probe_timer"
		elif event.type == 3:
			t_type = "retrans_timer"

		output_arr.append(t_type)
		output_arr.append(
			{
				"timer": str(event.timer / 1000)
			}
		)

		qlog["traces"][0]["events"].append(output_arr)

print("Tracing tcp events ... Hit Ctrl-C to end")

# Bind print functions to ebpf tables 
b["cwnd_change"].open_perf_buffer(print_cwnd_change)
b["init_event"].open_perf_buffer(print_init_cong_control)
b["mark_lost"].open_perf_buffer(print_mark_lost)
b["timer_calc"].open_perf_buffer(print_timer_used)


if len(sys.argv) == 2:
	outputfile = sys.argv[1]
else:
	outputfile = ti.strftime("%Y-%m-%d-%H-%M", ti.gmtime())
while 1:
	try:
		b.perf_buffer_poll()
	except KeyboardInterrupt:
		with open('/logs/' + outputfile + '.qlog', 'w') as f:
			f.write(json.dumps(qlog))
		exit()